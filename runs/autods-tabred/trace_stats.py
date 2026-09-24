#!/usr/bin/env python3
"""Per-trial diagnostics from our own AutoDS runs.

Reads every <trial>/agent/autods_trace.json under a jobs directory and reports,
for each trial: the model the agent says it used, the validation score it
reported to itself, the test metric the verifier computed, the gap between them,
the number of steps, and whether the repair loop appears in the trace.

The validation-to-test gap is the quantity of interest: TabReD splits are
temporal, so it measures how much of the agent's own estimate survives the
shift.  A large positive gap means the agent believed a model that does not hold
up out of time.

Usage:
    python3 trace_stats.py [jobs_dir] [--only=SUBSTRING]
"""
from __future__ import annotations

import json
import re
import statistics as st
import sys
from pathlib import Path

VAL_PAT = re.compile(r"(?:VALIDATION_SCORE|validation (?:metric|RMSE|score))"
                     r"[^0-9\-]{0,40}([0-9]*\.?[0-9]+)", re.I)
MODEL_PAT = re.compile(r"MODEL_USED\s*=\s*([A-Za-z_][A-Za-z0-9_]*)")
REPAIR_PAT = re.compile(r"debugger|repair|traceback", re.I)


def read_reward(trial: Path) -> tuple[str, float] | None:
    f = trial / "verifier" / "reward.json"
    if not f.is_file():
        return None
    d = json.loads(f.read_text())
    for k in ("rmse", "roc_auc", "auc"):
        if k in d:
            return k, float(d[k])
    return "reward", float(d.get("reward", float("nan")))


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--only=")), None)
    jobs = Path(args[0] if args else "jobs")
    if not jobs.is_dir():
        print(f"нет каталога {jobs}", file=sys.stderr)
        return 1

    rows = []
    for job in sorted(p for p in jobs.iterdir() if p.is_dir()):
        if only and only not in job.name:
            continue
        for trial in sorted(p for p in job.iterdir() if p.is_dir()):
            tf = trial / "agent" / "autods_trace.json"
            if not tf.is_file():
                continue
            try:
                d = json.loads(tf.read_text())
            except json.JSONDecodeError:
                continue
            steps = d.get("steps", [])
            txt = " ".join(s.get("message", "") for s in steps)
            m = MODEL_PAT.search(txt)
            v = VAL_PAT.search(txt)
            got = read_reward(trial)
            rows.append(dict(
                task=trial.name.split("__")[0],
                trial=trial.name,
                model=m.group(1) if m else "—",
                val=float(v.group(1)) if v else None,
                metric=got[0] if got else "—",
                test=got[1] if got else None,
                steps=len(steps),
                repair=bool(REPAIR_PAT.search(txt)),
            ))

    if not rows:
        print("трейсов не найдено")
        return 1

    print(f"{'задача':<20}{'модель':<18}{'валид.':>9}{'тест':>10}{'разрыв':>9}"
          f"{'шагов':>7}{'починка':>9}")
    gaps = []
    for r in sorted(rows, key=lambda r: (r["task"], r["trial"])):
        gap = (r["test"] - r["val"]) if (r["val"] is not None and r["test"] is not None) else None
        if gap is not None and r["metric"] == "rmse":
            gaps.append(gap)
        f = lambda x: "—" if x is None else f"{x:.4f}"
        print(f"{r['task']:<20}{r['model'][:17]:<18}{f(r['val']):>9}{f(r['test']):>10}"
              f"{f(gap):>9}{r['steps']:>7}{('да' if r['repair'] else 'нет'):>9}")

    if gaps:
        print(f"\nразрыв валидация→тест по RMSE: медиана {st.median(gaps):+.4f}, "
              f"n={len(gaps)}")
        print("положительный разрыв = на отложенном во времени тесте хуже, "
              "чем агент сам себе намерил")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
