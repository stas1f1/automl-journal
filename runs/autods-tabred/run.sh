#!/usr/bin/env bash
# Re-run AutoDS-Tools on the common TabReD adapter (full official splits).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADAPTER="$HERE/harbor-tabred-adapter"
AUTODS="$HERE/AutoDS-Tools"
AUTODS_REPO="https://github.com/florentiner/AutoDS-Tools.git"
AUTODS_BRANCH="mlab-gpu-pub"
export PATH="$HOME/.local/bin:$PATH"

# Trials run concurrently; the wall-clock per trial is one of the numbers we
# report, so this must be identical across every cell being compared and is
# stated with the results rather than left implicit.
CONC="${HARBOR_CONCURRENCY:-2}"

ENV_FILE=""
for cand in "$HERE/env.local" "$HERE/../../.env"; do
  if [[ -f "$cand" && -s "$cand" ]]; then ENV_FILE="$cand"; break; fi
done
# Значения, переданные вызывающим, должны пережить чтение .env: ось модели
# задаётся именно ими, а .env всегда содержит основную модель. Без этого
# ячейка оси молча пошла бы на прежней модели и была бы неотличима от неё.
_OV_MODEL="${AUTODS_MODEL:-}"
_OV_TMODEL="${TERMINUS_MODEL:-}"
_OV_PIN="${AUTODS_PRICE_INPUT_PER_1M:-}"
_OV_POUT="${AUTODS_PRICE_OUTPUT_PER_1M:-}"
if [[ -n "$ENV_FILE" ]]; then
  echo "читаю переменные из $ENV_FILE"
  set -a; . "$ENV_FILE"; set +a
  [[ -n "$_OV_MODEL"  ]] && export AUTODS_MODEL="$_OV_MODEL"
  [[ -n "$_OV_TMODEL" ]] && export TERMINUS_MODEL="$_OV_TMODEL"
  [[ -n "$_OV_PIN"    ]] && export AUTODS_PRICE_INPUT_PER_1M="$_OV_PIN"
  [[ -n "$_OV_POUT"   ]] && export AUTODS_PRICE_OUTPUT_PER_1M="$_OV_POUT"
else
  echo "не найден непустой env.local (или .env в корне репозитория)." >&2
  echo "скопируйте env.example в env.local и заполните AUTODS_API_KEY." >&2
  [[ "${1:-}" != "prepare" ]] && exit 1
fi
if [[ "${1:-}" != "prepare" && -z "${AUTODS_API_KEY:-}" ]]; then
  echo "AUTODS_API_KEY пуст — прогон не пойдёт." >&2; exit 1
fi

# AutoDS is not baked into the TabReD task images, so it is installed into the
# container from a pip spec at run time.
SPEC="git+${AUTODS_REPO}@${AUTODS_BRANCH}#subdirectory=packages/autods git+${AUTODS_REPO}@${AUTODS_BRANCH}#subdirectory=apps/harbor"

# The prescribed-knowledge layer is composed on the HOST, by the copy of
# autods_harbor that `prepare` snapshots into the harbor tool venv -- not by the
# copy pip installs inside the container.  So `prepare` is not idempotent with
# respect to the treatment: re-running it against a newer AutoDS-Tools checkout
# silently swaps the layer text and makes new runs incomparable to old ones.
# `verify` prints the fingerprint of the layer that would actually be applied.
LAYER_SHA="a58b4d40678ff1aa"   # tabular layer, 4972 chars, produced every run in the paper

