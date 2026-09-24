# Приложение к ревью от 21 сентября 2026: машинизированные формулировки и их правки

Список получен свипом шести агентов по разделам и проверен двумя независимыми проверяющими на каждый раздел (точность чисел и утверждений; стиль и обоснованность флага). Раздел 6 и кейсы прошли только стилевую проверку; точность девяти находок высокой важности из него сверена вручную. Всего найдено 236, оставлено 221. Правки на английском даны с числами-литералами; при переносе в .tex автор подставляет макросы из `tables/numbers.tex`.

Важность: high 59, medium 116, low 46. Категории: прочее (отрицание, афоризм, ремарка) 49, перегруженное предложение 36, метафора 33, внутренний термин без пояснения 32, число без единицы 28, абстрактное подлежащее 22, придуманная абстракция 15, номинализация 6.

Обозначения: **Q** исходное предложение, **P** в чём затруднение, **R** предлагаемая правка.


## main.tex

### main.tex:66 · high · прочее (отрицание, афоризм, ремарка)

- **Q:** One open 31B backbone, three agent architectures, one tuned-baseline scale
- **P:** Список существительных без глагола: это описание установки, а не результат. Читатель не узнаёт, что измерено и что получилось.
- **R:** We score three agent systems on one open 31B model against 18 tuned tabular baselines

### main.tex:67 · high · число без единицы

- **Q:** Architecture spans 0.26--0.85 of the range set by 18 expert-tuned baselines
- **P:** 0.26 и 0.85 даны в нормированной шкале, которую читатель highlights не видел; непонятно, что такое 0 и 1. Плюс двойной дефис как тире.
- **R:** Agent design moves the score from below tuned boosting to level with tuned LightGBM

### main.tex:68 · medium · число без единицы

- **Q:** The best agent ties tuned LightGBM and stays 0.02 short of tuned XGBoost
- **P:** «0.02» без единицы: это доля нормированного диапазона, о котором читатель не знает. «Ties» и «stays short» разговорные, система не названа.
- **R:** AutoDS-Tools is level with tuned LightGBM, ahead of CatBoost and below tuned XGBoost

### main.tex:69 · high · придуманная абстракция

- **Q:** Score is not monotonic in architectural weight: the middle design ranks first
- **P:** «Architectural weight» придумано для статьи и нигде не определено; отрицание «not monotonic» заставляет читателя достраивать порядок самому.
- **R:** The middle design, AutoDS-Tools, beats both the rigid pipeline and the open harness

### main.tex:70 · high · метафора

- **Q:** Tool and discipline prescription are two levers, and they do not add up
- **P:** «Levers» и «do not add up» метафора и разговорный оборот. Не сказано, что за две инструкции и на сколько их эффекты расходятся.
- **R:** Prescribing a library gains 0.69%, a training protocol 0.12%, both together 0.72%


## 00_abstract.tex

### 00_abstract.tex:2 · medium · перегруженное предложение

- **Q:** Large language models have made automated data science agents practical, but the value of the architecture around the model has not been measured: reported gains confound the backbone with the harness, and agentic systems are seldom compared with baselines a practitioner would tune.
- **P:** 45 слов, три части, подлежащее «the value of the architecture». «Backbone» и «harness» появляются как термины без пояснения в первом же предложении.
- **R:** Large language models have made automated data science agents practical. How much the system around the model contributes remains unmeasured: published gains change both at once, and agents are seldom compared with baselines a practitioner would tune.

### 00_abstract.tex:5 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** We hold the model fixed at one open 31B-parameter model and vary the architecture across three systems: a rigid pipeline over a fixed AutoML backend, a six-agent system and an open agentic harness.
- **P:** Системы не названы, и дальше аннотация ссылается на них описаниями («the rigid pipeline», «the open harness»), которые читатель должен держать в голове. «Hold the model fixed at one model» повтор.
- **R:** We use one open 31B-parameter model throughout and vary the system around it: FEDOT.LLM, a rigid pipeline over a fixed AutoML backend; AutoDS-Tools, six specialised agents; and Terminus-2, an open harness with a shell and an execution loop.

### 00_abstract.tex:10 · high · число без единицы

- **Q:** Normalised against those methods, the three systems span $\nFedot$ to $\nAutoDS$ as shipped; the strongest is level with tuned LightGBM and $\gapXGB$ short of tuned XGBoost.
- **P:** 0.26, 0.85 и 0.02 даны в шкале, которую аннотация не определяет; «as shipped» употреблено как термин без пояснения.
- **R:** On a scale where 0 is the weakest and 1 the strongest reference method, FEDOT.LLM scores 0.26, Terminus-2 0.72 and AutoDS-Tools as released 0.85, level with tuned LightGBM and 0.02 short of tuned XGBoost.

### 00_abstract.tex:12 · high · абстрактное подлежащее

- **Q:** The relationship is not monotonic in architectural weight: the rigid pipeline ranks last and the multi-agent system first, and most of the margin between the two agentic systems comes from a prescribed-knowledge layer.
- **P:** Подлежащее «the relationship» и придуманный «architectural weight»; «prescribed-knowledge layer» появляется без объяснения, что это за объект.
- **R:** AutoDS-Tools ships with an instruction file that names a library and a training protocol; most of its lead over Terminus-2 comes from that file.

### 00_abstract.tex:15 · medium · внутренний термин без пояснения

- **Q:** That layer is two interventions, which tool to use and how to train, and their effects are non-additive.
- **P:** «That layer» отсылает к термину, который читатель ещё не расшифровал; «non-additive» без чисел непроверяемо.
- **R:** The file makes two prescriptions, which library to use and how to train and validate; their gains are 0.69% and 0.12% alone and 0.72% together.

### 00_abstract.tex:16 · high · абстрактное подлежащее

- **Q:** Its value changes sign with the starting point: it helps where nothing is supplied and, on a second benchmark that supplies a working script, erases the result on \mlabWiped{} of \mlabRepeated{} tasks.
- **P:** Подлежащее «its value», «starting point» как термин без определения; «erases the result» не говорит, что именно происходит (агент не сдаёт ответ).
- **R:** Where the agent starts from an empty directory the file helps on every task; on MLAgentBench, where each task supplies a working script, it leaves 3 of 8 tasks with no submission.

### 00_abstract.tex:19 · medium · метафора

- **Q:** Handed to the open harness, the same text leaves accuracy unchanged and costs most of the trials.
- **P:** «Costs most of the trials» разговорно и неясно: читатель не знает, что испытание заканчивается без сданного ответа, и сколько таких испытаний.
- **R:** Handed to Terminus-2, the same file leaves accuracy unchanged and ends 11 of 24 trials without a submission, its library half alone 19 of 22.

### 00_abstract.tex:20 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** On three published scientific tasks the open harness, given the task text alone, matched or beat the author baselines where the split is comparable, and the library prescription cost it every attempt.
- **P:** «Cost it every attempt» разговорно; «where the split is comparable» оговорка без счёта; подлежащее разорвано вставкой, и неясно, к кому относится «it».
- **R:** On three published scientific tasks, Terminus-2, given only the task description, matched or beat the authors' baselines on the two tasks with a comparable split. Given the library instruction as well, it ended all nine attempts without a submission.


## 01_introduction.tex

### 01_introduction.tex:15 · medium · абстрактное подлежащее

- **Q:** What has not been measured is how much any of this is worth.
- **P:** Утверждение через отрицание с абстрактным подлежащим; «worth» разговорно, не сказано, в чём мерить.
- **R:** How much each of these design choices adds to accuracy remains unmeasured.

### 01_introduction.tex:18 · medium · перегруженное предложение

- **Q:** Comparisons across papers therefore cannot separate the contribution of the architecture from that of the model, and agentic systems are rarely measured against the baseline a competent practitioner would reach for: where a tuned gradient boosting model appears at all, it usually appears untuned.
- **P:** 45 слов, три части. Концовка «a tuned gradient boosting model ... appears untuned» с первого раза читается как противоречие.
- **R:** Comparisons across papers therefore cannot separate the architecture from the model. Agentic systems are also rarely measured against the baseline a competent practitioner would reach for, tuned gradient boosting; where gradient boosting appears at all, it is usually untuned.

### 01_introduction.tex:38 · low · внутренний термин без пояснения

- **Q:** A second benchmark, MLAgentBench~\citep{huang2024mlagentbench}, supplies a working script in every task and so provides a second starting point.
- **P:** «Starting point» вводится как термин мимоходом, а дальше на него опираются RQ3, вклады и аннотация.
- **R:** A second benchmark, MLAgentBench~\citep{huang2024mlagentbench}, supplies a working script in every task, so there the agent starts from a script to improve; on TabReD it starts from an empty directory.

### 01_introduction.tex:47 · high · внутренний термин без пояснения

- **Q:** \item[RQ2.] How much of that effect belongs to the architecture itself, and how much to the prescribed-knowledge layer, the container image and the choice of backbone that travel with it?
- **P:** «Prescribed-knowledge layer» здесь встречается впервые и без пояснения; «travel with it» метафора.
- **R:** \item[RQ2.] How much of that effect comes from the architecture itself, and how much from what is deployed with it: an instruction file that prescribes a library and a training protocol, the container image and the backbone model?

### 01_introduction.tex:50 · medium · абстрактное подлежащее

- **Q:** \item[RQ3.] Does the value of prescription carry over to a different starting point, where a working script replaces the empty directory, and to a different architecture?
- **P:** Подлежащее «the value of prescription»; «starting point» и «carry over» абстрактны, бенчмарки не названы.
- **R:** \item[RQ3.] Does the instruction file help as much when the agent starts from a working script (MLAgentBench) as from an empty directory (TabReD), and when it is handed to a different architecture?

### 01_introduction.tex:59 · high · число без единицы

- **Q:** (i)~A measurement of the ceiling. Under one backbone the architectures span $\nFedot$ to $\nAutoDS$ of the range set by the published baselines; the strongest is level with tuned LightGBM and $\gapXGB$ short of tuned XGBoost. This bounds what scaffolding can buy at this model scale.
- **P:** «The ceiling» не определён; 0.26, 0.85 и 0.02 в шкале без единицы; «what scaffolding can buy» разговорно.
- **R:** (i)~A measurement of how far the architecture carries a 31B model. On a scale where 0 is the weakest and 1 the strongest of the eighteen tuned reference methods, FEDOT.LLM scores 0.26, Terminus-2 0.72 and AutoDS-Tools 0.85. The best of the three is level with tuned LightGBM and 0.02 short of tuned XGBoost; no architecture we tested does better at this model size.

### 01_introduction.tex:63 · high · номинализация

- **Q:** (ii)~A separation of the architecture from what travels with it. The score is not monotonic in architectural weight, the best system being neither the most nor the least constrained. Of the $\gapAgentsShip$ between the two agentic systems, $\layerWorthNorm$ belongs to the prescribed-knowledge layer and $\gapAgentsOff$ to the architecture; the container image is worth nothing and the backbone less than the architecture.
- **P:** Номинализация без содержания («a separation of ... from what travels with it»), придуманный «architectural weight», «neither ... nor», три числа 0.13, 0.10, 0.03 без единицы.
- **R:** (ii)~A separation of the architecture from the instruction file, container image and backbone model deployed with it. FEDOT.LLM, the most constrained system, ranks last; Terminus-2, the least constrained, ranks second; AutoDS-Tools ranks first. AutoDS-Tools leads Terminus-2 by 0.13 on the same scale; 0.10 of that comes from its instruction file and 0.03 from the architecture. The container image contributes nothing, and swapping the backbone model moves the score less than swapping the architecture.

### 01_introduction.tex:69 · high · абстрактное подлежащее

- **Q:** (iii)~A separation of two interventions the literature treats as one. Prescribing which tool to use (\Ktool{}) and prescribing how to train and validate (\Kdisc{}) differ in size and their effects are non-additive. Their value changes sign with the starting point, erasing the result on \mlabWiped{} of \mlabRepeated{} tasks that start from a working script, and does not port between architectures. Together these explain why aggregate ablations of knowledge injection disagree.
- **P:** Символы K_tool и K_disc раньше раздела 3.4; «their value changes sign», «erasing the result», «does not port» абстрактно и метафорично, чисел нет, кроме 3 из 8.
- **R:** (iii)~A separation of two instructions the literature treats as one: which library to use and how to train and validate. Inside AutoDS-Tools on TabReD the library instruction gains 0.69%, the training instruction 0.12%, and both together 0.72%, less than their sum. Where the agent starts from a working script (MLAgentBench), the same instruction file leaves 3 of 8 tasks with no submission. Handed to Terminus-2, it leaves accuracy unchanged and ends trials without a submission: 19 of 22 with the library instruction alone, 11 of 24 with the whole file. These results explain why published ablations of knowledge injection disagree.

### 01_introduction.tex:75 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** (iv)~External validity on three published scientific tasks, maize yield, supercomputer job failure and polymer glass transition. Given the task text alone, the open harness matched or beat the author baselines where the split is comparable and rediscovered the published featurisation; the library prescription that the multi-agent system ran on cost it every attempt.
- **P:** «Cost it every attempt» разговорно; «the library prescription that the multi-agent system ran on» громоздко, и неясно, к кому относится «it».
- **R:** (iv)~External validity on three published scientific tasks: maize yield, supercomputer job failure and polymer glass transition. Given only the task description, Terminus-2 matched or beat the authors' baselines on the two tasks with a comparable split and rediscovered the published featurisation. Given the library instruction that AutoDS-Tools runs on as well, Terminus-2 ended all nine attempts without a submission.

### 01_introduction.tex:83 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** Terminal-Bench 2.0 introduces Terminus~2 as a deliberately minimal scaffold, built so that a leaderboard over it reads as a comparison between models~\citep{merrill2026terminalbench}.
- **P:** «Deliberately» из списка запрещённых авторских ремарок; смысл целиком передаёт придаточное «built so that».
- **R:** Terminal-Bench 2.0 introduces Terminus~2 as a minimal scaffold, built so that a leaderboard over it reads as a comparison between models~\citep{merrill2026terminalbench}.

### 01_introduction.tex:90 · medium · абстрактное подлежащее

- **Q:** We ask the question where a strong non-agentic reference exists and can calibrate the answer.
- **P:** «Calibrate the answer» абстрактно; «non-agentic reference» жаргон; не сказано, о какой области данных речь.
- **R:** We ask the same question on tabular data, where expert-tuned baselines exist to compare against.

### 01_introduction.tex:91 · high · число без единицы

- **Q:** With the backbone held constant, the three systems as they ship span $\spanShip$ of the range set by eighteen tuned baselines, and $\spanArch$ once the prescribed-knowledge layer is removed.
- **P:** 0.59 и 0.49 в нормированной шкале без единицы; «as they ship» и «prescribed-knowledge layer» как термины без пояснения.
- **R:** With the model held constant, the three systems as released differ by $\spanShip$ of the gap between the weakest and the strongest of the eighteen tuned baselines, and by $\spanArch$ once the instruction file is removed from AutoDS-Tools.

### 01_introduction.tex:94 · medium · число без единицы

- **Q:** Holding the architecture fixed and swapping the backbone across a \axPriceSpread-fold spread in price moves the score by at most $0.24$, and that figure rests on a single task, without which it is $0.07$.
- **P:** 0.24 и 0.07 без единицы; задача, на которой держится число, не названа.
- **R:** Holding the architecture fixed and swapping the backbone model across a 13-fold spread in price moves the score by at most 0.24 of the same gap. One task, \texttt{sberbank-housing}, drives that figure; without it the shift is 0.07.

### 01_introduction.tex:96 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** A scaffold is never neutral, and on this domain it is the larger of the two terms.
- **P:** Афористичная концовка; «the two terms» читатель должен восстановить из двух предыдущих предложений.
- **R:** On this domain the architecture moves the score more than the backbone does: $\spanArch$ against at most $0.24$.


## 02_related.tex

