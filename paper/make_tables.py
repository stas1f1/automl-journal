#!/usr/bin/env python3
"""Generate the LaTeX tables of the paper from the recorded run data.

Run from paper/:  python3 make_tables.py
Writes tables/*.tex.  Every number here traces to result_files/ or to a
Harbor job linked in result_files/DATA_SOURCES.md.
"""
import statistics as st
from pathlib import Path

OUT = Path(__file__).parent / "tables"
OUT.mkdir(exist_ok=True)

# ----------------------------------------------------------------------
# TabReD: 8 tasks, official temporal splits, metrics in raw target units.
# ----------------------------------------------------------------------
TASKS = ["homesite-insurance", "ecom-offers", "homecredit-default",
         "sberbank-housing", "cooking-time", "delivery-eta",
         "maps-routing", "weather"]
SHORT = ["Homesite", "Ecom", "HomeCred", "Sberbank",
         "Cooking", "Delivery", "Maps", "Weather"]
HIB = [True, True, True, False, False, False, False, False]   # higher is better
METRIC = ["ROC-AUC"] * 3 + ["RMSE"] * 5

# Published TabReD baselines: full official split, Optuna-tuned,
# mean over 15 seeds (Rubachev et al., arXiv:2406.19380, Table 2).
PUBLISHED = {
    "XGBoost":        [0.9601, 0.5763, 0.8670, 0.2419, 0.4823, 0.5468, 0.1616, 1.4671],
    "LightGBM":       [0.9603, 0.5758, 0.8664, 0.2468, 0.4826, 0.5468, 0.1618, 1.4625],
    "CatBoost":       [0.9606, 0.5596, 0.8621, 0.2482, 0.4823, 0.5465, 0.1619, 1.4688],
    "RandomForest":   [0.9570, 0.5764, 0.8269, 0.2640, 0.4884, 0.5959, 0.1653, 1.5838],
    "Linear":         [0.9290, 0.5665, 0.8168, 0.2509, 0.4882, 0.5579, 0.1709, 1.7679],
    "MLP":            [0.9500, 0.6015, 0.8545, 0.2508, 0.4820, 0.5504, 0.1622, 1.5470],
    "SNN":            [0.9492, 0.5996, 0.8551, 0.2858, 0.4838, 0.5544, 0.1651, 1.5649],
    "DCNv2":          [0.9392, 0.5955, 0.8466, 0.2770, 0.4842, 0.5532, 0.1672, 1.5782],
    "ResNet":         [0.9469, 0.5998, 0.8493, 0.2743, 0.4825, 0.5527, 0.1625, 1.5021],
    "FT-Transformer": [0.9622, 0.5775, 0.8571, 0.2440, 0.4820, 0.5542, 0.1625, 1.5104],
    "MLP (PLR)":      [0.9621, 0.5957, 0.8568, 0.2438, 0.4812, 0.5527, 0.1616, 1.5177],
    "Trompt":         [0.9588, 0.5803, 0.8355, 0.2509, 0.4809, 0.5519, 0.1624, 1.5187],
    "MLP ens.":       [0.9503, 0.6019, 0.8557, 0.2447, 0.4815, 0.5494, 0.1620, 1.5186],
    "MLP-PLR ens.":   [0.9629, 0.5981, 0.8585, 0.2381, 0.4806, 0.5518, 0.1612, 1.4953],
    "MLP aug.":       [0.9523, 0.6011, 0.8449, 0.2659, 0.4832, 0.5532, 0.1631, 1.5193],
    "MLP aug. rec.":  [0.9531, 0.5960, 0.7453, 0.2515, 0.4834, 0.5541, 0.1636, 1.5160],
    "TabR":           [0.9487, 0.5943, 0.8501, 0.2820, 0.4828, 0.5514, 0.1639, 1.4666],
    "ModernNCA":      [0.9514, 0.5765, 0.8531, 0.2593, 0.4825, 0.5498, 0.1625, 1.5062],
}
GROUP = {  # for the grouped leaderboard table
    "GBDT": ["XGBoost", "LightGBM", "CatBoost", "RandomForest", "Linear"],
    "Tabular DL": ["MLP", "SNN", "DCNv2", "ResNet", "FT-Transformer",
                   "MLP (PLR)", "Trompt"],
    "Ensembles": ["MLP ens.", "MLP-PLR ens."],
    "Training methodologies": ["MLP aug.", "MLP aug. rec."],
    "Retrieval-augmented": ["TabR", "ModernNCA"],
}

# Agents on the SAME data (harbor-tabred-adapter, full official splits).
# All three: mean of three attempts (per-attempt values in *_ATTEMPTS below).
# AutoDS-Tools: re-run of 2026-08-28 on the common adapter, mean of the attempts
# completed so far; regenerate with runs/autods-tabred/collect.py --only=full.
# NOTE: the AutoDS-Tools arm carries its prescribed-knowledge layer and an image
# with the libraries that layer names.  See the design section -- this row
# compares deployed systems, not isolated architectures.
AGENTS = {
    "Terminus-2":   [0.958801, 0.558499, 0.858995, 0.249054,
                     0.483730, 0.548203, 0.162825, 1.524693],
    "AutoDS-Tools": [0.961118, 0.579992, 0.863282, 0.251457,
                     0.482025, 0.547391, 0.161983, 1.478262],
    # FEDOT.LLM, 23.09.2026: full configuration (best_quality preset, tuning on,
    # 1200 s backend budget, holdout validation, column types read from the task
    # schema), three attempts per task under the shared 8 cores, 16 GB and
    # 3600 s ceiling.  Means over FEDOT_ATTEMPTS; jobs
    # fedot-tabred-40min-schema-20260922-141217, ...-schema5-20260922-171228,
    # ...-schema-sberbank-20260922-175429, ...-schema-delivery-20260922-224814;
    # summary runs/autods-tabred/fedot-tabred-logs/schema_final.json, report
    # result_files/FEDOT_TABRED_BUDGET_2026-09-22.md (sections 13-15).
    "FEDOT.LLM":    [0.959719, 0.620040, 0.856865, 0.239792,
                     0.486700, 0.562040, 0.166449, 1.565056],
}
# Agent minutes per attempt, same order as FEDOT_ATTEMPTS.
FEDOT_MINUTES = {
    "homesite-insurance": [23.9, 24.0, 23.9], "ecom-offers": [21.6, 21.8, 22.3],
    "homecredit-default": [31.1, 32.4, 30.8], "sberbank-housing": [20.7, 20.6, 21.0],
    "cooking-time": [35.6, 29.4, 40.2], "delivery-eta": [56.3, 58.1, 55.1],
    "maps-routing": [39.9, 39.4, 39.5], "weather": [34.1, 40.4, 31.4],
}
FEDOT_ATTEMPTS = {
    "homesite-insurance": [0.9597193604640095, 0.9597193604640095, 0.9597193604640095],
    "ecom-offers":        [0.6200401065164529, 0.6200401065164529, 0.6200401065164529],
    "homecredit-default": [0.8568652403688770, 0.8568652403688770, 0.8568652403688770],
    "sberbank-housing":   [0.2340035943377987, 0.2434141455206006, 0.2419586421037739],
    "cooking-time":       [0.4864429206486711, 0.4861604488609324, 0.4874956445390430],
    "delivery-eta":       [0.5620398532447416, 0.5620398532447416, 0.5620398532447416],
    "maps-routing":       [0.1664485447050930, 0.1664485447050930, 0.1664485447050930],
    "weather":            [1.5547329002094838, 1.5806360195484421, 1.5597989034287620],
}
# Per-attempt values, for the noise-floor table.  Fill AUTODS_ATTEMPTS from
# runs/autods-tabred/collect.py once the re-run completes; the table renders
# whatever is present and says so.
TERMINUS_ATTEMPTS = {
    "homesite-insurance": [0.9580949519213343, 0.9596429592113960, 0.9586672847710026],
    "ecom-offers":        [0.5609172532916561, 0.5609172532916561, 0.5536615895420993],
    "homecredit-default": [0.8588376004392972, 0.8588376004392972, 0.8593094135570923],
    "sberbank-housing":   [0.2517543402236549, 0.2477037524916460, 0.2477037524916460],
    "cooking-time":       [0.4838123558778030, 0.4835633821767485, 0.4838123558778030],
    "delivery-eta":       [0.5489498185424255, 0.5478294720234239, 0.5478294720234239],
    "maps-routing":       [0.1627495430083853, 0.1627977921372332, 0.1629278069003578],
    "weather":            [1.5276027945128190, 1.5232373154002330, 1.5232373154002330],
}

# Four of the 24 trials reached the task's 3600 s ceiling.  Three of them had
# already written a usable predictions.csv and are scored normally; the fourth
# had not, and is excluded -- averaging a timeout as a zero would report an
# infrastructure limit as model quality -- which is why homesite-insurance
# carries n=2.  An earlier copy of this run was discarded: it used an image that
# omitted libgomp1, so the very libraries the layer prescribes failed to fit
# (Section~\ref{sec:threats}).
AUTODS_ATTEMPTS = {
    "homesite-insurance": [0.9611184795445190, 0.9611184795445190],
    "ecom-offers":        [0.5799913674546233, 0.5799913674546233, 0.5799939369228467],
    "homecredit-default": [0.8627448770989221, 0.8635503910374048, 0.8635503910374048],
    "sberbank-housing":   [0.2514574079401016, 0.2514574079401016, 0.2514574079401016],
    "cooking-time":       [0.4819595408353929, 0.4820574527876803, 0.4820574527876803],
    "delivery-eta":       [0.5473909409965390, 0.5473909409965390, 0.5473909409965390],
    "maps-routing":       [0.1619181376325539, 0.1621122880989272, 0.1619181376325539],
    "weather":            [1.4782623416728129, 1.4782625768999724, 1.4782623131941837],
}

ATTEMPTS = {"Terminus-2": TERMINUS_ATTEMPTS, "AutoDS-Tools": AUTODS_ATTEMPTS,
            "FEDOT.LLM": FEDOT_ATTEMPTS}

# ----------------------------------------------------------------------
# MLAgentBench: K-tool ablation on AutoDS-Tools (identical architecture,
# the two branches differ only in the instruction file).
# ----------------------------------------------------------------------
MLAB = [
    # Опыт A: десять задач, три попытки на ячейку, обе ветки, сентябрь 2026.
    # Поля: задача, метрика, больше-лучше, затем по ветке "со слоем" и "без
    # слоя" — (сколько попыток дало оценку, среднее по ним, минимум, максимум),
    # и наконец опубликованное одиночное значение (со слоем, без слоя).
    # n=0 означает: все три попытки исчерпали бюджет, не оставив посылки.
    # None вместо среднего идёт вместе с n=0.
    ("identify-contrails", "Dice",      True,
     (3, 0.047831,  0.014870, 0.113715), (3, 0.002150,  0.0,      0.003972),
     0.3257,     0.0006),
    ("ogbn-arxiv",         "Accuracy",  True,
     (3, 0.506900, 0.433400, 0.557300), (3, 0.386633, 0.223700, 0.479000),
     0.5560,     0.3217),
    ("feedback",           "MCRMSE",    False,
     (0, None,     None,     None),     (3, 0.826142, 0.540315, 1.256879),
     0.5244,     1.6634),
    ("amp-parkinsons",     "SMAPE",     False,
     (3, 86.463734, 81.776829, 90.080350), (2, 62.278726, 58.211313, 66.346138),
     88.0821,    96.5844),
    ("spaceship-titanic",  "Accuracy",  True,
     (3, 0.810842, 0.807958, 0.813149), (3, 0.807382, 0.802191, 0.813149),
     0.8085,     0.8103),
    ("house-price",        "MAE",       False,
     (3, 16433.430376, 16161.953411, 16904.159562),
     (3, 15894.753083, 15529.723997, 16600.828679),
     15956.8001, 15671.4909),
    ("imdb",               "Accuracy",  True,
     None, None,
     0.8397,     0.8643),
    ("cifar10",            "Accuracy",  True,
     None, None,
     0.8228,     0.8849),
    ("clrs",               "Ptr. acc.", True,
     (0, None,     None,     None),     (3, 0.390882, 0.320408, 0.440409),
     0.0525,     0.4298),
    ("fathomnet",          "micro-F1",  True,
     (0, None,     None,     None),     (2, 0.143538, 0.142828, 0.144248),
     0.0300,     0.1676),
]

# ----------------------------------------------------------------------
def fmt(v, task_idx=None, decimals=4):
    if v is None:
        return "--"
    if abs(v) >= 1000:
        return f"{v:,.1f}".replace(",", "\\,")
    return f"{v:.{decimals}f}"


def spct(v, nd=2):
    """Signed number without a negative zero: -0.001 prints as 0.00, not -0.00."""
    if v is None:
        return "--"
    s = f"{v:+.{nd}f}"
    return s[1:] if s[1:] == f"{0:.{nd}f}" else s


