#!/usr/bin/env python3
"""Собрать результаты кейсов из заданий Harbor в один JSON.

Для каждого трайла: система, ветка, кейс, есть ли файл ответа, награда и
остальные метрики скорера (reward_full.json, если есть, иначе reward.json),
минуты агента. Запускать на машине с каталогом jobs/:

    python3 collect_cases.py jobs/terminus-cases-plain-2026* jobs/terminus-cases-2026* > cases.json
"""
import glob, json, os, sys
from datetime import datetime

f = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
rows = []
for job in sys.argv[1:]:
    jn = os.path.basename(job.rstrip("/"))
    system = "FEDOT.LLM" if jn.startswith("fedot") else "Terminus-2"
    arm = "plain" if "plain" in jn else "prescribed"
    for t in sorted(glob.glob(job + "/*/")):
        if not os.path.exists(t + "result.json"):
            continue
        r = json.load(open(t + "result.json"))
        a = r.get("agent_execution") or {}
        mins = (f(a["finished_at"]) - f(a["started_at"])).total_seconds() / 60 if a.get("finished_at") else None
        rew = None
        for name in ("reward_full.json", "reward.json"):
            p = t + "verifier/" + name
            if os.path.exists(p):
                rew = json.load(open(p)); break
        exc = (r.get("exception_info") or {}).get("exception_type")
        rows.append({
            "system": system, "arm": arm, "task": os.path.basename(t.rstrip("/")).split("__")[0],
            "trial": os.path.basename(t.rstrip("/")), "job": jn,
            "submitted": bool(rew) and "error" not in rew,
            "reward": rew.get("reward") if rew else None,
            "metrics": {k: v for k, v in (rew or {}).items() if k not in ("reward", "error") and isinstance(v, (int, float))},
            "error": (rew or {}).get("error"), "exception": exc, "agent_minutes": mins,
        })
json.dump(rows, sys.stdout, indent=1, ensure_ascii=False)