### 02_related.tex:17 · medium · внутренний термин без пояснения

- **Q:** Section~\ref{sec:axis} argues that this second axis bundles two interventions with different mechanisms.
- **P:** «Two interventions with different mechanisms» не названы; читатель узнает, о каких двух инструкциях речь, только в разделе 3.4.
- **R:** Section~\ref{sec:axis} splits this second axis into two instructions with different mechanisms: which library to use, and how to train and validate.

### 02_related.tex:38 · medium · перегруженное предложение

- **Q:** Its normalised scale is anchored on an untuned HistGradientBoosting oracle, so its unit of ``solved'' sits well below the tuned references used here, and its eight backbones are frontier and mixture-of-experts models from 80B to 1.6T parameters, with no dense small model.
- **P:** 47 слов и две разные мысли; «oracle» и «unit of ‘solved’» требуют расшифровки, «tuned references» не названы.
- **R:** GRACE-DS normalises scores against an untuned HistGradientBoosting model, so its threshold for a solved task sits well below the tuned XGBoost, LightGBM and CatBoost used here. Its eight backbones are frontier and mixture-of-experts models of 80B to 1.6T parameters, all larger than the dense 31B model used here.

### 02_related.tex:42 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** The two results are two sides of one observation.
- **P:** Афористичная связка без содержания; следующие два предложения уже говорят то же самое.
- **R:** The two designs are complementary.

### 02_related.tex:45 · high · число без единицы

- **Q:** Section~\ref{sec:modelaxis} gives the first half in sharper form: a stronger backbone moves the normalised score by $0.04$ under the multi-agent system, against $\spanArch$ between architectures at a fixed backbone.
- **P:** 0.04 и 0.49 даны в нормированной шкале, которая вводится только в разделе 5; «the first half» и «the multi-agent system» заставляют вспоминать, что имелось в виду.
- **R:** Section~\ref{sec:modelaxis} measures the backbone effect under our conditions. On a scale where 0 is the weakest and 1 the strongest of the eighteen published methods on each task, swapping the backbone under AutoDS-Tools moves the score by 0.04. Changing the architecture at a fixed backbone, with the prescribed-knowledge layer removed, moves it by 0.49.

### 02_related.tex:50 · medium · перегруженное предложение

- **Q:** Whether scaffolding can substitute for capability has been asked directly in the embodied setting, where reasoning, memory, reflection and reinforcement modules were crossed over a capability ladder of dense models, with the conclusion that external scaffolding can compensate for weaker native long-horizon reasoning~\citep{agentspec2026}.
- **P:** 45 слов, подлежащее — косвенный вопрос, «capability ladder» метафора; три мысли (вопрос, план, вывод) в одном предложении.
- **R:** One study in the embodied setting asked whether scaffolding can substitute for model capability~\citep{agentspec2026}. It crossed reasoning, memory, reflection and reinforcement modules with dense models of increasing size and concluded that external scaffolding can compensate for weaker native long-horizon reasoning.

### 02_related.tex:55 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** We take that design as precedent and ask the same question where a strong non-agentic reference exists, which supervised tabular learning provides and embodied benchmarks do not.
- **P:** Концовка «and embodied benchmarks do not» — контраст через отрицание; «non-agentic reference» нигде не расшифрован, два придаточных подряд.
- **R:** We follow that design on supervised tabular tasks, where eighteen tuned methods, among them XGBoost, LightGBM and CatBoost, give a strong reference.

### 02_related.tex:62 · high · придуманная абстракция

- **Q:** That literature varies the harness with the task family fixed; we vary the architectural weight of the system with the family fixed and a tuned non-agentic reference available on the same split, which turns a spread into a calibrated fraction of an achievable range.
- **P:** «Architectural weight» и «calibrated fraction of an achievable range» — внутренние термины статьи; 44 слова и три мысли, системы и бейзлайны не названы.
- **R:** That literature varies the harness with the task family fixed. We fix the task family and vary how much of the pipeline the architecture decides in advance, from FEDOT.LLM through AutoDS-Tools to Terminus-2. Tuned methods evaluated on the same split turn that spread into a fraction of the range between the weakest and the strongest published method.

### 02_related.tex:70 · high · номинализация

- **Q:** Our prescribed-knowledge axis is a prompt-level intervention, so Section~\ref{sec:axis} treats it as a quantity to be measured; the non-additivity of its two halves is what that localisation predicts.
- **P:** «The non-additivity of its two halves» и «that localisation» — две номинализации подряд; читатель ещё не знает, какие две половины и что именно предсказано.
- **R:** Our prescribed-knowledge layer is a prompt-level intervention, so Section~\ref{sec:axis} measures its size and Sections~\ref{sec:grid} and~\ref{sec:kdiscterm} measure its effect. That result predicts ours: the two instructions in the layer, which library to use and how to train and validate, gain less together than the sum of their separate gains.


## 03_systems.tex

### 03_systems.tex:33 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** The chain is literal: each stage writes a Markdown report that the next one reads, and a trial directory holds the analyst's, the researcher's and the planner's reports as separate artefacts.
- **P:** «The chain is literal» — авторская ремарка; слово «literal(ly)» в разделе повторяется дважды (строки 33 и 94).
- **R:** The agents communicate through files: each stage writes a Markdown report that the next one reads, and a trial directory keeps the analyst's, the researcher's and the planner's reports as separate files.

### 03_systems.tex:35 · medium · абстрактное подлежащее

- **Q:** Freedom of action is broad, any library in the environment and restructuring between iterations.
- **P:** Подлежащее «Freedom of action», затем перечень существительных без глагола; тот же приём, что в отвергнутом пункте highlights.
- **R:** The system may use any library installed in the environment and may restructure the solution between iterations.

### 03_systems.tex:41 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** There is no planner, no role decomposition and no template.
- **P:** Описание системы через три отрицания; читатель должен сам вывести, что в Terminus-2 есть.
- **R:** Planning, task decomposition and code structure are decided by the model at run time.

### 03_systems.tex:62 · medium · метафора

- **Q:** \Ktool{} & \emph{welded in} & switchable & off, switchable \\
- **P:** «Welded in» — метафора в ячейке таблицы; символы K_tool и K_disc стоят в таблице раньше своего определения в 3.4, без словесной подписи.
- **R:** \Ktool{}, tool & always on & switchable & off, switchable \\ \Kdisc{}, discipline & not crossed$^{\ast}$ & switchable & switchable \\

### 03_systems.tex:78 · high · внутренний термин без пояснения

- **Q:** In the material we study they are two interventions of very unequal size, and their effects are non-additive.
- **P:** «The material we study» и «two interventions» не названы, «non-additive» без числа; ключевое утверждение раздела повторяет пункт highlights, который автор отверг.
- **R:** In the layer AutoDS-Tools ships with they are two instructions of very unequal length: which library to use, and how to train and validate. Their combined gain is smaller than the sum of their separate gains (Sections~\ref{sec:grid} and~\ref{sec:kdiscterm}).

### 03_systems.tex:82 · low · метафора

- **Q:** \item[\Ktool{}, tool prescription.] Which class of instrument to reach for: a dedicated tabular AutoML library for tabular data, a vision backbone library for images, a graph learning library for graphs, a transformer library for text.
- **P:** «Which class of instrument to reach for» — фрагмент без глагола с метафорой «reach for».
- **R:** \item[\Ktool{}, tool prescription.] Which library to use: a dedicated tabular AutoML library for tabular data, a vision backbone library for images, a graph learning library for graphs, a transformer library for text.

### 03_systems.tex:87 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** \item[\Kdisc{}, training discipline.] How to train and how to check oneself: the validation protocol, the handling of temporal shift, leakage checks, and the prohibition of degenerate submissions.
- **P:** «Check oneself» разговорное; «the prohibition of degenerate submissions» — номинализация.
- **R:** \item[\Kdisc{}, training discipline.] How to train and how to validate: the validation protocol, the handling of temporal shift, leakage checks, and a ban on degenerate submissions.

### 03_systems.tex:93 · medium · перегруженное предложение

- **Q:** The layer AutoDS-Tools ships with is composed literally as an instruction, a library block selected by task family, and a discipline block; the first section of the discipline block is a hardware block that prescribes neither a tool nor a training protocol.
- **P:** 42 слова; «composed literally as an instruction» непонятно (инструкция чего?), а hardware-блок описан через «neither ... nor».
- **R:** The layer AutoDS-Tools ships with is assembled from a library block chosen by task family and a discipline block. The first section of the discipline block is a hardware block, which we count separately.

### 03_systems.tex:96 · medium · перегруженное предложение

- **Q:** Read from the module that composes the layer and checked against the instruction each container received, the library block runs from \layerLibMin{} characters for text to \layerLibMax{} for tabular tasks, the hardware block is a fixed \layerHardware{} and the discipline block a fixed \layerDiscipline{}.
- **P:** 46 слов, висячий причастный оборот и три подлежащих; способ измерения и результат слиты в одно предложение.
- **R:** We measured the blocks in the source module that assembles the layer and checked the counts against the instruction each container received. The library block runs from 369 characters for text to 1291 for tabular tasks; the hardware block is 668 characters and the discipline block 3008 on every task.

### 03_systems.tex:100 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** The tool prescription, the intervention the layer is named after, accounts for between $\layerShareMin\%$ and $\layerShareMax\%$ of the text; the discipline block is the largest component on every task.
- **P:** Вставка «the intervention the layer is named after» сбивает: слой в статье называется «prescribed-knowledge», а не «tool».
- **R:** The library block is $\layerShareMin\%$ to $\layerShareMax\%$ of the text; the discipline block is the largest block on every task.

### 03_systems.tex:105 · high · абстрактное подлежащее

- **Q:** This matters for attribution: any effect ascribed to tool prescription in an aggregate ablation is at least as likely to originate in the two fixed blocks that travel with it, and those are constant across modalities while the reported effects are not.
- **P:** «This matters» из запрещённого списка, «travel with it» метафора, 43 слова, концовка через отрицание «are not».
- **R:** An ablation that switches the whole layer at once measures all three blocks together. An effect ascribed to tool prescription in such an ablation is at least as likely to come from the hardware and discipline blocks. Those two blocks are identical across modalities; the reported effects differ by modality.

### 03_systems.tex:108 · medium · номинализация

- **Q:** That the two halves behave differently, and that their combination is not the sum of the parts, is shown by measurement in Sections~\ref{sec:grid} and~\ref{sec:kdiscterm}.
- **P:** Подлежащее — два придаточных «that ...», сказуемое в пассиве в конце; «not the sum of the parts» — отрицание без числа.
- **R:** Sections~\ref{sec:grid} and~\ref{sec:kdiscterm} measure the two halves separately and together. On TabReD, averaged over the eight tasks, the library half alone improves the task metric of AutoDS-Tools by 0.69%, the discipline half alone by 0.12%, and both together by 0.72%, 0.09 percentage points below the sum of the two.

### 03_systems.tex:112 · medium · метафора

- **Q:** In FEDOT.LLM the instruction to solve the task through FEDOT \emph{is} the pipeline, so \Ktool{} is welded in and cannot be switched off.
- **P:** «Welded in» метафора, курсивное «is» как ударение и «cannot be switched off» — отрицание там, где достаточно «always on».
- **R:** In FEDOT.LLM the tool prescription is the pipeline itself: every task is solved through FEDOT, so \Ktool{} is always on.

### 03_systems.tex:114 · high · метафора

- **Q:** This is the extreme point of the axis, and it gives Section~\ref{sec:ceiling} its lower anchor: the system whose tool prescription is maximal and non-removable performs worst on the family the prescribed tool was built for.
- **P:** «Lower anchor» и «extreme point» — внутренние координаты; «the family the prescribed tool was built for» вместо слова «tabular»; результат назван без имени системы и без сравнения с бейзлайном.
- **R:** FEDOT.LLM is the end point of the axis and gives Section~\ref{sec:ceiling} its lowest score: the system that fixes its tool most rigidly scores lowest on tabular data, the family FEDOT was built for.

### 03_systems.tex:123 · low · абстрактное подлежащее

- **Q:** Tool prescription is realisable only where the prescribed tool exists, which makes it a property of the environment as much as of the text.
- **P:** «Realisable», «exists», «the text» — абстракции вместо библиотеки, образа контейнера и промпта.
- **R:** A tool prescription works only where the prescribed library is installed, so the prescription is a property of the container image as much as of the prompt.

### 03_systems.tex:124 · medium · внутренний термин без пояснения

- **Q:** The layer states that the specialised library is pre-installed and forbids falling back on general-purpose estimators, so it presumes an image provisioned accordingly; against an image without that library the treatment fails outright.
- **P:** «The layer», «the treatment», «provisioned accordingly» — три внутренних слова в одном предложении из 36 слов; читатель должен помнить, что слой и treatment — одно и то же.
- **R:** The layer tells the agent that the specialised library is pre-installed and forbids a fallback to general-purpose estimators, so it assumes a container image with that library. On an image without it the prescription fails outright.

### 03_systems.tex:130 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** An agent given the prescription there reads the data, writes a correct pipeline, fails at import, and scores zero while having done nothing wrong.
- **P:** Концовка «while having done nothing wrong» — риторический удар вместо факта.
- **R:** An agent given the prescription on that image reads the data, writes a correct pipeline, fails at the import and scores zero.

### 03_systems.tex:133 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** The same holds for the literature: an ablation that prescribes a specialised library measures the prescription only where the provisioning already holds, and otherwise measures the provisioning.
- **P:** Зеркальная пара «measures the prescription ... measures the provisioning» — афористичная концовка, которую надо перечитать.
- **R:** Published ablations face the same confound. Only an image with the prescribed library installed lets an ablation measure the instruction itself; on any other image the score reflects the missing installation.


## figures_systems.tex

### figures_systems.tex:61 · low · метафора

- **Q:** Shaded stages are fixed by the architecture and cannot be renegotiated by the backbone; unshaded stages are where the model actually decides what to do.
- **P:** «Renegotiated by the backbone» — метафора с отрицанием; «actually» из списка авторских ремарок.
- **R:** Shaded stages are fixed by the architecture; in unshaded stages the model decides what to do.

### figures_systems.tex:62 · high · придуманная абстракция

- **Q:** Prescribed structure falls from top to bottom; measured performance does not follow it in either direction. The middle row scores highest and the top row lowest, which is the non-monotonicity of Section~\ref{sec:ceiling}.
- **P:** «Prescribed structure» путается с «prescribed knowledge»; «does not follow it in either direction» — отрицание; «the non-monotonicity of Section 5» — та же абстракция, что в отвергнутом пункте highlights, без имён систем.
- **R:** The share of the pipeline fixed in advance falls from top to bottom. On TabReD, AutoDS-Tools (middle row) scores highest, Terminus-2 (bottom row) second and FEDOT.LLM (top row) lowest (Section~\ref{sec:ceiling}).


## 04_design.tex

### 04_design.tex:10 · medium · внутренний термин без пояснения

- **Q:** \textbf{\Ktool{}} and \textbf{\Kdisc{}}: each on or off, crossed on AutoDS-Tools and Terminus-2; Terminus-2 has no prescription of its own to switch, so the text is appended to its task file instead.
- **P:** «the text» ни к чему не привязан: читатель должен догадаться, что это текст слоя AutoDS-Tools; «instead» даёт контраст вместо утверждения.
- **R:** \Ktool{} and \Kdisc{}: each on or off, crossed on AutoDS-Tools and Terminus-2. Terminus-2 ships no prescription of its own, so the halves of the AutoDS-Tools layer are appended to its task file.

### 04_design.tex:12 · high · перегруженное предложение

