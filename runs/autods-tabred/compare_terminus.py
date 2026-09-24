#!/usr/bin/env python3
"""Compare the AutoDS re-run against Terminus-2 on the common TabReD adapter.

Both arms use the full official temporal splits and the benchmark's own metrics,
so the values are directly comparable.  Differences are reported relative to the
Terminus-2 value and judged against the noise floor measured in the paper
(Section "Noise floor"): on TabReD, relative differences above 1% are treated as
real, anything smaller is not distinguishable from run-to-run variation.

Reporting the sign alone would overstate the result -- a system can be ahead on
every task and still be indistinguishable on most of them.

Comparing two configurations of the *same* system is a different question and
needs a different threshold: there the right figure is that system's own worst
task, not the noisier of a pair.  Pass --noise= to set it and --label= to name
the arm being compared.

Usage:
    python3 compare_terminus.py [jobs_dir] [--only=SUBSTRING] [--label=NAME]
                                [--noise=PCT]
"""
from __future__ import annotations

import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

# Terminus-2, mean of three attempts, from verifier/reward.json on the Harbor hub.
TERMINUS = {
    "homesite-insurance": 0.958801, "ecom-offers": 0.558499,
    "homecredit-default": 0.858995, "sberbank-housing": 0.249054,
    "cooking-time": 0.483730, "delivery-eta": 0.548203,
    "maps-routing": 0.162825, "weather": 1.524693,
}
HIB = {"homesite-insurance", "ecom-offers", "homecredit-default"}
NOISE_PCT = 1.0          # measured floor, see the paper's design section
LABEL = "AutoDS"         # name of the arm read from jobs_dir


def opt(name: str, default: str) -> str:
    pre = f"--{name}="
    return next((a[len(pre):] for a in sys.argv[1:] if a.startswith(pre)), default)


def main() -> int:
    global NOISE_PCT, LABEL
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = opt("only", "full")
    LABEL = opt("label", LABEL)
    NOISE_PCT = float(opt("noise", str(NOISE_PCT)))
    jobs = Path(args[0] if args else "jobs")

    per_task: dict[str, list[float]] = defaultdict(list)
    failed: list[tuple[str, str]] = []
    for job in sorted(p for p in jobs.iterdir() if p.is_dir()):
        if only and only not in job.name:
            continue
        for trial in sorted(p for p in job.iterdir() if p.is_dir()):
            f = trial / "verifier" / "reward.json"
            if not f.is_file():
                continue
            d = json.loads(f.read_text())
            v = d.get("roc_auc", d.get("rmse"))
            task = trial.name.split("__")[0]
            if v is not None:
                per_task[task].append(float(v))
            else:
                # No raw metric at all: the agent produced no submission.  A
                # timed-out trial looks exactly like this, and averaging its
                # zero would report an infrastructure limit as model quality.
                failed.append((task, trial.name))

    if not per_task:
        print("результатов не найдено")
        return 1

    print(f"{'задача':<20}{'n':>3}{LABEL:>11}{'свой шум':>10}"
          f"{'Terminus-2':>12}{'отн.разн.':>11}  вердикт")
    real = ahead = 0
    own = []
    for task in sorted(TERMINUS):
        vs = per_task.get(task)
        if not vs:
            print(f"{task:<20}{0:>3}{'—':>11}{'—':>10}{TERMINUS[task]:>12.5f}"
                  f"{'—':>11}  ещё не считано")
            continue
        m = st.mean(vs)
        sd = st.stdev(vs) if len(vs) > 1 else 0.0
        t = TERMINUS[task]
        rel = (m - t) / t * 100 * (1 if task in HIB else -1)
        ahead += rel > 0
        real += abs(rel) > NOISE_PCT
        verdict = "выше шума" if abs(rel) > NOISE_PCT else "в пределах шума"
        rsd = sd / abs(m) * 100 if len(vs) > 1 and m else None
        if rsd is not None:
            own.append(rsd)
        print(f"{task:<20}{len(vs):>3}{m:>11.5f}"
              f"{('—' if rsd is None else f'{rsd:.3f}%'):>10}{t:>12.5f}"
              f"{rel:>+10.2f}%  {verdict}")

    done = len(per_task)
    print(f"\nсчитано {done} задач из {len(TERMINUS)}; {LABEL} впереди на {ahead}, "
          f"но порог шума в {NOISE_PCT}% превышен только на {real}")
    if ahead and real < ahead:
        print("формулировать надо по второму числу, а не по первому")
    if failed:
        print(f"\nисключено из средних: {len(failed)} испытаний без сабмита "
              f"({', '.join(t for t, _ in failed)})")
    if own:
        print(f"\nсобственный разброс {LABEL}: медиана {st.median(own):.3f}% "
              f"относительного ст.откл., n={len(own)} задач с повторами")
        if NOISE_PCT == 1.0:
            print(f"порог {NOISE_PCT}% измерен на Terminus-2 и для сравнения двух систем остаётся\n"
                  "верным (берётся более шумная из них); для сравнения конфигураций одной\n"
                  "системы он слишком груб -- там значима куда меньшая разница")
        else:
            print(f"порог {NOISE_PCT}% задан вручную: это сравнение конфигураций одной системы,\n"
                  "и брать порог по более шумной из пары здесь нечего")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
