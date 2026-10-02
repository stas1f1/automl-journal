# How the agentic ML-engineering literature states claims, names concepts, reports ablations and draws figures

Research memo for the FGCS revision. Date: 2026-10-03. Method: 47 arXiv records pulled through the arXiv API (abstracts verbatim), 34 full texts pulled from arxiv.org/html and parsed for section headings, figure and table captions, and key sentences; three web pages (Anthropic "Building effective agents", Anthropic Agent Skills post, mini-swe-agent README, FEDOT.LLM README). All quotes below are verbatim from those sources. Items I could not verify are marked [UNVERIFIED].

## 1. Terminology for the three axes

### 1a. The architecture axis: "scaffold" (2024 to 2025), "harness" (2026)

Word counts in the full texts show the shift. "scaffold" appears 30 times in MLE-bench (Chan et al., ICLR 2025, 2410.07095), 112 times in HAL (Kapoor et al. 2025, 2510.11977), 156 times in the "Double Measurement Confound" paper (2609.09218). "harness" appears 93 times in SkillsBench (2602.12670), 107 times in Brilliantov et al. (2609.40303) and 178 times in Hu et al. (2609.32459), with "scaffold" at 2, 6 and 3 in the same papers.

- MLE-bench abstract: "We use open-source agent scaffolds to evaluate several frontier language models on our benchmark, finding that the best-performing setup--OpenAI's o1-preview with AIDE scaffolding--achieves at least the level of a Kaggle bronze medal in 16.9% of competitions." Body text: "MLAB and OpenHands are general-purpose scaffolds that take actions by calling tools; AIDE is purpose-built to perform a tree search over solutions on Kaggle competitions."
- MLGym (Nathani et al. 2025, 2502.14499) treats the two words as synonyms: "they vary both the harnesses (also known as scaffolds) and the LLMs when comparing performances."
- Terminal-Bench (Merrill et al. 2026, 2601.11868) uses "harness" for the runner and "agent"/"scaffold" for the policy around the model: "Terminal-Bench tasks are implemented in the Harbor task format and executed using the Harbor harness." On Terminus 2: "we created a simple scaffold, Terminus 2, which serves as a neutral testbed for comparing model performance. Terminus 2 has a single tool, a headless terminal, and completes tasks using only Bash commands."
- Hu et al. 2026 (2609.32459): "The agent harness substantially shapes how SE agents interact with repositories, execute actions, and validate solutions." Their taxonomy of harness components (Section 2.2): Tools, Context and Memory, Planning, Subagents, Skills.
- Brilliantov et al. 2026 (2609.40303): "modern MLE agents are deployed on top of increasingly elaborate machinery: multi-agent orchestrators, dedicated retrieval subagents, and more." They call the alternative "a minimal-harness coding agent baseline".
- Anthropic's workflow/agent split: "Workflows are systems where LLMs and tools are orchestrated through predefined code paths." "Agents, on the other hand, are systems where LLMs dynamically direct their own processes and tool usage." "At Anthropic, we categorize all these variations as agentic systems."
- "Multi-agent system (MAS)" and "single-agent system (SAS)" are the fixed labels in Kim et al. 2025 (2512.08296) and Cemri et al. 2025 (2503.13657).
- Caution on "scaffold": Agent K (Grosnit et al. 2024, 2411.03562) uses it 113 times in the Vygotsky sense ("scaffolded learning"), unrelated to code around a model.

Recommendation for axis (a). Use "harness" as the noun for the thing you vary, define it once in the introduction as the code around the model (tools, control flow, prompts, memory), and attach the three labels in the Anthropic taxonomy: a workflow (your rigid AutoML pipeline with an LLM front end: "orchestrated through predefined code paths"), a multi-agent system (six agents), and a minimal coding-agent harness (Terminus-2, single bash tool). Mention "scaffold" once in parentheses for readers who learned the 2024 word. Avoid "framework" and "pipeline" for this axis: in this literature "pipeline" is the ML artefact the agent produces (72 hits in AutoML-Agent, all in that sense) and "framework" names both software packages and the agents themselves.

### 1b. The injected-instructions axis: "Skills" (2025 to 2026), "expert-provided knowledge", "context files"

