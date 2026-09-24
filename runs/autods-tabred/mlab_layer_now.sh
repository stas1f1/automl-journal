#!/bin/bash
# Опыт C: чего стоит расхождение двух редакций слоя — в результатах, а не в символах.
#
# В опыте A обработанная ветка получала слой ТОЙ редакции, что выложена вместе с
# задачами, поданный текстом задания. Здесь та же система на тех же задачах
# получает слой, который наш сборщик собирает СЕГОДНЯ, из склонированной ветки.
#
# Тексты различаются: общий блок дисциплины короче на 113 символов, блок для
# графов длиннее на 668. И различие содержательное — в сегодняшней редакции
# стоят две подсказки под конкретные задачи бенчмарка (про максимальный штраф
# SMAPE на нулевой цели и про маскирование недостижимых кандидатов для
# указателей), а в выложенной они заменены общим запретом константной посылки.
#
# cifar10 и imdb исключены: без ускорителя не воспроизводятся.
# Условия те же, что в A и B: четыре испытания разом, три попытки на задачу.
set -u
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY="${HARBOR_CONCURRENCY:-4}"
export WORKSPACE=/workspace
export TASKSET=datasets/mlab

ATT="${ATTEMPTS:-3}"
NAME="autods-mlab-layernow"
TASKS="${TASKS-amp-parkinsons clrs fathomnet feedback house-price identify-contrails ogbn-arxiv spaceship-titanic}"
SEL=(); for t in $TASKS; do SEL+=(-i "$t"); done
L=mlab-layernow.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> "$L"; }
: > "$L"
say "AutoDS, слой сегодняшней редакции, задач $(echo $TASKS | wc -w), попыток $ATT, разом $HARBOR_CONCURRENCY"
say "задачи: $TASKS"

JOBNAME="$NAME" ATTEMPTS="$ATT" ./run.sh autods-set-layer "${SEL[@]}" > mlab-layernow.out 2>&1
rc=$?
j=$(ls -dt jobs/$NAME-2* 2>/dev/null | head -1)
say "код $rc, задание $(basename "${j:-нет}")"
if [ -n "${j:-}" ]; then
  # проверка, что слой действительно применился: без этой строки прогон
  # ничем не отличается от ветки «без слоя» и мерил бы не то
  say "слой применён в испытаниях: $(grep -l 'C1 layer applied' "$j"/*/trial.log 2>/dev/null | wc -l) из $(ls -d "$j"/*/ 2>/dev/null | wc -l)"
  for r in "$j"/*/verifier/reward.json; do
    [ -f "$r" ] && say "  $(basename "$(dirname "$(dirname "$r")")") -> $(tr -d '\n ' < "$r" | head -c 110)"
  done
  say "исчерпали бюджет: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -l AgentTimeoutError | wc -l), прочих исключений: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -L AgentTimeoutError | wc -l)"
fi
say "опыт C закончен"