- **Q:** \textbf{Backbone}: \texttt{gemma-4-31b-it} throughout, with \texttt{gemma-4-26b-a4b-it} below it and \texttt{glm-4.7} above it on the two agentic systems; the upper point leaves the family because the family has nothing larger, so this axis is read as a capability axis; the upper point differs in family as well as in size.
- **P:** 54 слова, три точки с запятой; «below it / above it» без указания, по какой шкале; «the upper point» — внутренняя координата; мысль про смену семейства повторена дважды.
- **R:** Backbone: \texttt{gemma-4-31b-it} throughout. AutoDS-Tools and Terminus-2 are also run on a smaller model, \texttt{gemma-4-26b-a4b-it}, and a larger one, \texttt{glm-4.7}. The Gemma family has nothing larger than 31B, so the larger model comes from a different family. This axis is therefore read as a capability axis: \texttt{glm-4.7} differs from \texttt{gemma-4-31b-it} in family as well as in size.

### 04_design.tex:16 · medium · внутренний термин без пояснения

- **Q:** \textbf{Starting point}: greenfield, where nothing is supplied, against improve-a-baseline, where a working training script is.
- **P:** Два придуманных термина введены эллипсисом («where a working training script is» требует достроить «is supplied»); «against» как контраст; определение даётся только в 4.2.
- **R:** Starting point: greenfield, where the agent receives the task statement alone, and improve-a-baseline, where it also receives a working training script.

### 04_design.tex:18 · medium · абстрактное подлежащее

- **Q:** Provisioning, the container image, is varied once on Terminus-2 as the nearest thing to a library manipulation that does not touch the instruction.
- **P:** «the nearest thing to a library manipulation that does not touch the instruction» — абстракция с отрицанием; читатель не понимает, что именно меняется.
- **R:** Provisioning, the container image, is varied once, on Terminus-2. Swapping the stock image for the enriched one changes the installed libraries and leaves the instruction unchanged.

### 04_design.tex:25 · medium · внутренний термин без пояснения

- **Q:** A trial is one attempt at one task; TabReD arms cover eight tasks, MLAgentBench arms the ten tasks of the benchmark, of which eight repeat on our hardware (Section~\ref{sec:coverage}). Stock: the benchmark's own image; enriched: the image built for AutoDS-Tools, carrying the libraries its layer names.
- **P:** Подпись не объясняет значения столбца Layer: «welded in», «trimmed», «shipped edition», «cloned edition» определяются только в разделах 3.4, 6 и 7; «eight repeat on our hardware» читается дважды.
- **R:** A trial is one attempt at one task. TabReD arms cover eight tasks; MLAgentBench arms cover the ten tasks of the benchmark, of which eight could be run three times on our hardware (Section~\ref{sec:coverage}). Image: stock is the benchmark's own image; enriched is the image built for AutoDS-Tools, with the libraries its layer names pre-installed. Layer: welded in means the library choice is fixed by the architecture (Section~\ref{sec:axis}); trimmed is the discipline half with its two clauses about training time removed (Section~\ref{sec:kdiscterm}); shipped and cloned are the two editions of the layer text compared in Section~\ref{sec:editions}.

### 04_design.tex:56 · medium · перегруженное предложение

- **Q:** \textbf{TabReD} contributes eight real-world tabular tasks with temporal splits~\citep{rubachev2024tabred} and, more importantly, a published reference table of eighteen methods: gradient boosting implementations, tabular deep learning architectures, ensembles and retrieval-augmented models, each tuned with Optuna on the official validation split and averaged over fifteen seeds.
- **P:** 50 слов с авторской ремаркой «more importantly» (запрещённый маркер); две мысли в одном предложении.
- **R:** TabReD contributes eight real-world tabular tasks with temporal splits~\citep{rubachev2024tabred}. It also publishes a reference table of eighteen methods: gradient boosting implementations, tabular deep learning architectures, ensembles and retrieval-augmented models, each tuned with Optuna on the official validation split and averaged over fifteen seeds.

### 04_design.tex:71 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** The benchmark carries no reference table and none exists in the literature at the granularity we would need, so there is no range to normalise against and no external ceiling to fall short of.
- **P:** Четыре отрицания подряд («no», «none», «no range», «no ceiling»); читатель собирает смысл из того, чего нет.
- **R:** MLAgentBench publishes no reference table, and the literature offers none at the granularity we would need. MLAgentBench scores therefore stay in each task's own metric, with no external ceiling to normalise against.

### 04_design.tex:73 · high · перегруженное предложение

- **Q:** Every MLAgentBench quantity in the paper is a within-study contrast, one branch of a system against another or one architecture against another under conditions we held fixed, and the normalised language of Section~\ref{sec:ceiling} is never carried across.
- **P:** 42 слова; «within-study contrast», «branch of a system», «normalised language ... carried across» — внутренний жаргон; читатель не знает, что такое «ветвь».
- **R:** Every MLAgentBench number in the paper compares two of our own runs under identical conditions, for example AutoDS-Tools with the layer on against the same system with it off, or AutoDS-Tools against Terminus-2 on the same task. The normalised scale of Section~\ref{sec:ceiling} is used for TabReD only.

### 04_design.tex:80 · medium · придуманная абстракция

- **Q:** Their instructions carry the heaviest prescription of any condition in the paper, naming the library, the featurisation, the leakage handling and the baseline to beat, and are read as the far end of the prescription axis.
- **P:** «carry the heaviest prescription», «the far end of the prescription axis» — координаты внутренней оси; читатель не знает, какой конец «дальний».
- **R:** Their instructions prescribe more than any other condition in the paper: the library, the featurisation, the leakage handling and the baseline to beat. They are therefore the most heavily prescribed point on the axis of Section~\ref{sec:axis}.

### 04_design.tex:84 · medium · номинализация

- **Q:** Terminus-2 runs on that text and on the same text with the library section removed, which makes the cases a second crossing of prescription with architecture.
- **P:** «a second crossing of prescription with architecture» — номинализация; первое «скрещивание» не названо, читатель должен вспомнить сетку 2×2 на TabReD.
- **R:** Terminus-2 runs on the full instruction and on the same instruction with the library section removed. The case studies thus cross tool prescription with architecture a second time, after TabReD (Sections~\ref{sec:grid} and~\ref{sec:kdiscterm}).

### 04_design.tex:100 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** Data, splits, metrics and backbone are identical across arms; the installed library set is not, and Section~\ref{sec:matched} measures what it is worth.
- **P:** Контраст через отрицание («is not») и разговорное «what it is worth» без указания, в чём измеряется.
- **R:** Data, splits, metrics and backbone are identical across arms. The installed library set differs between the stock and the enriched image, and Section~\ref{sec:matched} measures the effect of that difference on the score.

### 04_design.tex:109 · high · метафора

- **Q:** A row of Table~\ref{tab:leaderboard} therefore compares deployed systems rather than isolated architectures, and two further arms separate the strands: AutoDS-Tools with the layer switched off, run as a full $2\times2$ over the two halves, and Terminus-2 on the enriched image.
- **P:** «rather than» (запрещено), «separate the strands» — метафора, «the two halves» — читатель должен вспомнить, что это K_tool и K_disc; 44 слова.
- **R:** A row of Table~\ref{tab:leaderboard} therefore compares each system as it is shipped, with its own instruction and its own image. Two further arms isolate the architecture from both: AutoDS-Tools with the layer switched off, run as a full $2\times2$ over \Ktool{} and \Kdisc{}, and Terminus-2 on the enriched image.

### 04_design.tex:117 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** Rather than assume a significance threshold, we measure one.
- **P:** «Rather than» — запрещённый контраст; мысль формулируется прямо.
- **R:** We measure the significance threshold from repeated runs.

### 04_design.tex:117 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** Terminus-2 and AutoDS-Tools were each run three times on every TabReD task, and the two do not share a floor.
- **P:** «do not share a floor» — отрицание вместо утверждения; читатель останавливается, чтобы понять, что «floor» здесь — шумовой порог.
- **R:** Terminus-2 and AutoDS-Tools were each run three times on every TabReD task, and their noise floors differ.

### 04_design.tex:123 · medium · перегруженное предложение

- **Q:** We therefore treat relative differences above $1\%$ as real when comparing the two systems, taking the threshold from the noisier of the pair, and differences above $0.1\%$ as real when comparing configurations of AutoDS-Tools with each other, taking it from that system's worst task.
- **P:** 47 слов, два вложенных деепричастных оборота; два порога и два источника в одном предложении.
- **R:** Between the two systems we therefore treat a relative difference above $1\%$ as real, a threshold set by the noisier system, Terminus-2. Between configurations of AutoDS-Tools we treat a difference above $0.1\%$ as real, a threshold set by its noisiest task.

### 04_design.tex:136 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** MLAgentBench has a noise floor nothing like the tabular one.
- **P:** «nothing like» — разговорный оборот через отрицание; не сказано, в какую сторону отличается.
- **R:** MLAgentBench has a far wider noise floor than TabReD.

### 04_design.tex:136 · high · число без единицы

- **Q:** Every cell there was run three times, sixty trials across the two branches of the layer ablation, twenty-four for the second architecture and twenty-four for the second edition of the layer, and three attempts of one configuration span $\mlabOgbnOffLo$ to $\mlabOgbnOffHi$ on \texttt{ogbn-arxiv} and $0.0844$ to $0.3846$ on \texttt{fathomnet}.
- **P:** 56 слов; «две ветви», «вторая архитектура», «вторая редакция» — внутренние координаты; числа без метрики. По таблице mlabhead разброс 0.2237–0.4790 на ogbn-arxiv принадлежит AutoDS-Tools без слоя, а 0.0844–0.3846 на fathomnet — Terminus-2, то есть это две разные конфигурации, а не «одна».
- **R:** Every MLAgentBench cell was run three times: sixty trials for AutoDS-Tools with the layer on and off, twenty-four for Terminus-2 and twenty-four for AutoDS-Tools under the cloned edition of the layer (Section~\ref{sec:editions}). Three attempts of one cell can span 0.2237 to 0.4790 in accuracy, AutoDS-Tools without the layer on \texttt{ogbn-arxiv}, or 0.0844 to 0.3846 in micro-F1, Terminus-2 on \texttt{fathomnet}.

### 04_design.tex:141 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** A difference on this benchmark is worth reading only when it exceeds a spread of that size, so Section~\ref{sec:mlab} rests on cells that go to zero; cells that move by less than that spread are read as unchanged.
- **P:** «cells that go to zero» — внутреннее сокращение (ячейки, где результат падает до нуля); «worth reading» — разговорно.
- **R:** A difference on this benchmark is read as real only when it exceeds a spread of that size. Section~\ref{sec:mlab} therefore rests on cells in which a configuration produces no submission at all; a cell that moves by less than the spread is read as unchanged.

### 04_design.tex:144 · medium · внутренний термин без пояснения

- **Q:** On TabReD a trial that reaches the task ceiling has written nothing.
- **P:** «ceiling» здесь означает лимит времени, а в остальной статье — потолок качества по справочной таблице; один термин на два понятия. «lost trial» в предыдущем предложении не определён.
- **R:** Repetition also changed how a lost trial, one that ends with no submission, is counted. On TabReD a trial that exhausts its budget has written no submission.

### 04_design.tex:155 · high · прочее (отрицание, афоризм, ремарка)

- **Q:** Coverage across the three systems is uneven, and the unevenness is a result not a gap (Table~\ref{tab:coverage}).
- **P:** «a result not a gap» — контраст через отрицание и афоризм; суть (архитектура FEDOT.LLM определяет, какие задачи ей доступны) не сказана.
- **R:** Coverage across the three systems is uneven (Table~\ref{tab:coverage}), and every absence follows from the architecture of FEDOT.LLM.

### 04_design.tex:162 · medium · абстрактное подлежащее

- **Q:** The architecture that performs worst on the tasks it can attempt is also the one that can attempt the fewest, and both properties follow from the same design decision.
- **P:** Подлежащее — описательная конструкция вместо имени системы; «the same design decision» не названо, читатель должен восстановить, что речь о закреплённой табличной библиотеке.
- **R:** FEDOT.LLM performs worst on the tasks it can attempt and can attempt the fewest, and both follow from one decision: the pipeline is built around FEDOT, a tabular AutoML library, so the library choice is fixed.

### 04_design.tex:192 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** The five-epoch starter script finishes there; nothing that improves on it does.
- **P:** Эллиптическая концовка-«ударник»; «does» требует достроить «finishes», «there» — достроить «within the budget on the CPU».
- **R:** On the CPU the five-epoch starter script finishes within the budget; every attempt to train a better model runs out of time.

### 04_design.tex:207 · low · метафора

- **Q:** Both sets are released, so the difference between them can be read as the price of the preparation.
- **P:** «the price of the preparation» — метафора; читатель ждёт доллары.
- **R:** Both sets are released, so the difference between them measures the effect of the data preparation.

### 04_design.tex:208 · medium · метафора

- **Q:** The earlier comparison also differed in what was installed, the AutoDS-Tools arm carrying the libraries its prescription names while the others used the stock image; Section~\ref{sec:matched} closes that axis directly.
- **P:** «closes that axis» — метафора; «carrying the libraries its prescription names» вместо уже введённого термина «enriched image».
- **R:** The earlier comparison also differed in the installed libraries: the AutoDS-Tools arm ran on the enriched image and the other arms on the stock image. Section~\ref{sec:matched} measures that difference by running Terminus-2 on the enriched image.

### 04_design.tex:214 · medium · перегруженное предложение

- **Q:** The enriched image brings LightGBM as a dependency, but the base image ships no OpenMP runtime and the wheel carries none, so the import succeeds and the failure arrives inside the fit as a broken worker pool that reads as a modelling error.
- **P:** 45 слов, цепочка из четырёх союзов; причина и симптом в одном предложении.
- **R:** The enriched image installs LightGBM as a dependency, but the base image and the LightGBM wheel both lack an OpenMP runtime. The import therefore succeeds, and the failure appears inside the fit as a broken worker pool that looks like a modelling error.

### 04_design.tex:217 · medium · внутренний термин без пояснения

- **Q:** Forty-five trials met it, twenty-two of twenty-four AutoDS-Tools trials and twenty-three of twenty-four matched-provisioning trials, and all forty-five diagnosed and repaired it in a single step, so it went unnoticed until we read the traces.
- **P:** «matched-provisioning trials» — внутренняя координата (Terminus-2 на обогащённом образе), нигде в разделе не введена; 40 слов.
- **R:** Forty-five trials met it: twenty-two of twenty-four AutoDS-Tools trials and twenty-three of twenty-four Terminus-2 trials on the enriched image. All forty-five diagnosed and repaired it in a single step, so it went unnoticed until we read the traces.


## 05_results_tabred.tex

### 05_results_tabred.tex:17 · medium · внутренний термин без пояснения

- **Q:** The three architectures on the normalised TabReD scale, one backbone throughout. Ticks above the line are the eighteen published methods; the two AutoDS-Tools points differ only in whether its layer is applied.
- **P:** Подпись к рисунку читается отдельно от текста: «its layer» не назван, а «normalised scale» не расшифрована, читатель не знает, что такое 0 и 1 и какой слой включён.
- **R:** The three architectures on the normalised TabReD scale, one backbone throughout: 0 is the weakest and 1 the strongest of the eighteen published methods on each task. Ticks above the line mark those methods. The two AutoDS-Tools points differ only in whether the prescribed-knowledge layer is applied.

### 05_results_tabred.tex:23 · low · число без единицы

- **Q:** Per-task normalised score on TabReD. Bold marks the best value per task within each block; the last column is the mean over tasks.
- **P:** Подпись не говорит, что означают 0 и 1 на тепловой карте; рисунок на всю ширину читают отдельно от абзаца, где шкала определена.
- **R:** Per-task score on TabReD, normalised so that 0 is the weakest and 1 the strongest of the eighteen published methods on that task. Bold marks the best value per task within each block; the last column is the mean over the eight tasks.

### 05_results_tabred.tex:31 · medium · внутренний термин без пояснения

