# Architecture over Parameters: агентный AutoML на одной слабой модели

Рукопись для Future Generation Computer Systems (Elsevier). Три системы
автоматического машинного обучения на LLM работают на одной открытой модели
`gemma-4-31b-it`: FEDOT.LLM (жёсткий конвейер над AutoML-бэкендом FEDOT),
AutoDS-Tools (шесть агентов) и Terminus-2 (открытая оболочка с шеллом).
Модель зафиксирована, меняется только система вокруг неё, результат
сравнивается с восемнадцатью тюненными базовыми методами TabReD.

Главные выводы. Лучшая система выходит на уровень тюненного LightGBM и не
достаёт до тюненного XGBoost. Большая часть разрыва между агентными системами
приходится на файл инструкций, который поставляется с AutoDS-Tools; без него
три архитектуры расходятся в пределах шума. Тот же файл, помогающий на
задачах с нуля, оставляет задачи без посылки там, где дан рабочий скрипт
(MLAgentBench), и теряет попытки, если его приложить к другой архитектуре.
На трёх научных задачах открытая оболочка с одним текстом задания
сравнялась с авторскими базовыми уровнями или обошла их.

## Структура

| Путь | Что там |
|---|---|
| `paper/` | текст статьи по разделам, генераторы таблиц и рисунков, шаблон elsarticle, архив для Overleaf; подробности в `paper/README.md` |
| `result_files/` | мастер-таблица результатов, `DATA_SOURCES.md` с источником каждого числа, отчёты о прогонах |
| `runs/autods-tabred/` | скрипты запуска и сборки наборов задач, агент `fedot_harbor`, каталоги заданий Harbor с трайлами; описание в `runs/autods-tabred/README.md` |
| `progress.md` | журнал работ по датам |
| `task.md`, `task_fedot_tabred_40min.md` | постановки задач для прогонов |

Сборка статьи: `cd paper && python3 make_tables.py && python3 make_figures.py && latexmk -pdf main.tex`.

## Системы и фреймворки

- FEDOT.LLM: https://github.com/aimclub/FEDOT.LLM; бэкенд FEDOT: https://github.com/aimclub/FEDOT
- AutoDS-Tools: https://github.com/sb-ai-lab/AutoDS-Tools
- Terminus-2, оболочка из Terminal-Bench 2.0: https://github.com/laude-institute/terminal-bench (статья arXiv:2601.11868)
- Harbor, среда запуска и учёта трайлов: https://github.com/harbor-framework/harbor; хаб заданий: https://hub.harborframework.com
- LightAutoML, библиотека, которую предписывает файл инструкций AutoDS-Tools: https://github.com/sb-ai-lab/LightAutoML
- Модели вызывались через OpenRouter с настройками по умолчанию: https://openrouter.ai (`google/gemma-4-31b-it`, `google/gemma-4-26b-a4b-it`, `z-ai/glm-4.7`)

## Бенчмарки

- TabReD, восемь табличных задач с временными сплитами и таблицей тюненных методов: https://github.com/yandex-research/tabred (arXiv:2406.19380)
- MLAgentBench, десять задач с рабочим стартовым скриптом: https://github.com/snap-stanford/MLAgentBench (arXiv:2310.03302)
- Адаптации для Harbor: https://huggingface.co/datasets/danil-e/harbor-datasets-tabred и https://huggingface.co/datasets/danil-e/harbor-datasets-mlab; табличный адаптер с официальными сплитами: https://github.com/AaLexUser/harbor-tabred-adapter

## Научные кейсы

- Урожайность маиса, Genomes to Fields: Kick et al. 2023, G3, https://doi.org/10.1093/g3journal/jkad006; данные https://zenodo.org/records/6916775
- Исход заданий на суперкомпьютере Fugaku, F-DATA: Antici et al. 2025, Scientific Data, https://doi.org/10.1038/s41597-025-05633-1; данные https://zenodo.org/records/11467483
- Температура стеклования полимеров, OpenPoly: Wang et al. 2025, Chinese Journal of Polymer Science, https://doi.org/10.1007/s10118-025-3402-y; данные https://github.com/WangGroupFDU/Openpoly_benchmark

## Прогоны на Harbor Hub

- Terminus-2 на TabReD: https://hub.harborframework.com/jobs/7593cc7b-8b7e-4e5b-87c4-1c1f18527fa7
- Terminus-2 на MLAgentBench (ранний прогон): https://hub.harborframework.com/jobs/1a42d1fe-a3e1-4fa5-a3d4-e5338ae3ff08
- AutoDS-Tools, ранние прогоны со слоем и без: https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3 и https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d
- FEDOT.LLM на TabReD, полная конфигурация (набор `tabred-fedot-schema`): https://hub.harborframework.com/jobs/77c2d2f8-722e-471a-bf44-b075776c308e, https://hub.harborframework.com/jobs/374be194-9097-4b57-810b-354ce774cf8d, https://hub.harborframework.com/jobs/b9de44ad-9ef2-473e-a864-fd2e0bf7785f, https://hub.harborframework.com/jobs/7768c071-ce0a-4904-b323-efd106e7304d

Повторы AutoDS-Tools и Terminus-2 на нашем оборудовании лежат в
`runs/autods-tabred/jobs/`; какое задание за каким числом стоит, записано в
`result_files/DATA_SOURCES.md`.

## Что не в репозитории

Ключи API (`.env`), вложенные репозитории `runs/autods-tabred/AutoDS-Tools` и
`runs/autods-tabred/harbor-tabred-adapter` вместе с данными TabReD (10 ГБ),
резервные копии статьи и артефакты сборки LaTeX. Контексты Docker для серверов
настраиваются у каждого локально.
