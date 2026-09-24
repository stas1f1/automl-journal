#!/usr/bin/env python3
"""How often does each clause of the discipline block happen without being asked?

The prescribed-knowledge layer's largest component is a training-discipline
block of six clauses.  An ablation tells us what removing the whole block costs;
it does not tell us which clauses were doing the work.  This does: for each
clause we look for its textual signature in the agent's own trace and count the
trials that show it, with and without the prescription.

What this measures and what it does not.  A signature is evidence that the
behaviour appeared in the trace, not proof that it happened, and its absence is
weaker still: a library can satisfy a clause internally without ever printing
anything a grep would catch.  LightAutoML does exactly that for early stopping,
which is why the prescribed arm scores LOW on that row and the number must not
be read as "the prescribed system skips early stopping".  Rows are comparable
down a column, not across systems, unless the signature is one that a hand-rolled
and a library pipeline would both have to emit.

    python3 discipline.py [jobs_dir]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# clause -> (label, regex).  Signatures are deliberately broad: a false positive
# understates the contrast we are looking for, a false negative overstates it.
CLAUSES = [
    ("early stopping",      r"early[_ ]stopping|early stopping"),
    ("trivial baseline",    r"TRIVIAL_BASELINE|trivial (?:baseline|predictor)|"
                            r"DummyRegressor|DummyClassifier"),
    ("inspect submission",  r"describe\(\)|value_counts|nunique|"
                            r"degenerate|constant prediction"),
    ("budget allocation",   r"BUDGET_ALLOCATION|budget allocation|"
                            r"allocate .{0,20}budget"),
    # NB: `best_iteration` is excluded deliberately. LightGBM prints it whenever
    # early stopping fires, so counting it here would score the early-stopping
    # row a second time and invent a discipline the agent never exercised. This
    # clause is about choosing between separately trained variants.
    ("keep best variant",   r"best .{0,12}(?:validation|val).{0,12}score|"
                            r"best_score|best variant|best model"),
]

# Which files carry the agent's own account of what it did.  Terminus-2 writes a
# terminal pane, AutoDS a structured trajectory; both are the agent's record.
TRACES = ("agent/terminus_2.pane", "agent/trajectory.json")


def scan(job: Path) -> tuple[int, dict[str, int]]:
    hits = {label: 0 for label, _ in CLAUSES}
    n = 0
    for trial in sorted(p for p in job.iterdir() if p.is_dir()):
        text = ""
        for rel in TRACES:
            f = trial / rel
            if f.is_file():
                text += f.read_text(errors="replace")
        if not text:
            continue
        n += 1
        for label, pat in CLAUSES:
            if re.search(pat, text, re.I):
                hits[label] += 1
    return n, hits


def main() -> int:
    jobs = Path(sys.argv[1] if len(sys.argv) > 1 else "jobs")
    found = []
    for job in sorted(p for p in jobs.iterdir() if p.is_dir()):
        n, hits = scan(job)
        if n:
            found.append((job.name, n, hits))
    if not found:
        print("испытаний не найдено")
        return 1

    w = max(len(lbl) for lbl, _ in CLAUSES) + 2
    for name, n, hits in found:
        print(f"\n{name}  ({n} испытаний)")
        for label, _ in CLAUSES:
            k = hits[label]
            bar = "#" * round(20 * k / n)
            print(f"  {label:<{w}}{k:>3}/{n:<3} {100 * k / n:5.0f}%  {bar}")
    print("\nСигнатура — свидетельство, что поведение попало в трассу, а не что оно\n"
          "произошло; её отсутствие слабее вдвойне. LightAutoML делает раннюю\n"
          "остановку внутри и в трассу её не пишет, поэтому строку early stopping\n"
          "нельзя читать поперёк систем.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
