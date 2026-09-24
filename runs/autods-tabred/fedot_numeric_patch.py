"""Правка FEDOT 0.7.5 для числовых таблиц с заданными категориями (22.09).

TableTypesCorrector переводит всю матрицу признаков в object, чтобы по одной
ячейке определить типы столбцов (fedot/preprocessing/data_types.py,
convert_data_for_fit). На homecredit-default это 1.7 ГБ float, которые
превращаются в 15-18 ГБ ещё до обучения. Правка:

  1. Если матрица числовая и категории заданы снаружи (categorical_idx, его
     передаёт правленый fedotllm, fedot_patch.py, правка 4), типы столбцов
     считаются по маске NaN, и матрица остаётся float. Сведения о столбцах те
     же, что даёт define_column_types: в числовом столбце бывают только число
     и None. Без заданных категорий работает прежний путь: эвристика FEDOT
     пишет в матрицу строки, и ей нужен object.
  2. В конце convert_data_for_fit и convert_data_for_predict матрица, где все
     столбцы числовые, снова становится float.

Запуск внутри образа: python fedot_numeric_patch.py (правит установленный пакет).
"""
import pathlib

import fedot

p = pathlib.Path(fedot.__file__).parent / "preprocessing" / "data_types.py"
t = p.read_text()
if "fedot_numeric_patch" in t:
    print("already patched:", p)
    raise SystemExit(0)

old = """        data.features = data.features.astype(object)

        # Determine types for each column in features and target if it is necessary
        self.features_columns_info = define_column_types(data.features)
"""
new = """        numeric = _is_numeric_with_given_categories(data)  # fedot_numeric_patch
        if not numeric:
            data.features = data.features.astype(object)

        # Determine types for each column in features and target if it is necessary
        self.features_columns_info = (_numeric_columns_info(data.features) if numeric
                                      else define_column_types(data.features))
"""
assert t.count(old) == 1, "convert_data_for_fit: начало не найдено"
t = t.replace(old, new)

old = """        self._retain_columns_info_without_types_conflicts(data)
        return data
"""
new = """        self._retain_columns_info_without_types_conflicts(data)
        _as_float_if_numeric(data)  # fedot_numeric_patch
        return data
"""
assert t.count(old) == 2, "convert_data_for_fit/predict: конец не найден"
t = t.replace(old, new)

t += '''

# fedot_numeric_patch (automl-journal, 22.09): numeric tables stay numeric.
def _is_numeric_with_given_categories(data) -> bool:
    features = data.features
    return (isinstance(features, np.ndarray) and features.ndim == 2
            and features.dtype.kind in "biuf" and data.categorical_idx is not None)


def _numeric_columns_info(table: np.ndarray) -> pd.DataFrame:
    """What define_column_types returns for a numeric table, from the NaN mask."""
    is_int = table.dtype.kind in "iub"
    num_id, none_id = TYPE_TO_ID[int if is_int else float], TYPE_TO_ID[type(None)]
    nan = np.isnan(table) if table.dtype.kind == "f" else np.zeros(table.shape, dtype=bool)
    n_rows, n_nan = table.shape[0], nan.sum(axis=0)
    info = {}
    for col in range(table.shape[1]):
        n_num = int(n_rows - n_nan[col])
        info[col] = {
            _TYPES: [t for t, k in ((num_id, n_num), (none_id, n_nan[col])) if k],
            _FLOAT_NUMBER: 0 if is_int else n_num,
            _INT_NUMBER: n_num if is_int else 0,
            _STR_NUMBER: 0,
            _NAN_NUMBER: int(n_nan[col]),
            _NAN_IDS: np.flatnonzero(nan[:, col]),
        }
    return pd.DataFrame(info, index=[_TYPES, _FLOAT_NUMBER, _INT_NUMBER,
                                     _STR_NUMBER, _NAN_NUMBER, _NAN_IDS])


def _as_float_if_numeric(data) -> None:
    type_ids = data.supplementary_data.col_type_ids['features']
    numeric = [TYPE_TO_ID[int], TYPE_TO_ID[float], TYPE_TO_ID[bool]]
    if data.features.dtype == object and np.isin(type_ids, numeric).all():
        data.features = data.features.astype(float)
'''
p.write_text(t)
print("patched:", p)
