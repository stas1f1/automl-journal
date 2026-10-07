# Данные, промпты и метрики

## Коротко — что открывать

| что нужно | где |
|---|---|
| данные и промпты MLAgentBench (10 задач) | [huggingface.co/datasets/danil-e/harbor-datasets-mlab](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/tree/main/datasets/mlab-protocol) |
| данные и промпты TabReD (8 задач) | [huggingface.co/datasets/danil-e/harbor-datasets-tabred](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/tree/main/datasets/tabred-real) |
| итоговые метрики | `PAPER_FINAL_all_tasks.csv` — 18 задач, AutoDS против baseline, со ссылками на прогоны |
| прогоны, стоящие за метриками | Harbor Hub: [ветка AutoDS](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3) · [ветка baseline](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d) |
| в чём состоит воздействие | [C1_LAYER.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/C1_LAYER.md) |

Данные в этих репозиториях — ровно те, на которых посчитан `PAPER_FINAL_all_tasks.csv`: сверено по SHA-256 файлов `answer` и `test` каждой из 18 задач, расхождений нет.

## Две ветки сравнения

Ветки отличаются **только промптом**. Данные, скореры, оборудование, модель и температура одинаковы.

| ветка | что получает агент | файл |
|---|---|---|
| **baseline** | `instruction.md` дословно — постановка самого бенчмарка, ничего сверх | `<задача>/instruction.md` |
| **AutoDS (C1)** | тот же `instruction.md` **плюс** слой: предписание использовать специализированную библиотеку под модальность + блоки дисциплины обучения | `<задача>/instruction_c1.md` |

`instruction_c1.md` — не реконструкция: это байты, которые агент получил на прогоне. Проверено, что каждый из 18 файлов начинается ровно с опубликованного `instruction.md` (слой добавляет 5086 символов для tabular, 4364 vision, 4164 nlp, 4154 graph). Сам слой — [c1_prompt.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/c1_prompt.py), разбор — [C1_LAYER.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/C1_LAYER.md).

Какую библиотеку предписывает слой: **tabular** — LightAutoML; **vision** — timm / torchvision, для сегментации segmentation-models-pytorch; **graph** — PyTorch Geometric; **nlp** — HuggingFace transformers / sentence-transformers. Модальность определяется на прогоне по составу рабочего каталога; во всех 18 прогонах C1 применился слой, соответствующий объявленному семейству задачи.

## Условия прогона

| | |
|---|---|
| модель | `gemma-4-31b-it` через OpenRouter |
| температура | 0.2 в обеих ветках |
| повторов | 1 прогон на ячейку (18 задач × 2 ветки = 36 прогонов) |
| оборудование | Apple silicon, ускоритель MPS; одинаково для обеих веток |
| постановка MLAgentBench | улучшить выданный `train.py` (протокол бенчмарка) |
| постановка TabReD | с нуля — в бенчмарке агентного протокола нет |

## MLAgentBench — 10 задач

В рабочем каталоге уже лежит `train.py`, который работает, но даёт плохой результат; задача — улучшить его. Описания задач — дословный `research_problem.txt` из репозитория бенчмарка.

| задача | метрика | семейство | baseline-промпт | промпт C1 | прогон AutoDS | прогон baseline | данные | стартовый скрипт | скорер | источник данных |
|---|---|---|---|---|---|---|---|---|---|---|
| `house-price` | MAE | tabular | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/house-price/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/house-price/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/ffbb5c48-5c4c-53c8-a2bf-e369a57229c9) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/d2d85227-fa3b-5489-a577-7e08d8d26212) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/tree/main/datasets/mlab-protocol/house-price/environment/data) | [train.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/house-price/environment/data/train.py) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/house-price/tests/score.py) | Kaggle `house-prices-advanced-regression-techniques` |
| `spaceship-titanic` | accuracy | tabular | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/spaceship-titanic/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/spaceship-titanic/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/506e781c-cb54-5fd4-8df6-811113b6341d) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/bf69cafc-cfea-5f38-bd01-c8eaa8498807) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/tree/main/datasets/mlab-protocol/spaceship-titanic/environment/data) | [train.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/spaceship-titanic/environment/data/train.py) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/spaceship-titanic/tests/score.py) | Kaggle `spaceship-titanic` |
| `amp-parkinsons` | SMAPE | tabular | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/amp-parkinsons/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/amp-parkinsons/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/48232752-c806-50ce-92e6-775ae4c18636) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/7af312c9-0b00-5013-b238-ee31a65520af) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/tree/main/datasets/mlab-protocol/amp-parkinsons/environment/data) | [train.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/amp-parkinsons/environment/data/train.py) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/amp-parkinsons/tests/score.py) | Kaggle `amp-parkinsons-disease-progression-prediction` |
| `feedback` | MCRMSE | nlp | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/feedback/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/feedback/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/b321b961-b7f7-506c-810c-12cc599c3b7e) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/e33032cb-5d88-533d-a754-0bcd42d7f637) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/tree/main/datasets/mlab-protocol/feedback/environment/data) | [train.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/feedback/environment/data/train.py) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/feedback/tests/score.py) | Kaggle `feedback-prize-english-language-learning` |
| `imdb` | accuracy | nlp | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/imdb/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/imdb/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/75f2a81f-e742-5bc8-a084-672280c2c3c3) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/2ca5f2cb-d92d-552f-97a6-bd2fe59a1938) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/tree/main/datasets/mlab-protocol/imdb/environment/data) | [train.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/imdb/environment/data/train.py) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/imdb/tests/score.py) | HuggingFace `imdb` (plain_text, rev e628166), официальный сплит |
| `cifar10` | accuracy | vision | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/cifar10/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/cifar10/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/b2eedf2c-abfd-5279-a0d3-1fd439397f09) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/52088e7c-6e82-5587-b7c6-176909c9fdde) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/tree/main/datasets/mlab-protocol/cifar10/environment/data) | [train.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/cifar10/environment/data/train.py) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/cifar10/tests/score.py) | CIFAR-10, `cifar-10-python.tar.gz`, официальный сплит |
| `fathomnet` | MAP@20 | vision | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/fathomnet/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/fathomnet/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/118161e6-2941-5508-865a-03399e5c1599) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/ee6c6963-1d12-5edd-a9a5-aba07d8e28b8) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/tree/main/datasets/mlab-protocol/fathomnet/environment/data) | [train.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/fathomnet/environment/data/train.py) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/fathomnet/tests/score.py) | разметка — Kaggle `fathomnet-out-of-sample-detection`; изображения — API fathomnet.org |
| `identify-contrails` | Dice | vision | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/identify-contrails/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/identify-contrails/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/e6ec3514-b89f-510e-be1e-957a2b8c8599) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/ed5a1456-4b18-50ac-be0b-508d45c6ff89) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/tree/main/datasets/mlab-protocol/identify-contrails/environment/data) | [train.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/identify-contrails/environment/data/train.py) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/identify-contrails/tests/score.py) | Kaggle `google-research-identify-contrails-reduce-global-warming` |
| `ogbn-arxiv` | accuracy | graph | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/ogbn-arxiv/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/ogbn-arxiv/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/e6873fbb-63cd-55f4-b88f-a27f83400db4) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/7d999399-690f-5328-b3fd-55c91b9c020c) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/tree/main/datasets/mlab-protocol/ogbn-arxiv/environment/data) | [train.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/ogbn-arxiv/environment/data/train.py) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/ogbn-arxiv/tests/score.py) | OGB `ogbn-arxiv` |
| `clrs` | pointer accuracy | graph | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/clrs/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/clrs/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/db6b647a-f6bd-54d1-a02b-1535aff4e0a7) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/f368257e-624c-595e-b4da-de6af484feae) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/tree/main/datasets/mlab-protocol/clrs/environment/data) | [train.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/clrs/environment/data/train.py) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/clrs/tests/score.py) | сгенерировано официальным сэмплером `dm-clrs` |

## TabReD — 8 задач

Репозиторий бенчмарка отдаёт данные, официальные временные сплиты и `info.json` — и ничего не говорит агенту о том, что делать. Стартового скрипта нет, задачи решаются с нуля. Все восемь — табличные.

