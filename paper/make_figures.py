#!/usr/bin/env python3
"""Render the data figures of the paper from the dictionaries in make_tables.py.

Run from paper/:  python3 make_figures.py
Writes figures/fig_*.pdf.  Every number comes from make_tables.py, so the plots
cannot drift from the tables or from the macros in tables/numbers.tex.

House style: one sans font; titles centred, short, the same size everywhere;
no top or right spine; a light grid on the value axis only; colour for identity
only (Okabe-Ito hues, validated for colour-vision deficiency); grey for context.
"""
import statistics as st
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import numpy as np  # noqa: E402

import make_tables as mt  # noqa: E402

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

# House palette, 6 October 2026: the Okabe-Ito hues in cooler, deeper shades
# (the previous figures are in figures/archive_2026-10-06_okabe-ito/).  One
# colour and one marker per system across every figure; a pale canary for the
# instruction file; classic matplotlib colours for the raw case-study data.
# Neutrals are the original greys.  Details in figures/STYLE.md.
INK = "#1a1a1a"            # text, axes labels
MUTED = "#6e6e6e"          # secondary text
GRID_C = "#e4e4e4"         # grid lines
C = {"AutoDS-Tools": "#1F5FA8",   # cobalt
     "Terminus-2": "#D2502A",     # red-orange
     "FEDOT.LLM": "#0E9488",      # teal-green
     "context": "#9a9a9a"}        # grey, anything that is not a system
KNOWLEDGE = "#F7F0C4"      # instruction file: pale canary, a sticky-note highlight
CASE = {"primary": "#1F77B4",     # matplotlib tab:blue, the data a case panel shows
        "highlight": "#FF7F0E",   # tab:orange, the part to predict, a reference line
        "context": "#7F7F7F"}     # tab:gray, training or background data

TITLE = dict(fontsize=7, fontweight="bold", loc="center")
PANEL = dict(fontsize=6.5, fontweight="bold", loc="center")

plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 300, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "font.size": 7, "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "axes.titlesize": 7.5, "axes.titleweight": "bold", "axes.titlepad": 5,
    "axes.labelsize": 7, "axes.labelcolor": INK, "axes.edgecolor": "#9a9a9a",
    "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "axes.axisbelow": True, "grid.color": GRID_C, "grid.linewidth": 0.6,
    "xtick.color": INK, "ytick.color": INK, "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "text.color": INK, "legend.frameon": False, "legend.fontsize": 6.5,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "pdf.fonttype": 42,
})

COL_W = 3.45      # inches, one elsarticle 5p column
FULL_W = 7.1      # inches, full text width


def z2(v):
    """Two decimals without a negative zero."""
    s = f"{v:.2f}"
    return "0.00" if s == "-0.00" else s


def nmean(vals):
    return st.mean(mt.normalized(v, j) for j, v in enumerate(vals) if v is not None)


def grid_cell(col):
    """Normalised mean of one cell of the 2x2 grid (0 neither .. 3 both)."""
    return nmean([mt.GRID[t][2 + col] for t in mt.TASKS])


# figures the paper includes; the others go to figures/archive/
IN_PAPER = {"fig_leaderboard", "fig_ablations"}


def save(fig, name):
    p = (OUT if name in IN_PAPER else OUT / "archive") / f"{name}.pdf"
    p.parent.mkdir(exist_ok=True)
    fig.savefig(p)
    plt.close(fig)
    print("wrote", p.relative_to(Path(__file__).parent))


# ======================================================================
# Fig. position: where the systems sit on the normalised scale (flagship)
# ======================================================================
def fig_position():
    pub = {b: nmean(mt.PUBLISHED[b]) for b in mt.PUBLISHED}
    ours = [("FEDOT.LLM", nmean(mt.AGENTS["FEDOT.LLM"]), C["FEDOT.LLM"], "o"),
            ("Terminus-2", nmean(mt.AGENTS["Terminus-2"]), C["Terminus-2"], "o"),
            ("AutoDS-Tools, no layer", grid_cell(0), C["AutoDS-Tools"], "o"),
            ("AutoDS-Tools, as shipped", nmean(mt.AGENTS["AutoDS-Tools"]),
             C["AutoDS-Tools"], "D")]
    # label, height above the line, anchor, x offset
    named = {"Linear": (0.42, "center", 0.0),
             "CatBoost": (0.42, "right", -0.008),
             "LightGBM": (0.80, "right", -0.008),
             "XGBoost": (1.18, "right", -0.008),
             "MLP-PLR ens.": (1.56, "right", -0.008)}

    fig, ax = plt.subplots(figsize=(COL_W, 2.5))
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-1.85, 1.85)
    ax.axhline(0, color="#9a9a9a", lw=0.8, zorder=1)
    ax.set_yticks([])
    for s in ("left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0\nweakest\npublished", "0.25", "0.5", "0.75",
                        "1\nstrongest\npublished"], fontsize=6)
    ax.tick_params(axis="x", length=0, pad=8)
    for b, v in pub.items():
        ax.plot([v, v], [0.0, 0.18], color=C["context"], lw=0.9, zorder=2)
    for b, (y, ha, dx) in named.items():
        v = pub[b]
        ax.plot([v, v], [0.18, y - 0.08], color=C["context"], lw=0.5, zorder=2)
        ax.text(v + dx, y, f"{b} {v:.2f}", ha=ha, va="bottom", fontsize=6, color=MUTED)
    ax.text(0.0, 0.95, "18 published,\nOptuna-tuned", fontsize=6, color=MUTED,
            ha="left", va="bottom", linespacing=1.1)
    for i, (name, v, col, marker) in enumerate(ours):
        y = -0.42 - 0.4 * i
        ax.plot([v, v], [0, y], color=col, lw=0.6, alpha=0.6, zorder=2)
        ax.scatter([v], [y], s=26, color=col, marker=marker, zorder=3,
                   edgecolor="white", linewidth=0.5)
        ax.text(v - 0.015, y, f"{name}  {v:.2f}", ha="right", va="center",
                fontsize=6.5, color=INK)
    ax.set_title("Normalised score on TabReD", **TITLE)
    save(fig, "fig_position")


