"""Кейс maize: оценка на валидации, которую видел агент, против R^2 на тесте.

AutoDS-Tools: R^2 вне фолдов LightAutoML из вывода agent/autods_trace.json.
Terminus-2: «Validation R2» его собственного разбиения 80/20 из
agent/trajectory.json.  Запуск из runs/autods-tabred:

    python3 maize_validation.py
"""
import glob
import json
import re

AUTODS = ["jobs/autods-cases-20260924-152108/maize-yield__crg5riv",
          "jobs/autods-cases-20260924-152108/maize-yield__zzJe2ed",
          "jobs/autods-cases-top-20260924-164757/maize-yield__hYcCDmJ"]
TERMINUS = sorted(glob.glob("jobs/terminus-cases-plain-20260910-100339/maize-yield__*"))


def text_of(path):
    t = json.load(open(path))
    parts = []
    for s in t["steps"]:
        parts.append(json.dumps(s.get("observation", ""), ensure_ascii=False))
        parts.extend(json.dumps(o, ensure_ascii=False) for o in s.get("observations") or [])
    return " ".join(parts)


print("system | trial | validation R2 seen by the agent | test R2 | test Pearson r")
for system, trials, trace, pat in (
        ("AutoDS-Tools", AUTODS, "autods_trace.json", r"OOF R2: (-?[\d.]+)"),
        ("Terminus-2", TERMINUS, "trajectory.json", r"Validation R2: (-?[\d.]+)")):
    for t in trials:
        val = sorted(set(re.findall(pat, text_of(f"{t}/agent/{trace}"))))
        try:
            r = json.load(open(f"{t}/verifier/reward.json"))
            test = (round(r["r2"], 3), round(r["pearson_r"], 3))
        except (FileNotFoundError, KeyError):
            test = ("no submission", "")
        print(f"{system} | {t.split('__')[-1]} | {', '.join(val) or '-'} | {test[0]} | {test[1]}")