| задача | метрика | baseline-промпт | промпт C1 | прогон AutoDS | прогон baseline | данные | скорер |
|---|---|---|---|---|---|---|---|
| `homecredit-default` | ROC-AUC | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/homecredit-default/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/homecredit-default/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/900e20ae-bda0-56b2-896b-17107a421588) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/6b726609-ce20-509a-aef9-32e09dadf31a) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/tree/main/datasets/tabred-real/homecredit-default/environment/data) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/homecredit-default/tests/score.py) |
| `homesite-insurance` | ROC-AUC | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/homesite-insurance/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/homesite-insurance/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/cb19f843-0505-5835-8abe-d646429fedf9) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/7c6cdff8-781e-5f03-a50b-9f170f112c33) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/tree/main/datasets/tabred-real/homesite-insurance/environment/data) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/homesite-insurance/tests/score.py) |
| `ecom-offers` | ROC-AUC | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/ecom-offers/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/ecom-offers/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/0d74b867-1390-5d16-b59d-b108e8bb5fca) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/8dee1fae-c458-5bf3-8aa0-d4c69c05b4c0) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/tree/main/datasets/tabred-real/ecom-offers/environment/data) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/ecom-offers/tests/score.py) |
| `weather` | RMSE | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/weather/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/weather/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/6b033321-de03-533e-9eea-252feae4a333) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/9ab17ca8-fd7b-533b-b50d-87482afa8014) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/tree/main/datasets/tabred-real/weather/environment/data) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/weather/tests/score.py) |
| `maps-routing` | RMSE | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/maps-routing/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/maps-routing/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/e8df9aa0-a5b1-5179-86dc-7a33354d1147) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/dda6aba0-5145-5b51-85bc-a577733810ef) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/tree/main/datasets/tabred-real/maps-routing/environment/data) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/maps-routing/tests/score.py) |
| `cooking-time` | RMSE | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/cooking-time/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/cooking-time/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/1f870f75-2156-54c6-8fc8-d1745b5385a5) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/20659df8-7d81-5943-b8c3-01c56aefc4a4) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/tree/main/datasets/tabred-real/cooking-time/environment/data) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/cooking-time/tests/score.py) |
| `delivery-eta` | RMSE | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/delivery-eta/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/delivery-eta/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/42986e70-11b6-556a-9012-1000946b9e8b) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/cd67ac5c-25b7-5106-b220-2881013691b5) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/tree/main/datasets/tabred-real/delivery-eta/environment/data) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/delivery-eta/tests/score.py) |
| `sberbank-housing` | RMSE | [instruction.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/sberbank-housing/instruction.md) | [instruction_c1.md](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/sberbank-housing/instruction_c1.md) | [трасса](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3/trials/c5ab100d-3170-5b11-babf-ef5444798345) | [трасса](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d/trials/7cf27551-1d11-5863-bda2-ea19ba3b46de) | [data/](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/tree/main/datasets/tabred-real/sberbank-housing/environment/data) | [score.py](https://huggingface.co/datasets/danil-e/harbor-datasets-tabred/blob/main/datasets/tabred-real/sberbank-housing/tests/score.py) |

Источник всех восьми — репозиторий TabReD (данные Яндекса и соревнования Kaggle, перечисленные там же): `homecredit-default`, `homesite-insurance`, `sberbank-housing` происходят из соревнований Kaggle, остальные пять — из продуктовых данных Яндекса.

## Устройство задачи

Одинаково во всех 18 случаях:

```
<задача>/
  instruction.md              постановка (её и видит baseline)
  instruction_c1.md           та же постановка + слой C1 (её видит AutoDS)
  environment/data/           данные; у MLAgentBench здесь же стартовый train.py
  environment/prepare.py      раскладывает данные в рабочий каталог при сборке
  environment/Dockerfile      сборка от python:3.12-slim, без внешних образов
  tests/score.py              скорер
  task.toml                   конфиг задачи Harbor
```
Ключ (`answer.csv` / `answer.npz`) лежит в репозитории рядом с данными, но **в рабочий каталог агента не попадает**: `prepare.py` кладёт его в `/opt/mlab`, откуда его читает только скорер. Точка входа для запуска — `registry.json` в корне репозитория.

## Состав данных

Числа посчитаны по самим файлам. У MLAgentBench в `environment/data/` лежит ещё `train.py` — стартовый скрипт; у четырёх задач там же `task_descriptor.txt` из репозитория бенчмарка. **Имена файлов различаются между бенчмарками**: MLAgentBench отдаёт `train.csv` / `test.csv`, TabReD — `train_full.csv` / `test_full.csv`.

| задача | тип | обучение | тест | признаков | цель | посылка | файлы данных | объём |
|---|---|---|---|---|---|---|---|---|
| `amp-parkinsons` | регрессия, 4 цели | 2056 | 559 | 3 | `updrs_1, updrs_2, updrs_3, updrs_4` | `visit_id, updrs_1, updrs_2, updrs_3, updrs_4` | `answer.csv`, `task_descriptor.txt`, `test.csv`, `train_clinical_data.csv`, `train_peptides.csv`, `train_proteins.csv` | 59 МБ |
| `cifar10` | классификация, 10 классов | 50000 | 10000 | 1 | `label` | `id, label` | `answer.csv`, `test.csv`, `test_images.npy`, `train.csv`, `train_images.npy` | 185 МБ |
| `clrs` | предсказание указателей на графе | 10000 графов по 16 вершин | 1000 графов по 64 | матрица смежности + позиция | `Pi` | `graph_id, row, pointers` | `answer.npz`, `test.npz`, `train.npz` | 12 МБ |
| `fathomnet` | multi-label, список категорий | 1799 | 450 | 1 | `categories` | `id, categories` | `answer.csv`, `images/`, `task_descriptor.txt`, `test.csv`, `train.csv` | 4900 МБ |
| `feedback` | регрессия, 6 целей | 3128 | 783 | 2 | `cohesion, syntax, vocabulary, phraseology, grammar, conventions` | `text_id, cohesion, syntax, vocabulary, phraseology, grammar, conventions` | `answer.csv`, `task_descriptor.txt`, `test.csv`, `train.csv` | 9.3 МБ |
| `house-price` | регрессия | 1168 | 292 | 80 | `SalePrice` | `Id, SalePrice` | `answer.csv`, `test.csv`, `train.csv` | 0.5 МБ |
| `identify-contrails` | сегментация, RLE | 123 | 32 | 1 | `rle` | `record_id, rle` | `answer.csv`, `task_descriptor.txt`, `test.csv`, `test/`, `train.csv`, `train/` | 215 МБ |
| `imdb` | бинарная классификация текста | 25000 | 24877 | 2 | `label` | `id, label` | `answer.csv`, `test.csv`, `train.csv` | 66 МБ |
| `ogbn-arxiv` | классификация вершин, 40 классов | 90941 | 10000 | 1 | `label` | `id, label` | `answer.csv`, `edges.npy`, `node_features.npy`, `test.csv`, `train.csv` | 106 МБ |
| `spaceship-titanic` | бинарная классификация | 6954 | 1734 | 12 | `Transported` | `PassengerId, Transported` | `answer.csv`, `test.csv`, `train.csv` | 0.7 МБ |
| `cooking-time` | регрессия | 40000 | 10000 | 194 | `target` | `id, target` | `answer.csv`, `test_full.csv`, `train_full.csv` | 96 МБ |
| `delivery-eta` | регрессия | 40000 | 10000 | 225 | `target` | `id, target` | `answer.csv`, `test_full.csv`, `train_full.csv` | 95 МБ |
| `ecom-offers` | бинарная классификация | 40000 | 10000 | 121 | `target` | `id, target` | `answer.csv`, `test_full.csv`, `train_full.csv` | 26 МБ |
| `homecredit-default` | бинарная классификация | 40000 | 10000 | 698 | `target` | `id, target` | `answer.csv`, `test_full.csv`, `train_full.csv` | 143 МБ |
| `homesite-insurance` | бинарная классификация | 40000 | 10000 | 301 | `target` | `id, target` | `answer.csv`, `test_full.csv`, `train_full.csv` | 63 МБ |
| `maps-routing` | регрессия | 40000 | 10000 | 988 | `target` | `id, target` | `answer.csv`, `test_full.csv`, `train_full.csv` | 519 МБ |
| `sberbank-housing` | регрессия | 23674 | 4647 | 394 | `target` | `id, target` | `answer.csv`, `test_full.csv`, `train_full.csv` | 68 МБ |
| `weather` | регрессия | 40000 | 10000 | 105 | `target` | `id, target` | `answer.csv`, `test_full.csv`, `train_full.csv` | 44 МБ |

У `cifar10` признак в `train.csv` — ссылка на строку в `train_images.npy`; у `ogbn-arxiv` — в `node_features.npy` (плюс `edges.npy`); у `fathomnet` — имя файла в `images/`; у `identify-contrails` — каталог `train/` или `test/` с тремя `.npy` на запись. Поэтому в столбце «признаков» у них стоит 1.

## Система и запуск

| | |
|---|---|
| Harbor — среда запуска | https://www.harborframework.com |
| каталог задач Harbor | https://hub.harborframework.com/datasets |
| AutoDS, основной репозиторий | https://github.com/AaLexUser/AutoDS-Tools |
| AutoDS, форк с адаптером Harbor | https://github.com/florentiner/AutoDS-Tools (ветка `mlab-gpu-pub`) |

Все 18 задач опубликованы на хабе Harbor: `hub.harborframework.com/tasks/mlab/<задача>` и `.../tasks/tabred/<задача>`.

**Осторожно с версией слоя C1.** В форке на GitHub сейчас лежит предыдущая редакция `c1_prompt.py`: в ней остались две подсказки, написанные под конкретные задачи — маскирование недостижимых кандидатов для указателей CLRS и замечание о том, что SMAPE максимально штрафует ненулевой прогноз против нулевой цели. Обе убраны как знание о тестовой выборке внутри воздействия; вторая порождала константную посылку, которая выигрывала по SMAPE, ничего не моделируя. Метрики считались на версии **без** них — она опубликована здесь: [c1_prompt.py](https://huggingface.co/datasets/danil-e/harbor-datasets-mlab/blob/main/datasets/mlab-protocol/c1_prompt.py).

Все 36 прогонов, стоящие за таблицей статьи, выложены на хаб Harbor двумя job'ами по 18 испытаний: [ветка AutoDS](https://hub.harborframework.com/jobs/3113aba7-1a4b-5319-9777-2c6717635bc3) и [ветка baseline](https://hub.harborframework.com/jobs/56768b37-f841-5678-8fc8-c2af1a45af7d). В `PAPER_FINAL_all_tasks.csv` колонки `run_Autods` и `run_baseline` ведут на конкретное испытание. Каждое несёт трассу в формате ATIF, посылку, вывод скорера и все метрики.

Прогоны шли локально, без выгрузки на хаб, и их job-каталоги не сохранились. Опубликованное собрано из уцелевших артефактов: награда — из `reward.json` скорера, токены и стоимость — из `final_metrics` трассы, посылка и лог — из прогона, время — из отметок файлов, контрольная сумма задачи посчитана тем же `dirhash(sha256)`. Отметки времени отдельных шагов и разбивка испытания на фазы в прогонах не записывались и оставлены пустыми. Тип окружения в схеме Harbor не имеет значения для локального запуска и записан как `null` — так же, как Harbor писал его для собственных локальных job'ов.

Вытесненные попытки — те, что переделывались после найденного дефекта, — не выкладывались; опубликован только прогон, давший опубликованное число.

## Первоисточники

| | |
|---|---|
| MLAgentBench, репозиторий | https://github.com/snap-stanford/MLAgentBench |
| MLAgentBench, статья | https://arxiv.org/abs/2310.03302 |
| TabReD, репозиторий | https://github.com/yandex-research/tabred |
| TabReD, статья | https://arxiv.org/abs/2406.19380 |
| CLRS, генератор | https://github.com/google-deepmind/clrs |

Метрика каждой задачи взята из самого бенчмарка — `MLAgentBench/benchmarks/<task>/scripts/eval.py` и `tabred/data/<task>/info.json`, — а не из соответствующего соревнования Kaggle.

## Оговорки к данным

- `identify-contrails` — 155 записей из ~22385, 3 кадра из 8, float16: абсолютный Dice несопоставим с таблицей соревнования.
- `fathomnet` — подмножество ~38%. Метрика бенчмарка — (нормированный out-of-sample AUC + MAP@20)/2, но его `eval.py` заполняет колонку osd случайными числами, поэтому осмысленна только MAP@20; она и приведена.
- `imdb` и `spaceship-titanic` — удалены строки, дублирующиеся между train и test (123 и 5 соответственно).
- `ogbn-arxiv` — граф отдан целиком (169343 вершины, 1166243 ребра); размечены и используются для обучения и оценки 100941 строка, все 40 классов.
- `clrs` — обучение на графах из 16 вершин, проверка на графах из 64: это проверка обобщения на больший размер, как её ставит сам бенчмарк.
- TabReD — подвыборки официальных временных сплитов; хронология сохранена, доля положительного класса и среднее таргета отклоняются от оригинала не более чем на 2.8%. У `sberbank-housing` тестовый сплит взят целиком, все 4647 значений совпадают с оригиналом.

## Чего в репозиториях нет

Опубликованы задачи и промпты обеих веток — этого достаточно, чтобы воспроизвести сравнение любым Harbor-агентом. Код самой системы AutoDS и скрипты запуска кампании в этих репозиториях не лежат; из агентного кода опубликован только `c1_prompt.py` — то единственное, что отличает ветки.

## Трейсы Terminus 2: что агент выбрал сам

`TERMINUS2_trace_evidence.csv` — извлечение из трейсов Harbor Hub: какую модель
агент реально обучил, что доустановил в образ, искал ли гиперпараметры и какие
константы прописал руками. Задача в инструкции библиотеку не называет («train and
validate any model you choose»), поэтому выбор — собственный.

Итог по восьми задачам TabReD: градиентный бустинг на 8 из 8 (LightGBM на семи,
XGBoost вместе с `HistGradientBoostingRegressor` на восьмой), на шести LightGBM
агент доустанавливал сам в штатный образ. Поиска гиперпараметров нет ни в одном
трейсе; на семи задачах прописаны одни и те же `learning_rate=0.05` и
`n_estimators=1000`, на семи — ранняя остановка по отложенной выборке.

Два результата на MLAgentBench оказались вырожденными:

| задача | что в сабмите | как оценено |
|---|---|---|
| `imdb` | одна и та же метка на всех 25 000 строк | accuracy ровно 0.5000, проверки на константу у скорера нет |
| `amp-parkinsons` | 344 из 559 строк (61.5%) — одно и то же глобальное значение по каждой из 4 целей | SMAPE 66.35 |

### Как воспроизвести

```bash
harbor hub job trials 1a42d1fe-a3e1-4fa5-a3d4-e5338ae3ff08   # MLAgentBench, Terminus 2
harbor hub job trials 7593cc7b-8b7e-4e5b-87c4-1c1f18527fa7   # TabReD, три попытки
harbor hub trial download <trial-id> -o trials               # трейс, сабмит, reward.json
```

Полные значения наград в `<trial>/verifier/reward.json` совпадают с числами в
`MASTER_all_systems.csv` до последнего знака — сверено по всем восьми задачам
TabReD.

## Сверка чисел с артефактами (28.08.2026)

Каждое число, у которого есть прогон на Harbor Hub, сверено с
`<trial>/verifier/reward.json`:

| набор | что сверено | итог |
|---|---|---|
| Terminus 2, TabReD | 8 задач | совпало до последнего знака |
| AutoDS, TabReD, обе ветки | 16 значений | совпало до последнего знака |
| AutoDS, MLAgentBench, обе ветки | 20 значений | 18 совпали, 2 исправлены |

Исправление: у `fathomnet` скорер выдаёт **micro-F1**, а не MAP@20. В артефактах
0.030004 (ветка C1) против 0.167592 (baseline); прежние значения 0.0596 / 0.6933
в прогонах не встречаются. Знак эффекта не изменился, величина уменьшилась.

FEDOT.LLM, TabReD: сверено 22.09.2026. Восемь заданий на Harbor Hub от
14.08.2026 (по одному трайлу на задачу, ссылки в таблице ниже), `reward.json`
прочитаны при полной точности и внесены в `AGENTS` в `paper/make_tables.py`;
прежние значения с двумя знаками совпадают с округлением. Нормированное среднее
0.26 → 0.31, средний ранг 18.2 → 18.4 из 21 (округление вниз по RMSE давало
заниженную нормировку). Конфигурация по логам: агент
`harbor_adapter.agent:FedotLLMHarborAgent` (монорепозиторий FEDOT.LLM, FedotAI),
бэкенд FEDOT с бюджетом AutoML 1.0 мин, без тюнинга, набор моделей {lgbm}:
итоговый пайплайн во всех восьми трайлах один узел LightGBM. Трайлы 4.5–16.5
мин, $0.003–0.021.

| задача | job |
|---|---|
| homesite-insurance | 246ee034-209d-4ac8-a9eb-2844219306a3 |
| ecom-offers | 565794be-101b-437a-9cc2-2786ad685371 |
| homecredit-default | a16da5cf-8392-4d11-bf8f-b08746667d9f |
| sberbank-housing | b4bba467-d214-459f-9954-6b944e180a44 |
| cooking-time | b9b40419-daf6-4193-af5b-884200b88c08 |
| delivery-eta | 9b4c06e7-e346-47cc-ad24-db5f7a19f7e5 |
| maps-routing | bfb46c3d-7932-42d6-8c8c-1c6405007dfa |
| weather | 337976c3-7c31-4886-a833-9fa59ec5114f |

## Научные кейсы: инструкции с максимальным предписанием

Инструкции трёх кейсов (`agent/instruction.md` в трейлах
`58ed21ad`, `edf0f88f`, `433a969c`) — не «чистое» условие. В каждой есть раздел
**Specialized library to use — REQUIRED**: названа библиотека, дан рабочий
фрагмент кода, перечислены протекающие колонки, описан дизайн сплита и прямо
указан авторский бейзлайн как цель. В полимерном кейсе вдобавок пересказан сам
опубликованный результат — Morgan-фингерпринты радиуса 2 на 2048 бит плюс
градиентный бустинг.

Поэтому кейсы читаются как дальний конец оси предписанного знания, а не как
работа агента без подсказок. Полные метрики из `verifier/reward.json`:

| кейс | что говорит одна метрика | что говорят остальные |
|---|---|---|
| maize | Pearson r 0.5686 против 0.461 у авторов | norm. RMSE 0.9577 против 0.948 — по ошибке агент хуже; R² 0.0828, n=4240 |
| fdata | accuracy 0.9207 против 0.89 | мажоритарный класс даёт 0.8808; balanced accuracy 0.7054, n=23396 |
| openpoly | R² 0.543 против 0.904 | MAE 40.4 K против 14.56 K, тест всего n=89, датасет неполный |

## Перепрогон AutoDS на общем адаптере (28.08.2026)

24 испытания, 8 задач × 3 попытки, `google/gemma-4-31b-it`, 7 ч 36 мин,
$0.244, 2 124 851 входных и 154 403 выходных токенов. Данные и скореры те же,
что у Terminus 2 и FEDOT.LLM, поэтому строки сопоставимы напрямую.

Два испытания из двадцати четырёх упёрлись в потолок задачи `timeout_sec = 3600`
и были убиты, не успев записать `predictions.csv`: `homecredit-default` и
`maps-routing`. Они **исключены из средних**, а не усреднены как нули. Разница
принципиальная: усреднение нуля дало бы по `homecredit-default` 0.575 вместо
0.863 и уронило бы систему с третьего места на предпоследнее — то есть отказ
инфраструктуры выглядел бы как качество модели.

Длительности всех испытаний, минуты:

```
60.1*  60.0*  52.4  52.2  51.4  47.3  46.6  44.3  43.5  43.2  39.8  36.6
36.6   35.6   28.7  26.5  26.2  24.0  21.9  19.4  18.4  18.3  17.1
* убито таймаутом
```

Пять испытаний из двадцати трёх завершились в пределах пятнадцати минут от
потолка. Terminus 2 на тех же задачах и при том же лимите тратит около пяти
минут. Это цена архитектуры, измеренная во времени, а не в токенах.

Старые строки AutoDS по TabReD в `MASTER_all_systems.csv` оставлены: они помечены
как несопоставимые, и разница между ними и новыми — это измеренная цена
подготовки данных.


## AutoDS-Tools, основной прогон на сервере (28.08.2026, 15:17)

`runs/autods-tabred/jobs/autods-tabred-full-20260828-151739/` — 24 испытания,
8 задач по 3 попытки, 4 ч 26 мин при параллельности 4 на nss-calc2 (18 ядер,
96 ГБ, без GPU). Это основной прогон AutoDS-Tools: он идёт на исправленном
образе (с `libgomp1`) и делит этот образ с остальными ячейками сетки
`nolayer` / `libonly` / `disconly`, поэтому сравнение внутри сетки не
осложнено разницей окружений.

Отпечаток слоя подтверждён до запуска и после: 4972 символ, sha
`a58b4d40678ff1aa` — тот же, что во всех прогонах статьи.

Итоги из `jobs/*/result.json`: входных токенов 1 478 567, выходных 128 387,
стоимость $0.176723. Четыре испытания срезаны потолком 3600 с; три из них уже
успели записать сабмит и оценены наравне с прочими, четвёртое
(`homesite-insurance__y2ZxWwj`) — нет, и исключено из средних.

Длительности всех испытаний, минуты:

```
66.2* 63.1* 62.4* 61.2* 58.6  57.1  49.1  46.0  41.4  40.2  39.7  39.6
38.2  36.7  35.4  35.0  34.2  32.2  32.0  28.3  27.9  19.9  19.3  18.7
* срезано потолком; из этих четырёх три оценены, одно потеряно
```

Медиана 38.9, среднее 40.9. Измерение идёт от `started_at` в `result.json` до
времени изменения `verifier/reward.json`, поэтому у срезанных испытаний оно
включает работу проверяющего и выходит за 60 минут.

Сверка с прогоном на рабочей станции (`autods-tabred-full-20260828-014230`,
12 ядер, параллельность 2, образ без `libgomp1`): семь задач из восьми
расходятся не более чем на 0.13%, восьмая (`sberbank-housing`) на 0.34%.
Медианы времени 37.4 и 38.9 минуты. Иначе говоря, ни машина, ни удвоение
параллельности, ни починка образа на ходу заметно не сдвинули результат.
Сдвинулась доля потерь: 2 испытания из 24 против 1 из 24.

## Починка среды агентами

В образе не хватало системной библиотеки `libgomp1`: LightGBM импортировался,
а падал позже, внутри `fit_predict`, как развалившийся пул joblib — то есть
выглядел как ошибка моделирования, каковой не был.

Отказ затронул 45 испытаний: 22 из 24 у AutoDS-Tools (прогон 01:42) и 23 из 24
у Terminus-2 на обогащённом образе. Все 45 распознали причину и поставили
`libgomp1` через `apt-get`, после чего продолжили. Проверка:

```
grep -rl 'libgomp.so.1: cannot open' jobs/<задание>     # затронутые испытания
grep -rlE 'apt-get[^\n]{0,80}libgomp' jobs/<задание>    # починившие
```

Ни одно испытание не отказалось от библиотеки и ни одно не отразило починку
в итоговом отчёте. Отсюда вывод для §6: наше обеспечение среды бездействует как
воздействие не потому, что агент его не замечает, а потому, что агент
достраивает среду сам.

## Terminus-2 на обогащённом образе (прогон 28.08.2026)

`runs/autods-tabred/jobs/terminus-matched-20260828-105709/` — 24 испытания,
8 задач по 3 попытки, 52 минуты, тот же образ контейнера, что у AutoDS.
Метрика каждой строки читается из `<испытание>/verifier/reward.json`.

Что этот прогон изолирует: обычные прогоны Terminus-2 шли на штатном образе, а
AutoDS — на образе с предустановленными LightAutoML, featuretools и
feature-engine. Пара «штатный / обогащённый» при неизменных агенте, задачах и
срезах данных отделяет подготовку среды от архитектуры.

Итог: семь задач из восьми внутри собственного порога шума системы (0.94%),
средний собственный разброс 0.046%. Восьмая, `sberbank-housing`, отклоняется на
−3.49%, но две попытки из трёх точно воспроизводят штатные значения, а третья
обучала тысячу деревьев без ранней остановки.

Ни одно из 24 испытаний не упомянуло ни одну из трёх предустановленных
библиотек: `grep -ril 'lightautoml\|featuretools\|feature.engine'` по каталогам
`*/agent/` даёт ноль.

Оговорка: в образе не хватало системной библиотеки `libgomp1` — см. раздел
«Починка среды агентами». Отказ затронул 23 испытания из 24, и все 23 поставили
библиотеку сами. На вывод это не влияет: он держится на том, что агент вовсе не
называл предустановленные библиотеки, а не на том, работали ли они. Прогон
не переснимался; образ исправлен, и все последующие ячейки идут на нём.

## Сетка 2×2 по половинам слоя (28–29.08.2026)

Четыре ячейки по 24 испытания, один образ (с `libgomp1`), параллельность 4,
одна машина nss-calc2. Ячейки различаются только файлом задания.

| ячейка | задание | флаг | наград | потеряно |
|---|---|---|---|---|
| обе половины | `autods-tabred-full-20260828-151739` | — | 24 | 1 |
| только библиотеки | `autods-tabred-libonly-20260828-213712` | `AUTODS_K_DISC_DISABLED=1` | 24 | 0 |
| только дисциплина | `autods-tabred-disconly-20260829-010054` | `AUTODS_K_TOOL_DISABLED=1` | 24 | 0 |
| ничего | `autods-tabred-nolayer-20260828-194654` | `AUTODS_C1_DISABLED=1` | 24 | 0 |

Отсутствие слоя в ячейке `nolayer` проверено по существу, а не по строке
журнала: `instruction.md` в её испытаниях 1040–1076 символов против примерно
6000 при включённом слое (базовое задание около 1050 плюс слой 4972).

Ячейки запускались подряд скриптом `chain.sh` на сервере, чтобы параллельность
и образ совпадали: параллельность входит в измерение, а не является настройкой
удобства.

### Точность

Отклонение от ячейки «ничего», в процентах, знак приведён так, что плюс — лучше:

| задача | только библиотеки | только дисциплина | обе |
|---|---|---|---|
| homesite-insurance | +0.10 | −0.03 | +0.12 |
| ecom-offers | +3.68 | +1.24 | +2.67 |
| homecredit-default | +0.79 | +0.20 | +0.86 |
| sberbank-housing | −0.31 | −0.00 | +0.07 |
| cooking-time | +0.47 | −0.04 | +0.30 |
| delivery-eta | −0.00 | −0.05 | +0.04 |
| maps-routing | +0.64 | +0.09 | +0.45 |
| weather | +0.14 | −0.41 | +1.24 |
| **среднее** | **+0.69** | **+0.12** | **+0.72** |
| лучше «ничего» | 6/8 | 3/8 | 8/8 |

Главные эффекты, усреднённые по задачам: библиотеки +0.64%, дисциплина +0.08%,
взаимодействие −0.09%.

### Время и деньги

| ячейка | медиана мин/испытание | $/испытание | вх. токенов | вых. токенов |
|---|---|---|---|---|
| ничего | 15.4 | 0.0086 | 1 670 177 | 164 297 |
| только библиотеки | 30.4 | 0.0074 | 1 453 024 | 135 638 |
| только дисциплина | 9.7 | 0.0095 | 1 909 899 | 167 440 |
| обе | 38.9 | 0.0074 | 1 478 567 | 128 387 |

Предписанная библиотека сокращает перебор и удлиняет обучение; предписанная
дисциплина наоборот.

### Проверка воздействия

`discipline.py jobs` по трассам каждой ячейки:

| требование | ничего | библиотеки | дисциплина | обе |
|---|---|---|---|---|
| сравнить с тривиальным предсказанием | 0/24 | 0/24 | 24/24 | 20/20 |
| распланировать время | 0/24 | 0/24 | 24/24 | 20/20 |
| выбрать лучший вариант по валидации | 0/24 | 2/24 | 24/24 | 20/20 |
| осмотреть результат перед сдачей | 22/24 | 22/24 | 24/24 | 20/20 |
| ранняя остановка | 24/24 | 0/24 | 24/24 | 10/20 |

Три первых требования переключаются с нуля на сто процентов ровно тогда, когда
включена половина «дисциплина», и никогда иначе.

Две последние строки ничего не разделяют, и обе объясняют, почему прежняя
таблица §7 вводила в заблуждение. «Осмотреть результат» AutoDS делает и без
предписания (22/24) — это свойство архитектуры; Terminus-2 не делает никогда
(0/24). «Ранняя остановка» при включённой библиотеке исчезает из трассы, потому
что предписанная библиотека делает её внутри себя и не сообщает об этом.
Размер ячейки «обе» равен 20, а не 24: испытание, срезанное потолком, трассы не
пишет.

## Нижняя граница пригодности бэкбона (29.08.2026)

Ось бэкбона задумывалась как `gemma-3-12b-it` внизу, `gemma-4-31b-it`
посередине, `z-ai/glm-4.7` наверху. Нижняя точка оказалась непригодна, и это
измерено, а не предположено.

Прямая проверка вызова инструмента (три попытки на модель, обязательное поле
`cmd` в схеме):

| модель | аргументы заполнены |
|---|---|
| google/gemma-3-12b-it | 0/3 |
| google/gemma-3-27b-it | 3/3 |
| google/gemma-4-26b-a4b-it | 3/3 |
| qwen/qwen-2.5-72b-instruct | 3/3 |
| meta-llama/llama-3.1-70b-instruct | 1/3 |
| google/gemma-4-31b-it | 3/3 |

`gemma-3-12b-it` выдаёт вызов инструмента с пустым объектом аргументов
(`run_shell {}`), то есть обязательное поле не заполняется. Модель заявлена
как поддерживающая `tools` и `tool_choice`, поэтому по объявлению это не видно.

Пробные испытания на `cooking-time` подтвердили последствие и показали, что оно
зависит от обвязки:

| система | модель | итог | время |
|---|---|---|---|
| AutoDS-Tools | gemma-3-12b-it | `reward 0.0`, таймаут, трасса не записана | 63 мин |
| Terminus-2 | gemma-3-12b-it | `reward 0.0` | 4 мин |

Одна и та же неспособность проявляется по-разному: система, работающая через
вызов инструментов, зависает до потолка задачи, система, работающая через
терминал, быстро сдаёт негодный результат. Для сравнения систем это существенно
— обвязка определяет, во что превращается отказ модели, в потерянный час или в
плохую оценку.

Нижняя точка оси заменена на `google/gemma-3-27b-it` ($0.08/$0.45): то же
семейство поколением раньше, заведомо слабее текущей модели и при этом
работоспособна. Задания: `jobs/autods-tabred-Msmall-smoke-20260829-125556`,
`jobs/terminus-tabred-Msmall-smoke-*`.

### Верхняя точка: сильная модель выводит тяжёлую обвязку за бюджет

Те же пробные испытания на `cooking-time` для `z-ai/glm-4.7`:

| система | модель | итог | время |
|---|---|---|---|
| Terminus-2 | gemma-4-31b-it | RMSE 0.483730 | ~5 мин |
| Terminus-2 | glm-4.7 | RMSE 0.483033 | 5 мин |
| AutoDS-Tools | gemma-4-31b-it | RMSE 0.482057 | ~35 мин |
| AutoDS-Tools | glm-4.7 | `reward 0.0`, таймаут | 63 мин |

`glm-4.7` — рассуждающая модель, и её выход почти целиком уходит в рассуждения,
которые тарифицируются как выходные токены. Замер по балансу ключа: одно часовое
испытание AutoDS на ней стоит около $0.77, то есть проход из 24 испытаний обошёлся
бы примерно в $18 против $0.18 на текущей модели.

Лёгкая обвязка от смены бэкбона не выигрывает (+0.14%, внутри собственного порога
шума 0.94%), тяжёлая перестаёт укладываться в часовой потолок задачи. Поэтому
верхняя точка AutoDS снята как одна попытка на каждую из восьми задач
(`axis-autods-1`), а не три: ожидается сплошной отказ, и три попытки утроили бы
стоимость ради того же вывода.

## Сверка отчётной стоимости с балансом ключа

Задания отчитываются полем `cost_usd` в `result.json`, которое считается по
`AUTODS_PRICE_INPUT_PER_1M` и `AUTODS_PRICE_OUTPUT_PER_1M`. Цены проверены
прямым запросом к OpenRouter (`usage.cost_details`): для `gemma-4-31b-it` это
ровно $0.09 и $0.34 за 1M, то есть константы верны.

Проверка проведена прямая: баланс ключа снят до и после одной изолированной
ячейки из 24 испытаний (`jobs/terminus-tabred-Msmall-20260829-175356`).

| | |
|---|---|
| баланс до | $28.7378 |
| баланс после | $29.6499 |
| фактически израсходовано | **$0.912** |
| отчитано в `result.json` | **$0.926350** |

Расхождение полтора процента, и оно объясняется тем, что второй замер снят
через секунду после конца ячейки. **Учёт стоимости исправен, числа в `tab:cost`
править не нужно.** Прежнее предположение о систематическом недоучёте снято:
оно строилось на сравнении с записью в `progress.md`, время которой не
установлено, а не на измерении.

### Стоимость зависит от бэкбона гораздо сильнее, чем результат

Входных токенов на испытание:

| прогон | вх/испытание | $/проход |
|---|---|---|
| Terminus-2, Hub 7593cc7b, gemma-4-31b | 49 969 | 0.1656 |
| Terminus-2, наша ветка, gemma-4-31b | 63 519 | 0.1053 |
| AutoDS, ячейка «обе», gemma-4-31b | 61 606 | 0.1767 |
| AutoDS, ячейка «ничего», gemma-4-31b | 69 590 | 0.2062 |
| **Terminus-2, gemma-4-26b-a4b** | **720 720** | **0.9264** |

Все прогоны на штатной модели согласуются между собой. Выбивается только смена
модели: на `gemma-4-26b-a4b-it` терминальный агент делает больше ходов
(испытание идёт 11 минут вместо 5), а входные токены растут с числом ходов
квадратично, поскольку каждый ход пересылает всю переписку. Точность при этом
не меняется. Смена бэкбона удорожает проход в 5.6 раза, не улучшая результат.

## Ось бэкбона, Terminus-2 (29.08.2026)

Три точки, по 24 испытания, параллельность 4, одна машина, один образ.
Задания: `terminus-tabred-Msmall-20260829-175356` (gemma-4-26b-a4b-it),
`terminus-tabred-Mmid-20260829-185941` (gemma-4-31b-it),
`terminus-tabred-Mlarge-20260829-192307` (z-ai/glm-4.7).

### Надёжность растёт с силой модели, точность — нет

| модель | отказов из 24 | вх. токенов на испытание | $/проход |
|---|---|---|---|
| gemma-4-26b-a4b | 6 (25.0%) | 720 720 | 0.9263 |
| gemma-4-31b | 2 (8.3%) | 37 317 | 0.0690 |
| glm-4.7 | 0 (0.0%) | 110 602 | 0.7615 |

Отказ здесь — испытание, не давшее метрики (сдан ноль либо ничего).

Средние по задачам (значение·число попыток с метрикой):

| задача | 26b-a4b | 31b | glm-4.7 |
|---|---|---|---|
| homesite-insurance | 0.958848·3 | 0.959566·3 | 0.954624·3 |
| ecom-offers | 0.567430·1 | 0.563585·3 | 0.604341·3 |
| homecredit-default | 0.854153·3 | 0.857289·3 | 0.852459·3 |
| sberbank-housing | 0.254195·3 | 0.250328·3 | 0.365072·3 |
| cooking-time | 0.483812·1 | 0.483718·3 | 0.483784·3 |
| delivery-eta | 0.547614·2 | 0.547847·3 | 0.552850·3 |
| maps-routing | 0.162790·3 | 0.162705·2 | 0.163378·3 |
| weather | 1.617088·2 | 1.523593·2 | 1.545516·3 |

Против штатной модели: `26b-a4b` в среднем −0.93% (медиана −0.06%, вне порога
шума 0.94% две задачи из восьми), `glm-4.7` в среднем −5.31% (медиана −0.54%,
вне порога три из восьми).

Оговорка о доле отказов: та же `gemma-4-31b` дала 8.3% здесь и 0% в ветке
`terminus-matched-20260828-105709` (локально, параллельность 2). Доля отказов
частично свойство развёртывания, поэтому сравнивать её можно только внутри
одного развёртывания, а абсолютную величину приводить нельзя.

### Смена знака воспроизводится сменой бэкбона

Разброс у `glm-4.7` не равномерный, а знакопеременный, и причина видна в
трассах. Сильная модель чаще отклоняется от градиентного бустинга:

| задача | что выбрал glm-4.7 | итог против 31b |
|---|---|---|
| sberbank-housing | случайный лес в 2 трассах из 3 | RMSE 0.3159–0.4195 против 0.2477–0.2516, −46% |
| ecom-offers | лучшая из трёх попыток — случайный лес | ROC-AUC 0.6269 против 0.554–0.569, лучший результат за всю работу |

Одно и то же отклонение помогает на одной задаче и вредит на другой. Это тот же
механизм, что выведен в §7 из включения и выключения слоя предписаний, но
полученный другим воздействием: текст не менялся, менялся бэкбон. Хорошие
табличные результаты лёгкой обвязки держатся не на качестве рассуждения, а на
том, что она надёжно берёт бустинг; модель, рассуждающая лучше, пользуется
большей свободой выбора, и свобода оказывается вредной чаще, чем полезной.

## Ось бэкбона, AutoDS-Tools (29–30.08.2026)

Задания: `autods-tabred-Msmall-20260829-201246` (gemma-4-26b-a4b-it, 24
испытания), `autods-tabred-full-20260828-151739` (gemma-4-31b-it, опора),
`autods-tabred-Mlarge-20260830-003247` (glm-4.7, 8 испытаний по одной попытке).

Верхняя ячейка сокращена сознательно: проба показала, что на `glm-4.7`
испытание упирается в потолок, и три попытки утроили бы счёт ради того же
вывода. Восемь испытаний дают утверждение про все восемь задач.

| ячейка | без метрики | срезано потолком | вх/исп | $/проход |
|---|---|---|---|---|
| gemma-4-26b-a4b | 6/24 (25.0%) | 7/24 (29%) | 123 374 | 0.3990 |
| gemma-4-31b (опора) | 1/24 (4.2%) | 4/24 (17%) | 61 606 | 0.1767 |
| glm-4.7 | 1/8 (12.5%) | 4/8 (50%) | 251 010 | 1.1005 |

Отказы и срезы растут в обе стороны от штатной модели. У Terminus-2 отказы
падают монотонно с ростом силы модели (25% → 8.3% → 0%). Две архитектуры
отвечают на усиление бэкбона противоположно: лёгкая обвязка становится
надёжнее, тяжёлая — менее надёжной, потому что тратит прибавку на ходы внутри
неизменного часового бюджета.

Точность там, где работа доходит до конца:

| задача | 26b-a4b | 31b | glm-4.7 |
|---|---|---|---|
| homesite-insurance | 0.959968·3 | 0.961118·2 | 0.961118·1 |
| ecom-offers | 0.579983·2 | 0.579992·3 | 0.579410·1 |
| homecredit-default | 0.859903·2 | 0.863282·3 | 0.853918·1 |
| sberbank-housing | 0.252292·3 | 0.251457·3 | **0.231021·1** |
| cooking-time | 0.482312·2 | 0.482025·3 | 0.481861·1 |
| delivery-eta | 0.547438·2 | 0.547391·3 | 0.547520·1 |
| maps-routing | 0.162112·2 | 0.161983·3 | отказ |
| weather | 1.479850·2 | 1.478262·3 | 1.511525·1 |

Медиана против опоры: `26b-a4b` −0.09%, `glm-4.7` −0.02%.

`sberbank-housing` на `glm-4.7` — лучший результат по этой задаче за всю работу
(RMSE 0.231021 против 0.251457). Ровно на этой задаче Terminus-2 с той же
моделью проваливается на 46%, взяв случайный лес. Соблазнительно объяснить это
тем, что предписание удерживает сильную модель в правильном семействе, но
**артефактов для такого утверждения нет**: у выигравшего испытания трасса не
записана (`autods.log` пуст, `trajectory.json` отсутствует), потому что оно было
срезано потолком, успев записать ответ. Измерена только оценка; механизм
остаётся догадкой и в статье как механизм не заявлен.

Трассы вообще есть не у всех: 4 из 8 в верхней ячейке, 17 из 24 в нижней, 20 из
24 в опорной — ровно у тех испытаний, которые не были срезаны.

## Выполнение требований дисциплины (`runs/autods-tabred/discipline.py`)

Считается по записям прогонов: `agent/terminus_2.pane` у Terminus-2 и
`agent/trajectory.json` у AutoDS. Для каждого из пяти требований блока
дисциплины ищется его текстовый след.

Без слоя подсказок (Terminus-2, 24 испытания) против со слоем (AutoDS, 22
испытания с записью):

| требование | без | со |
|---|---|---|
| ранняя остановка | 24/24 | 8/22 |
| сравнить с тривиальным предсказанием | 0/24 | 22/22 |
| осмотреть результат перед сдачей | 0/24 | 22/22 |
| распланировать время | 0/24 | 22/22 |
| выбрать лучший вариант по валидации | 0/24 | 22/22 |

Строку про раннюю остановку нельзя читать поперёк колонок: LightAutoML делает
её внутри и в запись не пишет. Остальные четыре сопоставимы: backbone, задачи и
образ одинаковы, различается только текст инструкции.

Метод ограничен: след означает, что поведение попало в запись, а не что оно
произошло; отсутствие следа значит ещё меньше.

---

## K_disc, скрещенный с Terminus-2 (30.08.2026, nss-calc2)

**Зачем.** Блок дисциплины оказался почти бесплатным и почти бесполезным внутри
той системы, для которой написан (+0.08% в сетке 2×2). Оставался вопрос, свойство
это текста или свойство архитектуры, которая его переваривает. Terminus-2 — самый
чистый контроль: у него нет своего слоя предписанного знания, поэтому обычный
прогон и есть ячейка «без блока».

**Как доставлен блок.** Слой AutoDS собирается на хосте и доходит только до
собственного агента, поэтому единственный честный способ дать тот же текст другой
системе — положить его в саму задачу. `runs/autods-tabred/make_kdisc_tasks.py`
читает `_DISCIPLINE` из установленного пакета (не из клона), копирует
`datasets/tabred` → `datasets/tabred-kdisc` и дописывает
`base.rstrip() + "\n\n" + disc` в каждый `instruction.md`.
Блок: **3678 символов, sha256 `22b138e8d5317eac`**. Задания выросли с 1040–1076
до 4720–4756 символов.

**Проверка воздействия.** Строка блока встречается в `agent/trajectory.json`
**24/24** испытаний обработанной ячейки и **0/24** необработанной. В `config.json`
обработанных стоит `"source": "tabred-kdisc"`.
Замечание для повторяющих: строка проверки в `kdisc.sh` искала блок в
`agent/*.md`, которого у Terminus-2 не бывает, и печатала 0 — это значит «файла
нет», а не «блока нет». Исправлено на `agent/trajectory.json`.

**Ячейки.** Обе на nss-calc2, один образ, один адаптер, модель
`openrouter/google/gemma-4-31b-it`, `HARBOR_CONCURRENCY=4`, по 24 испытания.
Отличие одно — блок в задании.

| | без блока | с блоком |
|---|---|---|
| задание | `terminus-tabred-Mmid-20260829-185941` | `terminus-kdisc-20260830-113531` |
| испытаний с метрикой | 22/24 | 11/24 |
| потеряно | 2 | 13 |
| таймаутов | 0 | 0 |
| медиана шагов агента | 6 | 18 |
| медиана минут на испытание | 2.5 | 14.1 |
| входных токенов | 895 620 | 12 064 534 |
| выходных токенов | 45 859 | 212 923 |
| цена прохода | $0.0690 | $0.7278 |
| цена испытания | $0.0029 | $0.0303 |

**Точность (среднее по попыткам, вернувшим метрику).**

| задача | метрика | без блока (n) | с блоком (n) | отн. % |
|---|---|---|---|---|
| homesite-insurance | ROC-AUC | 0.959566 (3) | 0.959449 (2) | −0.01 |
| ecom-offers | ROC-AUC | 0.563585 (3) | 0.564631 (3) | +0.19 |
| homecredit-default | ROC-AUC | 0.857289 (3) | 0.856682 (1) | −0.07 |
| sberbank-housing | RMSE | 0.250328 (3) | 0.251640 (1) | −0.52 |
| cooking-time | RMSE | 0.483718 (3) | 0.483327 (1) | +0.08 |
| delivery-eta | RMSE | 0.547847 (3) | 0.547815 (1) | +0.01 |
| maps-routing | RMSE | 0.162705 (2) | 0.162731 (2) | −0.02 |
| weather | RMSE | 1.523593 (2) | результата нет (0) | — |

Среднее по семи задачам, вернувшим число: **−0.05%**, на порядок внутри
собственного шума Terminus-2 (0.94%). Два значения совпадают с необработанными
до последней цифры: sberbank 0.251640 и homesite 0.958605. То есть выжившие
испытания решают задачу ровно так же, как без блока.

**Изменение доли потерь значимо:** 2/24 против 13/24, точный тест Фишера,
двусторонний **p = 0.0013**.

**Механизм потерь.** Ни одного таймаута и ни одного `exception.txt`. Все 13
потерянных испытаний заканчиваются вызовом `mark_task_complete` без
`/app/predictions.csv` (`verifier/test-stdout.txt`: `Missing required file:
/app/predictions.csv`). Так же заканчиваются и обе потери в ячейке без блока —
то есть блок не создаёт нового способа сломаться, а делает старый в шесть раз
вероятнее. В 5 из 13 агент прямо пишет, что терминал перестал показывать вывод
(`"the terminal output continues to echo commands without showing their
output"`), и на этом основании объявляет задачу выполненной; в хвостах
`agent/terminus_2.pane` у cooking-time и sberbank видно обучение в процессе
(`Epoch 20: Val RMSE = 1.2434`) на момент завершения испытания. То есть агент
запускает длинный fit на переднем плане, принимает молчащий терминал за поломку
отчётности, а не за незаконченную работу, и уходит.

**Почему именно длинный fit.** Текст блока (`_DISCIPLINE`, разделы `Training
discipline — REQUIRED` и `Time budget management — REQUIRED`) прямо требует:
«Assume you have hours, not minutes», «~100 epochs is a sane starting point»,
«if the whole training phase finished within a couple of minutes you almost
certainly undertrained: raise the epoch budget and train again». Медиана
необработанного испытания на этих задачах — 2.5 минуты, и она не недообучена:
это бустинг на табличных данных, а блок написан под свёрточные и энкодерные
модели.

**Смещение отбора.** Выжившие обработанные попытки — самые быстрые, поэтому
колонка точности смещена в пользу воздействия. То, что она всё равно ничего не
показывает, — консервативное прочтение.

**Контраст с AutoDS-Tools.** Тот же блок внутри своей архитектуры не стоил ни
одного испытания: в ячейке `disconly` 0 нулей из 24, таймаутов 0; нули
появляются только в ячейке `full` (1 ноль, 4 таймаута), где включена и половина
библиотеки.

| ячейка сетки 2×2 | наград | нулей | таймаутов |
|---|---|---|---|
| `autods-tabred-nolayer-20260828-194654` | 24 | 0 | 0 |
| `autods-tabred-libonly-20260828-213712` | 24 | 0 | 0 |
| `autods-tabred-disconly-20260829-010054` | 24 | 0 | 0 |
| `autods-tabred-full-20260828-151739` | 24 | 1 | 4 |

**В статье.** §7, подраздел «The same block in another architecture»
(`sec:kdiscterm`), таблица `tab:kdiscterm`. Список факторов в §5 приведён в
соответствие: K_disc скрещён на двух системах, не на трёх; K_tool — только на
AutoDS-Tools, у Terminus-2 нечего переключать.

### Ось бэкбона в нормированных единицах (закрывает pending во введении)

Нормировка та же, что в §6: 0 — слабейший из восемнадцати опубликованных
базовых методов на задаче, 1 — сильнейший; среднее по восьми задачам.

| система | gemma-4-26b-a4b | gemma-4-31b | glm-4.7 | размах |
|---|---|---|---|---|
| Terminus-2 | 0.690 | 0.735 | 0.500 | **0.235** |
| AutoDS-Tools | 0.831 | 0.848 | 0.873 (7 задач) | **0.042** |

Для сравнения, размах по архитектурам при фиксированном бэкбоне:
FEDOT.LLM 0.257, Terminus-2 0.719, AutoDS-Tools 0.848 → **0.591** (до
уточнения FEDOT.LLM 22.09; при полной точности 0.31 и размах 0.54).

Размах 0.235 у Terminus-2 держится на одной задаче: вклад
`sberbank-housing` в разницу glm-4.7 − gemma-4-31b равен −0.301 из −0.235,
без неё среднее по остальным семи двигается на **+0.066**. В статье это сказано
прямо, и во введении число подано как «не более 0.24, и без одной задачи 0.07».

Заодно исправлены два устаревших числа, оставшихся от подмены значений AutoDS
на серверные: §6 «spread of 0.58» → 0.59 и «0.84 for the multi-agent system» →
0.85 (в самом рисунке `fig_position` уже стояло 0.85).

### Поправка: длина слоя 4972, а не 4971

Отпечаток `a58b4d40678ff1aa` всегда считался по хвосту, который слой дописывает
к заданию, вместе с двумя переводами строки разделителя. Длина этого хвоста —
**4972 символа**, измерено прямо по артефакту прогона:

```
jobs/autods-tabred-full-20260828-151739/cooking-time__3mdVEU6/agent/instruction.md
хвост: 4972 символа, sha a58b4d40678ff1aa   (весь файл 6022, задание 1050)
```

Число 4971 в записях бралось как `len(итог) - len(задание)` без `rstrip`, то
есть на разделитель меньше, чем то, по чему считалась контрольная сумма.
Подпись была внутренне несогласованной: сумма отвечает длине 4972. Исправлено
везде — §4, §11, `make_tables.py`, `run.sh`, README, `MASTER_all_systems.csv`.
Сама контрольная сумма и все измерения не меняются.

Для справки, в тех же единицах «хвост вместе с разделителем»:
библиотечная половина 1293 символа (`dcdd71dca39bfacb`), блок дисциплины 3680
(`a8fbb6ca6ef694ef`). В статье блок дисциплины назван как есть, без
разделителя: 3678 символов, `22b138e8d5317eac` — это согласованная пара.

---

## Урезанный блок дисциплины: какая именно часть текста вредит (30.08.2026, nss-calc2)

**Зачем.** В §7 причина потерь Terminus-2 была названа по чтению трасс: блок
требует долгого обучения там, где задача решается за две минуты. Это была
догадка, а не измерение. Ячейка проверяет её напрямую.

**Что выброшено.** Из семи разделов блока убраны два, и оба про время:

* `## Training discipline — REQUIRED` — «~100 epochs is a sane starting point»,
  «when you stop, raise the budget and train again»;
* `## Time budget management — REQUIRED` — «Assume you have hours, not minutes»,
  «if the whole training phase finished within a couple of minutes you almost
  certainly undertrained».

Оба выброшены вместе: речь про время размазана по обоим, вырезать один означало
бы оставить половину воздействия. Остались пять разделов, включая все три
пункта, по которым в `tab:clauses` считается доходимость: тривиальный предиктор,
проверка ответа перед сдачей, хранить лучший вариант.

Остаток: **2481 символ, sha `af1d7e38d9b8c745`** (полный блок 3678,
`22b138e8d5317eac`). Набор `datasets/tabred-kdisc-notime`, задания выросли с
1040–1076 до 3523–3559 символов.

Собирается тем же скриптом:
```bash
python3 make_kdisc_tasks.py --out tabred-kdisc-notime \
    --drop "Training discipline" --drop "Time budget management"
```

**Проверка воздействия.** Урезанный блок в `agent/trajectory.json` **24/24**;
строка `hours, not minutes` — **0/24**.

**Ячейки.** Все три на nss-calc2, один образ, один адаптер,
`openrouter/google/gemma-4-31b-it`, `HARBOR_CONCURRENCY=4`, по 24 испытания.

| | без блока | полный блок | урезанный блок |
|---|---|---|---|
| задание | `terminus-tabred-Mmid-20260829-185941` | `terminus-kdisc-20260830-113531` | `terminus-kdisc-notime-20260830-135205` |
| испытаний с метрикой | 22/24 | 11/24 | **24/24** |
| потеряно | 2 | 13 | **0** |
| таймаутов | 0 | 0 | 0 |
| медиана шагов | 6 | 18 | 7 |
| медиана минут | 2.5 | 14.1 | 3.0 |
| входных токенов | 895 620 | 12 064 534 | 1 403 607 |
| выходных токенов | 45 859 | 212 923 | 61 930 |
| цена прохода | $0.0690 | $0.7278 | $0.1059 |
| цена испытания | $0.0029 | $0.0303 | $0.0044 |
| весь проход, время | — | 1 ч 46 мин | 26 мин |

**Точность (среднее по попыткам с метрикой).**

| задача | метрика | без блока | полный | урезанный | урезанный отн. % |
|---|---|---|---|---|---|
| homesite-insurance | ROC-AUC | 0.959566 | 0.959449 | 0.959766 | +0.02 |
| ecom-offers | ROC-AUC | 0.563585 | 0.564631 | 0.559876 | −0.66 |
| homecredit-default | ROC-AUC | 0.857289 | 0.856682 | 0.815040 | −4.93 |
| sberbank-housing | RMSE | 0.250328 | 0.251640 | 0.250328 | +0.00 |
| cooking-time | RMSE | 0.483718 | 0.483327 | 0.483645 | +0.02 |
| delivery-eta | RMSE | 0.547847 | 0.547815 | 0.547754 | +0.02 |
| maps-routing | RMSE | 0.162705 | 0.162731 | 0.162748 | −0.03 |
| weather | RMSE | 1.523593 | результата нет | 1.523479 | +0.01 |

Среднее по восьми −0.69%, но оно целиком держится на одной попытке из двадцати
четырёх: на `homecredit-default` три попытки дали 0.858838, 0.856964 и
**0.729318**. Ответ записан, модель слабая — это выброс на одном испытании, а не
отказ. Без этой задачи среднее по остальным семи **−0.09%**. Семь задач из
восьми двигаются меньше чем на десятую долю процента.

**Значимость (точный тест Фишера, двусторонний, по числу потерь).**

* полный блок против «без блока»: 13/24 против 2/24, **p = 0.0013**;
* урезанный против полного: 0/24 против 13/24, **p = 2.6·10⁻⁵**;
* урезанный против «без блока»: 0/24 против 2/24, **p = 0.49** — неразличимы.

**Вывод.** Вредит не предписание, а два раздела из семи — те, что делают
допущение о характере работы, а не утверждение о методе. Текст был в двух
абзацах от переносимости, и стоило выяснить это одиннадцать центов и 26 минут.

**В статье.** §7, `sec:kdiscterm`, третий столбец `tab:kdiscterm`.

---

## Сетка слоя на Terminus-2 достроена (30.08.2026, nss-calc2)

Все пять ячеек: один образ (обогащённый, `python:3.12-slim` с LightAutoML),
один адаптер, `openrouter/google/gemma-4-31b-it`, `HARBOR_CONCURRENCY=4`, по 24
испытания. Отличие между ячейками — только то, что дописано в `instruction.md`.
Склейку делает сам `augment()` из установленного пакета, поэтому разделители
побайтово те же, что в прогонах AutoDS.

| ячейка | задание | годных | потеряно | задач с ответом | медиана шагов | медиана минут | $/исп. |
|---|---|---|---|---|---|---|---|
| ничего | `terminus-tabred-Mmid-20260829-185941` | 24 | 2 | 8/8 | 6 | 2.5 | 0.0029 |
| K_disc | `terminus-kdisc-20260830-113531` | 24 | 13 | 7/8 | 18 | 14.1 | 0.0303 |
| K_disc без времени | `terminus-kdisc-notime-20260830-135205` | 24 | 0 | 8/8 | 7 | 3.0 | 0.0044 |
| K_tool | `terminus-ktool2-20260830-192709` | 22 | 19 | 3/8 | 14 | 10.2 | 0.0107 |
| обе половины | `terminus-kboth-20260830-165917` | 24 | 11 | 6/8 | 20 | 18.4 | 0.1172 |

Проверка воздействия по всем ячейкам: нужная половина в 24/24 траекториях,
ненужная в 0/24. Таймаутов нет ни в одной ячейке.

**Точный тест Фишера по числу потерь, двусторонний.**

| сравнение | p |
|---|---|
| K_disc против «ничего» | 0.0013 |
| урезанный против K_disc | 2.6·10⁻⁵ |
| урезанный против «ничего» | 0.49 (неразличимы) |
| K_tool против «ничего» | 9.6·10⁻⁸ |
| K_tool против «обеих половин» | 0.0055 |
| «обе» против «ничего» | 0.0078 |

**Взаимодействие.** Библиотечная половина сама по себе теряет 19 испытаний из
22. Добавление к ней половины дисциплины, которая сама по себе стоит 13 потерь
из 24, снижает потери до 11 из 24. То, что вредит по отдельности, защищает в
паре: половина дисциплины говорит агенту, что долгая работа — норма, а
библиотечная половина именно этого от него и требует.

**Механизм успеха в библиотечных ячейках.** Испытания, дошедшие до ответа,
отличаются не качеством, а упорством: 228, 267 и 355 шагов агента за 46–57
минут против медианы 14 шагов и 10 минут. Все потери — это `mark_task_complete`
без `predictions.csv`, ровно как в ячейке дисциплины.

**Точность там, где она измерима.** K_tool +1.21% по трём задачам, «обе» +1.13%
по шести — то же направление и порядок, что +0.64% у библиотечной половины
внутри AutoDS. Но это среднее по выжившему меньшинству, а выживание в этих
ячейках и есть упорство, так что число не сопоставимо с первыми тремя строками.

**Испорченный прогон.** Первая съёмка ячейки K_tool
(`terminus-ktool-20260830-145000`) в дело не идёт: пять испытаний из 24 умерли
от обрыва связи с провайдером (`aiohttp`, не таймаут), все пять в одном окне
около 14:57. Из 19 годных потеряно 16 — эффект тот же, что в пересъёмке
(19 из 22), то есть воспроизводится. В пересъёмке тоже поймано два сетевых
падения, около 20:05; они исключены, отсюда 22 годных, а не 24.

### Совпадение значений до последней цифры — это детерминизм, а не находка

Проверено после того, как совпадение показалось подозрительным.

Что исключено:

* наборы `tabred-kdisc`, `tabred-kdisc-notime`, `tabred-ktool`, `tabred-kboth`
  отличаются от `tabred` только файлом `instruction.md` (`diff -rq` по дереву);
* `solution/predictions.csv` **побайтово совпадает** с ключом
  `tests/test_targets.csv` (md5 `b8cb8a544d400a4534fdd84338a92871`), то есть
  копирование эталона дало бы RMSE 0 и награду 1.0 — такого нет ни в одном
  испытании за все прогоны;
* в образ агента эталон не попадает: `Dockerfile` содержит только
  `COPY data/ /app/data/`, а `/solution` монтируется отдельному агенту-оракулу,
  чей `solve.sh` состоит из одной строки `cp`;
* в `test.csv`, доступном агенту, целевой колонки нет; скорер читает ключ из
  `/tests/test_targets.csv` в своём контейнере;
* ни одна трасса не упоминает `/tests` или `test_targets`; единственные
  вхождения строки `/solution` — это `/app/solution.py`, файл самого агента.

Настоящая причина: задачи детерминированы при фиксированной библиотеке и её
настройках. Решающее наблюдение — то же совпадение **без всякого слоя**:

```
sberbank-housing = 0.2516404543658208
    AutoDS  без слоя:   3 попытки из 3
    Terminus без слоя:  2 попытки из 3
```

Слой меняет только то, какая библиотека будет вызвана: в обработанных ячейках
все сходятся к другому значению, `0.2514574079401016`. Значения ячейки «обе
половины» совпадают именно со значениями `libonly` у AutoDS
(`0.5474849170451774`, `0.5799742521307027`, `0.5799913674546233`,
`0.8635503910374048`).

**Следствие для методики.** Попытки, совпадающие до последней цифры, — не
независимые измерения агента. Пороги шума в §5 частично меряют детерминизм
библиотеки, а не устойчивость системы. Оговорка добавлена в §5 и в §7
(`sec:kdiscterm`, последний абзац).

---

## Две редакции слоя: измерение вместо предположения

Скрипт: `runs/autods-tabred/mlab_layer_drift.py` (отделяет слой от задания и
считает отпечаток), `runs/autods-tabred/run.sh verify` (отпечаток того, что
собирается сейчас).

Файл `instruction_c1.md` в наборе задач — это **комментарий-шапка, потом
задание, потом слой**, а не задание плюс слой. Шапка дописана при выкладке
артефакта, в самом прогоне её не было; она сообщает читателю, что базовая ветка
получала `instruction.md` без слоя. Перед любым сравнением её надо срезать —
иначе разница длин завышена на 232 символа, а агент в пересъёмке получил бы
подсказку о том, в какой он ветке.

### Опубликованная редакция (на ней считались числа MLAgentBench)

Внутри семейства текст побайтно одинаков у всех задач семейства.

| семейство | задачи | символов | sha256 |
|---|---|---|---|
| tabular | amp-parkinsons, house-price, spaceship-titanic | 5085 | `bf1e4e7c8c4960a2` |
| vision | cifar10, fathomnet, identify-contrails | 4363 | `893113ea778cec91` |
| nlp | feedback, imdb | 4163 | `0822dc3f813cc203` |
| graph | clrs, ogbn-arxiv | 4153 | `45031c60da3db772` |

### Редакция из склонированной ветки (на ней считались числа TabReD)

| семейство | символов | sha256 |
|---|---|---|
| tabular | 4972 | `a58b4d40678ff1aa` |
| vision | 4250 | `dc615e8dfb576ce1` |
| nlp | 4050 | `71af4c4b3a0a6e5c` |
| graph | 4708 | `49074fc3b930c91a` |

### Чем именно различаются

Заголовков в обеих по восемь, набор одинаков. Общий блок дисциплины короче на
**113 символов**, блок библиотеки для графов длиннее на **668**.

Различие не косметическое. В склонированной ветке стоят две подсказки,
написанные под конкретные задачи бенчмарка:

* «SMAPE максимально штрафует ненулевой прогноз против нулевой цели» —
  под `amp-parkinsons`;
* «замаскируй недостижимые кандидаты перед softmax» — под указатели `clrs`.

В опубликованной редакции обе заменены общим требованием: посылка не должна
быть константой, прогнозы обязаны различаться по строкам, перед отправкой
напечатай число различных значений на цель.

### Что из этого следует для §11

Прежняя формулировка в §11 — «запрет на константную посылку был у двух задач и
отсутствовал у восьми» — **неверна**. Запрет есть у всех десяти, потому что он
живёт в слое, а слой одинаков внутри семейства. Асимметрия проходит не между
задачами, а между ветками: слой получала только обработанная ветка AutoDS,
а Terminus-2 не получал его ни на одной задаче — его перемычка подаёт голое
задание. Обе вырожденные посылки принадлежат именно Terminus-2, то есть ветке
без запрета. Абзац переписан.

---

## Опыт A: AutoDS-Tools на MLAgentBench, по три попытки, обе ветки

Скрипты: `runs/autods-tabred/mlab_autods.sh` (прогон), `fetch_mlab.py` (загрузка
задач), `mlab_testsh.py` (перемычка проверяющего), `mlab_patch.py` (правка
образа), `make_mlab_c1.py` (сборка ветки со слоем), `collect_mlab.py` (сборка
чисел), `durations.py` (длительности).

Задания: `autods-mlab-nolayer-full-20260903-153122`,
`autods-mlab-c1-full-20260903-234827`. Машина nss-calc2, 18 ядер, без GPU,
по четыре испытания разом, 60 испытаний, все с оценкой.

### Зачем

Строка MLAgentBench в статье собрана из одиночных прогонов. На четырёх задачах
пересъёмки Terminus разброс внутри задачи оказался пятикратным (`fathomnet`
0.1144 / 0.3303 / 0.5569), то есть одиночные прогоны там не измеряли ничего.
Опыт A даёт по три испытания в каждой ячейке и заодно проверяет, воспроизводим
ли мы опубликованные числа вообще.

### Устройство

Обе ветки идут на одних и тех же образах и одном и том же проверяющем: каталоги
`environment/` и `tests/` в наборе `mlab-c1` не копии, а ссылки на `mlab`.
Различается ровно текст задания.

* **без слоя** — `instruction.md`, как в бенчмарке;
* **со слоем** — `instruction_c1.md`, как выложен, за вычетом шапки-комментария.

Сборщик слоя погашен в обеих ветках (`AUTODS_C1_DISABLED=1`). Иначе поверх
опубликованного текста лёг бы ещё и сегодняшний, а они разошлись — см. раздел
про две редакции слоя.

### Правило исключения

Испытание, исчерпавшее бюджет и не оставившее посылки, из среднего исключается:
оно меряет бюджет, а не модель. Отличить его от честного нуля можно по самому
`reward.json` — у настоящей оценки рядом с наградой лежат поля метрики, у
несостоявшейся только `"reward": 0.0`. Правило то же, что было принято для
TabReD.

**Важно:** исчерпать бюджет и остаться без результата — разные вещи. В ветке без
слоя `clrs` дважды упёрся в потолок и дал при этом 0.4118 и 0.4404, `feedback` —
0.6492, `house-price` — 0.8838. Проверяющий считает то, что успело лечь в
`submission.csv`.

### Что вышло

Медиана времени испытания **10.9 минуты без слоя против 19.6 со слоем**.
Исчерпали бюджет 13 из 30 против 15 из 30.

**Обработанная ветка воспроизводит опубликованные числа.** Медиана наших трёх
попыток против опубликованного одиночного прогона: `amp-parkinsons` SMAPE 87.53
против 88.08, `spaceship-titanic` 0.8114 против 0.8085, `ogbn-arxiv` 0.53 против
0.556, `house-price` MAE 16234 против 15957, `clrs` и `fathomnet` — ноль в обоих
случаях.

**Необработанная — не воспроизводит, и ровно на трёх задачах.** `amp-parkinsons`
SMAPE 66.35 против опубликованных 96.58, `feedback` MCRMSE 0.6812 против 1.6634,
`ogbn-arxiv` 0.4572 против 0.3217. Это ровно те три задачи, на которых
опубликованные данные показывают выигрыш от слоя. По трём попыткам выигрыш
исчезает на `feedback` (необработанная ветка даёт 0.5403, обработанная не даёт
ничего), переворачивается на `amp-parkinsons` (58.21 и 66.35 против 81.78 и
хуже) и уменьшается с 0.23 до 0.07 на `ogbn-arxiv`.

**Слой обнуляет три задачи целиком.** `clrs`, `fathomnet` и `feedback` в
обработанной ветке дали ноль во всех трёх попытках, и все девять испытаний
упёрлись в потолок. В необработанной те же задачи дали 0.44, 0.14 и 0.54. Это
тот же отказ по нетерпению, что найден на TabReD у Terminus с блоком дисциплины,
теперь подтверждённый на другом бенчмарке и другой системе.

Разделение в обработанной ветке резкое: пять задач дают результат во всех трёх
попытках и **ни одного** исчерпанного бюджета, пять — ноль во всех трёх и
исчерпанный бюджет каждый раз. Промежуточных нет.

### Что пришлось пересчитать

`cifar10` и `imdb` дали ноль во всех шести испытаниях обеих веток, каждое
упёрлось ровно в час. Это две самые тяжёлые по счёту задачи набора, и бюджет у
них вдвое меньше остальных. При четырёх испытаниях разом на 18 ядрах час
настенного времени — около двадцати минут процессорного. Три из трёх в каждой
задаче — систематика, а не разброс, поэтому обе задачи пересняты отдельно, по
два испытания разом (`mlab_heavy.sh`, задания `autods-mlab-*-heavy-*`). Условия
у этих двух задач отличаются от остальных восьми, и это оговорено в статье.

### `cifar10` и `imdb`: почему повтор не удался

Шестнадцать испытаний из шестнадцати исчерпали часовой бюджет, не оставив
посылки: по шесть в каждой ветке при четырёх испытаниях разом (задания
`autods-mlab-*-full-2026090*`) и ещё четыре при двух разом
(`autods-mlab-nolayer-heavy-20260904-090950`). Раз при вдвое меньшей загрузке
результат тот же, нехватка ядер ни при чём — это была моя первая догадка, и она
неверна.

Агент не зависает и не буксует. В `/workspace/.autods` в первую же минуту
появляются отчёты аналитика, планировщика и исследователя, после чего процесс
Python непрерывно держит около восьми ядер: он считает. За 55 минут настенного
времени он намотал около семи часов процессорного.

Дело в том, сколько ему дают и на чём он считает. Этим двум задачам бенчмарк
отводит 3600 секунд, тогда как пяти другим — 7200. А образ по умолчанию ставит
**сборку torch под CUDA**: в `environment/Dockerfile` стоит
`ARG TORCH_VARIANT=auto`, и на x86_64 это разрешается в CUDA-колесо. При этом в
`task.toml` нет ключа `gpus`, так что видеокарты контейнер не получает и torch
откатывается на процессор.

Стартовый `train.py` с пятью эпохами на процессоре успевает. Любое улучшение,
которое агент над ним надстраивает, — нет. Опубликованные 0.8849 и 0.8643
получены, судя по всему, на машине с ускорителем; проверить это по артефактам мы
не можем, но образ собран именно под него.

**Следствие.** Эти две задачи остаются в таблице с опубликованными одиночными
числами и пометкой, что повторить их на машине без видеокарты не удалось.
Восемь остальных задач пересняты по три попытки. Это не относится к четырём
задачам, которые Terminus-2 недобрал (`clrs`, `feedback`, `identify-contrails`,
`fathomnet`): те на процессоре проходят и пересняты полностью.

---

## Опыт B: Terminus-2 на восьми задачах MLAgentBench, по три попытки

Скрипт `runs/autods-tabred/mlab_terminus.sh`, задание
`terminus-mlab-full-20260904-155000`. Машина nss-calc2, по четыре испытания
разом, 24 испытания, все с оценкой, один исчерпал бюджет.

### Зачем

Строка Terminus в таблице покрытия была склеена из шести опубликованных
одиночных прогонов и четырёх наших, снятых с другой перемычкой проверяющего.
Внутри себя она несопоставима. Теперь все восемь задач сняты одним заданием,
одной перемычкой, по три попытки. `cifar10` и `imdb` исключены — они не
воспроизводятся без ускорителя.

### Первая же попытка запуска пропала не по нашей вине

Прогон в 14:59 дал 24 исключения за семнадцать минут: прокси, через который
идут обращения к модели, отказывал в соединении. Проверено тремя способами —
порт прокси закрыт, прямое обращение к OpenRouter даёт 403, HuggingFace при этом
отвечает 200. Задание отложено как `.brosheno-terminus-proxy-20260904-145908` и
в сборку чисел не входит. Денег не стоило: ни одного запроса не прошло.

### Числа

| задача | метрика | среднее | попыток с посылкой | размах |
|---|---|---|---|---|
| `amp-parkinsons` | SMAPE ↓ | 60.4999 | 1 из 3 | — |
| `clrs` | указатели ↑ | 0.1397 | 2 из 3 | 0.1330–0.1464 |
| `fathomnet` | micro-F1 ↑ | 0.2440 | 3 из 3 | 0.0844–0.3846 |
| `feedback` | MCRMSE ↓ | 0.5279 | 2 из 3 | 0.4972–0.5586 |
| `house-price` | MAE ↓ | 21 594.8 | 2 из 3 | 19 422–23 767 |
| `identify-contrails` | Dice ↑ | 0.0 | 2 из 3 | 0–0 |
| `ogbn-arxiv` | точность ↑ | 0.1606 | 3 из 3 | 0.0597–0.2655 |
| `spaceship-titanic` | точность ↑ | 0.6590 | 3 из 3 | 0.5859–0.7059 |

Медиана времени испытания 6.1 минуты, максимум 91.9. У AutoDS без слоя на тех же
задачах 10.9 минуты. Бюджет исчерпан 1 раз из 24 против 13 из 30 у AutoDS.
Потеряно испытаний без посылки: 6 из 24 против 2 из 24 на тех же восьми задачах.

### Очная встреча архитектур

Впервые на этом бенчмарке две системы сняты в одинаковых условиях: одно задание,
один проверяющий, одна параллельность, один движок, по три попытки. Если считать
ничьёй разницу меньше 5% от большего значения, AutoDS без слоя берёт четыре
задачи, Terminus две, две вничью. Таблица `tab:mlabhead`.

`identify-contrails` проставлен ничьёй вручную: 0.0022 против нуля относительное
правило объявило бы победой AutoDS, но обе цифры означают отсутствие сегментации.

### Опубликованные числа Terminus не воспроизвелись

На трёх задачах из четырёх, где есть опубликованное значение, оно лежит **вне**
нашего размаха: `ogbn-arxiv` 0.5148 против 0.0597–0.2655, `spaceship-titanic`
0.8016 против 0.5859–0.7059, `house-price` MAE 16 695 против 19 422–23 767.

Проверяющий тут ни при чём, и это можно утверждать, а не предполагать: та же
самая перемычка воспроизводит опубликованные числа AutoDS на тех же задачах —
0.8085 против наших 0.8114 на `spaceship-titanic`, 88.08 против 87.53 на
`amp-parkinsons`. Перемычка, которая считала бы иначе, так бы не смогла.

Остаются два объяснения, и наши данные их не разделяют. Либо Terminus
разбрасывается шире, чем видно по одному испытанию на клетку, и опубликованный
прогон поймал верхний край. Либо между тем заданием и нашим сдвинулась версия
перемычки terminus-2 — мы работаем на Harbor 0.22.0, версия опубликованного
задания в том, что у нас есть, не записана. Первое согласуется с разбросами,
которые мы меряем в той же системе: `fathomnet` дал 0.0844 / 0.2629 / 0.3846 в
одном задании и 0.1144 / 0.3303 / 0.5569 в другом. Второе без окружения
исходного задания не проверить.

В статье приводим свои числа с размахом и печатаем опубликованный одиночный
прогон рядом, а не вместо.

---

## Опыт C: та же система, тот же слой, другая его редакция

Скрипт `runs/autods-tabred/mlab_layer_now.sh`, задание
`autods-mlab-layernow-20260904-183724`. 24 испытания, слой применён в 24 из 24 —
проверено по строке `AutoDS C1 layer applied` в каждом `trial.log`. Условия те же,
что в опытах A и B: те же задачи, образы, проверяющий, четыре испытания разом.

### Что сравнивается

В опыте A обработанная ветка получала слой **выложенной** редакции, поданный
текстом задания. Здесь та же система получает слой, который сборщик собирает
**сегодня** из склонированной ветки. Тексты различаются: общий блок дисциплины
короче на 113 символов, блок для графов длиннее на 668; в сегодняшней редакции
стоят две подсказки под конкретные задачи, в выложенной они заменены общим
запретом константной посылки.

### Числа

| задача | выложенная редакция | сегодняшняя редакция | |
|---|---|---|---|
| `feedback`, MCRMSE ↓ | **посылки нет, 0 из 3** | 0.5512, 3 из 3 | сегодняшняя |
| `clrs`, указатели ↑ | **посылки нет, 0 из 3** | 0.1281, 2 из 3 | сегодняшняя |
| `fathomnet`, micro-F1 ↑ | **посылки нет, 0 из 3** | 0.1507, 1 из 3 | сегодняшняя |
| `amp-parkinsons`, SMAPE ↓ | 86.46 | 93.15 | выложенная |
| `ogbn-arxiv`, точность ↑ | 0.5069 | 0.4683 | выложенная |
| `identify-contrails`, Dice ↑ | 0.0478 | 0.0374 | выложенная |
| `house-price`, MAE ↓ | 16 433 | 16 904 | вровень |
| `spaceship-titanic`, точность ↑ | 0.8108 | 0.8091 | вровень |

Испытаний с посылкой: **15 из 24 у выложенной редакции против 21 из 24 у
сегодняшней.** Бюджет исчерпан 4 раза из 24 против 15 из 30.

### Что из этого следует

Правка в сотню символов не улучшает и не ухудшает систему — она переставляет её
с одного края на другой. Выложенная редакция требует учиться дольше и не
останавливаться рано; на трёх задачах из восьми агент выполняет это требование и
не успевает сдать работу вообще. Сегодняшняя редакция требование смягчает: те же
три задачи начинают сдаваться, но там, где времени и так хватало, результат
немного хуже.

**Разница между двумя редакциями одного слоя больше, чем разница между «слой
есть» и «слоя нет»** на этих трёх задачах. Значит воспроизвести результат нельзя,
не имея точной версии текста, а версию обычно не публикуют. Это та самая угроза,
которую §11 называет движущейся мишенью; до опыта C она была подкреплена
подсчётом символов, теперь — числом сданных работ.

### Побочно: снова детерминизм библиотеки

`house-price` дал в этой ветке `16904.159562` во всех трёх попытках побайтно, и
то же самое значение встречается среди трёх попыток ветки с выложенной редакцией.
Совпадение до последней цифры между разными ветками — то же наблюдение, что
описано выше в разделе про детерминизм: попытки, совпадающие точно, не являются
независимыми измерениями агента.

## FEDOT.LLM на TabReD с бюджетом бэкенда (21–22.09.2026)

Полный отчёт: `result_files/FEDOT_TABRED_BUDGET_2026-09-22.md`. В статью и в
`MASTER_all_systems.csv` не внесено.

Редакция: CLI-предиктор из снимка `feat-fedot-ind-tabular` (как на кейсах 10.09),
не редакция с генерацией кода от 14.08. Конфигурация: `best_quality`, тюнинг,
бюджет 1200 с, отложенная выборка, 8 потоков у шести моделей FEDOT (правка в
образе), `train + val`, 8 ядер, 16 ГБ, потолок 3600 с, параллель 2.

Задания (сервер nss-calc2, `runs/autods-tabred/jobs/`, локальные копии без
`artifacts/`): основная ветка `fedot-tabred-40min-20260922-020323` (24 трайла,
15 с метрикой); ветка 64 ГБ `fedot-tabred-40min-mem64-20260922-080941` и
`fedot-tabred-40min-mem64b-20260922-100849`. На хаб не выкладывались.

Метрики по задачам (среднее по попыткам с метрикой): ecom-offers 0.6308,
sberbank-housing 0.2421, weather 1.5762, delivery-eta 0.5597, cooking-time
0.4873; homesite-insurance 0.9587 только при 64 ГБ; homecredit-default и
maps-routing без результата (корректор типов FEDOT переводит таблицы в dtype
object, 1.6–1.7 ГБ превращаются в 17 ГБ до обучения; пробы
`fedot_prep_probe.py`, `fedot_types_probe.py`).

Уточнение 22.09 (ответ коллеги, снимавшего строку FEDOT.LLM 14.08): запуск был
сознательно облегчённым, «в облегчённом режиме с lightgbm, чтобы получить хоть
какие-то первичные результаты». Бюджет 1 мин, набор {lgbm}, тюнинг выключен:
предварительная конфигурация, а не штатная.


## FEDOT.LLM на TabReD: строка статьи с 23.09.2026

Строка FEDOT.LLM в `paper/make_tables.py` (`AGENTS`, `FEDOT_ATTEMPTS`,
`FEDOT_MINUTES`, строка `TELEMETRY`) с 23.09.2026 снята с полной конфигурации:
снимок `feat-fedot-ind-tabular` с `fedot_patch.py` и `fedot_numeric_patch.py`,
пресет `best_quality`, тюнинг включён, бюджет бэкенда 1200 с, отложенная
выборка, типы столбцов из схемы задания (`FEDOTLLM_TYPES=schema`, столбцы
`cat_` передаются FEDOT как категориальные), 8 ядер, 16 ГБ, потолок 3600 с,
8 задач × 3 попытки. Задания (локально в `runs/autods-tabred/jobs/`, выложены на Harbor Hub
публично 23.09.2026 скриптом `upload_fedot.sh`):
`fedot-tabred-40min-schema-20260922-141217` (homesite, homecredit, maps) →
https://hub.harborframework.com/jobs/77c2d2f8-722e-471a-bf44-b075776c308e;
`fedot-tabred-40min-schema5-20260922-171228` (ecom, sberbank, cooking, delivery,
weather) → https://hub.harborframework.com/jobs/374be194-9097-4b57-810b-354ce774cf8d;
`fedot-tabred-40min-schema-sberbank-20260922-175429` →
https://hub.harborframework.com/jobs/b9de44ad-9ef2-473e-a864-fd2e0bf7785f;
`fedot-tabred-40min-schema-delivery-20260922-224814` →
https://hub.harborframework.com/jobs/7768c071-ce0a-4904-b323-efd106e7304d.
На хабе у задач RMSE в столбце reward стоит преобразованный балл
(1/(1+RMSE)), сырая метрика в `reward.json` трайла; четыре трайла с reward 0
(delivery bBNNjor, sberbank DHnjWNc, fbt9jqR, Bjj9qA3) упёрлись в потолок
3600 с при трёх параллельных заданиях и в строку статьи не входят, их
повторы вошли (отчёт, раздел 14). Сводка по трайлам:
`runs/autods-tabred/fedot-tabred-logs/schema_final.json`; отчёт
`result_files/FEDOT_TABRED_BUDGET_2026-09-22.md`, разделы 13–15.

Средние по задачам: homesite 0.959719, ecom 0.620040, homecredit 0.856865,
sberbank 0.239792, cooking 0.486700, delivery 0.562040, maps 0.166449,
weather 1.565056. Нормированное среднее 0.78, средний ранг 11.9 из 21
(AutoDS-Tools 0.85 и 6.9, Terminus-2 0.72 и 11.6). Стоимость в Таблице 7
посчитана по токенам из логов (64 322 входных, 3 731 выходных на 24 трайла) по
прайс-листу gemma-4-31b-it; Harbor стоимость FEDOT.LLM не пишет, модель
вызывается изнутри контейнера. Облегчённая строка 14.08 (раздел выше) из
статьи убрана и остаётся в мастер-таблице как `default`.

## AutoDS-Tools на научных кейсах: строки статьи с 05.10.2026

Строки AutoDS-Tools в `tab:cases` (`CASES`, `CASE_EXTRA` в
`paper/make_tables.py`) с 05.10.2026 сняты с трёх попыток на кейс от
24.09.2026 вместо одиночных июльских прогонов (трайлы хаба `58ed21ad`,
`433a969c`, `edf0f88f`). Задания локально в `runs/autods-tabred/jobs/`:
`autods-cases-20260924-152108` (три попытки на кейс; две сорвались на
установке агента, `AgentSetupTimeoutError`: `maize-yield__ieFaKAX`,
`openpoly-tg__sdS8APc`) и `autods-cases-top-20260924-164757` (по одной
попытке на maize и OpenPoly взамен сорвавшихся). Конфигурация: текст задания
с разделом о библиотеке, файл инструкций AutoDS выключен, шаги поиска по
литературе и вопросов о библиотеках включены (в июле были отключены),
gemma-4-31b-it. Значения по попыткам из `<trial>/verifier/reward.json`:

- maize, Pearson r: 0.563619, 0.535805, 0.615848 (норм. RMSE 1.003731,
  0.965781, 0.972600); минуты агента 13.9, 16.4, 14.1;
- F-DATA, accuracy: 0.920499, 0.920115, 0.920115 (balanced accuracy 0.704370,
  0.677490, 0.677490); минуты 21.8, 18.3, 20.1;
- OpenPoly, R²: 0.556093, 0.518430, 0.512330 (MAE 37.92, 37.93, 43.31);
  минуты 11.4, 13.1, 34.2.

Июльские значения (0.568563 / 0.920713 / 0.543) лежат внутри разброса новых
попыток. Оба задания выложены на Harbor Hub публично 06.10.2026 (загрузил
автор): `autods-cases-20260924-152108` (9 трайлов, включая две сорвавшиеся
на установке попытки) →
https://hub.harborframework.com/jobs/845146bc-7450-492a-852e-d4ae3519a78f;
`autods-cases-top-20260924-164757` (2 трайла) →
https://hub.harborframework.com/jobs/db04edc1-b853-4d34-8052-dfa186865cd8.
Отчёт: `result_files/AUTODS_CASES_2026-09-24.md`.

## Кто строит модель: сигнатуры в трассах AutoDS-Tools на TabReD (06.10.2026)

Поиск по `agent/*` и `artifacts/**` каждого трайла (24 трайла на ячейку):

- `autods-tabred-full-20260828-151739` (оба блока) и
  `autods-tabred-libonly-20260828-213712` (только библиотека): вызов
  `TabularAutoML(` в 24 из 24 трайлов каждой ячейки, с `timeout` от 600 до
  3600 с; собственных `use_algos` или настроек тюнинга нет, то есть
  LightAutoML работает с настройками по умолчанию.
- `autods-tabred-nolayer-20260828-194654` (без файла) и
  `autods-tabred-disconly-20260829-010054` (только дисциплина): ручной
  `LGBM*`, `XGB*` или `CatBoost*` в 24 из 24 трайлов каждой ячейки; ни
  `GridSearchCV`, ни `RandomizedSearchCV`, ни `optuna.create_study`, ни
  циклов по гиперпараметрам. Два упоминания Optuna в ячейке без файла: вывод
  `pip` и рекомендация в отчёте агента, не вызов.

Что LightAutoML делает по умолчанию (Optuna, 101 попытка на LightGBM и на
CatBoost, смесь пяти моделей) проверено повтором на F-DATA:
`result_files/LAMA_FDATA_2026-09-22.md`. Журналы самой LightAutoML в
трайлах TabReD не сохранены, поэтому, дошёл ли подбор до конца при заданном
агентом `timeout`, на TabReD не проверено.

## Что делал бэкенд FEDOT на TabReD и на кейсах (07.10.2026)

Сводка по логам `agent/fedotllm.log` всех 24 трайлов строки статьи (задания
`fedot-tabred-40min-schema*`, четыре трайла с потолком 3600 с исключены):
`runs/autods-tabred/fedot_pipelines.py`. Конвейеры по умолчанию сверены с
кодом FEDOT (`api/api_utils/assumptions/task_assumptions.py`): для
классификации CatBoost, XGBoost и LightGBM, объединённые логистической
регрессией; для регрессии случайный лес (`rfr`).

| задача | первое обучение, с | эволюционный поиск | итоговый конвейер | настройка, внутренняя метрика |
|---|---|---|---|---|
| homesite | 95–98 | пропущен | ансамбль по умолчанию | без изменений |
| ecom-offers | 24–30 | шёл, конвейер не сменил | ансамбль по умолчанию | без изменений (0.711) |
| homecredit | 273–287 | пропущен | ансамбль по умолчанию | без изменений |
| sberbank | 42–49 | шёл | LightGBM | 0.253 → 0.244–0.247 |
| cooking | 482–496 | пропущен | случайный лес | без изменений |
| delivery | 790–837 | пропущен | случайный лес | без изменений |
| maps | 2090–2125 | пропущен | случайный лес | не запускалась (осталось 16 с) |
| weather | 401–408 | пропущен | случайный лес | 1.693 → 1.676 в двух попытках из трёх |

Места FEDOT.LLM среди 21 метода: ecom 1, sberbank 2, homesite и homecredit
8, weather 18, cooking и maps 19, delivery 20.

Кейсы (`fedot-plain-20260910-114632`, на nss-calc2): F-DATA, три попытки,
поиск пропущен, итог ансамбль по умолчанию, настройка без изменений (0.952);
maize, три попытки, поиск пропущен, итог случайный лес.

## Кейс maize: валидация агента против теста (07.10.2026)

Скрипт `runs/autods-tabred/maize_validation.py`. Трассы Terminus-2 по кейсам
скачаны 07.10.2026 с nss-calc2
(`/var/essdata/s_chumakov/automl-journal/runs/autods-tabred/jobs/`) в
`runs/autods-tabred/jobs/terminus-cases-plain-20260910-100339` (без раздела
о библиотеке) и `terminus-cases-20260910-100938` (с ним); на Harbor Hub их нет.

| система | трайл | модель | R² на валидации агента | R² на тесте |
|---|---|---|---|---|
| AutoDS-Tools | crg5riv | LightAutoML по умолчанию, `fit_predict` | 0.698 (вне фолдов) | −0.007 |
| AutoDS-Tools | zzJe2ed | то же | 0.698 | 0.067 |
| AutoDS-Tools | hYcCDmJ | то же | 0.689 | 0.054 |
| Terminus-2 | Bvr8Khf | RandomForest, 100 деревьев, label encoding, 80/20 | 0.690 | 0.339 |
| Terminus-2 | y9P3UE3 | HistGradientBoosting, target encoding, 80/20 | 0.652 | 0.406 |
| Terminus-2 | UqitPYf | посылки нет | | |

Обе системы проверяли модель на случайном разбиении строк, которое смешивает
пары место-год; LightAutoML без колонки групп делит на 5 случайных фолдов
(`reader/utils.py`, `set_sklearn_folds`). Попытка crg5riv сначала написала
разбиение по `(ExperimentCode, Year)`, код упал на импорте `pearsonr` из
sklearn, и агент перешёл на `fit_predict`. Почему настроенный ансамбль
переносится на новые место-годы хуже простых моделей Terminus-2, по этим
данным не установлено; прямая проверка: LightAutoML с группами по месту-году.
