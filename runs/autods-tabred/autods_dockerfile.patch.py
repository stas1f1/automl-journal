#!/usr/bin/env python3
"""Provision the specialized-library environment the AutoDS C1 layer assumes.

The C1 tool prescription states LightAutoML is "pre-installed"; the plain TabReD
adapter image is python:3.13-slim with numpy/pandas/scikit-learn only, and
LightAutoML does not build on 3.13 (statsmodels fails: no pkg_resources).
This rewrites each task Dockerfile to python:3.12-slim plus the libraries the
layer names, restoring the environment the published AutoDS runs had.

The original is kept next to it as Dockerfile.plain, so the untouched image used
by the Terminus-2 and FEDOT.LLM runs can be restored with --revert.
"""
import sys
from pathlib import Path

TASKS = Path("harbor-tabred-adapter/datasets/tabred")

NEW = """FROM python:3.12-slim

WORKDIR /workspace

# apt drops privileges to the _apt user while fetching, and on hosts whose
# container DNS is only reachable as root that lookup fails with "Temporary
# failure resolving".  Fetching as root changes who downloads, not what gets
# installed, and is a no-op where the default already works.
RUN printf 'APT::Sandbox::User "root";\\n' > /etc/apt/apt.conf.d/99sandbox

# Install system dependencies.  libgomp1 is the OpenMP runtime LightGBM's
# shared library dlopen()s; the pip wheel does not carry it and python:*-slim
# does not ship it.  Without it the prescribed stack imports fine and then dies
# inside fit_predict with "libgomp.so.1: cannot open shared object file",
# which reads as a modelling failure and is not one.
RUN apt-get update && apt-get install -y \\
    git \\
    libgomp1 \\
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \\
    "numpy>=2.4,<3" \\
    "pandas>=2.3,<4" \\
    "scikit-learn>=1.8,<2"

# Specialized libraries the AutoDS prescribed-knowledge layer declares as
# pre-installed. Python is pinned to 3.12 because LightAutoML does not build
# on 3.13. Present for the AutoDS arm only; see runs/autods-tabred/README.md.
RUN pip install --no-cache-dir \\
    setuptools \\
    lightautoml \\
    featuretools \\
    feature-engine

COPY data/ /app/data/

CMD ["bash"]
"""

def main() -> int:
    revert = "--revert" in sys.argv
    n = 0
    for task in sorted(p for p in TASKS.iterdir() if p.is_dir()):
        df, plain = task / "environment/Dockerfile", task / "environment/Dockerfile.plain"
        if revert:
            if plain.is_file():
                df.write_text(plain.read_text()); plain.unlink(); n += 1
            continue
        if not plain.is_file():
            plain.write_text(df.read_text())
        if df.read_text() != NEW:
            df.write_text(NEW); n += 1
    print(("восстановлено" if revert else "обновлено") + f" задач: {n}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
