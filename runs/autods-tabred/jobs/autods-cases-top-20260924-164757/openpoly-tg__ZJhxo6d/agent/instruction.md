# Polymer glass-transition temperature (Tg) — tabular regression from PSMILES

Predict the **glass-transition temperature `Tg` (in Kelvin)** of polymers from
their structure, encoded as a **PSMILES** string (polymer SMILES with `[*]`/`*`
marking the repeat-unit connection points). This is the Tg property task from the
OpenPoly benchmark (Wang et al., *Chinese Journal of Polymer Science*, 2025).

## Data (already staged in your workspace, `/workspace`)
- `train.csv` — labeled training data. Columns: `id`, `PSMILES`, target **`Tg`**.
- `test.csv` — rows to predict. Columns: `id`, `PSMILES` (no target).
- ID column: **`id`**.

The only input feature is the `PSMILES` string — you must turn it into numeric
descriptors yourself.

## Specialized library to use — REQUIRED
Featurize `PSMILES` with **RDKit** (install it: `pip install rdkit`), computing
**Morgan fingerprints** (radius 2, 2048 bits) and/or RDKit molecular descriptors,
then fit a regressor with **LightAutoML** (`TabularAutoML`, pre-installed). This
mirrors the OpenPoly result that Morgan-fingerprint + gradient boosting is the
strongest Tg model. Convert `[*]`/`*` to a placeholder atom (e.g. replace with
`[*]`→`C`) or use `Chem.MolFromSmiles` with sanitization handling before
fingerprinting. You MAY `pip install` and compare: **CatBoost**, **XGBoost**.

```python
from rdkit import Chem
from rdkit.Chem import AllChem
import numpy as np

def fp(psmiles, n_bits=2048):
    mol = Chem.MolFromSmiles(psmiles.replace("[*]", "C").replace("*", "C"))
    if mol is None:
        return np.zeros(n_bits)
    bv = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=n_bits)
    return np.frombuffer(bytes(bv.ToBitString(), "ascii"), "u1") - ord("0")
```

## Submission — REQUIRED
Write predictions to **`/workspace/submission.csv`** with EXACTLY these columns:
- `id` — copied from `test.csv`
- `Tg` — your predicted glass-transition temperature (Kelvin)

Scoring: **R²** on the held-out Tg test set (higher is better); the verifier also
reports MAE. Author baseline for Tg on this benchmark: XGBoost + Morgan
fingerprints **R² ≈ 0.90, MAE ≈ 14.6 K**. Validate on a held-out split of
`train.csv` first; never fit on `test.csv`.
