# House style for the figures (6 October 2026)

The Okabe-Ito hues of the first version, in cooler and deeper shades, with the
original neutral greys. Every figure as it was before the change is in
`figures/archive_2026-10-06_okabe-ito/` (with the TikZ source of Fig. 1 and
the colour definitions from `main.tex`). Swatch: `STYLE_swatch.png`.
The colours are defined once, in `make_figures.py` (`C`, `KNOWLEDGE`, `CASE`,
neutrals); `make_case_figures.py` imports them, and Fig. 1 takes them from the
`\definecolor` lines in `main.tex`.

## Rules

1. Each system keeps one colour and one marker in every figure:
   AutoDS-Tools cobalt diamond, Terminus-2 red-orange circle, FEDOT.LLM
   teal-green square. Open marker = the same system without its instruction
   file.
2. Colour stands for a system only. Everything else (published methods,
   bands, reference lines) is a neutral grey.
3. The instruction file has its own colour, a pale canary like a sticky note,
   used only in Fig. 1.
4. The case-study data panels (Fig. 3a) show raw data, no system appears in
   them, and they use the classic matplotlib colours (tab:blue, tab:orange,
   tab:gray).

## Colours

| Role | Name | Hex |
|---|---|---|
| AutoDS-Tools | cobalt | `#1F5FA8` |
| Terminus-2 | red-orange | `#D2502A` |
| FEDOT.LLM | teal-green | `#0E9488` |
| instruction file (Fig. 1) | pale canary | `#F7F0C4` |
| case data, primary (Fig. 3a) | matplotlib tab:blue | `#1F77B4` |
| case data, held-out / reference (Fig. 3a) | matplotlib tab:orange | `#FF7F0E` |
| case data, training / background (Fig. 3a) | matplotlib tab:gray | `#7F7F7F` |
| text | ink | `#1A1A1A` |
| secondary text | muted | `#6E6E6E` |
| published methods | grey | `#B0B0B0` |
| tuned XGBoost, LightGBM, CatBoost | dark grey | `#3A3A3A` |
| band (middle half of published methods) | light grey | `#E6E6E6` |
| fixed stages in Fig. 1 | light grey | `#E8E8E8` |
| grid | — | `#E4E4E4` |

## Accessibility check

Minimum pairwise CIELAB distance between the three system colours, over
normal vision and simulated protanopia, deuteranopia and tritanopia
(Machado et al. 2009, full severity): 19.8 (original Okabe-Ito: 17.0). The
canary is at least 41 from every system colour. Lightness of the system
colours is 40, 51 and 55; in greyscale the markers carry the identity.

## Status

All figures in the paper use this palette: Fig. 1 (`fig_allsystems.pdf`,
drawn by hand in the same colours and included from `figures_systems.tex`), Fig. 2 (`fig_leaderboard`), Fig. 3 (`fig_cases`) and
Fig. 4 (`fig_ablations`).
