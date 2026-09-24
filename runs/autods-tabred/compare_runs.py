#!/usr/bin/env python3
"""Compare two runs of the same system task by task.

`compare_terminus.py` measures against the published Terminus-2 means, which is
the right tool for comparing two different systems.  This is the other case: the
cells of the crossed design, where both sides are the same system and the only
difference is the instruction text or the container.  There the threshold is not
the 1% floor taken from the noisier of a pair but that system's own worst task,
which for AutoDS-Tools is about 0.1%, two orders of magnitude tighter.

Pass the threshold explicitly.  There is no defensible default: it depends on
which system is on both sides.

    python3 compare_runs.py --a=SUBSTRING --b=SUBSTRING [--noise=PCT] [jobs_dir]

`--a` names the reference run and `--b` the one being judged against it; the
relative difference is signed so that positive always means "b is better".
"""
from __future__ import annotations

import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

HIB = {"homesite-insurance", "ecom-offers", "homecredit-default"}
ORDER = ["homesite-insurance", "ecom-offers", "homecredit-default",
         "sberbank-housing", "cooking-time", "delivery-eta",
         "maps-routing", "weather"]


def opt(name: str, default: str | None = None) -> str | None:
    pre = f"--{name}="
    return next((a[len(pre):] for a in sys.argv[1:] if a.startswith(pre)), default)


def read(jobs: Path, pat: str) -> tuple[dict[str, list[float]], list[str]]:
    per: dict[str, list[float]] = defaultdict(list)
    lost: list[str] = []
    for job in sorted(p for p in jobs.iterdir() if p.is_dir()):
        if pat not in job.name:
            continue
        for trial in sorted(p for p in job.iterdir() if p.is_dir()):
            f = trial / "verifier" / "reward.json"
            if not f.is_file():
                continue
            d = json.loads(f.read_text())
            v = d.get("roc_auc", d.get("rmse"))
            if v is None:
                # No raw metric: no submission.  A timeout looks exactly like
                # this, and averaging its zero reports a budget limit as quality.
                lost.append(trial.name)
            else:
                per[trial.name.split("__")[0]].append(float(v))
    return per, lost


def main() -> int:
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    jobs = Path(pos[0] if pos else "jobs")
    pa, pb = opt("a"), opt("b")
    if not pa or not pb:
        print(__doc__.strip())
        return 2
    noise = float(opt("noise", "0.1"))

    A, lost_a = read(jobs, pa)
    B, lost_b = read(jobs, pb)
    if not A or not B:
        print(f"не найдено испытаний: a={len(A)} задач, b={len(B)} задач")
        return 1

    print(f"a = {pa}\nb = {pb}\nпорог {noise}%\n")
    print(f"{'задача':<20}{'na':>3}{'a':>11}{'nb':>4}{'b':>11}{'отн.разн.':>11}  вердикт")
    real = better = 0
    seen = 0
    for task in ORDER:
        va, vb = A.get(task), B.get(task)
        if not va or not vb:
            print(f"{task:<20}{len(va or []):>3}{'—':>11}{len(vb or []):>4}{'—':>11}"
                  f"{'—':>11}  неполно")
            continue
        seen += 1
        ma, mb = st.mean(va), st.mean(vb)
        rel = (mb - ma) / abs(ma) * 100 * (1 if task in HIB else -1)
        better += rel > 0
        sig = abs(rel) > noise
        real += sig
        print(f"{task:<20}{len(va):>3}{ma:>11.5f}{len(vb):>4}{mb:>11.5f}"
              f"{rel:>+10.2f}%  {'выше шума' if sig else 'в пределах шума'}")

    print(f"\nсопоставлено задач: {seen}; b лучше на {better}, "
          f"порог превышен на {real}")
    for label, lost in (("a", lost_a), ("b", lost_b)):
        if lost:
            print(f"исключено из {label}: {len(lost)} испытаний без сабмита "
                  f"({', '.join(lost)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
