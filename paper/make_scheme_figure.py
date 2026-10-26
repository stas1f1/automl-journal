"""General scheme of an agentic AutoML system (figures/fig_scheme.pdf).

An illustration, so it follows the whole house style of figures/STYLE.md,
part 2: Avenir Next Regular and Bold, sizes in mm, line widths in pt. The
font is not in the repository. Pass the folder with the TrueType files
(converted from the OTF release, so that the PDF embeds TrueType like Fig. 2):

    python3 make_scheme_figure.py "<folder with Avenir Next Regular.ttf>"
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

FONT_DIR = Path(sys.argv[1])
for f in ("Avenir Next Regular.ttf", "Avenir Next Bold.ttf"):
    font_manager.fontManager.addfont(str(FONT_DIR / f))
plt.rcParams.update({"font.family": "Avenir Next W1G", "pdf.fonttype": 42})

OUT = Path(__file__).parent / "figures" / "fig_scheme.pdf"

# colours from STYLE.md, part 2
TEXT, TEXT2, ARROW, OUTLINE = "#1A1A1A", "#6E6E6E", "#4A4A4A", "#A0A0A0"
STICKER, STICKER_BAR, TAPE = "#FFF1C1", "#EDE0B3", "#E6E2D6"
CHEVRONS = ["#E6E8EB", "#D7DBE0", "#C9CED4", "#BAC0C9"]
CHEVRON_TEXT = "#29323E"
CARD = "#F2F3F5"          # tint 7 % of the chevron tone #4A5A70
SHEET_CORNER = "#E3E3E3"

W, H = 180, 84            # mm
MM = 1 / 25.4

fig = plt.figure(figsize=(W * MM, H * MM))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")


def box(x, y, w, h, r=1.8, fc="white", ec=OUTLINE, lw=0.6, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=z))


def text(x, y, s, size=8, bold=False, color=TEXT, ha="center", va="center", z=5):
    ax.text(x, y, s, fontsize=size, fontweight="bold" if bold else "normal",
            color=color, ha=ha, va=va, zorder=z, linespacing=1.15)


def named(x, y, w, h, name, note, thick=False, size=8):
    """A block with a bold name and a regular note under it."""
    box(x, y, w, h, ec=TEXT if thick else OUTLINE, lw=1.1 if thick else 0.6)
    text(x + w / 2, y + h - 3.0, name, size=size, bold=True)
    text(x + w / 2, y + (h - 4.6) / 2, note, size=7, color=TEXT2)


def arrow(p, q, lw=0.6, color=ARROW, rad=0.0, z=4, head=(1.2, 1.0)):
    # head length and width in mm, converted to points (mutation_scale=1)
    hl, hw = head[0] / 25.4 * 72, head[1] / 25.4 * 72
    a = FancyArrowPatch(p, q, arrowstyle=f"-|>,head_length={hl:.2f},head_width={hw / 2:.2f}",
                        connectionstyle=f"arc3,rad={rad}", lw=lw, color=color,
                        shrinkA=0, shrinkB=0, zorder=z, mutation_scale=1)
    ax.add_patch(a)


def polyline(points, lw=0.6, color=ARROW, head=True, z=4):
    xs, ys = zip(*points)
    ax.plot(xs[:-1] + (xs[-1],), ys[:-1] + (ys[-1],), color=color, lw=lw,
            solid_capstyle="butt", solid_joinstyle="round", zorder=z)
    if head:
        arrow(points[-2], points[-1], lw=lw, color=color)


def chevron(x, y, w, h, color, label, first=False):
    n = 2.2  # depth of the notch and of the point, mm
    pts = [(x, y), (x + w - n, y), (x + w, y + h / 2), (x + w - n, y + h), (x, y + h)]
    if not first:
        pts.append((x + n, y + h / 2))
    ax.add_patch(Polygon(pts, closed=True, fc=color, ec="none", zorder=2,
                         joinstyle="round"))
    text(x + w / 2 + (n / 2 if not first else 0), y + h / 2, label, size=7.5, bold=True,
         color=CHEVRON_TEXT, va="center_baseline")


def sheets(x, y, w, h):
    for k in (2, 1, 0):
        dx = dy = 0.9 * k
        c = 2.0
        pts = [(x + dx, y - dy), (x + dx + w, y - dy), (x + dx + w, y - dy + h - c),
               (x + dx + w - c, y - dy + h), (x + dx, y - dy + h)]
        ax.add_patch(Polygon(pts, closed=True, fc="white", ec=ARROW, lw=0.55, zorder=3 + (2 - k) * 0.1))
        if k == 0:
            ax.add_patch(Polygon([(x + w - c, y + h), (x + w - c, y + h - c), (x + w, y + h - c)],
                                 closed=True, fc=SHEET_CORNER, ec=ARROW, lw=0.55, zorder=3.3))


def sticker(x, y, w, h):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.3",
                                fc=STICKER, ec="none", zorder=2))
    ax.add_patch(FancyBboxPatch((x, y), w, 1.2, boxstyle="round,pad=0,rounding_size=0.3",
                                fc=STICKER_BAR, ec="none", zorder=2.1))
    ax.add_patch(FancyBboxPatch((x + w / 2 - 3.5, y + h - 1.1), 7, 2.2,
                                boxstyle="round,pad=0,rounding_size=0.3",
                                fc=TAPE, ec="none", zorder=2.2, alpha=0.95))


# --- the work of a data scientist: phases on top --------------------------
CX0, CX1 = 40, 140         # system card
cw, gap = (CX1 - CX0 - 3 * 1.0) / 4, 1.0
for i, (lab, col) in enumerate(zip(["explore", "plan", "write code", "run"], CHEVRONS)):
    chevron(CX0 + i * (cw + gap), 72.0, cw, 4.6, col, lab, first=(i == 0))
# repeat loop over the phases
yl = 79.0
polyline([(CX1 - cw / 2, 76.6), (CX1 - cw / 2, yl), (CX0 + cw / 2, yl), (CX0 + cw / 2, 76.8)],
         color=TEXT2)
text((CX0 + CX1) / 2, yl + 0.9, "repeat until a submission is ready", size=7, color=TEXT2, va="bottom")
text(CX0 - 3, 74.3, "the work of\na data scientist", size=7, color=TEXT2, ha="right")

# --- task ----------------------------------------------------------------
box(3, 29, 29, 27)
text(17.5, 52.2, "task", bold=True)
text(17.5, 41.5, "training data\ndescription\nmetric\ntime budget", size=7, color=TEXT2)
arrow((32, 42.5), (CX0, 42.5))

# --- system card -----------------------------------------------------------
box(CX0, 13, CX1 - CX0, 56, fc=CARD, ec="none", z=1)
text(CX0 + 2.5, 66.3, "agentic AutoML system", size=7.5, bold=True, ha="left")

# harness: four components
hy, hh = 45.5, 12.5
hx0, hx1 = CX0 + 4.5, CX1 - 4.5
hw = (hx1 - hx0 - 3 * 2) / 4
box(CX0 + 2.5, 43.5, CX1 - CX0 - 5, 19.5, fc="none", ec=OUTLINE, lw=0.6, z=1.5)
text(hx0, 60.6, "harness", size=7.5, bold=True, ha="left")
parts = [("actions", "shell, code,\nlibrary calls"),
         ("control", "who sets\nthe plan"),
         ("execution loop", "output and errors\nback to the model"),
         ("memory", "what passes\nbetween steps")]
for i, (n_, note) in enumerate(parts):
    named(hx0 + i * (hw + 2), hy, hw, hh, n_, note, size=7.5)

# language model, decides
lx, ly, lw_, lh = 66, 25, 48, 10
named(lx, ly, lw_, lh, "language model", "chooses the next action", thick=True)
arrow((lx + lw_ / 2 - 5, ly + lh), (lx + lw_ / 2 - 5, 43.5))
arrow((lx + lw_ / 2 + 5, 43.5), (lx + lw_ / 2 + 5, ly + lh))
text(lx + lw_ / 2 - 6, (ly + lh + 43.5) / 2, "action", size=7, ha="right")
text(lx + lw_ / 2 + 6, (ly + lh + 43.5) / 2, "result", size=7, ha="left")

# knowledge, the yellow sticker
sticker(CX0 + 4.5, 16, 20, 21)
text(CX0 + 14.5, 31.2, "knowledge", size=7.5, bold=True)
text(CX0 + 14.5, 23.3, "instruction file,\nretrieved,\nlibrary docs", size=7)
arrow((CX0 + 24.5, 30), (lx, 30), lw=0.8, head=(1.1, 0.96))

# model builder
bx, by, bw, bh = 116.5, 16, 19, 25
box(bx, by, bw, bh)
text(bx + bw / 2, by + bh - 3.0, "model\nbuilder", bold=True, va="top")
box(bx + 2, by + 9.6, bw - 4, 4.6, r=1.0)
text(bx + bw / 2, by + 11.9, "own code", size=7)
box(bx + 2, by + 2.6, bw - 4, 6.0, r=1.0)
text(bx + bw / 2, by + 5.6, "AutoML\nlibrary", size=7)
arrow((lx + lw_, 30), (bx, 30))

# environment
box(CX0, 3, CX1 - CX0, 6.4, r=2.8)
r = fig.canvas.get_renderer()
t1 = ax.text(0, 6.2, "environment", fontsize=8, fontweight="bold", color=TEXT, va="center", zorder=5)
t2 = ax.text(0, 6.2, "container, libraries, hardware, time limit", fontsize=8, color=TEXT,
             va="center", zorder=5)
to_mm = lambda t: t.get_window_extent(r).width / fig.dpi * 25.4
w1, w2, sp = to_mm(t1), to_mm(t2), 1.8
x0 = (CX0 + CX1 - w1 - sp - w2) / 2
t1.set_x(x0)
t2.set_x(x0 + w1 + sp)

# --- outcome -----------------------------------------------------------------
sx, sy, sw, sh = 152, 44, 17, 14
sheets(sx, sy, sw, sh)
text(sx + sw / 2, sy + sh / 2, "submission", size=7)
polyline([(bx + bw, 28.5), (144, 28.5), (144, 51), (sx, 51)])
text(sx + sw / 2 + 0.9, sy - 4.6, "or none", size=7, color=TEXT2)

outs = [("reliability", "share of attempts\nwith a submission"),
        ("accuracy", "score of a submission"),
        ("cost", "time and tokens")]
oy = 34
for name, note in outs:
    text(150, oy, name, size=7, bold=True, ha="left", va="top")
    text(150, oy - 3.0, note, size=7, color=TEXT2, ha="left", va="top")
    oy -= 3.0 + 3.0 * (note.count("\n") + 1) + 0.6

fig.savefig(OUT)
print("wrote", OUT)