# ======================================================================
# Fig. heatmap: per-task normalised position, systems against references
# ======================================================================
def fig_heatmap():
    rows = [("AutoDS-Tools, as shipped", mt.AGENTS["AutoDS-Tools"]),
            ("AutoDS-Tools, no layer", [mt.GRID[t][2] for t in mt.TASKS]),
            ("Terminus-2", mt.AGENTS["Terminus-2"]),
            ("FEDOT.LLM", mt.AGENTS["FEDOT.LLM"]),
            ("MLP-PLR ens. (best published)", mt.PUBLISHED["MLP-PLR ens."]),
            ("XGBoost", mt.PUBLISHED["XGBoost"]),
            ("LightGBM", mt.PUBLISHED["LightGBM"]),
            ("CatBoost", mt.PUBLISHED["CatBoost"]),
            ("Linear", mt.PUBLISHED["Linear"])]
    labels = [r[0] for r in rows]
    M = np.array([[mt.normalized(v, j) for j, v in enumerate(r[1])] for r in rows])
    means = M.mean(axis=1)
    n_ours = 4
    # best per column within each block, bold
    best = np.zeros(M.shape, dtype=bool)
    for lo, hi in ((0, n_ours), (n_ours, M.shape[0])):
        idx = lo + M[lo:hi].argmax(axis=0)
        best[idx, np.arange(M.shape[1])] = True
    best_mean = {int(np.argmax(means[:n_ours])), n_ours + int(np.argmax(means[n_ours:]))}

    fig, ax = plt.subplots(figsize=(FULL_W, 2.7))
    cmap = plt.get_cmap("Blues")
    vmin, vmax = -0.25, 1.0
    im = ax.imshow(np.clip(M, vmin, vmax), cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(mt.TASKS)))
    ax.set_xticklabels(mt.SHORT)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.tick_params(length=0)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, z2(v), ha="center", va="center", fontsize=6.5,
                    color="white" if v > 0.62 else INK,
                    fontweight="bold" if best[i, j] else "normal")
    ax.axhline(n_ours - 0.5, color="white", lw=3)
    ax.axhline(n_ours - 0.5, color=INK, lw=0.6)
    for i, m in enumerate(means):
        ax.text(len(mt.TASKS) - 0.5 + 0.35, i, z2(m), ha="left", va="center",
                fontsize=7, fontweight="bold" if i in best_mean else "normal")
    ax.text(len(mt.TASKS) - 0.5 + 0.35, -0.75, "mean", ha="left", va="center",
            fontsize=6.5, color=MUTED)
    ax.set_xlim(-0.5, len(mt.TASKS) + 0.4)
    ax.set_title("Per-task normalised score on TabReD", **TITLE)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01, ticks=[0, 0.5, 1.0])
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=6.5, length=0)
    save(fig, "fig_heatmap")


# ======================================================================
# Fig. grid: the 2x2 on TabReD, per-task relative change vs the untreated cell
# ======================================================================
def fig_grid():
    cols = [("$K_{\\mathrm{tool}}$ only", 1, C["AutoDS-Tools"], "o"),
            ("$K_{\\mathrm{disc}}$ only", 2, C["FEDOT.LLM"], "s"),
            ("both halves", 3, INK, "D")]
    tasks = list(mt.TASKS)
    fig, ax = plt.subplots(figsize=(COL_W, 2.5))
    ax.axvspan(-0.1, 0.1, color="#efefef", zorder=0)
    ax.axvline(0, color="#9a9a9a", lw=0.8, zorder=1)
    ax.grid(axis="x")
    for i, t in enumerate(tasks):
        y = len(tasks) - 1 - i
        for lab, c, col, marker in cols:
            ax.scatter(mt._grid_rel(t, c), y, s=20, color=col, marker=marker,
                       zorder=3, edgecolor="white", linewidth=0.5)
    ymean = -1.2
    ax.axhline(-0.6, color="#cfcfcf", lw=0.6)
    for lab, c, col, marker in cols:
        m = st.mean(mt._grid_rel(t, c) for t in tasks)
        ax.scatter(m, ymean, s=26, color=col, marker=marker, zorder=3,
                   edgecolor="white", linewidth=0.5)
    ax.set_yticks(list(range(len(tasks)))[::-1] + [ymean])
    ax.set_yticklabels(list(mt.SHORT) + ["mean"])
    ax.set_xlabel("change against the untreated cell, %")
    ax.set_title("Splitting the layer on TabReD", **TITLE)
    handles = [Line2D([], [], marker=m, color=col, ls="", markersize=4.5, label=l)
               for l, _c, col, m in cols]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.2),
              ncol=3, handletextpad=0.3, columnspacing=1.2)
    ax.text(0.0, len(tasks) - 0.4, "noise floor ±0.1%", fontsize=6, color=MUTED,
            ha="center", va="bottom")
    ax.set_ylim(-1.8, len(tasks) - 0.1)
    save(fig, "fig_grid")


# ======================================================================
# Fig. model axis: accuracy, reliability and price under three backbones
# ======================================================================
def fig_modelaxis():
    order = ["gemma-4-26b-a4b", "gemma-4-31b", "glm-4.7"]
    short = {"gemma-4-26b-a4b": "gemma-4\n26b-a4b", "gemma-4-31b": "gemma-4\n31b (ref.)",
             "glm-4.7": "glm-4.7"}
    systems = ["Terminus-2", "AutoDS-Tools"]
    fig, axes = plt.subplots(1, 3, figsize=(FULL_W, 1.75))
    x = np.arange(len(order))
    w = 0.36
    for k, sysname in enumerate(systems):
        rows = {r[0]: r for r in mt.AXIS[sysname]}
        col = C[sysname]
        off = (k - 0.5) * w
        d = [rows[m][7] if rows[m][7] is not None else 0.0 for m in order]
        axes[0].bar(x + off, d, w, color=col, label=sysname)
        lost = [100 * rows[m][2] / rows[m][1] for m in order]
        axes[1].bar(x + off, lost, w, color=col)
        for xi, m in zip(x, order):
            axes[1].text(xi + off, 100 * rows[m][2] / rows[m][1] + 0.8 + 2.6 * k,
                         f"{rows[m][2]}/{rows[m][1]}", ha="center", va="bottom", fontsize=5.5)
        cost = [rows[m][5] for m in order]
        axes[2].bar(x + off, cost, w, color=col)
    axes[0].set_title("Median accuracy change, %", **PANEL)
    axes[0].axhline(0, color="#9a9a9a", lw=0.8)
    axes[0].set_ylim(-0.9, 0.3)
    axes[1].set_title("Trials with no metric, %", **PANEL)
    axes[1].set_ylim(0, 34)
    axes[2].set_title("Price per sweep, $", **PANEL)
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels([short[m] for m in order], fontsize=6)
        ax.grid(axis="y")
        ax.tick_params(axis="x", length=0)
    axes[0].legend(loc="lower left", handlelength=1.0, handletextpad=0.4)
    fig.subplots_adjust(wspace=0.38)
    save(fig, "fig_modelaxis")