- Anthropic Agent Skills post: "A skill is a directory containing a SKILL.md file that contains organized folders of instructions, scripts, and resources that give agents additional capabilities." "Building a skill for an agent is like putting together an onboarding guide for a new hire." Also: "capturing and sharing their procedural knowledge".
- SkillsBench (Li et al. 2026, 2602.12670): "Skills encode standard operating procedures, domain conventions, and task heuristics as modular artifacts mediated by the agent harness." They name the arms "no-Skills" and "curated-Skills" and treat Skills as one case of "runtime augmentation paradigms" (Table 1).
- Coding-agent papers say "context files" or "instruction files": Gloaguen et al. 2026 (2602.11988) "repository-level context files"; Lulla et al. 2026 (2601.20404) "repository-level instructions"; Chatlatanagulchai et al. 2025 (2511.12884) "context files for agentic coding".
- Science and data-science benchmarks say "expert-provided knowledge": ScienceAgentBench (Chen et al., ICLR 2025, 2410.05080): "(c) Expert-Provided Knowledge, which includes explanations for scientific terms, formulas to conduct analysis, and example usages of programming tools." DS-Agent (Guo et al., ICML 2024, 2402.17453) says "expert knowledge from Kaggle" and "human insights" (31 hits).
- R&D-Agent (Yang et al. 2025, 2505.14738) uses "external knowledge" for retrieved material (Appendix C.2).
- MLZero (Fang et al. 2025, 2505.13941) uses "-ext*: without external knowledge" as an ablation label.
- "Priors" is used for model priors in tabular ML (TabArena, 22 hits), almost never for text given to an agent.

Recommendation for axis (b). "Skill" is the 2026 term for a file of procedural instructions mounted into a harness, and SkillsBench gives you the paired-arm vocabulary (no-Skills vs curated-Skills, "absolute gain Δ in pp", "normalized gain g"). If the FGCS reader may be older-school, write "an instruction file (an Agent Skill in current terminology)" at first use and then say "Skill". Separate its two contents by name: "library guidance" (which AutoML library) and "training discipline" (validation and leakage rules). "Prescribed knowledge" is your own coinage; nobody else uses it, so define it or drop it.

### 1c. The model axis

"backbone" is standard where the model is held fixed across harnesses: Brilliantov et al. (84 hits: "the same frontier LLM backbone", "pointing to the backbone as the primary driver for performance"), MLE-Dojo (13 hits), R&D-Agent ("backend LLMs"). "open-weight" is used by Terminal-Bench ("Terminus 2 and Kimi K2 Thinking performing best among the open-weight models"), ScienceAgentBench ("five open-weight and proprietary LLMs"), Hu et al. ("two prominent open-weight model families"). "base model" is used loosely in SE papers. Say "a single open-weight 31B backbone".

## 2. How headline claims are stated in abstracts

Pattern in almost every abstract: (1) one sentence of context, (2) one sentence of gap, (3) "We introduce/present X", (4) one or two sentences with the key numbers, (5) one sentence of implication or release. The empirical-comparison papers put the finding, with its condition, in a single sentence.

1. MLE-bench (2410.07095): "We use open-source agent scaffolds to evaluate several frontier language models on our benchmark, finding that the best-performing setup--OpenAI's o1-preview with AIDE scaffolding--achieves at least the level of a Kaggle bronze medal in 16.9% of competitions. In addition to our main results, we investigate various forms of resource scaling for AI agents and the impact of contamination from pre-training." Pattern: setup named in full (model + scaffold), one number, then secondary studies listed.
2. Brilliantov et al. (2609.40303): "In this paper we find that, under an equal time budget and the same frontier LLM backbone, open-source state-of-the-art harnesses provide no advantages over a single session of a minimal-harness coding agent baseline, pointing to the backbone as the primary driver for performance. Via a series of large-scale systematic ablation studies, we argue that the machinery layers become redundant in the coding agent setting. We conclude that the effort spent elaborating hand-crafted harnesses around strong models yields poor returns for current MLE benchmarks." Pattern: controls stated first ("under an equal time budget and the same ... backbone"), then the null result, then the scoped conclusion ("for current MLE benchmarks").
3. Hu et al. (2609.32459): "Experimental results show that harness effectiveness depends jointly on model capability and task type. Complex harnesses provide diminishing marginal gains on SWE-style issue repair as model capability improves, but can benefit stronger models on more complex and open-ended repository-level tasks." Pattern: an interaction claim, then the two directions of it.
4. SkillsBench (2602.12670): "curated Skills lift task-macro pass rate from 33.9% to 50.5% (+16.6 pp; 25.5% normalized gain), with substantial configuration-level heterogeneity (+4.1 to +25.7 pp)." Pattern: before and after, absolute and relative gain, range across configurations.
5. Gloaguen et al. (2602.11988): "Surprisingly, we find that providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average." Then: "developer-committed files outperform LLM-generated ones by a significant margin of 7% on average." Pattern: null on the primary metric, cost effect, then the one condition that does work.
6. ScienceAgentBench (2410.05080): "Given three attempts for each task, the best-performing agent can only solve 32.4% of the tasks independently and 34.3% with expert-provided knowledge." And: "without expert-provided knowledge, Claude-3.5-Sonnet using self-debug can successfully solve 10.8% more tasks than using OpenHands CodeAct while costing 17 times less API fees." Pattern: the budget ("three attempts") is inside the sentence; knowledge effect given as two numbers side by side.
7. Kim et al. (2512.08296): "Relative performance change compared to single-agent baseline ranges from +80.8% on decomposable financial reasoning to -70.0% on sequential planning, demonstrating that architecture-task alignment determines collaborative success." Pattern: range across tasks, then the mechanism.
8. Agentless (Xia et al. 2024, 2407.01489): "Our results on the popular SWE-bench Lite benchmark show that surprisingly the simplistic Agentless is able to achieve both the highest performance (32.00%, 96 correct fixes) and low cost ($0.70) compared with all existing open-source software agents!" Pattern: accuracy and cost in one sentence.
9. DS-Agent (2402.17453): "Empirically, DS-Agent with GPT-4 achieves 100% success rate in the development stage, while attaining 36% improvement on average one pass rate across alternative LLMs in the deployment stage. In both stages, DS-Agent achieves the best rank in performance, costing $1.60 and $0.13 per run with GPT-4, respectively."
10. MLAgentBench (Huang et al., ICML 2024, 2310.03302): "We benchmark agents based on Claude v1.0, Claude v2.1, Claude v3 Opus, GPT-4, GPT-4-turbo, Gemini-Pro, and Mixtral and find that a Claude v3 Opus agent is the best in terms of success rate. It can build compelling ML models over many tasks in MLAgentBench with 37.5% average success rate. However, the success rates vary considerably; they span from 100% on well-established older datasets to as low as 0% on recent Kaggle challenges".

