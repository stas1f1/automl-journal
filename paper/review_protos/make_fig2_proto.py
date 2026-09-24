#!/usr/bin/env python3
"""Prototype replacement for Fig. 2 (fig_position): per-task strips in raw units
plus an average-rank strip on top.  Reads the real data from paper/make_tables.py
without writing anything into paper/.
"""
import statistics as st
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, "/home/stas/Documents/GitHub/automl-journal/paper")
import make_tables as mt  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import numpy as np  # noqa: E402

OUT = Path(__file__).parent

INK = "#1a1a1a"
MUTED = "#6e6e6e"
TICK_OTHER = "#c4c4c4"
TICK_GBDT = "#4a4a4a"
C = {"AutoDS-Tools": "#0072B2", "Terminus-2": "#D55E00", "FEDOT.LLM": "#009E73"}
GBDT = {"XGBoost", "LightGBM", "CatBoost"}
NAMED = ["MLP-PLR ens.", "XGBoost", "LightGBM", "CatBoost", "Linear"]

plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 300, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "font.size": 7, "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "text.color": INK, "figure.facecolor": "white", "axes.facecolor": "white",
    "pdf.fonttype": 42,
})
FULL_W = 7.1


# ---------------------------------------------------------------- data
def avg_rank(pool):
    r = {k: [] for k in pool}
    for j in range(len(mt.TASKS)):
        order = sorted(pool, key=lambda m: -pool[m][j] if mt.HIB[j] else pool[m][j])
        for pos, m in enumerate(order, 1):
            r[m].append(pos)
    return {k: st.mean(v) for k, v in r.items()}


NOLAYER = [mt.GRID[t][2] for t in mt.TASKS]
BASE = {**mt.PUBLISHED, **mt.AGENTS}
RANK = avg_rank(BASE)
RANK_NOLAYER = avg_rank({**mt.PUBLISHED, "Terminus-2": mt.AGENTS["Terminus-2"],
                         "FEDOT.LLM": mt.AGENTS["FEDOT.LLM"],
                         "AutoDS-Tools": NOLAYER})["AutoDS-Tools"]


def corner(agent, sign):
    """Per-task most (sign=+1) or least (sign=-1) favourable value."""
    if agent == "FEDOT.LLM":
        return [v + sign * 0.005 if mt.HIB[j] else v - sign * 0.005
                for j, v in enumerate(mt.AGENTS[agent])]
    att = mt.ATTEMPTS[agent]
    better = (lambda xs: max(xs)) if sign > 0 else (lambda xs: min(xs))
    worse = (lambda xs: min(xs)) if sign > 0 else (lambda xs: max(xs))
    return [better(att[t]) if mt.HIB[j] else worse(att[t]) for j, t in enumerate(mt.TASKS)]


RANK_RANGE = {a: sorted([avg_rank({**BASE, a: corner(a, +1)})[a],
                         avg_rank({**BASE, a: corner(a, -1)})[a]])
              for a in mt.AGENTS}

# lane A: the three deployed systems; lane B: the untreated AutoDS-Tools cell
AGENT_STYLE = {  # name -> (colour, marker, filled)
    "AutoDS-Tools": (C["AutoDS-Tools"], "D", True),
    "Terminus-2": (C["Terminus-2"], "o", True),
    "FEDOT.LLM": (C["FEDOT.LLM"], "s", True),
}


def marker(ax, x, y, name, filled=True, size=20, z=5):
    col, mk, _ = AGENT_STYLE[name]
    if filled:
        ax.scatter([x], [y], s=size, marker=mk, color=col, zorder=z,
                   edgecolor="white", linewidth=0.5)
    else:
        ax.scatter([x], [y], s=size, marker=mk, facecolor="white", edgecolor=col,
                   linewidth=0.9, zorder=z)


def ticks_lane(ax, xs_by_name, y0, y1):
    for name, x in xs_by_name.items():
        gb = name in GBDT
        ax.plot([x, x], [y0, y1], color=TICK_GBDT if gb else TICK_OTHER,
                lw=1.0 if gb else 0.8, zorder=3 if gb else 2,
                solid_capstyle="butt")


# ---------------------------------------------------------------- panels
Y_TICK0, Y_TICK1 = 0.30, 1.0    # published ticks
Y_A = -0.20                     # lane A
Y_B = -0.70                     # lane B
Y_LAB = -1.35                   # endpoint labels


