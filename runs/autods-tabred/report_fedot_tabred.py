#!/usr/bin/env python3
"""Сводка прогона FEDOT.LLM на TabReD с бюджетом бэкенда (task_fedot_tabred_40min.md).

Читает задания Harbor из jobs/ и печатает Markdown: по каждой задаче попытки,
среднее по попыткам с метрикой, отказы с причиной, время агента; затем
нормированную оценку и средний ранг по шкале статьи (функции и словари
paper/make_tables.py), рядом со строкой FEDOT.LLM, которая сейчас в статье.

    python3 report_fedot_tabred.py JOB [JOB ...] [--json OUT]

Потерянные трайлы в среднее не входят, как у двух других систем. Задача, где
метрики нет ни в одной попытке, в нормированное среднее и ранг не входит, и
это печатается явно.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import re
import statistics as st
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mt", HERE.parent.parent / "paper" / "make_tables.py")
mt = importlib.util.module_from_spec(spec)
sys.modules["mt"] = mt
spec.loader.exec_module(mt)

TASKS = mt.TASKS
CLASSIF = {"homesite-insurance", "ecom-offers", "homecredit-default"}


def minutes(result: dict) -> float | None:
    a = result.get("agent_execution") or {}
    try:
        f = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return (f(a["finished_at"]) - f(a["started_at"])).total_seconds() / 60
    except (KeyError, TypeError, ValueError):
        return None


def failure(trial: Path) -> str | None:
    e = trial / "exception.txt"
    if not e.is_file():
        return None
    t = e.read_text(errors="replace")
    if "AgentTimeoutError" in t:
        return "потолок 3600 с"
    if "exit 137" in t:
        return "убит по памяти (137)"
    m = re.search(r"exit (\d+)", t)
    return f"код {m.group(1)}" if m else "исключение"


def fedot_facts(trial: Path) -> dict:
    """Что FEDOT сделал с бюджетом, по его журналу."""
    log = trial / "agent" / "fedotllm.log"
    out = {}
    if not log.is_file():
        return out
    t = log.read_text(errors="replace")
    if m := re.search(r"Initial pipeline was fitted in ([\d.]+) sec", t):
        out["initial_fit_s"] = float(m.group(1))
    out["composing_skipped"] = "Timeout is too small for composing" in t
    if m := re.search(r"Initial metric: \[([\d.]+)\]", t):
        out["tuner_initial"] = float(m.group(1))
    if m := re.search(r"Final metric: ([\d.]+)", t):
        out["tuner_final"] = float(m.group(1))
    if m := re.search(r"Final graph: (\{.*?\})\n", t):
        out["final_graph"] = m.group(1)
    elif m := re.search(r"Initial graph: (\{.*?\})\n", t):
        out["final_graph"] = m.group(1)
    toks = [int(x) for x in re.findall(r"Total number of prompt tokens:\S*\s*(\d+)", t)]
    ctoks = [int(x) for x in re.findall(r"Total number of completion tokens:\S*\s*(\d+)", t)]
    if toks:
        out["prompt_tokens"] = toks[-1]
    if ctoks:
        out["completion_tokens"] = ctoks[-1]
    if m := re.search(r"predictor_init_kwargs: (\{.*?\})\n", t):
        out["init_kwargs"] = m.group(1)
    return out


def collect(jobs: list[Path]) -> dict:
    rows = {t: [] for t in TASKS}
    for job in jobs:
        for trial in sorted(p for p in job.iterdir() if p.is_dir() and "__" in p.name):
            task = trial.name.split("__")[0]
            if task not in rows:
                continue
            # оборванные остановкой задания трайлы не считаются: у них нет
            # result.json или в exception.txt отмена (CancelledError)
            if not (trial / "result.json").is_file():
                continue
            exc = trial / "exception.txt"
            if exc.is_file() and "CancelledError" in exc.read_text(errors="replace"):
                continue
            rj = trial / "verifier" / "reward.json"
            reward = json.loads(rj.read_text()) if rj.is_file() else {}
            key = "roc_auc" if task in CLASSIF else "rmse"
            res = json.loads((trial / "result.json").read_text()) if (trial / "result.json").is_file() else {}
            rows[task].append({
                "job": job.name, "trial": trial.name,
                "value": reward.get(key), "failure": failure(trial) if key not in reward else None,
                "minutes": minutes(res), **fedot_facts(trial),
            })
    return rows


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--json")]
    out_json = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--json=")), None)
    jobs = [Path(a) for a in args]
    rows = collect(jobs)
    old = mt.AGENTS["FEDOT.LLM"]

    P = print
    P("| Задача | Метрика | Попытки | Среднее | Старая строка | Отказы | Мин. агента |")
    P("|---|---|---|---|---|---|---|")
    new = []
    for j, t in enumerate(TASKS):
        vals = [r["value"] for r in rows[t] if r["value"] is not None]
        fails = [r["failure"] for r in rows[t] if r["failure"]]
        mins = [r["minutes"] for r in rows[t] if r["minutes"] is not None]
        mean = st.mean(vals) if vals else None
        new.append(mean)
        P(f"| `{t}` | {mt.METRIC[j]} | {', '.join(f'{v:.4f}' for v in vals) or '—'} "
          f"| {f'{mean:.4f}' if mean is not None else '—'} | {old[j]:.4f} "
          f"| {'; '.join(fails) or '—'} | {', '.join(f'{m:.1f}' for m in mins) or '—'} |")

    P()
    have = [j for j, v in enumerate(new) if v is not None]
    n_old = st.mean(mt.normalized(old[j], j) for j in range(len(TASKS)))
    P(f"Нормированное среднее старой строки по всем восьми задачам: {n_old:.4f}.")
    if have:
        n_new = st.mean(mt.normalized(new[j], j) for j in have)
        n_old_same = st.mean(mt.normalized(old[j], j) for j in have)
        P(f"Новая строка по {len(have)} задачам с метрикой: {n_new:.4f}; старая на тех же задачах: {n_old_same:.4f}.")
        # средний ранг среди 21 метода: подставляем новую строку вместо старой
        agents_backup = dict(mt.AGENTS)
        mt.AGENTS["FEDOT.LLM"] = [new[j] if new[j] is not None else None for j in range(len(TASKS))]
        r, _ = mt.ranks()
        P(f"Средний ранг новой строки по {len(r['FEDOT.LLM'])} задачам: {st.mean(r['FEDOT.LLM']):.2f} из {len(r)}.")
        mt.AGENTS.clear(); mt.AGENTS.update(agents_backup)
        r0, _ = mt.ranks()
        P(f"Средний ранг старой строки: {st.mean(r0['FEDOT.LLM']):.2f} из {len(r0)}.")
        for name in ("Linear", "Terminus-2", "AutoDS-Tools", "XGBoost"):
            pool = {**mt.PUBLISHED, **mt.AGENTS}
            if name in pool:
                P(f"  {name}: нормированное {st.mean(mt.normalized(pool[name][j], j) for j in have):.4f} на тех же задачах.")
    if out_json:
        Path(out_json).write_text(json.dumps({"rows": rows, "means": dict(zip(TASKS, new))}, indent=1, ensure_ascii=False))
        P(f"\nПодробности по трайлам: {out_json}")


if __name__ == "__main__":
    main()
