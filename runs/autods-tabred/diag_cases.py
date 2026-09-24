#!/usr/bin/env python3
"""Сводка по трайлам одного задания Harbor: время агента, число шагов,
признаки в трассе и последние два рассуждения. Нужна, чтобы отличить
поведение агента от сбоя инфраструктуры.

    python3 diag_cases.py jobs/terminus-cases-20260910-100938
"""
import json, os, re, sys
from datetime import datetime

PAT = {
    "no-module": r"ModuleNotFoundError|No module named",
    "lightautoml": r"lightautoml|LightAutoML",
    "pip": r"pip install",
    "traceback": r"Traceback",
    "terminal": r"not showing|only echoing|unresponsive|missing the actual|no output|not displaying",
    "fit": r"fit_predict|\.fit\(",
    "oom": r"Killed|MemoryError",
    "submission": r"submission\.csv",
}
f = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
job = sys.argv[1]
for name in sorted(os.listdir(job)):
    t = os.path.join(job, name)
    if not os.path.isdir(t) or not os.path.exists(t + "/result.json"):
        continue
    r = json.load(open(t + "/result.json"))
    a = r.get("agent_execution") or {}
    dur = (f(a["finished_at"]) - f(a["started_at"])).total_seconds() / 60 if a.get("finished_at") else float("nan")
    try:
        d = json.load(open(t + "/agent/trajectory.json"))
        steps = d.get("steps", [])
        txt = json.dumps(d, ensure_ascii=False)
    except Exception as e:  # noqa: BLE001
        steps, txt = [], f"<no trajectory: {e}>"
    flags = {k: len(re.findall(p, txt)) for k, p in PAT.items()}
    rew = ""
    if os.path.exists(t + "/verifier/reward.json"):
        rew = open(t + "/verifier/reward.json").read()[:60]
    print(f"== {name}: {dur:.1f} min, {len(steps)} steps, reward {rew}")
    print("   flags:", {k: v for k, v in flags.items() if v})
    for s in steps[-2:]:
        m = s.get("message") or s.get("content") or ""
        print("   -", str(m)[:300].replace("\n", " "))