What this means for your abstract. The senior reader's question ("does architecture not matter and only a skill is needed?") is answered in this literature by one sentence that names the controls, the null or non-null for each axis, and the scope. A template built from items 2, 4 and 5: "Holding the backbone (one open-weight 31B model) and the time budget fixed, we find that [the instruction file / library guidance] changes [metric] by [Δ pp, range across benchmarks], whereas moving from [workflow] to [six-agent system] to [minimal terminal harness] changes it by [Δ pp]; the harness still determines [valid-submission rate / cost / wall-clock]. We conclude that for [tabular tasks on a mid-size open model] [X], and that this does not extend to [Y]."

## 3. How performance and gains are reported

Metrics, with their canonical definitions:

- Medal rates: "any medal", "silver and above", "gold" (MLE-bench; AIRA Fig. 5). "Valid Subm. (%) is the fraction of all competitions (not just those with a submission) where the submission passed validity checks. Above Median (%) is the fraction of competitions where the score was strictly above the median of human Kaggle participants." (AIDE Table 3 caption, quoting MLE-bench.)
- AutoKaggle (Li et al. 2024, 2410.20424) separates "Made Submission" from "Valid Submission" and defines a composite: "CS = 0.5 × VS + 0.5 × ANPS". AutoML-Agent (Trirat et al., ICML 2025, 2410.02958) uses "success rate (SR) of code generation and the normalized performance score (NPS) of the built pipelines" plus the same "comprehensive score (CS)".
- Human-relative: "Exceeds % of humans indicates the percentage of human Kaggle participants being outperformed by the agents" (AIDE Table 1). MLRC-Bench (Zhang et al., NeurIPS 2025 D&B, 2504.09702): "closes only 9.3% of the gap between baseline and top human participant scores". Agent K: "Elo-MMR score of 1694".
- Rank-based: DS-Agent "Mean rank and best rank w.r.t. task-specific evaluation metric results on 12 data science tasks"; SELA (Chi et al. 2024, 2410.17238) "average Normalized Score (NS), average rank, and average best rank" plus "win rate of 65% to 80% against each baseline"; MLZero "average rank of 1.43". MLGym uses "performance profile curves (Dolan and Moré, 2002)" and the AUP score.
- Improvement over starter code: MLAgentBench "the percentage over 8 trials where the LM-based agent achieves an 10% improvement on the performance metric over the baseline in the starter code."
- Cost and time: DS-Agent "$1.60 and $0.13 per run"; HAL "21,730 agent rollouts ... with a total cost of about $40,000"; Brilliantov Fig. 3 box plots of "cumulative input, output and modelled cache-read tokens ... plus a fourth group giving the resulting per-run USD cost"; Lulla et al. "lower median runtime (Δ 28.64%) and reduced output token consumption (Δ 16.58%)"; Gloaguen et al. "average number of steps ... and execution cost (in USD ...) per ... instance".

Run counts and uncertainty, in the order of how often they appear:

