#!/bin/bash
# Сокращение ветки 64 ГБ (22.09). homecredit-default упал по памяти и при 64 ГБ
# через 52.6 мин, не закончив начальный конвейер; maps-routing на 18-й минуте
# занимал 56.6 ГБ, тоже без начального конвейера. Прогоны FEDOT при этих
# настройках повторяются побитно, поэтому ещё по две попытки на этих задачах
# ничего не добавят и стоят около 4 часов. Скрипт ждёт конца текущей попытки
# maps-routing, останавливает задание и прогоняет homesite-insurance × 3 при
# 64 ГБ, где при 16 ГБ трайл жил 15.6 мин.
#
#   nohup ./fedot_mem64_trim.sh > /dev/null 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")" || exit 1
L=fedot-chain.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> "$L"; }
export FEDOTLLM_TIME_LIMIT=1200 FEDOTLLM_CV_FOLDS=none

job=$(ls -dt jobs/fedot-tabred-40min-mem64-2* | head -1)
say "сокращение ветки 64 ГБ: жду конца текущей попытки maps-routing в $job"
until ls "$job"/maps-routing__*/result.json >/dev/null 2>&1; do sleep 30; done
say "попытка maps-routing закончена, останавливаю задание"

for p in $(pgrep -x fedot_chain.sh); do kill "$p"; done
for p in $(pgrep -x tabred_fedot.sh); do kill "$p"; done
for p in $(pgrep -f "harbor run -p datasets/tabred-fedot-mem64"); do
  [ "$p" = "$$" ] || kill -INT "$p"
done
for i in $(seq 1 18); do
  pgrep -f "harbor run -p datasets/tabred-fedot-mem64" >/dev/null || break
  sleep 10
done
for p in $(pgrep -f "harbor run -p datasets/tabred-fedot-mem64"); do kill -TERM "$p"; done
sleep 15
say "задание остановлено; начатые после maps-routing трайлы без результата не считаются"

say "ветка 64 ГБ, продолжение: homesite-insurance × 3, по одной"
ATTEMPTS=3 HARBOR_CONCURRENCY=1 SUFFIX=-mem64b DATASET=tabred-fedot-mem64 TASKS=homesite-insurance ./tabred_fedot.sh
say "ветка 64 ГБ закончена: $(ls -dt jobs/fedot-tabred-40min-mem64b-* | head -1)"
say "цепочка закончена"