verify() {
  local V=""
  for lib in "$(uv tool dir 2>/dev/null)"/harbor/lib/python3.*/site-packages/autods_harbor; do
    [[ -d "$lib" ]] && { V="$lib"; break; }
  done
  [[ -n "$V" ]] || { echo "не найден установленный autods_harbor под $(uv tool dir 2>/dev/null)/harbor/lib" >&2; return 1; }
  python3 - "$V" <<'PYEOF'
import hashlib, sys
sys.path.insert(0, sys.argv[1])
import c1_prompt as c
layer = "\n\n" + c._LIBRARY["tabular"] + "\n" + c._DISCIPLINE
sha = hashlib.sha256(layer.encode()).hexdigest()[:16]
print(f"слой tabular: {len(layer)} символов, sha {sha}")
PYEOF
  echo
  echo "строка в trial.log, подтверждающая применение слоя: 'AutoDS C1 layer applied'"
  local on off
  for job in "$HERE"/jobs/*/; do
    [[ -d "$job" ]] || continue
    on=$( { grep -l  'C1 layer applied' "$job"*/trial.log 2>/dev/null || true; } | wc -l)
    off=$( { grep -L 'C1 layer applied' "$job"*/trial.log 2>/dev/null || true; } | wc -l)
    local halves
    halves=$( { grep -ho 'tool=[A-Za-z]*, discipline=[A-Za-z]*' "$job"*/trial.log 2>/dev/null || true; } \
              | sort -u | paste -sd';' - )
    printf '  %-46s слой вкл %2d, выкл %2d  %s\n' "$(basename "$job")" "$on" "$off" "${halves:-}"
  done
}

prepare() {
  local TABRED_ARGS=("$@")
  [[ -d "$ADAPTER" ]] || git clone --depth 1 https://github.com/AaLexUser/harbor-tabred-adapter.git "$ADAPTER"
  [[ -d "$AUTODS"  ]] || git clone --depth 1 -b "$AUTODS_BRANCH" "$AUTODS_REPO" "$AUTODS"
  # Harbor must import the agent class from the host process.
  uv tool install harbor --with "$AUTODS/apps/harbor" --force
  # Build the eight task directories from the Kaggle-hosted preprocessed data.
  # NB: the adapter and the upstream `tabred` PyPI package both declare a
  # console script named `tabred`; the package wins in the venv. Call the
  # adapter module directly so the right one runs.
  ( cd "$ADAPTER/adapters/tabred" && uv sync && uv run python -m tabred_adapter.main "${TABRED_ARGS[@]}" )
  echo
  echo "готово. задачи:"; ls "$ADAPTER/datasets/tabred" 2>/dev/null || \
    echo "  ВНИМАНИЕ: datasets/tabred не создан — проверьте учётку Kaggle и правила соревнований"
}

# Terminus-2 on whatever image the adapter currently carries.  Run this while
# the task images are patched (autods_dockerfile.patch.py, no --revert) and it
# becomes the matched-provisioning arm: same data, same metrics, same libraries
# available, only the architecture differs.  Run it after --revert and it
# reproduces the stock-image baseline instead.
run_terminus() {  # run_terminus <job-name> <attempts> [extra harbor args...]
  local name="$1" k="$2"; shift 2
  name="${name}-$(date +%Y%m%d-%H%M%S)"
  # Harbor resolves credentials per provider, not from AUTODS_*: terminus-2 wants
  # OPENROUTER_API_KEY and a model string carrying the provider prefix. The
  # published Terminus-2 job used openrouter/google/gemma-4-31b-it.
  : "${OPENROUTER_API_KEY:=${AUTODS_API_KEY:?нет ни OPENROUTER_API_KEY, ни AUTODS_API_KEY}}"
  export OPENROUTER_API_KEY
  local model="${TERMINUS_MODEL:-openrouter/${AUTODS_MODEL:?задайте AUTODS_MODEL в env.local}}"
  # набор задач выбирается вызывающим: вариант tabred-kdisc несёт тот же блок
  # дисциплины, что получает AutoDS, дописанный в само задание
  ( cd "$ADAPTER" && harbor run \
      -p "${TASKSET:-datasets/tabred}" \
      -a terminus-2 \
      -m "$model" \
      --job-name "$name" \
      -o "$HERE/jobs" \
      -k "$k" \
      -n "$CONC" \
      "$@" )
}