- 3 seeds, mean ± SEM: MLE-bench Table 2 "Each experiment is repeated with 3 seeds, except o1-preview (AIDE) and GPT-4o (AIDE) which use 16 and 36 seeds respectively. Scores represent the mean ± one standard error of the mean." R&D-Agent Table 2: "mean ± SEM from three independent runs with different random seeds." MLE-STAR Table 1 copies the MLE-bench sentence. SELA: "Each method, except for AutoGluon, is run three times for each dataset. AutoGluon, being deterministic, is run only once."
- 5 runs: DS-Agent development stage ("five repetitive trials"), AI Agents That Matter ("We run each agent five times"), Terminal-Bench ("we run the benchmark at least five times, resulting in a total of 32,155 trials").
- 8 trials, best attempt: MLAgentBench; MLRC-Bench "we perform 8 trials per configuration and report the best attempt", footnoted "limited to 8 due to budget constraints on API usage."
- 10 runs: DS-Agent deployment stage; AIRA Fig. 8 "10 independent runs per task"; AIRA Fig. 4 "20 seeds".
- 95% CIs by bootstrap over seeds, macro-averaged over tasks: Brilliantov "We report 95% Confidence Intervals (CIs) on macro-task averages, holding the set of tasks fixed and bootstrapping on the seeds available for each task." AIRA Fig. 5 "95% confidence intervals computed using stratified bootstrapping." SkillsBench marks CIs on every bar. Gloaguen et al. use a "Two-sided Cochran-Mantel-Haenszel test" for paired resolution rates.
- Honest under-powering is stated, not hidden: R&D-Agent Table 3 "Full System shows mean ± SEM over 3 runs; ablation results report single representative runs due to computational constraints." Brilliantov: "at our current statistical power level, we cannot make strong conclusions about these results".

Guidance: report mean ± SEM over at least 3 seeds per cell, and bootstrap CIs on any difference you call a finding. Report the valid-submission rate separately from the quality metric, always, because MLE-bench made that split canonical: "All agents often failed to create valid submissions, despite having access to the validation server."

## 4. How ablations are named and tabulated

- Column-per-removed-component with "w/o": R&D-Agent Table 3 columns "Full System | w/o Planning | w/o Exploration Path | w/o Reasoning Pipeline | w/o Memory Context", rows "Avg. Loops, Improve Rate (%), First-Medal (h), Medal Rate (%), Any Medal (%)", and a bullet list "w/o Planning (24% relative decline)" etc. Caption: "Each column removes one component while preserving others."
- Suffix codes: MLZero "def: default settings of each agent, 8B*: using LLama 3.1 8B, -ext*: without external knowledge, -epi*: without episodic memory, +rea*: with reasoning LLM, +ext*: with external knowledge."
- Plus/minus interventions on a base: Brilliantov Table 1 "+ indicates interventions on top of base, - indicates intervention removals."
- Tool-set ablation as rows: AutoKaggle Table 2 rows "No Tools / DC Tools / DC & FE Tools / All Tools", reported for VS and CS.
- Arm naming by condition: SkillsBench "A: instruction alone; B: curated bundle ...; C: the agent authors its own skill documents". Gloaguen et al. "None / LLM / Dev." for context-file conditions.
- Temporal ablation: R&D-Agent Fig. 3 "Development Phase Temporal Ablation. Medal acquisition rate ... over 12 hours reveals when and how each component contributes."

Section structure that recurs (headings verbatim): MLE-STAR "4.1 Main results / 4.2 Ablation studies / 5 Discussion"; R&D-Agent "4.2 Main Results / 4.3 Ablation Study / 4.3.1 Research Phase Ablation Study / 4.3.2 Development Phase Ablation Study"; DS-Agent "4.2.1 Main Results / 4.2.2 Ablation Study / 4.3.2 Further Analyses" plus appendix "C.2 Case Study / C.3 Error Mode Analyses"; AutoML-Agent "4.2 Main Results / 4.3 Additional Analysis (Ablation Study, hyperparameter study)"; Terminal-Bench "4.1 Cost and Model Performance / 4.4 Trajectory-Level Error Analysis / 4.5 Command-Level Error Analysis"; Brilliantov "4 What interventions actually matter? / 4.1 Coding agent environment / 4.2 Search primitives / 4.3 Autonomy / 4.4 Multi-agent orchestration / 5 Generalization to production harnesses / 5.2 Trace Analysis"; Hu et al. use RQ1/RQ2/RQ3 headings with findings as subsection titles ("RQ1.1-Scaling of Harness Performance with Model Capability"). SkillsBench and Kim et al. use "Finding N: <claim>" as run-in headings ("Finding 3: Harness choice materially changes how the same model uses Skills.").

The split is therefore: main results = the full systems on the full benchmark; ablation = one factor removed at a time, on a subset if needed, with the subset named ("40-competition subset", "fixed14 split"); analysis = behaviour over time, traces, failure taxonomy, cost; case study = one task walked through, usually in the appendix.

## 5. Figure conventions

Architecture diagrams (two inspected as images, others from captions):

