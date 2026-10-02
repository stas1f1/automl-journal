# How accepted AutoML and tabular-ML papers evaluate quality and show gains

Research notes for the FGCS revision. All quotes are verbatim from the full texts listed in section 9. Where a paper could not be opened, this is stated.

## 1. Aggregation metrics

**Average rank.** The most common aggregate in this literature. Gorishniy et al. 2021: "For each dataset, ranks are calculated by sorting the reported scores; the 'rank' column reports the average rank across all datasets." TabReD's Table 3 reports "Average Rank" with a ± spread, e.g. XGBoost "2.9 ± 1.5", MLP-PLR ens. "2.4 ± 1.5". The ± there is the standard deviation of per-dataset ranks across the 8 datasets. TabReD and TabM use a tie-aware rule so that seed noise does not produce spurious ranks. TabReD, appendix C.2: "we rank method A below method B if |Bmean − Amean| < Bstddev and B score is better." TabM spells the algorithm out: "we define that the model A is better than the model B if: Amean − Astd > Bmean ... Starting from the best model (with a rank equal to 1) we iterate over models and assign the rank 1 to all models that are no worse than the best model according to the above rule. The first model in descending order that is worse than the best model is assigned rank 2 and becomes the new reference model." They add: "Intuitively, our ranks can be considered as 'tiers'."

**Normalized / scaled score.** Several formulas coexist; each paper defines its own in one sentence.
- AMLB: "we first scale all results per task between the random forest performance (0) and the best observed performance (1)". Negative values mean worse than the random forest.
- TabRepo / TabArena: "we linearly rescale the error such that the best method has a normalized score of one, and the median method has a normalized score of 0. Scores below zero are clipped to zero. These scores are then averaged across datasets." TabRepo writes it as (l_method − l_topline)/(l_baseline − l_topline), "clipping the denominator to 1e-5 and the final score value to [0,1]".
- AutoGluon-Tabular "rescaled loss": "set = 0 for the champion framework and = 1 for the worst-performing framework. The remaining frameworks are linearly scaled between these endpoints based on their relative loss."
- Grinsztajn et al. (ADTM variant): "normalizing each test accuracy between 0 and 1 via an affine renormalization between the top-performing and worse-performing models. Instead of the worse-performing model, we use models achieving the 10% (classification) or 50% (regression) test error quantile." McElfresh et al. and Auto-sklearn 2.0 use the same ADTM family.
- TabPFN v2: "The absolute scores are linearly scaled such that a score of 1.0 corresponds to the highest value achieved by any method on that dataset, whereas a score of 0 represents the lowest result."

**Relative improvement over a baseline.** TabM: "on a given dataset, the metric is defined as (score/baseline − 1)·100%, where 'score' is the metric of a given model, and 'baseline' is the metric of MLP. In this computation, for regression tasks, we convert the raw metrics from RMSE to R2 to better align the scales of classification and regression metrics." TabReD's Figure 1 uses the same quantity: "We plot average relative percentage improvement over the MLP baseline on both benchmarks."

**Win / loss / champion counts.** AutoGluon-Tabular Table 2 lists per framework "the number of datasets where each framework produced: better predictions than AutoGluon (Wins), worse predictions (Losses), a system failure during training (Failures), or more accurate predictions than all of the other 5 frameworks (Champion)". LightAutoML reports "Wins", "Avg Rank" and "Avg Reciprocal Rank". TabArena reports "#wins" and "Improvability := (err_i − best_err_i)/err_i · 100%". McElfresh counts a win when the 0-1 scaled accuracy is at least 0.99.

**Elo.** TabArena: "a 400-point Elo gap corresponding to a 10 to 1 (91%) expected win rate. We calibrate 1000 Elo to the performance of our default random forest configuration across all figures, and perform 200 rounds of bootstrapping to obtain 95% confidence intervals". Their reason: "each dataset contributes equally to Elo, hence the aggregation is not biased towards certain domains or dataset properties". Elo is used with 51 datasets; it is a large-benchmark tool.

**IQM and optimality gap** (Agarwal et al.): "IQM discards the bottom and top 25% of the runs and calculates the mean score of the remaining 50% runs". Written for RL with few runs per task, cited by tabular papers for bootstrap CIs.

