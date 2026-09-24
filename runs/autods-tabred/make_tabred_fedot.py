#!/usr/bin/env python3
"""Набор datasets/tabred-fedot: восемь задач TabReD в образе с FEDOT.LLM.

Задание, данные и скорер те же, что у Terminus-2 и AutoDS-Tools (datasets/tabred);
меняется только окружение. fedotllm принимает лишь python 3.10, а образы TabReD
стоят на 3.12, поэтому окружение другое:

  datasets/tabred-fedot/_base      базовый образ fedot-tabred-base: рецепт
                                   FEDOT_DOCKERFILE из make_cases.py без шагов
                                   кейсов (prepare.py, venv скорера кейсов)
  datasets/tabred-fedot/<задача>   FROM fedot-tabred-base + COPY data/

Базовый образ собирается один раз вручную (docker build -t fedot-tabred-base
datasets/tabred-fedot/_base), задачи наследуют его: восемь установок fedotllm
по пять минут и по 5 ГБ не нужны, а на /mnt/containerd сервера места мало.

Данные связываются жёсткими ссылками (cp -al): символические Docker в контекст
сборки не берёт, а копия удвоила бы 6 ГБ. Поэтому набор строится на той же
файловой системе, где лежит datasets/tabred.

    python3 make_tabred_fedot.py --fedot-src PATH [задача ...]
    python3 make_tabred_fedot.py --memory-mb 65536 maps-routing   вариант с 64 ГБ
    python3 make_tabred_fedot.py --schema --fedot-src PATH [задача ...]
        набор tabred-fedot-schema (22.09): образ fedot-tabred-schema поверх
        базового, в нём fedotllm с правкой 4 fedot_patch.py (типы столбцов
        снаружи) и FEDOT с fedot_numeric_patch.py. Агенту нужно
        FEDOTLLM_TYPES=schema.

PATH: исходники FEDOT.LLM после fedot_patch.py, те же, что в образе кейсов
10 сентября (datasets/cases-fedot/<кейс>/environment/fedotllm-src).
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from make_cases import FEDOT_DOCKERFILE

HERE = Path(__file__).resolve().parent
DS = HERE / "harbor-tabred-adapter" / "datasets"
SRC = DS / "tabred"
OUT = DS / "tabred-fedot"
BASE_TAG = "fedot-tabred-base"
TASKS = ["homesite-insurance", "ecom-offers", "homecredit-default",
         "sberbank-housing", "cooking-time", "delivery-eta",
         "maps-routing", "weather"]

# Рецепт кейсов без хвоста, который нужен только кейсам: скорер кейсов искал
# /opt/venvs/tabular, а prepare.py качал их данные при сборке. Скорер TabReD
# вызывает системный python, которому хватает numpy и scikit-learn из FEDOT.
BASE_DOCKERFILE = FEDOT_DOCKERFILE.split("# Скорер оригинала")[0].replace(
    "# Образ кейса для FEDOT.LLM", "# Базовый образ FEDOT.LLM для задач TabReD").replace(
    "# Собран make_cases.py из копии исходников в environment/fedotllm-src.",
    "# Собран make_tabred_fedot.py; задачи наследуют его как " + BASE_TAG + ".")
# Потоки моделей FEDOT. Таблица параметров FEDOT держит n_jobs=1 у лесов и
# бустингов: при поиске он обучает много конвейеров параллельно. Начальный
# конвейер (fit_assumption_and_check_correctness) обучается до поиска, один, и
# бюджет FEDOT на него не распространяется. На weather (383 тыс. строк) лес на
# одном ядре не закончился за весь потолок задачи 3600 с (проба 21.09, стек
# py-spy). Ставим число потоков по числу ядер контейнера (cpus = 8 в task.toml);
# -1 внутри контейнера может взять все ядра хоста. Модели, гиперпараметры,
# пресет и бюджет не меняются.
BASE_DOCKERFILE = BASE_DOCKERFILE.rstrip() + """

RUN python - <<'PY'
import json, fedot, pathlib
p = pathlib.Path(fedot.__file__).parent / "core/repository/data/default_operation_params.json"
d = json.loads(p.read_text())
ops = ["rf", "rfr", "lgbm", "lgbmreg", "xgboost", "xgboostreg"]
for op in ops:
    assert d[op].get("n_jobs") == 1, (op, d[op])
    d[op]["n_jobs"] = 8
