#!/usr/bin/env python3
"""Собрать строки таблицы результатов из заданий MLAgentBench.

Правило про испытания без результата — то же, что было принято для TabReD:
испытание, исчерпавшее бюджет и не оставившее посылки, из среднего исключается,
потому что оно меряет бюджет, а не модель. Отличить одно от другого можно по
самому reward.json: у настоящей оценки рядом с наградой лежат поля метрики
(accuracy, dice, smape и так далее), у несостоявшейся — только "reward": 0.0.

    python3 collect_mlab.py <каталог задания> [<каталог задания> ...]
"""
from __future__ import annotations

import json
import pathlib
import statistics
import sys

# какое поле reward.json попадает в таблицу и как оно называется в статье
METRIC = {
    "amp-parkinsons":     ("smape",            "SMAPE",            0),
    "cifar10":            ("accuracy",         "accuracy",         1),
    "clrs":               ("pointer_accuracy", "pointer accuracy", 1),
    "fathomnet":          ("micro_f1",         "micro-F1",         1),
    "feedback":           ("mcrmse",           "MCRMSE",           0),
    "house-price":        ("mae",              "MAE",              0),
    "identify-contrails": ("dice",             "Dice",             1),
    "imdb":               ("accuracy",         "accuracy",         1),
    "ogbn-arxiv":         ("accuracy",         "accuracy",         1),
    "spaceship-titanic":  ("accuracy",         "accuracy",         1),
}


def collect(job: pathlib.Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for d in sorted(p for p in job.iterdir() if p.is_dir()):
        task = d.name.split("__")[0]
        if task not in METRIC:
            continue
        rec = out.setdefault(task, {"values": [], "lost": 0, "timeouts": 0})
        rj = d / "verifier" / "reward.json"
        timed_out = (d / "exception.txt").is_file() and \
            "AgentTimeoutError" in (d / "exception.txt").read_text()
        rec["timeouts"] += timed_out
        if not rj.is_file():
            rec["lost"] += 1
            continue
        data = json.loads(rj.read_text())
        field = METRIC[task][0]
        if field not in data:          # только "reward": 0.0 — посылки не было
            rec["lost"] += 1
            continue
        rec["values"].append(data[field])
    return out


def main() -> int:
    for arg in sys.argv[1:]:
        job = pathlib.Path(arg)
        print(f"########## {job.name}")
        for task, rec in sorted(collect(job).items()):
            field, name, hib = METRIC[task]
            v = rec["values"]
            mean = statistics.fmean(v) if v else None
            spread = f"{min(v):.6g}..{max(v):.6g}" if len(v) > 1 else (f"{v[0]:.6g}" if v else "—")
            print(f"  {task:<20} {name:<16} n={len(v)} "
                  f"среднее={mean if mean is None else round(mean, 6)} "
                  f"размах={spread} потеряно={rec['lost']} бюджет исчерпан={rec['timeouts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