What is standard for a few systems over 8-100 datasets: average rank plus one magnitude metric (scaled score or relative improvement), plus win counts in a table. Elo and Bradley-Terry trees appear only at 40+ datasets.

## 2. Statistical validation

**Demšar 2006** is the reference every tabular paper cites. The recommendation: "the Wilcoxon signed ranks test for comparison of two classifiers" and the Friedman test with a post-hoc test for several. Friedman's CD: "CD = q_α sqrt(k(k+1)/(6N))". Rule of thumb for the chi-square approximation: "when N and k are big enough (as a rule of a thumb, N > 10 and k > 5). For a smaller number of algorithms and data sets, exact critical values have been computed". On averaging raw metrics: "If the results on different data sets are not comparable, their averages are meaningless" and "Averages are also susceptible to outliers." On the sign test: "it is much weaker than the Wilcoxon signed-ranks test ... the sign test will not reject the null-hypothesis unless one algorithm almost always outperforms the other." On replicability: "the actual experiments should be conducted on as many data sets as possible." Holm over Bonferroni-Dunn: "Holm's procedure is more powerful than the Bonferroni-Dunn's and makes no additional assumptions about the hypotheses tested."

**Benavoli et al. 2016** on Nemenyi-type post-hoc tests: "the outcome of the mean-ranks test depends on the pool of algorithms originally included in the experiment"; a pair may be "declared significant if the pool comprises algorithms C, D, E and not significant if the pool comprises algorithms F, G, H". They recommend "a test whose outcome only depends on the two algorithms being compared, such as the sign-test or the Wilcoxon signed-rank test" with a multiplicity correction.

**Benavoli et al. 2017** (Bayesian): "NHST yields no information about the null hypothesis"; ROPE for accuracy: "the interval [-0.01,0.01] thus defines a region of practical equivalence (rope) for classifiers." Conclusions are worded as probabilities: "we can conclude with probability 90% that aode is practically better than nbc" and "we can conclude that nbc and aode are practically equivalent".

**Agarwal et al. 2021** (few runs): "re-sample runs with replacement independently for each task to construct an empirical bootstrap sample with N runs each for M tasks"; recommendations: "Interval estimates via stratified bootstrap confidence intervals", "Performance profiles (score distributions)", "Interquartile Mean (IQM)", "probability of improvement".

**What the applied papers do.**
- AMLB: "test for the presence of statistically significant differences in the average rank distributions using a non-parametric Friedman test at p < 0.05 (here, p ≈ 0 for every diagram) and use a Nemenyi post-hoc test to find which pairs differ." They then say CD diagrams "obfuscate the relative performance differences" and add box plots of scaled scores.
- TabArena, A.5: "critical difference diagrams (CDDs) to represent the results of a Friedman test and then a Nemenyi post-hoc test (α = 0.05) from AutoRank". Finding: "there always exists a group of not statistically significantly different top models containing at least one deep learning model and GBDT".
- McElfresh: "We use a Friedman test ... We then use a Wilcoxon signed-rank test ... With the Wilcoxon tests we use a Holm-Bonferroni correction".
- Auto-sklearn 2.0: "we ran the Wilcoxon signed-rank test as a statistical hypothesis test with α=0.05", results over 10 repetitions as mean and std.
- TabPFN v2: "we evaluated 10 repetitions, each with a different random seed and train–test split ... All confidence intervals shown are 95% confidence intervals", and "Wilcoxon P refers to the two-sided Wilcoxon signed-rank test P value" printed on the figure.
- TabReD: tie-aware ranks plus "a Tamhane's T2 test of statistical significance for multiple comparisons. Results for Tamhane's test are in Table 5", caption: "Ranking in not significantly altered compared to our simple testing procedure."
- TabM, Gorishniy 2021, AutoGluon-Tabular, TabRepo, FEDOT, LightAutoML, TPOT, MLAgentBench: no hypothesis test; they report means, std over seeds, counts.

