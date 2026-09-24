#!/usr/bin/env python3
# OBSOLETE since 22 September 2026: the FEDOT.LLM TabReD values in make_tables.py
# are read at full precision from the Harbor Hub jobs of 14 August 2026, so the
# rounding interval this script sweeps no longer exists.  Kept for the record.

"""How much of FEDOT.LLM's leaderboard placement is an artefact of rounding?

FEDOT.LLM's TabReD metrics reached us at two decimals.  Each reported value v
therefore stands for the interval [v-0.005, v+0.005].  This script sweeps every
task independently to the most and the least favourable end of that interval and
reports the resulting range of the average rank and the normalised mean, so the
paper can state which claims survive the whole interval and which do not.

Run from paper/:  python3 precision_check.py
"""
import importlib.util
import statistics as st
from pathlib import Path

spec = importlib.util.spec_from_file_location("mt", Path(__file__).parent / "make_tables.py")
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)

HIB, PUB = mt.HIB, mt.PUBLISHED
FED = mt.AGENTS["FEDOT.LLM"]
OTHERS = {k: v for k, v in mt.AGENTS.items() if k != "FEDOT.LLM"}
EPS = 0.005          # half of the last printed decimal
N = len(mt.TASKS)


def rank_of(vals, name="FEDOT.LLM"):
    pool = {**PUB, **OTHERS, name: vals}
    return [sorted(pool, key=lambda m: -pool[m][j] if HIB[j] else pool[m][j]).index(name) + 1
            for j in range(N)]


def norm_mean(vals):
    return st.mean(mt.normalized(vals[j], j) for j in range(N))


def main():
    best = [FED[j] + EPS if HIB[j] else FED[j] - EPS for j in range(N)]
    worst = [FED[j] - EPS if HIB[j] else FED[j] + EPS for j in range(N)]

    print(f"{'вариант':<18}{'ср.ранг':>9}{'норм.среднее':>14}   поранговые места")
    for label, vals in (("как напечатано", FED), ("лучший угол", best), ("худший угол", worst)):
        r = rank_of(vals)
        print(f"{label:<18}{st.mean(r):>9.2f}{norm_mean(vals):>14.3f}   {r}")

    for k, v in OTHERS.items():
        print(f"\n{k:<18}{st.mean(rank_of(v, k)):>9.2f}{norm_mean(v):>14.3f}")
    print(f"{'Linear (опубл.)':<18}{'':>9}{norm_mean(PUB['Linear']):>14.3f}")

    print(f"\nинтервал ср. ранга FEDOT.LLM : {st.mean(rank_of(best)):.1f} .. {st.mean(rank_of(worst)):.1f}"
          f" из {len(PUB) + len(mt.AGENTS)}")
    print(f"интервал норм. среднего      : {norm_mean(worst):.2f} .. {norm_mean(best):.2f}")
    for k, v in OTHERS.items():
        print(f"минимальный отрыв {k:<12}: {norm_mean(v) - norm_mean(best):.2f}")
    print("\nвывод: порядок относительно линейной регрессии по этой точности не разрешается;\n"
          "отставание от открытого харнесса выдерживает весь интервал.")


if __name__ == "__main__":
    raise SystemExit(main())
