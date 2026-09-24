#!/bin/bash
# Пересчёт двух задач, которые в опыте A утонули в нехватке ядер.
#
# cifar10 и imdb — самые тяжёлые по счёту задачи набора (свёрточная сеть на
# пятидесяти тысячах картинок; дообучение трансформера на двадцати пяти тысячах
# отзывов), и при этом бенчмарк даёт им час, а не два. При четырёх испытаниях
# разом час настенного времени — это около двадцати минут процессорного, и все
# шесть испытаний в опыте A упёрлись в потолок с нулём. Три из трёх в каждой
# задаче — это систематика, а не разброс.
#
# Поэтому здесь по два испытания разом, а не по четыре. Условия отличаются от
# остальных восьми задач, и это придётся оговорить, но лучше оговорённое число,
# чем ноль, который меряет загрузку машины, а не систему.
set -u
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY="${HARBOR_CONCURRENCY:-2}"
export WORKSPACE=/workspace
ATT="${ATTEMPTS:-3}"
L=mlab-heavy.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> "$L"; }
: > "$L"
say "cifar10 и imdb заново, попыток на задачу $ATT, разом $HARBOR_CONCURRENCY"

branch(){  # branch <ярлык> <набор задач>
  local tag="$1" set="$2" name="autods-mlab-$1-heavy"
  say "=== ветка $tag, набор $set"
  TASKSET="$set" JOBNAME="$name" ATTEMPTS="$ATT" \
    ./run.sh autods-set -i cifar10 -i imdb > "mlab-heavy-$tag.out" 2>&1
  local rc=$? j; j=$(ls -dt jobs/$name-2* 2>/dev/null | head -1)
  say "  код $rc, задание $(basename "${j:-нет}")"
  [ -n "${j:-}" ] || { say "  задание не создалось"; return; }
  for r in "$j"/*/verifier/reward.json; do
    [ -f "$r" ] && say "  $(basename "$(dirname "$(dirname "$r")")") -> $(tr -d '\n ' < "$r" | head -c 100)"
  done
  say "  исчерпали бюджет: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -l AgentTimeoutError | wc -l)"
}

branch nolayer datasets/mlab
branch c1      datasets/mlab-c1
say "пересчёт тяжёлых закончен"