def normalized(value, j):
    """0 = worst published baseline on task j, 1 = best published baseline.

    Returns None for a missing value, so a partially filled agent row (a run
    still in flight, or a task that failed) degrades to blank cells instead of
    crashing the build.
    """
    if value is None:
        return None
    col = [PUBLISHED[b][j] for b in PUBLISHED]
    best = max(col) if HIB[j] else min(col)
    worst = min(col) if HIB[j] else max(col)
    return (value - worst) / (best - worst)


def ranks():
    """Average rank per method.  A method with no value on task j is left out of
    that column entirely, so its rank is averaged over the tasks it ran."""
    pool = {**PUBLISHED, **AGENTS}
    r = {k: [] for k in pool}
    for j in range(len(TASKS)):
        present = [m for m in pool if pool[m][j] is not None]
        order = sorted(present, key=lambda m: -pool[m][j] if HIB[j] else pool[m][j])
        for pos, m in enumerate(order, 1):
            r[m].append(pos)
    return r, pool


# ----------------------------------------------------------------------
def table_leaderboard():
    r, pool = ranks()
    L = []
    A = L.append
    A(r"\begin{table*}[t]")
    A(r"\centering")
    A(r"\caption{Agent architectures placed in the TabReD leaderboard: full "
      r"official temporal splits, the benchmark's metrics in raw units. Published "
      r"rows are Optuna-tuned means over 15 seeds \citep{rubachev2024tabred}; agent "
      r"rows use \texttt{gemma-4-31b-it}; agent rows are means over three attempts. "
      r"Best per column in bold.}")
    A(r"\label{tab:leaderboard}")
    A(r"\small")
    A(r"\setlength{\tabcolsep}{3pt}")
    A(r"\begin{tabular}{l" + "r" * len(TASKS) + "r}")
    A(r"\toprule")
    A(r"& \multicolumn{3}{c}{ROC-AUC $\uparrow$} & \multicolumn{5}{c}{RMSE $\downarrow$} & \\")
    A(r"\cmidrule(lr){2-4}\cmidrule(lr){5-9}")
    A("Method & " + " & ".join(SHORT) + r" & Avg.\ rank \\")
    A(r"\midrule")

    bests = []
    for j in range(len(TASKS)):
        col = [pool[m][j] for m in pool if pool[m][j] is not None]
        bests.append((max(col) if HIB[j] else min(col)) if col else None)

    def row(name, label=None):
        cells = []
        for j in range(len(TASKS)):
            v = pool[name][j]
            s = fmt(v, decimals=4)
            if v is not None and bests[j] is not None and abs(v - bests[j]) < 1e-12:
                s = r"\textbf{" + s + "}"
            cells.append(s)
        got = r[name]
        rk = f"{st.mean(got):.1f}" if got else "--"
        n = sum(1 for j in range(len(TASKS)) if pool[name][j] is not None)
        if n and n < len(TASKS):
            rk += f"$^{{{n}}}$"          # ranks averaged over the tasks that ran
        return f"{label or name} & " + " & ".join(cells) + f" & {rk} " + r"\\"

    for gname, members in GROUP.items():
        A(r"\addlinespace[2pt]")
        A(r"\multicolumn{%d}{l}{\itshape %s} \\" % (len(TASKS) + 2, gname))
        for m in members:
            A(row(m))

    A(r"\midrule")
    A(r"\multicolumn{%d}{l}{\itshape Agentic AutoML systems (this work)} \\" % (len(TASKS) + 2))
    AGENT_LABEL = {
        "Terminus-2":   r"Terminus-2 \emph{(open harness)}",
        "AutoDS-Tools": r"AutoDS-Tools \emph{(multi-agent)}",
        "FEDOT.LLM":    r"FEDOT.LLM \emph{(rigid pipeline)}",
    }
    for name in AGENTS:
        A(row(name, AGENT_LABEL.get(name)))
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\end{table*}")
    return "\n".join(L)


def table_normalized():
    L = []
    A = L.append
    A(r"\begin{table*}[t]")
    A(r"\centering")
    A(r"\caption{Normalised position on each TabReD task: $0$ is the weakest and $1$ "
      r"the strongest of the 18 published baselines. The three agent rows share one "
      r"backbone model, so the spread among them is attributable to architecture alone.}")
    A(r"\label{tab:normalized}")
    A(r"\small")
    A(r"\setlength{\tabcolsep}{4pt}")
    A(r"\begin{tabular}{l" + "r" * len(TASKS) + "r}")
    A(r"\toprule")
    A("Method & " + " & ".join(SHORT) + r" & Mean \\")
    A(r"\midrule")
    for name in AGENTS:
        vals = [normalized(AGENTS[name][j], j) for j in range(len(TASKS))]
        got = [v for v in vals if v is not None]
        cells = " & ".join("--" if v is None else f"{v:.2f}" for v in vals)
        mean = r"\textbf{" + (f"{st.mean(got):.2f}" if got else "--") + r"}"
        A(f"{name} & {cells} & {mean} \\\\")
    A(r"\midrule")
    for name in ["XGBoost", "MLP-PLR ens.", "Linear"]:
        vals = [normalized(PUBLISHED[name][j], j) for j in range(len(TASKS))]
        A(f"{name} & " + " & ".join(f"{v:.2f}" for v in vals) +
          f" & {st.mean(vals):.2f} " + r"\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\end{table*}")
    return "\n".join(L)


def table_noise():
    """Run-to-run spread per system.  Renders a block per system that has data."""
    live = {k: v for k, v in ATTEMPTS.items() if v}
    ident_tot = sum(1 for v in live.values() for a in v.values() if len(set(a)) < len(a))
    L = []
    A = L.append
    A(r"\begin{table}[t]")
    A(r"\centering")
    A(r"\caption{Run-to-run spread over independent attempts on the same task. "
      r"A dagger marks a task on which two attempts agree to machine precision, i.e.\ "
      r"the agent reproduced a bit-identical submission; this happens for %d of the "
      r"%d task--system cells here, so repeats carry less independent information than "
      r"their count suggests.%s}"
      % (ident_tot, sum(len(v) for v in live.values()),
         " The systems do not share a noise floor, which is why the threshold used for"
         " cross-system comparison is taken from the noisier of them." if len(live) > 1
         else ""))
    A(r"\label{tab:noise}")
    A(r"\small")
    A(r"\begin{tabular}{llrrrr}")
    A(r"\toprule")
    A(r"Task & Metric & $n$ & Mean & SD & Rel.\ SD \\")
    for sysname, att in live.items():
        A(r"\midrule")
        A(r"\multicolumn{6}{l}{\itshape %s} \\" % sysname)
        for j, t in enumerate(TASKS):
            v = att.get(t)
            if not v:
                continue
            m = st.mean(v)
            sd = st.stdev(v) if len(v) > 1 else 0.0
            ident = r"$^{\dagger}$" if len(set(v)) < len(v) else ""
            A(f"\\texttt{{{t}}}{ident} & {METRIC[j]} & {len(v)} & {m:.4f} & {sd:.5f} & "
              f"{100 * sd / abs(m):.2f}\\% \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\begin{tablenotes}\footnotesize")
    A(r"\item[$\dagger$] Two attempts bit-identical.")
    A(r"\end{tablenotes}")
    A(r"\end{table}")
    return "\n".join(L)


# Очная встреча двух архитектур на MLAgentBench: одно задание, один
# проверяющий, одна параллельность, по три попытки. До этого прогона такого
# сравнения на этом бенчмарке не было — числа приходили из разных заданий
# разных времён. cifar10 и imdb исключены: на машине без ускорителя они не
# воспроизводятся (см. sec:scope).
# Поля ячейки: (сколько попыток из трёх дало посылку, среднее, минимум, максимум)
# ---------------------------------------------------------------------------
# Научные кейсы (10.09.2026): система × текст задания, три попытки на ячейку.
# Метрика та, которой пользуются авторы исходной работы; None = трайл не оставил
# файла ответа (агент закончил, пока обучение ещё шло в терминале). Источник:
# result_files/cases_terminus_2026-09-10.json (collect_cases.py), июльские
# трайлы AutoDS с Harbor Hub (одна попытка, текст с предписанием).
# ---------------------------------------------------------------------------
CASE_META = {
    # кейс: (подпись, метрика, авторский бейзлайн, подпись бейзлайна)
    "maize-yield": ("Maize yield (G2F)", "Pearson $r$ $\\uparrow$", 0.461, "best author model, BLUP"),
    "fdata-exit":  ("Fugaku exit state (F-DATA)", "Accuracy $\\uparrow$", 0.89, "authors, XGBoost/RF"),
    "openpoly-tg": ("Polymer $T_g$ (OpenPoly)", "$R^2$ $\\uparrow$", 0.904, "authors, full data"),
}
CASE_ARMS = [
    # (система, текст) в порядке строк таблицы. FEDOT.LLM идёт одной строкой:
    # предписание инструмента у него зашито, раздел о библиотеке он выполнить
    # не может, поэтому второй текст для него не условие (прогон с ним сделан
    # 10.09 как проверка: вывод колонок и числа на fdata совпали).
    ("AutoDS-Tools", "prescribed"),
    ("Terminus-2", "plain"), ("Terminus-2", "prescribed"),
    ("FEDOT.LLM", "plain"),
]
CASES = {
    # (кейс, система, текст): ([метрика по попыткам], [минуты агента по попыткам])
    ("maize-yield", "AutoDS-Tools", "prescribed"): ([0.568563], [16.7]),
    # минуты AutoDS-Tools: agent_execution в result.json июльских трайлов
    # (433a969c F-DATA 17.5, edf0f88f OpenPoly 7.0; result_files/LAMA_FDATA_2026-09-22.md)
    ("fdata-exit",  "AutoDS-Tools", "prescribed"): ([0.920713], [17.5]),
    ("openpoly-tg", "AutoDS-Tools", "prescribed"): ([0.543], [7.0]),
    ("maize-yield", "Terminus-2", "plain"):      ([0.63576, None, 0.674405], [0.8, 3.2, 2.1]),
    ("fdata-exit",  "Terminus-2", "plain"):      ([0.922038, 0.922038, 0.922551], [0.4, 1.1, 1.7]),
    ("openpoly-tg", "Terminus-2", "plain"):      ([0.566729, 0.475295, None], [4.8, 1.1, 3.2]),
    ("maize-yield", "Terminus-2", "prescribed"): ([None, None, None], [3.4, 5.5, 4.0]),
    ("fdata-exit",  "Terminus-2", "prescribed"): ([None, None, None], [2.5, 1.5, 4.7]),
    ("openpoly-tg", "Terminus-2", "prescribed"): ([None, None, None], [1.7, 3.0, 2.6]),
    # FEDOT.LLM, текст без раздела о библиотеке, бэкенд FEDOT, time_limit 2400 с
    # (result_files/cases_fedot_2026-09-10.json); на OpenPoly не применим.
    ("maize-yield", "FEDOT.LLM", "plain"):      ([0.602824, 0.579247, 0.578079], [52.8, 52.1, 57.0]),
    ("fdata-exit",  "FEDOT.LLM", "plain"):      ([0.951787, 0.951787, 0.951787], [45.7, 42.7, 45.4]),
}
# Вторичные метрики тех же трайлов для прозы (только попытки с файлом).
CASE_EXTRA = {
    ("maize-yield", "AutoDS-Tools", "prescribed"): {"norm_rmse": [0.957710], "r2": [0.082792]},
    ("maize-yield", "Terminus-2", "plain"):        {"norm_rmse": [0.8128, 0.7705], "r2": [0.3394, 0.4063]},
    ("fdata-exit",  "AutoDS-Tools", "prescribed"): {"balanced_accuracy": [0.705421]},
    ("fdata-exit",  "Terminus-2", "plain"):        {"balanced_accuracy": [0.7164, 0.7161, 0.7142]},
    ("openpoly-tg", "AutoDS-Tools", "prescribed"): {"mae": [40.379846]},
    ("openpoly-tg", "Terminus-2", "plain"):        {"mae": [37.6775, 42.4584]},
    ("maize-yield", "FEDOT.LLM", "plain"):         {"norm_rmse": [0.8483, 0.8650, 0.8660], "r2": [0.2804, 0.2518, 0.2500]},
    ("fdata-exit",  "FEDOT.LLM", "plain"):         {"balanced_accuracy": [0.8530, 0.8530, 0.8530]},
}
CASE_FLOORS = {"fdata-exit": 0.880792}   # мажоритарный класс
# Сколько секунд занимает предписанный вызов TabularAutoML с настройками по
# умолчанию в образе кейса на nss-calc2 (runs/autods-tabred: lama_time.py,
# 10.09.2026); это то обучение, которого Terminus-2 не дождался.
CASE_LAMA_FIT_S = {"fdata-exit": 582, "maize-yield": 656}
CASE_AUTHOR_SECONDARY = {"maize-yield": ("norm. RMSE", 0.948), "openpoly-tg": ("MAE, K", 14.56)}