p.write_text(json.dumps(d, indent=2))
print("fedot n_jobs=8 for", ops)
PY

WORKDIR /workspace
"""

TASK_DOCKERFILE = f"""\
# Задача TabReD для FEDOT.LLM: базовый образ с fedotllm (make_tabred_fedot.py)
# плюс те же данные, что в datasets/tabred. Собрать базу заранее:
#   docker build -t {BASE_TAG} datasets/tabred-fedot/_base
FROM {BASE_TAG}:latest

COPY data/ /app/data/

WORKDIR /workspace
CMD ["bash"]
"""


def build_base(src: Path) -> str:
    d = OUT / "_base"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    (d / "Dockerfile").write_text(BASE_DOCKERFILE)
    shutil.copytree(src, d / "fedotllm-src",
                    ignore=shutil.ignore_patterns(".venv", ".git", "__pycache__", "*.pyc", ".references"))
    pin = (d / "fedotllm-src" / "pyproject.toml").read_text()
    if "click<8.2" not in pin or "fedot-ind" in pin:
        sys.exit(f"{src}: исходники не прошли fedot_patch.py (нет пина click<8.2 или остался fedot-ind)")
    return "база: Dockerfile и fedotllm-src"


def build(task: str) -> str:
    s = SRC / task
    if not (s / "task.toml").is_file():
        return "нет задачи в datasets/tabred, пропускаю"
    d = OUT / task
    if d.exists():
        shutil.rmtree(d)
    (d / "environment").mkdir(parents=True)
    shutil.copy2(s / "instruction.md", d / "instruction.md")
    shutil.copytree(s / "tests", d / "tests")
    (d / "environment" / "Dockerfile").write_text(TASK_DOCKERFILE)
    subprocess.run(["cp", "-al", str(s / "environment" / "data"), str(d / "environment" / "data")], check=True)
    toml = (s / "task.toml").read_text()
    new = re.sub(r'^name = "yandex-research/tabred__', 'name = "tabred-fedot/', toml, count=1, flags=re.M)
    assert new != toml, f"{task}: не нашёл имя задачи в task.toml"
    (d / "task.toml").write_text(new)
    mb = sum(f.stat().st_size for f in (d / "environment" / "data").iterdir()) / 2**20
    return f"данные {mb:.0f} МБ ссылками, скорер и текст без изменений"


def build_memory_variant(task: str, memory_mb: int, agent_timeout: int | None = None) -> str:
    """Копия задачи из tabred-fedot с другим memory_mb и тем же всем остальным.

    Нужна там, где FEDOT не помещается в общие 16 ГБ (проба 21.09: maps-routing
    убит по памяти и при n_jobs=1). Всё связывается жёсткими ссылками, кроме
    task.toml: его ссылку сначала разрывают, иначе правка ушла бы в оригинал.
    """
    s = OUT / task
    if not (s / "task.toml").is_file():
        return "нет задачи в tabred-fedot, сначала основной набор"
    name = f"{OUT.name}-mem{memory_mb // 1024}" + (f"-t{agent_timeout // 3600}h" if agent_timeout else "")
    d = OUT.with_name(name) / task
    if d.exists():
        shutil.rmtree(d)
    d.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-al", str(s), str(d)], check=True)
    toml = (d / "task.toml").read_text()
    (d / "task.toml").unlink()
    new, n = re.subn(r"^memory_mb = \d+", f"memory_mb = {memory_mb}", toml, flags=re.M)
    assert n == 1, f"{task}: нет memory_mb в task.toml"
    if agent_timeout:
        # потолок агента: секция [agent], timeout_sec
        new, k = re.subn(r"(\[agent\]\s*\ntimeout_sec = )[\d.]+", rf"\g<1>{float(agent_timeout)}", new)
        assert k == 1, f"{task}: нет [agent] timeout_sec в task.toml"
    new = new.replace('name = "tabred-fedot/', f'name = "{name}/', 1)
    (d / "task.toml").write_text(new)
    return f"memory_mb = {memory_mb}" + (f", потолок агента {agent_timeout} с" if agent_timeout else "") + \
        f", остальное ссылками на tabred-fedot ({d.parent.name})"


SCHEMA_TAG = "fedot-tabred-schema"
SCHEMA_DOCKERFILE = f"""\
# Слой поверх {BASE_TAG} (make_tabred_fedot.py --schema, 22.09):
# fedotllm с правкой 4 fedot_patch.py (automl.fedot.categorical_columns) и
# FEDOT с fedot_numeric_patch.py (числовая таблица с заданными категориями не
# переводится в object). Версии пакетов те же, что в {BASE_TAG}.
#   docker build -t {SCHEMA_TAG} datasets/tabred-fedot/_schema
FROM {BASE_TAG}:latest

