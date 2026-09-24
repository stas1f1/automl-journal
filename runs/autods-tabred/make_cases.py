#!/usr/bin/env python3
"""Три научных кейса как два набора заданий для Terminus-2.

Кейсы опубликованы в реестре Harbor как itmo-autods/maize-yield,
itmo-autods/fdata-exit и itmo-autods/openpoly-tg; это те самые задания, на
которых в июле снят AutoDS-Tools. Исходники лежат в datasets/cases-src и
получены командой

    harbor download itmo-autods/<task> -o harbor-tabred-adapter/datasets/cases-src

Из них собираются две ветки:

  datasets/cases        задание как опубликовано: с разделом «Specialized
                        library to use — REQUIRED», то есть с предписанием
                        библиотеки, кодом и пересказом авторского результата;
  datasets/cases-plain  то же задание без этого раздела. Данные, окружение и
                        проверяющий общие с первой веткой (ссылкой, как в
                        make_mlab_c1.py), различается только текст.

Окружение переписывается: опубликованный Dockerfile наследует приватный образ
семейства autods-mlab-tabular, которого на nss-calc2 нет. Вместо него тот же
стек ставится в python:3.12-slim (как autods_dockerfile.patch.py делает для
TabReD), плюс tmux и asciinema, без которых Terminus-2 здесь не стартует
(см. mlab_patch.py). prepare.py не меняется, в скорере только раскладывается словарь бейзлайнов (см. build); prepare.py качает данные
с Zenodo/GitHub при сборке образа, как и в оригинале.

Третья и четвёртая ветки, для FEDOT.LLM (только табличные кейсы maize-yield и
fdata-exit; OpenPoly он не принимает: единственный признак там строка PSMILES):

  datasets/cases-fedot        текст как опубликован, образ python:3.10 с fedotllm
  datasets/cases-fedot-plain  текст без раздела о библиотеке, тот же образ

Образ собирается из копии исходников FEDOT.LLM, подготовленной fedot_patch.py из
снимка ветки feat-fedot-ind-tabular (без fedot-ind и dask-expr, см. там), путь к
которой передаётся флагом --fedot-src. Агент для Harbor лежит в
fedot_harbor/ и ставится в venv инструмента harbor на хосте.

    python3 make_cases.py                      все три кейса, ветки Terminus
    python3 make_cases.py maize-yield          только названные
    python3 make_cases.py --fedot-src PATH     плюс ветки FEDOT.LLM
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE / "harbor-tabred-adapter" / "datasets"
SRC, FULL, PLAIN = DS / "cases-src", DS / "cases", DS / "cases-plain"
TASKS = ["maize-yield", "fdata-exit", "openpoly-tg"]

DOCKERFILE = """\
# Самодостаточный образ кейса: тот же стек, что в семейном образе
# autods-mlab-tabular (LightAutoML, featuretools, feature-engine, torch на CPU),
# но в системном интерпретаторе python:3.12-slim. Собран make_cases.py.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

