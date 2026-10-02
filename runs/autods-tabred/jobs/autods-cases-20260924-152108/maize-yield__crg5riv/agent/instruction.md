# Maize grain yield — tabular regression

Predict maize **grain yield** for field plots from the Genomes-to-Fields (G2F)
initiative, using genotype (pedigree), environment (site/year) and management /
agronomic measurements. This is the official split from Kick et al., *G3* 2023
("Yield prediction through integration of genetic, environment, and management
data"). Rows span 41 sites over 6 years; the train/test split is stratified so
that a given location-year appears in only one of the two sets (no environment
leakage).

## Data (already staged in your workspace, `/workspace`)
- `train.csv` — labeled training data. Target column: **`GrainYield`** (bushels/acre).
- `test.csv` — rows to predict, without the target. Same feature columns as `train.csv`.
- ID column: **`Index`** (a unique row id, present in both files — do NOT use it as a feature).

Post-harvest outcome columns that leak the target (`PlotWeight`, `TestWeight`,
`PercentGrainMoisture`, `PercentStand`) have already been removed. Use the
remaining pedigree / site / management columns (e.g. `F`, `M`, `Pedigree`,
`ExperimentCode`, `Year`, `DaysToPollen`, `DaysToSilk`, `Height`, `EarHeight`,
`StandCount`, `RootLodging`, `StalkLodging`).

## Specialized library to use — REQUIRED
Use **LightAutoML** (`TabularAutoML`) as the primary approach (pre-installed in
this environment). It natively handles the mixed numeric + high-cardinality
categorical features (pedigree, experiment code) and does its own CV / feature
selection, which fits this heterogeneous agronomic table far better than a
hand-rolled single estimator. You MAY `pip install` and compare these
alternatives: **AutoGluon**, **CatBoost**.

```python
from lightautoml.automl.presets.tabular_presets import TabularAutoML
from lightautoml.tasks import Task
automl = TabularAutoML(task=Task("reg"))
oof = automl.fit_predict(train_df, roles={"target": "GrainYield", "drop": ["Index"]})
pred = automl.predict(test_df).data[:, 0]
```

## Submission — REQUIRED
Write predictions to **`/workspace/submission.csv`** with EXACTLY these columns:
- `Index` — copied from `test.csv`
- `GrainYield` — your predicted yield

Scoring: **R²** on the held-out Test set (higher is better). The verifier also
reports RMSE, normalized RMSE (RMSE / std) and Pearson r. Author baselines on
this split: DNN normalized RMSE ≈ 0.948, Pearson r ≈ 0.426 (best model BLUP
r ≈ 0.461). Validate on a held-out split of `train.csv` first; never fit on `test.csv`.