COPY predictor_fedot.py default.yaml fedot_numeric_patch.py /tmp/schema-patch/
RUN python - <<'PY'
import fedotllm, pathlib, shutil
pkg = pathlib.Path(fedotllm.__file__).parent
shutil.copy("/tmp/schema-patch/predictor_fedot.py", pkg / "predictor" / "fedot.py")
shutil.copy("/tmp/schema-patch/default.yaml", pkg / "configs" / "default.yaml")
assert "categorical_columns" in (pkg / "predictor" / "fedot.py").read_text()
print("fedotllm patched:", pkg)
PY
RUN python /tmp/schema-patch/fedot_numeric_patch.py \\
 && python -c "from fedotllm.predictor.fedot import FedotTabularPredictor, _categorical_columns; print('import ok')"

WORKDIR /workspace
"""


def build_schema(src: Path, tasks: list[str]) -> None:
    """Слой fedot-tabred-schema и набор tabred-fedot-schema из готового tabred-fedot."""
    fedot_py = src / "fedotllm" / "predictor" / "fedot.py"
    cfg = src / "fedotllm" / "configs" / "default.yaml"
    if "_categorical_columns" not in fedot_py.read_text() or "categorical_columns" not in cfg.read_text():
        sys.exit(f"{src}: исходники без правки 4 fedot_patch.py")
    d = OUT / "_schema"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    (d / "Dockerfile").write_text(SCHEMA_DOCKERFILE)
    shutil.copy2(fedot_py, d / "predictor_fedot.py")
    shutil.copy2(cfg, d / "default.yaml")
    shutil.copy2(HERE / "fedot_numeric_patch.py", d / "fedot_numeric_patch.py")
    print(f"слой: {d}")
    name = f"{OUT.name}-schema"
    for task in tasks:
        s = OUT / task
        if not (s / "task.toml").is_file():
            print(f"{task}: нет задачи в tabred-fedot, пропускаю")
            continue
        t = OUT.with_name(name) / task
        if t.exists():
            shutil.rmtree(t)
        t.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cp", "-al", str(s), str(t)], check=True)
        # разорвать ссылки на файлы, которые меняются
        for f in (t / "task.toml", t / "environment" / "Dockerfile"):
            text = f.read_text()
            f.unlink()
            if f.name == "task.toml":
                text = text.replace('name = "tabred-fedot/', f'name = "{name}/', 1)
                assert f'name = "{name}/' in text, f"{task}: имя задачи не заменено"
            else:
                assert f"FROM {BASE_TAG}:latest" in text
                text = text.replace(f"FROM {BASE_TAG}:latest", f"FROM {SCHEMA_TAG}:latest")
            f.write_text(text)
        print(f"{task}: {t.parent.name}, образ {SCHEMA_TAG}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fedot-src", type=Path)
    ap.add_argument("--memory-mb", type=int,
                    help="собрать вариант tabred-fedot-mem<ГБ> с этим лимитом из готового набора")
    ap.add_argument("--agent-timeout", type=int,
                    help="вместе с --memory-mb: потолок агента в секундах (вариант -t<ч>h)")
    ap.add_argument("--schema", action="store_true",
                    help="слой fedot-tabred-schema и набор tabred-fedot-schema (нужен --fedot-src)")
    ap.add_argument("tasks", nargs="*")
    a = ap.parse_args()
    for t in a.tasks:
        if t not in TASKS:
            sys.exit(f"неизвестная задача {t}")
    if a.memory_mb:
        for t in a.tasks or TASKS:
            print(f"{t}: {build_memory_variant(t, a.memory_mb, a.agent_timeout)}")
        return
    if not a.fedot_src:
        sys.exit("нужен --fedot-src (или --memory-mb для варианта)")
    if a.schema:
        build_schema(a.fedot_src.resolve(), a.tasks or TASKS)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    print(build_base(a.fedot_src.resolve()))
    for t in a.tasks or TASKS:
        print(f"{t}: {build(t)}")


if __name__ == "__main__":
    main()
