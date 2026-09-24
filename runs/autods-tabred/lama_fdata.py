"""Повтор решения AutoDS-Tools на F-DATA (17.07) с подробным логом LightAutoML (22.09).

Июльская трасса не сохранила ни кода, ни вывода, поэтому по ней не видно,
подбирал ли LightAutoML гиперпараметры. Здесь тот же код из раздела задания
(TabularAutoML(task=Task("binary")) с настройками по умолчанию), тот же порядок,
что описал агент: проверка на разбиении 80/20, затем обучение на всём train.csv,
порог 0.5. verbose=2 выводит состав моделей, подбор Optuna и время.

    docker run --rm --cpus 4 -m 16g -v $PWD:/probe:ro cases-fdata \
        python /probe/lama_fdata.py
"""
import time

import lightautoml
import pandas as pd
from lightautoml.automl.presets.tabular_presets import TabularAutoML
from lightautoml.tasks import Task
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.model_selection import train_test_split

print("lightautoml", getattr(lightautoml, "__version__", "?"), flush=True)
train = pd.read_csv("/workspace/train.csv")
test = pd.read_csv("/workspace/test.csv")
answer = pd.read_csv("/opt/mlab/answer.csv")
print("train", train.shape, "test", test.shape, flush=True)
roles = {"target": "success", "drop": ["jobid"]}

t0 = time.time()
tr, va = train_test_split(train, test_size=0.2, random_state=42, stratify=train["success"])
automl = TabularAutoML(task=Task("binary"))
automl.fit_predict(tr, roles=roles, verbose=2)
p = automl.predict(va).data[:, 0]
print(f"=== holdout: accuracy {accuracy_score(va['success'], p >= 0.5):.4f}, "
      f"{time.time() - t0:.0f} s", flush=True)
print(automl.create_model_str_desc(), flush=True)

t1 = time.time()
automl = TabularAutoML(task=Task("binary"))
automl.fit_predict(train, roles=roles, verbose=2)
proba = automl.predict(test).data[:, 0]
sub = pd.DataFrame({"jobid": test["jobid"], "success": (proba >= 0.5).astype(int)})
m = answer.merge(sub, on="jobid", suffixes=("", "_pred"))
print(f"=== full fit {time.time() - t1:.0f} s; test accuracy "
      f"{accuracy_score(m['success'], m['success_pred']):.4f}, balanced "
      f"{balanced_accuracy_score(m['success'], m['success_pred']):.4f}, n={len(m)}", flush=True)
print(automl.create_model_str_desc(), flush=True)
print(f"=== total {time.time() - t0:.0f} s", flush=True)
