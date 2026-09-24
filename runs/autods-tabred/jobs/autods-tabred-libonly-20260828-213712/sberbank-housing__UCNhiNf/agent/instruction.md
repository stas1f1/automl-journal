# TabReD: sberbank-housing

Build a tabular machine-learning model for the **sberbank-housing** dataset. This
is a regression task from the TabReD benchmark. The source benchmark metric
is **rmse**.

The data is available in `/app/data`:

- `train.csv`: 18847 rows with 392 feature columns and a
  `target` column.
- `val.csv`: 4827 rows with the same columns, including
  `target`.
- `test.csv`: 4647 rows with feature columns only.
- `schema.json`: feature groups, split sizes, and task metadata.

Feature names begin with `num_`, `bin_`, or `cat_` to identify numerical, binary, and
categorical features. Missing numerical values are represented as `nan`.

Train and validate any model you choose, then write predictions for every row
of `test.csv`, in the same order, to:

`/app/predictions.csv`

The output must be a CSV file with exactly one column named `target`. It must
contain exactly 4647 finite numeric predictions and no index column.
For binary classification, output the probability or score for the positive class, not a hard class label.

## Specialized library to use — REQUIRED, STRICT
The final model you submit MUST be **LightAutoML** (pre-installed). Start from this
skeleton and adapt only the marked parts:
```python
from lightautoml.automl.presets.tabular_presets import TabularAutoML
from lightautoml.tasks import Task

task = Task('reg')            # 'reg' | 'binary' | 'multiclass' — per the instruction
roles = {'target': TARGET_COLUMN}
automl = TabularAutoML(task=task, timeout=TIME_BUDGET_SECONDS)
oof = automl.fit_predict(train_df, roles=roles)      # train_df includes the target
pred = automl.predict(test_df).data.reshape(-1)
print('MODEL_USED=', type(automl).__name__)          # must print TabularAutoML
```
You MUST print the `MODEL_USED=` line, and it MUST say `TabularAutoML`.
You MUST NOT submit predictions from `RandomForestRegressor`, `GradientBoosting*`,
`Ridge`, `LinearRegression` or any other scikit-learn estimator as the final model —
they are allowed only as a quick sanity reference you print alongside.
If an import or an API call fails, read the error and fix it (check the installed
package, e.g. `help(TabularAutoML)`); do NOT abandon LightAutoML.
For multi-target problems, fit one TabularAutoML per target.
You MAY additionally use the pre-installed **featuretools** / **feature-engine**.
