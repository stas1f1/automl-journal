#!/usr/bin/env python3
"""Collect AutoDS TabReD metrics from Harbor job artefacts.

Usage:
    python3 collect.py [jobs_dir] [--only=SUBSTRING]
        jobs_dir   default ./jobs
        --only=    keep only jobs whose directory name contains SUBSTRING,
                   e.g. --only=full to exclude the smoke job

Walks every trial, reads the verifier reward payload, and prints
  1. a per-trial table,
  2. the per-task mean across attempts,
  3. a ready-to-paste dict for paper/make_tables.py.

Raw metrics live in <trial>/verifier/reward.json.  For this adapter the reward
is ROC-AUC for classification and 1/(1+RMSE) for regression, with the raw
metric preserved alongside -- we always take the raw metric, never the reward.
"""
from __future__ import annotations

import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

# Task order used by paper/make_tables.py -- keep in sync.
TASK_ORDER = ["homesite-insurance", "ecom-offers", "homecredit-default",
              "sberbank-housing", "cooking-time", "delivery-eta",
              "maps-routing", "weather"]
CLASSIFICATION = {"homesite-insurance", "ecom-offers", "homecredit-default"}

METRIC_KEYS = ("roc_auc", "rocauc", "auc", "rmse", "root_mean_squared_error")


def find_reward(trial: Path) -> dict | None:
    for cand in (trial / "verifier" / "reward.json",
                 trial / "verifier" / "results.json",
                 trial / "reward.json"):
        if cand.is_file():
            try:
                return json.loads(cand.read_text())
            except json.JSONDecodeError:
                return None
    return None


def extract(payload: dict, task: str) -> tuple[str, float] | None:
    """Pull the raw benchmark metric, ignoring the derived reward."""
    flat: dict[str, float] = {}

    def walk(d, prefix=""):
        for k, v in (d or {}).items():
            if isinstance(v, dict):
                walk(v, f"{prefix}{k}.")
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                flat[f"{prefix}{k}".lower()] = float(v)

    walk(payload)
    want = ("roc_auc", "rocauc", "auc") if task in CLASSIFICATION else ("rmse",)
    for key in flat:
        base = key.rsplit(".", 1)[-1]
        if base in want:
            return base, flat[key]
    # Fall back: derive RMSE from the reward if only that survived.
    for key in ("reward", "score"):
        if key in flat and task not in CLASSIFICATION and flat[key] > 0:
            return "rmse (derived from reward)", 1.0 / flat[key] - 1.0
    return None


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--only=")), None)
    jobs = Path(args[0] if args else "jobs")
    if not jobs.is_dir():
        print(f"нет каталога {jobs}", file=sys.stderr)
        return 1

    per_task: dict[str, list[float]] = defaultdict(list)
    rows: list[tuple[str, str, str, str, float]] = []
    failed: list[tuple[str, str]] = []   # trials with no submission at all

    for job in sorted(p for p in jobs.iterdir() if p.is_dir()):
        if only and only not in job.name:
            continue
        for trial in sorted(p for p in job.iterdir() if p.is_dir()):
            payload = find_reward(trial)
            if payload is None:
                rows.append((job.name, trial.name, "—", "нет reward.json", float("nan")))
                continue
            task = next((t for t in TASK_ORDER if trial.name.startswith(t)), trial.name)
            got = extract(payload, task)
            if got is None:
                why = "нет метрики"
                stdout = trial / "verifier" / "test-stdout.txt"
                if stdout.is_file() and "Missing required file" in stdout.read_text():
                    why = "СБОЙ: нет predictions.csv"
                    failed.append((task, trial.name))
                rows.append((job.name, trial.name, task, why, float("nan")))
                continue
            metric, value = got
            rows.append((job.name, trial.name, task, metric, value))
            per_task[task].append(value)

    if not rows:
        print("испытаний не найдено")
        return 1

    print(f"{'job':<22}{'trial':<30}{'задача':<20}{'метрика':<12}{'значение':>12}")
    for j, tr, task, m, v in rows:
        sv = "—" if v != v else f"{v:.6f}"
        print(f"{j[-21:]:<22}{tr[:29]:<30}{task:<20}{m[:11]:<12}{sv:>12}")

    print(f"\n{'задача':<20}{'n':>3}{'среднее':>12}{'ст.откл.':>12}")
    for t in TASK_ORDER:
        vs = per_task.get(t, [])
        if not vs:
            print(f"{t:<20}{0:>3}{'—':>12}{'—':>12}")
            continue
        sd = st.stdev(vs) if len(vs) > 1 else 0.0
        print(f"{t:<20}{len(vs):>3}{st.mean(vs):>12.6f}{sd:>12.6f}")

    if failed:
        print(f"\nИСКЛЮЧЕНО ИЗ СРЕДНИХ: {len(failed)} испытаний без сабмита.")
        for task, name in failed:
            print(f"  {task:<20}{name}")
        print("Такое испытание не является результатом моделирования: агент не успел\n"
              "дописать predictions.csv до жёсткого таймаута задачи (timeout_sec в\n"
              "task.toml). Усреднять его как ноль значило бы выдать отказ инфраструктуры\n"
              "за качество модели.")

    missing = [t for t in TASK_ORDER if not per_task.get(t)]

    if "--attempts" in sys.argv:
        print("\n# --- вставить в AUTODS_ATTEMPTS в paper/make_tables.py ---")
        print("AUTODS_ATTEMPTS = {")
        for t in TASK_ORDER:
            vs = per_task.get(t)
            if vs:
                print(f'    "{t}":{" " * max(1, 21 - len(t))}'
                      f'[{", ".join(repr(v) for v in vs)}],')
        print("}")

    print("\n# --- вставить в AGENTS в paper/make_tables.py ---")
    vals = ", ".join(f"{st.mean(per_task[t]):.6f}" if per_task.get(t) else "None"
                     for t in TASK_ORDER)
    print(f'    "AutoDS-Tools": [{vals}],')
    if missing:
        print(f"# ВНИМАНИЕ: нет данных по задачам: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