# ======================================================================
# Fig. wall-time: the clock binds
# ======================================================================
def fig_walltime():
    ok = sorted(m for m in mt.RERUN_MINUTES if m < mt.RERUN_CEILING_MIN)
    tel = {r[0] + "|" + r[1]: r for r in mt.TELEMETRY}
    term = tel["Terminus-2|TabReD"]
    term_mean = term[8] * term[4] / term[3] / 60
    fig, ax = plt.subplots(figsize=(COL_W, 1.5))
    rng = np.random.default_rng(3)
    jit = rng.uniform(-0.08, 0.08, size=len(ok))
    ax.scatter(ok, 1 + jit, s=14, color=C["AutoDS-Tools"], zorder=3,
               edgecolor="white", linewidth=0.4, label="AutoDS-Tools, finished")
    lim = mt.RERUN_CEILING_MIN
    for i in range(mt.RERUN_CEILING_SCORED):
        ax.scatter([lim], [1 + 0.16 * (i - 1)], s=16, facecolor="white",
                   edgecolor=C["AutoDS-Tools"], linewidth=0.9, zorder=3,
                   label="cut at the limit, submitted" if i == 0 else None)
    for i in range(mt.RERUN_TIMEOUTS):
        ax.scatter([lim], [1 + 0.16 * (mt.RERUN_CEILING_SCORED - 1 + i)], s=26,
                   color=INK, marker="x", linewidth=1.0, zorder=4,
                   label="cut at the limit, nothing" if i == 0 else None)
    ax.axvline(lim, color="#9a9a9a", lw=0.8, ls=(0, (3, 2)), zorder=1)
    ax.text(lim - 0.6, 0.6, "limit", ha="right", va="center", fontsize=6, color=MUTED)
    ax.scatter([term_mean], [0.35], s=18, color=C["Terminus-2"], zorder=3,
               edgecolor="white", linewidth=0.4, label="Terminus-2, mean of 24")
    ax.set_xlim(0, 65)
    ax.set_ylim(0.05, 1.7)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("agent wall-clock per trial, minutes")
    ax.grid(axis="x")
    ax.legend(loc="upper left", ncol=2, columnspacing=0.8, handletextpad=0.3,
              borderaxespad=0.0)
    ax.set_title("Wall-clock per trial on TabReD", **PANEL)
    save(fig, "fig_walltime")


# ======================================================================
# Fig. sign flip: the layer on MLAgentBench, three attempts per cell
# ======================================================================
def fig_signflip():
    rows = []
    for task, metric, hib, on, off, *_ in mt.MLAB:
        if on is None or off is None:
            continue           # cifar10, imdb: not repeated, omitted
        if on[0] == 0:
            rows.append((task, None))
            continue
        sc = max(abs(on[1]), abs(off[1])) or 1.0
        d = ((on[1] - off[1]) if hib else (off[1] - on[1])) / sc
        rows.append((task, d))
    rows.sort(key=lambda r: (r[1] is None, -(r[1] or 0)))
    fig, ax = plt.subplots(figsize=(COL_W, 2.1))
    n = len(rows)
    ax.axvline(0, color="#9a9a9a", lw=0.8, zorder=1)
    ax.grid(axis="x")
    for i, (task, d) in enumerate(rows):
        y = n - 1 - i
        if d is None:
            ax.barh(y, -1.0, color="#d9d9d9", height=0.62, zorder=2)
            ax.text(-0.97, y, "no submission, 3 of 3", ha="left",
                    va="center", fontsize=6, color=INK)
        else:
            col = C["AutoDS-Tools"] if d > 0 else C["Terminus-2"]
            ax.barh(y, d, color=col, height=0.62, zorder=2)
            ax.text(d + (0.02 if d >= 0 else -0.02), y, f"{d:+.2f}",
                    ha="left" if d >= 0 else "right", va="center", fontsize=6)
    ax.set_yticks(range(n))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.set_xlim(-1.05, 1.05)
    ax.set_xlabel("normalised effect of the layer  (positive = layer helps)")
    ax.set_title("The layer on AutoDS-Tools over MLAgentBench", **TITLE)
    save(fig, "fig_signflip")


# ======================================================================
# Fig. kdiscterm: the layer handed to the open harness
# ======================================================================
def fig_kdiscterm():
    names = {"neither": "no file", "discipline": "discipline",
             "discipline, minus time": "discipline,\ntime advice\nremoved",
             "library": "library", "both": "both"}
    cells = mt.KDISC_TERM
    fig, axes = plt.subplots(2, 1, figsize=(COL_W, 2.9), sharex=True)
    x = np.arange(len(cells))
    lost = [100 * c[2] / c[1] for c in cells]
    cols = [C["Terminus-2"] if c[2] / c[1] > 0.25 else C["context"] for c in cells]
    axes[0].bar(x, lost, 0.6, color=cols)
    for xi, c in zip(x, cells):
        axes[0].text(xi, 100 * c[2] / c[1] + 1.5, f"{c[2]}/{c[1]}", ha="center",
                     va="bottom", fontsize=6)
    axes[0].set_title("Trials with no submission, %", **PANEL)
    axes[0].set_ylim(0, 100)
    mins = [c[5] for c in cells]
    axes[1].bar(x, mins, 0.6, color=cols)
    for xi, m in zip(x, mins):
        axes[1].text(xi, m + 0.3, f"{m:.1f}", ha="center", va="bottom", fontsize=6)
    axes[1].set_title("Median minutes per trial", **PANEL)
    axes[1].set_ylim(0, 22)
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels([names[c[0]] for c in cells], fontsize=6)
        ax.grid(axis="y")
        ax.tick_params(axis="x", length=0)
    axes[0].tick_params(labelbottom=False)
    fig.subplots_adjust(hspace=0.35)
    save(fig, "fig_kdiscterm")


