# Peer-review working draft — REVIEW-FGCS-AUTOML-SELF-001

> Private working document. Human review, policy checks, and factual verification are required. Do not submit this scaffold with unresolved placeholders. Do not make or announce an editorial decision.

## Intake record

- Reviewer capacity: `author_requested_reader`
- Peer-review model: `single_anonymized`
- Declared processing plan: `local_deterministic_tools`
- Manuscript text is not embedded by the generator.
- Conflicts: self-review of the authors' own manuscript. This is not an independent review and must not be presented as one.
- Competence limits: benchmark metrics were not independently reimplemented; artefacts of the earlier hub runs were not available.

# Comments to authors

## Evidence-bounded summary

The manuscript asks how much of an LLM agent's measured performance comes from the surrounding architecture rather than the backbone model. It holds the backbone fixed at one open 31B model and compares three systems occupying different points on a constraint axis, inside a shared execution environment, on the official temporal splits of a tabular benchmark with eighteen expert-tuned reference methods, and on a second benchmark of improve-a-baseline tasks. It further decomposes the prescribed-knowledge layer carried by one system into a tool half and a discipline half, and crosses them.

## Strengths

- The confound the paper targets is real and is targeted directly: one backbone, one execution environment, one verifier, one concurrency setting per comparison.
- The reference ceiling is a genuinely strong one (Optuna-tuned, fifteen seeds), which is rare in this literature and makes the headline gap meaningful.
- Negative and null results are reported rather than buried: provisioning is shown to be inert, and the arm that fails to submit anything is reported as such rather than dropped.
- Reproducibility discipline is unusually explicit: layer text is identified by byte length and hash, and both editions in circulation are fingerprinted.

## Status of major comments

All nine comments were closed on 8 September 2026; the text below is each finding
as raised, followed by what was changed.

## Major comments

### Major comment M1

- **CLOSED.** The architecture-only span is now reported as $0.49$ in the abstract, Section 1, Section 6 and Section 7; $0.59$ is retained only where the systems are explicitly described as deployed. The ratio claims in Section 7 were recomputed against $0.49$ and are now a factor of two and of twelve.

- Location: Section 1, Relation to the neutral-scaffold assumption; abstract, second finding.
- Observation: The headline figure "architecture alone moves the normalised score by 0.59" is computed between the multi-agent system **with its prescribed-knowledge layer applied** and the rigid pipeline. It is therefore architecture plus prescription, not architecture alone.
- Evidence or criterion: Section 6 now reports the separating arm. Removing the layer moves that system from 0.8482 to 0.7509. Against the rigid pipeline at 0.2572, the architecture-only span is 0.4937, not 0.5910.
- Why it matters: The paper's own separation contradicts its headline number, in the same document. A reviewer who reads Section 6 before the introduction will see it immediately, and the number appears in both the abstract and the contributions.
- Requested action: Report the architecture-only span as 0.49 and keep 0.59 only where it is explicitly labelled as the deployed configuration. Both are defensible; using the larger one under the smaller one's name is not.

### Major comment M2

- **CLOSED.** XGBoost is named as the comparator throughout, and the position against LightGBM (level) and CatBoost (ahead) is stated in the same sentence in the abstract, Section 1, Section 6 and Section 12.

- Location: Abstract, first finding; Section 6.
- Observation: "None matches a tuned gradient boosting model at 0.87" selects the strongest of the three gradient boosting references as the comparator.
- Evidence or criterion: On the same normalised scale the multi-agent system reaches 0.8482. LightGBM is at 0.8493, a difference of 0.0011, well inside the stated noise floor. CatBoost is at 0.7962, which the system beats by 0.05.
- Why it matters: The claim as phrased says gradient boosting is out of reach. The measurement says the system ties one tuned GBDT, beats another, and trails a third. That is a more interesting result and a more defensible one.
- Requested action: Name the comparator explicitly ("does not match tuned XGBoost at 0.87") and state the position against the other two GBDTs in the same sentence.

### Major comment M3

- **CLOSED.** The opposite-directions claim was removed from Section 1, Section 2 and Section 4 and replaced with sub-additivity, which the crossed design does support: tool half alone $0.87$, discipline half alone $0.77$, both $0.85$.

- Location: Section 1, contribution 3; Section 2; Section 4, opening.
- Observation: The claim that the two halves of the layer "move the same task in opposite directions" is not supported at the strength stated.
- Evidence or criterion: Across the eight crossed tasks the two halves have opposite signs on three. On two of those three the magnitudes are +0.10% against -0.03% and +0.47% against -0.04%, at or below the 0.1% noise floor the paper itself adopts for within-system comparison. Only `weather` shows an opposite pair with either side clearly above that floor.
- Why it matters: The claim is load-bearing: it is one of three contributions and is repeated in the related-work section as the finding that explains inconsistent ablations elsewhere.
- Requested action: Replace with the interaction the data does support and which the manuscript already reports elsewhere: the halves are strongly sub-additive, the tool half alone reaching 0.8711 against 0.8482 for both together, and on the second architecture the library half alone loses 19 of 22 trials while both halves together lose 11 of 24.

