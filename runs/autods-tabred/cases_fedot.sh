#!/bin/bash
# FEDOT.LLM на двух табличных кейсах, текст без раздела о библиотеке
# (cases-fedot-plain): предписание инструмента у него зашито, раздел он
# выполнить не может, поэтому второй текст для него не условие. Набор
# cases-fedot с полным текстом остаётся для проверки. Агент fedot_harbor должен стоять в venv инструмента harbor:
#   uv pip install --python "$(uv tool dir)/harbor/bin/python" ./fedot_harbor
# Ключ, модель и прокси берутся из .env в корне репозитория, как в run.sh.
#
#   ./cases_fedot.sh                                              3 попытки на кейс
#   ATTEMPTS=1 ARMS=cases-fedot-plain TASKS=fdata-exit SUFFIX=-smoke ./cases_fedot.sh
set -u
cd "$(dirname "$0")" || exit 1
export PATH="$HOME/.local/bin:$PATH"
CONC="${HARBOR_CONCURRENCY:-4}"
for cand in env.local ../../.env; do
  [ -s "$cand" ] && { set -a; . "$cand"; set +a; break; }
done
: "${AUTODS_API_KEY:?нет AUTODS_API_KEY в .env}"
export FEDOTLLM_LLM_API_KEY="${FEDOTLLM_LLM_API_KEY:-$AUTODS_API_KEY}"
MODEL="${FEDOT_MODEL:-openrouter/${AUTODS_MODEL:?задайте AUTODS_MODEL}}"

ATT="${ATTEMPTS:-3}"
ARMS="${ARMS:-cases-fedot-plain}"
TASKS="${TASKS-maize-yield fdata-exit}"
SUFFIX="${SUFFIX:-}"
L="cases-fedot${SUFFIX}.log"
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> "$L"; }
: > "$L"
say "FEDOT.LLM ($MODEL), кейсы: $TASKS; ветки: $ARMS; попыток $ATT; разом $CONC"

for arm in $ARMS; do
  [ -d "harbor-tabred-adapter/datasets/$arm" ] || { say "нет набора $arm, сначала make_cases.py --fedot-src"; continue; }
  SEL=(); for t in $TASKS; do SEL+=(-i "$t"); done
  name="fedot-${arm#cases-fedot}${SUFFIX}-$(date +%Y%m%d-%H%M%S)"; name="${name/fedot--/fedot-}"
  say "ветка $arm: старт, задание $name"
  ( cd harbor-tabred-adapter && harbor run \
      -p "datasets/$arm" \
      -a fedot_harbor.agent:FedotLLMAgent \
      -m "$MODEL" \
      --job-name "$name" \
      -o ../jobs \
      -k "$ATT" \
      -n "$CONC" \
      "${SEL[@]}" ) > "cases-fedot-${arm}${SUFFIX}.out" 2>&1
  rc=$?
  j="jobs/$name"
  say "ветка $arm: код $rc"
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
done
say "FEDOT.LLM на кейсах закончен"
