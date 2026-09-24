#!/bin/bash
# Достроить сетку 2x2 на Terminus-2: две недостающие ячейки.
#   neither  = terminus-tabred-Mmid-20260829-185941   (уже есть)
#   K_disc   = terminus-kdisc-20260830-113531         (уже есть)
#   K_tool   = эта ячейка, библиотечная половина в задании
#   both     = эта ячейка, обе половины
# Все четыре на одном образе (обогащённом), одной модели, параллельности 4.
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY=4
L=grid2.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> $L; }
: > $L

cell(){  # cell <half> <набор> <имя задания> <строка, которой в задании быть НЕ должно>
  local half="$1" set="$2" job="$3" absent="$4"
  say "=== ячейка $half"
  python3 make_kdisc_tasks.py --half "$half" --out "$set" >> $L 2>&1 || { say "ПРЕРВАНО на сборке $half"; return 1; }
  export TASKSET="datasets/$set" JOBNAME="$job"
  ./run.sh term-set-smoke > "$job-smoke.log" 2>&1
  local rc=$? j; j=$(ls -dt jobs/${job}-smoke-* 2>/dev/null | head -1)
  say "  проба код $rc; награда: $(cat $j/*/verifier/reward.json 2>/dev/null | tr -d '\n ' | head -c 120)"
  [ "$rc" -ne 0 ] && { say "ПРЕРВАНО на пробе $half"; return 1; }
  say "  предписание библиотеки в траектории: $(grep -l "LightAutoML" $j/*/agent/trajectory.json 2>/dev/null | wc -l) (ожидается 1)"
  if [ -n "$absent" ]; then
    say "  чего быть не должно ($absent): $(grep -l "$absent" $j/*/agent/trajectory.json 2>/dev/null | wc -l) (ожидается 0)"
  fi
  ./run.sh term-set > "$job-full.log" 2>&1
  rc=$?; j=$(ls -dt jobs/${job}-2* 2>/dev/null | head -1)
  say "  проход код $rc, задание ${j:-нет}, наград $(find "$j" -name reward.json 2>/dev/null | wc -l)/24"
  say "  потерянных: $(grep -l '\"reward\": 0.0' $j/*/verifier/reward.json 2>/dev/null | wc -l) (neither 2, K_disc 13)"
  return 0
}

# сперва библиотечная половина: это та, что у AutoDS дала почти весь эффект
cell tool tabred-ktool terminus-ktool "hours, not minutes" || exit 1
cell both tabred-kboth terminus-kboth "" || exit 1
say "сетка 2x2 на Terminus-2 достроена"
