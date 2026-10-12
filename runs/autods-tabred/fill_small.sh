#!/bin/bash
# Перезапуск 12.10.2026: один запуск ячейки Terminus-2 на gemma-4-26b-a4b-it
# (delivery-eta), в августе упал с APIError до первого ответа модели и входил
# в шесть запусков без результата.  Команда и окружение те же, что в
# axis_chain.sh (ячейка small, axis-terminus), параллельность 4.
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY=4
L=fill_small.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> $L; }
load(){ say "  загрузка: $(cut -d' ' -f1-3 /proc/loadavg); чужие контейнеры: $(docker ps --format '{{.Names}}' | grep -vc __env-main)"; }
say "=== перезапуск delivery-eta, Terminus-2, gemma-4-26b-a4b-it"; load
AUTODS_MODEL=google/gemma-4-26b-a4b-it TERMINUS_MODEL=openrouter/google/gemma-4-26b-a4b-it MODEL_SLUG=small \
  AUTODS_PRICE_INPUT_PER_1M=0.07 AUTODS_PRICE_OUTPUT_PER_1M=0.34 \
  JOBNAME=terminus-tabred-Msmall-fill ATTEMPTS=1 \
  ./run.sh term-set -i delivery-eta > fill-small.log 2>&1
say "  код $?"; load
j=$(ls -dt jobs/terminus-tabred-Msmall-fill-2* 2>/dev/null | head -1)
say "  задание ${j:-нет}: наград $(find "$j" -name reward.json 2>/dev/null | wc -l)/1, APIError $(grep -l -s APIError "$j"/*/result.json | wc -l)"
say "=== закончено"
