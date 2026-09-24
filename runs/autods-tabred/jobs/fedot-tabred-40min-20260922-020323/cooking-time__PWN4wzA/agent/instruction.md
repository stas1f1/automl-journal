# TabReD: cooking-time

Build a tabular machine-learning model for the **cooking-time** dataset. This
is a regression task from the TabReD benchmark. The source benchmark metric
is **rmse**.

The data is available in `/app/data`:

- `train.csv`: 227087 rows with 192 feature columns and a
  `target` column.
- `val.csv`: 51251 rows with the same columns, including
  `target`.
- `test.csv`: 41648 rows with feature columns only.
- `schema.json`: feature groups, split sizes, and task metadata.

Feature names begin with `num_`, `bin_`, or `cat_` to identify numerical, binary, and
categorical features. Missing numerical values are represented as `nan`.

Train and validate any model you choose, then write predictions for every row
of `test.csv`, in the same order, to:

`/app/predictions.csv`

The output must be a CSV file with exactly one column named `target`. It must
contain exactly 41648 finite numeric predictions and no index column.
For binary classification, output the probability or score for the positive class, not a hard class label.