#!/usr/bin/env python3
"""Скачать задачи MLAgentBench из набора на HuggingFace в каталог адаптера.

Задания бенчмарка лежат в datasets/mlab-protocol/<задача>/ и устроены так же,
как задачи TabReD: instruction.md, environment/, tests/, task.toml. Кладём их
рядом, в datasets/mlab/<задача>/, чтобы Harbor запускал их тем же способом.

    python3 fetch_mlab.py --list
    python3 fetch_mlab.py clrs
    python3 fetch_mlab.py clrs feedback identify-contrails fathomnet
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import re
import sys
import threading
import time
import urllib.request
from pathlib import Path

REPO = "danil-e/harbor-datasets-mlab"
SRC = "datasets/mlab-protocol"
DST = Path(__file__).resolve().parent / "harbor-tabred-adapter" / "datasets" / "mlab"
API = f"https://huggingface.co/api/datasets/{REPO}/tree/main"
RAW = f"https://huggingface.co/datasets/{REPO}/resolve/main"


def get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=300) as r:
        return r.read()


def tree(path: str, recursive: bool = False) -> list[dict]:
    """Список файлов каталога.

    HuggingFace отдаёт не больше 1000 записей за запрос, а продолжение кладёт в
    заголовок Link. Без этого каталог с картинками обрывается на середине, и
    качалка считает, что всё уже на месте.
    """
    url = f"{API}/{path}" + ("?recursive=true" if recursive else "")
    out: list[dict] = []
    while url:
        with urllib.request.urlopen(url, timeout=300) as r:
            out.extend(json.loads(r.read()))
            link = r.headers.get("Link", "")
        m = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = m.group(1) if m else None
    return out


def human(n: float) -> str:
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if n < 1024 or unit == "ГБ":
            return f"{n:.0f} {unit}" if unit == "Б" else f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} ГБ"


def fetch(task: str, workers: int = 8) -> None:
    entries = [e for e in tree(f"{SRC}/{task}", recursive=True) if e["type"] == "file"]
    # мелкие файлы вперёд: task.toml и instruction.md должны лечь раньше данных,
    # иначе прерванная загрузка оставляет каталог, который Harbor не признаёт
    entries.sort(key=lambda e: e.get("size", 0))
    total = sum(e.get("size", 0) for e in entries)
    print(f"{task}: файлов {len(entries)}, объём {human(total)}", flush=True)

    todo = []
    done = 0
    for e in entries:
        rel = e["path"][len(f"{SRC}/{task}/"):]
        out = DST / task / rel
        size = e.get("size", -1)
        if out.is_file() and out.stat().st_size == size:
            done += max(size, 0)
        else:
            todo.append((e["path"], out, max(size, 0)))
    if not todo:
        print(f"  всё уже на месте: {DST / task}", flush=True)
        return
    print(f"  докачать {len(todo)}, уже есть {human(done)}", flush=True)

    lock = threading.Lock()
    state = {"done": done, "fresh": 0}

    def one(item):
        path, out, size = item
        out.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(3):
            try:
                out.write_bytes(get(f"{RAW}/{path}"))
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
        with lock:
            state["done"] += size
            state["fresh"] += 1
            if state["fresh"] % 200 == 0:
                pct = state["done"] / max(total, 1) * 100
                print(f"  {pct:5.1f}%  скачано {state['fresh']} из {len(todo)}", flush=True)

    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        for r in pool.map(one, todo):
            pass
    print(f"  готово, скачано файлов {state['fresh']}: {DST / task}", flush=True)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--list" in sys.argv or not args:
        for e in tree(SRC):
            if e["type"] == "directory":
                print("  ", e["path"].split("/")[-1])
        return 0
    for t in args:
        fetch(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