def task_panel(ax, j):
    task, hib = mt.TASKS[j], mt.HIB[j]
    pub = {b: mt.PUBLISHED[b][j] for b in mt.PUBLISHED}
    best_name = max(pub, key=pub.get) if hib else min(pub, key=pub.get)
    worst_name = min(pub, key=pub.get) if hib else max(pub, key=pub.get)
    lo, hi = min(pub.values()), max(pub.values())
    span = hi - lo
    means = {a: mt.AGENTS[a][j] for a in mt.AGENTS}
    means["nolayer"] = NOLAYER[j]
    ext = [v for a in ("Terminus-2", "AutoDS-Tools") for v in mt.ATTEMPTS[a][task]]
    xmin = min(lo, *means.values(), *ext) - 0.04 * span
    xmax = max(hi, *means.values(), *ext) + 0.04 * span
    ax.set_xlim((xmax, xmin) if not hib else (xmin, xmax))
    ax.set_ylim(-1.75, 1.15)
    ax.axis("off")

    # baseline under the ticks
    ax.plot([xmin, xmax], [Y_TICK0, Y_TICK0], color="#b9b9b9", lw=0.6, zorder=1)
    ticks_lane(ax, pub, Y_TICK0, Y_TICK1)

    # lane A: whiskers then markers
    for a in ("Terminus-2", "AutoDS-Tools"):
        att = mt.ATTEMPTS[a][task]
        ax.plot([min(att), max(att)], [Y_A, Y_A], color=AGENT_STYLE[a][0],
                lw=1.4, alpha=0.9, zorder=4, solid_capstyle="butt")
    for a in ("Terminus-2", "AutoDS-Tools"):
        marker(ax, means[a], Y_A, a)
    # lane B: the untreated cell and FEDOT.LLM with its rounding interval
    f = means["FEDOT.LLM"]
    ax.plot([f - 0.005, f + 0.005], [Y_B, Y_B], color=C["FEDOT.LLM"], lw=0.8,
            alpha=0.3, zorder=3, solid_capstyle="butt")
    for e in (f - 0.005, f + 0.005):
        ax.plot([e, e], [Y_B - 0.12, Y_B + 0.12], color=C["FEDOT.LLM"], lw=0.8,
                alpha=0.3, zorder=3)
    marker(ax, f, Y_B, "FEDOT.LLM")
    marker(ax, means["nolayer"], Y_B, "AutoDS-Tools", filled=False)

    # endpoint labels: the published extremes in raw units
    ax.text(pub[worst_name], Y_LAB, f"{pub[worst_name]:.4f}  {worst_name}",
            ha="left", va="top", fontsize=6, color=MUTED)
    ax.text(pub[best_name], Y_LAB, f"{best_name}  {pub[best_name]:.4f}",
            ha="right", va="top", fontsize=6, color=MUTED)
    # row label
    arrow = "↑" if hib else "↓"
    ax.text(-0.012, 0.62, mt.SHORT[j], transform=ax.transAxes, ha="right",
            va="center", fontsize=7, fontweight="bold", color=INK)
    ax.text(-0.012, 0.28, f"{mt.METRIC[j]} {arrow}", transform=ax.transAxes,
            ha="right", va="center", fontsize=6.2, color=MUTED)