# ----------------------------------------------------------------------
# fig_ranks: the agents among the 18 tuned baselines, per task in raw units
# and on top by average rank.  Replaces fig_position and fig_heatmap in the
# paper; both are still generated for the supplementary material.
# ----------------------------------------------------------------------
TICK_OTHER = "#cfcfcf"
TICK_GBDT = "#3a3a3a"
GBDT = {"XGBoost", "LightGBM", "CatBoost"}
NAMED = ["MLP-PLR ens.", "XGBoost", "LightGBM", "CatBoost", "Linear"]
AGENT_STYLE = {"AutoDS-Tools": (C["AutoDS-Tools"], "D"),
               "Terminus-2": (C["Terminus-2"], "o"),
               "FEDOT.LLM": (C["FEDOT.LLM"], "s")}
RULE = "#e4e4e4"                       # faint row guides
RK_Y_TICK0, RK_Y_TICK1 = 0.30, 1.0    # published ticks, both panels
RK_ROWS_B = (-0.22, -0.82, -1.42)      # AutoDS on/off, Terminus-2, FEDOT.LLM
RK_Y_LAB = -2.02                       # end labels (weakest, strongest published)


def rk_task_ranks(pool):
    r = {k: [] for k in pool}
    for j in range(len(mt.TASKS)):
        order = sorted(pool, key=lambda m: -pool[m][j] if mt.HIB[j] else pool[m][j])
        for pos, m in enumerate(order, 1):
            r[m].append(pos)
    return r


def rk_avg_rank(pool):
    return {k: st.mean(v) for k, v in rk_task_ranks(pool).items()}


def rk_corner(agent, sign):
    """Per-task most (sign=+1) or least (sign=-1) favourable value: the best or
    worst of the three attempts."""
    att = mt.ATTEMPTS[agent]
    better = max if sign > 0 else min
    worse = min if sign > 0 else max
    return [better(att[t]) if mt.HIB[j] else worse(att[t]) for j, t in enumerate(mt.TASKS)]


def rk_marker(ax, x, y, name, filled=True, size=20, z=5):
    col, mk = AGENT_STYLE[name]
    if filled:
        ax.scatter([x], [y], s=size, marker=mk, color=col, zorder=z,
                   edgecolor="white", linewidth=0.5)
    else:
        ax.scatter([x], [y], s=size, marker=mk, facecolor="white", edgecolor=col,
                   linewidth=0.9, zorder=z)


def rk_ticks(ax, xs_by_name, y0, y1):
    """The published methods as ticks: the three tuned GBDT dark and full
    height, the other fifteen light and shorter."""
    for name, x in xs_by_name.items():
        gb = name in GBDT
        top = y1 if gb else y0 + 0.62 * (y1 - y0)
        ax.plot([x, x], [y0, top], color=TICK_GBDT if gb else TICK_OTHER,
                lw=1.0 if gb else 0.8, zorder=3 if gb else 2, solid_capstyle="butt")


def rk_row_label(ax, y_axes, text, bold=False, size=7, color=INK):
    ax.text(-0.012, y_axes, text, transform=ax.transAxes, ha="right", va="center",
            fontsize=size, fontweight="bold" if bold else "normal", color=color)


def rk_task_panel(ax, j, nolayer):
    task, hib = mt.TASKS[j], mt.HIB[j]
    pub = {b: mt.PUBLISHED[b][j] for b in mt.PUBLISHED}
    best_name = max(pub, key=pub.get) if hib else min(pub, key=pub.get)
    worst_name = min(pub, key=pub.get) if hib else max(pub, key=pub.get)
    lo, hi = min(pub.values()), max(pub.values())
    span = hi - lo
    means = {a: mt.AGENTS[a][j] for a in mt.AGENTS}
    means["nolayer"] = nolayer[j]
    ext = [v for a in mt.ATTEMPTS for v in mt.ATTEMPTS[a][task]]
    xmin = min(lo, *means.values(), *ext) - 0.04 * span
    xmax = max(hi, *means.values(), *ext) + 0.04 * span
    ax.set_xlim((xmax, xmin) if not hib else (xmin, xmax))
    ax.set_ylim(-2.6, 1.2)
    ax.axis("off")
    if j % 2 == 0:      # alternate bands so the strips of neighbouring tasks separate
        ax.axhspan(-2.6, 1.2, color="#f3f3f3", zorder=-2, lw=0)
    y0 = RK_Y_TICK0
    ax.plot([xmin, xmax], [y0, y0], color="#b9b9b9", lw=0.6, zorder=1)
    rk_ticks(ax, pub, y0, RK_Y_TICK1)
    # end ticks with the weakest and strongest published values
    for name, ha, fmt in ((worst_name, "left", "{v:.4f}  {n}"),
                          (best_name, "right", "{n}  {v:.4f}")):
        x = pub[name]
        ax.plot([x, x], [y0, y0 - 0.14], color="#9a9a9a", lw=0.6, zorder=2)
        ax.text(x, RK_Y_LAB, fmt.format(v=x, n=name), ha=ha, va="top",
                fontsize=6, color=MUTED)
    yA, yT, yF = RK_ROWS_B
    rows = (("AutoDS-Tools", yA), ("Terminus-2", yT), ("FEDOT.LLM", yF))
    for a, y in rows:
        att = mt.ATTEMPTS[a][task]
        ax.plot([min(att), max(att)], [y, y], color=AGENT_STYLE[a][0],
                lw=1.4, alpha=0.9, zorder=4, solid_capstyle="butt")
    rk_marker(ax, means["nolayer"], yA, "AutoDS-Tools", filled=False)
    rk_marker(ax, means["AutoDS-Tools"], yA, "AutoDS-Tools")
    rk_marker(ax, means["Terminus-2"], yT, "Terminus-2")
    rk_marker(ax, means["FEDOT.LLM"], yF, "FEDOT.LLM")
    arrow = "↑" if hib else "↓"
    rk_row_label(ax, 0.74, mt.SHORT[j], bold=True)
    rk_row_label(ax, 0.46, f"{mt.METRIC[j]} {arrow}", size=6.2, color=MUTED)


