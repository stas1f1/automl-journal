#!/bin/bash
# Опыт A: AutoDS-Tools на всех десяти задачах MLAgentBench, две ветки.
#
#   без слоя  — задание как в бенчмарке (datasets/mlab)
#   со слоем  — заданием подан опубликованный instruction_c1.md (datasets/mlab-c1)
#
# Сборщик слоя погашен в обеих ветках (это делает сам run.sh): иначе поверх
# опубликованного текста лёг бы ещё и сегодняшний, а они разошлись.
#
# Зачем три попытки. На одной задаче этого бенчмарка три одинаковые попытки
# Terminus дали 0.1144, 0.3303 и 0.5569 — разброс впятеро. Одиночные прогоны
# здесь не измеряют ничего, поэтому в каждой ячейке по три испытания.
#
# Параллельность. У задач не объявлено ограничение по ядрам, значит каждый
# контейнер видит все 18 и torch забивает их целиком. При четырёх испытаниях
# разом на каждое приходится вчетверо меньше, чем при одном; самое долгое
# наблюдавшееся испытание шло 42 минуты при двух разом, потолок задачи — два
# часа, так что четыре — это запас примерно вдвое. Число одно и то же в обеих
# ветках: иначе ветки различались бы не только слоем.
set -u
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY="${HARBOR_CONCURRENCY:-4}"
export WORKSPACE=/workspace

SMOKE="${SMOKE:-}"
if [ -n "$SMOKE" ]; then
  ATT=1; SEL=(-i house-price); TAG=smoke; L=mlab-autods-smoke.log
else
  ATT="${ATTEMPTS:-3}"; SEL=(); TAG=full; L=mlab-autods.log
fi

say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> "$L"; }
: > "$L"
say "ветки: без слоя и с опубликованным слоем; попыток на задачу $ATT; разом $HARBOR_CONCURRENCY"

branch(){  # branch <ярлык> <набор задач>
  local tag="$1" set="$2" name="autods-mlab-$1-$TAG"
  say "=== ветка $tag, набор $set"
  TASKSET="$set" JOBNAME="$name" ATTEMPTS="$ATT" \
    ./run.sh autods-set "${SEL[@]}" > "mlab-autods-$tag-$TAG.out" 2>&1
  local rc=$? j; j=$(ls -dt jobs/$name-2* 2>/dev/null | head -1)
  say "  код $rc, задание $(basename "${j:-нет}")"
  [ -n "${j:-}" ] || { say "  задание не создалось"; return; }
  local n=0
  for r in "$j"/*/verifier/reward.json; do
    [ -f "$r" ] || continue
    n=$((n+1))
    say "  $(basename "$(dirname "$(dirname "$r")")") -> $(tr -d '\n ' < "$r" | head -c 120)"
  done
  say "  испытаний с наградой: $n"
  say "  таймаутов: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -l AgentTimeoutError | wc -l), прочих исключений: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -L AgentTimeoutError | wc -l)"
  if [ "$rc" -ne 0 ]; then say "  ПОСЛЕДНИЕ СТРОКИ: $(tail -5 "mlab-autods-$tag-$TAG.out" | tr '\n' ' ' | head -c 400)"; fi
}

branch nolayer datasets/mlab
branch c1      datasets/mlab-c1
say "опыт A закончен"