**With 8 tasks and 3 seeds.** A Friedman/Nemenyi CD over 23 methods and N = 8 gives CD = q_0.05(23)·sqrt(23·24/48) ≈ 3.6·3.4 ≈ 12 rank positions; such a diagram shows one big connected group and carries no information. The exact Wilcoxon signed-rank test on 8 paired task means reaches two-sided p = 0.0078 only when all 8 differences point one way; the sign test needs 8 of 8 (p = 0.008) or gives p = 0.07 at 7 of 8. The honest conventions at this size are: descriptive mean rank with spread, tie-aware ranks that absorb seed noise, win counts "on k of 8 tasks", stratified bootstrap CIs over tasks and seeds, and a Bayesian signed-rank with ROPE if a probability statement is wanted.

**How non-significance is worded.** AMLB: "AUTOGLUON(B) is generally not significantly better than the second best framework" and "All AutoML frameworks except AUTOGLUON(B) and TPOT are generally ranked close to each other". McElfresh: "for a surprisingly high number of datasets, either the performance difference between GBDTs and NNs is negligible, or light hyperparameter tuning on a GBDT is more important than choosing between NNs and GBDTs". TabArena: "a group of not statistically significantly different top models".

## 3. Figure types and how they look

**Critical difference diagram** (Demšar Fig. 1; AMLB Fig. 2; TabArena Fig. A.12; TabRepo Fig. 4 bottom). "The top line in the diagram is the axis on which we plot the average ranks of methods. The axis is turned so that the lowest (best) ranks are to the right ... we connect the groups of algorithms that are not significantly different ... We also show the critical difference above the graph." One row of method labels fanning off a single rank axis; with 20+ methods the labels are split left and right. Produced with the `autorank` package in TabRepo and TabArena.

**Box plots of scaled scores per method** (AMLB Fig. 3): x = framework, y = scaled performance (random forest = 0, best = 1), y clipped to the useful range, "The number of outliers for each framework that are not shown in the plot are denoted on the x-axis." One panel per task type and budget.

**Jitter dots plus box per method** (TabM Fig. 2 and Fig. 3): "one dot on a jitter plot describes the performance score on one of the 46 datasets. The box plots describe the percentiles ... 25th, 50th, and 75th percentiles, and the whiskers describe the 10th and 90th percentiles. Outliers are clipped. The numbers at the bottom are the mean and standard deviations over the jitter plots." Figure 3 has three panels: left is mean rank ± std as one point with an error bar per model; middle and right are relative improvement over MLP with a zero reference line, separately for random and domain-aware splits. Reads well because each model is one column, baselines sit on the left, and the reference (MLP) is a horizontal line at 0.

**Grouped bars of relative improvement** (TabReD Fig. 1): x = technique family (ensembling, embeddings, retrieval, training recipes), y = average relative improvement over MLP in percent, two bars per family (TabReD vs an older benchmark). Four groups, two colours, eight bars. The message (two techniques transfer, two do not) is readable at a glance because per-dataset detail stays in Table 3.

**Leaderboard strip with CIs** (TabArena Fig. 1): one row per model, x = Elo, three markers per row for default / tuned / tuned + ensembled, 95% bootstrap CIs as horizontal bars, rows sorted by best Elo, random forest fixed at 1000 as the reference. Table A.1 duplicates it in numbers with "Elo (↑)", "Norm. score (↑)", "Avg. rank (↓)", "#wins (↑)", "Improvability (↓)", train and predict time per 1K rows.

**Per-dataset scatter A vs B** (TabPFN v2 Fig. 4b): "A per-dataset comparison of TabPFN with its strongest baseline, CatBoost. Each dot is the average score on one dataset", diagonal is the tie line. Two methods only; the reader counts dots above the diagonal.

**Relative loss per dataset against one reference** (AutoGluon-Tabular Fig. 3A): x = datasets, y = loss relative to AutoGluon on a log scale, AutoGluon is the horizontal line at 1, dots coloured by task type, "Failed runs are not shown in these plots". Fig. 3B: y = "Proportion of teams in each Kaggle competition whose scores were beat by each AutoML framework".