MLAB_HEAD = [
    # задача, метрика, больше-лучше, AutoDS без слоя, Terminus-2, Terminus опубл.
    ("clrs",   "Ptr. acc.", True,
     (3, 0.390882, 0.320408, 0.440409), (2, 0.139717, 0.133002, 0.146432), None),
    ("ogbn-arxiv", "Accuracy", True,
     (3, 0.386633, 0.223700, 0.479000), (3, 0.160633, 0.059700, 0.265500), 0.5148),
    ("spaceship-titanic", "Accuracy", True,
     (3, 0.807382, 0.802191, 0.813149), (3, 0.658977, 0.585928, 0.705882), 0.8016),
    ("house-price", "MAE", False,
     (3, 15894.753083, 15529.723997, 16600.828679),
     (2, 21594.775191, 19422.132430, 23767.417952), 16694.56),
    # Ничья проставлена вручную. Относительное правило объявило бы победу
    # AutoDS: 0.0022 против нуля — это разница в бесконечность. Но обе цифры
    # означают одно и то же, отсутствие сегментации, и назвать одну из них
    # выигрышем значило бы измерять шум.
    ("identify-contrails", "Dice", True,
     (3, 0.002150, 0.0, 0.003972), (2, 0.0, 0.0, 0.0), None, "ничья"),
    ("amp-parkinsons", "SMAPE", False,
     (2, 62.278726, 58.211313, 66.346138), (1, 60.499872, None, None), 66.35),
    ("feedback", "MCRMSE", False,
     (3, 0.826142, 0.540315, 1.256879), (2, 0.527900, 0.497165, 0.558634), None),
    ("fathomnet", "micro-F1", True,
     (2, 0.143538, 0.142828, 0.144248), (3, 0.243969, 0.084381, 0.384615), None),
]


def table_mlabhead():
    """Две архитектуры на одном задании, по три попытки; n и диапазон отдельными
    столбцами."""
    L = []
    A = L.append

    def cells(c, win):
        n, mean, lo, hi = c
        body = fmt(mean)
        if win:
            body = r"\textbf{" + body + "}"
        if lo is not None and n > 1:
            return f"{body} & {n} & {fmt(lo)} & {fmt(hi)}"
        return f"{body} & {n} & -- & --"

    A(r"\begin{table*}[t]")
    A(r"\centering")
    A(r"\caption{AutoDS-Tools without its layer and Terminus-2 on MLAgentBench "
      r"under one job, one verifier and three attempts per task. $n$ counts the "
      r"attempts that submitted; mean, min and max are over those. Bold marks the "
      r"better system where the margin exceeds $5\%$.}")
    A(r"\label{tab:mlabhead}")
    A(r"\small")
    A(r"\setlength{\tabcolsep}{5pt}")
    A(r"\begin{tabular}{llrcrrrcrr}")
    A(r"\toprule")
    A(r" & & \multicolumn{4}{c}{AutoDS-Tools} & \multicolumn{4}{c}{Terminus-2} \\")
    A(r"\cmidrule(lr){3-6}\cmidrule(lr){7-10}")
    A(r"Task & Metric & mean & $n$ & min & max & mean & $n$ & min & max \\")
    A(r"\midrule")
    wins = [0, 0]
    for row in MLAB_HEAD:
        task, metric, hib, a, tm, pub = row[:6]
        forced_tie = len(row) > 6
        better_a = (a[1] > tm[1]) if hib else (a[1] < tm[1])
        gap = abs(a[1] - tm[1]) / (max(abs(a[1]), abs(tm[1])) or 1.0)
        tie = gap < 0.05 or forced_tie
        if not tie:
            wins[0 if better_a else 1] += 1
        arrow = r"$\uparrow$" if hib else r"$\downarrow$"
        A(f"\\texttt{{{task}}} & {metric} {arrow} & {cells(a, better_a and not tie)} & "
          f"{cells(tm, (not better_a) and not tie)} \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\begin{tablenotes}\footnotesize")
    A(r"\item \texttt{identify-contrails} is counted as a tie: both cells sit at the "
      r"floor of the metric. "
      f"AutoDS-Tools takes {wins[0]} of the eight tasks and Terminus-2 {wins[1]}. "
      r"Median trial: $6.1$ minutes for Terminus-2 against $10.9$; means $19.1$ "
      r"against $63.2$. Terminus-2 reached its agent budget once in $24$ trials, "
      r"AutoDS-Tools $13$ times in $30$.")
    A(r"\end{tablenotes}")
    A(r"\end{table*}")
    return "\n".join(L)



def table_mlab():
    """Таблицы mlabhead и ktool слиты в одну: AutoDS-Tools без слоя и со слоем и
    Terminus-2 без слоя, по строке на задачу. n < 3 даётся надстрочным индексом у
    среднего; «none» значит, что ни одна попытка не сдала посылку."""
    L = []
    A = L.append

    def cell(c, bold=False):
        if c is None:
            return r"\multicolumn{3}{c}{--}"
        n, mean, lo, hi = c
        if n == 0:
            return r"\multicolumn{3}{c}{none}"
        body = fmt(mean)
        if bold:
            body = r"\textbf{" + body + "}"
        if n < 3:
            body += f"$^{{{n}}}$"
        if n > 1 and lo is not None:
            return f"{body} & {fmt(lo)} & {fmt(hi)}"
        return f"{body} & -- & --"

    def delta(on, off, hib):
        if on is None or off is None or on[0] == 0 or off[0] == 0:
            return None
        scale = max(abs(on[1]), abs(off[1])) or 1.0
        return ((on[1] - off[1]) if hib else (off[1] - on[1])) / scale

    by_task = {row[0]: row for row in MLAB}
    A(r"\begin{table*}[t]")
    A(r"\centering")
    A(r"\caption{AutoDS-Tools with and without its prescribed-knowledge layer, "
      r"and Terminus-2, on the eight MLAgentBench tasks that repeat on our hardware: "
      r"one job, one verifier, three attempts per task. Mean, min and max are over "
      r"the attempts that submitted; a superscript gives the number of submitting "
      r"attempts where it is below three, and \emph{none} means no attempt "
      r"submitted. Bold marks the better of AutoDS-Tools without the layer and "
      r"Terminus-2 where the margin exceeds $5\%$. $\Delta$ is the change in mean "
      r"score with the layer, divided by the larger of the two means, positive "
      r"where the layer helps.}")
    A(r"\label{tab:mlab}")
    A(r"\footnotesize")
    A(r"\setlength{\tabcolsep}{3pt}")
    A(r"\begin{tabular}{llrrrrrrrrrr}")
    A(r"\toprule")
    A(r" & & \multicolumn{3}{c}{AutoDS-Tools, layer off} & "
      r"\multicolumn{3}{c}{AutoDS-Tools, layer on} & "
      r"\multicolumn{3}{c}{Terminus-2} & \\")
    A(r"\cmidrule(lr){3-5}\cmidrule(lr){6-8}\cmidrule(lr){9-11}")
    A(r"Task & Metric & mean & min & max & mean & min & max & mean & min & max & $\Delta$ \\")
    A(r"\midrule")
    wins = [0, 0]
    for row in MLAB_HEAD:
        task, metric, hib, a, tm, _pub = row[:6]
        forced_tie = len(row) > 6
        better_a = (a[1] > tm[1]) if hib else (a[1] < tm[1])
        gap = abs(a[1] - tm[1]) / (max(abs(a[1]), abs(tm[1])) or 1.0)
        tie = gap < 0.05 or forced_tie
        if not tie:
            wins[0 if better_a else 1] += 1
        on = by_task[task][3]
        off = by_task[task][4]
        d = delta(on, off, hib)
        dtxt = r"\multicolumn{1}{c}{--}" if d is None else spct(d)
        arrow = r"$\uparrow$" if hib else r"$\downarrow$"
        A(f"\\texttt{{{task}}} & {metric} {arrow} & "
          f"{cell(off, bold=better_a and not tie)} & {cell(on)} & "
          f"{cell(tm, bold=(not better_a) and not tie)} & {dtxt} \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\begin{tablenotes}\footnotesize")
    A(r"\item \texttt{identify-contrails} is counted as a tie between AutoDS-Tools "
      r"and Terminus-2: both cells sit at the floor of the metric, and its $\Delta$ "
      r"divides one small number by another and is not read as a result. "
      f"Without the layer AutoDS-Tools takes {wins[0]} of the eight tasks against "
      f"Terminus-2 and Terminus-2 {wins[1]}. "
      r"Median trial: $6.1$ minutes for Terminus-2 against $10.9$ for AutoDS-Tools "
      r"without the layer; means $19.1$ against $63.2$. Terminus-2 reached its "
      r"agent budget once in $24$ trials, AutoDS-Tools $13$ times in $30$.")
    A(r"\end{tablenotes}")
    A(r"\end{table*}")
    return "\n".join(L)


def case_cell(key):
    """(n с файлом, среднее, min, max, медиана минут) для одной ячейки кейсов."""
    if key not in CASES:
        return None
    vals, mins = CASES[key]
    got = [v for v in vals if v is not None]
    med = st.median([m for m in mins if m is not None]) if any(m is not None for m in mins) else None
    if not got:
        return (0, None, None, None, med, len(vals))
    return (len(got), st.mean(got), min(got), max(got), med, len(vals))


def table_cases():
    """Три научных кейса: строка на систему и текст задания, три попытки."""
    L = []
    A = L.append
    A(r"\begin{table*}[t]")
    A(r"\centering")
    A(r"\caption{Three scientific case studies, one row per system and task text. "
      r"\emph{Prescribed} is the published task text with its library section; "
      r"\emph{plain} is the same text without it. $n$ counts attempts that left a "
      r"submission; mean, min and max are over those. Minutes are the median agent "
      r"time per attempt. Author baselines are on the authors' own metric. Bold: "
      r"the best system mean per case.}")
    A(r"\label{tab:cases}")
    A(r"\small")
    A(r"\setlength{\tabcolsep}{5pt}")
    A(r"\begin{tabular}{llllcrrrr}")
    A(r"\toprule")
    A(r"Case & Metric & System & Text & $n$ & mean & min & max & min/attempt \\")
    A(r"\midrule")
    for i, (task, (label, metric, author, author_note)) in enumerate(CASE_META.items()):
        if i:
            A(r"\midrule")
        A(f"{label} & {metric} & \\emph{{authors}} & & & {author:.3f} & & & \\\\")
        cells = [(system, arm, case_cell((task, system, arm))) for system, arm in CASE_ARMS]
        # all three case metrics are higher-is-better; bold the best system mean
        best_mean = max((c[1] for _s, _a, c in cells if c is not None and c[0] > 0), default=None)
        for system, arm, c in cells:
            if c is None:
                continue   # ячейка не применима (FEDOT.LLM на OpenPoly)
            n, mean, lo, hi, med, total = c
            mins = f"{med:.1f}" if med is not None else "--"
            if system == "FEDOT.LLM":
                arm = "plain (tool welded in)"
            m = f"{mean:.3f}" if n else "--"
            if n and mean == best_mean:
                m = r"\textbf{" + m + "}"
            if n == 0:
                A(f" & & {system} & {arm} & 0/{total} & -- & -- & -- & {mins} \\\\")
            elif n == 1:
                A(f" & & {system} & {arm} & 1/{total} & {m} & -- & -- & {mins} \\\\")
            else:
                A(f" & & {system} & {arm} & {n}/{total} & {m} & {lo:.3f} & {hi:.3f} & {mins} \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\begin{tablenotes}\footnotesize")
    A(r"\item AutoDS-Tools rows are the single July runs on the published text. "
      r"FEDOT.LLM cannot act on the library section and has no molecular featurisation, "
      r"so it has one row and was not run on OpenPoly. "
      r"F-DATA: majority class scores " + f"{CASE_FLOORS['fdata-exit']:.3f}" + r". "
      r"OpenPoly: the author figure is on the full dataset, ours on a subset with an "
      r"89-row test split, so that row is indicative only.")
    A(r"\end{tablenotes}")
    A(r"\end{table*}")
    return "\n".join(L)

def table_ktool():
    """Слой на MLAgentBench, три попытки на ячейку.  Диапазон попыток вынесен
    в отдельный столбец, а не в мелкий шрифт внутри ячейки."""
    L = []
    A = L.append

    def mean_cell(c):
        if c is None:
            return r"\multicolumn{1}{c}{--}"
        if c[0] == 0:
            return r"\multicolumn{1}{c}{none}"
        return fmt(c[1])

    def range_cell(c):
        if c is None or c[0] == 0:
            return r"\multicolumn{1}{c}{--} & \multicolumn{1}{c}{--}"
        return f"{fmt(c[2])} & {fmt(c[3])}"

    def delta(on, off, hib):
        if on is None or off is None or on[0] == 0 or off[0] == 0:
            return None
        scale = max(abs(on[1]), abs(off[1])) or 1.0
        return ((on[1] - off[1]) if hib else (off[1] - on[1])) / scale

    A(r"\begin{table*}[!t]")
    A(r"\centering")
    A(r"\caption{The prescribed-knowledge layer on AutoDS-Tools over MLAgentBench, "
      r"three attempts per cell; the two branches differ only in the instruction "
      r"file. Min and max are over the attempts that submitted; \emph{none} means no "
      r"attempt submitted. $\Delta$ is the normalised effect, positive where the layer helps.}")
    A(r"\label{tab:ktool}")
    A(r"\small")
    A(r"\setlength{\tabcolsep}{5pt}")
    A(r"\begin{tabular}{llrrrrrrr}")
    A(r"\toprule")
    A(r" & & \multicolumn{3}{c}{layer off} & \multicolumn{3}{c}{layer on} & \\")
    A(r"\cmidrule(lr){3-5}\cmidrule(lr){6-8}")
    A(r"Task & Metric & mean & min & max & mean & min & max & $\Delta$ \\")
    A(r"\midrule")
    for task, metric, hib, on, off, *_ in MLAB:
        if on is None and off is None:
            continue          # cifar10, imdb: not repeated, omitted
        d = delta(on, off, hib)
        dtxt = r"\multicolumn{1}{c}{--}" if d is None else spct(d)
        arrow = r"$\uparrow$" if hib else r"$\downarrow$"
        A(f"\\texttt{{{task}}} & {metric} {arrow} & {mean_cell(off)} & {range_cell(off)} & "
          f"{mean_cell(on)} & {range_cell(on)} & {dtxt} \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\end{table*}")
    return "\n".join(L)


