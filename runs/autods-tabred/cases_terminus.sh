#!/bin/bash
# Terminus-2 на трёх научных кейсах, две ветки: без предписания (cases-plain)
# и с предписанием библиотеки, как опубликовано (cases). Наборы собирает
# make_cases.py. Модель, ключ и прокси приходят из .env через run.sh, как во
# всех прочих прогонах; параллельность та же, что в опыте B на MLAgentBench.
#
#   ./cases_terminus.sh                                  обе ветки, 3 попытки
#   ATTEMPTS=1 ARMS=cases-plain TASKS=openpoly-tg SUFFIX=-smoke ./cases_terminus.sh
set -u
cd "$(dirname "$0")" || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY="${HARBOR_CONCURRENCY:-4}"

ATT="${ATTEMPTS:-3}"
ARMS="${ARMS:-cases-plain cases}"
TASKS="${TASKS-maize-yield fdata-exit openpoly-tg}"
SUFFIX="${SUFFIX:-}"
L="cases-terminus${SUFFIX}.log"
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> "$L"; }
: > "$L"
say "Terminus-2, кейсы: $TASKS; ветки: $ARMS; попыток $ATT; разом $HARBOR_CONCURRENCY"

for arm in $ARMS; do
  [ -d "harbor-tabred-adapter/datasets/$arm" ] || { say "нет набора $arm, сначала make_cases.py"; continue; }
  SEL=(); for t in $TASKS; do SEL+=(-i "$t"); done
  say "ветка $arm: старт"
  TASKSET="datasets/$arm" JOBNAME="terminus-${arm}${SUFFIX}" ATTEMPTS="$ATT" \
    ./run.sh term-set "${SEL[@]}" > "cases-terminus-${arm}${SUFFIX}.out" 2>&1
  rc=$?
  j=$(ls -dt "jobs/terminus-${arm}${SUFFIX}-2"* 2>/dev/null | head -1)
  say "ветка $arm: код $rc, задание $(basename "${j:-нет}")"
  if [ -n "${j:-}" ]; then
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
say "кейсы закончены"