**Quality vs budget curves** (Grinsztajn Fig. 1 and 2): x = number of random-search iterations (log), y = normalized test score averaged across datasets, one line per model family, "Dotted lines correspond to the score of the default hyperparameters", "The ribbon corresponds to the minimum and maximum scores on these 15 shuffles." Auto-sklearn 2.0 and TabArena Fig. 5 right use the same shape with time on x.

**Pareto plots** (AMLB Fig. 7; TabRepo Fig. 4 top; TabArena Fig. 5 left; TabPFN Fig. 4c): x = inference or training time (log), y = scaled score or Elo, one marker per method, Pareto front traced. TabArena: "We report the median inference time per 1000 samples across all datasets."

**Performance profiles** (Agarwal Fig. 7): x = normalized score threshold τ, y = fraction of runs above τ, one curve per method with bootstrap bands; a curve higher everywhere dominates.

**Heatmap / rank table** (TabReD Table 5): methods × datasets with integer ranks from the significance test. Appendix material.

In all of these, per-dataset numbers go to a table (main text in TabReD and Gorishniy; appendix in TabArena, AMLB, TabM), and the main figure carries one aggregate per method.

## 4. Table conventions

- Bold best per column, with seed noise taken into account: TabReD "Bold entries represent the best methods on each dataset, with standard deviations over 15 seeds taken into account." Gorishniy 2021: "The metric values averaged over 15 random seeds are reported. See supplementary for standard deviations. For each dataset, top results are in bold."
- Metric direction in the header: TabReD "Classification (ROC AUC ↑)", "Regression (RMSE ↓)"; TabArena "Elo (↑)", "Avg. rank (↓)".
- Average-rank column with ± std across datasets, placed last (TabReD) or first after the name (McElfresh, who gives min/max/mean/median of rank).
- Gold/silver/bronze cell colours for top three (TabArena Table A.1); bold ranks for top-3 within each model class (TabReD).
- Counts next to averages: AutoGluon Table 2 columns "Wins, Losses, Failures, Champion, Avg. Rank, Avg. Rescaled Loss, Avg. Time (min)", with "Averages are computed over only the subset of datasets/folds where all methods ran successfully."
- Mean ± std over runs: Auto-sklearn 2.0 "report the mean and standard deviation over these repetitions"; FEDOT Table 7 "The standard deviation of the quality metrics ... is estimated for the 20 independent runs".

Caption lengths (word counts of the captions quoted above):
- AMLB Fig. 2 (CD plots): 31 words.
- AMLB Fig. 3 (box plots): 53 words.
- TabReD Table 3: 59 words.
- Grinsztajn Fig. 1: 70 words.
- TabM Fig. 3: about 115 words.
- AutoGluon Table 2: about 123 words.
- AutoGluon Table 5 (ablation): 17 words: "Ablation study of AutoGluon on the AutoML Benchmark (4h training time). Columns are defined as in Table 2."
Captions of 50-120 words that define the encoding (what a dot is, what 0 and 1 mean, how many seeds) are the norm; short captions appear only when the encoding was defined in an earlier caption.

## 5. Terminology and sentence patterns

Standard terms, as used in the sources: "time budget" / "training time limit" (AMLB, AutoGluon: "1h as well as 4h"); "anytime performance" and "optimization budget" (Auto-sklearn 2.0); "search space" (TabArena: "we curate a strong hyperparameter search space"); "pipeline" and "composite pipeline" (TPOT, FEDOT); "post-hoc ensembling", "weighted ensembling", "multi-layer stacking", "bagging" (AutoGluon, TabArena); "hyperparameter optimization (HPO)", "random search", "Optuna / TPE" (Gorishniy); "meta-learning" and "portfolio" (Auto-sklearn 2.0: "a set of complementary configurations that covers as many diverse datasets as possible"); "default", "tuned", "tuned + ensembled" (TabRepo, TabArena: "(D)", "(T)", "(T+E)"); "baseline" and "reference pipeline" (TabArena); "inference time per 1000 samples", "training time per 1K samples" (TabArena, McElfresh); "constant predictor" and "random forest" as the floor baselines (AMLB); "champion" (AutoGluon); "valid submission", "above median", "any medal" (MLE-bench); "success rate" with a threshold (MLAgentBench: "improve the performance metric ... by at least 10% over the baseline").

