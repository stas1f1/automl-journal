#!/bin/bash
# Одна ячейка: блок дисциплины без двух разделов про время и эпохи.
# Проверяет, эти ли разделы стоили Terminus-2 половины ответов.
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY=4
export TASKSET=datasets/tabred-kdisc-notime
export JOBNAME=terminus-kdisc-notime
L=notime.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> $L; }
: > $L

say "=== сборка набора задач"
python3 make_kdisc_tasks.py --out tabred-kdisc-notime \
  --drop "Training discipline" --drop "Time budget management" >> $L 2>&1 || { say "ПРЕРВАНО на сборке"; exit 1; }

say "=== проба"
./run.sh term-set-smoke > notime-smoke.log 2>&1
rc=$?; j=$(ls -dt jobs/${JOBNAME}-smoke-* 2>/dev/null | head -1)
say "проба код $rc; награда: $(cat $j/*/verifier/reward.json 2>/dev/null | tr -d '\n ' | head -c 120)"
[ "$rc" -ne 0 ] && { say "ПРЕРВАНО на пробе"; exit 1; }

# проверка воздействия: урезанный блок должен быть в траектории, а речи про
# время и эпохи в ней быть не должно
say "блок в траектории: $(grep -l "REQUIRED, STRICT" $j/*/agent/trajectory.json 2>/dev/null | wc -l) (ожидается 1)"
say "речь про часы в траектории: $(grep -l "hours, not minutes" $j/*/agent/trajectory.json 2>/dev/null | wc -l) (ожидается 0)"

say "=== полный проход"
./run.sh term-set > notime-full.log 2>&1
rc=$?; j=$(ls -dt jobs/${JOBNAME}-2* 2>/dev/null | head -1)
say "проход код $rc, задание ${j:-нет}, наград $(find "$j" -name reward.json 2>/dev/null | wc -l)/24"
say "потерянных: $(grep -l '\"reward\": 0.0' $j/*/verifier/reward.json 2>/dev/null | wc -l) (без блока 2, с полным блоком 13)"
say "ячейка notime закончена"