# apt в работающем контейнере роняет привилегии на _apt, а DNS тут доступен
# только root; tmux и asciinema нужны Terminus-2 и ставятся сразу в образ.
# libgomp1 нужен LightGBM внутри LightAutoML.
RUN printf 'APT::Sandbox::User "root";\\n' > /etc/apt/apt.conf.d/99sandbox \\
 && apt-get update && apt-get install -y --no-install-recommends \\
        git curl ca-certificates build-essential libgomp1 tmux \\
 && rm -rf /var/lib/apt/lists/*

# torch с индекса CPU, иначе LightAutoML тянет многогигабайтную сборку CUDA.
RUN pip install --upgrade pip wheel "setuptools<81" \\
 && pip install "torch==2.2.2" --index-url https://download.pytorch.org/whl/cpu \\
 && pip install lightautoml featuretools feature-engine scikit-learn pandas "numpy<2" \\
        pyarrow asciinema
RUN python -c "import lightautoml, sklearn, pandas, numpy; print('tabular env OK; numpy', numpy.__version__)"

# Скорер и prepare.py оригинала ищут /opt/venvs/tabular/bin/python.
RUN mkdir -p /opt/venvs/tabular/bin \\
 && ln -s "$(command -v python)" /opt/venvs/tabular/bin/python \\
 && ln -s "$(command -v pip)" /opt/venvs/tabular/bin/pip

COPY prepare.py /opt/mlab/prepare.py
RUN python /opt/mlab/prepare.py

WORKDIR /workspace
"""

FEDOT_TASKS = ["maize-yield", "fdata-exit"]
FEDOT_DOCKERFILE = """\
# Образ кейса для FEDOT.LLM: python:3.10 (единственная версия, которую принимает
# fedotllm) с fedotllm и его бэкендом FEDOT в системном интерпретаторе.
# Собран make_cases.py из копии исходников в environment/fedotllm-src.
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

RUN printf 'APT::Sandbox::User "root";\\n' > /etc/apt/apt.conf.d/99sandbox \\
 && apt-get update && apt-get install -y --no-install-recommends \\
        git curl ca-certificates build-essential libgomp1 libgl1 libglib2.0-0 tmux \\
 && rm -rf /var/lib/apt/lists/*

COPY fedotllm-src /opt/fedotllm-src
# torch с индекса CPU до установки пакета, иначе autogluon тянет сборку CUDA.
RUN pip install --upgrade pip wheel "setuptools<81" \\
 && pip install torch --index-url https://download.pytorch.org/whl/cpu \\
 && pip install /opt/fedotllm-src pyarrow asciinema
RUN fedotllm --help >/dev/null && python -c "import fedot; print('fedot', fedot.__version__)"

# Скорер оригинала ищет /opt/venvs/tabular/bin/python.
RUN mkdir -p /opt/venvs/tabular/bin \\
 && ln -s "$(command -v python)" /opt/venvs/tabular/bin/python \\
 && ln -s "$(command -v pip)" /opt/venvs/tabular/bin/pip

COPY prepare.py /opt/mlab/prepare.py
RUN python /opt/mlab/prepare.py

WORKDIR /workspace
"""

SECTION = re.compile(r"^## Specialized library to use.*?(?=^## )", re.S | re.M)


def build(task: str) -> str:
    s = SRC / task
    if not (s / "task.toml").is_file():
        return "нет исходника в datasets/cases-src, пропускаю"
    text = (s / "instruction.md").read_text()
    if not SECTION.search(text):
        return "в задании нет раздела Specialized library, пропускаю"

    # ветка с предписанием: копия исходника с новым Dockerfile
    if FULL.joinpath(task).exists():
        shutil.rmtree(FULL / task)
    shutil.copytree(s, FULL / task, ignore=shutil.ignore_patterns("solution"))
    (FULL / task / "environment" / "Dockerfile").write_text(DOCKERFILE)
    # Harbor 0.22 принимает в reward.json только числа; опубликованный скорер
    # кладёт словарь авторских бейзлайнов под ключом baseline, и трайл падает
    # на валидации уже после подсчёта метрики. Раскладываем словарь в плоские
    # ключи baseline_<имя>; сами метрики не меняются.
    sp = FULL / task / "tests" / "score.py"
    code = re.sub(r"baseline=BASELINE(?=[,)])",
                  '**{f"baseline_{k}": v for k, v in BASELINE.items()}', sp.read_text())
    # По той же причине строка error (нет файла, нет нужных колонок) не может
    # лежать в reward.json: Harbor роняет трайл на валидации, хотя награда 0
    # уже записана. Числа остаются в reward.json, всё остальное уходит в
    # reward_full.json рядом с ним.
    emit_old = '        reward_path.write_text(json.dumps({"reward": float(reward), **extra}), encoding="utf-8")\n'
    emit_new = ('        payload = {"reward": float(reward), **extra}\n'
                '        reward_path.with_name("reward_full.json").write_text(json.dumps(payload), encoding="utf-8")\n'
                '        reward_path.write_text(json.dumps({k: v for k, v in payload.items()\n'
                '                                           if isinstance(v, (int, float)) and v is not None}), encoding="utf-8")\n')
    assert code.count(emit_old) == 1, f"{task}: не нашёл emit в score.py"
    sp.write_text(code.replace(emit_old, emit_new))
    toml = (s / "task.toml").read_text().replace('name = "itmo-autods/', 'name = "cases/')
    (FULL / task / "task.toml").write_text(toml)

    # ветка без предписания: текст без раздела, окружение и скорер ссылкой
    d = PLAIN / task
    d.mkdir(parents=True, exist_ok=True)
    plain = SECTION.sub("", text)
    (d / "instruction.md").write_text(plain)
    (d / "task.toml").write_text(toml.replace('name = "cases/', 'name = "cases-plain/'))
    for sub in ("environment", "tests"):
        link = d / sub
        if link.is_symlink():
            link.unlink()
        elif link.exists():
            shutil.rmtree(link)
        # относительная ссылка: набор переезжает на сервер под другим путём
        link.symlink_to(Path("..") / ".." / FULL.name / task / sub, target_is_directory=True)
    return f"полное {len(text)} симв., без предписания {len(plain)} симв."


def build_fedot(task: str, src: Path) -> str:
    full = FULL / task
    if not (full / "task.toml").is_file():
        return "сначала ветка Terminus, пропускаю"
    d = DS / "cases-fedot" / task
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(full, d, ignore=shutil.ignore_patterns("solution"))
    (d / "environment" / "Dockerfile").write_text(FEDOT_DOCKERFILE)
    shutil.copytree(src, d / "environment" / "fedotllm-src",
                    ignore=shutil.ignore_patterns(".venv", ".git", "__pycache__", "*.pyc", ".references"))
    toml = (full / "task.toml").read_text().replace('name = "cases/', 'name = "cases-fedot/')
    (d / "task.toml").write_text(toml)
    text = (full / "instruction.md").read_text()

    p = DS / "cases-fedot-plain" / task
    p.mkdir(parents=True, exist_ok=True)
    (p / "instruction.md").write_text(SECTION.sub("", text))
    (p / "task.toml").write_text(toml.replace('name = "cases-fedot/', 'name = "cases-fedot-plain/'))
    for sub in ("environment", "tests"):
        link = p / sub
        if link.is_symlink():
            link.unlink()
        elif link.exists():
            shutil.rmtree(link)
        link.symlink_to(Path("..") / ".." / "cases-fedot" / task / sub, target_is_directory=True)
    n = sum(1 for _ in (d / "environment" / "fedotllm-src").rglob("*") if _.is_file())
    return f"образ FEDOT.LLM, исходники {n} файлов"


def main() -> int:
    args = sys.argv[1:]
    src = None
    if "--fedot-src" in args:
        i = args.index("--fedot-src")
        src = Path(args[i + 1]).resolve()
        del args[i:i + 2]
    names = [a for a in args if not a.startswith("-")] or TASKS
    for name in names:
        print(f"  {name}: {build(name)}")
    if src is not None:
        for name in [t for t in FEDOT_TASKS if t in names]:
            print(f"  {name} (FEDOT.LLM): {build_fedot(name, src)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