Reusable results sentences (verbatim from the sources):
1. "AUTOGLUON(B) and TPOT respectively achieve the best and worst rank among AutoML frameworks in almost every setting" (AMLB)
2. "AUTOGLUON(B) is generally not significantly better than the second best framework" (AMLB)
3. "Only AUTOGLUON(B) and LIGHTAUTOML achieve significantly better ranks across all settings." (AMLB)
4. "Even if ranks are similar, the performance distribution might be noticeably different." (AMLB)
5. "On over half of the datasets in each benchmark (23/39 for AutoML, 7/11 for Kaggle), AutoGluon performed better than all of the other frameworks combined." (AutoGluon)
6. "the high accuracy of AUTOGLUON(B) comes at the cost of extremely slow inference times" (AMLB)
7. "GBDT and MLP with embeddings (MLP-PLR) are the overall best models on the TabReD benchmark." (TabReD)
8. "FT-Transformer is a runner-up, however, it can be slower to train." (TabReD)
9. "SNN, DCNv2, ResNet and Trompt are no better than the MLP baseline." (TabReD)
10. "ResNet turns out to be an effective baseline that none of the competitors can consistently outperform." (Gorishniy 2021)
11. "There is still no universal solution among DL models and GBDT." (Gorishniy 2021)
12. "Tree-based models are superior for every random search budget, and the performance gap stays wide even after a large number of random search iterations." (Grinsztajn)
13. "nearly every algorithm ranks first on at least one dataset and last on at least one other" (McElfresh)
14. "the best out of all algorithms, CatBoost, only achieved an average rank of 5.06" (McElfresh)
15. "In 2.8 s, TabPFN outperforms an ensemble of the strongest baselines tuned for 4 h in a classification setting." (TabPFN v2)
16. "TabPFN surpasses CatBoost, the strongest default baseline, by 0.187 (0.939 compared with 0.752) in normalized ROC AUC." (TabPFN v2)
17. "Portfolio combined with ensembling outperforms AutoGluon for both accuracy and latency given the same 4h fitting budget" (TabRepo)
18. "No model is able to beat state-of-the-art AutoML systems even with tuning and ensembling" (TabRepo)
19. "there always exists a group of not statistically significantly different top models containing at least one deep learning model and GBDT" (TabArena)
20. "o1-preview significantly outperforms all other models, achieving a medal on 16.9% of competitions - almost twice the number of medals on average as the next best model." (MLE-bench)
21. "GPT-4o scores 8.7% given 24 hours to attempt each competition, but 11.8% when given 100 hours." (MLE-bench)
22. "The valid submission rate increased from 63.6% ± 4.5% to 92.4% ± 2.6%" (AIDE)
23. "Each feature removal decreases the LightAutoML rank, which shows that all those features make our framework more accurate" (LightAutoML)
24. "reducing the relative error by up to a factor of 4.5, and yielding a performance in 10 minutes that is substantially better than what Auto-sklearn 1.0 achieves within an hour" (Auto-sklearn 2.0)

Templates distilled from these: "X achieves the best average rank (r ± s) among the N methods"; "X outperforms Y on k of M datasets"; "X is within seed variance of Y on M − k datasets"; "the gap between X and Y is d points of normalized score (95% CI [a, b])"; "X is never significantly worse than Y"; "the gain of X comes at the cost of t× longer training".

## 6. Ablations and budget fairness

AutoGluon-Tabular, section "4.3 Ablation Studies": "we study the importance of AutoGluon's various components via ablation analysis. We run variants of AutoGluon with the following functionalities sequentially removed: First, we omit iterated repetitions of bagging ... (NoRepeat). Second, we omit our multi-layer stacking strategy ... (NoMultiStack). Third, we omit bagging ... (NoBag). Fourth, we omit our neural network ... (NoNetwork)." Table 5 keeps the same columns as the main table: Avg. Rank 1.93 → 2.12 → 2.85 → 3.91 → 4.19 and Avg. Rescaled Loss 0.166 → 0.220 → 0.524 → 0.720 → 0.817. Variants are named by the removed component, rows ordered from full system to most stripped. LightAutoML does the same with "No auto-typing", "No finetune", measured by average reciprocal rank. TabM calls the section "5 Analysis" with question-form headings such as "How does the performance of TabM depend on k?". AutoML-Agent and AIDE report ablations as success-rate changes; MLAgentBench reports "8 trials per task" and the "fraction of time" an agent crosses the threshold.

