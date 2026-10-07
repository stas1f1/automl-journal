"""Что бэкенд FEDOT сделал в каждом трайле строки FEDOT.LLM на TabReD.

Время первого обучения, пропущен ли эволюционный поиск, бюджет и итог
настройки, итоговый конвейер.  Четыре трайла, упёршиеся в потолок 3600 с,
в строку статьи не входят и пропускаются.  Запуск из runs/autods-tabred:

    python3 fedot_pipelines.py jobs
"""
import glob
import re
import sys

SKIP = {"bBNNjor", "DHnjWNc", "fbt9jqR", "Bjj9qA3"}
root = sys.argv[1] if len(sys.argv) > 1 else "jobs"
print("task | trial | first fit, s | search | tuning, min | metric before | after | final pipeline")
for f in sorted(glob.glob(f"{root}/fedot-tabred-40min-schema*/*/agent/fedotllm.log")):
    task, tid = f.split("/")[-3].split("__")
    if tid in SKIP:
        continue
    s = open(f, errors="replace").read()

    def g(p):
        m = re.search(p, s)
        return m.group(1) if m else None

    search = "skipped" if "too small for composing" in s else (
        "ran" if "Pipeline composition started" in s else "?")
    fin = g(r"Final pipeline: (\{.*\})")
    nodes = re.search(r"'nodes': \[([^\]]*)\]", fin).group(1) if fin else None
    print(" | ".join(str(x) for x in (
        task, tid, g(r"Initial pipeline was fitted in ([\d.]+) sec"), search,
        g(r"Hyperparameters tuning started with ([\d.]+) min"),
        g(r"Initial metric: \[?(-?[\d.]+)"), g(r"Final metric: \[?(-?[\d.]+)"), nodes)))