run() {  # run <job-name> <attempts> [extra harbor args...]
  local name="$1" k="$2"; shift 2
  # Harbor refuses to reuse a job dir whose lock.json no longer matches (it
  # changes whenever a task image changes), so give every run a fresh name.
  name="${name}-$(date +%Y%m%d-%H%M%S)"
  # набор задач и рабочий каталог задаёт вызывающий: у TabReD агент работает в
  # /app, у MLAgentBench данные разложены в /workspace и туда же пишется
  # submission.csv, так что каталог должен совпадать с тем, что объявлен в
  # artifacts задачи — иначе агент готовит ответ не там, где его ищет проверяющий
  ( cd "$ADAPTER" && harbor run \
      -p "${TASKSET:-datasets/tabred}" \
      -a autods_harbor.agent:AutoDSAgent \
      -m "${AUTODS_MODEL:?задайте AUTODS_MODEL в env.local}" \
      --ak install_spec="$SPEC" \
      --ak workspace="${WORKSPACE:-/app}" \
      --job-name "$name" \
      -o "$HERE/jobs" \
      -k "$k" \
      -n "$CONC" \
      "$@" )
}

case "${1:-}" in
  prepare) shift; prepare "$@" ;;
  # fingerprint the layer that would actually be applied, and audit past jobs
  verify)  verify ;;
  smoke)   run "autods-tabred-smoke" 1 -i cooking-time ;;
  full)    run "autods-tabred-full"  3 ;;
  # ось бэкбона: модель и её цены приходят из окружения, MODEL_SLUG попадает
  # в имя задания, чтобы ячейки оси не путались между собой.
  axis-autods)   run "autods-tabred-M${MODEL_SLUG:?задайте MODEL_SLUG}" 3 ;;
  axis-terminus) run_terminus "terminus-tabred-M${MODEL_SLUG:?задайте MODEL_SLUG}" 3 ;;
  axis-autods-smoke)   run "autods-tabred-M${MODEL_SLUG:?задайте MODEL_SLUG}-smoke" 1 -i cooking-time ;;
  # одна попытка на каждую из восьми задач: для ячейки, где ожидается сплошной
  # отказ, восьми испытаний хватает, а три попытки только умножали бы таймауты
  axis-autods-1) run "autods-tabred-M${MODEL_SLUG:?задайте MODEL_SLUG}" 1 ;;
  axis-terminus-smoke) run_terminus "terminus-tabred-M${MODEL_SLUG:?задайте MODEL_SLUG}-smoke" 1 -i cooking-time ;;
  # matched-provisioning arm: Terminus-2 on the enriched image.  Only
  # meaningful while the images are patched; check before launching.
  # K_disc, скрещенный с Terminus-2: тот же текст, поданный через задание
  kdisc-smoke) export TASKSET=datasets/tabred-kdisc; run_terminus "terminus-kdisc-smoke" 1 -i cooking-time ;;
  kdisc)       export TASKSET=datasets/tabred-kdisc; run_terminus "terminus-kdisc"       3 ;;
  # общая форма того же самого: набор задач и имя задания задаёт вызывающий.
  # Нужна для ячеек, где блок урезан или заменён другой половиной слоя, чтобы
  # не заводить отдельный режим под каждую.
  term-set-smoke) shift; run_terminus "${JOBNAME:?задайте JOBNAME}-smoke" 1 -i "${SMOKE_TASK:-cooking-time}" "$@" ;;
  # лишние аргументы передаются дальше: ими вызывающий сужает набор задач.
  # Без "$@" фильтр молча теряется и прогон идёт по всему набору — на этом я
  # уже сжёг час машинного времени в дымовой проверке AutoDS.
  term-set)       shift; run_terminus "${JOBNAME:?задайте JOBNAME}"       "${ATTEMPTS:-3}" "$@" ;;
  # одна задача набора, столько попыток, сколько скажут: нужно для MLAgentBench,
  # где недостающие задачи добираются поштучно, а у ветки одна попытка на задачу
  term-one)       run_terminus "${JOBNAME:?задайте JOBNAME}" "${ATTEMPTS:-1}" -i "${TASK:?задайте TASK}" ;;
  # то же для AutoDS: набор задач, каталог и число попыток задаёт вызывающий.
  # Ветка «без слоя» получает ещё и AUTODS_C1_DISABLED=1 снаружи, ветка
  # «с опубликованным слоем» — набор задач, где instruction.md уже несёт слой,
  # и тот же флаг, чтобы слой не наложился вторым слоем поверх первого
  # оба режима гасят сборщик слоя: в задачах MLAgentBench слой приходит текстом
  # задания (набор mlab-c1) либо не приходит вовсе (набор mlab), и сборщик тут
  # только наложил бы поверх ещё и свой, сегодняшний — не тот, что публиковался.
  # .env читается выше и ставит эту переменную пустой, поэтому экспорт здесь,
  # после чтения, а не снаружи скрипта.
  autods-set)     export AUTODS_C1_DISABLED=1; shift
                  run "${JOBNAME:?задайте JOBNAME}" "${ATTEMPTS:-3}" "$@" ;;
  autods-one)     export AUTODS_C1_DISABLED=1; shift
                  run "${JOBNAME:?задайте JOBNAME}" "${ATTEMPTS:-1}" -i "${TASK:?задайте TASK}" "$@" ;;
  # то же, но сборщик слоя НЕ гасится: ветка получает слой сегодняшней редакции,
  # собранный на лету из c1_prompt по семейству задачи. Нужна, чтобы оценить
  # разницу между выложенной редакцией и текущей в результатах, а не в символах.
  # .env ставит переменную пустой, поэтому явно снимаем её здесь.
  autods-set-layer) unset AUTODS_C1_DISABLED; shift
                  run "${JOBNAME:?задайте JOBNAME}" "${ATTEMPTS:-3}" "$@" ;;
  matched-smoke) run_terminus "terminus-matched-smoke" 1 -i cooking-time ;;
  matched)       run_terminus "terminus-matched"       3 ;;
  # AutoDS with the prescribed-knowledge layer switched off, on the same
  # adapter and the same image.  Isolates the layer from the architecture:
  # `full` minus `nolayer` is what the prescription is worth here.
  # The layer is composed on the host before the container starts, so exporting
  # the variable here is enough -- but VERIFY: trial.log must NOT contain the
  # line "AutoDS C1 layer applied".  If it does, the run is not what it claims.
  nolayer-smoke) export AUTODS_C1_DISABLED=1; run "autods-tabred-nolayer-smoke" 1 -i cooking-time ;;
  nolayer)       export AUTODS_C1_DISABLED=1; run "autods-tabred-nolayer"       3 ;;
  # The two half-cells of the K_tool x K_disc design.  enable_halves.py must have
  # been applied first; it backports the flags without touching the layer text,
  # so `full` above is the both-on cell and `nolayer` the neither cell, and only
  # these two remain to be run.  Check trial.log for tool=/discipline= to confirm
  # which half actually shipped.
  libonly-smoke) export AUTODS_K_DISC_DISABLED=1; run "autods-tabred-libonly-smoke" 1 -i cooking-time ;;
  libonly)       export AUTODS_K_DISC_DISABLED=1; run "autods-tabred-libonly"       3 ;;
  disconly-smoke) export AUTODS_K_TOOL_DISABLED=1; run "autods-tabred-disconly-smoke" 1 -i cooking-time ;;
  disconly)      export AUTODS_K_TOOL_DISABLED=1; run "autods-tabred-disconly"      3 ;;
  *) echo "usage: $0 {prepare|verify|smoke|full|matched-smoke|matched|nolayer-smoke|nolayer|libonly|disconly|axis-autods|axis-terminus|kdisc-smoke|kdisc|term-set-smoke|term-set|term-one|autods-set|autods-set-layer|autods-one (TASKSET= WORKSPACE= JOBNAME= TASK= ATTEMPTS=)}" >&2; exit 2 ;;
esac