def rk_rank_panel(ax, rank, rank_range, rank_nolayer):
    ax.set_xlim(21.6, 0.4)          # 1 = best, on the right
    ax.set_ylim(-4.05, 2.75)
    ax.axis("off")
    y0, y1 = RK_Y_TICK0, RK_Y_TICK1
    rows = ((-0.50, "AutoDS-Tools"), (-1.25, "AutoDS-Tools, layer off"),
            (-2.00, "Terminus-2"), (-2.75, "FEDOT.LLM"))
    y_axis = -3.40
    for y, _ in rows:
        ax.plot([21.6, 0.4], [y, y], color=RULE, lw=0.4, zorder=0)
    ax.plot([21.6, 0.4], [y0, y0], color="#b9b9b9", lw=0.6, zorder=1)
    pub_r = {b: rank[b] for b in mt.PUBLISHED}
    rk_ticks(ax, pub_r, y0, y1)
    # named published methods, staggered on two levels above the ticks
    place = {"Linear": (1.20, "center"), "CatBoost": (1.20, "right"),
             "XGBoost": (1.20, "center"), "LightGBM": (1.85, "center"),
             "MLP-PLR ens.": (1.85, "left")}
    for name in NAMED:
        x = pub_r[name]
        yl, ha = place[name]
        ax.plot([x, x], [y1, yl - 0.08], color="#b9b9b9", lw=0.5, zorder=1)
        ax.text(x, yl, f"{name} {x:.1f}", ha=ha, va="bottom", fontsize=6, color=MUTED)
    # rank axis under the rows
    ax.plot([21.6, 0.4], [y_axis, y_axis], color="#9a9a9a", lw=0.6, zorder=1)
    for r in (1, 5, 10, 15, 20):
        ax.plot([r, r], [y_axis, y_axis - 0.12], color="#9a9a9a", lw=0.6)
        ax.text(r, y_axis - 0.18, str(r), ha="center", va="top", fontsize=6, color=MUTED)
    # one row per system, value printed past the better end of the whisker
    values = {"AutoDS-Tools": (rank["AutoDS-Tools"], rank_range["AutoDS-Tools"], True),
              "AutoDS-Tools, layer off": (rank_nolayer, None, False),
              "Terminus-2": (rank["Terminus-2"], rank_range["Terminus-2"], True),
              "FEDOT.LLM": (rank["FEDOT.LLM"], rank_range["FEDOT.LLM"], True)}
    for y, name in rows:
        x, rng, filled = values[name]
        sysname = "AutoDS-Tools" if name.startswith("AutoDS") else name
        better_end = x
        if rng is not None:
            lo, hi = rng
            ax.plot([lo, hi], [y, y], color=AGENT_STYLE[sysname][0], lw=1.4,
                    alpha=0.9, zorder=4, solid_capstyle="butt")
            better_end = lo
        rk_marker(ax, x, y, sysname, filled=filled, size=26)
        ax.text(better_end - 0.35, y, f"{x:.1f}", ha="left", va="center",
                fontsize=6.5, color=INK)
        y_axes = (y - ax.get_ylim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0])
        rk_row_label(ax, y_axes, name, bold=True, size=6.5)