# ----------------------------------------------------------------------
# Harbor Hub telemetry, read from `harbor hub job show <id> --json`.
# n_concurrent is the job's own setting; wall-clock is finished_at minus
# started_at and therefore includes queueing and environment builds.
# ----------------------------------------------------------------------
TELEMETRY = [
    # label, benchmark, job id, trials, concurrency, cost usd, in tok, out tok, wall-clock sec
    # Per-trial times read from the hub trial records (started_at/finished_at,
    # `harbor hub job trials 7593cc7b --json`, 22 September 2026); the last field
    # is their SUM in seconds and concurrency is set to 1, as for the rows below,
    # so wall*conc/n is the mean trial time.  End-to-end job time was 3692.4 s at
    # concurrency 2, which gave 5.13 min per trial against 5.07 here.
    ("Terminus-2", "TabReD", "7593cc7b", 24, 1, 0.16557048, 1199257, 50673, 7306.1),
    ("Terminus-2", "MLAgentBench", "1a42d1fe", 6, 1, 0.089077296, 840565, 27431, 4202.6),
    ("AutoDS-Tools ($K$ on)", "both", "3113aba7", 18, 1, 0.313829, 2525266, 180306, 140526.0),
    ("AutoDS-Tools ($K$ off)", "both", "56768b37", 18, 1, 0.219441, 1709777, 142540, 108252.5),
    # This work: the re-run on the common adapter, 8 tasks x 3 attempts.
    ("AutoDS-Tools (this work)", "TabReD", "server", 24, 4, 0.176723, 1478567, 128387, 15972.4),
    # FEDOT.LLM, 8 tasks x 3 attempts, 22-23.09.2026 (schema_final.json): token
    # counts from the trial logs; the cost is those tokens at the list price of
    # gemma-4-31b-it ($0.09 / $0.34 per million), since fedotllm calls the model
    # from inside the container and Harbor records no cost for it.  Last field:
    # the SUM of agent times over the 24 trials, concurrency 1.
    ("FEDOT.LLM", "TabReD", "schema", 24, 1, 0.007058, 64322, 3731, 47610.0),
    # Повторы на MLAgentBench, сентябрь 2026. У этих строк последнее поле — СУММА
    # времён отдельных испытаний, а не сквозное время задания, поэтому
    # предпоследнее поле равно 1: та же формула wall*conc/n тогда даёт среднее
    # время испытания, а не делит сквозное время на параллельность.
    ("AutoDS-Tools ($K$ off, this work)",      "MLAgentBench", "server", 30, 1,
     0.266275,  2293918, 175947, 113747.1),
    ("AutoDS-Tools (shipped $K$, this work)",  "MLAgentBench", "server", 30, 1,
     0.309540,  2713178, 192220, 126937.8),
    ("AutoDS-Tools (composed $K$, this work)", "MLAgentBench", "server", 24, 1,
     0.609890,  5698124, 285475,  69560.8),
    ("Terminus-2 (this work)",                 "MLAgentBench", "server", 24, 1,
     10.359975, 47746639, 284960, 27445.6),
]

# Per-trial agent wall-clock in the re-run, in minutes, from result.json's
# started_at to the mtime of verifier/reward.json (walltime.py).  The task
# ceiling is 3600 s; four trials reached it, and one of those four had written
# nothing scoreable by then.
RERUN_MINUTES = [66.2, 63.1, 62.4, 61.2, 58.6, 57.1, 49.1, 46.0, 41.4, 40.2,
                 39.7, 39.6, 38.2, 36.7, 35.4, 35.0, 34.2, 32.2, 32.0, 28.3,
                 27.9, 19.9, 19.3, 18.7]

# Per-trial minutes of the Terminus-2 leaderboard job on TabReD (7593cc7b), from
# the hub trial records started_at/finished_at, sorted like RERUN_MINUTES.
TERMINUS_TABRED_MINUTES = [7.96, 7.08, 7.00, 6.73, 6.72, 6.52, 6.34, 6.33, 5.75,
                           5.60, 5.33, 4.98, 4.96, 4.88, 4.78, 4.61, 4.03, 3.88,
                           3.87, 3.14, 2.98, 2.89, 2.78, 2.64]
RERUN_TIMEOUTS = 1          # trials that reached the ceiling with no submission
RERUN_CEILING_SCORED = 3    # trials cut at the ceiling that had already written one
RERUN_CEILING_MIN = 60.0    # task.toml timeout_sec = 3600


# ----------------------------------------------------------------------
# TabReD, the layer split into its two halves: a full 2x2 over K_tool (the
# library block) and K_disc (the discipline block), 24 trials per cell, all
# four cells on one image at one concurrency setting on one machine, so the
# cells differ in the instruction file and in nothing else.  Values are means
# over three attempts, read from <trial>/verifier/reward.json.
# ----------------------------------------------------------------------
GRID = {
    # task: (metric, higher_is_better, neither, K_tool only, K_disc only, both)
    "homesite-insurance": ("ROC-AUC", True, 0.959991, 0.960913, 0.959679, 0.961118),
    "ecom-offers": ("ROC-AUC", True, 0.564894, 0.585667, 0.571918, 0.579992),
    "homecredit-default": ("ROC-AUC", True, 0.855948, 0.862719, 0.857621, 0.863282),
    "sberbank-housing": ("RMSE", False, 0.251640, 0.252408, 0.251640, 0.251457),
    "cooking-time": ("RMSE", False, 0.483463, 0.481200, 0.483669, 0.482025),
    "delivery-eta": ("RMSE", False, 0.547611, 0.547637, 0.547903, 0.547391),
    "maps-routing": ("RMSE", False, 0.162710, 0.161668, 0.162566, 0.161983),
    "weather": ("RMSE", False, 1.496830, 1.494790, 1.502959, 1.478262),
}
GRID_COST = {"nolayer": 0.206178, "libonly": 0.176889, "disconly": 0.228821, "full": 0.176723}
GRID_MEDIAN_MIN = {"nolayer": 15.4, "libonly": 30.4, "disconly": 9.7, "full": 38.9}
GRID_TRIALS = 24

# Clause uptake per cell, from discipline.py over each cell's own traces.  This
# is the manipulation check: the discipline half should switch on the clauses it
# names and nothing else.  `early stopping` is not comparable across cells --
# the library the tool half prescribes does it internally and never says so --
# and `inspect submission` fires without prescription in every cell, so neither
# separates the treatment.  The other three do.
GRID_CLAUSES = [
    # clause, neither, K_tool only, K_disc only, both, separates?
    ("compare with a trivial predictor", 0, 0, 24, 20, True),
    ("allocate the time budget", 0, 0, 24, 20, True),
    ("keep the best variant", 0, 2, 24, 20, True),
    ("inspect the submission", 22, 22, 24, 20, False),
    ("use early stopping", 24, 0, 24, 10, False),
]


def _grid_rel(task, col):
    _metric, hib, *cells = GRID[task]
    base = cells[0]
    d = (cells[col] - base) / abs(base) * 100.0
    return d if hib else -d


def table_grid():
    L = []
    A = L.append
    A(r"\begin{table*}[t]")
    A(r"\centering")
    A(r"\caption{The prescribed-knowledge layer split into its halves on "
      r"AutoDS-Tools over TabReD, twenty-four trials per cell on one image and "
      r"one machine. The untreated cell is given in the task's own units; the "
      r"other three as relative change against it, positive is better.}")
    A(r"\label{tab:grid}")
    A(r"\small")
    A(r"\setlength{\tabcolsep}{5pt}")
    A(r"\begin{tabular}{llrrrr}")
    A(r"\toprule")
    A(r" & & untreated & \multicolumn{3}{c}{change against untreated, \%} \\")
    A(r"\cmidrule(l){4-6}")
    A(r"Task & Metric & cell & $K_{\text{tool}}$ only & $K_{\text{disc}}$ only & both \\")
    A(r"\midrule")
    cols = [[], [], []]
    for task, entry in GRID.items():
        metric, _hib, base = entry[0], entry[1], entry[2]
        vals = [_grid_rel(task, c) for c in (1, 2, 3)]
        for i, v in enumerate(vals):
            cols[i].append(v)
        cells = " & ".join(spct(v) for v in vals)
        A("\\texttt{" + task + "} & " + metric + f" & {base:.4f} & {cells} \\\\")
    A(r"\midrule")
    A("mean over tasks & & & "
      + " & ".join(spct(sum(c) / len(c)) for c in cols) + r" \\")
    A("tasks improved & & & "
      + " & ".join(f"{sum(1 for v in c if v > 0)} of 8" for c in cols) + r" \\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\end{table*}")
    return "\n".join(L)


def table_clauses():
    L = []
    A = L.append
    A(r"\begin{table}[t]")
    A(r"\centering")
    A(r"\caption{Manipulation check for the same four cells: how many trials "
      r"leave a trace of each discipline clause. The three clauses the "
      r"discipline half names go from never to always exactly when that half is "
      r"switched on, and never otherwise. The last two rows are marked because "
      r"they do not separate the treatment: the submission is inspected without "
      r"being told to, and early stopping is hidden by the library the tool half "
      r"prescribes, which does it internally and does not report it.}")
    A(r"\label{tab:clauses}")
    A(r"\small")
    A(r"\begin{tabular}{lrrrr}")
    A(r"\toprule")
    A(r"Clause & neither & $K_{\text{tool}}$ & $K_{\text{disc}}$ & both \\")
    A(r"\midrule")
    for clause, a, b, c, d, sep in GRID_CLAUSES:
        name = clause if sep else clause + r"$^{\dagger}$"
        A(f"{name} & {a}/24 & {b}/24 & {c}/24 & {d}/20 \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\par\smallskip")
    A(r"\begin{minipage}{0.92\linewidth}\footnotesize $^{\dagger}$ does not "
      r"separate the treatment; see the caption. Cell sizes differ because a "
      r"trial cut at the time limit writes no trace.\end{minipage}")
    A(r"\end{table}")
    return "\n".join(L)


# ----------------------------------------------------------------------
# Backbone axis on TabReD: three models per system, all cells on one image at
# one concurrency setting on one machine.  A "loss" is a trial that returned no
# metric; a timeout is a trial cut at the task's 3600 s ceiling, which is not
# the same thing (Section~\ref{sec:ceiling}).  The upper AutoDS-Tools cell is
# eight trials, one per task, rather than twenty-four: the pilot showed the cell
# runs into the ceiling, and three attempts would have tripled the bill for the
# same conclusion.
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# The prescribed-knowledge layer given to the open harness, which has none of
# its own.  The layer is composed on the host and reaches only the multi-agent
# system, so the only way to hand the same text to another system is to append
# it to the task file.  Five cells of twenty-four trials on one machine, one
# image, one backbone and one concurrency setting, differing only in what was
# appended.  The trimmed cell is the discipline block with its two sections
# about training time deleted.  Byte lengths and SHA-256 prefixes of the
# appended text are given in the caption of Table~\ref{tab:layersplit}.
# ----------------------------------------------------------------------
KDISC_TERM = [
    # label, valid trials, lost, tasks returning a result, median steps,
    # median minutes, $/trial, mean relative % vs the untreated cell
    ("neither",                        24,  2, 8,  6,  2.5, 0.0029, None),
    (r"$K_{\text{disc}}$",             24, 13, 7, 18, 14.1, 0.0303, -0.05),
    (r"$K_{\text{disc}}$, minus time", 24,  0, 8,  7,  3.0, 0.0044, -0.69),
    (r"$K_{\text{tool}}$",             22, 19, 3, 14, 10.2, 0.0107, +1.21),
    ("both",                           24, 11, 6, 20, 18.4, 0.1172, +1.13),
]
# Fisher's exact, two-sided, on the loss counts
KDISC_TERM_P = {
    "disc_vs_neither": "0.0013",
    "trim_vs_disc": "2.6\\times10^{-5}",
    "trim_vs_neither": "0.49",
    "tool_vs_neither": "9.6\\times10^{-8}",
    "tool_vs_both": "0.0055",
    "both_vs_neither": "0.0078",
}


