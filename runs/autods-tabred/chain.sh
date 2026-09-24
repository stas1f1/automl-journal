#!/bin/bash
# Дожидается конца текущей серии full и запускает три оставшиеся ячейки сетки
# подряд на том же образе и той же параллельности. Параллельность входит
# в измерение: менять её между ячейками нельзя.
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY=4
CUR="jobs/autods-tabred-full-20260828-151739"
LOG="chain.log"
say() { echo "[$(date +%F\ %H:%M:%S)] $*" >> "$LOG"; }

say "цепочка запущена, жду конца $CUR"
stall=0; prev=-1
while true; do
  n=$(find "$CUR" -name reward.json 2>/dev/null | wc -l)
  [ "$n" -ge 24 ] && { say "текущая серия закрыта: наград $n"; break; }
  if [ "$n" -eq "$prev" ]; then stall=$((stall+1)); else stall=0; prev=$n; fi
  # 18 проверок по 5 минут = 90 минут без движения при часовом потолке -- это остановка
  if [ "$stall" -ge 18 ]; then say "ОСТАНОВКА: наград $n, полтора часа без движения; цепочка не стартует"; exit 1; fi
  sleep 300
done

for cell in nolayer libonly disconly; do
  say "=== ячейка $cell"
  ./run.sh "$cell" > "$cell.log" 2>&1
  rc=$?
  j=$(ls -dt jobs/autods-tabred-$cell-* 2>/dev/null | head -1)
  say "ячейка $cell завершена, код $rc, задание ${j:-нет}, наград $(find "$j" -name reward.json 2>/dev/null | wc -l)"
  if [ "$rc" -ne 0 ]; then say "ПРЕРВАНО на $cell"; exit 1; fi
done
say "цепочка закончена"
