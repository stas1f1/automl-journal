#!/usr/bin/env python3
"""Дописать образам задач MLAgentBench то, без чего Terminus-2 не стартует.

Harbor ставит tmux внутрь контейнера сам, уже во время прогона. На этом хосте
apt внутри работающего контейнера не резолвит имена: он роняет привилегии на
пользователя _apt, а DNS в контейнере доступен только root. Ровно это мы уже
чинили для TabReD строкой APT::Sandbox::User "root".

Правка дописывается ОТДЕЛЬНЫМ слоем в конец Dockerfile, а не в начало: иначе
сборка потеряет кэш на слое с torch, а он самый дорогой. Заодно ставим tmux
прямо в образ — во время сборки сеть работает, и тогда прогон вообще не зависит
от apt внутри контейнера.

Ни данных, ни задания, ни скорера правка не касается.

    python3 mlab_patch.py clrs feedback
    python3 mlab_patch.py --all
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "harbor-tabred-adapter" / "datasets" / "mlab"
MARK = "# --- правка окружения прогона (см. mlab_patch.py) ---"
MARK2 = "# --- правка 2: asciinema в образ ---"

PATCH = f"""
{MARK}
# apt внутри работающего контейнера роняет привилегии на _apt, а DNS здесь
# доступен только root: без этой строки установка tmux во время прогона падает
# с "Temporary failure resolving". Во время сборки сеть работает, поэтому tmux
# ставим сразу и снимаем зависимость от apt в прогоне.
RUN printf 'APT::Sandbox::User "root";\\n' > /etc/apt/apt.conf.d/99sandbox \\
 && apt-get update \\
 && apt-get install -y --no-install-recommends tmux \\
 && rm -rf /var/lib/apt/lists/*
"""


PATCH2 = f"""
{MARK2}
# Harbor ставит ещё и asciinema, тоже через apt внутри работающего контейнера.
# Здесь этот apt не отваливается, а виснет: Harbor ждёт 120 секунд и роняет
# испытание, не дойдя до отката на pip. Ставим заранее — шаг установки
# пропускается целиком.
RUN pip install --no-cache-dir asciinema
"""


def main() -> int:
    names = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--all" in sys.argv or not names:
        names = sorted(p.name for p in ROOT.iterdir() if p.is_dir())
    for name in names:
        f = ROOT / name / "environment" / "Dockerfile"
        if not f.is_file():
            print(f"  {name}: Dockerfile не найден, пропускаю")
            continue
        text = f.read_text()
        added = []
        if MARK not in text:
            text = text.rstrip() + "\n" + PATCH
            added.append("tmux и правка apt")
        if MARK2 not in text:
            text = text.rstrip() + "\n" + PATCH2
            added.append("asciinema")
        if not added:
            print(f"  {name}: уже поправлен")
            continue
        f.write_text(text)
        print(f"  {name}: дописано — {', '.join(added)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