- **Q:** With the backbone fixed, the architecture moves the normalised mean from $\nFedot$ for FEDOT.LLM to $\nAutoDS$ for AutoDS-Tools as deployed, with Terminus-2 at $\nTerminus$ between them (Figure~\ref{fig:position}).
- **P:** «As deployed» употреблено как термин без пояснения; читатель не знает, чем эта конфигурация отличается от остальных, хотя различие (файл инструкции) определяет всё дальнейшее.
- **R:** With the backbone fixed, the architecture moves the normalised mean from 0.26 for FEDOT.LLM to 0.85 for AutoDS-Tools as deployed, with its prescribed-knowledge layer on, and Terminus-2 at 0.72 between them (Figure~\ref{fig:position}).

### 05_results_tabred.tex:35 · high · число без единицы

- **Q:** Part of the spread belongs to the prescribed-knowledge layer: without the layer AutoDS-Tools scores $\nAutoDSOff$, so the span attributable to architecture alone is $\spanArch$ against $\spanShip$ for the systems as they ship.
- **P:** «Span» 0.49 и 0.59 даны без указания, разность каких чисел это; читатель должен сам вычесть 0.26 из 0.75 и из 0.85, а «as they ship» снова не расшифровано.
- **R:** Part of the spread belongs to the prescribed-knowledge layer: without the layer AutoDS-Tools scores 0.75. The span attributable to architecture alone is therefore 0.49 (0.26 to 0.75), against 0.59 (0.26 to 0.85) for the systems as deployed.

### 05_results_tabred.tex:44 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** AutoDS-Tools at $\nAutoDS$ lands inside the gradient-boosting band, not below it: level with LightGBM at $\nLGBM$, ahead of CatBoost at $\nCat$, and $\gapXGB$ short of XGBoost.
- **P:** «Not below it» - контраст через отрицание; «gradient-boosting band» - самодельный термин для трёх настроенных бустингов.
- **R:** AutoDS-Tools at $\nAutoDS$ sits among the three tuned gradient-boosting methods: level with LightGBM at $\nLGBM$, ahead of CatBoost at $\nCat$, and $\gapXGB$ below XGBoost at $\nXGB$.

### 05_results_tabred.tex:46 · high · абстрактное подлежащее

- **Q:** The boundary is therefore narrower than the usual one.
- **P:** Подлежащее «the boundary» и сравнение с «the usual one» без референтов: читатель не понимает, граница чего и с чем сравнивается.
- **R:** The remaining gap to tuned gradient boosting is therefore small: 0.02 on the normalised scale to tuned XGBoost.

### 05_results_tabred.tex:60 · medium · метафора

- **Q:** What survives the whole interval is what we use: at its most favourable corner FEDOT.LLM remains $\fedotBestCornerBelowTerminus$ of the normalised range below Terminus-2, $\fedotBestCornerBelowAutoDS$ below AutoDS-Tools, and below every tuned gradient-boosting baseline.
- **P:** «Most favourable corner» и «what survives the interval» - образы вместо описания процедуры; читатель должен вспомнить, что интервал - это интервал округления до двух знаков.
- **R:** We rely only on what holds across the whole rounding interval. Even with every task rounded in its favour, FEDOT.LLM stays $\fedotBestCornerBelowTerminus$ of the normalised range below Terminus-2, $\fedotBestCornerBelowAutoDS$ below AutoDS-Tools, and below every tuned gradient-boosting baseline.

### 05_results_tabred.tex:64 · high · придуманная абстракция

- **Q:** This point is the lower anchor of the architectural axis, and its position sets the axis's length.
- **P:** «Lower anchor», «architectural axis», «axis's length» - внутренние координаты статьи; читатель не понимает, какая величина измеряется и от чего.
- **R:** FEDOT.LLM is the weakest of the three architectures, so the span we attribute to architecture, $\spanArch$, is measured from its score.

### 05_results_tabred.tex:69 · high · число без единицы

- **Q:** \paragraph{Observation 1} With one open 31B backbone, architecture alone moves the normalised score from $\nFedot$ to $\nAutoDSOff$, and the deployed multi-agent system reaches $\nAutoDS$: level with tuned LightGBM, ahead of tuned CatBoost, and $\gapXGB$ short of tuned XGBoost.
- **P:** Итоговое наблюдение оперирует числами 0.26 и 0.75 без единицы и словом «deployed» без расшифровки; читатель, открывший статью на этом абзаце, не поймёт, что они значат.
- **R:** With one open 31B backbone, architecture alone moves the normalised mean from 0.26 for FEDOT.LLM, next to linear regression at 0.28, to 0.75 for AutoDS-Tools without its layer. With the layer on, AutoDS-Tools reaches 0.85: level with tuned LightGBM, ahead of tuned CatBoost, and 0.02 short of tuned XGBoost.

### 05_results_tabred.tex:77 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** The system that ranks highest is neither the most nor the least constrained.
- **P:** «Neither ... nor» - запрещённый контраст через отрицание; система не названа, «constrained» без указания, чем ограничена.
- **R:** The system that ranks highest, AutoDS-Tools, sits between the rigid pipeline and the open harness in how much its design constrains the model.

### 05_results_tabred.tex:78 · medium · абстрактное подлежащее

- **Q:** Read as deployed, the relationship is an inverted U: FEDOT.LLM at $\nFedot$, AutoDS-Tools at $\nAutoDS$, Terminus-2 at $\nTerminus$.
- **P:** Подлежащее «the relationship» и образ «inverted U» вместо прямого перечисления; «as deployed» снова без пояснения.
- **R:** As deployed, FEDOT.LLM scores 0.26, AutoDS-Tools 0.85 and Terminus-2 0.72: the score rises from the pipeline to the six-agent system and falls again for the open harness.

### 05_results_tabred.tex:83 · low · метафора

- **Q:** Two arms separate those strands.
- **P:** «Strands» - образ; «arms» читатель должен помнить из таблицы раздела 4, а что именно разделяется (файл инструкции и образ контейнера), сказано только в предыдущем предложении.
- **R:** Two arms separate the layer from the image.

### 05_results_tabred.tex:85 · low · перегруженное предложение

- **Q:** With the layer removed, the \emph{untreated} cell of Table~\ref{tab:grid} on the same tasks and image, AutoDS-Tools scores $\nAutoDSOff$ against $\nAutoDS$ as deployed, with Terminus-2 at $\nTerminus$.
- **P:** Вставка «the untreated cell of Table 3 on the same tasks and image» посреди предложения разрывает подлежащее и сказуемое; «as deployed» третий раз без пояснения.
- **R:** With the layer removed (the untreated cell of Table~\ref{tab:grid}, same tasks and image), AutoDS-Tools scores 0.75 against 0.85 as deployed, and Terminus-2 scores 0.72.

### 05_results_tabred.tex:88 · high · число без единицы

- **Q:** The ordering survives the separation and the distance does not: $\gapAgentsShip$ as deployed becomes $\gapAgentsOff$ once neither system carries a prescription, so on these tasks the layer is worth about \layerOverArch{} times the architectural difference between the two agentic systems.
- **P:** Контраст через отрицание, разности 0.13 и 0.03 без указания, разности чего, и разговорное «worth about 3 times»; читатель должен сам восстановить 0.10.
- **R:** AutoDS-Tools stays ahead of Terminus-2 with the layer and without it, and the margin shrinks: 0.13 on the normalised scale as deployed, 0.03 without the layer. The layer therefore accounts for 0.10 of the 0.13, about three times the 0.03 that the architecture accounts for.

### 05_results_tabred.tex:91 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** Neither the distance to FEDOT.LLM nor the gap to XGBoost is affected.
- **P:** «Neither ... nor» и два расстояния без указания, от чего они отсчитаны.
- **R:** The gap of 0.02 from AutoDS-Tools as deployed to tuned XGBoost, and the lead of both agentic systems over FEDOT.LLM, are unchanged.

### 05_results_tabred.tex:106 · high · метафора

- **Q:** Averaged over the tasks the library half is worth $\gridToolMean\%$, the discipline half $\gridDiscMean\%$, and their interaction $\gridInteraction\%$: one intervention and one piece of ballast.
- **P:** «Ballast» и концовка-ударник; «interaction -0.09%» не объяснено как разность суммы половин и совместного эффекта; «library half / discipline half» - третья пара имён для K_tool / K_disc.
- **R:** Averaged over the eight tasks, naming the library (\Ktool{}) improves the metric by $\gridToolMean\%$, prescribing the training discipline (\Kdisc{}) by $\gridDiscMean\%$, and both together by $\gridBothMean\%$, below the $\gridSumHalves\%$ sum of the two (interaction $\gridInteraction\%$). The library instruction carries the effect and the discipline instruction adds almost nothing on top of it.

### 05_results_tabred.tex:112 · low · перегруженное предложение

- **Q:** No other task moves by more than $\gridToolRestMax\%$, and five of the six stay within half a percent, at or below what the same cell reproduces across its own three attempts.
- **P:** Хвост «at or below what the same cell reproduces across its own three attempts» требует второго прочтения, чтобы понять, что речь о разбросе между повторами.
- **R:** No other task moves by more than 0.64%, and five of the six move by less than half a percent, within the spread of the same cell across its own three attempts.

### 05_results_tabred.tex:125 · high · число без единицы

- **Q:** \paragraph{Observation 2} Of the $\gapAgentsShip$ that separates the two agentic systems as shipped, $\layerWorthNorm$ is the prescribed-knowledge layer and $\gapAgentsOff$ the architecture; the ordering survives the separation, the margin does not.
- **P:** Три числа нормированной шкалы без единицы, «as shipped» без пояснения и зеркальная пара с отрицанием «survives ... does not» в итоговом наблюдении.
- **R:** As deployed, AutoDS-Tools leads Terminus-2 by 0.13 on the normalised scale. Of that, 0.10 comes from the prescribed-knowledge layer and 0.03 from the architecture, so with the layer off AutoDS-Tools stays ahead by 0.03.

### 05_results_tabred.tex:142 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** Provisioning without a text that points at it changes the container and not the run.
- **P:** «X and not Y» - контраст через отрицание; «a text that points at it» - размытая формулировка для инструкции, называющей библиотеку.
- **R:** Provisioning a library that no instruction names changes only the container; the agent's run is the same as on the stock image.

### 05_results_tabred.tex:152 · high · прочее (отрицание, афоризм, ремарка)

- **Q:** The behaviour is the finding: provisioning is inert as a treatment because the agents rebuild the environment, and a system that installs what it needs cannot be studied by installing it in advance.
- **P:** «The behaviour is the finding» - афоризм из списка запрещённых; «inert as a treatment» - медицинская метафора; концовка-ударник.
- **R:** These forty-five repairs explain why provisioning has no measurable effect: the agents rebuild the environment they need, so installing a library in advance changes nothing for a system that installs its own libraries.

### 05_results_tabred.tex:157 · medium · число без единицы

- **Q:** The one exception is \texttt{sberbank-housing}, at $\matchedSberbank\%$ with a spread of $\matchedSberbankSD$ across attempts against $0.001$ or less elsewhere.
- **P:** «Spread of 0.017» без единицы (это RMSE), и «-3.49%» без указания, что минус означает ухудшение.
- **R:** The one exception is \texttt{sberbank-housing}, where the enriched image scores 3.49% worse and the three attempts have a standard deviation of 0.017 RMSE, against 0.001 or less elsewhere.

### 05_results_tabred.tex:177 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** The backbone changes the deliberation, not the artefact.
- **P:** «X, not Y» - запрещённый контраст; «artefact» здесь означает итоговую модель, что читатель должен угадать.
- **R:** The backbone changes the deliberation and leaves the final model unchanged.

### 05_results_tabred.tex:188 · medium · придуманная абстракция

- **Q:** On the normalised scale the backbone axis spans $0.24$ under Terminus-2 and $0.04$ under AutoDS-Tools, against $\spanArch$ for the architectures at a fixed backbone once prescription is taken out.
- **P:** «The backbone axis spans» - внутренняя координата; читатель не знает, что «span» - разброс среднего между тремя моделями, и с чем сравниваются 0.49.
- **R:** On the normalised scale the three backbones differ by up to 0.24 in mean score under Terminus-2 and by 0.04 under AutoDS-Tools; the three architectures on one backbone, with the layer removed, differ by 0.49.

### 05_results_tabred.tex:190 · high · число без единицы

- **Q:** The larger of the two is not a broad effect: $0.30$ of that $0.24$ comes from \texttt{sberbank-housing} alone, and the remaining seven tasks move the mean the other way by $+0.07$.
- **P:** «0.30 of that 0.24» - часть больше целого, читатель спотыкается; знаки не объяснены; «not a broad effect» - отрицание вместо утверждения.
- **R:** The $0.24$ under Terminus-2 comes from one task: \texttt{sberbank-housing} alone moves the mean by $0.30$, and the other seven tasks together move it the other way by $0.07$.

### 05_results_tabred.tex:192 · medium · придуманная абстракция

- **Q:** Architecture is the larger term by a factor of two against the worse-behaved backbone axis and twelve against the other.
- **P:** «Larger term», «worse-behaved backbone axis» - читатель должен восстановить, что сравниваются 0.49 с 0.24 и с 0.04.
- **R:** Architecture moves the mean about twice as far as the backbone does under Terminus-2 (0.49 against 0.24) and twelve times as far as it does under AutoDS-Tools (0.49 against 0.04).

### 05_results_tabred.tex:194 · high · метафора

- **Q:** Where accuracy does move, it moves both ways on the hinge this paper is about: a stronger backbone exercises more discretion, and discretion departs from the gradient-boosting default.
- **P:** «Hinge» и «discretion» - образы; читатель не знает, о каком «шарнире» речь и что значит «moves both ways on» него.
- **R:** Where accuracy does move, the cause is the same in both directions: a stronger backbone more often chooses a model other than the gradient-boosting default.

### 05_results_tabred.tex:200 · high · метафора

- **Q:** Prescription and backbone are two levers on one hinge, whether the default being overridden was right to begin with.
- **P:** «Levers», «hinge» - метафоры; придаточное «whether ...» повисает без главного предложения, фраза грамматически не закончена.
- **R:** Prescription and backbone both act on one decision, whether the agent keeps the gradient-boosting default or overrides it, and the sign of the outcome depends on whether that default suited the task.

### 05_results_tabred.tex:209 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** Trials cut at the time limit move the same way, at \axAutoDSRefCutPct{}, \axAutoDSSmallCutPct{} and \axAutoDSBigCutPct{} per cent.
- **P:** Три процента без привязки к моделям; читатель должен сопоставить их порядок с порядком в предыдущем предложении.
- **R:** Trials cut at the time limit follow the same pattern: 17% at the reference model, 29% at the smaller model and 50% at the stronger one.

### 05_results_tabred.tex:212 · medium · перегруженное предложение

- **Q:** A stronger model does not make that architecture finish sooner; it gives the six agents more to say inside a fixed hour, and when the clock is the binding constraint a better backbone buys nothing the clock will let the system deliver.
- **P:** Отрицание в зачине, 43 слова, метафоры «buys», «the clock will let» и афористичная концовка.
- **R:** A stronger model makes the six agents of AutoDS-Tools exchange more text inside the same hour. More trials then reach the time limit, and accuracy is unchanged.

### 05_results_tabred.tex:222 · medium · метафора

- **Q:** And the axis has a floor, which we found by hitting it.
- **P:** «Axis has a floor», «found by hitting it» - образы; читатель не знает, какая ось и что значит «пол».
- **R:** The backbone comparison also has a lower limit.

### 05_results_tabred.tex:226 · medium · абстрактное подлежащее

- **Q:** Below some level of capability the question this axis asks has no answer, and that level is above what a parameter count would suggest.
- **P:** «The question this axis asks» - абстракция; читатель должен восстановить, что речь о невозможности сравнить точность, если модель не выдаёт результата.
- **R:** Below some level of capability a backbone returns no usable submission, so its accuracy cannot be compared, and that level is higher than the parameter count alone would suggest.

### 05_results_tabred.tex:229 · medium · перегруженное предложение

