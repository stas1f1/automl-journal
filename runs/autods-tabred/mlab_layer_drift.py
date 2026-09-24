#!/usr/bin/env python3
"""Насколько опубликованный слой разошёлся с тем, что собирается сегодня.

В наборе задач слой лежит отдельным файлом instruction_c1.md. Сначала
проверяем, что это буквально задание плюс дописанный хвост, а не переписанный
текст: если хвост отделяется, его можно сравнивать со слоем, который наш
сборщик собирает сейчас. Если нет — сравнивать нечего, и это надо знать.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import sys

SRC = pathlib.Path(__file__).resolve().parent / "harbor-tabred-adapter" / "datasets" / "mlab"

# Выложенный файл начинается с комментария, объясняющего читателю, что это за
# файл. В прогоне его не было — он дописан при выкладке. Срезаем.
HEAD = re.compile(r"\A<!--.*?-->\s*", re.S)


def body(text: str) -> str:
    return HEAD.sub("", text)


def family(d: pathlib.Path) -> str:
    for line in (d / "task.toml").read_text().splitlines():
        if line.startswith("family"):
            return line.split("=", 1)[1].strip().strip('"')
    return "?"


def main() -> int:
    groups: dict[tuple[str, int, str], list[str]] = {}
    for d in sorted(p for p in SRC.iterdir() if p.is_dir()):
        if not (d / "instruction_c1.md").is_file():
            continue
        base = (d / "instruction.md").read_text()
        c1 = body((d / "instruction_c1.md").read_text())
        fam = family(d)
        if not c1.startswith(base):
            print(f"{d.name:<20} {fam:<8} задание НЕ префикс: слой не просто дописан")
            continue
        tail = c1[len(base):]
        sha = hashlib.sha256(tail.encode()).hexdigest()[:16]
        print(f"{d.name:<20} {fam:<8} хвост {len(tail):>5} символов, sha {sha}")
        groups.setdefault((fam, len(tail), sha), []).append(d.name)

    print("\nсгруппировано по семействам:")
    for (fam, n, sha), names in sorted(groups.items()):
        print(f"  {fam:<8} {n:>5} символов, sha {sha}   {', '.join(names)}")

    # заголовки разделов: совпадают ли наборы
    print("\nзаголовки разделов в хвостах:")
    seen: dict[str, list[str]] = {}
    for d in sorted(p for p in SRC.iterdir() if p.is_dir()):
        if not (d / "instruction_c1.md").is_file():
            continue
        base = (d / "instruction.md").read_text()
        c1 = body((d / "instruction_c1.md").read_text())
        if not c1.startswith(base):
            continue
        heads = tuple(l.strip() for l in c1[len(base):].splitlines() if l.startswith("#"))
        seen.setdefault("\n".join(heads), []).append(d.name)
    for heads, names in seen.items():
        print(f"  --- {', '.join(names)}")
        for h in heads.splitlines():
            print(f"      {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
