#!/bin/bash
# FEDOT.LLM на двух самых широких задачах TabReD с максимумом ресурсов сервера
# (22.09). Настройки FEDOT те же, что на остальных шести задачах: бюджет 1200 с,
# отложенная выборка, best_quality, тюнинг, 8 потоков моделей. Меняются только
# ресурсы: память 84 ГБ (из 94 на сервере) и потолок агента 3 часа.
#
# Почему: корректор типов FEDOT объявляет категориальными 148 столбцов
# homecredit-default (в TabReD их 82) и 92 столбца maps-routing (в TabReD 2),
# переводит матрицу в dtype object и раздувает её с 1.6-1.7 ГБ до 17 ГБ ещё до
# обучения (fedot_prep_probe.py). При 64 ГБ и часе обе задачи не закончили
# начальный конвейер. Прогоны FEDOT детерминированы, поэтому одна попытка на
# задачу; повторы, если хватит времени.
#
#   nohup ./fedot_long.sh > /dev/null 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")" || exit 1
L=fedot-chain.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> "$L"; }
export FEDOTLLM_TIME_LIMIT=1200 FEDOTLLM_CV_FOLDS=none

say "длинные прогоны: жду конца ветки 64 ГБ (homesite-insurance)"
until grep -q "ветка 64 ГБ закончена" "$L"; do sleep 60; done
python3 make_tabred_fedot.py --memory-mb 86016 --agent-timeout 10800 homecredit-default maps-routing >> "$L" 2>&1
for t in homecredit-default maps-routing; do
  say "длинный прогон: $t × 1, 84 ГБ, потолок 3 ч"
  ATTEMPTS=1 HARBOR_CONCURRENCY=1 SUFFIX="-mem84-long-$t" DATASET=tabred-fedot-mem84-t3h TASKS="$t" ./tabred_fedot.sh
  say "длинный прогон $t закончен: $(ls -dt jobs/fedot-tabred-40min-mem84-long-$t-* | head -1)"
done
say "длинные прогоны закончены"
say "цепочка закончена"
