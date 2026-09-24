#!/bin/bash
# Опыт B: Terminus-2 на всех десяти задачах MLAgentBench, по три попытки.
#
# Зачем. Сейчас строка Terminus в таблице покрытия собрана из двух разных
# прогонов: шесть задач сняты коллегой по одной попытке, четыре добраны нами
# уже с другой перемычкой проверяющего. Сравнивать такое между собой нельзя.
# Тридцать испытаний одним заданием делают строку однородной.
#
# Ветка одна: своего слоя предписанного знания у Terminus нет, задание он
# получает как есть.
#
# Параллельность та же, что в опыте A, — иначе две системы окажутся снятыми
# в разных условиях, и разницу между ними нельзя будет отнести к архитектуре.
set -u
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY="${HARBOR_CONCURRENCY:-4}"
export TASKSET=datasets/mlab

ATT="${ATTEMPTS:-3}"
NAME="terminus-mlab-full"

# cifar10 и imdb исключены. У AutoDS они дали шестнадцать исчерпанных бюджетов
# из шестнадцати: это единственные две задачи набора, у которых тяжёлый счёт
# сошёлся с урезанным вдвое бюджетом (3600 с против 7200 у остальных тяжёлых),
# а образ собран под ускоритель, которого на этой машине нет. Гонять их ещё раз
# — тратить сутки на заведомый ноль. В таблице у них остаются опубликованные
# одиночные числа с пометкой, что повтор не удался.
TASKS="${TASKS-amp-parkinsons clrs fathomnet feedback house-price identify-contrails ogbn-arxiv spaceship-titanic}"
SEL=(); for t in $TASKS; do SEL+=(-i "$t"); done
L=mlab-terminus.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> "$L"; }
: > "$L"
say "Terminus-2, задач $(echo $TASKS | wc -w), попыток на задачу $ATT, разом $HARBOR_CONCURRENCY"
say "задачи: $TASKS"

JOBNAME="$NAME" ATTEMPTS="$ATT" ./run.sh term-set "${SEL[@]}" > mlab-terminus.out 2>&1
rc=$?
j=$(ls -dt jobs/$NAME-2* 2>/dev/null | head -1)
say "код $rc, задание $(basename "${j:-нет}")"
if [ -n "${j:-}" ]; then
  n=0
  for r in "$j"/*/verifier/reward.json; do
    [ -f "$r" ] || continue
    n=$((n+1))
    say "  $(basename "$(dirname "$(dirname "$r")")") -> $(tr -d '\n ' < "$r" | head -c 120)"
  done
  say "испытаний с наградой: $n"
  # таймаут тут не равен «нет результата»: проверяющий считает то, что успело
  # лечь в submission.csv, и такие испытания сплошь и рядом дают оценку
  say "исчерпали бюджет: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -l AgentTimeoutError | wc -l), прочих исключений: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -L AgentTimeoutError | wc -l)"
fi
say "опыт B закончен"