def table_kdisc_term():
    L = []
    A = L.append
    A(r"\begin{table}[t]")
    A(r"\centering")
    A(r"\caption{The prescribed-knowledge layer appended to the task file for "
      r"Terminus-2, twenty-four trials per cell on one machine, one image and one "
      r"backbone. Lost: trials ending with no submission. Steps and minutes are "
      r"medians per trial.}")
    A(r"\label{tab:kdiscterm}")
    A(r"\footnotesize")
    A(r"\setlength{\tabcolsep}{3pt}")
    A(r"\begin{tabular}{lrrrrrrr}")
    A(r"\toprule")
    A(r"Cell & Trials & Lost & Tasks & Steps & Min & \$/trial & rel.\ \% \\")
    A(r"\midrule")
    short_label = {"neither": "none", r"$K_{\text{disc}}$, minus time": r"$K_{\text{disc}}$ trimmed"}
    for label, n, lost, tasks, steps, mins, cost, rel in KDISC_TERM:
        relcell = "ref." if rel is None else spct(rel)
        label = short_label.get(label, label)
        A(f"{label} & {n} & {lost} & {tasks}/8 & {steps} & {mins:.1f} & "
          f"{cost:.4f} & {relcell} \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\par\smallskip")
    A(r"\begin{minipage}{0.97\linewidth}\scriptsize The $K_{\text{tool}}$ cell "
      r"lost two trials to a network fault and reports twenty-two. No cell had a "
      r"timeout. Tasks: how many of eight returned a metric at least once. "
      r"rel.\ \%: mean relative change against the untreated cell over the tasks "
      r"that cell returns; the last two rows average over a surviving minority. "
      r"Fisher's exact test on loss counts, "
      rf"two-sided: $K_{{\text{{disc}}}}$ against neither $p={KDISC_TERM_P['disc_vs_neither']}$; "
      rf"trimmed against $K_{{\text{{disc}}}}$ $p={KDISC_TERM_P['trim_vs_disc']}$; "
      rf"trimmed against neither $p={KDISC_TERM_P['trim_vs_neither']}$, i.e.\ "
      rf"indistinguishable; $K_{{\text{{tool}}}}$ against neither "
      rf"$p={KDISC_TERM_P['tool_vs_neither']}$; $K_{{\text{{tool}}}}$ against both "
      rf"$p={KDISC_TERM_P['tool_vs_both']}$. Five tests are reported without a "
      r"multiplicity correction; at these $p$-values a Holm correction changes no "
      r"conclusion. Trimmed: the discipline half with its two clauses about "
      r"training time removed."
      r"\end{minipage}")
    A(r"\end{table}")
    return "\n".join(L)

AXIS = {
    "Terminus-2": [
        # model, trials, losses, timeouts_or_None, in_tok_per_trial, cost, mean_delta, median_delta
        ("gemma-4-26b-a4b", 24, 6, None, 720720, 0.9263, -0.93, -0.06),
        ("gemma-4-31b",     24, 2, None,  37317, 0.0690,  None,  None),
        ("glm-4.7",         24, 0, None, 110602, 0.7615, -5.31, -0.54),
    ],
    "AutoDS-Tools": [
        ("gemma-4-26b-a4b", 24, 6,  7, 123374, 0.3990, -0.14, -0.09),
        ("gemma-4-31b",     24, 1,  4,  61606, 0.1767,  None,  None),
        ("glm-4.7",          8, 1,  4, 251010, 1.1005, +0.67, -0.02),
    ],
}


def table_axis():
    L = []
    A = L.append
    A(r"\begin{table*}[t]")
    A(r"\centering")
    A(r"\caption{Changing the backbone under each system on TabReD, everything "
      r"else fixed. $\Delta$ is the median relative change against that system's "
      r"\texttt{gemma-4-31b} row over trials that returned a metric, positive is "
      r"better.}")
    A(r"\label{tab:modelaxis}")
    A(r"\small")
    A(r"\setlength{\tabcolsep}{4pt}")
    A(r"\begin{tabular}{llrrrrrr}")
    A(r"\toprule")
    A(r"System & Backbone & Trials & Lost & Cut & In tok/trial & \$/sweep "
      r"& $\Delta$ med. \\")
    A(r"\midrule")
    for system, rows in AXIS.items():
        A(r"\multicolumn{8}{l}{\itshape " + system + r"} \\")
        for model, n, lost, cut, tin, cost, _mean, med in rows:
            cutcell = "--" if cut is None else f"{cut}"
            medcell = "ref." if med is None else spct(med) + "\\%"
            A(f" & \\texttt{{{model}}} & {n} & {lost} & {cutcell} & "
              f"{tin:,} & {cost:.3f} & {medcell} \\\\".replace(",", "\\,"))
        if system != list(AXIS)[-1]:
            A(r"\midrule")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\par\smallskip")
    A(r"\begin{minipage}{0.95\linewidth}\footnotesize Lost: no metric returned. "
      r"Cut: stopped at the time limit, which does not always lose the trial; "
      r"not recorded per trial for the open harness, which finishes far inside it. "
      r"The upper AutoDS-Tools cell is eight trials, one per task "
      r"(Section~\ref{sec:modelaxis}).\end{minipage}")
    A(r"\end{table*}")
    return "\n".join(L)


COST_SHORT = {
    "AutoDS-Tools ($K$ on)": "AutoDS ($K$ on)",
    "AutoDS-Tools ($K$ off)": "AutoDS ($K$ off)",
    "AutoDS-Tools (this work)": "AutoDS",
    "AutoDS-Tools ($K$ off, this work)": "AutoDS ($K$ off)",
    "AutoDS-Tools (shipped $K$, this work)": "AutoDS (shipped $K$)",
    "AutoDS-Tools (composed $K$, this work)": "AutoDS (composed $K$)",
    "Terminus-2 (this work)": "Terminus-2",
}


