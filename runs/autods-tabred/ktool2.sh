#!/bin/bash
# Пересъёмка ячейки с библиотечной половиной: первый прогон испорчен обрывом
# связи, пять испытаний умерли с ошибкой aiohttp на седьмой минуте.
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY=4
export TASKSET=datasets/tabred-ktool
export JOBNAME=terminus-ktool2
L=ktool2.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> $L; }
: > $L
say "=== пересъёмка библиотечной половины (набор уже собран)"
./run.sh term-set > ktool2-full.log 2>&1
rc=$?; j=$(ls -dt jobs/${JOBNAME}-2* 2>/dev/null | head -1)
say "проход код $rc, задание ${j:-нет}, наград $(find "$j" -name reward.json 2>/dev/null | wc -l)/24"
say "сетевых падений: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -l aiohttp | wc -l) (должно быть 0)"
say "таймаутов: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -l AgentTimeoutError | wc -l)"
say "потерянных: $(grep -l '\"reward\": 0.0' $j/*/verifier/reward.json 2>/dev/null | wc -l)"
say "воздействие: библиотека $(grep -l 'LightAutoML' $j/*/agent/trajectory.json 2>/dev/null | wc -l)/24, дисциплина $(grep -l 'hours, not minutes' $j/*/agent/trajectory.json 2>/dev/null | wc -l)/24 (ожидается 24 и 0)"
say "пересъёмка закончена"