- **Q:** \paragraph{Observation 3} Provisioning the image without a text that points at it changes nothing measurable, and swapping the backbone across a \axPriceSpread-fold price range moves accuracy by a fraction of a percent while moving reliability and cost in opposite directions for the two architectures.
- **P:** 45 слов и три утверждения в одном предложении итогового наблюдения; «a text that points at it» - размытая формулировка.
- **R:** Provisioning the image with libraries that no instruction names changes nothing measurable. Swapping the backbone across a 13-fold price range moves accuracy by a fraction of a percent. The same swap moves reliability and cost in opposite directions for the two architectures.

### 05_results_tabred.tex:248 · high · перегруженное предложение

- **Q:** The orderings of accuracy and cost disagree, and by different amounts in different columns: on the common adapter AutoDS-Tools spends $\costRatioDollars\times$ the dollars of Terminus-2 and $\costRatioIn\times$ its input tokens, which is nothing, against $\costRatioOut\times$ its output tokens and $\costRatioMin\times$ its wall-clock, which is not.
- **P:** 50 слов, абстрактное подлежащее «the orderings», зеркальная пара «which is nothing / which is not» и «common adapter» без пояснения.
- **R:** Accuracy and cost rank the two systems differently, and the size of the cost difference depends on what is counted. On the same data adapter AutoDS-Tools spends $\costRatioDollars\times$ the dollars of Terminus-2 and $\costRatioIn\times$ its input tokens, $\costRatioOut\times$ its output tokens and $\costRatioMin\times$ its wall-clock. The first two ratios are negligible; the last two are large.

### 05_results_tabred.tex:261 · medium · метафора

- **Q:** On the common adapter the money goes the other way and only the time agrees: Table~\ref{tab:grid} has the bill falling from $\gridNeitherCost$ to $\gridBothCost$ dollars a trial while the median trial rises from $\gridNeitherMin$ to $\gridBothMin$ minutes.
- **P:** «The money goes the other way and only the time agrees» - образ вместо прямого утверждения о знаках двух величин.
- **R:** On the same data adapter the layer lowers the bill, the opposite of the earlier rows: Table~\ref{tab:grid} has it falling from 0.0086 to 0.0074 dollars a trial. The median trial rises from 15.4 to 38.9 minutes.

### 05_results_tabred.tex:268 · low · метафора

- **Q:** What binds is the clock (Figure~\ref{fig:walltime}).
- **P:** «Binds» без дополнения и афористичный зачин абзаца.
- **R:** The binding limit is the one-hour ceiling per task (Figure~\ref{fig:walltime}).

### 05_results_tabred.tex:272 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** A killed trial and a lost trial are not the same thing: \rerunCutScored{} of the \rerunCut{} had already written a submission and are scored like any other, and \rerunLost{} had not.
- **P:** Определение через отрицание («not the same thing», «had not»); «killed» и «cut» - два слова для одного понятия.
- **R:** A cut trial can still count: 3 of the 4 had already written a submission and are scored like any other trial, and 1 had written nothing and is lost.

### 05_results_tabred.tex:276 · medium · перегруженное предложение

- **Q:** We count the lost trial as a failure and exclude it from the mean, since a timeout says how long the budget was and nothing about the model (Section~\ref{sec:threats}), and note that truncation falls on the slowest tasks and is therefore not random with respect to the result.
- **P:** 47 слов, две вложенные оговорки и два отрицания в одном предложении.
- **R:** We count the lost trial as a failure and exclude it from the mean, because a timeout measures the budget and says nothing about the model (Section~\ref{sec:threats}). Truncation falls on the slowest tasks, so it depends on the result.

### 05_results_tabred.tex:279 · high · метафора

- **Q:** An architecture averaging forty minutes where another averages five buys its accuracy partly with a margin it does not have.
- **P:** «Buys its accuracy with a margin it does not have» - образ и афоризм; системы не названы, читатель не понимает, что речь о запасе до часового лимита.
- **R:** AutoDS-Tools averages forty minutes a trial where Terminus-2 averages five, so part of its accuracy depends on time close to the one-hour limit, and \rerunCut{} of its twenty-four trials were cut by that limit.

### 05_results_tabred.tex:296 · medium · метафора

- **Q:** \paragraph{Observation 4} Accuracy is bought with the clock: on the common adapter AutoDS-Tools spends $\costRatioMin\times$ the wall-clock of Terminus-2 for $\costRatioDollars\times$ the money, and what it runs into is the one-hour task ceiling.
- **P:** «Bought with the clock», «runs into» - образы в итоговом наблюдении; «common adapter» без пояснения.
- **R:** The cost of AutoDS-Tools' accuracy is wall-clock time: on the same data adapter it uses 8.7 times the wall-clock of Terminus-2 at 1.07 times the dollars, and the limit it meets is the benchmark's one-hour ceiling per task.


## grid.tex

### grid.tex:3 · medium · внутренний термин без пояснения

- **Q:** The prescribed-knowledge layer split into its halves on AutoDS-Tools over TabReD, twenty-four trials per cell on one image and one machine. The untreated cell is given in the task's own units; the other three as relative change against it, positive is better.
- **P:** «Its halves» в подписи не названы, а в шапке таблицы стоят K_tool и K_disc; «untreated» не расшифровано как ячейка без инструкции.
- **R:** The prescribed-knowledge layer split into its two halves, which library to use ($K_{\text{tool}}$) and how to train and validate ($K_{\text{disc}}$), on AutoDS-Tools over TabReD, twenty-four trials per cell on one image and one machine. The untreated cell, with the layer off, is given in the task's own metric; the other three columns give the relative change against it, positive is better.


## axis.tex

### axis.tex:23 · low · внутренний термин без пояснения

- **Q:** Lost: no metric returned. Cut: stopped at the time limit, which does not always lose the trial; not recorded per trial for the open harness, which finishes far inside it. The upper AutoDS-Tools cell is eight trials, one per task (Section~\ref{sec:modelaxis}).
- **P:** «The open harness» вместо Terminus-2 и «the upper AutoDS-Tools cell» вместо имени строки: читатель должен угадать, о какой строке речь.
- **R:** Lost: no metric returned. Cut: stopped at the time limit; a cut trial that had already written a submission is still scored. Terminus-2 finishes far inside the limit, so cuts are not recorded for it. The \texttt{glm-4.7} row of AutoDS-Tools has eight trials, one per task (Section~\ref{sec:modelaxis}).


## 06_results_mlab.tex

### 06_results_mlab.tex:1 · low · внутренний термин без пояснения

- **Q:** \section{Results on MLAgentBench: the same layer at a different starting point}
- **P:** Заголовок читают из оглавления; «the layer» и «starting point» вне контекста разделов 3 и 4 ничего не говорят.
- **R:** Results on MLAgentBench: the same prescription when a working script is supplied

### 06_results_mlab.tex:7 · high · придуманная абстракция

- **Q:** The ordering of Section~\ref{sec:ceiling} does not follow architectural weight: the most constrained system performs worst and the best of the three sits between the extremes.
- **P:** «Architectural weight» нигде не определён как величина, и утверждение дано через отрицание; «самая ограниченная система» и «лучшая из трёх» читатель должен расшифровать сам.
- **R:** Section~\ref{sec:ceiling} ranks the three systems on TabReD as AutoDS-Tools first, Terminus-2 second and FEDOT.LLM last. On the prescription axis of Section~\ref{sec:axis} FEDOT.LLM prescribes the most and Terminus-2 the least, so the system that prescribes the most scores worst and the one in the middle scores best.

### 06_results_mlab.tex:9 · medium · абстрактное подлежащее

- **Q:** We propose a sharper statement, which this section tests: constraint pays where it removes a decision the weak model reliably gets wrong, and everywhere else it removes exploration the model could have recovered from.
- **P:** Подлежащее «constraint» абстрактно, «pays» метафора платы; читатель не видит, какая инструкция и какая модель имеются в виду.
- **R:** This section tests a sharper statement. A prescribed decision helps where the 31B model, left to itself, reliably chooses wrongly. Everywhere else it removes exploration from which the model would have recovered on its own.

### 06_results_mlab.tex:12 · medium · внутренний термин без пояснения

- **Q:** MLAgentBench supplies what TabReD does not, a working training script in every task, so a default is already in place before the agent starts. This is the second starting point of the design, and the section answers RQ3 under it.
- **P:** Контраст через отрицание, «a default» без уточнения, «второй стартовый пункт дизайна» — внутренняя координата статьи.
- **R:** Every MLAgentBench task supplies a working training script, so the agent begins from an existing model, where on TabReD it begins from the data alone. Section~\ref{sec:design} calls these the two starting points, and this section answers RQ3 for the second.

### 06_results_mlab.tex:25 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** The earlier Terminus-2 figures mixed single trials from two jobs under different verifier glue, so we re-ran the whole set.
- **P:** «Jobs» и «verifier glue» — жаргон инфраструктуры; не сказано, о каких «earlier figures» речь.
- **R:** Our earlier Terminus-2 numbers on this benchmark came from single trials in two separate batches with two versions of the scoring code, so we re-ran the whole set.

### 06_results_mlab.tex:33 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** What the table adds is the size of the second half. Terminus-2 takes about a third of the mean wall-clock per trial and reaches its agent budget once in $24$ trials where AutoDS-Tools reaches it $13$ times in $30$; it also fails to submit more often, $\headMissTerminus$ attempts of $24$ against $\headMissAutoDS$. Neither of those is visible in a table of scores.
- **P:** «Размер второй половины» отсылает к предыдущей фразе, и читатель возвращается; «agent budget» не пояснён, «13 из 30» при 24 испытаниях в таблице требует оговорки; концовка через отрицание.
- **R:** The table also shows the size of the cost difference. Terminus-2's mean wall-clock per trial is about a third of AutoDS-Tools' (19.1 against 63.2 minutes), and it runs out of the task's time budget in 1 of 24 trials, where AutoDS-Tools does so in 13 of 30 over all ten tasks. Terminus-2 also leaves no submission more often, in 6 attempts of 24 against 2 of 24. A table of scores alone would hide both differences.

### 06_results_mlab.tex:40 · medium · внутренний термин без пояснения

- **Q:** \paragraph{Observation 5} Under one job, one verifier and three attempts per task, AutoDS-Tools takes \headWinsAutoDS{} of \headTasks{} tasks and Terminus-2 \headWinsTerminus{}; Terminus-2 is the faster of the two and the one that more often returns nothing.
- **P:** «One job, one verifier» — термины инфраструктуры без пояснения; «Terminus-2 2» читается как опечатка; «returns nothing» разговорно, а числа скорости и потерь в наблюдении не названы.
- **R:** Run in one batch with one scorer and three attempts per task, AutoDS-Tools is better on 4 of the 8 MLAgentBench tasks and Terminus-2 on 2; the remaining two are within the 5% margin of the table. Terminus-2 is faster (median 6.1 against 10.9 minutes per trial) and leaves no submission more often (6 attempts of 24 against 2).

### 06_results_mlab.tex:58 · medium · внутренний термин без пояснения

- **Q:** \caption{The layer ablation of Table~\ref{tab:ktool}, one bar per task. On three tasks the treated branch produced no submission in any attempt.}
- **P:** «Treated branch» требует помнить, что «treated» значит «с предписанием»; подпись не говорит, какая величина отложена по оси.
- **R:** Effect of the prescription on AutoDS-Tools over the MLAgentBench tasks of Table~\ref{tab:ktool}, one bar per task. A bar is the change in mean score with the prescription divided by the larger of the two means, positive where the prescription helps. On \texttt{clrs}, \texttt{feedback} and \texttt{fathomnet} no attempt with the prescription produced a submission.

### 06_results_mlab.tex:62 · medium · абстрактное подлежащее

- **Q:** Measured three times per cell, the effect splits the tasks into two groups of very unequal weight (Figure~\ref{fig:signflip}).
- **P:** Подлежащее «the effect»; «неравный вес» групп не сказано чего; читатель ждёт чисел, а получает образ.
- **R:** With three attempts per cell, the prescription removes the whole result on three tasks and improves one by a clear margin (Figure~\ref{fig:signflip}).

### 06_results_mlab.tex:64 · medium · внутренний термин без пояснения

- **Q:** On \texttt{clrs} the untreated branch scores $\mlabClrsOff$ pointer accuracy over three attempts, while the treated branch submits nothing in three, every attempt exhausting the task's agent budget.
- **P:** «Untreated/treated branch» вместо «без/с предписанием»; «agent budget» не пояснён как лимит времени задачи.
- **R:** Without the prescription AutoDS-Tools scores 0.3909 pointer accuracy on clrs, mean of three attempts; with it, all three attempts run out of the task's time budget and submit nothing.

### 06_results_mlab.tex:72 · medium · метафора

- **Q:** The paying side is thinner than the shape of the split suggests.
- **P:** «Paying side» и «shape of the split» — метафоры; смысл (выигрыш меньше, чем кажется по рисунку) приходится восстанавливать.
- **R:** The gains are smaller than the figure suggests.

### 06_results_mlab.tex:74 · medium · число без единицы

- **Q:** \texttt{identify-contrails} moves the same way, $\mlabContrailsOff$ to $\mlabContrailsOn$, but both figures sit near zero on a metric whose useful range does not, so the normalised $+0.96$ in the table is an artefact of dividing by a small number and we do not read it as a result.
- **P:** 47 слов с двумя вложенными оборотами; «normalised +0.96» — величина без определения (формула Δ в статье не дана); «whose useful range does not» — эллипсис.
- **R:** \texttt{identify-contrails} also rises, from Dice 0.0022 to 0.0478. Both values sit near the floor of a metric whose useful range lies far above zero, so the $\Delta$ of +0.96 in Table~\ref{tab:ktool} comes from dividing by a small number and we discount it.

### 06_results_mlab.tex:80 · high · придуманная абстракция

- **Q:** Prescription is an override: here its cost is large, repeatable and total on \mlabWiped{} tasks, while its benefit is defensible on one of eight. FEDOT.LLM is the limiting case, permanently in override mode, which agrees with its position at the bottom of Table~\ref{tab:leaderboard}.
- **P:** «Override», «override mode», «limiting case» — авторские абстракции; тройка «large, repeatable and total» ради ритма; читатель не понимает, что именно перекрывается.
- **R:** The prescription replaces a decision that the supplied script had already made. On MLAgentBench that replacement removes the whole result on 3 of 8 tasks in every attempt and improves 1 of 8 by a defensible margin. FEDOT.LLM replaces that decision on every task by construction, which agrees with its last place in Table~\ref{tab:leaderboard}.

### 06_results_mlab.tex:86 · medium · абстрактное подлежащее

- **Q:** The starting point is what separates this outcome from TabReD. There the branch carrying the prescription wins all eight tasks at three attempts per cell (Table~\ref{tab:grid}, column \emph{both}); here the branch without it wins \mlabOffWins{} of the \mlabRepeated{} tasks we could repeat, and \mlabWiped{} of those wins are total.
- **P:** Подлежащее «the starting point»; «branch carrying the prescription», «wins are total» — внутренний язык; «there/here» заставляет держать в голове, какой бенчмарк где.
- **R:** The two benchmarks differ in what the agent starts from. On TabReD, where no script is supplied, AutoDS-Tools with the prescription beats AutoDS-Tools without it on all eight tasks at three attempts per cell (Table~\ref{tab:grid}, column both). On MLAgentBench, where a working script is supplied, the version without the prescription wins 5 of the 8 repeated tasks, and on 3 of those the version with it submits nothing.

### 06_results_mlab.tex:95 · high · число без единицы