def table_cost():
    L = []
    A = L.append
    A(r"\begin{table}[!t]")
    A(r"\centering")
    A(r"\caption{Cost and wall-clock per trial from the Harbor telemetry: means "
      r"over trials of the trials' own cost, tokens and time. MLAB abbreviates "
      r"MLAgentBench. Bold: the lowest value in its column within a benchmark.}")
    A(r"\label{tab:cost}")
    A(r"\scriptsize")
    A(r"\setlength{\tabcolsep}{2.5pt}")
    A(r"\begin{tabular}{llrrrrr}")
    A(r"\toprule")
    A(r"System & Bench & $n$ & \$/tr. & In/tr. & Out/tr. & Min/tr. \\")
    A(r"\midrule")
    # The two AutoDS-Tools jobs on the earlier data preparation and the six-trial
    # Terminus-2 job on MLAgentBench are kept in TELEMETRY for the macros of the
    # deviations section but are no longer printed: the paper reports the
    # repeats on the common adapter (Section 4.6).
    OLD_ROWS = {"AutoDS-Tools ($K$ on)|both", "AutoDS-Tools ($K$ off)|both",
                "Terminus-2|MLAgentBench",
                # the cloned-edition arm left the paper on 24.09.2026
                "AutoDS-Tools (composed $K$, this work)|MLAgentBench"}
    rows = [(COST_SHORT.get(label, label), bench.replace("MLAgentBench", "MLAB"), n,
             cost / n, tin // n, tout // n, wall * conc / n / 60)
            for label, bench, _jid, n, conc, cost, tin, tout, wall in TELEMETRY
            if f"{label}|{bench}" not in OLD_ROWS]
    # the lowest value per column within a benchmark is set in bold
    best = {}
    for _lab, bench, _n, *vals in rows:
        best[bench] = [min(v, b) for v, b in zip(vals, best.get(bench, vals))]
    def cell(v, text, bench, k):
        return r"\textbf{" + text + "}" if v == best[bench][k] else text
    for lab, bench, n, usd, tin, tout, mins in rows:
        # разделитель разрядов ставим только в числах: подписи строк содержат
        # запятые, и общая замена по строке ломала бы их
        A(f"{lab} & {bench} & {n} & "
          f"{cell(usd, f'{usd:.4f}', bench, 0)} & "
          f"{cell(tin, f'{tin:,}'.replace(',', chr(92) + ','), bench, 1)} & "
          f"{cell(tout, f'{tout:,}'.replace(',', chr(92) + ','), bench, 2)} & "
          f"{cell(mins, f'{mins:.1f}', bench, 3)} \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\begin{tablenotes}\footnotesize")
    A(r"\item Distributions are right-tailed: the untreated AutoDS-Tools branch on "
      r"MLAgentBench has a median of $10.9$ minutes against a mean of $63.2$, and "
      r"one Terminus-2 trial (\texttt{feedback}, $571$ steps, \$8.71) is $84\%$ of "
      r"its job, whose median trial cost \$0.033. FEDOT.LLM calls the model from "
      r"inside its container, so its cost is its token count at list price.")
    A(r"\end{tablenotes}")
    A(r"\end{table}")
    return "\n".join(L)


# ----------------------------------------------------------------------
# TabReD: the same K-tool ablation in the greenfield condition.  These runs
# used the earlier data preparation (see the threats section) and are NOT
# comparable to PUBLISHED above; both branches share that preparation, so the
# contrast between them is internally valid.  Values verified against
# <trial>/verifier/reward.json on the Harbor hub.
# ----------------------------------------------------------------------
TABRED_ABLATION = [
    # task, metric, higher_is_better, with K-tool, without
    ("homesite-insurance", "ROC-AUC", True,  0.961639, 0.959053),
    ("ecom-offers",        "ROC-AUC", True,  0.583746, 0.619655),
    ("homecredit-default", "ROC-AUC", True,  0.864131, 0.762126),
    ("sberbank-housing",   "RMSE",    False, 0.256119, 0.247287),
    ("cooking-time",       "RMSE",    False, 0.486440, 0.487815),
    ("delivery-eta",       "RMSE",    False, 0.563853, 0.565624),
    ("maps-routing",       "RMSE",    False, 0.165726, 0.166641),
    ("weather",            "RMSE",    False, 1.525844, 1.561127),
]


# ----------------------------------------------------------------------
# Composition of the prescribed-knowledge layer, in characters.  Measured
# from the module that actually composed it: c1_prompt.py in the harbor
# tool venv (autods_harbor), verified byte-identical to the tail of
# <trial>/agent/instruction.md for the runs in this paper.  The `hardware`
# block is the first section of _DISCIPLINE ("## Hardware --- REQUIRED,
# STRICT"), separated out here because it prescribes neither a tool nor a
# training protocol.
LAYER_LIBRARY = {"tabular": 1291, "vision": 569, "nlp": 369, "graph": 1027}
LAYER_HARDWARE = 668
LAYER_DISCIPLINE = 3008          # _DISCIPLINE minus the hardware section
# Same trial, for scale: the benchmark's own task statement before the layer,
# and the layer as shipped (the block sums plus their separators).
LAYER_BASE_TASK = 1050
LAYER_TOTAL_TABULAR = 4972


# ----------------------------------------------------------------------
# Matched-provisioning arm: Terminus-2 on the image built for AutoDS, the
# same eight tasks, three attempts each.  Compare against TERMINUS_ATTEMPTS
# above, which is the same agent on the benchmark's stock image.
MATCHED_ATTEMPTS = {
    "homesite-insurance": [0.9581659166521772, 0.9586146350779462, 0.959642959211396],
    "ecom-offers":        [0.5536615895420993, 0.5526283688657418, 0.5536615895420993],
    "homecredit-default": [0.8588376004392972, 0.8588376004392972, 0.8573448006699509],
    "sberbank-housing":   [0.2778332642581892, 0.24770375249164597, 0.24770375249164597],
    "cooking-time":       [0.48381235587780297, 0.48381235587780297, 0.48381235587780297],
    "delivery-eta":       [0.5478294720234239, 0.5478294720234239, 0.5478294720234239],
    "maps-routing":       [0.16270452603270547, 0.16270452603270547, 0.16270452603270547],
    "weather":            [1.523237315400233, 1.5235929632266498, 1.5235929632266498],
}
# Trials in that arm that mentioned any of the three libraries the enriched
# image pre-installs, out of 24.  Counted over agent/trajectory.json and the
# terminal pane.
MATCHED_LIBRARY_MENTIONS = 0
MATCHED_TRIALS = 24

# How often each clause of the discipline block appears in the agent's own
# trace, with the layer (AutoDS re-run, 22 trials carrying a trajectory) and
# without it (Terminus-2 on the same image, 24 trials).  discipline.py.
# The early-stopping row is not comparable across the two columns: LightAutoML
# performs it internally and writes nothing a trace search can see.
DISCIPLINE = [
    ("early stopping",                 24, 24,  8, 22, False),
    ("compare with a trivial predictor", 0, 24, 22, 22, True),
    ("inspect the submission",           0, 24, 22, 22, True),
    ("allocate the time budget",         0, 24, 22, 22, True),
    ("keep the best variant",            0, 24, 22, 22, True),
]


def table_greenfield():
    L = []
    A = L.append
    wins = sum(1 for _t, _m, hib, on, off in TABRED_ABLATION
               if (on > off if hib else on < off))
    A(r"\begin{table}[t]")
    A(r"\centering")
    A(r"\caption{The same layer ablation in the greenfield condition. "
      r"Nothing is supplied beyond the task statement, and the branch carrying the "
      r"prescription wins %d of %d---the opposite of the improve-a-baseline count in "
      r"Table~\ref{tab:ktool}. Superseded and not printed in the paper: these runs used "
      r"an earlier data preparation at one attempt per cell, and Table~\ref{tab:grid} "
      r"repeats the same contrast on the common adapter at three attempts. Retained "
      r"in the data package as the record of the earlier measurement; both branches "
      r"share the preparation, so the contrast is "
      r"internally valid.}" % (wins, len(TABRED_ABLATION)))
    A(r"\label{tab:greenfield}")
    A(r"\small")
    A(r"\begin{tabular}{llrrr}")
    A(r"\toprule")
    A(r"Task & Metric & layer on & off & $\Delta$ (norm.) \\")
    A(r"\midrule")
    for task, metric, hib, on, off in TABRED_ABLATION:
        scale = max(abs(on), abs(off)) or 1.0
        d = ((on - off) if hib else (off - on)) / scale
        A(f"\\texttt{{{task}}} & {metric} & {on:.4f} & {off:.4f} & {d:+.3f} \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\end{table}")
    return "\n".join(L)



def table_layersplit():
    """Character budget of the layer, from the module that composed it."""
    L = []
    A = L.append
    fams = ["tabular", "vision", "nlp", "graph"]
    share = {f: 100 * LAYER_LIBRARY[f] /
             (LAYER_LIBRARY[f] + LAYER_HARDWARE + LAYER_DISCIPLINE) for f in fams}
    lo, hi = min(share.values()), max(share.values())
    A(r"\begin{table}[t]")
    A(r"\centering")
    A(r"\caption{Composition of the prescribed-knowledge layer, in characters, "
      r"measured from the module that composed it. Only the first column varies "
      r"with the task modality; the other two are fixed text appended to every "
      r"task. Blocks are measured separately and sum to five characters less than "
      r"the whole, the difference being the separators between them; these are the "
      r"figures for the edition cloned for the TabReD runs, the edition shipped "
      r"with the MLAgentBench tasks being longer (Section~\ref{sec:threats}). "
      r"On the tabular tasks studied here the layer runs to %d characters "
      r"against a %d-character task statement.}"
      % (LAYER_TOTAL_TABULAR, LAYER_BASE_TASK))
    A(r"\label{tab:layersplit}")
    A(r"\small")
    A(r"\begin{tabular}{lrrrr}")
    A(r"\toprule")
    A(r"Family & \textsc{library} & \textsc{hardware} & \textsc{discipline} & Tool share \\")
    A(r"\midrule")
    for f in fams:
        pad = r"\phantom{0}" if share[f] < 10 else ""
        A(f"{f} & {LAYER_LIBRARY[f]} & {LAYER_HARDWARE} & {LAYER_DISCIPLINE} & "
          f"${pad}{share[f]:.1f}\\%$ \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\end{table}")
    A(r"%% tool share range: %.1f--%.1f%%" % (lo, hi))
    return "\n".join(L)



def table_matched():
    """Same agent, same tasks, two images: stock and the one built for AutoDS."""
    import statistics as _st
    L = []
    A = L.append
    rows = []
    for j, task in enumerate(TASKS):
        a = _st.mean(TERMINUS_ATTEMPTS[task])
        b = _st.mean(MATCHED_ATTEMPTS[task])
        sd = _st.stdev(MATCHED_ATTEMPTS[task])
        sign = 1 if j < 3 else -1          # first three are ROC-AUC, higher is better
        rows.append((task, a, b, sd, sign * (b - a) / a * 100))
    within = sum(1 for *_x, d in rows if abs(d) <= 0.94)
    A(r"\begin{table}[t]")
    A(r"\centering")
    A(r"\caption{The open harness on the image built for the multi-agent system, "
      r"against the same harness on the benchmark's stock image. Three attempts "
      r"per task in each column; $\sigma$ is the spread of the three enriched-image "
      r"attempts. %d of %d tasks fall inside this system's own noise floor of "
      r"$0.94\%%$, and the exception is explained in the text. Across all %d trials "
      r"the agent named none of the three pre-installed libraries.}"
      % (within, len(rows), MATCHED_TRIALS))
    A(r"\label{tab:matched}")
    A(r"\small")
    A(r"\begin{tabular}{lrrrr}")
    A(r"\toprule")
    A(r"Task & stock & enriched & $\sigma$ & rel.\ diff. \\")
    A(r"\midrule")
    for task, a, b, sd, d in rows:
        A(f"\\texttt{{{task}}} & {a:.4f} & {b:.4f} & {sd:.4f} & ${d:+.2f}\\%$ \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\end{table}")
    return "\n".join(L)


def table_discipline():
    """Which clauses of the discipline block happen without being asked."""
    L = []
    A = L.append
    flips = sum(1 for _c, w, wn, _wi, _win, cmp in DISCIPLINE
                if cmp and w == 0)
    A(r"\begin{table}[t]")
    A(r"\centering")
    A(r"\caption{Trials whose trace shows each clause of the discipline block, "
      r"with the layer and without it. Both columns are the same backbone on the "
      r"same eight tasks and the same image, so the only difference is the text. "
      r"%d of the %d comparable clauses go from never to always. The early-stopping "
      r"row is marked because it is not comparable: the prescribed system delegates "
      r"it to a library that performs it internally and prints nothing a trace "
      r"search can find, so its low count records the method's blind spot rather "
      r"than the system's behaviour. Superseded and not printed in the paper: this "
      r"is the earlier on/off pair of jobs, and Table~\ref{tab:clauses} repeats the "
      r"check across the four crossed cells on the common adapter. Where the two "
      r"disagree---\emph{inspect the submission}, never traced here without the "
      r"layer and traced in 22 of 24 untreated trials there---the crossed "
      r"measurement is the one the paper uses.}" % (flips, sum(1 for r in DISCIPLINE if r[5])))
    A(r"\label{tab:discipline}")
    A(r"\small")
    A(r"\begin{tabular}{lrr}")
    A(r"\toprule")
    A(r"Clause & without the layer & with it \\")
    A(r"\midrule")
    for clause, w, wn, wi, win, comparable in DISCIPLINE:
        mark = "" if comparable else r"$^{\dagger}$"
        A(f"{clause}{mark} & {w}/{wn} & {wi}/{win} \\\\")
    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\end{table}")
    return "\n".join(L)


# ======================================================================
# Figures.  Same rule as the tables: every number comes from the data
# above, so the plots cannot drift from the text.
# ======================================================================
def fig_position():
    """Five labelled points on one axis.  Our systems below the line, the two
    reference marks above it.  Nothing else on the plot."""
    pub = {b: st.mean(normalized(PUBLISHED[b][j], j) for j in range(len(TASKS)))
           for b in PUBLISHED}
    ag = {a: st.mean(normalized(AGENTS[a][j], j) for j in range(len(TASKS))
                     if AGENTS[a][j] is not None) for a in AGENTS}
    best = max(pub, key=lambda b: pub[b])
    refs = [("tuned XGBoost", pub["XGBoost"]), (f"best published ({best})", pub[best])]
    L = []
    A = L.append
    A(r"\begin{figure}[t]")
    A(r"\centering")
    A(r"\begin{tikzpicture}[x=9.2cm,y=1cm]")
    A(r"\draw[black!60] (0,0) -- (1,0);")
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        A(f"\\draw[black!60] ({t},0) -- ({t},-0.07);")
    A(r"\node[font=\scriptsize,black!60,anchor=north] at (0,-0.10) {0 = weakest};")
    A(r"\node[font=\scriptsize,black!60,anchor=north] at (1,-0.10) {1 = strongest};")
    # references above the line
    for i, (name, v) in enumerate(refs):
        y = 0.42 + 0.42 * i
        A(f"\\draw[black!55] ({v:.4f},0.04) -- ({v:.4f},{y - 0.05:.2f});")
        A(f"\\draw[black!55,fill=white] ({v:.4f},{y:.2f}) circle (2.3pt);")
        A(f"\\node[font=\\footnotesize,black!55,anchor=west,xshift=4pt]"
          f" at ({v:.4f},{y:.2f}) {{{name}\\ {v:.2f}}};")
    # our three systems below the line
    label = {"AutoDS-Tools": "AutoDS-Tools \\emph{(multi-agent)}",
             "Terminus-2": "Terminus-2 \\emph{(open harness)}",
             "FEDOT.LLM": "FEDOT.LLM \\emph{(rigid pipeline)}"}
    for i, (k, v) in enumerate(sorted(ag.items(), key=lambda kv: -kv[1])):
        y = -0.62 - 0.42 * i
        A(f"\\draw[black!45] ({v:.4f},-0.04) -- ({v:.4f},{y + 0.05:.2f});")
        A(f"\\fill ({v:.4f},{y:.2f}) circle (2.6pt);")
        A(f"\\node[font=\\footnotesize,anchor=east,xshift=-4pt]"
          f" at ({v:.4f},{y:.2f}) {{{label.get(k, k)}\\ \\textbf{{{v:.2f}}}}};")
    A(r"\end{tikzpicture}")
    A(r"\caption{The three architectures (below the line) against the two marks "
      r"that matter (above it), on the normalised scale where $0$ is the weakest "
      r"and $1$ the strongest of the eighteen published baselines on each task. "
      r"One backbone throughout.}")
    A(r"\label{fig:position}")
    A(r"\end{figure}")
    return "\n".join(L)


def fig_signflip():
    """Эффект слоя по трём попыткам на ячейку, расходящимися полосами.

    Прежняя версия рисунка сравнивала наши три попытки с более ранним одиночным
    замером. Сравнение снято: те замеры делались нами же на другой машине, и
    противопоставление придавало обычному различию условий вес открытия.
    Осталось то, что рисунок и должен показывать, — на каких задачах слой
    помогает, на каких вредит, и где он не даёт сдать работу вовсе.
    """
    rows = []
    for task, metric, hib, on, off, *_ in MLAB:
        d = None
        if on is not None and off is not None and on[0] and off[0]:
            sc = max(abs(on[1]), abs(off[1])) or 1.0
            d = ((on[1] - off[1]) if hib else (off[1] - on[1])) / sc
        wiped = on is not None and on[0] == 0
        rows.append((task, d, wiped))
    # сначала выигрыши по убыванию, затем потери, затем обнулённые ячейки
    rows.sort(key=lambda r: (r[1] is None, -(r[1] or 0)))
    L = []
    A = L.append
    A(r"\begin{figure}[t]")
    A(r"\centering")
    A(r"\begin{tikzpicture}[x=3.1cm,y=0.58cm]")
    n = len(rows)
    A(f"\\draw[black!55] (0,1.05) -- (0,{-n - 0.2});")
    for t in (-1, -0.5, 0.5, 1):
        A(f"\\draw[black!20] ({t},0.4) -- ({t},{-n - 0.1});")
        A(f"\\node[font=\\scriptsize,black!55] at ({t},0.72) {{{t:+g}}};")
    A(r"\node[font=\scriptsize,black!55] at (0,0.72) {0};")
    for i, (task, d, wiped) in enumerate(rows):
        y = -i - 0.5
        if d is not None:
            col = "black!72" if d > 0 else "black!38"
            A(f"\\fill[{col}] (0,{y - 0.24}) rectangle ({d:.4f},{y + 0.24});")
            anchor = "east" if d > 0 else "west"
            x = -0.03 if d > 0 else 0.03
        elif wiped:
            A(f"\\node[font=\\scriptsize,black!55,anchor=west] at (0.03,{y})"
              r" {no submission in three attempts};")
            anchor, x = "east", -0.03
        else:
            A(f"\\node[font=\\scriptsize,black!40,anchor=west] at (0.03,{y})"
              r" {not repeated};")
            anchor, x = "east", -0.03
        A(f"\\node[anchor={anchor},font=\\scriptsize] at ({x},{y})"
          f" {{\\texttt{{{task}}}}};")
    A(f"\\node[font=\\footnotesize,anchor=north] at (0,{-n - 0.55})"
      r"{normalised effect of the prescribed-knowledge layer};")
    A(r"\node[font=\scriptsize,black!55,anchor=south east] at (-0.05,1.15) {layer hurts};")
    A(r"\node[font=\scriptsize,black!55,anchor=south west] at (0.05,1.15) {layer helps};")
    A(r"\end{tikzpicture}")
    A(r"\caption{The same layer, the same architecture, the same backbone, three "
      r"attempts per cell: only the task changes. Two tasks gain, three lose "
      r"outright---on those the treated branch exhausted its budget without "
      r"submitting anything, three attempts out of three---and the rest are level. "
      r"An aggregate over these tasks would report close to nothing while "
      r"concealing that the layer costs three of them their entire result.}")
    A(r"\label{fig:signflip}")
    A(r"\end{figure}")
    return "\n".join(L)


def fig_walltime():
    """One row of dots, one ceiling, one contrast. Nothing else."""
    ok = sorted(m for m in RERUN_MINUTES if m < RERUN_CEILING_MIN)
    term = TELEMETRY[0][8] * TELEMETRY[0][4] / TELEMETRY[0][3] / 60   # min/trial
    L = []
    A = L.append
    A(r"\begin{figure}[t]")
    A(r"\centering")
    A(r"\begin{tikzpicture}[x=0.145cm,y=1cm]")
    A(r"\draw[black!60] (0,0) -- (64,0);")
    for t in (0, 15, 30, 45, 60):
        A(f"\\draw[black!60] ({t},0) -- ({t},-0.07)"
          f" node[below,font=\\scriptsize,black!60]{{{t}}};")
    A(r"\node[font=\footnotesize,anchor=north] at (32,-0.5)"
      r"{minutes per trial};")
    A(f"\\draw[densely dashed,black!75] ({RERUN_CEILING_MIN},-0.12)"
      f" -- ({RERUN_CEILING_MIN},1.05);")
    A(f"\\node[font=\\scriptsize,anchor=south east] at ({RERUN_CEILING_MIN} - 0.5,1.05)"
      r"{limit};")
    for m in ok:
        A(f"\\fill[black!70] ({m},0.42) circle (2.2pt);")
    # Trials cut at the ceiling sit on the line itself: the clock we measure runs
    # to the verifier, so their raw minutes overshoot the limit that stopped them.
    for i in range(RERUN_CEILING_SCORED):
        A(f"\\draw[black!70,line width=0.7pt] ({RERUN_CEILING_MIN},{0.42 + 0.26 * i})"
          f" circle (2.2pt);")
    for i in range(RERUN_TIMEOUTS):
        x = RERUN_CEILING_MIN
        y = 0.42 + 0.26 * RERUN_CEILING_SCORED
        A(f"\\draw[black,line width=0.8pt] ({x}-1.1,{y}-0.09+{0.26 * i})"
          f" -- ({x}+1.1,{y}+0.09+{0.26 * i}) ({x}-1.1,{y}+0.09+{0.26 * i})"
          f" -- ({x}+1.1,{y}-0.09+{0.26 * i});")
    A(f"\\node[font=\\scriptsize,anchor=east,xshift=-6pt]"
      f" at ({RERUN_CEILING_MIN},{0.42 + 0.26 * (RERUN_CEILING_SCORED + RERUN_TIMEOUTS)})"
      r" {cut at the limit};")
    A(f"\\fill[black!70] ({term:.1f},0.42) circle (2.2pt);")
    A(f"\\draw[black!55] ({term:.1f},0.52) -- ({term:.1f},0.92);")
    A(f"\\node[font=\\scriptsize,anchor=south west,xshift=-2pt] at ({term:.1f},0.92)"
      r"{Terminus-2, mean};")
    A(r"\node[font=\scriptsize,anchor=south] at (34,0.92) {AutoDS-Tools, 24 trials};")
    A(r"\end{tikzpicture}")
    A(r"\caption{Agent wall-clock per trial on TabReD. Each filled dot is an "
      r"AutoDS-Tools trial that finished on its own. Four did not: they were cut "
      r"at the task's own limit, and the distinction that matters is what was on "
      r"disk at that moment. Three (open circles) had already written a "
      r"submission and are scored like any other trial; one (cross) had not, and "
      r"is the only trial we lose. The open harness averages five minutes on the "
      r"same tasks under the same limit.}")
    A(r"\label{fig:walltime}")
    A(r"\end{figure}")
    return "\n".join(L)


# ======================================================================
# Numbers for the prose.  Every figure the text quotes from the data above
# is emitted once here as a LaTeX macro, so the prose cannot drift from the
# tables.  Names are \nX for normalised means, \rkX for average ranks, and
# descriptive names otherwise.  A number that is not derivable from the data
# in this file stays a literal in the prose and is not defined here.
# ======================================================================
def _macro_name(s):
    """LaTeX macro names admit letters only."""
    return "".join(ch for ch in s if ch.isalpha())


def table_numbers():
    L = []
    A = L.append
    A("% AUTO-GENERATED by make_tables.py -- do not edit by hand.")
    A("% Macros for numbers quoted in the prose.  Regenerate after any data change.")

    def define(name, value):
        A(f"\\newcommand{{\\{name}}}{{{value}}}")

    def nmean(vals):
        got = [normalized(v, j) for j, v in enumerate(vals) if v is not None]
        return st.mean(got)


    # --- scientific case studies --------------------------------------------
    ctag = {"maize-yield": "Maize", "fdata-exit": "Fdata", "openpoly-tg": "Poly"}
    atag = {("AutoDS-Tools", "prescribed"): "AutoDS", ("Terminus-2", "plain"): "TermPlain",
            ("Terminus-2", "prescribed"): "TermPresc", ("FEDOT.LLM", "plain"): "FedotPlain",
            ("FEDOT.LLM", "prescribed"): "FedotPresc"}
    for task, (label, metric, author, _n) in CASE_META.items():
        define(f"caseAuthor{ctag[task]}", f"{author:.3f}")
        for key, tg in atag.items():
            c = case_cell((task,) + key)
            if c is None:
                continue
            n, mean, lo, hi, med, total = c
            define(f"case{tg}{ctag[task]}N", f"{n}")
            define(f"case{tg}{ctag[task]}Of", f"{total}")
            if n:
                define(f"case{tg}{ctag[task]}Mean", f"{mean:.3f}")
                define(f"case{tg}{ctag[task]}Min", f"{lo:.3f}")
                define(f"case{tg}{ctag[task]}Max", f"{hi:.3f}")
            if med is not None:
                define(f"case{tg}{ctag[task]}Min" + "utes", f"{med:.1f}")
    for (task, system, arm), extra in CASE_EXTRA.items():
        for name, vals in extra.items():
            # имена макросов не могут содержать цифр: r2 -> Rsq
            nm = "".join(w.capitalize() for w in name.replace("r2", "rsq").split("_"))
            define(f"case{atag[(system, arm)]}{ctag[task]}{nm}", f"{st.mean(vals):.3f}")
    define("caseFdataFloor", f"{CASE_FLOORS['fdata-exit']:.3f}")
    for task, sec in CASE_LAMA_FIT_S.items():
        if sec is not None:
            define(f"caseLamaFit{ctag[task]}Min", f"{sec/60:.1f}")
    presc_lost = sum(1 for (t, sy, a), (v, m) in CASES.items() if sy == "Terminus-2" and a == "prescribed" for x in v if x is None)
    presc_total = sum(len(v) for (t, sy, a), (v, m) in CASES.items() if sy == "Terminus-2" and a == "prescribed")
    plain_lost = sum(1 for (t, sy, a), (v, m) in CASES.items() if sy == "Terminus-2" and a == "plain" for x in v if x is None)
    plain_total = sum(len(v) for (t, sy, a), (v, m) in CASES.items() if sy == "Terminus-2" and a == "plain")
    define("caseTermPrescLost", str(presc_lost)); define("caseTermPrescTotal", str(presc_total))
    define("caseTermPlainLost", str(plain_lost)); define("caseTermPlainTotal", str(plain_total))
    # --- leaderboard: normalised means and average ranks -------------------
    r, pool = ranks()
    tag = {"AutoDS-Tools": "AutoDS", "Terminus-2": "Terminus", "FEDOT.LLM": "Fedot",
           "XGBoost": "XGB", "LightGBM": "LGBM", "CatBoost": "Cat", "Linear": "Linear",
           "MLP-PLR ens.": "Best"}
    for name, t in tag.items():
        define(f"n{t}", f"{nmean(pool[name]):.2f}")
        define(f"rk{t}", f"{st.mean(r[name]):.1f}")
    best = max(PUBLISHED, key=lambda b: nmean(PUBLISHED[b]))
    define("nBestName", best)
    define("nMethods", str(len(pool)))
    n_autods, n_term, n_fedot = (nmean(AGENTS[k]) for k in
                                 ("AutoDS-Tools", "Terminus-2", "FEDOT.LLM"))
    n_xgb = nmean(PUBLISHED["XGBoost"])
    define("spanShip", f"{max(n_autods, n_term, n_fedot) - min(n_autods, n_term, n_fedot):.2f}")
    define("gapXGB", f"{n_xgb - n_autods:.2f}")
    define("gapAgentsShip", f"{n_autods - n_term:.2f}")

    # --- the 2x2 grid on the normalised scale ------------------------------
    cells = {}
    for ci, lab in enumerate(("Neither", "Tool", "Disc", "Both")):
        vals = [GRID[t][2 + ci] for t in TASKS]
        cells[lab] = nmean(vals)
        define(f"nGrid{lab}", f"{cells[lab]:.2f}")
    define("nAutoDSOff", f"{cells['Neither']:.2f}")
    # average rank of the untreated AutoDS-Tools cell, substituted for the
    # shipped configuration in the pool of published methods and agents
    pool_off = {**PUBLISHED, **{k: v for k, v in AGENTS.items() if k != "AutoDS-Tools"},
                "AutoDS-Tools": [GRID[t][2] for t in TASKS]}
    rk_off = []
    for j in range(len(TASKS)):
        order = sorted(pool_off, key=lambda m: -pool_off[m][j] if HIB[j] else pool_off[m][j])
        rk_off.append(order.index("AutoDS-Tools") + 1)
    define("rkAutoDSOff", f"{st.mean(rk_off):.1f}")
    define("spanArch", f"{max(cells['Neither'], n_term, n_fedot) - min(cells['Neither'], n_term, n_fedot):.2f}")
    define("gapAgentsOff", f"{cells['Neither'] - n_term:.2f}")
    define("layerWorthNorm", f"{n_autods - cells['Neither']:.2f}")
    define("layerOverArch",
           f"{(n_autods - cells['Neither']) / (cells['Neither'] - n_term):.0f}")
    define("fedotAboveTerminus", f"{n_fedot - n_term:.2f}")
    define("fedotBelowAutoDS", f"{n_autods - n_fedot:.2f}")
    define("fedotAboveAutoDSOff", f"{n_fedot - cells['Neither']:.2f}")
    # FEDOT.LLM's normalised mean is carried by ecom-offers, where its tuned
    # ensemble beats every published method; the means without that task.
    je = TASKS.index("ecom-offers")
    noecom = [j for j in range(len(TASKS)) if j != je]
    def on(rowvals, idx):
        return st.mean(normalized(rowvals[j], j) for j in idx)
    for tg, key in (("Fedot", "FEDOT.LLM"), ("AutoDS", "AutoDS-Tools"), ("Terminus", "Terminus-2")):
        define(f"n{tg}NoEcom", f"{on(AGENTS[key], noecom):.2f}")
    define("nFedotEcom", f"{normalized(AGENTS['FEDOT.LLM'][je], je):.2f}")
    define("fedotEcomAuc", f"{AGENTS['FEDOT.LLM'][je]:.3f}")
    # relative-% means and wins per column
    cols = {lab: [_grid_rel(t, c) for t in TASKS]
            for c, lab in ((1, "Tool"), (2, "Disc"), (3, "Both"))}
    for lab, c in cols.items():
        define(f"grid{lab}Mean", f"{sum(c) / len(c):+.2f}")
        define(f"grid{lab}MeanU", f"{sum(c) / len(c):.2f}")   # unsigned, for "by X%"
        define(f"grid{lab}Wins", f"{sum(1 for v in c if v > 0)}")
    m = {lab: sum(c) / len(c) for lab, c in cols.items()}
    define("gridInteraction", f"{m['Both'] - m['Tool'] - m['Disc']:+.2f}")
    define("gridSumHalves", f"{m['Tool'] + m['Disc']:+.2f}")
    define("gridSumHalvesU", f"{m['Tool'] + m['Disc']:.2f}")
    define("gridToolEcom", f"{_grid_rel('ecom-offers', 1):+.2f}")
    define("gridToolHomecredit", f"{_grid_rel('homecredit-default', 1):+.2f}")
    rest = [abs(_grid_rel(t, 1)) for t in TASKS
            if t not in ("ecom-offers", "homecredit-default")]
    define("gridToolRestMax", f"{max(rest):.2f}")
    for k, lab in (("nolayer", "Neither"), ("libonly", "Tool"),
                   ("disconly", "Disc"), ("full", "Both")):
        define(f"grid{lab}Min", f"{GRID_MEDIAN_MIN[k]:.1f}")
        define(f"grid{lab}Cost", f"{GRID_COST[k] / GRID_TRIALS:.4f}")
    define("gridDiscCostPct",
           f"{(GRID_COST['disconly'] / GRID_COST['nolayer'] - 1) * 100:.0f}")

    # --- noise floor ---------------------------------------------------------
    def relsd(att):
        out = []
        for v in att.values():
            if len(v) > 1:
                out.append(100 * st.stdev(v) / abs(st.mean(v)))
        return out
    for sysname, t in (("Terminus-2", "Terminus"), ("AutoDS-Tools", "AutoDS"), ("FEDOT.LLM", "Fedot")):
        vals = relsd(ATTEMPTS[sysname])
        define(f"noise{t}Min", f"{min(vals):.2f}")
        define(f"noise{t}Max", f"{max(vals):.2f}")
        define(f"bitIdent{t}",
               str(sum(1 for v in ATTEMPTS[sysname].values() if len(set(v)) < len(v))))
    define("allIdentAutoDS",
           str(sum(1 for v in AUTODS_ATTEMPTS.values() if len(set(v)) == 1)))
    define("allIdentFedot",
           str(sum(1 for v in FEDOT_ATTEMPTS.values() if len(set(v)) == 1)))
    worst = max(AUTODS_ATTEMPTS, key=lambda t: (100 * st.stdev(AUTODS_ATTEMPTS[t]) /
                                                 st.mean(AUTODS_ATTEMPTS[t])
                                                 if len(AUTODS_ATTEMPTS[t]) > 1 else 0))
    define("noiseAutoDSWorstTask", worst)

    # --- the lost trial scored as zero (threats) --------------------------------
    hs = AUTODS_ATTEMPTS["homesite-insurance"] + [0.0]
    zero_vals = list(AGENTS["AutoDS-Tools"])
    zero_vals[0] = st.mean(hs)
    define("timeoutZeroHomesite", f"{st.mean(hs):.3f}")
    define("timeoutZeroNorm", f"{nmean(zero_vals):.2f}")
    pool3 = {**PUBLISHED, **AGENTS, "AutoDS-Tools": zero_vals}
    rk = []
    for j in range(len(TASKS)):
        order = sorted(pool3, key=lambda m: -pool3[m][j] if HIB[j] else pool3[m][j])
        rk.append(order.index("AutoDS-Tools") + 1)
    define("timeoutZeroRank", f"{st.mean(rk):.1f}")

    # --- matched provisioning ------------------------------------------------------
    rows = []
    for j, task in enumerate(TASKS):
        a = st.mean(TERMINUS_ATTEMPTS[task]); b = st.mean(MATCHED_ATTEMPTS[task])
        sign = 1 if HIB[j] else -1
        rows.append((task, sign * (b - a) / a * 100, st.stdev(MATCHED_ATTEMPTS[task])))
    define("matchedWithin", str(sum(1 for _t, d, _s in rows if abs(d) <= 0.94)))
    define("matchedSberbank", f"{[d for t, d, _s in rows if t == 'sberbank-housing'][0]:+.2f}")
    define("matchedSberbankSD", f"{[s for t, _d, s in rows if t == 'sberbank-housing'][0]:.3f}")
    others = [abs(d) for t, d, _s in rows if t != "sberbank-housing"]
    define("matchedOthersMax", f"{max(others):.2f}")
    define("matchedMentions", str(MATCHED_LIBRARY_MENTIONS))

    # --- MLAgentBench layer ablation ---------------------------------------------------
    wiped = [t for t, _m, _h, on, off, *_ in MLAB if on is not None and on[0] == 0]
    define("mlabWiped", str(len(wiped)))
    repeated = [row for row in MLAB if row[3] is not None]
    define("mlabRepeated", str(len(repeated)))
    off_wins = 0
    for _t, _m, hib, on, off, *_ in repeated:
        if on[0] == 0:
            off_wins += 1
        elif (off[1] > on[1]) if hib else (off[1] < on[1]):
            off_wins += 1
    define("mlabOffWins", str(off_wins))
    byname = {row[0]: row for row in MLAB}
    for task, key in (("clrs", "Clrs"), ("fathomnet", "Fathomnet"),
                      ("feedback", "Feedback"), ("ogbn-arxiv", "Ogbn"),
                      ("identify-contrails", "Contrails"), ("amp-parkinsons", "Amp"),
                      ("spaceship-titanic", "Spaceship"), ("house-price", "House")):
        _t, _m, _h, on, off, *_ = byname[task]
        dec = 2 if task == "amp-parkinsons" else 4
        if off is not None and off[0]:
            define(f"mlab{key}Off", fmt(off[1], decimals=dec))
            define(f"mlab{key}OffLo", fmt(off[2], decimals=dec))
            define(f"mlab{key}OffHi", fmt(off[3], decimals=dec))
        if on is not None and on[0]:
            define(f"mlab{key}On", fmt(on[1], decimals=dec))
            define(f"mlab{key}OnLo", fmt(on[2], decimals=dec))
            define(f"mlab{key}OnHi", fmt(on[3], decimals=dec))

    # --- MLAgentBench head-to-head ---------------------------------------------------------
    wins = [0, 0]; miss = [0, 0]
    for row in MLAB_HEAD:
        task, metric, hib, a, t, pub = row[:6]
        forced_tie = len(row) > 6
        better_a = (a[1] > t[1]) if hib else (a[1] < t[1])
        gap = abs(a[1] - t[1]) / (max(abs(a[1]), abs(t[1])) or 1.0)
        if not (gap < 0.05 or forced_tie):
            wins[0 if better_a else 1] += 1
        miss[0] += 3 - a[0]; miss[1] += 3 - t[0]
    define("headWinsAutoDS", str(wins[0]))
    define("headWinsTerminus", str(wins[1]))
    define("headMissAutoDS", str(miss[0]))
    define("headMissTerminus", str(miss[1]))
    define("headTasks", str(len(MLAB_HEAD)))

    # --- the layer given to the open harness -----------------------------------------------
    for label, n, lost, tasks, steps, mins, cost, rel in KDISC_TERM:
        key = {"neither": "Neither", r"$K_{\text{disc}}$": "Disc",
               r"$K_{\text{disc}}$, minus time": "Trim",
               r"$K_{\text{tool}}$": "Tool", "both": "Both"}[label]
        define(f"kt{key}Trials", str(n)); define(f"kt{key}Lost", str(lost))
        define(f"kt{key}Tasks", str(tasks)); define(f"kt{key}Steps", str(steps))
        define(f"kt{key}Min", f"{mins:.1f}"); define(f"kt{key}Cost", f"{cost:.4f}")
        if rel is not None:
            define(f"kt{key}Rel", f"{rel:+.2f}")
    for k, v in KDISC_TERM_P.items():
        define("ktP" + _macro_name(k.title()), v)

    # --- backbone axis --------------------------------------------------------------------------
    for sysname, t in (("Terminus-2", "Terminus"), ("AutoDS-Tools", "AutoDS")):
        for model, n, lost, cut, tok, cost, _dmean, dmed in AXIS[sysname]:
            key = t + {"gemma-4-26b-a4b": "Small", "gemma-4-31b": "Ref", "glm-4.7": "Big"}[model]
            define(f"ax{key}Trials", str(n)); define(f"ax{key}Lost", str(lost))
            if cut is not None:
                define(f"ax{key}Cut", str(cut))
                define(f"ax{key}CutPct", f"{100 * cut / n:.0f}")
            if dmed is not None:
                define(f"ax{key}Delta", f"{dmed:+.2f}")
    ref_cost = [c for m, *_r, c, _a, _b in AXIS["Terminus-2"] if m == "gemma-4-31b"][0]
    costs = [c for _m, *_r, c, _a, _b in AXIS["Terminus-2"]]
    define("axPriceSpread", f"{max(costs) / ref_cost:.0f}")

    # --- cost table, this-work rows on TabReD ----------------------------------------------------
    tel = {row[0] + "|" + row[1]: row for row in TELEMETRY}
    term = tel["Terminus-2|TabReD"]; auto = tel["AutoDS-Tools (this work)|TabReD"]

    def per_trial(row):
        _l, _b, _j, n, conc, cost, tin, tout, wall = row
        return cost / n, tin / n, tout / n, wall * conc / n / 60
    tc, ti, to, tm = per_trial(term); ac, ai, ao, am = per_trial(auto)
    define("costTerminusTabred", f"{tc:.4f}"); define("costAutoDSTabred", f"{ac:.4f}")
    define("costRatioDollars", f"{ac / tc:.2f}"); define("costRatioIn", f"{ai / ti:.2f}")
    define("costRatioOut", f"{ao / to:.1f}"); define("costRatioMin", f"{am / tm:.1f}")
    define("minTerminusTabred", f"{tm:.1f}"); define("minAutoDSTabred", f"{am:.1f}")
    fc, fi, fo, fm = per_trial(tel["FEDOT.LLM|TabReD"])
    define("costFedotTabred", f"{fc:.4f}"); define("minFedotTabred", f"{fm:.1f}")
    define("minFedotTabredMin", f"{min(sum(FEDOT_MINUTES.values(), [])):.0f}")
    define("minFedotTabredMax", f"{max(sum(FEDOT_MINUTES.values(), [])):.0f}")
    kon = tel["AutoDS-Tools ($K$ on)|both"]; koff = tel["AutoDS-Tools ($K$ off)|both"]
    define("oldLayerInPct", f"{(kon[6] / koff[6] - 1) * 100:.0f}")
    define("oldLayerOutPct", f"{(kon[7] / koff[7] - 1) * 100:.0f}")
    define("oldLayerCostPct", f"{(kon[5] / koff[5] - 1) * 100:.0f}")

    # --- the re-run wall-clock ---------------------------------------------------------------------
    ok = sorted(m for m in RERUN_MINUTES if m < RERUN_CEILING_MIN)
    define("rerunMedianMin", f"{st.median(RERUN_MINUTES):.1f}")
    define("rerunMinMin", f"{min(RERUN_MINUTES):.1f}")
    define("rerunNearCeiling", str(sum(1 for m in ok if m >= RERUN_CEILING_MIN - 15)))
    define("rerunCut", str(RERUN_TIMEOUTS + RERUN_CEILING_SCORED))
    define("rerunCutScored", str(RERUN_CEILING_SCORED))
    define("rerunLost", str(RERUN_TIMEOUTS))
    define("termMedianMin", f"{st.median(TERMINUS_TABRED_MINUTES):.1f}")
    define("termMaxMin", f"{max(TERMINUS_TABRED_MINUTES):.1f}")
    define("termMeanMin", f"{st.mean(TERMINUS_TABRED_MINUTES):.1f}")

    # --- layer composition ---------------------------------------------------------------------------
    share = {f: 100 * LAYER_LIBRARY[f] / (LAYER_LIBRARY[f] + LAYER_HARDWARE + LAYER_DISCIPLINE)
             for f in LAYER_LIBRARY}
    define("layerLibMin", str(min(LAYER_LIBRARY.values())))
    define("layerLibMax", str(max(LAYER_LIBRARY.values())))
    define("layerHardware", str(LAYER_HARDWARE))
    define("layerDiscipline", str(LAYER_DISCIPLINE))
    define("layerShareMin", f"{min(share.values()):.1f}")
    define("layerShareMax", f"{max(share.values()):.1f}")
    define("layerTotalTabular", str(LAYER_TOTAL_TABULAR))
    define("layerBaseTask", str(LAYER_BASE_TASK))
    define("layerTimesTask", f"{LAYER_TOTAL_TABULAR / LAYER_BASE_TASK:.1f}")

    # --- the greenfield ablation on the common adapter, normalised effect of "both" ---------------
    # on the leaderboard's normalised scale, per task
    eff = []
    for j, t in enumerate(TASKS):
        _m, _hib, neither, _tool, _disc, both = GRID[t]
        eff.append((t, normalized(both, j) - normalized(neither, j)))
    define("gridBothEffMin", f"{min(e for _t, e in eff):+.3f}")
    define("gridBothEffMinTask", min(eff, key=lambda x: x[1])[0])
    define("gridBothEffMax", f"{max(e for _t, e in eff):+.3f}")
    define("gridBothEffMaxTask", max(eff, key=lambda x: x[1])[0])
    define("gridBothEffMedian", f"{st.median(e for _t, e in eff):.2f}")
    define("gridBothEffAboveTwo", str(sum(1 for _t, e in eff if e > 0.020)))
    return "\n".join(L)



if __name__ == "__main__":
    for name, fn in [("numbers", table_numbers),
                     ("leaderboard", table_leaderboard),
                     ("normalized", table_normalized),
                     ("noise", table_noise),
                     ("ktool", table_ktool),
                     ("cost", table_cost),
                     ("grid", table_grid),
                     ("clauses", table_clauses),
                     ("axis", table_axis), ("kdiscterm", table_kdisc_term),
                     ("greenfield", table_greenfield),
                     ("layersplit", table_layersplit),
                     ("matched", table_matched),
                     ("discipline", table_discipline),
                     ("mlabhead", table_mlabhead), ("mlab", table_mlab),
                     ("cases", table_cases),
                     ("fig_position", fig_position),
                     ("fig_signflip", fig_signflip),
                     ("fig_walltime", fig_walltime)]:
        p = OUT / f"{name}.tex"
        p.write_text(fn() + "\n", encoding="utf-8")
        print("wrote", p.relative_to(Path(__file__).parent))

    r, pool = ranks()
    print("\n-- average ranks (sanity) --")
    for m in sorted(pool, key=lambda k: st.mean(r[k])):
        tag = "  <- agent" if m in AGENTS else ""
        print(f"  {m:<16} {st.mean(r[m]):5.2f}{tag}")
