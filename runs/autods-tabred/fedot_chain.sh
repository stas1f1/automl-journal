#!/bin/bash
# Цепочка FEDOT.LLM на TabReD с 40-минутным бюджетом (task_fedot_tabred_40min.md):
#
#   1. дождаться конца пробы (tabred-fedot-smoke.log) и проверить, что каждый её
#      трайл дошёл до награды с метрикой: иначе основной прогон сгорел бы целиком;
#   2. основная ветка: 8 задач × 3 попытки, общие 16 ГБ и 8 ядер, как у
#      Terminus-2 и AutoDS-Tools. Параллель 2, а не 4: FEDOT держит процессор
#      (лес начального конвейера на 8 потоках), и 4 × 8 = 32 потока на 18 ядрах
#      сервера удвоили бы обучение и увели регрессии в таймаут. При 2 × 8 каждый
#      трайл получает заявленные в task.toml 8 ядер, как в пробе;
#   3. ветка 64 ГБ: задачи основной ветки, где хоть одна попытка убита по памяти
#      (код 137), ещё раз по 3 попытки по одной за раз, в наборе tabred-fedot-mem64.
#      Отдельное отклонение: FEDOT на матрицах 1.6 ГБ не помещается в 16 ГБ даже
#      при n_jobs=1 (проба 21.09).
#
#   nohup ./fedot_chain.sh > /dev/null 2>&1 &
set -u
cd "$(dirname "$0")" || exit 1
# Конфигурация FEDOT.LLM для всех веток.
#  - Отложенная выборка: 5-фолдовая оценка начального конвейера шла 48 минут мимо
#    бюджета FEDOT (проба 21.09, weather).
#  - Бюджет 1200 с: FEDOT тратит бюджет, плюс одну оценку сверх него, плюс
#    финальное обучение, равное начальному (10-15 мин на этих таблицах). При
#    1800 с cooking-time не успел финальное обучение на 2 минуты (проба 22.09),
#    weather закончил за 57.7 из 60 минут.
#  - Тюнинг, поиск и пресет best_quality включены; потоки моделей 8 в образе.
export FEDOTLLM_TIME_LIMIT=1200 FEDOTLLM_CV_FOLDS=none
L=fedot-chain.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> "$L"; }
: > "$L"

if [ "${SKIP_SMOKE:-0}" = 1 ]; then
  say "проба пропущена (SKIP_SMOKE=1): weather прошёл в jobs/fedot-tabred-40min-smoke-20260922-010033"
else
say "жду конца пробы"
until grep -q "закончен\|не запускаю" tabred-fedot-smoke.log 2>/dev/null; do sleep 60; done
smoke=$(ls -dt jobs/fedot-tabred-40min-smoke-2* | head -1)
ok=1; n=0
for t in "$smoke"/*/; do
  [ -d "$t" ] || continue; n=$((n+1))
  r="$t/verifier/reward.json"
  if [ -f "$r" ] && grep -q '"rmse"\|"roc_auc"' "$r"; then
    say "проба $(basename "$t"): $(tr -d '\n ' < "$r")"
  else
    say "проба $(basename "$t") без метрики"; ok=0
  fi
done
if [ "$ok" = 0 ] || [ "$n" = 0 ]; then
  say "проба не прошла ($smoke), основной прогон не запускаю"; exit 1
fi
fi

say "основная ветка: 8 задач × 3, параллель 2, 16 ГБ"
ATTEMPTS=3 HARBOR_CONCURRENCY=2 SUFFIX="" DATASET=tabred-fedot ./tabred_fedot.sh
main=$(ls -dt jobs/fedot-tabred-40min-2* | head -1)
say "основная ветка закончена: $main"

oom=$(grep -l "exit 137" "$main"/*/exception.txt 2>/dev/null \
      | xargs -r -n1 dirname | xargs -r -n1 basename | sed 's/__.*//' | sort -u | tr '\n' ' ')
if [ -z "${oom// }" ]; then
  say "убитых по памяти нет, ветка 64 ГБ не нужна"
else
  say "убиты по памяти в основной ветке: $oom"
  python3 make_tabred_fedot.py --memory-mb 65536 $oom >> "$L" 2>&1
  say "ветка 64 ГБ: $oom × 3, по одной"
  ATTEMPTS=3 HARBOR_CONCURRENCY=1 SUFFIX=-mem64 DATASET=tabred-fedot-mem64 TASKS="$oom" ./tabred_fedot.sh
  say "ветка 64 ГБ закончена: $(ls -dt jobs/fedot-tabred-40min-mem64-* | head -1)"
fi
say "цепочка закончена"
