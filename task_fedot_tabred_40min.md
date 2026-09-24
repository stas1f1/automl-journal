# Задание: FEDOT.LLM на TabReD с 40-минутным бюджетом бэкенда

Дата постановки: 22 сентября 2026. Ответ нужен до подачи в FGCS.

## Зачем

Строка FEDOT.LLM в лидерборде (Таблица 4) снята соавтором 14 августа 2026
адаптером `harbor_adapter.agent:FedotLLMHarborAgent` из монорепозитория
FEDOT.LLM: бюджет AutoML бэкенда 1 минута, тюнинг выключен, набор моделей
`{lgbm}`, итоговый конвейер в каждом из восьми трайлов один узел LightGBM, по
одному трайлу на задачу. Агентам на тех же задачах дан час. От этой строки
отсчитываются оба размаха статьи: 0.54 для систем как поставляются и 0.44 для
архитектуры без слоя (`\spanShip`, `\spanArch`), и на ней стоит тезис о
немонотонности. Сейчас разница бюджетов заявлена как факт конфигурации в §4.6,
§5.1, §8.4 и подписи Таблицы 2. Рецензент спросит, почему одной системе дали
минуту. Прогон с 40-минутным бюджетом, как на кейсах 10 сентября, снимает
вопрос в обе стороны: либо FEDOT.LLM остаётся внизу, и вывод крепнет, либо
поднимается, и это надо знать до подачи.

## Что уже есть

- Агент `runs/autods-tabred/fedot_harbor/src/fedot_harbor/agent.py`
  (`FedotLLMAgent`): запускает `fedotllm /workspace` внутри контейнера с
  `-o automl.enabled=fedot -o time_limit=$FEDOTLLM_TIME_LIMIT` (по умолчанию
  2400 с), модель через OpenRouter, ключ из `.env` (`AUTODS_API_KEY`), прокси
  хоста пробрасывается. Ставится в venv инструмента harbor:
  `uv pip install --python "$(uv tool dir)/harbor/bin/python" ./fedot_harbor`.
- Рецепт образа с fedotllm: константа `FEDOT_DOCKERFILE` в
  `runs/autods-tabred/make_cases.py` (python:3.10-slim, torch CPU, fedotllm из
  копии исходников). Исходники: снимок
  `~/Documents/GitHub/Fedot-assistant-feat-fedot-ind-tabular`, перед сборкой
  через `fedot_patch.py` (убраны fedot-ind и dask-expr, пин `click<8.2`).
  Образ около 5 ГБ, собирался на кейсах 10 сентября.
- Задачи TabReD: `runs/autods-tabred/harbor-tabred-adapter/datasets/tabred/<task>/`,
  восемь штук, официальные сплиты. Контракт: данные в `/app/data`
  (`train.csv`, `val.csv` со столбцом `target`, `test.csv` без него,
  `schema.json`), выход `/app/predictions.csv` с единственным столбцом
  `target` в порядке `test.csv`. Скорер `tests/score.py` пишет
  `/logs/verifier/reward.json` с сырой метрикой (`roc_auc` или `rmse`).
  Потолок агента `timeout_sec = 3600`, 8 CPU.
- Сборщик `runs/autods-tabred/collect.py jobs --only=<подстрока>` печатает
  готовый словарь для `AGENTS` в `paper/make_tables.py`.

## Что мешает запустить как есть

1. Образы TabReD (python:3.12-slim) не содержат fedotllm, а fedotllm принимает
   только python 3.10. Нужен вариант набора с образом из `FEDOT_DOCKERFILE`.
2. Агент собирает `sample_submission.csv` из констант `prepare.py` кейсов
   (`ID`, `TARGET`), которых в задачах TabReD нет, и пишет
   `/workspace/submission.csv` с двумя столбцами. Скорер TabReD ждёт
   `/app/predictions.csv` с одним столбцом `target`.

## Шаги

