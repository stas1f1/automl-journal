#!/usr/bin/env python3
"""Per-trial agent wall-clock, from the recorded start to the scored reward.

The Harbor artefacts carry no duration field, so the interval between
``result.json``'s ``started_at`` and the mtime of ``verifier/reward.json``
(written by the scorer afterwards) is what we have.  It slightly overstates the
agent's own time by including scoring, and that is the same overstatement for
every arm, so arm-to-arm comparisons hold.

``started_at`` is used rather than the mtime of ``agent/instruction.md``,
which only AutoDS writes: keying on it scored every Terminus-2 trial as a
timeout.

A trial with no reward file hit the ceiling without submitting.  Those are
reported separately and never averaged: a timeout measures the budget, not the
system.

    python3 walltime.py [jobs_dir] --only=SUBSTRING
"""
from __future__ import annotations

import json
import statistics as st
import sys
from datetime import datetime
from pathlib import Path

CEILING_MIN = 60.0          # task.toml timeout_sec = 3600


def started(trial: Path) -> float | None:
    r = trial / "result.json"
    if r.is_file():
        try:
            v = json.loads(r.read_text()).get("started_at")
        except json.JSONDecodeError:
            v = None
        if v:
            return datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp()
    inst = trial / "agent" / "instruction.md"
    return inst.stat().st_mtime if inst.is_file() else None


def minutes(trial: Path) -> float | None:
    begin = started(trial)
    end = trial / "verifier" / "reward.json"
    if begin is None or not end.is_file():
        return None
    return (end.stat().st_mtime - begin) / 60.0


def main() -> int:
    argv = sys.argv[1:]
    pos = [a for a in argv if not a.startswith("--")]
    only = next((a.split("=", 1)[1] for a in argv if a.startswith("--only=")), "")
    jobs = Path(pos[0] if pos else "jobs")

    vals: list[tuple[str, float]] = []
    lost: list[str] = []
    for job in sorted(p for p in jobs.iterdir() if p.is_dir()):
        if only and only not in job.name:
            continue
        for trial in sorted(p for p in job.iterdir() if p.is_dir()):
            m = minutes(trial)
            if m is None:
                if (trial / "agent").is_dir():
                    lost.append(trial.name)
                continue
            vals.append((trial.name, m))

    if not vals and not lost:
        print("испытаний не найдено")
        return 1

    ms = sorted((m for _n, m in vals), reverse=True)
    near = sum(1 for m in ms if CEILING_MIN - 15 <= m < CEILING_MIN)
    over = sum(1 for m in ms if m >= CEILING_MIN)
    print(f"испытаний с результатом: {len(ms)}")
    if ms:
        print(f"  медиана {st.median(ms):.1f} мин, среднее {st.mean(ms):.1f}, "
              f"мин {min(ms):.1f}, макс {max(ms):.1f}")
        print(f"  в последних 15 минутах до потолка: {near}; на потолке и выше: {over}")
    if lost:
        print(f"без сабмита (потолок {CEILING_MIN:.0f} мин): {len(lost)} "
              f"-- {', '.join(lost)}")
        total = len(ms) + len(lost)
        print(f"  доля потерь: {100 * len(lost) / total:.1f}% из {total}")
    print("\nдля make_tables.py (RERUN_MINUTES):")
    print("[" + ", ".join(f"{m:.1f}" for m in ms) + "]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
