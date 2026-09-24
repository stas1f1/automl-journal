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

## Hardware — REQUIRED, STRICT
Resolve the compute device with EXACTLY this snippet, before any training:
```python
import torch
DEVICE = ('cuda' if torch.cuda.is_available()
          else 'mps' if torch.backends.mps.is_available() else 'cpu')
print('DEVICE=', DEVICE)
```
You MUST NOT hardcode `'cuda'`, and you MUST NOT write a CUDA-only check such as
`'cuda' if torch.cuda.is_available() else 'cpu'` — on a machine whose accelerator is
Apple MPS that silently drops you to CPU and training becomes ~10x slower.
Move the model AND every batch to `DEVICE`; print the `DEVICE=` line so the log
proves which device was used. On `mps` keep tensors float32 (no float64).

## Training discipline — REQUIRED
Do NOT stop after an arbitrary small budget (5 or 15 epochs is almost always badly
undertrained). Choose a budget large enough to converge — for a small CNN/U-Net or a
fine-tuned encoder on this data ~100 epochs is a sane starting point — and use early
stopping with patience on a held-out split. If the validation metric is still improving
when you stop, raise the budget and train again.
Validate with the TASK'S OWN metric (the one named in the instruction), not just the
training loss, and print `VALIDATION_SCORE=<value>`.

## Decision threshold — REQUIRED when predictions are thresholded
For binary / multi-label / segmentation outputs, do NOT leave the threshold at the
default 0.5. Sweep candidate thresholds on the validation split and keep the one that
maximises the task metric. With rare positives, 0.5 typically predicts nothing at all.
If positives are rare, weight them in the loss accordingly.

## Beat a trivial baseline — REQUIRED
Before submitting, score at least one trivial predictor on your validation split with
the TASK'S OWN metric — per-target median / most-frequent class, or the training mean —
and print both numbers. If your trained model does not beat the trivial predictor, do
not submit the model: fix it, or submit the simpler predictor that actually scores
better. Merely MATCHING the trivial score is also a failure — it means the model
collapsed onto the majority answer; change the approach rather than submitting it.
Think about what the metric rewards, not just about fitting the data. For example
SMAPE applies its maximum penalty whenever the true value is 0 and your prediction is
non-zero — however small — so for a target that is often exactly 0, predicting exactly
0 on those rows can matter more than fitting the non-zero rows precisely.

## Sanity-check the submission — REQUIRED
Before finishing, inspect what you are about to submit. A submission that is empty,
constant, all-negative or otherwise degenerate scores ~0 even when training looked
fine. If you see that, fix the cause (threshold, class weighting, longer training)
instead of submitting it.

## Time budget management — REQUIRED
Assume you have hours, not minutes: this run is not tightly time-boxed. At the start
allocate your wall-clock budget across stages (exploration / training / improvement /
finalisation) and print the allocation, then check elapsed time between stages.
Training the model to convergence is NOT 'optional work' — never cut the number of
epochs to finish early. Drop optional exploration instead. As a rule of thumb, if the
whole training phase finished within a couple of minutes you almost certainly
undertrained: raise the epoch budget and train again until the validation metric
stops improving.

## Keep the best model — REQUIRED
Save every model variant you train together with its validation score. Your FINAL
submission predictions MUST come from the variant with the BEST validation score —
never simply the last one trained.
