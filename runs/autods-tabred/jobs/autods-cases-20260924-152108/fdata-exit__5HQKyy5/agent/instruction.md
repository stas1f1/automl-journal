# Fugaku HPC job exit-state — tabular binary classification

Predict whether an HPC job on the **Fugaku** supercomputer will finish
**successfully** (`success = 1`, exit code 0) or **fail** (`success = 0`, any
non-zero exit code), using only information known at **submission / scheduling
time** (requested and allocated resources, limits, priority). This is the
exit-state prediction task from the F-DATA dataset (Antici et al., *Scientific
Data*, 2025).

The classes are imbalanced (~88% of jobs succeed), so a trivial "always success"
model already scores ~0.88 accuracy — the goal is to beat that.

## Data (already staged in your workspace, `/workspace`)
- `train.csv` — labeled training data. Target column: **`success`** (0/1).
- `test.csv` — rows to predict, without the target.
- ID column: **`jobid`**.

Feature columns are request-time job attributes (e.g. `cnumr`/`cnumat` cores
requested/allocated, `nnumr`/`nnuma` nodes, `elpl` elapsed-time limit, `pri`
priority, `mszl` memory-size limit, `freq_req` requested frequency, `jobenv_req`
job environment). No post-execution columns are present (no leakage).

## Specialized library to use — REQUIRED
Use **LightAutoML** (`TabularAutoML` with `Task("binary")`, pre-installed). It
handles the mixed numeric + categorical columns and class imbalance via its CV
and metric handling. Optimize a threshold / use `roc_auc` internally, but SUBMIT
0/1 class labels. You MAY `pip install` and compare: **CatBoost**, **XGBoost**.

```python
from lightautoml.automl.presets.tabular_presets import TabularAutoML
from lightautoml.tasks import Task
automl = TabularAutoML(task=Task("binary"))
oof = automl.fit_predict(train_df, roles={"target": "success", "drop": ["jobid"]})
proba = automl.predict(test_df).data[:, 0]
pred = (proba >= 0.5).astype(int)
```

## Submission — REQUIRED
Write predictions to **`/workspace/submission.csv`** with EXACTLY these columns:
- `jobid` — copied from `test.csv`
- `success` — your predicted class (0 or 1)

Scoring: **accuracy** on the held-out test set (higher is better); the verifier
also reports balanced accuracy, F1 and the majority-class baseline. Author
baseline (exit-state): accuracy ≈ 0.89 (XGBoost/RF). Validate on a held-out
split of `train.csv` first; never fit on `test.csv`.