Budget fairness is stated once in the setup and once beside the headline claim. AMLB: frameworks "are instantiated with their default configuration, except that we control ... Runtime for the search ... Resource constraints ... Target metric", with the same instance type and "1 hour leeway for data loading, making predictions, and cleanup operations". AutoGluon: "All frameworks were run on the same type of EC2 cloud instance with an identical training time limit ... As some frameworks only loosely respected the specified time limits, we report actual training times as well." Grinsztajn: "This does not take into account that each random search iteration is generally slower for NNs than for tree-based models." TabPFN: "All methods were evaluated using 8 CPU cores. Moreover, TabPFN makes use of a 5-year-old consumer-grade GPU." MLE-bench fixes hardware and "24 hours to produce a submission", then shows the 100-hour variant separately. Failures are counted and shown (AutoGluon "Failures" column; AMLB imputation with the constant predictor and a failure figure; MLE-bench "Valid Submission (%)").

## 7. Recommendation for 3 systems × 8 tasks × 3 seeds among 20 published baselines, plus 2×2 ablation with 24 attempts per cell

**Statistics to report.**
1. Tie-aware ranks per task following TabM/TabReD: on each task, a system and a baseline tie when the mean difference is within the larger of the two seed standard deviations. This absorbs 3-seed noise and matches the TabReD protocol the baselines come from. Report "Average rank r ± s" over the 8 tasks, exactly as TabReD Table 3 does.
2. One magnitude metric alongside rank: relative improvement over a fixed reference (TabM formula, with RMSE converted to R² for regression) or AMLB-style scaled score with the reference at 0 and the best published baseline at 1. State the formula in one sentence.
3. Pairwise claims between the three systems: win counts "k of 8 tasks", exact Wilcoxon signed-rank on the 8 task means, and a stratified bootstrap (resample tasks, then seeds within task, 10 000 draws) for the CI of the mean rank or mean scaled score. State up front that with N = 8 a Friedman/Nemenyi CD spans about 12 rank positions and is therefore omitted. If a probability statement is wanted, add the Bayesian signed-rank test with a ROPE and write "with probability p system A is practically better than B".
4. For the ablation: success proportions per cell out of 24 with Wilson 95% intervals, differences between cells with their CIs, Fisher's exact test for the two main effects, and a separate quality metric computed on successful attempts only, stated as such. Table rows named by the removed component, ordered full → stripped, same columns as the main table (AutoGluon Table 5 pattern).

**Figure 1 (main): rank strip, one row per method.** 23 rows sorted by mean rank, best at top. x = tie-aware rank, 1 at the left. Baselines: label in grey, mean rank as a grey dot, ±1 std across tasks as a thin grey line, per-task ranks as small grey ticks on the same line. The three systems: coloured filled markers (three hues), heavier line for the ±std, their per-task ranks as small coloured ticks, label in the same colour. Two thin vertical dashed lines mark the mean rank of the best GBDT and the best DL baseline, labelled at the top. No legend beyond the three system names; the caption defines the encoding in about 60 words. The flicker in the current dot plot comes from 8 × 23 equal markers; the strip keeps the 8 per-task values as ticks subordinate to one dot and one bar per row. A split version with two panels (classification tasks, regression tasks) is optional.

**Figure 2: gain over the reference per task.** Three panels side by side (one per system) or one panel with three columns. y = relative improvement over the reference baseline in percent, x = 8 task labels, one dot per task, a short vertical bar for the 3-seed range, a horizontal line at 0 for the reference, a dashed line at the best published baseline's improvement on that task. Per-task numbers go to the appendix table with means, ± std over seeds, bold best per column, ↑↓ in headers. This panel is the TabM Figure 3 middle panel reduced to 8 tasks; with 8 points per column a jitter plot works and a box plot does not.

