#!/usr/bin/env python3
"""Render the case-study data figure (figures/fig_cases.pdf).

Three panels, one per scientific case, drawn from the original open data so
the reader sees what each task is about rather than a benchmark id:

  maize    G2F yield trials (Kick et al., G3 2023; Zenodo 6916775, CC-BY 3.0):
           grain yield per location-year, with the held-out environments of the
           official split highlighted. The task is yield of hybrids in
           environments the model has never seen.
  F-DATA   Fugaku job logs (Antici et al., Sci. Data 2025; Zenodo 11467483,
           CC-BY 4.0), month 2021-04: success rate against requested node
           count. The task is flagging jobs likely to fail at submission time.
  OpenPoly literature-curated polymer table (Wang et al., CJPS 2025; GitHub
           WangGroupFDU/Openpoly_benchmark, MIT): glass-transition temperature
           against chain rigidity read off the PSMILES string.

Sources are downloaded once into .cache/cases/ (set CASES_DATA_DIR to reuse a
copy). Run from paper/:  python3 make_case_figures.py
"""
import os
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from make_figures import C, CASE, COL_W, FULL_W, GRID_C, INK, MUTED, PANEL, save  # noqa: E402

DATA = Path(os.environ.get("CASES_DATA_DIR", Path(__file__).parent / ".cache" / "cases"))
SRC = {
    "maize.csv": "https://zenodo.org/records/6916775/files/Train_Test_Split_Reference_Phenotypes.csv",
    "fdata_21_04.parquet": "https://zenodo.org/records/11467483/files/21_04.parquet",
    "openpoly.csv": ("https://raw.githubusercontent.com/WangGroupFDU/Openpoly_benchmark/"
                     "main/data/final_polymer_properties_fromliterature.csv"),
}
# Case colours of the house palette (figures/STYLE.md): never a system colour.
TEST_C = CASE["highlight"]    # held-out / target of prediction, reference lines
TRAIN_C = CASE["context"]     # training or background data
ACCENT = CASE["primary"]      # the data the panel shows


def fetch(name):
    p = DATA / name
    if not p.exists():
        DATA.mkdir(parents=True, exist_ok=True)
        print("downloading", SRC[name])
        urllib.request.urlretrieve(SRC[name], p)
    return p


# ---------------------------------------------------------------- maize
def panel_maize(ax):
    m = pd.read_csv(fetch("maize.csv"), low_memory=False)
    m = m[m.GrainYield.notna() & m.Set.isin(["Train", "Test"])]
    m["env"] = m.ExperimentCode.astype(str) + "_" + m.Year.astype(str)
    g = (m.groupby(["env", "Year", "Set"])["GrainYield"]
          .agg(["median", lambda s: s.quantile(0.25), lambda s: s.quantile(0.75), "size"])
          .reset_index())
    g.columns = ["env", "Year", "Set", "med", "q1", "q3", "n"]
    g = g.sort_values(["Year", "med"]).reset_index(drop=True)
    x = np.arange(len(g))
    for s, col, z in (("Train", TRAIN_C, 1), ("Test", TEST_C, 2)):
        sel = g.Set == s
        ax.vlines(x[sel], g.q1[sel], g.q3[sel], color=col, lw=0.8, zorder=z, alpha=0.9)
        ax.scatter(x[sel], g.med[sel], s=6, color=col, zorder=z + 1, lw=0)
    # year bands
    for y, grp in g.groupby("Year"):
        lo, hi = grp.index.min(), grp.index.max()
        ax.text((lo + hi) / 2, 8, str(y), ha="center", va="bottom", fontsize=6, color=MUTED)
        if lo > 0:
            ax.axvline(lo - 0.5, color=GRID_C, lw=0.6)
    ax.set_xlim(-1, len(g))
    ax.set_ylim(0, 320)
    ax.set_xticks([])
    ax.set_ylabel("grain yield of field plots, bu/acre")
    ax.set_xlabel(f"one mark = one site in one year ({len(g)} in all)", fontsize=6.5)
    ax.grid(axis="y")
    ax.set_title("Maize yield in unseen fields", **PANEL)
    ax.scatter([], [], s=10, color=TRAIN_C, label=f"sites used for training")
    ax.scatter([], [], s=10, color=TEST_C, label=f"sites to predict (held out)")
    ax.legend(loc="upper left", handletextpad=0.3)


