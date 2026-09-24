"""Проба 22.09: FEDOT получает типы столбцов из схемы TabReD.

Так делает правленый FedotTabularPredictor (fedot_patch.py, правка 4): данные
идут в FEDOT через InputData.from_dataframe с categorical_idx, где перечислены
столбцы с префиксом cat_. Эвристика TableTypesCorrector (числовой столбец с
3..12 значениями -> строки) тогда не включается. Коды категорий в TabReD
целые, поэтому матрица может остаться числовой.

Варианты:
  idx       список категорий, FEDOT без изменений;
  idx+cast  то же и заплатка FEDOT: после приведения типов матрица без
            строковых столбцов снова становится float.
  fast      правка fedot_numeric_patch.py: для числовой таблицы с заданными
            категориями типы по маске NaN, матрица не переводится в object.

    docker run --rm -m 24g --cpus 8 -v <data>:/data:ro -v $PWD:/probe:ro \
        fedot-tabred-base python /probe/fedot_schema_probe.py <task_type> <idx|idx+cast|fast>
"""
import resource
import sys
import time

import numpy as np
import pandas as pd

task_type, variant = sys.argv[1], sys.argv[2]


def peak_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20


def step(msg: str, t0: float) -> None:
    print(f"{time.time() - t0:7.1f}s  peak {peak_gb():6.2f} GB  {msg}", flush=True)


if variant == "idx+cast":
    # та же логика, что вписывается в fedot/preprocessing/data_types.py
    from fedot.preprocessing import data_types as dt

    def _as_float(self, data):
        ids = data.supplementary_data.col_type_ids["features"]
        numeric = [dt.TYPE_TO_ID[int], dt.TYPE_TO_ID[float], dt.TYPE_TO_ID[bool]]
        if data.features.dtype == object and np.isin(ids, numeric).all():
            data.features = data.features.astype(float)
        return data

    for name in ("convert_data_for_fit", "convert_data_for_predict"):
        orig = getattr(dt.TableTypesCorrector, name)
        setattr(dt.TableTypesCorrector, name,
                (lambda f: lambda self, data: _as_float(self, f(self, data)))(orig))

if variant == "fast":
    # правка исходника FEDOT, та же, что ставится в базовый образ
    import subprocess
    subprocess.run([sys.executable, "/probe/fedot_numeric_patch.py"], check=True)

t0 = time.time()
df = pd.concat([pd.read_csv("/data/train.csv"), pd.read_csv("/data/val.csv")], ignore_index=True)
test = pd.read_csv("/data/test.csv")
y = df.pop("target")
cats = [c for c in df.columns if c.startswith("cat_")]
step(f"read: train {df.shape}, test {test.shape}, cat_ columns {len(cats)}", t0)

from fedot.api.api_utils.api_data import ApiDataProcessor
from fedot.core.data.data import InputData
from fedot.core.repository.tasks import Task, TaskTypesEnum

task = Task(TaskTypesEnum.classification if task_type == "classification" else TaskTypesEnum.regression)
train = InputData.from_dataframe(df, y, categorical_idx=cats, task=task)
del df
step(f"from_dataframe: features {train.features.shape} dtype {train.features.dtype}, "
     f"categorical_idx {len(train.categorical_idx)}", t0)

if variant == "fast":
    # сверка: векторный подсчёт типов против исходного define_column_types
    from fedot.preprocessing import data_types as dt
    part = train.features[:5000]
    a, b = dt._numeric_columns_info(part), dt.define_column_types(part.astype(object))
    same = all(
        sorted(a.loc[dt._TYPES, c]) == sorted(b.loc[dt._TYPES, c])
        and all(int(a.loc[k, c]) == int(b.loc[k, c])
                for k in (dt._FLOAT_NUMBER, dt._INT_NUMBER, dt._STR_NUMBER, dt._NAN_NUMBER))
        and np.array_equal(a.loc[dt._NAN_IDS, c], b.loc[dt._NAN_IDS, c])
        for c in range(part.shape[1]))
    step(f"column types check on 5000 rows: same as define_column_types = {same}", t0)
    assert same

proc = ApiDataProcessor(task, use_input_preprocessing=True)
train = proc.define_data(features=train, is_predict=False)
step(f"define_data (fit): dtype {train.features.dtype}, FEDOT categorical "
     f"{len(train.categorical_idx)}, numerical {len(train.numerical_idx)}", t0)

from fedot.core.pipelines.pipeline_builder import PipelineBuilder
node = "rf" if task_type == "classification" else "rfr"
pipe = PipelineBuilder().add_node("scaling").add_node(node, params={"n_estimators": 5, "n_jobs": 8}).build()
pipe.fit(train)
step(f"fit scaling->{node}(5 trees) incl. pipeline preprocessing", t0)

test_data = InputData.from_dataframe(test, pd.Series(np.zeros(len(test))), categorical_idx=cats, task=task)
test_data.target = None
test_data = proc.define_data(features=test_data, is_predict=True)
pred = pipe.predict(test_data)
step(f"predict: {np.asarray(pred.predict).shape}, finite {np.isfinite(np.asarray(pred.predict, dtype=float)).all()}", t0)
