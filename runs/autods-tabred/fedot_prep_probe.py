"""Сколько памяти FEDOT тратит на обязательную предобработку таблицы TabReD.

Запускается в образе fedot-tabred-base с данными задачи в /data:
    docker run --rm -m 24g --cpus 4 -v <data>:/data:ro -v $PWD:/probe:ro \
        fedot-tabred-base python /probe/fedot_prep_probe.py <task_type>

Повторяет раскладку агента (train + val), строит InputData так же, как Fedot API,
и печатает форму и пиковую память процесса после каждого шага.
"""
import resource
import sys
import time

import numpy as np
import pandas as pd

task_type = sys.argv[1]  # classification | regression


def peak_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20


def step(msg: str, t0: float) -> None:
    print(f"{time.time() - t0:7.1f}s  peak {peak_gb():6.2f} GB  {msg}", flush=True)


t0 = time.time()
tr = pd.read_csv("/data/train.csv")
va = pd.read_csv("/data/val.csv")
df = pd.concat([tr, va], ignore_index=True)
del tr, va
y = df.pop("target").to_numpy()
step(f"read train+val: {df.shape}, pandas {df.memory_usage(deep=True).sum() / 2**30:.2f} GB, "
     f"object cols {int((df.dtypes == object).sum())}", t0)

from fedot.api.api_utils.api_data import ApiDataProcessor
from fedot.core.repository.tasks import Task, TaskTypesEnum

task = Task(TaskTypesEnum.classification if task_type == "classification" else TaskTypesEnum.regression)
proc = ApiDataProcessor(task, use_input_preprocessing=True)
data = proc.define_data(features=df, target=y, is_predict=False)
step(f"define_data: features {getattr(data.features, 'shape', None)} "
     f"dtype {getattr(data.features, 'dtype', None)}", t0)

try:
    cat = data.categorical_idx if hasattr(data, "categorical_idx") else None
    print("categorical idx:", None if cat is None else len(cat), flush=True)
    uniq = [len(np.unique(data.features[:, i])) for i in (cat or [])][:20]
    print("uniques of first categorical columns:", uniq, flush=True)
except Exception as e:  # диагностика, не падать
    print("categorical inspect failed:", e, flush=True)

from fedot.core.pipelines.pipeline_builder import PipelineBuilder
node = "rf" if task_type == "classification" else "rfr"
pipe = PipelineBuilder().add_node("scaling").add_node(node, params={"n_estimators": 5}).build()
pipe.fit(data)
step(f"fit scaling->{node}(5 trees) incl. pipeline preprocessing", t0)
print("preprocessor state:", type(pipe.preprocessor).__name__, flush=True)