# ---------------------------------------------------------------- F-DATA
def panel_fdata(ax):
    f = pd.read_parquet(fetch("fdata_21_04.parquet"), columns=["nnumr", "ec"])
    f = f[f.ec.notna()]
    f["ok"] = (f.ec == 0)
    edges = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096, 1e9]
    f["bin"] = pd.cut(f.nnumr, edges, right=True)
    g = f.groupby("bin", observed=True)["ok"].agg(["mean", "size"]).reset_index()
    x = np.arange(len(g))
    majority = f.ok.mean()
    ax.bar(x, 100 * g["mean"], width=0.72, color=ACCENT, lw=0, zorder=2)
    ax.axhline(100 * majority, color=TEST_C, lw=0.9, ls="--", zorder=3)
    ax.text(len(g) - 0.4, 100 * majority - 0.8, f"{100*majority:.1f}%: always guess \"success\"",
            ha="right", va="top", fontsize=6, color=TEST_C,
            bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.85))
    for xi, (mean, n) in enumerate(zip(g["mean"], g["size"])):
        ax.text(xi, 62, f"{n/1000:.0f}k" if n >= 1000 else str(n), ha="center", va="bottom",
                fontsize=5, color="white", rotation=90)
    labels = ["1", "2", "3-4", "5-8", "9-16", "17-32", "33-64", "65-128", "129-256",
              "257-512", "513-1k", "1k-4k", ">4k"]
    ax.set_xticks(x)
    ax.set_xticklabels(labels[:len(g)], rotation=60, ha="right", fontsize=5)
    ax.set_ylim(60, 100)
    ax.set_xlim(-0.6, len(g) - 0.4)
    ax.set_ylabel("jobs that finished successfully, %")
    ax.set_xlabel("compute nodes requested (job count in bar)", fontsize=6.5, labelpad=1)
    ax.grid(axis="y")
    ax.set_title("Fugaku jobs: will this job fail?", **PANEL)


# ---------------------------------------------------------------- OpenPoly
def rigidity(psmiles):
    """Aromatic-atom fraction of the repeat unit, a crude chain-rigidity index."""
    from rdkit import Chem
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")
    mol = Chem.MolFromSmiles(psmiles.replace("[*]", "C").replace("*", "C"))
    if mol is None or mol.GetNumHeavyAtoms() == 0:
        return np.nan, np.nan
    arom = sum(a.GetIsAromatic() for a in mol.GetAtoms())
    return arom / mol.GetNumHeavyAtoms(), mol.GetNumHeavyAtoms()


def panel_openpoly(ax):
    o = pd.read_csv(fetch("openpoly.csv"))
    o = o[["Name", "PSMILES", "Tg (K)"]].dropna()
    o[["arom", "heavy"]] = o.PSMILES.apply(lambda s: pd.Series(rigidity(s)))
    o = o.dropna()
    rng = np.random.default_rng(0)
    jitter = rng.uniform(-0.012, 0.012, len(o))
    ax.scatter(o.arom + jitter, o["Tg (K)"], s=7, color=ACCENT, alpha=0.55, lw=0, zorder=2,
               label=f"one dot = one polymer ({len(o)})")
    # trend by bins
    bins = pd.cut(o.arom, [-0.01, 0.001, 0.35, 0.6, 1.0])
    grp = o.groupby(bins, observed=True)
    med, cen = grp["Tg (K)"].median(), grp["arom"].mean()
    ax.plot(cen.values, med.values, color=TEST_C, lw=1.2, marker="o", ms=3, zorder=3,
            label="typical value (median)")
    ax.set_xlabel("share of ring atoms in the repeat unit", fontsize=6.5)
    ax.set_ylabel("$T_g$: where the plastic softens, K")
    ax.set_xlim(-0.04, 1.04)
    ax.grid(axis="y")
    ax.set_title("Polymers: softening point", **PANEL)
    ax.text(0.0, 128, "flexible chains", ha="left", va="bottom", fontsize=6, color=MUTED)
    ax.text(1.0, 128, "rigid chains", ha="right", va="bottom", fontsize=6, color=MUTED)
    ax.set_ylim(120, 610)
    ax.legend(loc="upper left", handletextpad=0.3)


