#!/usr/bin/env python3
"""Собрать вариант набора задач TabReD с дописанным слоем предписаний.

Зачем отдельный набор, а не флаг: слой AutoDS собирается на хосте копией
autods_harbor и достаётся только его агенту. У Terminus-2 такого пути нет -- он
получает ровно instruction.md задачи. Чтобы скрестить половины слоя с ним,
единственный честный способ -- положить тот же текст в само задание.

Текст берётся из установленного пакета, а не из клона: слой в статье
зафиксирован отпечатком, а не тегом, и клон от него уже отошёл. Склейка тоже не
переписывается вручную -- вызывается сам augment(), поэтому разделители
побайтово те же, что в прогонах AutoDS.

    python3 make_kdisc_tasks.py                     datasets/tabred-kdisc
    python3 make_kdisc_tasks.py --check             только проверить
    python3 make_kdisc_tasks.py --half tool  --out tabred-ktool
    python3 make_kdisc_tasks.py --half both  --out tabred-kboth

Можно выбросить из блока дисциплины отдельные разделы -- это нужно, чтобы
проверить, какая именно часть текста меняет поведение, а не только блок целиком.
Раздел задаётся куском своего заголовка:

    python3 make_kdisc_tasks.py --out tabred-kdisc-notime \
        --drop "Training discipline" --drop "Time budget management"
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATASETS = HERE / "harbor-tabred-adapter" / "datasets"
SRC = DATASETS / "tabred"
FAMILY = "tabular"


def c1_module():
    """Модуль слоя из установленного пакета, не из клона рядом."""
    d = subprocess.run(["uv", "tool", "dir"], capture_output=True, text=True, check=True)
    base = Path(d.stdout.strip()) / "harbor/lib"
    for lib in sorted(base.glob("python3.*")):
        p = lib / "site-packages/autods_harbor"
        if p.is_dir():
            sys.path.insert(0, str(p))
            import c1_prompt as c  # noqa: E402
            return c
    raise SystemExit(f"не найден установленный autods_harbor под {base}")


def drop_sections(text: str, wanted: list[str]) -> str:
    """Убрать разделы блока, чьи заголовки `## ...` содержат заданный кусок."""
    lines = text.splitlines()
    heads = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
    keep, dropped = [], []
    for a, b in zip(heads, heads[1:] + [len(lines)]):
        if any(w.lower() in lines[a].lower() for w in wanted):
            dropped.append(lines[a])
            continue
        keep.extend(lines[a:b])
    missing = [w for w in wanted if not any(w.lower() in d.lower() for d in dropped)]
    if missing:
        raise SystemExit("не найдены разделы: " + ", ".join(missing))
    for d in dropped:
        print(f"  выброшен раздел: {d}")
    return "\n".join(keep).rstrip() + "\n"


def argval(flag: str, default: str | None = None) -> str | None:
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def main() -> int:
    check = "--check" in sys.argv
    drop = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--drop"]
    half = argval("--half", "disc")
    if half not in ("tool", "disc", "both"):
        raise SystemExit("--half принимает tool, disc или both")
    dst = DATASETS / (argval("--out") or "tabred-kdisc")

    c = c1_module()
    if drop:
        if half == "tool":
            raise SystemExit("--drop относится к блоку дисциплины, а он выключен")
        c._DISCIPLINE = drop_sections(c._DISCIPLINE, drop)

    # склейку делает сам пакет: разделители те же, что в прогонах AutoDS
    added = c.augment("", FAMILY, tool=half in ("tool", "both"),
                      discipline=half in ("disc", "both")).lstrip("\n")
    sha = hashlib.sha256(added.encode()).hexdigest()[:16]
    print(f"половина {half}: {len(added)} символов, sha {sha}")

    if not SRC.is_dir():
        raise SystemExit(f"нет исходного набора: {SRC}")
    tasks = sorted(p for p in SRC.iterdir() if p.is_dir())
    print(f"задач в наборе: {len(tasks)}")
    if check:
        return 0

    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(SRC, dst)
    for t in sorted(p for p in dst.iterdir() if p.is_dir()):
        f = t / "instruction.md"
        base = f.read_text()
        f.write_text(c.augment(base, FAMILY, tool=half in ("tool", "both"),
                               discipline=half in ("disc", "both")))
        print(f"  {t.name:<22} {len(base):>5} -> {len(f.read_text()):>5}")
    print(f"собрано: {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