1. R&D-Agent Fig. 2 (2505.14738). Two large coloured bands, blue for the Research Agent and purple for the Development Agent, six numbered components (1 Planning ... 6 Evaluation Strategy), a tree of green (improved) and red (failed) nodes with a legend, arrows left to right. About 12 boxes. Caption 58 words: "Framework of R&D-Agent. R&D-Agent works in an iterative loop in which the Research Agent proposes ideas and the Development Agent implements them into runnable solutions to obtain feedback from data. ..." What makes it legible: one colour per agent, numbers that match the section numbers, and a legend for node states.
2. MLE-STAR Fig. 2 (2506.15692). Three stacked horizontal panels (a) Initialization, (b) Target code block extraction, (c) Code block refinement; the same robot icon reused with a subscript naming the agent role; real snippets of prompts and scores (0.91, 0.90, 0.85) inside the flow. Caption 105 words. Legible because each panel is one left-to-right pass and the subscripts map to the appendix prompts A.1 to A.13.
3. MLE-bench Fig. 1 (2410.07095). One environment box with three parts (description, dataset, grading code) and a leaderboard. Caption 36 words: "MLE-bench is an offline Kaggle competition environment for AI agents. Each competition has an associated description, dataset, and grading code. Submissions are graded locally and compared against real-world human attempts via the competition's leaderboard."
4. Hu et al. Fig. 2 (2609.32459): "The general architecture of modern agent harnesses." (9 words) followed by Fig. 3 "Overview of our agent harness study: (1) joint model–harness–task effects and (2) component-level harness analysis." (17 words). A study-design figure separate from the system figure is common in 2026 empirical papers (also SkillsBench Fig. 3 "Anatomy of a SkillsBench task", Gloaguen Fig. 1, 98 words).

Result figures:

5. R&D-Agent Fig. 1: "Stacked bars show any medal rates for Low==Lite (22 tasks), Medium (38 tasks), and High (15 tasks) complexity levels. The dashed line indicates overall performance (mean ± SEM)." (51 words.) One bar per system, stacked by difficulty, overall as a dashed line.
6. Brilliantov Fig. 1: "Any-medal rate (↑, top) and mean percentile (↑, bottom), self-select (filled) vs. oracle (open), macro-averaged over the full fixed30 set at 24h time budget. Brackets are 95% bootstrap CIs. Backbones are grouped along a single shared x-axis; color identifies the harness." (48 words.) This is the closest template to your design: x = backbone, colour = harness, two metrics stacked vertically, filled vs open markers for two selection rules.
7. SkillsBench Fig. 1: "Each bar stacks the no-Skills baseline and curated-Skills lift; open/filled interval markers denote 95% CIs for the baseline/total. Bars are ordered by Curated-Skills pass rate and colored by model family." (59 words.) Template for showing the Skill effect: baseline segment plus lift segment per model–harness pair.
8. AIRA Fig. 4 (2507.02554): "Perceived vs. actual medal rate over 24 hours of AIDE-greedy. The curves show the mean validation (agent-reported) and held-out test medal rates across 20 seeds for all tasks. The widening band illustrates the generalization gap". (72 words.) Two curves over wall-clock time with the band between them; the figure that carries the leakage/overfitting message.
9. Terminal-Bench Fig. 5: "The Pareto frontier of agent performance showing the tradeoff between performance and cost (log scale) on Terminal-Bench 2.0." (20 words.) Fig. 1: bars with "95% confidence interval", scaffold chosen per model. Fig. 8: "LLM Judge evaluation of failure modes across models (Terminus 2 scaffold). Execution errors dominate, while coherence and verification failures occur at comparable rates." (25 words.) HAL Fig. 2 is the same Pareto design with a dotted frontier line (195-word caption, too long).
10. Gloaguen Fig. 3: "Resolution rate for 4 different models, without context files, with LLM-generated context files, and with developer-written context files, on SWE-bench (left) and CTXbench (right)." (26 words.) Grouped bars, 3 conditions × 4 models × 2 panels.
11. AI Agents That Matter Fig. 1 (2407.01502): accuracy vs mean total cost scatter, five runs per point, with the simple baselines on the frontier (136-word caption); error bars moved to Fig. A1 with "95% confidence intervals ... and the minimum and maximum values".

Caption lengths: main-text figure captions in these papers run 20 to 60 words when the figure is a chart and 50 to 105 words when it is a system overview. Captions above 130 words appear only in HAL, Kim et al. and Kapoor et al., where the caption carries method detail. The first sentence of a result caption states the finding ("The percentage of medals achieved increases with the number of attempts allowed."), the second names the encoding (what bars, lines, markers and error bars mean), the third gives n and the budget.

## 6. Findings to cite and position against

Harness matters less with stronger models, or a simple harness matches a complex one:

