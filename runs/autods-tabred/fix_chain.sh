#!/bin/bash
# Перезапуск 07.10.2026 после правки glob_search в адаптере AutoDS-Tools
# (агент в контейнере больше не падает на абсолютном шаблоне).  Заменяет шесть
# запусков допрогона glm-4.7 (fill_chain.sh): четыре упали на glob_search
# (cooking-time ×2, homecredit-default, sberbank-housing), два не стартовали из-за
# таймаута установки агента (ecom-offers, homecredit-default).  Та же команда,
# параллельность 4.
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY=4
L=fix_chain.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> $L; }
load(){ say "  загрузка: $(cut -d' ' -f1-3 /proc/loadavg); чужие контейнеры: $(docker ps --format '{{.Names}}' | grep -vc __env-main)"; }
check(){ # job dir, expected trials
  local j=$1 want=$2
  say "  задание ${j:-нет}: наград $(find "$j" -name reward.json 2>/dev/null | wc -l)/$want, APIError $(grep -l -s APIError "$j"/*/result.json | wc -l), таймаутов $(grep -l -s AgentTimeoutError "$j"/*/result.json | wc -l), таймаутов установки $(grep -l -s AgentSetupTimeoutError "$j"/*/result.json | wc -l), падений glob $(grep -l -s 'Non-relative patterns' "$j"/*/agent/autods.log | wc -l), правка glob $(grep -l -s 'glob_search patched' "$j"/*/agent/setup/*.txt "$j"/*/trial.log 2>/dev/null | wc -l), слой применён $(grep -l -s 'AutoDS C1 layer applied' "$j"/*/trial.log | wc -l)"
}
say "=== перезапуск, слой: $(./run.sh verify 2>/dev/null | grep -m1 sha)"
glm(){ AUTODS_MODEL=z-ai/glm-4.7 TERMINUS_MODEL=openrouter/z-ai/glm-4.7 MODEL_SLUG=large \
  AUTODS_PRICE_INPUT_PER_1M=0.40 AUTODS_PRICE_OUTPUT_PER_1M=1.75 ./run.sh axis-autods-fix "$@"; }
n=0
for set in "-i cooking-time -i homecredit-default -i sberbank-housing -i ecom-offers" \
           "-i cooking-time -i homecredit-default"; do
  n=$((n+1)); want=$(echo $set | grep -o -- -i | wc -l)
  say "--- AutoDS-Tools, glm-4.7, часть $n: $set"; load
  glm $set > "fix-Mlarge-$n.log" 2>&1
  say "  код $?"; load; check "$(ls -dt jobs/autods-tabred-Mlarge-fix-2* 2>/dev/null | head -1)" $want
done
say "=== перезапуск закончен"