def fig_ranks():
    nolayer = [mt.GRID[t][2] for t in mt.TASKS]
    base = {**mt.PUBLISHED, **mt.AGENTS}
    rank = rk_avg_rank(base)
    rank_nolayer = rk_avg_rank({**mt.PUBLISHED, "Terminus-2": mt.AGENTS["Terminus-2"],
                                "FEDOT.LLM": mt.AGENTS["FEDOT.LLM"],
                                "AutoDS-Tools": nolayer})["AutoDS-Tools"]
    rank_range = {a: sorted([rk_avg_rank({**base, a: rk_corner(a, +1)})[a],
                             rk_avg_rank({**base, a: rk_corner(a, -1)})[a]])
                  for a in mt.AGENTS}
    n = len(mt.TASKS)
    fig = plt.figure(figsize=(FULL_W, 4.9))
    gs = fig.add_gridspec(n + 2, 1, height_ratios=[2.6, 0.42] + [1.0] * n,
                          left=0.135, right=0.995, top=0.865, bottom=0.005, hspace=0.06)
    ax_a = fig.add_subplot(gs[0])
    rk_rank_panel(ax_a, rank, rank_range, rank_nolayer)
    axes_b = [fig.add_subplot(gs[j + 2]) for j in range(n)]
    for j, ax in enumerate(axes_b):
        rk_task_panel(ax, j, nolayer)
    # panel headings, left-aligned with the row-label column
    xh = 0.005
    ya = ax_a.get_position().y1 + 0.006
    fig.text(xh, ya, "a", ha="left", va="bottom", fontsize=8, fontweight="bold")
    fig.text(xh + 0.018, ya, "Average rank over the eight tasks among the 21 methods "
             "of the leaderboard, 1 = best", ha="left", va="bottom", fontsize=7)
    yb = axes_b[0].get_position().y1 + 0.006
    fig.text(xh, yb, "b", ha="left", va="bottom", fontsize=8, fontweight="bold")
    fig.text(xh + 0.018, yb, "Each task in its own metric, better to the right; "
             "end labels give the weakest and strongest published values",
             ha="left", va="bottom", fontsize=7)
    handles = [
        Line2D([], [], marker="D", color=C["AutoDS-Tools"], ls="", ms=4.5,
               label="AutoDS-Tools"),
        Line2D([], [], marker="D", mfc="white", mec=C["AutoDS-Tools"], ls="", ms=4.5,
               label="AutoDS-Tools, layer off"),
        Line2D([], [], marker="o", color=C["Terminus-2"], ls="", ms=4.5, label="Terminus-2"),
        Line2D([], [], marker="s", color=C["FEDOT.LLM"], ls="", ms=4.5, label="FEDOT.LLM"),
        Line2D([], [], marker="|", color=TICK_GBDT, ls="", ms=7, mew=1.0,
               label="tuned XGBoost, LightGBM, CatBoost"),
        Line2D([], [], marker="|", color=TICK_OTHER, ls="", ms=5, mew=0.8,
               label="other 15 published methods"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=6, frameon=False,
               fontsize=6.3, handletextpad=0.3, columnspacing=1.1,
               bbox_to_anchor=(0.5, 0.945))
    fig.suptitle("Three agent systems on one 31B model against the eighteen tuned "
                 "TabReD methods", x=0.5, y=0.985, fontsize=8, fontweight="bold")
    save(fig, "fig_ranks")
    print("   ranks", {k: round(v, 2) for k, v in rank.items() if k in mt.AGENTS},
          "layer off", round(rank_nolayer, 2))


# ======================================================================
# fig_leaderboard (Figure 2 of the remaster, 3 October 2026): a ranked list
# of the 21 methods on the left, the eight tasks on one normalised axis on
# the right.  Replaces fig_ranks, whose per-task strips in raw units needed
# end labels and four rows per task.
# ======================================================================
PUB_DOT = "#b0b0b0"         # published methods
GBDT_DOT = "#3a3a3a"        # tuned XGBoost, LightGBM, CatBoost
BAND = "#e6e6e6"            # middle half of the published methods
SYS_MARK = {"AutoDS-Tools": ("D", C["AutoDS-Tools"]), "Terminus-2": ("o", C["Terminus-2"]),
            "FEDOT.LLM": ("s", C["FEDOT.LLM"])}
NOFILE = "AutoDS-Tools, no file"


def _sys_marker(ax, x, y, name, filled=True, size=26, z=6):
    mk, col = SYS_MARK[name]
    if filled:
        ax.scatter([x], [y], s=size, marker=mk, color=col, zorder=z, edgecolor="white", linewidth=0.5)
    else:
        ax.scatter([x], [y], s=size, marker=mk, facecolor="white", edgecolor=col, linewidth=1.0, zorder=z)


def lb_rank_panel(ax):
    r, pool = mt.ranks()
    avg = {m: st.mean(r[m]) for m in pool}
    nolayer = [mt.GRID[t][2] for t in mt.TASKS]
    # rank of AutoDS-Tools with the file removed, computed in place of the deployed row
    pool2 = {**mt.PUBLISHED, "Terminus-2": mt.AGENTS["Terminus-2"],
             "FEDOT.LLM": mt.AGENTS["FEDOT.LLM"], "AutoDS-Tools": nolayer}
    r_nofile = rk_task_ranks(pool2)["AutoDS-Tools"]
    rk_nofile = st.mean(r_nofile)
    entries = [(m, avg[m]) for m in pool] + [(NOFILE, rk_nofile)]
    entries.sort(key=lambda e: e[1])
    n = len(entries)
    ax.set_ylim(n - 0.4, -0.6)
    ax.set_xlim(21.5, 0.5)   # mirrored: better rank to the right, as in panel b
    ax.set_xticks([1, 5, 10, 15, 20])
    ax.set_xlabel("Average rank over the eight tasks (1 = best)")
    ax.grid(axis="x")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    labels = []
    for i, (m, x) in enumerate(entries):
        if m in mt.AGENTS or m == NOFILE:
            sysname = "AutoDS-Tools" if m == NOFILE else m
            lo, hi = (mt.rank_interval(m) if m != NOFILE
                      else mt.rank_interval(None, task_ranks=r_nofile))
            ax.plot([lo, hi], [i, i], color=SYS_MARK[sysname][1], lw=1.2, zorder=5,
                    solid_capstyle="butt")
            _sys_marker(ax, x, i, sysname, filled=(m != NOFILE), size=30)
            ax.text(lo - 0.45, i, f"{x:.1f}", ha="left", va="center", fontsize=6,
                    color=SYS_MARK[sysname][1], fontweight="bold")
            labels.append((m, True, SYS_MARK[sysname][1]))
        else:
            gb = m in GBDT
            ax.scatter([x], [i], s=16 if gb else 11, color=GBDT_DOT if gb else PUB_DOT, zorder=4)
            labels.append((m, gb, INK if gb else MUTED))
    ax.set_yticks(range(n))
    ax.set_yticklabels([m for m, _b, _c in labels], fontsize=6.3)
    for tick, (_m, bold, col) in zip(ax.get_yticklabels(), labels):
        tick.set_color(col)
        if bold:
            tick.set_fontweight("bold")


def lb_task_panel(ax):
    n = len(mt.TASKS)
    nolayer = [mt.GRID[t][2] for t in mt.TASKS]
    ax.set_ylim(n - 0.4, -0.7)
    ax.set_xlim(-0.12, 1.5)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5])
    ax.set_xticklabels(["0", "", "0.5", "", "1", "", "1.5"])
    ax.set_xlabel("Normalised score\n(0 = weakest, 1 = strongest published method)")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    for x in (0.0, 1.0):
        ax.axvline(x, color="#9a9a9a", lw=0.7, zorder=1)
    dy = {"AutoDS-Tools": -0.22, "Terminus-2": 0.0, "FEDOT.LLM": 0.22}
    for j, task in enumerate(mt.TASKS):
        pub = [mt.normalized(mt.PUBLISHED[b][j], j) for b in mt.PUBLISHED]
        q1, q3 = np.percentile(pub, [25, 75])
        ax.add_patch(plt.Rectangle((q1, j - 0.38), q3 - q1, 0.76, color=BAND, zorder=0, lw=0))
        for b in GBDT:
            x = mt.normalized(mt.PUBLISHED[b][j], j)
            ax.plot([x, x], [j - 0.38, j + 0.38], color=GBDT_DOT, lw=1.0, zorder=2)
        for a in mt.AGENTS:
            att = [mt.normalized(v, j) for v in mt.ATTEMPTS[a][task]]
            y = j + dy[a]
            ax.plot([min(att), max(att)], [y, y], color=SYS_MARK[a][1], lw=1.0, zorder=5)
            _sys_marker(ax, mt.normalized(mt.AGENTS[a][j], j), y, a)
        _sys_marker(ax, mt.normalized(nolayer[j], j), j + dy["AutoDS-Tools"], "AutoDS-Tools", filled=False)
    ax.set_yticks(range(n))
    ax.set_yticklabels([f"{s}  ({m})" for s, m in zip(mt.SHORT, mt.METRIC)], fontsize=6.3)
    for j in range(n - 1):
        ax.axhline(j + 0.5, color=GRID_C, lw=0.5, zorder=0)


