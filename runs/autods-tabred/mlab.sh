#!/bin/bash
# Задачи MLAgentBench, которых не хватает у Terminus-2.
# Ветка снята с одной попыткой на задачу, поэтому ATTEMPTS=1 — как у остальных
# шести задач этой ветки, иначе строки таблицы покрытия несопоставимы.
# Задачи, которые качать долго, передаются вторым списком: они пойдут после.
cd /var/essdata/s_chumakov/automl-journal/runs/autods-tabred || exit 1
export PATH="$HOME/.local/bin:$PATH"
export HARBOR_CONCURRENCY=2
export TASKSET=datasets/mlab
export ATTEMPTS=1
# без двоеточия: пустое значение означает "ничего не запускать", а не
# "подставь список по умолчанию" — на этом я уже дважды перезапустил лишнее
READY="${READY-clrs feedback identify-contrails}"
LATER="${LATER-fathomnet}"
L=mlab.log
say(){ echo "[$(date +%F\ %H:%M:%S)] $*" >> $L; }
: > $L

one(){  # one <задача>
  local t="$1"
  say "=== задача $t"
  TASK="$t" JOBNAME="terminus-mlab-$t" ./run.sh term-one > "mlab-$t.log" 2>&1
  local rc=$? j; j=$(ls -dt jobs/terminus-mlab-$t-2* 2>/dev/null | head -1)
  say "  код $rc, задание $(basename ${j:-нет})"
  say "  награда: $(cat $j/*/verifier/reward.json 2>/dev/null | tr -d '\n ' | head -c 160)"
  say "  таймаутов: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -l AgentTimeoutError | wc -l), прочих исключений: $(find "$j" -name exception.txt -print0 2>/dev/null | xargs -0 -r grep -L AgentTimeoutError | wc -l)"
  if [ "$rc" -ne 0 ]; then say "  ПОСЛЕДНИЕ СТРОКИ: $(tail -3 mlab-$t.log | tr '\n' ' ' | head -c 300)"; fi
}

# тяжёлое качается параллельно прогонам, а не до них
if [ -n "$LATER" ]; then
  say "=== качаю в фоне: $LATER"
  ( python3 fetch_mlab.py $LATER > mlab-fetch.log 2>&1; echo $? > mlab-fetch.rc ) &
fi

say "=== перемычка проверяющего для готовых задач"
python3 mlab_testsh.py $READY >> $L 2>&1
say "=== правка образа: tmux и apt"
python3 mlab_patch.py $READY >> $L 2>&1

for t in $READY; do one "$t"; done

if [ -n "$LATER" ]; then
  say "=== жду догрузку"
  wait
  say "загрузка: код $(cat mlab-fetch.rc 2>/dev/null), $(tail -1 mlab-fetch.log 2>/dev/null)"
  python3 mlab_testsh.py $LATER >> $L 2>&1
  python3 mlab_patch.py $LATER >> $L 2>&1
  for t in $LATER; do
    if [ -f "harbor-tabred-adapter/datasets/mlab/$t/task.toml" ]; then one "$t"; else say "=== $t: не докачалась, пропускаю"; fi
  done
fi

say "задачи MLAgentBench закончены"