### Major comment M4

- **CLOSED.** Both endpoints now come from the generated table: $9.1\%$ to $26.0\%$.

- Location: Section 1, contribution 3, against Table `layersplit`.
- Observation: The tool share of the layer is given as "between 8.6% and 25.4%" in the introduction and as 9.1% to 26.0% in the table generated from the module itself.
- Evidence or criterion: The table is computed from the composing module; the introduction figure is not reproduced by it.
- Why it matters: A reviewer checking one number against the other finds a discrepancy in a paper whose central methodological argument is that layer text must be identified byte-exactly.
- Requested action: Take both endpoints from the table, or state which edition of the layer each range refers to.

### Major comment M5

- **CLOSED.** Section 5 now states, where the benchmark is introduced, that MLAgentBench ships no reference table, that no range exists against which to normalise, that every quantity reported on it is a within-study contrast, and that the normalised $0$-to-$1$ language belongs to TabReD alone.

- Location: Sections 5, 8, 9, and the MLAgentBench tables.
- Observation: The manuscript does not state that the second benchmark has no external reference methods at all. Every MLAgentBench claim is an internal comparison between arms or systems.
- Evidence or criterion: The consolidated metric table carries 144 published-baseline rows for the tabular benchmark and none for MLAgentBench.
- Why it matters: All normalised, range-relative language belongs to the tabular benchmark alone. Without the statement, a reader can carry the normalised framing across and read the improve-a-baseline results as positioned against a ceiling that does not exist there.
- Requested action: Say once, in the design section, that MLAgentBench carries no reference methods and that its results are read as within-study contrasts only.

## Minor comments

### Minor comment m1

- **CLOSED.** Both drafting notes removed from the manuscript. The abstract's numbers are final. The framing decision that the other note carried is tracked in the project record instead of the manuscript; the text meanwhile states the weaker non-monotonicity claim, which holds under either framing.

- Location: Abstract, final line; Section 1, contribution 2.
- Observation: Two drafting notes remain in author-facing text.
- Evidence or criterion: Direct inspection of the compiled document.
- Why it matters: They will be visible to an editor at submission.
- Requested action: Resolve or delete before submission.

### Minor comment m2

- **CLOSED.** A note on the cost table states that every figure is a mean over right-tailed distributions, gives the untreated multi-agent branch as the worked example ($10.9$ min median against a $63.2$ min mean, $13$ of $30$ trials at a ceiling), and says which figure answers which question.

- Location: Table `cost`.
- Observation: The per-trial wall-clock figures are means, and for the multi-agent rows they differ from the medians quoted in Section 7 by a factor of six (63.2 against 10.9 minutes).
- Evidence or criterion: Both figures are correct for what they measure; the distributions are heavily right-tailed, and 13 of 30 trials reached the task ceiling.
- Why it matters: A reader comparing the table to the text will read one of them as an error.
- Requested action: Add a median column, or state in the caption that the distribution is right-tailed and the text quotes medians.

### Minor comment m3

- **CLOSED.** Section 6 now states directly that the rigid pipeline falls below plain linear regression ($0.26$ against $0.29$) and names this as the sharpest form of the non-monotonicity.

- Location: Section 6.
- Observation: The rigid pipeline scores below plain linear regression on the normalised scale (0.2572 against 0.2846). The manuscript notes the neighbourhood but does not draw the comparison.
- Evidence or criterion: Normalised means over the eight tasks.
- Why it matters: It is the sharpest available statement of the non-monotonicity claim and it is currently left implicit.
- Requested action: Consider stating it directly where the non-monotonicity argument is made.

### Minor comment m4

- **CLOSED.** Both overfull boxes eliminated; the document now compiles with none.

- Location: Whole document.
- Observation: Four overfull horizontal boxes remain, the largest 12.9pt.
- Evidence or criterion: Compilation log.
- Why it matters: Cosmetic, but the journal's production stage will flag them.
- Requested action: Fix at the final compression pass.

## Limitations of this review

This is a self-review of the authors' own manuscript and carries the conflict declared above. It is not independent and must not be represented as such. Benchmark metrics were not independently reimplemented; all numeric checks were recomputed from the manuscript's own data module and the released result registry. No claim about the correctness of the underlying benchmark implementations is made. No editorial decision is expressed or implied.

# Confidential comments to editor

- Conflict: this assessment was produced by the authors on their own manuscript and is a self-check, not an independent review.
- Assistance disclosure: analysis was carried out locally with deterministic tooling; no manuscript content was sent to any external service.
- Specialist review needed: none identified within the declared scope.
