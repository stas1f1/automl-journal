#!/bin/bash
# Допрогон 07.10.2026: недостающие 2 испытания ячейки «библиотечная половина
# в Terminus-2» (delivery-eta, weather; в августе упали с APIError) и ещё две
# попытки на задачу у AutoDS-Tools на glm-4.7 (в августе одна).  Команды те же,
# что в августе (ktool2.sh, axis_chain.sh), параллельность 4.
# Первый запуск (14:22) шёл рядом с чужим расчётом на 13 из 18 ядер; его задания
# перенесены в jobs-contended/, этот запуск идёт на свободной машине.  Перед
# каждой ячейкой и после неё в лог пишется загрузка: другой нагрузки быть не должно.
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY=4
L=fill_chain.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> $L; }
load(){ say "  загрузка: $(cut -d' ' -f1-3 /proc/loadavg); чужие контейнеры: $(docker ps --format '{{.Names}}' | grep -vc __env-main)"; }
check(){ # job dir, expected trials
  local j=$1 want=$2
  say "  задание ${j:-нет}: наград $(find "$j" -name reward.json 2>/dev/null | wc -l)/$want, APIError $(grep -l -s APIError "$j"/*/result.json | wc -l), таймаутов $(grep -l -s AgentTimeoutError "$j"/*/result.json | wc -l), слой применён $(grep -l -s 'AutoDS C1 layer applied' "$j"/*/trial.log | wc -l)"
}
say "=== допрогон, слой: $(./run.sh verify 2>/dev/null | grep -m1 sha)"

say "--- Terminus-2, библиотечная половина: delivery-eta, weather"; load
TASKSET=datasets/tabred-ktool JOBNAME=terminus-ktool2-fill ATTEMPTS=1 \
  ./run.sh term-set -i delivery-eta -i weather > fill-ktool.log 2>&1
say "  код $?"; load; check "$(ls -dt jobs/terminus-ktool2-fill-2* 2>/dev/null | head -1)" 2

for pass in 2 3; do
  say "--- AutoDS-Tools, glm-4.7, попытка $pass из 3"; load
  AUTODS_MODEL=z-ai/glm-4.7 TERMINUS_MODEL=openrouter/z-ai/glm-4.7 MODEL_SLUG=large \
    AUTODS_PRICE_INPUT_PER_1M=0.40 AUTODS_PRICE_OUTPUT_PER_1M=1.75 \
    ./run.sh axis-autods-1 > "fill-Mlarge-$pass.log" 2>&1
  say "  код $?"; load; check "$(ls -dt jobs/autods-tabred-Mlarge-2* 2>/dev/null | head -1)" 8
done
say "=== допрогон закончен"