def rank_panel(ax):
    ax.set_xlim(21.6, 0.4)          # 1 = best, on the right
    ax.set_ylim(-3.2, 2.6)
    ax.axis("off")
    y0, y1 = Y_TICK0, Y_TICK1
    ax.plot([21.6, 0.4], [y0, y0], color="#b9b9b9", lw=0.6, zorder=1)
    pub_r = {b: RANK[b] for b in mt.PUBLISHED}
    ticks_lane(ax, pub_r, y0, y1)
    # numeric axis under the baseline
    for r in (1, 5, 10, 15, 20):
        ax.plot([r, r], [y0, y0 - 0.12], color="#b9b9b9", lw=0.6)
        ax.text(r, y0 - 0.2, str(r), ha="center", va="top", fontsize=6, color=MUTED)
    # named baselines, two alternating levels above the ticks
    # (level, ha): CatBoost and LightGBM are 0.5 rank apart, so they sit on
    # different levels and are aligned away from each other.
    place = {"Linear": (1.25, "center"), "CatBoost": (1.25, "right"),
             "XGBoost": (1.25, "center"), "LightGBM": (1.85, "center"),
             "MLP-PLR ens.": (1.85, "left")}
    for name in NAMED:
        x = pub_r[name]
        yl, ha = place[name]
        ax.plot([x, x], [y1, yl - 0.08], color="#b9b9b9", lw=0.5, zorder=1)
        ax.text(x, yl, f"{name} {x:.1f}", ha=ha, va="bottom", fontsize=6,
                color=MUTED)
    # lane A: three deployed systems with corner whiskers, direct labels
    ya, yb = -0.85, -2.15
    for a in ("Terminus-2", "AutoDS-Tools"):
        lo, hi = RANK_RANGE[a]
        ax.plot([lo, hi], [ya, ya], color=AGENT_STYLE[a][0], lw=1.4, alpha=0.9,
                zorder=4, solid_capstyle="butt")
        marker(ax, RANK[a], ya, a, size=26)
        ax.text(RANK[a], ya - 0.32, f"{a}  {RANK[a]:.1f}", ha="center", va="top",
                fontsize=6.5, color=INK)
    lo, hi = RANK_RANGE["FEDOT.LLM"]
    ax.plot([lo, hi], [yb, yb], color=C["FEDOT.LLM"], lw=0.8, alpha=0.3, zorder=3,
            solid_capstyle="butt")
    for e in (lo, hi):
        ax.plot([e, e], [yb - 0.1, yb + 0.1], color=C["FEDOT.LLM"], lw=0.8,
                alpha=0.3, zorder=3)
    marker(ax, RANK["FEDOT.LLM"], yb, "FEDOT.LLM", size=26)
    ax.text(RANK["FEDOT.LLM"], yb - 0.32, f"FEDOT.LLM  {RANK['FEDOT.LLM']:.1f}",
            ha="center", va="top", fontsize=6.5, color=INK)
    marker(ax, RANK_NOLAYER, yb, "AutoDS-Tools", filled=False, size=26)
    ax.text(RANK_NOLAYER, yb - 0.32, f"AutoDS-Tools, no layer  {RANK_NOLAYER:.1f}",
            ha="center", va="top", fontsize=6.5, color=INK)
    ax.text(-0.012, 0.62, "All 8 tasks", transform=ax.transAxes, ha="right",
            va="center", fontsize=7, fontweight="bold", color=INK)
    ax.text(-0.012, 0.50, "average rank\n(1 = best of 21)", transform=ax.transAxes,
            ha="right", va="top", fontsize=6.2, color=MUTED, linespacing=1.15)


def main():
    n = len(mt.TASKS)
    fig = plt.figure(figsize=(FULL_W, 4.5))
    gs = fig.add_gridspec(n + 1, 1, height_ratios=[2.35] + [1.0] * n,
                          left=0.115, right=0.995, top=0.90, bottom=0.01,
                          hspace=0.10)
    ax_top = fig.add_subplot(gs[0])
    rank_panel(ax_top)
    for j in range(n):
        task_panel(fig.add_subplot(gs[j + 1]), j)

    # legend, one row on top
    handles = [
        Line2D([], [], marker="D", color=C["AutoDS-Tools"], ls="", ms=4.5,
               label="AutoDS-Tools, as shipped"),
        Line2D([], [], marker="D", mfc="white", mec=C["AutoDS-Tools"], ls="", ms=4.5,
               label="AutoDS-Tools, no layer"),
        Line2D([], [], marker="o", color=C["Terminus-2"], ls="", ms=4.5,
               label="Terminus-2"),
        Line2D([], [], marker="s", color=C["FEDOT.LLM"], ls="", ms=4.5,
               label="FEDOT.LLM"),
        Line2D([], [], marker="|", color=TICK_GBDT, ls="", ms=7, mew=1.0,
               label="XGBoost, LightGBM, CatBoost (tuned)"),
        Line2D([], [], marker="|", color=TICK_OTHER, ls="", ms=7, mew=0.8,
               label="other 15 published methods"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=6, frameon=False,
               fontsize=6.3, handletextpad=0.3, columnspacing=1.0,
               bbox_to_anchor=(0.55, 0.995))
    fig.text(0.995, 0.905, "better →", ha="right", va="bottom", fontsize=6.3,
             color=MUTED)
    fig.suptitle("Agents among the 18 tuned TabReD baselines", x=0.55, y=1.035,
                 fontsize=7.5, fontweight="bold")
    p = OUT / "fig2_proto.png"
    fig.savefig(p)
    fig.savefig(OUT / "fig2_proto.pdf")
    print("wrote", p)
    print("ranks", {k: round(v, 2) for k, v in RANK.items() if k in mt.AGENTS},
          "nolayer", round(RANK_NOLAYER, 2), "ranges", RANK_RANGE)


if __name__ == "__main__":
    main()