### 1. Набор `datasets/tabred-fedot`

Скрипт `runs/autods-tabred/make_tabred_fedot.py` по образцу `build_fedot` из
`make_cases.py`:

- для каждой из восьми задач скопировать каталог задачи в
  `datasets/tabred-fedot/<task>` без `solution/`; данные (`environment/data`,
  до 700 МБ на задачу) не копировать, а связать жёсткими ссылками
  (`cp -al`), символические ссылки Docker в контекст сборки не берёт;
- `environment/Dockerfile` заменить на `FEDOT_DOCKERFILE` без строк про
  `prepare.py` и `/opt/venvs/tabular`, добавить `COPY data/ /app/data/` и
  `libgomp1` (уже есть в рецепте);
- скопировать исходники fedotllm в `environment/fedotllm-src`, как делает
  `build_fedot`;
- в `task.toml` заменить `name = "yandex-research/tabred__…"` на
  `"tabred-fedot/…"`, остальное (потолки, CPU) оставить;
- `instruction.md`, `tests/` оставить без изменений: скорер и данные те же,
  что у Terminus-2 и AutoDS-Tools.

### 2. Агент `FedotLLMTabredAgent`

Подкласс `FedotLLMAgent` в том же `agent.py`, отличия только в раскладке:

- перед запуском: собрать в `/workspace` файлы `train.csv`, `test.csv`,
  `sample_submission.csv` из `/app/data`. Обучающая таблица: `train.csv`
  плюс `val.csv` (агенты получают размеченную валидацию, см. пятую угрозу в
  §8.4; бэкенд сам отрежет валидацию). `sample_submission.csv`: столбец `id`
  с номером строки теста и столбец `target` с нулями; `description.md` из
  текста задачи, как сейчас;
- после запуска: из `/workspace/submission.csv` взять столбец `target` в
  исходном порядке строк и записать `/app/predictions.csv` без индекса.
  Проверить число строк против `test.csv`;
- `FEDOTLLM_TIME_LIMIT=2400`; настройки тюнинга и набора моделей оставить по
  умолчанию снимка, как на кейсах. В `fedotllm.log` трайла должно быть видно
  `time_limit=2400` и включённый тюнинг; записать точную конфигурацию в
  `result_files/DATA_SOURCES.md`.

### 3. Пробный трайл

```bash
cd runs/autods-tabred
python3 make_tabred_fedot.py --fedot-src ~/Documents/GitHub/Fedot-assistant-feat-fedot-ind-tabular weather
FEDOTLLM_TIME_LIMIT=2400 ATTEMPTS=1 TASKS=weather SUFFIX=-smoke ./tabred_fedot.sh
```

Скрипт `tabred_fedot.sh` пишется по образцу `cases_fedot.sh`:
`harbor run -p datasets/tabred-fedot -a fedot_harbor.agent:FedotLLMTabredAgent
-m openrouter/google/gemma-4-31b-it --job-name fedot-tabred-40min-<дата>
-o ../jobs -k $ATTEMPTS -n $HARBOR_CONCURRENCY`. Смотреть: собрался ли образ
(1200 с на сборку по `task.toml`), появился ли `/app/predictions.csv`,
что в `reward.json`, сколько минут занял трайл, что пишет `fedotllm.log` про
бюджет и тюнинг. Если бэкенд не укладывается в 40 минут на больших таблицах
(`cooking-time` 227 тыс. строк × 192 признака, `homesite-insurance`),
уменьшить `FEDOTLLM_TIME_LIMIT` до 1800 и записать это; потолок задачи
3600 с включает чтение данных и предсказание.

### 4. Полный прогон

```bash
FEDOTLLM_TIME_LIMIT=2400 ATTEMPTS=3 HARBOR_CONCURRENCY=4 ./tabred_fedot.sh
```

