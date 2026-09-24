#!/usr/bin/env python3
"""Ветка «с опубликованным слоем» для задач MLAgentBench.

В наборе задач слой предписанного знания лежит рядом с заданием отдельным
файлом instruction_c1.md — ровно тот текст, что применялся в опубликованных
прогонах. Ветка собирается так: то же задание, но instruction.md берётся из
instruction_c1.md, а окружение и проверяющий общие с базовой веткой.

Общие они буквально: environment/ и tests/ не копируются, а связываются
ссылкой. Во-первых, fathomnet весит 4.6 ГБ и копия была бы чистой тратой
места. Во-вторых, так между ветками физически не может разойтись ни образ,
ни проверяющий — различается только текст задания, а это и есть воздействие.

    python3 make_mlab_c1.py            собрать для всех задач набора
    python3 make_mlab_c1.py clrs imdb  только для названных
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "harbor-tabred-adapter" / "datasets" / "mlab"
DST = HERE / "harbor-tabred-adapter" / "datasets" / "mlab-c1"

# Выложенный instruction_c1.md начинается с комментария о том, что это за файл
# и что базовая ветка получала instruction.md без слоя. В самом прогоне этого
# комментария не было: его дописали при выкладке артефакта. Агенту он сообщал
# бы, что тот находится в обработанной ветке, — подсказка, которой в оригинале
# не было, поэтому шапку срезаем.
HEAD = re.compile(r"\A<!--.*?-->\s*", re.S)


def build(task: str) -> str:
    s, d = SRC / task, DST / task
    if not (s / "task.toml").is_file():
        return "нет task.toml, пропускаю"
    c1 = s / "instruction_c1.md"
    if not c1.is_file():
        return "нет instruction_c1.md, пропускаю"

    d.mkdir(parents=True, exist_ok=True)
    # задание — со слоем
    text = HEAD.sub("", c1.read_text())
    (d / "instruction.md").write_text(text)
    # имя задачи меняем, чтобы ветки не путались в артефактах
    toml = (s / "task.toml").read_text().replace('name = "mlab/', 'name = "mlab-c1/')
    (d / "task.toml").write_text(toml)
    # окружение и проверяющий — общие, ссылкой
    for sub in ("environment", "tests"):
        link = d / sub
        if link.is_symlink() or link.exists():
            if link.is_symlink():
                link.unlink()
            else:
                shutil.rmtree(link)
        link.symlink_to(s / sub, target_is_directory=True)

    n_task = len((s / "instruction.md").read_text())
    n_c1 = len(text)
    return f"собрано, задание {n_task} -> {n_c1} символов (+{n_c1 - n_task})"


def main() -> int:
    tasks = sys.argv[1:] or sorted(p.name for p in SRC.iterdir() if p.is_dir())
    for t in tasks:
        print(f"{t:<20} {build(t)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