- Brilliantov, Hernández-Cano, Abbé et al. 2026, arXiv 2609.40303: under equal time budget and backbone, four open-source MLE harnesses give no advantage over a single session of a minimal coding agent on MLE-bench and NatureBench; "the coding agent environment is the dominant factor and that no further intervention yields a statistically significant gain"; "multi-agent orchestration introduced in previous work is less critical for modern frontier LLMs operating in coding agent environments." [venue: preprint]
- Hu, Zhang, Yu et al. 2026, arXiv 2609.32459: "Complex harnesses provide diminishing marginal gains on SWE-style issue repair as model capability improves"; "the OpenCode advantage decreases from about 6 pp for Qwen3-Max to 2.67 pp for Qwen3.7-Max". [preprint]
- Xia, Deng, Dunn, Zhang 2024, arXiv 2407.01489 (Agentless): a three-phase non-agentic procedure scores 32.00% on SWE-bench Lite at $0.70, above all open-source agents at the time.
- Chen et al., ICLR 2025, arXiv 2410.05080 (ScienceAgentBench): self-debug beats OpenHands CodeAct by 10.8 points at 17× lower cost for Claude-3.5-Sonnet.
- Kapoor, Stroebl, Siegel, Nadgir, Narayanan 2024, arXiv 2407.01502 (AI Agents That Matter): "Our simple baselines offer Pareto improvements over SOTA agents" on HumanEval; argues for cost-controlled, Pareto-curve evaluation.
- Merrill et al. 2026, arXiv 2601.11868 (Terminal-Bench): a one-tool bash scaffold (Terminus 2) is the "neutral testbed"; "Codex CLI paired with GPT-5.2 achieves the highest average resolution rate of 63%, followed by Terminus 2 with Claude Opus 4.5 and Terminus 2 with Gemini 3 Pro at 58% and 57%".
- Starace et al. 2025, arXiv 2504.01848 (PaperBench): a prompt change (IterativeAgent) "significantly boost[s] scores for o3-mini and o1 compared to BasicAgent, but hamper[s] Claude 3.5 Sonnet, highlighting models' sensitivities to prompting." Harness × model interaction.
- Yang et al. 2024, arXiv 2405.15793 (SWE-agent): the opposite pole; the agent-computer interface "significantly enhances" performance (pass@1 12.5% on SWE-bench). Cite for the claim that interface design matters at weaker model strength.
- Chan et al., ICLR 2025, arXiv 2410.07095 (MLE-bench): the purpose-built scaffold beat general ones with the same model: "GPT-4o (AIDE) achieves more medals on average than both MLAB and OpenHands (8.7% vs. 0.8% and 4.4% respectively), despite making a similar number of valid submissions." Also "Small details in scaffold implementations can make a big difference."
- Toledo et al. 2025, arXiv 2507.02554 (AIRA): "AIDE's operators, rather than the search algorithm, are a bottleneck to better performance"; search policy changes alone give no gain.
- Kapoor et al. 2025, arXiv 2510.11977 (HAL): "task-specific agents consistently outperform" generalist scaffolds, at higher cost; "higher reasoning effort reducing accuracy in the majority of runs."

Instructions and Skills change outcomes (both directions):

- Li et al. 2026, arXiv 2602.12670 (SkillsBench): curated Skills lift pass rate 33.9% to 50.5% across 18 model–harness configurations; "Harness choice materially changes how the same model uses Skills"; "small models with Skills can match larger models without"; "Self-generated Skills do not substitute for curated ones."
- Gloaguen et al. 2026, arXiv 2602.11988: context files "do not generally improve task success rates, while increasing inference cost by over 20% on average"; developer-written ones beat LLM-generated ones by 7%; "instructions in the context files are well followed by coding agents, repository overviews ... are not helpful."
- Lulla et al. 2026, arXiv 2601.20404: AGENTS.md presence associated with 28.64% lower median runtime and 16.58% fewer output tokens.
- Chatlatanagulchai et al. 2025, arXiv 2511.12884: developers put "test procedures (75.9%), implementation details (70.8%), and architecture (68.1%)" in context files.
- Yang et al. 2025, arXiv 2505.14738 (R&D-Agent, App. C.2): retrieved external knowledge hurt: "incorporating external knowledge surprisingly harms overall performance, with particularly severe degradation on Low==Lite tasks" (68.2 to 54.6 any-medal on Lite).
- Guo et al., ICML 2024, arXiv 2402.17453 (DS-Agent): case-based reuse of Kaggle "human insights" gives 100% success rate with GPT-4 in development and a 36% one-pass improvement for weaker LLMs in deployment.
- Hollmann, Müller, Hutter 2023, arXiv 2305.03403 (CAAFE): context (dataset descriptions) given to the LLM drives feature-engineering gains; the earliest "knowledge in the prompt" result in tabular AutoML.

Multi-agent adds cost or fails in specific ways:

