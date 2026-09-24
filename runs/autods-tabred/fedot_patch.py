#!/usr/bin/env python3
"""Собрать из снимка FEDOT.LLM (ветка feat-fedot-ind-tabular) исходники, которые
ставятся в образ кейсов. Две правки, обе не касаются пайплайна, которым мы
пользуемся (LLM-вывод колонок и типа задачи, бэкенд FEDOT):

  1. pyproject.toml: убраны зависимости fedot-ind и dask-expr. Fedot.Industrial
     0.5.0 требует dask-ml>2025, а dask-expr прибит к старому dask, и вместе
     они не разрешаются ни pip, ни uv. Бэкенд fedot_ind в кейсах не нужен.
  2. fedotllm/predictor/__init__.py: импорт предикторов Fedot.Industrial
     сделан необязательным, иначе пакет не импортируется без fedot_ind.
  3. pyproject.toml: добавлен пин click<8.2. Снимок требует typer<0.16, а
     click 8.2+ сломал его совместимость (TyperArgument.make_metavar), и CLI
     падает ещё до разбора аргументов.
  4. Типы столбцов снаружи (22.09, для TabReD). Ключ automl.fedot.
     categorical_columns: список имён или путь к JSON-файлу со списком. Если он
     задан, FedotTabularPredictor передаёт FEDOT данные как InputData с
     categorical_idx, и эвристика FEDOT (числовой столбец с 3..12 значениями
     считается категорией и переводится в строки) не включается. По умолчанию
     ключ пуст, и поведение прежнее: кейсы 10 сентября это не затрагивает.

    python3 fedot_patch.py <снимок> <куда>
"""
import re
import shutil
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".venv", ".git", "__pycache__", "*.pyc", ".references"))

py = dst / "pyproject.toml"
t = py.read_text()
t = re.sub(r'^\s*"fedot-ind",\n', "", t, flags=re.M)
t = re.sub(r'^\s*"dask-expr[^"]*",\n', "", t, flags=re.M)
t = re.sub(r'^fedot-ind = .*\n', "", t, flags=re.M)
t = t.replace('dependencies = [\n', 'dependencies = [\n    "click<8.2",\n', 1)
assert '"click<8.2"' in t, "pyproject: не удалось добавить пин click"
py.write_text(t)

init = dst / "fedotllm" / "predictor" / "__init__.py"
t = init.read_text()
old = """from .fedot_ind import (
    FedotIndustrialTabularPredictor,
    FedotIndustrialTimeSeriesPredictor,
)
"""
new = """try:  # Fedot.Industrial is optional here (see fedot_patch.py)
    from .fedot_ind import (
        FedotIndustrialTabularPredictor,
        FedotIndustrialTimeSeriesPredictor,
    )
except ImportError:  # pragma: no cover
    FedotIndustrialTabularPredictor = None
    FedotIndustrialTimeSeriesPredictor = None
"""
assert old in t, "predictor/__init__.py: блок импорта fedot_ind не найден"
init.write_text(t.replace(old, new))
cfg = dst / "fedotllm" / "configs" / "default.yaml"
t = cfg.read_text()
old = """  fedot:
    predictor_init_kwargs:
      preset: best_quality
      with_tuning: True
    predictor_fit_kwargs: {}
"""
assert old in t, "default.yaml: секция automl.fedot не найдена"
cfg.write_text(t.replace(old, old + "    categorical_columns: null  # fedot_patch.py, правка 4\n", 1))

pred = dst / "fedotllm" / "predictor" / "fedot.py"
t = pred.read_text()
helper = '''

def _categorical_columns(config: Any, columns) -> Optional[list]:
    """Categorical columns given in automl.fedot.categorical_columns (fedot_patch.py, 4).

    A list of names or a path to a JSON file with one. Names absent from the
    table are skipped. None when the key is empty: FEDOT then guesses types.
    """
    value = config.get("categorical_columns") if hasattr(config, "get") else None
    if value is None:
        return None
    if isinstance(value, str):
        import json
        with open(value) as f:
            value = json.load(f)
    present = set(columns)
    return [str(c) for c in value if str(c) in present]


def _as_input_data(data: pd.DataFrame, label: str, categorical: list, problem: str) -> InputData:
    features = data.drop(columns=[label], errors="ignore")
    target = data[label] if label in data.columns else pd.Series(np.zeros(len(data)), index=data.index)
    input_data = InputData.from_dataframe(features, target, categorical_idx=categorical, task=problem)
    if label not in data.columns:
        input_data.target = None
    return input_data


class FedotTabularPredictor(Predictor):'''
assert t.count("\n\nclass FedotTabularPredictor(Predictor):") == 1
t = t.replace("\n\nclass FedotTabularPredictor(Predictor):", helper, 1)
old_fit = """        self.predictor = Fedot(**predictor_init_kwargs)
        self.predictor.fit(
            task.train_data,
            task.label_column,
            **unpack_omega_config(predictor_fit_kwargs),
        )
"""
new_fit = """        self.predictor = Fedot(**predictor_init_kwargs)
        self.categorical_columns = _categorical_columns(self.config, task.train_data.columns)
        if self.categorical_columns is not None:
            logger.info(f"categorical columns given: {len(self.categorical_columns)}")
            self.metadata["categorical_columns"] = self.categorical_columns
            self.predictor.fit(
                _as_input_data(task.train_data, task.label_column, self.categorical_columns,
                               PROBLEM_TO_FEDOT[task.problem_type]),
                **unpack_omega_config(predictor_fit_kwargs),
            )
        else:
            self.predictor.fit(
                task.train_data,
                task.label_column,
                **unpack_omega_config(predictor_fit_kwargs),
            )
"""
assert t.count(old_fit) == 1, "predictor/fedot.py: вызов fit табличного предиктора не найден"
t = t.replace(old_fit, new_fit)
old_pred = """    def predict(self, task: PredictionTask) -> TabularDataset:
        if (
            task.eval_metric in CLASSIFICATION_PROBA_EVAL_METRIC
            and self.problem_type in [BINARY, MULTICLASS]
        ):
            predictions = self.predictor.predict_proba(task.test_data)
        else:
            predictions = self.predictor.predict(task.test_data)
        return pd.DataFrame(predictions, columns=[task.label_column])

    def save_artifacts(self, path: str):
        self.predictor.current_pipeline.save(path)


class FedotMultiModalPredictor"""
new_pred = """    def predict(self, task: PredictionTask) -> TabularDataset:
        test_data = task.test_data
        if getattr(self, "categorical_columns", None) is not None:
            test_data = _as_input_data(test_data, task.label_column, self.categorical_columns,
                                       PROBLEM_TO_FEDOT[self.problem_type])
        if (
            task.eval_metric in CLASSIFICATION_PROBA_EVAL_METRIC
            and self.problem_type in [BINARY, MULTICLASS]
        ):
            predictions = self.predictor.predict_proba(test_data)
        else:
            predictions = self.predictor.predict(test_data)
        return pd.DataFrame(predictions, columns=[task.label_column])

    def save_artifacts(self, path: str):
        self.predictor.current_pipeline.save(path)


class FedotMultiModalPredictor"""
assert t.count(old_pred) == 1, "predictor/fedot.py: predict табличного предиктора не найден"
pred.write_text(t.replace(old_pred, new_pred))

print(f"ok: {dst}, fedot-ind/dask-expr в pyproject: {('fedot-ind' in py.read_text()) + ('dask-expr' in py.read_text())}")