- **Q:** On MLAgentBench the prescription can take a task from a usable score to no submission at all; on TabReD every cell returns a metric on every task and the normalised effect of the layer runs from $\gridBothEffMin$ on \texttt{\gridBothEffMinTask} to $\gridBothEffMax$ on \texttt{\gridBothEffMaxTask}, with a median of $\gridBothEffMedian$.
- **P:** +0.004, +0.357 и 0.06 даны в нормированной шкале лидерборда, которая в этом разделе не определена, а раздел 4 обещал, что нормированный язык на MLAgentBench не переносится; 51 слово.
- **R:** On MLAgentBench the prescription can turn a usable score into no submission. On TabReD every cell returns a score on every task. There the gain from the prescription, on the scale where 0 is the weakest and 1 the strongest published method per task, runs from +0.004 on sberbank-housing to +0.357 on ecom-offers, median 0.06.

### 06_results_mlab.tex:100 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** Where nothing is supplied, structure does not pay richly; it stops costing.
- **P:** Афористичная концовка с отрицанием и метафорой платы; читатель должен догадаться, что «structure» здесь предписание, а «stops costing» означает отсутствие потерь.
- **R:** Where the agent starts from the data alone, the prescription improves all eight tasks, and the median gain is 0.06 on that scale.

### 06_results_mlab.tex:103 · medium · перегруженное предложение

- **Q:** The two halves of this comparison are not a crossed design. The benchmarks differ in tasks, metrics and time budgets as well as in starting point, so what we observe is one factor across two protocols, and the aggregate win count across them should not be read as one number.
- **P:** Утверждение через отрицание, затем 40 слов с тремя придаточными; «one factor across two protocols» — сжатая формула, которую надо разворачивать.
- **R:** The comparison across the two benchmarks is confounded. They differ in tasks, metrics and time budgets as well as in what the agent starts from, so the win counts come from two different protocols and we keep them separate.

### 06_results_mlab.tex:109 · low · абстрактное подлежащее

- **Q:** What the evidence supports without the crossing is the asymmetry itself, visible inside each protocol separately: prescription never destroys a task where nothing was supplied, and destroys \mlabWiped{} of \mlabRepeated{} where a working script was.
- **P:** Подлежащее «what the evidence supports», абстракция «the asymmetry itself»; «destroys a task» разговорно.
- **R:** Each benchmark on its own supports the weaker claim: on TabReD the prescription removes the result on 0 of 8 tasks, and on MLAgentBench it removes the result on 3 of 8.

### 06_results_mlab.tex:114 · medium · внутренний термин без пояснения

- **Q:** \paragraph{Observation 6} The layer that helps on every TabReD task erases the result on \mlabWiped{} of \mlabRepeated{} MLAgentBench tasks and helps defensibly on one; what differs between the two benchmarks is whether a working default was already in place.
- **P:** В заголовочном наблюдении «the layer» и «a working default» требуют помнить, что слой = предписание, а default = обучающий скрипт из задачи.
- **R:** The prescription that improves AutoDS-Tools on all 8 TabReD tasks removes its result on 3 of 8 MLAgentBench tasks and improves 1. The benchmarks differ in whether a working training script is supplied at the start.

### 06_results_mlab.tex:122 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** Whether either half of the layer is worth anything in general is a different question, and the two agentic systems are far enough apart to ask it. The layer is composed on the host and reaches only its own agent, so the only way to hand the same text to Terminus-2 is to append it to the task file.
- **P:** «Far enough apart to ask it» — неясно, в чём далеки; «composed on the host and reaches only its own agent» — деталь реализации без пояснения.
- **R:** Whether either block of the prescription helps in a second architecture is a separate question, and Terminus-2 differs enough from AutoDS-Tools to test it. AutoDS-Tools builds the prescription text at run time and passes it only to its own agents, so for Terminus-2 we appended the same text to the task file.

### 06_results_mlab.tex:137 · low · внутренний термин без пояснения

- **Q:** \caption{The cells of Table~\ref{tab:kdiscterm}: the layer appended to the task for Terminus-2, twenty-four trials per cell.}
- **P:** «Cells» и «the layer» в подписи: читатель рисунка не знает, какие пять условий изображены.
- **R:** The five cells of Table~\ref{tab:kdiscterm}: Terminus-2 with nothing appended to its task file, with the discipline block, with the trimmed discipline block, with the library block, or with both blocks; twenty-four trials per cell, twenty-two for the library block.

### 06_results_mlab.tex:141 · medium · перегруженное предложение

- **Q:** Accuracy is not where the answer lies. In the discipline cell every value lands inside the untreated arm's own spread, two reproduce an untreated value to every digit, and the mean over the \ktDiscTasks{} tasks that return a number is $\ktDiscRel\%$, an order of magnitude inside this system's $\noiseTerminusMax\%$ noise floor.
- **P:** Первая фраза — афоризм через отрицание; вторая 44 слова из трёх частей; «discipline cell», «untreated arm» — внутренние ярлыки.
- **R:** The scores change little. With the discipline block appended, every task score lies within the spread of the untreated Terminus-2 trials, and two scores match an untreated value to every digit. The mean change over the 7 tasks that returned a score is -0.05%, an order of magnitude inside this system's 0.94% noise floor.

### 06_results_mlab.tex:151 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** The layer introduces no new failure mode; it makes the existing one common.
- **P:** Зеркальная концовка с отрицанием; факт (тот же способ отказа, что у двух потерь без предписания, только чаще) можно сказать прямо с числом.
- **R:** The untreated harness already fails this way in 2 of 24 trials; the prescription makes the same failure common.

### 06_results_mlab.tex:153 · medium · метафора

- **Q:** The failure is one of patience.
- **P:** Олицетворение («терпение» агента); что именно произошло, читатель узнаёт только к концу абзаца.
- **R:** The agent stops waiting for a running fit.

### 06_results_mlab.tex:173 · low · число без единицы

- **Q:** The median trial returns to \ktTrimSteps{} steps and three minutes, the bill to less than a sixth, and the whole sweep from one hour forty-six minutes to twenty-six.
- **P:** «Less than a sixth» без базы; числа в долларах есть в таблице (0.0303 и 0.0044), их и надо назвать.
- **R:** The median trial returns to 7 steps and three minutes, the cost per trial falls from 0.0303 to 0.0044 dollars, and the whole sweep of twenty-four trials from one hour forty-six minutes to twenty-six.

### 06_results_mlab.tex:177 · high · метафора

- **Q:** On the library side the same assumption arrives as a fact of the environment, because the prescribed library is slow, and it produces the sharpest cell in the design and its strangest pairing.
- **P:** «Arrives as a fact of the environment», «sharpest cell», «strangest pairing» — три метафоры подряд; что измерено, становится ясно только из следующих двух предложений.
- **R:** With the library block appended, the fit is long because the prescribed library is slow. This cell loses the most trials of the five, and adding the discipline block to it reduces the losses.

### 06_results_mlab.tex:182 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** The instruction that harms by itself protects in combination, and the mechanism is legible: what the discipline half tells this harness is that a long-running job is normal, which is what the library half requires it to believe.
- **P:** Авторская ремарка «the mechanism is legible», зеркальная пара «harms by itself / protects in combination»; 38 слов без чисел.
- **R:** The discipline block tells the agent that a long-running job is normal, and the library block makes the job long-running, so the pair loses fewer trials than the library block alone.

### 06_results_mlab.tex:187 · medium · абстрактное подлежащее

- **Q:** AutoDS-Tools met none of this. The same four cells inside its own architecture lost none, none, none and one trial of twenty-four (Section~\ref{sec:grid}). Whatever absorbs the instruction there, a fixed workflow, a repair loop, a planner that owns the schedule, is what makes the prescription survivable, and none of it is part of the prescription.
- **P:** «Met none of this» — контраст через отрицание; подлежащее «whatever absorbs the instruction»; «survivable» — авторский термин.
- **R:** AutoDS-Tools lost none, none, none and one trial of twenty-four in the same four cells (Section~\ref{sec:grid}). Something in its architecture absorbs the instruction, its fixed workflow, its repair loop or its planner that owns the schedule; all three belong to the architecture, so whether the prescription is safe depends on the system that runs it.

### 06_results_mlab.tex:191 · high · метафора

- **Q:** Measured inside the system it ships with, the layer is worth $\gridBothMean\%$ and costs nothing; the same bytes handed to a different architecture leave the answers untouched and cost most of them.
- **P:** «Worth», «costs nothing», «cost most of them» — метафора платы без единиц; читатель не знает, что +0.72% — средний относительный прирост на TabReD, а «most of them» — потерянные испытания.
- **R:** Inside AutoDS-Tools the prescription improves every one of the eight TabReD tasks, by 0.72% on average. Appended to Terminus-2, the same text leaves the scores within the noise floor and loses 13 of 24 trials with the discipline block and 19 of 22 with the library block.

### 06_results_mlab.tex:194 · high · метафора

- **Q:** A layer that has been measured in one architecture has not been measured in another. The practical consequence is smaller than that framing suggests: on the discipline side the text was two paragraphs away from being portable, and finding which two took one cell of twenty-four trials costing eleven cents. What fails to port is the assumption that travels with the knowledge.
- **P:** Афоризм-тавтология в начале, метафоры «port/portable» и «travels with the knowledge» в конце; итог абзаца читатель восстанавливает сам.
- **R:** The effect of the prescription has to be measured in each architecture separately. In practice the fix was small: deleting two of the seven sections of the discipline block made it safe for Terminus-2, and finding those two took one cell of twenty-four trials costing eleven cents. The harm came from the assumption about training time in those two sections; the other five could stay.

### 06_results_mlab.tex:203 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** Those figures average over the minority of trials that survived, and survival in those cells is persistence, so we report the direction and no more.
- **P:** «Survival is persistence» — сжатая формула: выжили те испытания, где агент дольше ждал, и это смещение выборки.
- **R:** Those means cover only the few trials that finished, and those are the trials whose agent waited longest, so we report the direction and no more.

### 06_results_mlab.tex:205 · medium · перегруженное предложение

- **Q:** Separately, several cells reproduce another system's value to sixteen digits, and that is not two architectures converging under a shared prescription: \texttt{sberbank-housing} returns the same RMSE in all three untreated AutoDS-Tools attempts and two of three untreated Terminus-2 attempts, with no prescription anywhere.
- **P:** 52 слова, утверждение через отрицание («that is not two architectures converging»), причина названа только в следующем предложении.
- **R:** Several cells reproduce a value from the other system to sixteen digits. The cause is library determinism: \texttt{sberbank-housing} returns the same RMSE in all three AutoDS-Tools attempts and in two of three Terminus-2 attempts without the prescription.

### 06_results_mlab.tex:217 · medium · внутренний термин без пояснения

- **Q:** \paragraph{Observation 7} Handed to Terminus-2, the layer leaves accuracy inside the noise floor and costs \ktDiscLost{} of twenty-four trials with the discipline half and \ktToolLost{} of \ktToolTrials{} with the library half; deleting the two paragraphs about training time restores every trial.
- **P:** В заголовочном наблюдении «the layer», «discipline half», «library half»; «restores every trial» неточно, число (0 потерь из 24) не названо.
- **R:** Appended to Terminus-2's task file, the prescription leaves scores within the noise floor and loses 13 of 24 trials with the discipline block and 19 of 22 with the library block. Deleting the two sections of the discipline block that concern training time brings the losses to 0 of 24.


## mlabhead.tex

### mlabhead.tex:3 · medium · внутренний термин без пояснения

- **Q:** \caption{AutoDS-Tools without its layer and Terminus-2 on MLAgentBench under one job, one verifier and three attempts per task. $n$ counts the attempts that submitted; mean, min and max are over those. Bold marks the better system where the margin exceeds $5\%$.}
- **P:** «Without its layer», «one job, one verifier» — внутренние термины в подписи, которую читают отдельно от текста.
- **R:** AutoDS-Tools with its prescription switched off and Terminus-2 on the eight MLAgentBench tasks, run in one batch with one scorer and three attempts per task. $n$ counts the attempts that produced a submission; mean, min and max are over those. Bold marks the better system where the margin exceeds $5\%$.

### mlabhead.tex:24 · low · внутренний термин без пояснения

- **Q:** Terminus-2 reached its agent budget once in $24$ trials, AutoDS-Tools $13$ times in $30$.
- **P:** «Agent budget» не пояснён (лимит времени задачи); 30 испытаний при 24 в таблице требуют оговорки про две неповторённые задачи.
- **R:** Terminus-2 ran out of the task's time budget in 1 of 24 trials, AutoDS-Tools in 13 of 30 trials over all ten tasks.


## ktool.tex

### ktool.tex:3 · high · число без единицы

- **Q:** $\Delta$ is the normalised effect, positive where the layer helps.
- **P:** Формула Δ нигде в статье не дана; читатель не может понять, что значат +0.96 или -0.28 (в make_tables.py это разность средних, делённая на больший из двух модулей, со знаком в пользу предписания).
- **R:** Δ is the change in mean score with the prescription, divided by the larger of the two means, with the sign chosen so that positive means the prescription helped.


## 06b_cases.tex

### 06b_cases.tex:7 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** Benchmarks measure what they were built to measure.
- **P:** Афористичный зачин без содержания; следующее предложение говорит всё нужное.
- **R:** To test the same design on tasks posed by researchers who needed the answer, we took three published studies with an author-reported baseline and made each a Harbor task.

### 06b_cases.tex:38 · low · перегруженное предложение

- **Q:** Each task text was written for the July AutoDS-Tools runs and sits at the far end of the prescription axis of Section~\ref{sec:axis}: it names LightAutoML as the required library, supplies a working snippet, lists the columns that leak the target, describes the split and states the author baseline as the number to beat.
- **P:** 47 слов; «the far end of the prescription axis» — внутренняя координата, хотя дальше она расшифрована.
- **R:** Each task text was written for the July AutoDS-Tools runs and carries the fullest prescription in the paper (Section~\ref{sec:axis}). It names LightAutoML as the required library, supplies a working snippet, lists the columns that leak the target, describes the split and states the author baseline as the number to beat.

### 06b_cases.tex:46 · medium · перегруженное предложение

- **Q:** FEDOT.LLM enters on the two tabular cases with the text without the library section, three attempts each and a $40$-minute budget for its backend: its tool choice is welded in, so the library section is no condition for it, and a check run with that section in place inferred the same columns and returned the same F-DATA scores.
- **P:** 55 слов, метафора «welded in», отрицание «is no condition for it»; три факта в одном предложении.
- **R:** FEDOT.LLM ran on the two tabular cases with the library section removed, three attempts each and a 40-minute budget for its backend. Its library is fixed by design, so the library section changes nothing for it; a check run with the section present inferred the same columns and returned the same F-DATA scores.

### 06b_cases.tex:59 · medium · внутренний термин без пояснения

- **Q:** Unaided, Terminus-2 matched or exceeded the author baselines on both tasks with a comparable split.
- **P:** Одно условие названо тремя словами: «plain» в таблице, «without the library section» и «unaided» в тексте; читатель не сразу понимает, что «unaided» = plain, и какие «both tasks» имеются в виду.
- **R:** On the plain text Terminus-2 matched or exceeded the author baselines on both tasks with a comparable split, maize and F-DATA.

### 06b_cases.tex:60 · medium · перегруженное предложение

- **Q:** On maize its two scoring attempts reached Pearson $r$ of $\caseTermPlainMaizeMin$ and $\caseTermPlainMaizeMax$ against the authors' best model at $\caseAuthorMaize$, and normalised RMSE of $\caseTermPlainMaizeNormRmse$ on average against the authors' $0.948$; the July AutoDS-Tools run had beaten the authors on $r$ ($\caseAutoDSMaizeMean$) while losing on error ($\caseAutoDSMaizeNormRmse$), and Terminus-2 wins on both.
- **P:** 58 слов, шесть чисел и три системы в одном предложении; «normalised RMSE» здесь авторская метрика, а не шкала статьи, и это стоит оговорить.
- **R:** On maize its two scoring attempts reached Pearson r of 0.636 and 0.674, against 0.461 for the authors' best model. Its normalised RMSE, the authors' own metric, averaged 0.792 against the authors' 0.948. The July AutoDS-Tools run had beaten the authors on r (0.569) and lost on normalised RMSE (0.958); Terminus-2 beats them on both.

