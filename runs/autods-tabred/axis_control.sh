#!/bin/bash
# контроль: AutoDS тем же путём оси, но на модели, на которой он заведомо работает.
# Если и он упрётся в потолок -- виноват путь запуска, а не модели.
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY=1
L=axis_smoke.log
say(){ echo "[$(date +%H:%M:%S)] $*" >> $L; }
say "=== КОНТРОЛЬ: axis-autods-smoke / google/gemma-4-31b-it"
AUTODS_MODEL=google/gemma-4-31b-it TERMINUS_MODEL=openrouter/google/gemma-4-31b-it \
  MODEL_SLUG=ctl AUTODS_PRICE_INPUT_PER_1M=0.09 AUTODS_PRICE_OUTPUT_PER_1M=0.34 \
  ./run.sh axis-autods-smoke > smoke-ctl-axis-autods-smoke.log 2>&1
rc=$?; j=$(ls -dt jobs/*Mctl-smoke-* 2>/dev/null | head -1)
say "КОНТРОЛЬ код $rc; награда: $(cat $j/*/verifier/reward.json 2>/dev/null | tr -d '\n ' | head -c 120)"
say "контроль закончен"