- Kim et al. 2025, arXiv 2512.08296: "coordination yields diminishing returns once single-agent baselines exceed certain performance"; "tool-heavy tasks appear to incur multi-agent overhead"; range +80.8% to -70.0% relative to single agent.
- Cemri et al. 2025, arXiv 2503.13657 (MAST): 14 failure modes in 3 categories "(i) system design issues, (ii) inter-agent misalignment, and (iii) task verification."
- Jing et al. 2024, arXiv 2409.07703 (DSBench): "The AutoGen framework tends to consume more time to finish data analysis tasks and has higher costs compared to the original vanilla model-only method."

Agents fail on validation, leakage and submission format:

- Chan et al. 2025 (MLE-bench): "All agents often failed to create valid submissions, despite having access to the validation server."
- Toledo et al. 2025 (AIRA): "we find systematic overfitting: selecting the final solution in a search graph by its test—rather than validation—score, would increase the medal rate by 9 to 13 % (absolute scale)".
- Brilliantov et al. 2026: defines "validation gap" between self-selected and oracle-best runs; "hidden validation" split as a mitigation (App. C.3).
- Nam et al. 2025, arXiv 2506.15692 (MLE-STAR): "LLM-generated Python scripts might have the risk of introducing data leakage, for example, by improperly accessing information from a test dataset during training dataset preparation"; adds a "data leakage checker" and "data usage checker" agent.
- Huang et al., ICML 2024 (MLAgentBench): "key challenges ... how to effectively plan and replan over long horizons and hallucination about the current progress"; success from 100% on house-price to 0 to 25% on recent Kaggle tasks.
- Kapoor et al. 2025 (HAL): "The TAU-bench Few Shot agent suffered from data leakage that invalidated our results; we discovered this through automated log analysis".
- Zhang et al. 2026, arXiv 2609.09218: "scaffold ownership is an uncontrolled axis wherever we probed it"; argues benchmark scores must be read "together with their scaffolding level".

Also relevant for positioning: Rubachev et al. 2024, arXiv 2406.19380 (TabReD) for the temporal-split argument; Erickson et al., NeurIPS 2025 D&B, arXiv 2506.16791 (TabArena) as the model benchmark, with no LLM-agent evaluation in it (verified by text search: no agent results); Grosnit et al. 2024, arXiv 2411.03562 (Agent K); Fang et al. 2025, arXiv 2505.13941 (MLZero, the AutoGluon-team system that keeps its result "even with a compact 8B LLM"); Lapin, Hromov, Chumakov et al. 2025, arXiv 2507.13413 (LightAutoDS-Tab); Kulibaba et al. 2025, arXiv 2508.10177 (KompeteAI); Trirat et al., ICML 2025 (AutoML-Agent, with an appendix "A.2 Challenges with Smaller Models" and five system-prompt role variants in C.2); Luo et al., ACM MM 2024, arXiv 2408.00665 (AutoM3L); Hong et al. 2024, arXiv 2402.18679 (Data Interpreter); Qiang et al. 2025, arXiv 2505.07782 (MLE-Dojo); Egg et al. 2025, arXiv 2506.23719 (DABstep); Huang et al., EMNLP 2024, arXiv 2410.07331 (DA-Code); Lu et al. 2024, arXiv 2408.06292 (AI Scientist); Gottweis et al. 2025, arXiv 2502.18864 (Co-Scientist).

[UNVERIFIED] FEDOT.LLM: the GitHub README (aimclub/FEDOT.LLM) describes "an LLM-based prototype for next-generation AutoML" and lists no paper; I found no arXiv record under "FEDOT" with LLM in the abstract. Cite the repository or ask the ITMO authors for the reference. [UNVERIFIED] "AutoGluon Assistant" as a paper: the MLZero paper is the one I could find; the product name maps to the same codebase to my knowledge, but I did not confirm this from the paper. [UNVERIFIED] "The Bitter Lesson" (Sutton 2019) is a blog essay, no arXiv id; I did not fetch it. Harness-Bench "6×8 factorial (Yao et al. 2026)" is cited inside 2609.09218; I did not locate its id.

## 7. Reusable sentence patterns (adapted from the sources above)

Setup and controls
1. "Under an equal time budget and the same backbone, A provides no advantage over B."
2. "We hold the model, the time budget and the task set fixed and vary only the harness."
3. "Each experiment is repeated with N seeds; scores are the mean ± one standard error of the mean."
4. "We report 95% confidence intervals on macro-task averages, bootstrapping on the seeds available for each task."
5. "Given k attempts per task, the best configuration solves X% of tasks without the instruction file and Y% with it."
6. "Each column removes one component while preserving the others."
7. "Ablation results report single runs due to computational constraints; the full system reports mean ± SEM over three runs."