**Figure 3: ablation 2×2.** A dot-and-interval plot: four cells on x, success rate out of 24 on y with Wilson 95% intervals, the two factor levels encoded by marker fill and position, and the quality of successful runs as a second small panel beside it. The numbers appear in a table with the AutoGluon Table 5 layout. A Pareto panel (quality vs wall-clock or token cost, one marker per system, log x) belongs in the main text only if cost is a claim of the paper; otherwise in the appendix with AMLB Figure 7 as the model.

**Wording.** Follow the AMLB/TabReD sentence shapes: "System A achieves the best average rank among the three systems (r ± s) and places between CatBoost and MLP-PLR among the published baselines", "A outperforms B on 6 of 8 tasks; the two are within seed variance on the remaining 2", "no pair of systems differs at α = 0.05 under the exact Wilcoxon test, which with 8 tasks requires a clean sweep". Claims about cost: "A reaches this rank at t minutes per task, B at 3× that budget".

## 8. Caveats

- Benavoli 2016 shows that a Nemenyi outcome for a pair depends on which other methods are in the pool; with 20 published baselines in the pool, pairwise claims between the three systems should rest on pairwise tests only.
- TabReD baselines were tuned with 100 Optuna iterations and 15 seeds; any comparison with 3 seeds should say so beside the table and use the tie rule, as above.
- Mean rank across 8 tasks is itself a noisy statistic; TabReD prints ± 1.5 to 2.8 next to ranks of 2 to 9. The paper should present rank spreads of that size as expected, and avoid ordering claims between methods whose spreads overlap.

## 9. Sources consulted

Opened in full text (arXiv HTML, ar5iv, PMC, or PDF via pdftotext):
1. Gijsbers et al., AMLB: an AutoML Benchmark, JMLR 2024, arXiv 2207.12560.
2. Erickson et al., AutoGluon-Tabular, 2020, arXiv 2003.06505.
3. Salinas & Erickson, TabRepo, 2024, arXiv 2311.02971.
4. Erickson et al., TabArena, 2025, arXiv 2506.16791 (incl. A.1, A.5, D.1).
5. Feurer et al., Auto-sklearn 2.0, JMLR 2022, arXiv 2007.04074.
6. Rubachev et al., TabReD, ICLR 2025, arXiv 2406.19380 (incl. Table 3, Fig. 1, C.2, Table 5).
7. Gorishniy et al., Revisiting Deep Learning Models for Tabular Data, 2021, arXiv 2106.11959.
8. Gorishniy et al., TabM, ICLR 2025, arXiv 2410.24210.
9. Grinsztajn et al., Why do tree-based models still outperform deep learning on tabular data, 2022, arXiv 2207.08815.
10. McElfresh et al., When do neural nets outperform boosted trees, 2023, arXiv 2305.02997.
11. Hollmann et al., TabPFN v2, Nature 2025 (PMC11711098; nature.com redirected to a login page).
12. Nikitin et al., FEDOT, FGCS 2022, arXiv 2106.15397.
13. Vakhrushev et al., LightAutoML, 2021, arXiv 2109.01528.
14. Olson et al., TPOT, 2016, arXiv 1603.06212.
15. Demšar, Statistical comparisons of classifiers over multiple data sets, JMLR 2006 (PDF).
16. Benavoli, Corani, Mangili, Should we really use post-hoc tests based on mean-ranks?, JMLR 2016, arXiv 1505.02288 (abstract page only).
17. Benavoli et al., Time for a change, JMLR 2017, arXiv 1606.04316.
18. Agarwal et al., Deep RL at the edge of the statistical precipice, NeurIPS 2021, arXiv 2108.13264.
19. Chan et al., MLE-bench, 2024, arXiv 2410.07095.
20. Jiang et al., AIDE, 2025, arXiv 2502.13138.
21. Huang et al., MLAgentBench, 2023, arXiv 2310.03302.
22. Trirat et al., AutoML-Agent, 2024, arXiv 2410.02958.
23. H2O AutoML documentation (docs.h2o.ai, automl page) for terminology.

Could not open: LeDell & Poirier 2020, H2O AutoML paper (automl.org PDF returned 404); the H2O docs page was used for terminology only. Nature's own page for TabPFN v2 redirected to a login; the PMC copy was used.