# ---------------------------------------------------------------- results
import make_tables as mt  # noqa: E402

RES_ROWS = [  # (label, system, text) from top to bottom
    ("AutoDS-Tools, with library section", "AutoDS-Tools", "prescribed"),
    ("Terminus-2, with library section", "Terminus-2", "prescribed"),
    ("Terminus-2, plain text", "Terminus-2", "plain"),
    ("FEDOT.LLM, plain text", "FEDOT.LLM", "plain"),
]
RES_META = {
    "maize-yield": ("Pearson $r$ (higher is better)", (0.40, 0.72)),
    "fdata-exit": ("accuracy (higher is better)", (0.875, 0.965)),
    "openpoly-tg": ("$R^2$ (higher is better)", (0.40, 0.95)),
}
MARK = {"AutoDS-Tools": "D", "Terminus-2": "o", "FEDOT.LLM": "s"}


def panel_results(ax, task, first):
    label, (lo, hi) = RES_META[task]
    author = mt.CASE_META[task][2]
    n = len(RES_ROWS)
    ax.set_ylim(n - 0.5, -0.5)
    ax.set_xlim(lo, hi)
    ax.axvline(author, color=INK, lw=0.9, ls="--", zorder=2)
    ax.text(author, -0.45, f"authors {author:.3f}", ha="center", va="bottom", fontsize=6, color=INK)
    if task == "fdata-exit":
        floor = mt.CASE_FLOORS[task]
        ax.axvline(floor, color=MUTED, lw=0.7, ls=":", zorder=1)
        ax.text(floor, n - 0.55, "constant", ha="center", va="top", fontsize=5.5, color=MUTED)
    for i, (lab, system, text) in enumerate(RES_ROWS):
        key = (task, system, text)
        if key not in mt.CASES:
            ax.text((lo + hi) / 2, i, "not applicable", ha="center", va="center", fontsize=6, color=MUTED)
            continue
        vals, _mins = mt.CASES[key]
        col = C[system]
        got = [v for v in vals if v is not None]
        lost = len(vals) - len(got)
        rng = np.random.default_rng(1)
        for v in got:
            ax.scatter([v], [i + rng.uniform(-0.12, 0.12)], s=22, marker=MARK[system], color=col,
                       zorder=4, edgecolor="white", linewidth=0.5)
        if lost:
            xs = np.linspace(lo + 0.04 * (hi - lo), lo + 0.04 * (hi - lo) + 0.05 * (hi - lo) * (lost - 1), lost)
            ax.scatter(xs, [i] * lost, s=24, marker="x", color=col, linewidth=1.1, zorder=4)
    ax.set_yticks(range(n))
    ax.set_yticklabels([r[0] for r in RES_ROWS] if first else [""] * n, fontsize=6)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x")
    ax.set_xlabel(label, fontsize=6.5)


def fig_cases():
    fig = plt.figure(figsize=(FULL_W, 3.7))
    gs_top = fig.add_gridspec(1, 3, left=0.075, right=0.99, top=0.95, bottom=0.52, wspace=0.40)
    gs_bot = fig.add_gridspec(1, 3, left=0.20, right=0.99, top=0.27, bottom=0.085, wspace=0.22)
    top = [fig.add_subplot(gs_top[0, k]) for k in range(3)]
    panel_maize(top[0]); panel_fdata(top[1]); panel_openpoly(top[2])
    bottom = [fig.add_subplot(gs_bot[0, k]) for k in range(3)]
    for k, task in enumerate(["maize-yield", "fdata-exit", "openpoly-tg"]):
        panel_results(bottom[k], task, first=(k == 0))
    fig.text(0.075, 0.955, "a", ha="left", va="bottom", fontsize=8.5, fontweight="bold")
    fig.text(0.02, 0.305, "b", ha="left", va="bottom", fontsize=8.5, fontweight="bold")
    fig.text(0.04, 0.305, "Every attempt against the author baseline (dashed); cross: no submission",
             ha="left", va="bottom", fontsize=6.5)
    save(fig, "fig_cases")


if __name__ == "__main__":
    fig_cases()
