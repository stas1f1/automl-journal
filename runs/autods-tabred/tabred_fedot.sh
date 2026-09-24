#!/bin/bash
# FEDOT.LLM на восьми задачах TabReD с бюджетом бэкенда 40 минут, как на кейсах
# 10 сентября (task_fedot_tabred_40min.md). Набор datasets/tabred-fedot строит
# make_tabred_fedot.py; базовый образ собирается заранее одной командой:
#   docker build -t fedot-tabred-base harbor-tabred-adapter/datasets/tabred-fedot/_base
# Агент fedot_harbor должен стоять в venv инструмента harbor:
#   uv pip install --python "$(uv tool dir)/harbor/bin/python" ./fedot_harbor
# Ключ, модель и прокси берутся из .env в корне репозитория, как в run.sh.
#
#   ./tabred_fedot.sh                                     8 задач, 3 попытки
#   ATTEMPTS=1 TASKS=weather SUFFIX=-smoke ./tabred_fedot.sh
set -u
cd "$(dirname "$0")" || exit 1
export PATH="$HOME/.local/bin:$PATH"
CONC="${HARBOR_CONCURRENCY:-4}"
for cand in env.local ../../.env; do
  [ -s "$cand" ] && { set -a; . "$cand"; set +a; break; }
done
: "${AUTODS_API_KEY:?нет AUTODS_API_KEY в .env}"
export FEDOTLLM_LLM_API_KEY="${FEDOTLLM_LLM_API_KEY:-$AUTODS_API_KEY}"
export FEDOTLLM_TIME_LIMIT="${FEDOTLLM_TIME_LIMIT:-2400}"
MODEL="${FEDOT_MODEL:-openrouter/${AUTODS_MODEL:?задайте AUTODS_MODEL}}"

ATT="${ATTEMPTS:-3}"
TASKS="${TASKS-}"
SUFFIX="${SUFFIX:-}"
DATASET="${DATASET:-tabred-fedot}"   # tabred-fedot-mem64: вариант с лимитом 64 ГБ
L="tabred-fedot${SUFFIX}.log"
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> "$L"; }
: > "$L"

docker image inspect fedot-tabred-base >/dev/null 2>&1 \
  || { say "нет образа fedot-tabred-base, соберите его (см. шапку)"; exit 1; }
[ -d "harbor-tabred-adapter/datasets/$DATASET" ] \
  || { say "нет набора $DATASET, сначала make_tabred_fedot.py"; exit 1; }

# Модель вызывается изнутри контейнера через прокси хоста. Если прокси лежит,
# FEDOT.LLM не падает, а продолжает с проваленным выводом столбцов и сжигает
# трайл (проба 21.09: «Connection error», порт прокси закрыт). Проверяем до
# запуска; адрес прокси в журнал не пишем, в нём учётные данные.
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 \
         ${HTTPS_PROXY:+-x "$HTTPS_PROXY"} https://openrouter.ai/api/v1/models || true)
[ "$code" = "200" ] || { say "OpenRouter через прокси ответил '$code' вместо 200, не запускаю"; exit 1; }

SEL=(); for t in $TASKS; do SEL+=(-i "$t"); done
name="fedot-tabred-40min${SUFFIX}-$(date +%Y%m%d-%H%M%S)"
say "FEDOT.LLM ($MODEL), набор $DATASET, задачи: ${TASKS:-все восемь}; попыток $ATT; разом $CONC; бюджет бэкенда ${FEDOTLLM_TIME_LIMIT} с; n_jobs ${FEDOTLLM_N_JOBS:-по умолчанию снимка}; cv_folds ${FEDOTLLM_CV_FOLDS:-по умолчанию снимка}"
say "задание $name"
( cd harbor-tabred-adapter && harbor run \
    -p "datasets/$DATASET" \
    -a fedot_harbor.agent:FedotLLMTabredAgent \
    -m "$MODEL" \
    --job-name "$name" \
    -o ../jobs \
    -k "$ATT" \
    -n "$CONC" \
    "${SEL[@]}" ) > "tabred-fedot${SUFFIX}.out" 2>&1
rc=$?
j="jobs/$name"
say "код $rc"
if [ -d "$j" ]; then
  n=0
  for r in "$j"/*/verifier/reward.json; do
    [ -f "$r" ] || continue
    n=$((n+1))
    say "  $(basename "$(dirname "$(dirname "$r")")") -> $(tr -d '\n ' < "$r" | head -c 160)"
  done
  say "  испытаний с наградой: $n"
  say "  исчерпали бюджет: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -l AgentTimeoutError | wc -l), прочих исключений: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -L AgentTimeoutError | wc -l)"
fi
say "FEDOT.LLM на TabReD закончен"
