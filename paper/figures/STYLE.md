# House style for the figures (6 October 2026)

Replaces the Okabe-Ito palette; every figure as it was before the change is in
`figures/archive_2026-10-06_okabe-ito/` (with the TikZ source of Fig. 1 and
the colour definitions from `main.tex`). Swatch: `STYLE_swatch.png`.
The colours are defined once, in `make_figures.py` (`C`, `KNOWLEDGE`, `CASE`,
neutrals); `make_case_figures.py` imports them, and Fig. 1 takes them from the
`\definecolor` lines in `main.tex`.

## Rules

1. Each system keeps one colour and one marker in every figure:
   AutoDS-Tools indigo diamond, Terminus-2 raspberry circle, FEDOT.LLM
   mustard square. Open marker = the same system without its instruction file.
2. Colour stands for a system only. Everything else (published methods,
   bands, reference lines) is a warm stone grey.
3. The instruction file has its own colour, a light lime like a sticky note,
   used only in Fig. 1.
4. The case-study data panels (Fig. 3a) use three colours of their own that
   never stand for a system.

## Colours

| Role | Name | Hex |
|---|---|---|
| AutoDS-Tools | indigo | `#283C8C` |
| Terminus-2 | raspberry | `#C8457E` |
| FEDOT.LLM | mustard | `#B98A17` |
| instruction file (Fig. 1) | lime | `#D6F26A` |
| case data, primary (Fig. 3a) | cyan | `#2E9CB8` |
| case data, held-out / reference (Fig. 3a) | sienna | `#9C5B34` |
| case data, training / background (Fig. 3a) | stone | `#A39A8C` |
| text | ink | `#1F2330` |
| secondary text | muted | `#6B6862` |
| published methods | stone | `#B4AFA6` |
| tuned XGBoost, LightGBM, CatBoost | graphite | `#3B3A36` |
| band (middle half of published methods) | sand | `#ECE8E1` |
| grid | — | `#E8E5DF` |

## Accessibility check

Minimum pairwise CIELAB distance between the three system colours, over
normal vision and simulated protanopia, deuteranopia and tritanopia
(Machado et al. 2009, full severity): 32.9 (Okabe-Ito triple used before:
17.0). With the lime added: 29.1. Lightness of the system colours is 28, 50
and 60, so they also separate in greyscale print; markers carry the identity
as well.

## Status

All figures in the paper use this palette since 6 October 2026: Fig. 1
(`figures_systems.tex`, colours from `main.tex`, the instruction file as a
lime tag), Fig. 2 (`fig_leaderboard`), Fig. 3 (`fig_cases`: case colours in
the top row, system colours and markers in the bottom row) and Fig. 4
(`fig_ablations`, system colours and markers).