def fig_leaderboard():
    fig = plt.figure(figsize=(FULL_W, 3.75))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.35], left=0.145, right=0.985,
                          top=0.85, bottom=0.135, wspace=0.40)
    ax_a = fig.add_subplot(gs[0]); ax_b = fig.add_subplot(gs[1])
    lb_rank_panel(ax_a); lb_task_panel(ax_b)
    for ax, letter, head in ((ax_a, "a", "Leaderboard by average rank"),
                             (ax_b, "b", "Each task on the normalised scale")):
        ax.text(-0.02, 1.015, letter, transform=ax.transAxes, ha="right", va="bottom",
                fontsize=8.5, fontweight="bold")
        ax.text(0.0, 1.015, head, transform=ax.transAxes, ha="left", va="bottom", fontsize=7)
    handles = [
        Line2D([], [], marker="D", color=C["AutoDS-Tools"], ls="", ms=4.5, label="AutoDS-Tools"),
        Line2D([], [], marker="D", mfc="white", mec=C["AutoDS-Tools"], ls="", ms=4.5,
               label="AutoDS-Tools without its instruction file"),
        Line2D([], [], marker="o", color=C["Terminus-2"], ls="", ms=4.5, label="Terminus-2"),
        Line2D([], [], marker="s", color=C["FEDOT.LLM"], ls="", ms=4.5, label="FEDOT.LLM"),
        Line2D([], [], marker="|", color=GBDT_DOT, ls="", ms=7, mew=1.0,
               label="tuned XGBoost, LightGBM, CatBoost"),
        plt.Rectangle((0, 0), 1, 1, color=BAND, label="middle half of the 18 published methods"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, fontsize=6.3,
               handletextpad=0.4, columnspacing=1.4, bbox_to_anchor=(0.56, 1.0))
    fig.subplots_adjust(top=0.84)
    save(fig, "fig_leaderboard")


# ======================================================================
# fig_ablations (Figure 3 of the remaster): every factor the paper varies,
# as the paired difference on the normalised scale with a 95% bootstrap
# interval over tasks, and the share of trials that ended without a
# submission.  One figure answers "what moves the result".
# ======================================================================
ABL_ROWS = [
    # (group header or None, left = reference, right = changed, comparison key
    #  (right minus left), system of the right side, lost key right, lost key
    #  left[, system of the left side when two systems are compared])
    ("Harness, no instruction file", None, None, None, None, None, None),
    (None, "Terminus-2", "AutoDS-Tools", "archAutoDSvsTerminus", "AutoDS-Tools", "autods_none", "term_enriched", "Terminus-2"),
    (None, "Terminus-2", "FEDOT.LLM", "shipFedotvsTerminus", "FEDOT.LLM", "fedot", "term_stock", "Terminus-2"),
    (None, "FEDOT.LLM", "AutoDS-Tools", "archAutoDSvsFedot", "AutoDS-Tools", "autods_none", "fedot", "FEDOT.LLM"),
    ("Instruction file in AutoDS-Tools", None, None, None, None, None, None),
    (None, "no file", "whole file", "fileBoth", "AutoDS-Tools", "autods_both", "autods_none"),
    (None, "no file", "library part", "fileTool", "AutoDS-Tools", "autods_tool", "autods_none"),
    (None, "no file", "discipline part", "fileDisc", "AutoDS-Tools", "autods_disc", "autods_none"),
    ("Same file in the Terminus-2 task", None, None, None, None, None, None),
    (None, "no file", "whole file", "termBoth", "Terminus-2", "term_kboth", "term_none_axis"),
    (None, "no file", "library part", "termTool", "Terminus-2", "term_ktool", "term_none_axis"),
    (None, "no file", "discipline part", "termDisc", "Terminus-2", "term_kdisc", "term_none_axis"),
    (None, "no file", "discipline, time advice cut", "termTrim", "Terminus-2", "term_kdisc_trim", "term_none_axis"),
    ("Container image, Terminus-2", None, None, None, None, None, None),
    (None, "stock", "libraries pre-installed", "image", "Terminus-2", "term_enriched", "term_stock"),
    ("Language model, Terminus-2", None, None, None, None, None, None),
    (None, "gemma-4-31b", "gemma-4-26b-a4b", "termSmall", "Terminus-2", "term_small", "term_none_axis"),
    (None, "gemma-4-31b", "glm-4.7", "termBig", "Terminus-2", "term_big", "term_none_axis"),
    ("Language model, AutoDS-Tools", None, None, None, None, None, None),
    (None, "gemma-4-31b", "gemma-4-26b-a4b", "autodsSmall", "AutoDS-Tools", "autods_small", "autods_both"),
    (None, "gemma-4-31b", "glm-4.7", "autodsBig", "AutoDS-Tools", "autods_big", "autods_both"),
    ("Instruction file in AutoDS-Tools, MLAgentBench", None, None, None, None, None, None),
    (None, "no file", "whole file", None, "AutoDS-Tools", "mlab_autods_file", "mlab_autods_none"),
]
ABL_XLIM = (-0.32, 0.32)


def fig_ablations():
    """Every factor the paper varies.  One row per comparison: the reference
    configuration is named left of the axes, the changed one right of the
    accuracy axis.  Both panels read the same way: a mark right of zero means
    the right configuration is better.  Accuracy: paired difference in mean
    normalised score.  Reliability: change in the share of trials that ended
    with a submission."""
    from matplotlib.transforms import blended_transform_factory as blend
    comps = mt.comparison_set()
    rows = ABL_ROWS
    n = len(rows)
    W, H = FULL_W, 4.6
    fig = plt.figure(figsize=(W, H))
    # columns in inches: left labels | accuracy | right labels + tasks | gap | reliability | counts
    x0, wl, wa, wr, gap, wrel = 0.06, 0.80, 2.05, 2.08, 0.52, 0.95
    bot, top = 0.42, H - 0.42
    ax = fig.add_axes([(x0 + wl) / W, bot / H, wa / W, (top - bot) / H])
    xrel = x0 + wl + wa + wr + gap
    ax2 = fig.add_axes([xrel / W, bot / H, wrel / W, (top - bot) / H], sharey=ax)
    ax.set_ylim(n - 0.5, -0.5)
    ax.set_xlim(*ABL_XLIM)
    ax.set_xticks([-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3])
    ax.set_xticklabels(["0.3", "0.2", "0.1", "0", "0.1", "0.2", "0.3"])
    ax.axvline(0, color="#9a9a9a", lw=0.8, zorder=1)
    ax.set_xlabel("Difference in mean normalised score", fontsize=6.6)
    ax.grid(axis="x")
    ax.tick_params(axis="y", length=0, labelleft=False)
    ax.spines["left"].set_visible(False)
    ax2.set_xlim(-100, 100)
    ax2.set_xticks([-100, -50, 0, 50, 100])
    ax2.set_xticklabels(["100", "", "0", "", "100"])
    ax2.axvline(0, color="#9a9a9a", lw=0.8, zorder=1)
    ax2.set_xlabel("Difference, percentage points", fontsize=6.6)
    ax2.tick_params(axis="y", length=0, labelleft=False)
    ax2.spines["left"].set_visible(False)
    ax2.grid(axis="x")
    tr = blend(fig.transFigure, ax.transData)
    xl = (x0 + wl - 0.06) / W            # right edge of the left labels
    xr = (x0 + wl + wa + 0.11) / W       # left edge of the right labels
    xt = (x0 + wl + wa + wr - 0.34) / W  # centre of the task-count column
    xc = (xrel + wrel + 0.06) / W        # submission count of the right side
    xcl = (xrel - 0.06) / W              # submission count of the left side
    # grey band behind the task counts, so the column reads as its own block
    from matplotlib.patches import Rectangle
    fig.add_artist(Rectangle((xt - 0.30 / W, bot / H), 0.60 / W, (top + 0.30 - bot) / H,
                             transform=fig.transFigure, color="#ececec", lw=0, zorder=0))
    for i, (head, left, right, key, sysname, lk_a, lk_b, *rest) in enumerate(rows):
        left_sys = rest[0] if rest else None
        if head:
            for a in (ax, ax2):
                a.axhspan(i - 0.5, i + 0.5, color="#f3f3f3", lw=0, zorder=0)
            fig.text(x0 / W, i, head, transform=tr, ha="left", va="center",
                     fontsize=6.6, fontweight="bold", color=INK)
            continue
        col = C[sysname]
        fig.text(xl, i, left, transform=tr, ha="right", va="center", fontsize=6.4,
                 color=C[left_sys] if left_sys else INK, fontweight="bold" if left_sys else "normal")
        fig.text(xr, i, right, transform=tr, ha="left", va="center", fontsize=6.4,
                 color=col if left_sys else INK, fontweight="bold" if left_sys else "normal")
        if key is None:
            ax.text(0, i, "no common scale, see Table 4", ha="center", va="center",
                    fontsize=6, color=MUTED, style="italic")
        else:
            s = mt.paired_stats(*comps[key])
            lo, hi = max(s["lo"], ABL_XLIM[0]), min(s["hi"], ABL_XLIM[1])
            # two systems: the part of the interval left of zero takes the colour of
            # the left system, the part right of zero that of the right system, and
            # the point takes the marker of the system on whose side the mean lies
            col_l = C[left_sys] if left_sys else col
            if lo < 0:
                ax.plot([lo, min(hi, 0)], [i, i], color=col_l, lw=1.3, zorder=4, solid_capstyle="butt")
            if hi > 0:
                ax.plot([max(lo, 0), hi], [i, i], color=col, lw=1.3, zorder=4, solid_capstyle="butt")
            for v, side in ((s["lo"], -1), (s["hi"], 1)):
                if v < ABL_XLIM[0] or v > ABL_XLIM[1]:   # interval runs off the axis
                    ax.annotate("", xy=(ABL_XLIM[1] if side > 0 else ABL_XLIM[0], i),
                                xytext=((ABL_XLIM[1] - 0.02) if side > 0 else (ABL_XLIM[0] + 0.02), i),
                                arrowprops=dict(arrowstyle="-|>", color=col if side > 0 else col_l,
                                                lw=1.0, mutation_scale=6))
            x = min(max(s["diff"], ABL_XLIM[0] + 0.005), ABL_XLIM[1] - 0.005)
            winner = sysname if (s["diff"] >= 0 or not left_sys) else left_sys
            ax.scatter([x], [i], s=24, marker=SYS_MARK[winner][0], color=C[winner], zorder=6,
                       edgecolor="white", linewidth=0.5)
            ra, rb = comps[key]                        # right, left per task
            left_wins = sum(1 for j in range(len(mt.TASKS))
                            if ra[j] is not None and rb[j] is not None and ra[j] != rb[j]
                            and (rb[j] > ra[j]) == mt.HIB[j])
            fig.text(xt, i, f"{left_wins} : {s['wins']}", transform=tr, ha="center", va="center",
                     fontsize=6.2, color=INK)
        la, ta = mt.LOST[lk_a]
        lb, tb = mt.LOST[lk_b]
        sa, sb = ta - la, tb - lb                      # trials with a submission
        d = 100 * sa / ta - 100 * sb / tb
        if abs(d) > 0.5:
            ax2.barh(i, d, height=0.55, color=col, zorder=3, lw=0)
        cc = INK
        fig.text(xcl, i, f"{sb}/{tb}", transform=tr, ha="right", va="center", fontsize=5.8, color=cc)
        fig.text(xc, i, f"{sa}/{ta}", transform=tr, ha="left", va="center", fontsize=5.8, color=cc)
    # headers
    hy = 1.012
    for a_, title, lt, rt in ((ax, "Accuracy", "← left better", "right better →"),
                              (ax2, "Trials with a submission", "← left", "right →")):
        a_.text(0.5, hy + 0.035, title, transform=a_.transAxes, ha="center", va="bottom",
                fontsize=7, fontweight="bold")
        a_.text(0.0, hy, lt, transform=a_.transAxes, ha="left", va="bottom", fontsize=6.0, color=MUTED)
        a_.text(1.0, hy, rt, transform=a_.transAxes, ha="right", va="bottom", fontsize=6.0, color=MUTED)
    fig.text(xt, (top + 0.02) / H, "tasks won\nleft : right", ha="center", va="bottom",
             fontsize=5.8, color=MUTED)

    save(fig, "fig_ablations")

if __name__ == "__main__":
    for fn in (fig_position, fig_heatmap, fig_grid, fig_modelaxis, fig_walltime,
               fig_signflip, fig_kdiscterm, fig_ranks, fig_leaderboard, fig_ablations):
        fn()
