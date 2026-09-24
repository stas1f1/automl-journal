#!/usr/bin/env python3
"""Дописать tests/test.sh задачам MLAgentBench.

Набор на HuggingFace отдаёт только tests/score.py, а раздел [verifier.env] в
task.toml пуст. Нашей версии Harbor этого мало: при пустом разделе проверяющий
запускается в среде задачи и точкой входа обязан быть tests/test.sh, иначе
каталог вообще не считается задачей ("There are 0 tasks available").

Перемычка ничего не решает за скорер. Пути она берёт из самой задачи:
посылку — из artifacts в task.toml, ключ — оттуда, куда его кладёт
environment/prepare.py. Метрика остаётся ровно та, что в score.py.

    python3 mlab_testsh.py clrs feedback identify-contrails fathomnet
    python3 mlab_testsh.py --all
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "harbor-tabred-adapter" / "datasets" / "mlab"

TEMPLATE = """#!/bin/bash
# Перемычка между Harbor и score.py задачи. Написана нами: набор задач её не
# содержит. Скорер и метрика не тронуты, пути взяты из task.toml и prepare.py.
set -u
mkdir -p /logs/verifier
echo "0" > /logs/verifier/reward.txt
printf '{{"reward": 0.0}}\\n' > /logs/verifier/reward.json

python /tests/score.py \\
  --submission {sub} \\
  --answer {ans} \\
  --reward-json /logs/verifier/reward.json || true

python - <<'PY' || true
import json
d = json.load(open("/logs/verifier/reward.json"))
open("/logs/verifier/reward.txt", "w").write("%.12g\\n" % float(d.get("reward", 0.0)))
PY

chmod 664 /logs/verifier/reward.txt /logs/verifier/reward.json 2>/dev/null || true
exit 0
"""


def submission_path(task: Path) -> str:
    text = (task / "task.toml").read_text()
    m = re.search(r'^artifacts\s*=\s*\[\s*"([^"]+)"', text, re.M)
    if not m:
        raise SystemExit(f"{task.name}: в task.toml нет artifacts, путь посылки неизвестен")
    return m.group(1)


def answer_path(task: Path) -> str:
    text = (task / "environment" / "prepare.py").read_text()
    names = sorted(set(re.findall(r'answer\.[A-Za-z0-9]+', text)))
    if len(names) != 1:
        raise SystemExit(f"{task.name}: не понял, как называется ключ: {names}")
    m = re.search(r'MLAB_ANSWER_DIR"\s*,\s*"([^"]+)"', text)
    return f"{m.group(1) if m else '/opt/mlab'}/{names[0]}"


def main() -> int:
    tasks = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--all" in sys.argv or not tasks:
        tasks = sorted(p.name for p in ROOT.iterdir() if p.is_dir())
    for name in tasks:
        task = ROOT / name
        if not task.is_dir():
            print(f"  {name}: каталога нет, пропускаю")
            continue
        sub, ans = submission_path(task), answer_path(task)
        out = task / "tests" / "test.sh"
        out.write_text(TEMPLATE.format(sub=sub, ans=ans))
        out.chmod(0o755)
        print(f"  {name:20} посылка {sub}   ключ {ans}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
