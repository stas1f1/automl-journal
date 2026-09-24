#!/bin/bash
# Ось бэкбона: пять полных проходов TabReD.
# Параллельность 4 во всех ячейках -- она входит в измерение времени испытания
# и должна совпадать с ячейкой, против которой ось читается.
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY=4
# ключ нужен самому скрипту для замера баланса; run.sh читает .env отдельно
set -a; . ../../.env; set +a
L=axis_chain.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> $L; }
say "ось бэкбона: пять проходов, параллельность $HARBOR_CONCURRENCY"

cell(){ # slug model pin pout mode
  local slug=$1 model=$2 pin=$3 pout=$4 mode=$5
  say "=== $mode / $model"
  AUTODS_MODEL="$model" TERMINUS_MODEL="openrouter/$model" MODEL_SLUG="$slug" \
    AUTODS_PRICE_INPUT_PER_1M="$pin" AUTODS_PRICE_OUTPUT_PER_1M="$pout" \
    ./run.sh "$mode" > "axis-$slug-$mode.log" 2>&1
  local rc=$? j n
  j=$(ls -dt jobs/*M$slug-2* 2>/dev/null | head -1)
  n=$(find "$j" -name reward.json 2>/dev/null | wc -l)
  local want=24; [ "$mode" = axis-autods-1 ] && want=8
  say "$mode/$slug: код $rc, задание ${j:-нет}, наград $n/$want"
  # прерываем цепочку только на настоящем отказе, а не на отдельных таймаутах
  if [ "$rc" -ne 0 ] && [ "$n" -lt $((want / 2)) ]; then say "ПРЕРВАНО на $mode/$slug"; return 1; fi
  return 0
}

# сперва Terminus-2: три точки по часу, быстрая обратная связь
cell small google/gemma-4-26b-a4b-it 0.07 0.34 axis-terminus || exit 1
say "баланс ключа до средней ячейки: $(curl -s https://openrouter.ai/api/v1/key -H "Authorization: Bearer $AUTODS_API_KEY" | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['usage'])" 2>/dev/null)"
cell mid   google/gemma-4-31b-it 0.09 0.34 axis-terminus || exit 1
say "баланс ключа после средней ячейки: $(curl -s https://openrouter.ai/api/v1/key -H "Authorization: Bearer $AUTODS_API_KEY" | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['usage'])" 2>/dev/null)"
cell large z-ai/glm-4.7          0.40 1.75 axis-terminus || exit 1
# затем AutoDS: две точки по несколько часов; средняя точка уже измерена
cell small google/gemma-4-26b-a4b-it 0.07 0.34 axis-autods   || exit 1
# верхняя точка AutoDS: одна попытка на задачу, не три. Проба показала, что
# ячейка упирается в потолок; три попытки утроили бы стоимость ради того же
# вывода. Восемь испытаний дают утверждение про все задачи, а не про одну.
cell large z-ai/glm-4.7          0.40 1.75 axis-autods-1 || exit 1
say "ось закончена"
