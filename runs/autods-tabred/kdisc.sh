#!/bin/bash
# K_disc, скрещенный с Terminus-2: сначала проба, потом полный проход
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY=4
L=kdisc.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> $L; }
: > $L
say "=== проба"
./run.sh kdisc-smoke > kdisc-smoke.log 2>&1
rc=$?; j=$(ls -dt jobs/terminus-kdisc-smoke-* 2>/dev/null | head -1)
say "проба код $rc; награда: $(cat $j/*/verifier/reward.json 2>/dev/null | tr -d '\n ' | head -c 120)"
if [ "$rc" -ne 0 ]; then say "ПРЕРВАНО на пробе"; exit 1; fi
# проверка по существу: блок дисциплины должен быть в задании, которое видел агент
n=$(grep -l "REQUIRED, STRICT" $j/*/agent/trajectory.json 2>/dev/null | wc -l)
say "блок в задании испытания: $n (ожидается 1)"
say "=== полный проход"
./run.sh kdisc > kdisc-full.log 2>&1
rc=$?; j=$(ls -dt jobs/terminus-kdisc-2* 2>/dev/null | head -1)
say "проход код $rc, задание ${j:-нет}, наград $(find "$j" -name reward.json 2>/dev/null | wc -l)/24"
say "K_disc на Terminus-2 закончен"
