"""Послушается ли FEDOT типов столбцов из схемы TabReD (проба 22.09).

Адаптер мог бы привести столбцы по префиксам имён, как делают агентные системы:
num_ и bin_ к float32, cat_ к строкам или к pandas category. Проба проверяет,
сколько столбцов FEDOT после этого сочтёт категориальными, какого типа будет
матрица и сколько памяти уйдёт до обучения и на короткое обучение.

    docker run --rm -m 24g --cpus 4 -v <data>:/data:ro -v $PWD:/probe:ro \
        fedot-tabred-base python /probe/fedot_types_probe.py <task_type> <str|category|impute>

impute: без приведения типов, только заполнение пропусков средним по числовым
столбцам, как делал сгенерированный код редакции FEDOT.LLM 14 августа.
"""
import collections
import resource
import sys
import time

import pandas as pd

task_type, cat_as = sys.argv[1], sys.argv[2]


def peak_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20


def step(msg: str, t0: float) -> None:
    print(f"{time.time() - t0:7.1f}s  peak {peak_gb():6.2f} GB  {msg}", flush=True)


t0 = time.time()
df = pd.concat([pd.read_csv("/data/train.csv"), pd.read_csv("/data/val.csv")], ignore_index=True)
y = df.pop("target").to_numpy()
if cat_as == "impute":
    # как августовский сгенерированный код: числовые столбцы (по dtype) -> среднее
    from sklearn.impute import SimpleImputer
    num = df.select_dtypes(include="number").columns
    df[num] = SimpleImputer(strategy="mean", keep_empty_features=True).fit_transform(df[num])
for c in (df.columns if cat_as != "impute" else []):
    if c.startswith(("num_", "bin_")):
        df[c] = df[c].astype("float32")
    elif c.startswith("cat_"):
        s = df[c].astype("Int64").astype(str)  # коды категорий как метки, nan -> "<NA>"
        df[c] = s.astype("category") if cat_as == "category" else s
names = list(df.columns)
step(f"prepared ({cat_as}): {df.shape}, pandas {df.memory_usage(deep=True).sum() / 2**30:.2f} GB, "
     f"prefixes {dict(collections.Counter(n.split('_')[0] for n in names))}", t0)

from fedot.api.api_utils.api_data import ApiDataProcessor
from fedot.core.repository.tasks import Task, TaskTypesEnum

task = Task(TaskTypesEnum.classification if task_type == "classification" else TaskTypesEnum.regression)
data = ApiDataProcessor(task, use_input_preprocessing=True).define_data(features=df, target=y)
step(f"define_data: features {data.features.shape} dtype {data.features.dtype}", t0)

cat_idx = getattr(data, "categorical_idx", None)
fnames = list(getattr(data, "features_names", None) or [])
if cat_idx is not None and len(cat_idx) and fnames:
    kinds = collections.Counter(str(fnames[i]).split("_")[0] for i in cat_idx)
    print(f"FEDOT categorical: {len(cat_idx)} columns by prefix {dict(kinds)}", flush=True)
else:
    print(f"FEDOT categorical: {None if cat_idx is None else len(cat_idx)} (names unavailable)", flush=True)

from fedot.core.pipelines.pipeline_builder import PipelineBuilder
node = "rf" if task_type == "classification" else "rfr"
pipe = PipelineBuilder().add_node("scaling").add_node(node, params={"n_estimators": 5}).build()
pipe.fit(data)
step(f"fit scaling->{node}(5 trees) incl. pipeline preprocessing", t0)