### 06b_cases.tex:71 · medium · перегруженное предложение

- **Q:** The traces show what it reached for. On F-DATA a random forest or XGBoost with class weights and a validation split; on maize gradient boosting over label-encoded pedigree and site columns; on OpenPoly it installed RDKit, computed Morgan fingerprints and descriptors from the PSMILES string and fit XGBoost on them, which is the published recipe, arrived at without being told.
- **P:** Метафора «reached for», затем 50 слов, где первые две части без сказуемого; концовка «arrived at without being told» — ударник.
- **R:** The traces show which methods it chose. On F-DATA it fit a random forest or XGBoost with class weights and a validation split. On maize it fit gradient boosting over label-encoded pedigree and site columns. On OpenPoly it installed RDKit, computed Morgan fingerprints and descriptors from the PSMILES string and fit XGBoost on them, which is the published recipe, found by the agent on its own.

### 06b_cases.tex:85 · medium · перегруженное предложение

- **Q:** The prescribed call, LightAutoML at its defaults, takes $\caseLamaFitFdataMin$ minutes on the F-DATA table and $\caseLamaFitMaizeMin$ on the maize table in the same image, and the prescribed RDKit snippet floods the pane with a deprecation warning per molecule, so under the prescription every attempt outlived the agent's patience; unaided, the agent chose estimators that return in seconds.
- **P:** 60 слов, две причины и следствие в одной фразе; «outlived the agent's patience» — олицетворение; «unaided» снова вместо «plain».
- **R:** The prescribed call, LightAutoML at its defaults, takes 9.7 minutes on the F-DATA table and 10.9 on the maize table in the same image, and the prescribed RDKit snippet prints a deprecation warning per molecule. Under the prescription every attempt therefore ran longer than the agent was willing to wait. On the plain text the agent chose estimators that return in seconds.

### 06b_cases.tex:91 · high · метафора

- **Q:** The same prescription therefore helps one architecture and sinks the other on a task family where the prescribed library is a sound choice, which is the non-portability of Section~\ref{sec:kdiscterm} observed where the prescription is correct.
- **P:** «Sinks», «non-portability» — метафора и авторская абстракция; архитектуры не названы, и читатель должен вспоминать содержание раздела 6.3.
- **R:** The same text therefore helps AutoDS-Tools and loses every Terminus-2 attempt on tasks where LightAutoML is a sound choice. This repeats the result of Section~\ref{sec:kdiscterm}: the effect of a prescription depends on the architecture that receives it, here even when the prescribed library is right.

### 06b_cases.tex:96 · low · внутренний термин без пояснения

- **Q:** The rigid pipeline is the best system on one of the two tables it can read.
- **P:** «Rigid pipeline» вместо имени системы; «tables it can read» — обиняк вместо «табличные задачи».
- **R:** FEDOT.LLM is the best system on F-DATA, one of the two tabular cases it can run.

### 06b_cases.tex:97 · medium · перегруженное предложение

- **Q:** On F-DATA, FEDOT.LLM reached $\caseFedotPlainFdataMean$ accuracy in all three attempts, to the last digit, with balanced accuracy $\caseFedotPlainFdataBalancedAccuracy$ against $\caseTermPlainFdataBalancedAccuracy$ for the harness and $\caseAutoDSFdataBalancedAccuracy$ for the July run: the budget it spends on tuning a fixed backend buys three points of accuracy and fourteen of balanced accuracy over two agents that fit one model and stop.
- **P:** 62 слова; «the harness» и «the July run» вместо Terminus-2 и AutoDS-Tools; «buys ... points» — метафора платы.
- **R:** On F-DATA FEDOT.LLM reached 0.952 accuracy in all three attempts, identical to the last digit, with balanced accuracy 0.853 against 0.716 for Terminus-2 and 0.705 for AutoDS-Tools. The time it spends tuning a fixed backend gains three points of accuracy and fourteen of balanced accuracy over the two agents, which each fit one model and stop.

### 06b_cases.tex:107 · medium · метафора

- **Q:** Its attempts took $\caseFedotPlainMaizeMinutes$ minutes of the hour on the larger table, because the backend treats its budget as advice, which is a different failure from the harness's impatience and the same clock.
- **P:** «Treats its budget as advice», «the harness's impatience», «the same clock» — три метафоры; читатель не понимает, что общего между двумя отказами.
- **R:** On the maize table its attempts took 52.8 minutes of the hour, because the FEDOT backend ran past the 40-minute budget it was given. Both failures concern the clock: Terminus-2 stops waiting too soon, and FEDOT.LLM keeps going past its budget.

### 06b_cases.tex:112 · high · перегруженное предложение

- **Q:** \paragraph{Observation 8} On three published tasks an open 31B model in the open harness, given nothing beyond the task, matched or beat the author baselines where the split is comparable and rediscovered the published featurisation; the library prescription that AutoDS-Tools ran on cost Terminus-2 all nine attempts; and the rigid pipeline, which cannot read the prescription at all, beat both agents on the one table where tuning a fixed backend is the whole task.
- **P:** 71 слово с тремя точками с запятой; «open harness», «rigid pipeline» вместо имён систем; «the one table where tuning a fixed backend is the whole task» — обиняк вместо F-DATA.
- **R:** On three published tasks Terminus-2 with the open 31B model and the plain task text matched or beat the author baselines where the split is comparable, and on OpenPoly it rediscovered the published featurisation. The library prescription that AutoDS-Tools ran on in July cost Terminus-2 all nine attempts. FEDOT.LLM, which cannot use the prescription, beat both agents on F-DATA, where tuning a fixed backend is the whole task.


## cases.tex

### cases.tex:15 · low · метафора

- **Q:** plain (tool welded in)
- **P:** «Welded in» — метафора в ячейке таблицы (строки 15 и 21); примечание к таблице уже говорит, что FEDOT.LLM не может использовать библиотечный раздел.
- **R:** plain (library fixed by design)


## 07_mechanism.tex

### 07_mechanism.tex:26 · medium · число без единицы

- **Q:** On tabular data the prescription therefore restates the default, and that is why it is worth $\gridToolMean\%$ inside AutoDS-Tools and nothing measurable inside Terminus-2.
- **P:** «that is why» из запрещённого списка; «+0.69%» без указания, процент чего (среднее относительное изменение метрики задачи по восьми задачам).
- **R:** On tabular data the prescription therefore restates the default. Inside AutoDS-Tools it improves the task metric by 0.69% on average over the eight TabReD tasks, and inside Terminus-2 it changes nothing measurable.

### 07_mechanism.tex:30 · low · внутренний термин без пояснения

- **Q:** The same traces locate the ceiling.
- **P:** «the ceiling» — внутренняя метка из раздела 5; читатель должен вспомнить, что это разрыв до настроенного XGBoost.
- **R:** The same traces show why the best system stops short of tuned XGBoost.

### 07_mechanism.tex:35 · high · прочее (отрицание, афоризм, ремарка)

- **Q:** The gap to the published gradient-boosting rows is not a gap in tool selection, which the harness gets right unaided, but a gap in search: the baselines are Optuna-tuned over fifteen seeds, the agent writes one plausible configuration and stops.
- **P:** Контраст «not X but Y», 38 слов с двумя вложенными оборотами; это главный вывод подраздела, и он читается дважды.
- **R:** The gap to the published gradient-boosting rows is a gap in search. The harness picks the right tool unaided. The baselines are Optuna-tuned over fifteen seeds; the agent writes one plausible configuration and stops.

### 07_mechanism.tex:38 · medium · перегруженное предложение

- **Q:** Telling a weak model which tool to use is worth a great deal where it would otherwise choose badly and nothing on tabular data; what remains unaddressed there, search over the chosen tool, is what no system in our comparison performs.
- **P:** 44 слова; оборот «what remains ..., is what ...» с двойным «what»; «worth a great deal» разговорное.
- **R:** Telling a weak model which tool to use helps where it would otherwise choose badly and does nothing on tabular data. What remains open there is search over the chosen tool, and no system in our comparison performs it.

### 07_mechanism.tex:47 · medium · число без единицы

- **Q:** Table~\ref{tab:grid} says the discipline half is worth $\gridDiscMean\%$ on the score.
- **P:** «+0.12% on the score» — не сказано, процент чего; «the discipline half» требует помнить, что это половина слоя предписаний.
- **R:** Table~\ref{tab:grid} puts the discipline half of the layer at +0.12% on the task metric, averaged over the eight TabReD tasks.

### 07_mechanism.tex:48 · medium · номинализация

- **Q:** Read for behaviour, the same four cells show the treatment reaching the agent.
- **P:** «Read for behaviour» и «the treatment» — абстракции; читатель гадает, кто что читает и что такое treatment.
- **R:** The traces of the same four cells show that the discipline half reaches the agent.

### 07_mechanism.tex:51 · medium · придуманная абстракция

- **Q:** They leave a signature in no trial of either cell where the discipline half is off and in every trial of both cells where it is on.
- **P:** «leave a signature» — придуманный термин; порядок «ни в одном ... и в каждом» заставляет перечитывать.
- **R:** All three behaviours appear in every trial of the two cells with the discipline half on, and in no trial of the two cells with it off.

### 07_mechanism.tex:56 · medium · придуманная абстракция

- **Q:** Two further clauses separate nothing, and both show why single-arm readings mislead.
- **P:** «separate nothing» и «single-arm readings» — сжатые обороты без расшифровки; смысл ясен только из следующих предложений.
- **R:** Two further clauses fail as a manipulation check, and both show why reading one arm alone misleads.

### 07_mechanism.tex:57 · medium · перегруженное предложение

- **Q:** AutoDS-Tools inspects its submission in twenty-two of twenty-four trials with no prescription at all; contrasting that with Terminus-2, which leaves no trace of the clause in any of its twenty-four trials, would credit the text with a habit that belongs to the architecture.
- **P:** 45 слов, три вложенных оборота; подлежащее главного предложения («contrasting that») появляется в середине.
- **R:** AutoDS-Tools inspects its submission in twenty-two of twenty-four untreated trials; Terminus-2 leaves no trace of the clause in any of its twenty-four. A comparison across the two systems would credit the instruction with a habit that belongs to the architecture.

### 07_mechanism.tex:62 · low · придуманная абстракция

- **Q:** A signature shows that an instruction reached the trace and leaves open whether it was carried out.
- **P:** Снова «signature» как термин; читатель должен помнить, что это след клаузы в трассе.
- **R:** A trace of a clause shows that the instruction reached the agent and leaves open whether the agent carried it out.

### 07_mechanism.tex:67 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** As an instruction it is active; as an intervention it is inert, on a family where the agent's untutored defaults were already adequate.
- **P:** Зеркальная пара «active / inert» вместо прямого утверждения; «untutored defaults» разговорно.
- **R:** The agent follows the block; on tabular data its own defaults were already adequate, so the score hardly moves.

### 07_mechanism.tex:69 · medium · абстрактное подлежащее

- **Q:** One connection survives with its attribution corrected.
- **P:** Подлежащее «connection» и абстрактное «attribution»; читатель не понимает, связь чего с чем и кому что приписано.
- **R:** One clause links to an observed failure, once the failure is attributed to the system that lacked the clause.

### 07_mechanism.tex:78 · medium · придуманная абстракция

- **Q:** \subsection{Prescription raises execution friction}
- **P:** «execution friction» — придуманная абстракция; в тексте она означает частоту срабатывания цикла починки.
- **R:** \subsection{Prescription makes execution fail more often}

### 07_mechanism.tex:88 · medium · метафора

- **Q:** The imbalance concentrates where the prescription pushes hardest: four invocations against none on \texttt{clrs} and three against none on \texttt{amp-parkinsons}, both tasks on which the agent is steered to a specialised library whose interface it then fails on.
- **P:** «pushes hardest» — метафора; 43 слова с двумя вложенными оборотами.
- **R:** The imbalance concentrates on the tasks where the prescription names a specialised library: four invocations against none on \texttt{clrs} and three against none on \texttt{amp-parkinsons}. On both, the agent is steered to a library whose interface it then fails on.

### 07_mechanism.tex:95 · high · метафора

- **Q:** Read as a mediator, this quantifies the cost side. Prescription raises execution friction, and its net effect is positive only where the prescribed tool is enough better to repay it.
- **P:** «Read as a mediator» — статистический термин без пояснения; «cost side», «friction», «repay» — три метафоры в двух предложениях.
- **R:** The repair count shows the cost side of prescription. Prescription makes execution fail more often, and its net effect is positive only where the prescribed tool gains enough to cover those failures.

### 07_mechanism.tex:97 · medium · перегруженное предложение

- **Q:** The effect we measure is therefore that of prescription as delivered by a system able to recover from the errors prescription causes; in a harness without a repair loop the losses would plausibly be larger, which is what Section~\ref{sec:kdiscterm} found.
- **P:** 45 слов; «which is what» из запрещённого списка; «as delivered» без пояснения.
- **R:** We therefore measure prescription inside a system that can recover from the errors prescription causes. In a harness without a repair loop the losses would be larger, as Section~\ref{sec:kdiscterm} found for Terminus-2.

### 07_mechanism.tex:117 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** The instruction is not wrong as advice; it is written without reference to the budget the task grants, and on this task the two are incompatible.
- **P:** «not wrong ... it is» — контраст через отрицание.
- **R:** As advice the instruction is sound. It is written without reference to the time budget the task grants, and on \texttt{clrs} the two are incompatible.

### 07_mechanism.tex:126 · medium · перегруженное предложение

- **Q:** The layer is composed on the host by the agent package installed when the runner was set up, and the copy inside the container plays no part, so reinstalling from a newer checkout changes the treatment without changing anything visible in the run configuration.
- **P:** 46 слов, три сочинённые части; «the treatment» абстрактно.
- **R:** The agent package installed on the host when the runner was set up composes the layer; the copy inside the container plays no part. Reinstalling the package from a newer checkout therefore changes the instruction text, and nothing visible in the run configuration changes with it.

### 07_mechanism.tex:137 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** The difference is not cosmetic.
- **P:** Утверждение через отрицание; надо сказать, что различие меняет.
- **R:** The difference changes what the agent is told to do.

### 07_mechanism.tex:150 · medium · внутренний термин без пояснения

- **Q:** Where the budget was never binding the shipped edition is the better of the two, SMAPE $\mlabAmpOn$ against $93.15$ and accuracy $\mlabOgbnOn$ against $0.4683$, and the remaining pair is level.
- **P:** «budget was never binding» и «the remaining pair» без названия задач; читатель не знает, к каким задачам относятся SMAPE и accuracy.
- **R:** On the tasks where neither edition ran out of time the shipped edition scores better: SMAPE $\mlabAmpOn$ against $93.15$ on \texttt{amp-parkinsons} and accuracy $\mlabOgbnOn$ against $0.4683$ on \texttt{ogbn-arxiv}. The remaining two tasks are level.

### 07_mechanism.tex:152 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** Counting submissions rather than scores, the shipped edition yields $15$ of $24$ and the cloned edition $21$ of $24$.
- **P:** «rather than» из запрещённого списка.
- **R:** Counted by submissions, the shipped edition yields 15 of 24 and the cloned edition 21 of 24.

### 07_mechanism.tex:154 · medium · метафора

- **Q:** The edit is a move along the axis this paper is about: one edition presses harder on training discipline and pays in unfinished runs, the other presses less and finishes.
- **P:** «the axis this paper is about», «presses harder», «pays in» — три метафоры; какая редакция какая, не названо.
- **R:** The two editions differ in how much they constrain the agent, which is the variable this paper studies. The shipped edition demands more training discipline and leaves runs unfinished; the cloned edition demands less and finishes.