Headline results
8. "The best-performing setup, model M with harness H, achieves [metric] in X% of tasks."
9. "Curated instructions raise the average pass rate from X% to Y% (+Δ pp; g% normalized gain), with configuration-level gains ranging from +a to +b pp."
10. "Providing context files does not generally improve task success, while increasing inference cost by over Z% on average."
11. "A achieves more medals on average than B and C (x% vs. y% and z%), despite making a similar number of valid submissions."
12. "Relative to the single-agent baseline, performance ranges from +p% on [task type] to −q% on [task type]."
13. "Harness effectiveness depends jointly on model capability and task type."
14. "The advantage of the elaborate harness decreases from about 6 pp for model M1 to 2.7 pp for the stronger M2."
15. "Self-debug solves 10.8% more tasks than the agent framework while costing 17 times less."
16. "The agent closes only X% of the gap between the baseline and the top human score."

Mechanism and failure
17. "All agents often failed to create valid submissions, despite having access to a validation tool."
18. "We find systematic overfitting: selecting the final solution by test score would increase the medal rate by 9 to 13 points."
19. "The operators, rather than the search algorithm, are the bottleneck to better performance." (Rewrite without the contrast for your own text: "The bottleneck is the operator set; changing the search policy alone gives no gain.")
20. "Instructions in the file are well followed; repository overviews are not helpful."
21. "Incorporating external knowledge harms overall performance, with the largest degradation on the easiest tasks."
22. "Execution errors dominate; coherence and verification failures occur at comparable rates."
23. "Small details in harness implementation can make a large difference."
24. "Multi-agent coordination yields diminishing returns once the single-agent baseline exceeds a threshold."

Scope and implication
25. "The effort spent elaborating hand-crafted harnesses around strong models yields poor returns for current MLE benchmarks."
26. "These results hold for [tabular tasks, 31B open-weight model, 24h budget]; we do not claim they extend to [multimodal tasks / frontier models]."
27. "Benchmark scores should be interpreted together with their scaffolding level, scoring criterion, and reliability profile."
28. "Small models with Skills can match larger models without them."
29. "At our current statistical power, arms whose CI contains zero are indistinguishable."
30. "Developers should report the model, the harness, internet access, hardware, runtime and any solutions included in prompts."

## Sources consulted

arXiv (id, first author, year): 2310.03302 Huang (MLAgentBench); 2410.07095 Chan (MLE-bench); 2502.13138 Jiang (AIDE); 2506.15692 Nam (MLE-STAR); 2505.14738 Yang (R&D-Agent); 2410.02958 Trirat (AutoML-Agent); 2402.17453 Guo (DS-Agent); 2402.18679 Hong (Data Interpreter); 2410.17238 Chi (SELA); 2410.20424 Li (AutoKaggle); 2411.03562 Grosnit (Agent K); 2505.13941 Fang (MLZero); 2408.00665 Luo (AutoM3L); 2507.13413 Lapin (LightAutoDS-Tab); 2508.10177 Kulibaba (KompeteAI); 2305.03403 Hollmann (CAAFE); 2409.07703 Jing (DSBench); 2410.07331 Huang (DA-Code); 2506.23719 Egg (DABstep); 2502.14499 Nathani (MLGym); 2504.09702 Zhang (MLRC-Bench); 2410.05080 Chen (ScienceAgentBench); 2504.01848 Starace (PaperBench); 2506.16791 Erickson (TabArena); 2406.19380 Rubachev (TabReD); 2601.11868 Merrill (Terminal-Bench); 2405.15793 Yang (SWE-agent); 2407.01489 Xia (Agentless); 2402.01030 Wang (CodeAct, abstract only); 2407.01502 Kapoor (AI Agents That Matter); 2510.11977 Kapoor (HAL); 2602.12670 Li (SkillsBench); 2602.11988 Gloaguen (Evaluating AGENTS.md); 2601.20404 Lulla (AGENTS.md efficiency); 2511.12884 Chatlatanagulchai (Agent READMEs); 2602.12430 Xu (Agent Skills survey, abstract only); 2503.13657 Cemri (MAST); 2512.08296 Kim (Scaling Agent Systems); 2507.02554 Toledo (AIRA); 2505.07782 Qiang (MLE-Dojo); 2609.40303 Brilliantov (How much of a harness); 2609.32459 Hu (Beyond the Model); 2609.26760 Li (Grow the Harness, abstract only); 2609.09218 Zhang (Double Measurement Confound); 2408.06292 Lu (AI Scientist, abstract only); 2502.18864 Gottweis (Co-Scientist, abstract only); 2411.10478 Gu (survey, abstract only).

Web: anthropic.com/engineering/building-effective-agents; anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills; github.com/SWE-agent/mini-swe-agent ("Just some 100 lines of python for the agent class", "Does not have any tools other than bash", "Scores >74% on the SWE-bench verified benchmark"); github.com/aimclub/FEDOT.LLM.