Восемь задач × 3 попытки = 24 трайла; при 40 минутах бюджета и параллели 4
около 5 часов на сервере nss-calc2 (18 ядер), плюс сборка образа. Стоимость
токенов у FEDOT.LLM на кейсах $0.003–0.021 за трайл, то есть до одного доллара
на весь прогон. Машина и параллель те же, что у повторов AutoDS-Tools 28
августа, чтобы времена были сопоставимы.

### 5. Сбор и проверка

```bash
python3 collect.py jobs --only=fedot-tabred-40min
```

Проверить: 24 `reward.json`; сколько трайлов без посылки и сколько упёрлись в
потолок (`exception.txt` с `AgentTimeoutError`); что метрика в `reward.json`
сырая (`rmse`, `roc_auc`), как у остальных; что данные и скорер не менялись
(`tests/` те же файлы). Выложить задание на хаб (`harbor hub job upload` или
как для повторов) и записать идентификатор в `DATA_SOURCES.md`, мастер-таблицу
и `progress.md`.

### 6. Правки в статье

Решение по умолчанию: строка с 40-минутным бюджетом становится строкой
FEDOT.LLM в статье, строка соавтора с минутным бюджетом уходит в
дополнительные материалы как «FEDOT.LLM, adapter defaults». Тогда:

- `paper/make_tables.py`: `AGENTS["FEDOT.LLM"]` заменить средними по трём
  попыткам, добавить `FEDOT_ATTEMPTS` для шумового пола (§4.4), строку в
  `TELEMETRY` для Таблицы 7 (стоимость, токены, сумма времён трайлов),
  сохранить минутную строку отдельным словарём для приложения;
- `paper/make_figures.py`: в `rk_corner` FEDOT.LLM получает усы по попыткам,
  как два других агента; подпись рисунка рангов в §5;
- Таблица 2 (arms): строка FEDOT.LLM на TabReD, 24 трайла, образ «FEDOT
  image», подпись про бюджеты;
- §4.6: абзац про два издания и два бюджета переписать: минутный прогон
  соавтора остаётся как проверка, основная строка снята с тем же бюджетом,
  что на кейсах; §5.1 абзац про FEDOT.LLM (сейчас говорит про один узел
  LightGBM и минутный бюджет); §8.4 первая угроза («one run for FEDOT.LLM»)
  и шестая, если ранг сдвинулся; §6.4 фраза «against the one-minute budget
  of its TabReD row»; §3.4 оговорка «under the backend budget its adapter
  set»;
- если положение FEDOT.LLM относительно линейной регрессии изменится,
  править аннотацию, введение (вклад i), Highlights 1 и заключение: там
  стоит «level with linear regression»;
- пересобрать: `python3 make_tables.py && python3 make_figures.py &&
  latexmk -pdf main.tex`; проверить лимит 18 страниц со снятыми `\todo`.

### 7. Критерии готовности

- 24 трайла с `reward.json`, число потерянных и срезанных по потолку названо.
- В `fedotllm.log` каждого трайла бюджет 2400 с (или единый меньший) и
  включённый тюнинг; конфигурация записана в `DATA_SOURCES.md`.
- Идентификатор задания на хабе и словарь в `make_tables.py` совпадают с
  `collect.py` до последнего знака.
- Статья собирается без ошибок, все числа про FEDOT.LLM идут через макросы,
  текст про бюджет в §4.6, §5.1, §8.4 и подписях согласован.

## Риски

- Образ 5 ГБ и восемь сборок: на nss-calc2 место и время сборки; сборку можно
  разделить, собрав базовый образ с fedotllm один раз и наследуя его в восьми
  Dockerfile.
- FEDOT на 227 тыс. строк × 192 признака за 40 минут: возможны падения по
  памяти или выход за потолок 3600 с; для этого пробный трайл на большой
  задаче до полного прогона.
- Обучение на `train + val` против `train` у опубликованных базовых линий:
  та же небольшая фора, что у агентов, и она уже названа в §8.4; записать
  выбор в `DATA_SOURCES.md`.