### 07_mechanism.tex:158 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** A result of this kind cannot be repeated from a description of the layer, only from its bytes, and the bytes are what is least often reported.
- **P:** Концовка-«ударник» с зеркальной парой «description / bytes».
- **R:** A result of this kind can be repeated only from the exact text of the layer, and papers seldom publish that text.


## 08_discussion.tex

### 08_discussion.tex:10 · high · число без единицы

- **Q:** \textbf{RQ1.} With one open 31B backbone, the three architectures span $\nFedot$ to $\nAutoDS$ of the range set by eighteen expert-tuned methods.
- **P:** Числа 0.26 и 0.85 без указания, что такое 0 и 1; системы не названы. Это авторский пример 1 из highlights, повторённый в ответе на RQ1.
- **R:** \textbf{RQ1.} With one open 31B backbone, changing the architecture moves the TabReD result from 0.26 (FEDOT.LLM) to 0.85 (AutoDS-Tools) on the scale where 0 is the weakest and 1 the strongest of eighteen published methods. The lower end is level with plain linear regression.

### 08_discussion.tex:12 · medium · число без единицы

- **Q:** The best of them is level with tuned LightGBM and $\gapXGB$ short of tuned XGBoost; none approaches the strongest published method at $\nBest$.
- **P:** «0.02 short» и «at 0.95» без единицы; «the best of them» вместо имени системы; сильнейший метод не назван.
- **R:** AutoDS-Tools is level with tuned LightGBM and 0.02 short of tuned XGBoost on that scale; the strongest published method, an MLP-PLR ensemble, sits at 0.95, and no system approaches it.

### 08_discussion.tex:17 · high · число без единицы

- **Q:** \textbf{RQ2.} Of the $\gapAgentsShip$ that separates the two agentic systems as shipped, $\layerWorthNorm$ belongs to the prescribed-knowledge layer and $\gapAgentsOff$ to the architecture (Section~\ref{sec:grid}).
- **P:** Три числа 0.13, 0.10, 0.03 без единицы; «as shipped» как термин без пояснения; системы не названы.
- **R:** \textbf{RQ2.} As deployed, AutoDS-Tools scores 0.13 above Terminus-2 on that scale. Removing its prescribed-knowledge layer, the library and training instructions it carries, takes away 0.10 of that lead, and 0.03 remains for the architecture (Section~\ref{sec:grid}).

### 08_discussion.tex:19 · medium · перегруженное предложение

- **Q:** The container image contributes nothing measurable (Section~\ref{sec:matched}), and the backbone moves accuracy by a fraction of a percent while moving reliability and cost in opposite directions for the two systems (Section~\ref{sec:modelaxis}).
- **P:** «moving reliability and cost in opposite directions for the two systems» читается дважды: непонятно, что противоположно чему.
- **R:** The container image contributes nothing measurable (Section~\ref{sec:matched}). Swapping the backbone moves accuracy by a fraction of a percent while the bill varies 13-fold; a stronger backbone loses fewer trials under Terminus-2 and more under AutoDS-Tools (Section~\ref{sec:modelaxis}).

### 08_discussion.tex:23 · high · число без единицы

- **Q:** Architecture remains the larger term, $\spanArch$ against at most $0.24$ for the backbone.
- **P:** «0.49 против 0.24» без единицы и без пояснения, что это размах по нормированной шкале; «term» отсылает к статистической модели, которой в тексте нет.
- **R:** Architecture remains the larger factor: with prescription removed, the three architectures span $\spanArch$ of the normalised scale, and swapping the backbone spans at most $0.24$ under either agentic system.

### 08_discussion.tex:26 · medium · метафора

- **Q:** \textbf{RQ3.} The layer that helps on every TabReD task erases the result on \mlabWiped{} of \mlabRepeated{} MLAgentBench tasks, where a working script was already in place (Section~\ref{sec:signflip}).
- **P:** «erases the result» — метафора; конкретно это «ни одной поданной работы за три попытки».
- **R:** \textbf{RQ3.} The layer that improves every one of the eight TabReD tasks leaves AutoDS-Tools with no submission in any attempt on \mlabWiped{} of \mlabRepeated{} MLAgentBench tasks, where a working script was already in place (Section~\ref{sec:signflip}).

### 08_discussion.tex:28 · high · прочее (отрицание, афоризм, ремарка)

- **Q:** Handed to Terminus-2, it leaves accuracy untouched and costs most of the trials, for a reason two paragraphs long (Section~\ref{sec:kdiscterm}).
- **P:** «for a reason two paragraphs long» — авторская ремарка вместо причины; «costs most of the trials» не говорит, сколько попыток и как именно они теряются.
- **R:** Appended to the Terminus-2 task text, the layer leaves accuracy unchanged, and trials end without a submission in 13 of 24 with the discipline half and in 19 of 22 with the library half. The agent launches a fit in the foreground, sees a terminal that has stopped producing output, and declares the task finished while the fit is still running (Section~\ref{sec:kdiscterm}).

### 08_discussion.tex:35 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** \subsection{What the non-monotonic ordering does and does not show}
- **P:** Заголовок построен на контрасте «does and does not»; «non-monotonic ordering» — внутренняя формула.
- **R:** \subsection{What the ordering of the three systems shows}

### 08_discussion.tex:37 · high · придуманная абстракция

- **Q:** Read as deployed, the three systems trace a hump over architectural weight, the middle design scoring highest.
- **P:** «hump over architectural weight» — придуманная ось плюс метафора; «as deployed» без пояснения. Это авторский пример 2.
- **R:** Compared as deployed, the rigid pipeline FEDOT.LLM ranks last, the six-agent AutoDS-Tools first, and the open harness Terminus-2 between them.

### 08_discussion.tex:39 · medium · метафора

- **Q:** Three points cannot fix the shape of a curve, and most of the hump is not architecture.
- **P:** «most of the hump is not architecture» — метафора плюс отрицание; надо сказать, чему принадлежит преимущество.
- **R:** Three points cannot fix the shape of a curve, and most of AutoDS-Tools' lead belongs to its prescribed-knowledge layer.

### 08_discussion.tex:40 · high · число без единицы

- **Q:** With the layer removed the ordering becomes $\nFedot$, $\nAutoDSOff$ and $\nTerminus$, and the two agentic systems sit $\gapAgentsOff$ apart, inside the range where their noise floors and deployment effects still matter.
- **P:** Три числа без имён систем, причём не по возрастанию (0.26, 0.75, 0.72), так что слово «ordering» сбивает; «noise floors and deployment effects» — жаргон.
- **R:** With the layer removed the scores are FEDOT.LLM 0.26, AutoDS-Tools 0.75 and Terminus-2 0.72 on the normalised scale. The two agentic systems are 0.03 apart, a distance of the same order as their run-to-run noise and deployment effects.

### 08_discussion.tex:44 · high · перегруженное предложение

- **Q:** Performance does not increase with structure, since the most constrained system is last by a margin that survives the rounding of its metrics, and it does not decrease with structure either, since the least constrained system is not first.
- **P:** 42 слова, двойное отрицание, системы не названы; заглавный тезис второй половины статьи читается дважды.
- **R:** FEDOT.LLM, the most constrained system, is last by a margin larger than the rounding of its metrics, and Terminus-2, the least constrained, is second.

### 08_discussion.tex:56 · low · внутренний термин без пояснения

- **Q:** The case studies of Section~\ref{sec:cases} bear on the ceiling of Section~\ref{sec:ceiling} and on RQ3.
- **P:** «the ceiling» — внутренняя метка; не раскрыто, что это разрыв до настроенного XGBoost.
- **R:** The case studies of Section~\ref{sec:cases} bear on the gap to the tuned baselines (Section~\ref{sec:ceiling}) and on RQ3.

### 08_discussion.tex:59 · medium · номинализация

- **Q:** That is a result about applied scientific baselines, which are frequently well below what a competent tabular pipeline achieves, and it supports reading the ceiling as a statement about tuned tabular baselines specifically.
- **P:** «reading the ceiling as a statement» — номинализация; 36 слов с двумя вложенными оборотами.
- **R:** That result concerns applied scientific baselines, which are often well below what a competent tabular pipeline achieves. The gap to tuned XGBoost on TabReD is therefore a statement about expert-tuned tabular baselines specifically.

### 08_discussion.tex:62 · medium · внутренний термин без пояснения

- **Q:** The rigid pipeline, which cannot read the prescription, beat both agents on the table where the task reduces to tuning a fixed backend, so the ordering of Section~\ref{sec:ceiling} is not a fixed property of the architectures either.
- **P:** «the table» без названия задачи и без чисел; «not a fixed property» через отрицание.
- **R:** FEDOT.LLM, the rigid pipeline, which cannot read the prescription, beat both agents on F-DATA (accuracy $\caseFedotPlainFdataMean$ against $\caseTermPlainFdataMean$ and $\caseAutoDSFdataMean$), where the task reduces to tuning a fixed backend. The TabReD ordering of Section~\ref{sec:ceiling} therefore depends on the task as well as on the architecture.

### 08_discussion.tex:65 · medium · придуманная абстракция

- **Q:** The cases also close the crossing that Section~\ref{sec:kdiscterm} left open: on a family where the prescribed library is a sound choice, the prescription still cost the open harness every attempt, and for the same reason.
- **P:** «close the crossing» — придуманный оборот; «for the same reason» отсылает к причине, которую надо помнить из раздела 6.
- **R:** The cases also answer a question Section~\ref{sec:kdiscterm} left open. On a family where the prescribed library is a sound choice, the prescription still cost Terminus-2 every one of its \caseTermPrescTotal{} attempts, for the same reason: the agent declared the task finished while the prescribed fit was still running.

### 08_discussion.tex:87 · medium · абстрактное подлежащее

- **Q:** Since the clause is a constraint, the asymmetry runs against the only arm that carried it.
- **P:** Подлежащее «the asymmetry» с оборотом «runs against»; читатель должен сам восстановить, в чью пользу смещение.
- **R:** The clause constrains the agent, so any bias from this asymmetry works against the one arm that carried it.

### 08_discussion.tex:105 · medium · число без единицы

- **Q:** Scoring it as zero would move that task from $0.961$ to $\timeoutZeroHomesite$ and the normalised mean from $\nAutoDS$ to $\timeoutZeroNorm$, below every published baseline, while the average rank moved only from $\rkAutoDS$ to $\timeoutZeroRank$.
- **P:** Три пары чисел в трёх разных единицах (ROC-AUC, нормированная шкала, ранг из 21) в одном предложении, единицы не названы.
- **R:** Scoring the lost trial as zero would move \texttt{homesite-insurance} from ROC-AUC $0.961$ to $\timeoutZeroHomesite$, the normalised mean of AutoDS-Tools from $\nAutoDS$ to $\timeoutZeroNorm$ (below every published baseline), and its average rank only from $\rkAutoDS$ to $\timeoutZeroRank$ of \nMethods{}.

### 08_discussion.tex:110 · low · прочее (отрицание, афоризм, ремарка)

- **Q:** The exclusion is not neutral either, since it drops the slowest attempt of a system whose failures fall on the tasks it finds hardest.
- **P:** Утверждение через отрицание «not neutral»; направление смещения читатель выводит сам.
- **R:** The exclusion favours AutoDS-Tools, since it drops the slowest attempt of a system whose failures fall on the tasks it finds hardest.


## 09_conclusion.tex

### 09_conclusion.tex:9 · high · число без единицы

- **Q:** Under one open 31B model the three systems span $\nFedot$ to $\nAutoDS$ of the range set by eighteen expert-tuned baselines; the strongest is level with tuned LightGBM and $\gapXGB$ short of tuned XGBoost.
- **P:** 0.26, 0.85 и 0.02 без единицы; заключение повторяет непонятный пункт highlights, системы не названы.
- **R:** Under one open 31B model, changing the agent system moves the TabReD result from the level of plain linear regression (FEDOT.LLM) to the level of tuned LightGBM (AutoDS-Tools). On the scale where 0 is the weakest and 1 the strongest of eighteen published methods, that is 0.26 to 0.85, and AutoDS-Tools stays 0.02 short of tuned XGBoost.

### 09_conclusion.tex:11 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** The gap architecture closes is large, and the gap it leaves is search: every system selects gradient boosting unaided and none tunes it.
- **P:** Зеркальная пара «closes / leaves» ради ритма; «the gap it leaves is search» афористично.
- **R:** Architecture closes half the range. What remains between AutoDS-Tools and tuned XGBoost is hyperparameter search: every system selects gradient boosting unaided and none tunes it.

### 09_conclusion.tex:15 · high · абстрактное подлежащее

- **Q:** The relationship is not monotonic in architectural weight.
- **P:** Подлежащее «the relationship» и придуманная ось «architectural weight»; читатель не знает, связь между чем и чем.
- **R:** The rigid pipeline FEDOT.LLM, the most constrained of the three, ranks last; the open harness Terminus-2, the least constrained, ranks second; and the six-agent AutoDS-Tools, between them in structure, ranks first.

### 09_conclusion.tex:15 · high · перегруженное предложение

- **Q:** The most constrained system ranks last and the best of the three is neither extreme, and once the prescribed-knowledge layer is separated from the architecture that carries it, $\layerWorthNorm$ of the $\gapAgentsShip$ between the two agentic systems belongs to the layer and $\gapAgentsOff$ to the architecture.
- **P:** 50 слов, три числа без единицы, «neither extreme» через отрицание; ни одна система не названа.
- **R:** AutoDS-Tools leads Terminus-2 by 0.13 on that scale. Of that, 0.10 comes from its prescribed-knowledge layer, the library and training instructions it carries, and 0.03 from the architecture.

### 09_conclusion.tex:23 · high · внутренний термин без пояснения

- **Q:** The same layer that helps on every greenfield task erases the result on \mlabWiped{} of \mlabRepeated{} tasks that start from a working script, and handed to another architecture it costs most of the trials for a reason two paragraphs long.
- **P:** «greenfield» в заключении не раскрыто; «erases the result» и «for a reason two paragraphs long» стоят вместо факта и причины; 44 слова.
- **R:** The same layer improves every TabReD task, where the agent starts from scratch, and leaves AutoDS-Tools with no submission on 3 of 8 MLAgentBench tasks, where a working script was already in place. Appended to the Terminus-2 task text it ends most trials without a submission. The agent launches a fit in the foreground, sees a terminal that has stopped producing output, and declares the task finished while the fit is still running.

### 09_conclusion.tex:26 · medium · перегруженное предложение

- **Q:** On three published scientific tasks the same pattern held outside benchmark conditions: the open harness, given the task alone, matched or beat the author baselines where the split is comparable, and the library prescription that the multi-agent system ran on cost it every attempt.
- **P:** 47 слов; «cost it every attempt» — неясно, кому «it»; системы названы описательно вместо имён.
- **R:** On three published scientific tasks, outside benchmark conditions, the same pattern held. Terminus-2, given the task text alone, matched or beat the author baselines where the split is comparable. Given the library prescription that AutoDS-Tools runs on, Terminus-2 produced no submission in any of nine attempts.

### 09_conclusion.tex:29 · medium · прочее (отрицание, афоризм, ремарка)

- **Q:** A layer measured in one architecture has not been measured in another, and this, we suggest, is why aggregate ablations of knowledge injection in the literature disagree.
- **P:** Афористичная формулировка плюс «is why» из запрещённого списка.
- **R:** A layer measured in one architecture has not been measured in another. We suggest this is the source of the disagreement among published ablations of knowledge injection.

### 09_conclusion.tex:34 · medium · перегруженное предложение

- **Q:** An agentic system's value lies in coverage, cost and the tasks where no such baseline exists; there, in the case studies, an open 31B model told which library and featurisation to use exceeded two of three published author baselines.
- **P:** «model told which library ... to use exceeded» читается как «модель сказала», потом приходится перечитывать; правило трёх «coverage, cost and the tasks».
- **R:** An agentic system's value lies in coverage, cost and the tasks where no such baseline exists. In the case studies an open 31B model, told which library and featurisation to use, exceeded two of three published author baselines.
