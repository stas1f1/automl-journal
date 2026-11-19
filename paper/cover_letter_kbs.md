Dear Editor,

We submit the manuscript "Where to Put Knowledge in Agentic AutoML: Language
Model, Harness, AutoML Library or Instruction File" for consideration as a
research article in Knowledge-Based Systems.

Agents built on large language models now automate data-science work. Such
an agent holds knowledge about how to build a model in four places: the
parameters of the language model, the harness around it, the AutoML library
it may call, and explicit instructions written by experts. Published
systems change all four at once, so it is not known which of them decides
accuracy and reliability. The manuscript separates these places in a
general scheme and tests three hypotheses about them. One open-weight 31B
language model runs under three harnesses on eight real-world tabular tasks
of TabReD, against eighteen tuned reference methods, and on MLAgentBench and
three scientific tasks.

The results bear on knowledge engineering for such systems. Knowledge about
search and tuning raises accuracy when an AutoML library applies it, and
agents that write their own code do not apply it on their own. Explicit
knowledge in an instruction file adds accuracy in the harness it was written
for. Moved to another harness, the same text leaves 11 of 24 trials without
a result, against 2 of 24 without it. The manuscript states these findings
as design rules on where to put knowledge in an agentic AutoML system.

The work continues lines of research published in Knowledge-Based Systems:
evolutionary AutoML for composite pipelines (Revin et al., 2023; Nikitin et
al., 2024), the survey of AutoML by He et al. (2021), and multi-agent
generation of machine-learning pipelines (Bâra et al., 2026).

All tasks, instruction files, execution traces and result tables are
released in a public repository. The manuscript is not under consideration
elsewhere, and all authors have approved the submission. Competing
interests and the use of generative AI tools are declared in the manuscript.

Sincerely,
Stanislav Chumakov, on behalf of all authors
AI Institute, ITMO University, Saint Petersburg, Russia
stas1f1@gmail.com
