# Evaluation methodology for LLM-generated email summaries and drafts

**Wayfinder research ticket:** [#83](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/83) (part of map [#80](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/80))
**Status:** evidence only. This note deliberately makes **no recommendation** and does **not** select a metric set, a dataset, or an evaluation design. Those belong to a decision ticket.
**Research date / access date for every URL below: 5 August 2026.**

---

## 1. Question

What is a defensible way to evaluate LLM-generated email summaries and drafts in 2026, and what benchmark email data can this project legally and ethically use?

Sub-questions from the ticket:

1. **Metric validity** — the state of the argument on ROUGE/BERTScore for LLM-generated summaries. What do they measure, and where do they mislead?
2. **Alternatives** — LLM-as-judge and reference-free approaches (G-Eval and successors): mechanism, known biases, and whether their use is defensible in a project that must also *report* its method.
3. **Hallucination measurement** — how faithfulness against a source document is measured, and what a small team can realistically implement. NFR-02 requires a *measurable* reduction, which presupposes a measurement.
4. **Human evaluation** — what a structured rubric for "contextually appropriate" looks like, and what inter-rater reliability is expected. NFR-02/FR-03 requires ≥90% of drafts rated appropriate.
5. **Benchmark corpora** — what email datasets exist, their licensing, and their PII implications given NFR-01 forbids real PII.

**Constraints that shape what "defensible" means here.** Four part-time undergraduates, roughly five weeks to a demonstrable system, no budget, and NFR-01's prohibition on processing real personal data. An evaluation design that is methodologically ideal but unimplementable is not useful, so implementation cost and hardware requirements are reported alongside every option.

---

## 2. Summary of findings

### 2.1 NFR-02's committed thresholds are not defensible as written

Four independent reasons, each separately sufficient:

1. **The numbers are underspecified, therefore untestable.** "ROUGE-L" is ambiguous between `rougeL` and `rougeLsum`, which are different computations, and the reference Python implementation cannot reproduce the original Perl script's stopword removal [3]. "BERTScore F1 ≥ 0.85" is meaningless without naming the model, layer, library version hash and rescaling: the maintainers' own documentation states raw scores with RoBERTa-large "often [are] between 0.85 and 0.95" [5]. **0.85 is approximately the floor of the raw scale, not a quality bar.** On WMT18 the mean raw score of 0.9311 became 0.5758 after their baseline rescaling [5].
2. **The ROUGE-L threshold exceeds published state of the art in this exact task.** On EmailSum — the only human-annotated abstractive *email thread* summarisation benchmark located — the best system reaches ROUGE-L **28.76** (short summaries) and **31.38** (long) [7]. 0.40 is not a stretch target; it is above what anyone has published on email threads.
3. **The metrics do not track quality for LLM-generated text.** Goyal, Li & Durrett found GPT-3 summaries scored ~7 ROUGE-L points *below* fine-tuned models while humans overwhelmingly preferred them, and concluded reference-based and reference-free metrics "cannot reliably evaluate GPT-3 summaries" [1]. The team's own literature review already cites this paper; the contradiction the ticket identifies is real.
4. **It is worse in this domain than in news.** EmailSum's authors report the best correlation between any automatic metric and human overall-quality ranking was Pearson **r = 0.14, p = 0.16** for short summaries, with "little or negative correlation" for long ones, and conclude ROUGE and BERTScore "are poorly correlated with human judgment" on email thread summarisation [7]. Dai, Karimi & Fang separately show summarisation metrics are meta-evaluated almost exclusively on news data, so validity does not transfer by default [10].

None of this makes the metrics useless. Deutsch, Dror & Roth's position — that such metrics belong as **diagnostics** rather than as targets to maximise — is the mainstream restatement [8].

### 2.2 Alternatives exist, are citable, and are biased in documented ways

LLM-as-judge is the dominant 2023–2026 alternative. G-Eval reports Spearman ρ = 0.514 with human judgment on SummEval against ROUGE-L's 0.165 [15]. But every primary source that studies it reports biases: position bias (a weaker model was made to "win" 82.5% of comparisons purely by reordering [17]), self-preference stated by G-Eval's own authors ("G-Eval-4 always gives higher scores to GPT-3.5 summaries than human-written summaries, even when human judges prefer human-written summaries" [15]), verbosity bias, score-distribution skew, dimension collapse, and low consistency across runs [19, 28]. Two 2025–2026 papers now function as reporting checklists [30, 31], and multiple sources converge on one requirement: **an LLM judge must be validated against a human-labelled subset before its numbers are reported** [21, 27, 30]. Open-weight judges (Prometheus 2, Apache-2.0) remove the API cost but sit ~0.12 Pearson below the human–human ceiling [22].

### 2.3 Hallucination measurement is cheap and available; its reliability on modern output is not established

Two CPU-runnable open-weight faithfulness classifiers put automatic scoring within reach of a laptop and a zero budget: Vectara HHEM-2.1-Open (~0.1B params, <600MB RAM, Apache-2.0, no GPU) [48] and MiniCheck-Flan-T5-Large (770M, reported 74.7% balanced accuracy vs GPT-4's 75.3% at ~400× lower cost) [44]. The counter-evidence is equally clear: on FaithBench, built from *modern LLM* summaries where detectors disagree, HHEM-2.1 scores 55.68% and GPT-4o 56.29% balanced accuracy — near chance [52]. Published mitigation studies use small paired before/after designs (56–500 items) and mostly do **not** report significance tests [53, 54], so a paired design with McNemar plus bootstrap confidence intervals would put a student project above median published practice [9, 57].

### 2.4 Human evaluation: the template exists, and the ≥90% threshold has a power problem

SummEval is the canonical rubric: four defined dimensions (coherence, consistency, fluency, relevance) on 1–5 Likert scales, 3 experts + 5 crowd workers per summary, order randomised [6]. Its most transferable finding is the cheapest known intervention: a targeted **second adjudication round** raised expert Krippendorff's α from **0.4132 to 0.7127** [6]. Expected agreement in this field is low — surveyed NLG papers report agreement "in most cases … 0.3 to 0.5" [61] — and Artstein & Poesio warn against treating any single cutoff as a gate [72]. A skewed binary "appropriate / not appropriate" judgment is specifically hazardous: the kappa paradox means near-total agreement can still yield a low κ [72, 73, 74].

On the ≥90% figure itself: this is a binomial proportion, and its confidence interval at realistic sample sizes is wide. Using the Wilson interval [58], 46/50 drafts rated appropriate (92%) gives a 95% CI of **[0.812, 0.968]** — the data cannot distinguish a 90% system from an 82% one. A 95% *lower bound* above 0.90 requires **n ≥ 35 at a perfect 100% score**, or **n ≈ 140 at a 95% observed rate**. Card et al. separately show the modal NLP design (3 raters × 100 items) is underpowered for effects below 0.2 on a [0,1] scale [59].

### 2.5 Data: what actually exists

- **Enron has no licence, no consent, and verified live PII surviving professional cleansing.** The CMU distribution page states no terms of use at all, only a request to "be sensitive to the privacy of the people involved" [81]. EDRM/Nuix's 2013 forensic pass found 60 items with credit card numbers, 572 with Social Security or national identity numbers, 292 with dates of birth, and 532 with medical or legal matters [82]. Noever then identified "nearly 50,000 additional items that might qualify as PII" in **both** the original 2003 and the cleansed 2016 corpus [83]. "Use the cleaned version" does not solve the problem.
- **Every high-quality email-thread summarisation benchmark is Enron- or Avocado-derived.** AESLC is free and ungated but inherits Enron's PII with zero mitigation [93]. EmailSum is well-anonymised but its email text is licence-gated behind LDC's Avocado agreements [7, 95]. BC3 — the closest thing to a purpose-built email summarisation benchmark — is un-anonymised W3C mail with real names and addresses [97].
- **The clean options are proxies or self-generated.** SAMSum's dialogues were "created and written down by linguists fluent in English", so the corpus "does not contain any sensitive data" — verified verbatim from the paper [99]; its licence is CC BY-NC-**ND** 4.0 and its official Samsung/ELRA channels now 401 [99]. DialogSum is CC BY-NC-SA 4.0 from ESL teaching material [100]. Synthetic email generated from CC BY 4.0 persona sets [105] is contamination-free by construction but measurably easier and less lexically diverse than human-authored data [107, 110].

### 2.6 One cross-cutting constraint to know before designing anything

The Gemini API terms (effective 23 March 2026) state that for the **unpaid** tier, "Google uses the content you submit to the Services and any generated responses to provide, improve, and develop Google products and services", that "human reviewers may read, annotate, and process your API input and output", and instruct: "**Do not submit sensitive, confidential, or personal information to the Unpaid Services**" [116]. The pricing page confirms free-tier content is used to improve Google products, unlike the paid tier [117]. This binds any pipeline that routes benchmark email through a free-tier API — Enron content included.

---

## 3. Metric validity — the ROUGE/BERTScore question, answered on evidence

### 3.1 What the metrics actually measure

**ROUGE** (Lin, 2004 [2]) is a family of n-gram and longest-common-subsequence overlap statistics between a candidate summary and one or more human reference summaries. It measures *lexical overlap with a specific reference*, nothing else, and was introduced in the DUC-era extractive news summarisation setting.

Two implementation facts matter for any threshold written into a requirement [3]:

- `rougeL` computes LCS over the whole text ignoring newlines; `rougeLsum` treats newlines as sentence boundaries and computes LCS per sentence pair. These give different numbers for the same text. A requirement saying "ROUGE-L" without saying which is not testable as written.
- Google Research's `rouge-score` (Apache-2.0, the de-facto Python implementation) states it is "designed to replicate results from the original perl package" but "not all options provided by the original perl ROUGE script are supported", and specifically omits stopword removal: "we are unable to replicate this functionality precisely we do not include stopword removal". Scores are implementation-dependent.

**BERTScore** (Zhang, Kishore, Wu, Weinberger & Artzi, ICLR 2020 [4]) computes token-level cosine similarity between contextual embeddings of candidate and reference, greedily matched, reported as precision/recall/F1. It was validated on **363 machine translation and image captioning systems** — not on summarisation, and not on faithfulness.

The official BERTScore repository documents the interpretability problem directly [5]:

- "BERTScore computed with the large RoBERTa model often is between 0.85 and 0.95."
- Baseline rescaling (`--rescale_with_baseline`) subtracts an empirical floor computed by scoring ~500,000 *randomly paired* sentences from a large monolingual corpus: `X̂ = (X − Base) / (1 − Base)`. On WMT18 this moved the mean from **0.9311 to 0.5758**.
- Rescaling "does not affect BERTScore's correlation with human judgment, as measured by Pearson's r and Kendall's τ coefficients" — it changes the readable range only.
- The README instructs users to "Report the hash code … in your paper so that people know what setting you use", and warns "Changes in huggingface's transformers version may also affect the score."

**Consequence for NFR-02.** An unqualified "BERTScore F1 ≥ 0.85" sits at or below the floor of the raw RoBERTa-large scale — a threshold that near-any fluent text pair clears — and becomes a completely different, much harder target under rescaling. The threshold is not well-defined until model, layer, version hash and rescaling are pinned.

### 3.2 The evidence that overlap metrics mislead on LLM output

**Goyal, Li & Durrett (2023) [1]** — the paper the team already cites. Reported scores:

| Model | CNN/DM R-1 / R-2 / R-L | XSum R-1 / R-2 / R-L |
|---|---|---|
| BRIO (fine-tuned) | 38.49 / 17.08 / 31.44 | 49.66 / 25.97 / 41.04 |
| T0 | 35.06 / 13.84 / 28.46 | 44.20 / 20.72 / 35.84 |
| GPT-3 (`text-davinci-002`) | 31.86 / 11.31 / 24.71 | 28.78 / 7.64 / 20.60 |

The paper's own summary: GPT-3 summaries "score much lower on automatic metrics (7 ROUGE-L points on average) than all prior state-of-the-art models while comfortably outperforming them on human evaluation." Human study: 100 articles per dataset, 3 annotators each, 60 unique annotators per dataset. Conclusions: reference-based metrics "cannot reliably evaluate GPT-3 summaries", and none of the reference-free metrics tested "follow these trends for both CNN/DM and XSum datasets."

**SummEval (Fabbri, Kryściński, McCann, Xiong, Socher & Radev, TACL 2021) [6]** provides the correlation numbers. System-level Kendall's τ against *expert* annotations, 11 references per example, 100 CNN/DM articles, 12,800 annotations:

| Metric | Coherence | Consistency | Fluency | Relevance |
|---|---|---|---|---|
| ROUGE-1 | 0.2500 | 0.5294 | 0.5240 | 0.4118 |
| ROUGE-2 | 0.1618 | 0.5882 | 0.4797 | 0.2941 |
| **ROUGE-L** | **0.0735** | **0.1471** | **0.2583** | **0.2353** |
| BERTScore-P | 0.0588 | −0.1912 | 0.0074 | 0.1618 |
| BERTScore-R | 0.1471 | 0.6618 | 0.4945 | 0.3088 |
| BERTScore-F | 0.2059 | 0.0441 | 0.2435 | 0.4265 |
| MoverScore | 0.1912 | −0.0294 | 0.2583 | 0.2941 |

Two observations. **ROUGE-L is the weakest ROUGE variant on every dimension** — the specific variant NFR-02 names. And this is *pre-LLM* data: fine-tuned neural summarisers, not GPT-class models. Also from SummEval: group-averaged expert and crowd ratings correlated "close to 0", and crowd ratings were near-uniform across the four dimensions.

**Maynez, Narayan, Bohnet & McDonald (ACL 2020) [36]** give the faithfulness-specific correlations on XSum: entailment **0.431** vs ROUGE-1 0.197, ROUGE-2 0.162, ROUGE-L 0.162, BERTScore 0.190. Overlap metrics are close to useless as faithfulness proxies.

### 3.3 The domain-transfer problem — the strongest single piece of evidence

**EmailSum (Zhang, Celikyilmaz, Gao & Bansal, ACL-IJCNLP 2021) [7]** is the only human-annotated abstractive **email thread** summarisation benchmark located. Its abstract states the finding directly:

> "we find that widely used automatic evaluation metrics (ROUGE, BERTScore) are weakly correlated with human judgments on this email thread summarization task. Hence, we emphasize the importance of human evaluation and the development of better metrics by the community."

Numbers from the paper: the best correlation was ROUGE-1 vs human overall quality ranking for short summaries, **coefficient 0.14, p = 0.16** (not significant); for long summaries "there is little or negative correlation between metrics and human judgment." Best reported system scores: ROUGE-1/2/L **36.98 / 11.21 / 28.76** (short) and **44.56 / 14.61 / 31.38** (long).

**Dai, Karimi & Fang (Findings of EMNLP 2024) [10]** generalise the point: summarisation metrics "are primarily meta-evaluated on datasets consisting of examples from news summarisation datasets", and they call for diverse benchmarks to test generalisation and for "user-centric quality dimensions that consider the generated summary's communicative goal and the role of summarisation in the workflow." Metric validity established on CNN/DailyMail does not automatically transfer to threaded workplace email.

**DIAL-SUMMER (Ramnath et al., 2026) [14]** extends this to dialogue summaries with a hierarchical error taxonomy (dialogue-level vs within-turn-level), and finds turns in the middle of a dialogue are most frequently missed while extrinsic hallucinations cluster at summary endings — an error profile with no analogue in single-document news summarisation.

### 3.4 The reference-free counter-argument

**Deutsch, Dror & Roth (EMNLP 2022) [8]** argue reference-free metrics are structurally biased: they are "equivalent to using one generation model to evaluate another", so (1) they can be optimised at test time, (2) they are "inherently biased toward models which are more similar to their own", and (3) they "can be biased against higher-quality outputs, including those written by humans." Their recommendation: reference-free metrics "should be used as diagnostic tools for analyzing and understanding model behavior instead of measures of how well models perform a task, in which the goal is to achieve as high of a score as possible."

**Deutsch, Dror & Roth (TACL 2021) [9]** add the statistical dimension: confidence intervals on metric correlations "are rather wide, demonstrating high uncertainty in the reliability of automatic metrics", and most metrics show **no statistically significant improvement over ROUGE**. A small observed gap between two systems on any of these metrics may well be inside the noise.

### 3.5 Recent (2024–2026) work on the same question

- **van Schaik & Pugh (SIGIR 2024) [11]** — a practitioner-facing survey of offline, system-level evaluation of LLM-generated text, with strategies for avoiding common pitfalls.
- **Nguyen, Chen, Pobbathi & Ding (2024) [12]** compare eight automatic metrics, human evaluation and an LLM-based method on patent summarisation, reporting that "LLMs evaluation aligns closely with human evaluation, while widely-used automatic metrics such as ROUGE-2, BERTScore, and SummaC do not and also lack consistency."
- **Liu, Brahma & Henao (2026) [13]** address the calibration problem for model-based metrics — "predicted scores are frequently miscalibrated, limiting their reliability" — proposing proxy scores requiring neither reference summaries nor human annotations, plus group isotonic regression binning.
- **Unell et al. (2026) [35]** address the inverse problem: how to validate an LLM judge against human raters with the fewest human annotations, reporting a 32.5% reduction in required annotations over random subset selection.

---

## 4. Alternatives and their biases

### 4.1 G-Eval and the LLM-as-judge mechanism

**G-Eval (Liu, Iter, Xu, Wang, Xu & Zhu, EMNLP 2023) [15]** has three components:

1. A **prompt** containing the task description plus an explicit evaluation criterion (e.g. "Coherence (1-5) — the collective quality of all sentences …").
2. **Auto chain-of-thought** — the LLM generates its own "Evaluation Steps" from the criterion; these are pasted back into the evaluation prompt.
3. **Form-filling with probability-weighted scoring** — the model outputs only a score, and the metric is `score = Σ p(sᵢ) × sᵢ` over the discrete score set. Motivation: "one digit usually dominates the distribution of the scores, such as 3 for a 1-5 scale", producing ties and low variance.

Reported SummEval summary-level correlations: G-Eval-4 average Spearman **ρ = 0.514**, Kendall **τ = 0.418** (coherence 0.582, consistency 0.507, fluency 0.506, relevance 0.547); G-Eval-3.5 ρ = 0.401. Baselines in the same table: ROUGE-1 0.192, ROUGE-2 0.205, **ROUGE-L 0.165**, BERTScore 0.225, MoverScore 0.191, BARTScore 0.385, UniEval 0.474, GPTScore 0.417. On QAGS: G-Eval-4 r = 0.599, ρ = 0.611, τ = 0.525.

Disclosed settings, which model good reporting practice: `text-davinci-003` at temperature 0; GPT-4 sampled `n=20, temperature=1, top_p=1` to estimate token probabilities; full prompts in Appendix A. Their Limitation #2 names API cost and model-version drift as reproducibility threats.

### 4.2 Known biases, with magnitudes

| Bias | Primary evidence |
|---|---|
| **Self-preference** | G-Eval §4: "G-Eval-4 always gives higher scores to GPT-3.5 summaries than human-written summaries, even when human judges prefer human-written summaries" [15]. Panickssery, Bowman & Feng: GPT-4 recognises its own summaries at ~73.5% pairwise accuracy, and self-recognition capability correlates linearly with self-preference strength; fine-tuning on ~500 examples pushes GPT-3.5/Llama-2 self-recognition past 90% with self-preference rising alongside [18]. |
| **The bias is really about perplexity, not identity** | Wataoka, Takahashi & Ri: LLMs "assign significantly higher evaluations to outputs with lower perplexity than human evaluators, **regardless of whether the outputs were self-generated**" — the bias "exists because LLMs prefer texts more familiar to them" [112]. Using a different vendor's model as judge does not break the loop. |
| **Position bias** | Zheng et al.: consistency under swapping candidate order was GPT-4 65.0%, GPT-3.5 46.2%, Claude-v1 23.8% [16]. Wang et al.: Vicuna-13B was made to beat ChatGPT on **66 of 80 queries (82.5%)** purely by exploiting ordering [17]. |
| **Verbosity bias** | Zheng et al.: on a padded "repetitive list" attack, GPT-3.5 and Claude-v1 failed 91.3% of the time (GPT-4 8.7%) [16]. Norman et al. measured verbosity bias as minimal (<0.011) under their rubric — the effect is protocol-dependent [29]. |
| **Score-distribution skew** | Stureborg, Alikaniotis & Suhara: on a 1–100 scale the judge "assigns outsized probabilities to certain scores such as 90 and 95"; scores concentrate in 70–100 with 1–60 "almost entirely ignored" [19]. |
| **Familiarity bias** | Same paper: GPT-4 shows "disproportionate bias towards low perplexity summaries" (mean perplexity 5.34–6.06 for its high ratings vs 6.26–6.43 for human experts') [19]. |
| **Dimension collapse** | Same paper: asked for several attributes at once, human between-attribute Pearson r = 0.315 vs **GPT-4 r = 0.979** — the judge merges distinct dimensions into one number [19]. |
| **Low self-consistency** | Same paper: GPT-4 inter-sample Krippendorff's α = **0.587** against human inter-annotator α = 0.659 [19]. Haldar & Hockenmaier report low intra-rater reliability across runs — "inconsistent, almost arbitrary in the worst case" [28]. |
| **Prompt sensitivity** | Removing the source document from the prompt dropped performance 26.7% overall, 44.6% on relevance [19]. |
| **Agreement statistics overstate the judge** | Thakur et al.: "high percent agreement masks substantial score differences"; assigned scores can differ from human scores by up to 5 points [26]. Norman et al.: **Cohen's κ falls 33–41 percentage points below exact-match accuracy** on MT-Bench; judge rankings shifted by up to 14 positions across benchmarks; two production judges showed test-retest reliability >0.95 *while* showing severe position bias [29]. |

### 4.3 The case in favour, and mitigations that were measured

- **Zheng et al. (NeurIPS 2023 Datasets & Benchmarks) [16]**: GPT-4 achieves "over 80% agreement with human preferences — the same level of agreement between humans" (MT-Bench pairwise 85% vs a human–human baseline of 81%; Chatbot Arena 87% vs 87%). When GPT-4 and a human disagreed, 75% of humans still judged GPT-4's explanation reasonable and 34% changed their own choice. Measured mitigations: three in-context examples lifted GPT-4 position-bias consistency from **65.0% → 77.5%**; on maths grading, GPT-4 failure rate went **70% → 30% (CoT) → 15% (reference-guided)**. Position swapping — run both orders, call disagreement a tie — is their standard fix.
- **Chiang & Lee (ACL 2023) [20]**: the minimal reproducible design — give the LLM *the exact same instructions, samples and rating questions given to human experts*, then compare the two rating sets. "The texts rated higher by human experts are also rated higher by the LLMs", robust to instruction rephrasing and to sampling algorithm.
- **Bavaresco et al., JUDGE-BENCH (ACL 2025) [21]**: 20 datasets with human annotations, 11 LLMs. "Our evaluations show substantial variance across models and datasets. Models are reliable evaluators on some tasks, but overall display substantial variability depending on the property being evaluated, the expertise level of the human judges, and whether the language is human or model-generated." Prescription: "**LLMs should be carefully validated against human judgments before being used as evaluators.**"
- **Prometheus 2 (Kim et al., EMNLP 2024) [22]** — the no-budget judge. `prometheus-7b-v2.0` and `prometheus-2-8x7b-v2.0`, both **Apache-2.0**, weights on Hugging Face, supporting direct assessment (1–5 against a user-supplied rubric) and pairwise ranking. Pearson vs human on FLASK: 8x7B **0.555**, 7B 0.545, against a **human–human ceiling of 0.679**. Pairwise accuracy (8x7B): HHH Alignment 85.52%, MT-Bench Human Judgment 71.96%, Auto-J Eval 79.98%. Caveat on the model card: the Preference Collection training data is subject to OpenAI's Terms of Use for generated data.
- **Panel of LLM evaluators (Verga et al., preprint) [23]**: a three-model panel from disjoint families (Command R 35B, Claude 3 Haiku, GPT-3.5) beat a single GPT-4 judge on human agreement (KILT Cohen's κ 0.763 / 0.906 / 0.867 vs GPT-4's 0.627 / 0.841 / 0.830; Chatbot Arena Hard Pearson 0.917 vs 0.817) at **seven to eight times lower cost**, with the smallest self-bias standard deviation (2.2) of any configuration tested.
- **LLM-Rubric (Hashemi, Eisner, Rosset, Van Durme & Kedzie, ACL 2024) [24]**: a manually constructed 9-question rubric; the LLM answers each question as a distribution; a **small feed-forward network with judge-specific and judge-independent parameters** is trained to predict each individual human judge's ratings. RMS error < 0.5 on a 1–4 satisfaction scale, 2× better than the uncalibrated baseline. This is the "calibrate the judge to your own raters" pattern.
- **FineSurE (Song, Su, Shalyminov, Cai & Mansour, ACL 2024) [25]**: decomposes summarisation evaluation into two LLM sub-tasks — sentence-level **fact checking** and **keyfact alignment** — producing per-sentence hallucination counts plus completeness and conciseness rather than one Likert number. Motivation stated in the abstract: "Traditional methods like ROUGE do not correlate well with human judgment, while recently proposed LLM-based metrics provide only summary-level assessment using Likert-scale scores."
- **Calderon, Reichart & Dror, the alt-test (ACL 2025) [27]**: a statistical procedure deciding, from "only a modest subset of annotated examples", whether an LLM judge is justified as a replacement for human annotators, with an interpretable winning-rate measure.
- **Gu et al. [33]** and **Li et al.** provide maintained surveys of the area; Gu et al. is at v6 (October 2025) with an accompanying project page.

### 4.4 Reporting an LLM-judge method — the assessed-report requirement

No single universally adopted standard exists. Two sources function as checklists.

**Dietz et al., "Principles and Guidelines for the Use of LLM Judges" (ICTIR 2025) [30]** answers the exact question the team faces — "Can I use LLM judgments in my next research paper?" — with: "**Yes**, if the focus is on improving runtime efficiency. **It depends**, if the goal is to improve result quality." Their three conditions:

1. The LLM-based metrics "should have been **recently validated against human or user judgments**, and used in combination with diverse, complementary metrics to reduce the risk of overfitting or bias."
2. The setup "must ensure that LLM-based judgments **are not influencing system development in a way that introduces circularity or test signal leakage**; such risks should be demonstrably mitigated."
3. "**Known failure modes and evaluation tropes** … should be acknowledged, quantified, and addressed through appropriate guardrails."

They enumerate 14 named "evaluation tropes", each with a *quantify* and a *guardrail* paragraph. Directly relevant here: **#3 LLM Narcissism** (guardrail: reserve a judge model family not used by any system under test); **#1 Circularity** and **#2 LLM Evaluator as a Ranker**; **#7 LLM Evolution** — "LLM providers may seamlessly retire older versions or update models without notice … This makes it difficult — or even impossible — to reproduce prior evaluation findings using the same version of the evaluator"; **#12 Rubber-Stamp Effect** (human verifiers conform to LLM labels, an Asch-conformity effect, so the human validation subset must be designed to avoid anchoring); **#5 Ignored Label Correlation** — agreement "should be assessed directly at the label level", citing a case where system-level Spearman ρ = 1 coexisted with per-label agreement ranging 0.12–0.61. Concrete circularity evidence: reusing one LLM evaluator both to rerank and to evaluate dropped Kendall's τ against manual judgments from **0.84 → 0.63** (top-60 systems) and 0.44 (top-20), with human and LLM evaluators disagreeing on 18% of system pairs.

**Rao & Callison-Burch (2026) [31]** give an 11-item reporting checklist: state the judgment scale before the metric; report at most one of Pearson / Spearman / Kendall τb / φ / MCC on binary data (they prove these are **the same statistic** for binary verdicts on non-degenerate cases); report the 2×2 confusion matrix and N; state the handling rule for ties, abstentions and invalid outputs; report abstention/tie/invalid/coverage rates; state the aggregation level and resampling unit. Motivating evidence: **the same model's reported accuracy ranged 0.534 → 0.874 purely from handling-rule choices, with no verdict changed**; on a rubric benchmark, four protocol choices moved accuracy 0.551 → 0.899 and moved κ across zero. Their coding of 24 recent LLM-judge papers found these protocol choices are usually left implicit.

**An open disagreement in the literature.** Stureborg et al. recommend temperature 0, no CoT, a 1–10 scale, one output per attribute [19]; Yamauchi, Yano & Oyamada find **non-deterministic sampling improves alignment with human preferences over greedy decoding** and that CoT adds little once criteria are explicit [32]. These are not reconciled.

### 4.5 Tooling, licence and cost

| Tool | Licence | Paid API required? | LLM-judge support |
|---|---|---|---|
| **DeepEval** (Confident AI) [34] | Apache-2.0 | No — metrics run locally; a custom model can be substituted | Ships a G-Eval implementation, plus DAG, Answer Relevancy, Faithfulness, Contextual Precision/Recall, Hallucination, Summarization, Bias, Toxicity. Confident AI is a separate, optional paid platform |
| **RAGAS** [47] | Apache-2.0 | No, but the quickstart defaults to OpenAI GPT-4o; `llm_factory` swaps providers | Reference-free RAG metrics (Faithfulness, Response Relevancy, Context Precision/Recall, Noise Sensitivity), plus Aspect Critic and Rubrics-Based Scoring |
| **OpenAI Evals** [34] | MIT | **Yes** — requires `OPENAI_API_KEY`; the repo warns about running costs | Model-graded evals via custom YAML |
| **Hugging Face `evaluate`** [34] | Apache-2.0 | No | **No native LLM-as-judge**; the docs redirect to LightEval for LLM evaluation |
| **Prometheus 2 weights** [22] | Apache-2.0 | No | Local open-weight judge, 7B and 8x7B |

---

## 5. Hallucination / faithfulness measurement

### 5.1 The taxonomy and the baseline problem

**Maynez, Narayan, Bohnet & McDonald (ACL 2020) [36]** define the standard distinction: **intrinsic** hallucinations are "consequences of synthesizing content using the information present in the input document" (source facts misrepresented); **extrinsic** hallucinations are "model generations that ignore the source material altogether."

Their XSum measurements (500 articles × 5 systems, 3 annotators each, Fleiss' κ 0.67–0.73) — percentage of summaries containing a hallucination: PtGen 75.3%, TConvS2S 78.5%, TranS2S 79.3%, BertS2S 73.1%, and **human-written gold summaries 76.9%**. Only ~21–27% of summaries were fully faithful. Only 7.8% of BertS2S's hallucinations were factually correct against world knowledge — hallucination and factual error are not the same thing.

### 5.2 The measurement families

**NLI / entailment-based.** SummaC (Laban, Schnabel, Bennett & Hearst, TACL 2022) [41] diagnosed why earlier NLI metrics failed — a *granularity mismatch*: NLI models are trained on sentence pairs but were applied to whole documents. The fix is a sentence-level NLI score matrix with aggregation. SummaC-ZS is zero-shot (no training); SummaC-Conv learns a ~50-parameter 1-D convolution. Balanced accuracy on the six-dataset SummaC benchmark: **SummaC-Conv 74.4%**, SummaC-ZS 72.1%, QuestEval 69.4%, DAE 64.2%, FactCC-CLS 62.8%, FEQA 58.7%. Throughput ~430 documents/minute on a Quadro RTX 8000 vs 20–40 docs/min for QA-generation metrics. Apache-2.0, `pip install summac`, `device="cpu"` supported.

**Synthetic-corruption classifiers.** FactCC (Kryściński, McCann, Xiong & Socher, EMNLP 2020) [37] trains BERT-base on 1,003,355 synthetic examples generated by rule-based corruptions (entity/number/pronoun swap, sentence negation, back-translation paraphrase, noise injection). 74.15% weighted accuracy, F1 0.5106 on a 503-example annotated test set; off-the-shelf BERT+MNLI transfer got only 51.51%, barely above chance at document level. Training used 8× V100 for 10 epochs — not reproducible on this budget, though the released checkpoint is free (BSD-3-Clause).

**QA-based.** QAGS (Wang, Cho & Lewis, ACL 2020) [38] generates questions from the summary, answers them against summary and source, and compares. Pearson r with human factual-consistency judgments: CNN/DM **54.53** vs ROUGE-1 28.74 / BERTScore 27.63; XSum **17.49** vs ROUGE-1 13.22 / BERTScore 2.51. Annotator agreement was itself low — Krippendorff's α 0.51 (CNN/DM), 0.34 (XSum). FEQA (Durmus, He & Diab, ACL 2020) [39] is the sibling approach and documents an abstractiveness/faithfulness trade-off: outputs with less lexical overlap with the source are more likely unfaithful. QAFactEval (Fabbri, Wu, Liu & Xiong, NAACL 2022) [40] optimises the QA pipeline for **+14% average over previous QA-based metrics** on the SummaC benchmark, and finds QA-based and entailment-based signals **complementary**.

**Meta-benchmarks.** TRUE (Honovich et al., NAACL 2022) [42] standardises 11 datasets across summarisation, dialogue, fact verification and paraphrase into a single *binary* scheme and meta-evaluates with **ROC AUC at the example level** rather than system-level correlation — "more actionable and interpretable", and it removes the need for many systems to correlate over. Average ROC AUC: ANLI 81.5, SummaC-ZS 81.4, Q² 80.7, BARTScore 72.2, QuestEval 71.4, BLEURT 71.4, FactCC 71.4, BERTScore 66.7, token-F1 63.8; an NLI + QG-QA ensemble reaches 86.0. AggreFact (Tang et al., ACL 2023) [43] aggregates nine annotation sets and stratifies by summariser generation, warning that "much of the recent improvement in the factuality detection space has been on summaries from older (pre-Transformer) models instead of more relevant recent summarization models", and that **no single metric wins across model classes or error types**.

**Atomic-fact decomposition.** FActScore (Min et al., EMNLP 2023) [45] decomposes a generation into atomic facts and scores the percentage supported by a knowledge source — a **precision** measure, not recall, which is a limitation to state explicitly. ChatGPT scored 58% on people biographies; the automated estimator has <2% error vs the human FActScore. Their cost datum: automatically scoring 6,500 generations from 13 LMs would have cost **$26K** by human annotation. RAGAS's Faithfulness metric is structurally identical: "Number of claims in the response supported by the retrieved context / Total number of claims in the response" [47].

**Reference-free / sampling consistency.** SelfCheckGPT (Manakul, Liusie & Gales, EMNLP 2023) [46] samples the same prompt multiple times at non-zero temperature: known facts recur, hallucinations diverge. No source document or external knowledge base required. On `wiki_bio_gpt3_hallucination`: SelfCheck-NLI 92.50 AUC-PR (NonFact) / 66.08 (Factual) / 74.14 passage ranking; SelfCheck-Prompt with gpt-3.5-turbo 93.42 / 67.09 / 78.32. MIT, `pip install selfcheckgpt`. Cost is N× generation.

### 5.3 The cheap, CPU-runnable options

**MiniCheck (Tang, Laban & Durrett, EMNLP 2024) [44]** is the strongest cost/accuracy point in the literature. MiniCheck-Flan-T5-Large is **770M parameters** and reports **74.7% balanced accuracy on LLM-AggreFact vs GPT-4's 75.3%**, at a measured cost of **$0.24 vs $107** on the 13K-example test set (≈400× cheaper). It runs on a free Colab T4 and on CPU. Licence is inconsistent across surfaces — repo Apache-2.0, `lytang/MiniCheck-Flan-T5-Large` model card MIT, `bespokelabs/Bespoke-MiniCheck-7B` **CC BY-NC 4.0 (non-commercial)** — confirm at download time. The **LLM-AggreFact** benchmark (`lytang/LLM-AggreFact`, now 11 datasets, 30,420 dev / 29,320 test) is **CC-BY-ND-4.0** with an explicit restriction: "Data in the benchmark should not be used in pretraining or fine-tuning any NLP models" — evaluation only.

**Vectara HHEM-2.1-Open [48]** is cheaper still: base google/flan-t5-base, **~0.1B parameters, Apache-2.0, <600MB RAM at 32-bit, ~1.5s for a 2k-token input on a modern x86 CPU, no GPU required**, unlimited context length. Balanced accuracy / F1: AggreFact-SOTA 76.55 / 66.77; RAGTruth-Summ 64.42 / 44.83; RAGTruth-QA 74.28 / 60.00. Note that **HHEM-2.3 is commercial-only** — the versions must not be conflated. RAGAS ships an official `FaithfulnesswithHHEM` variant that uses HHEM for the verification step, removing the paid-API dependency for verification, though claim decomposition still needs an LLM [47].

The **Vectara hallucination leaderboard** [49] (Apache-2.0, last updated 11 May 2026) is a directly copyable experimental protocol: >7,700 articles across domains (50–24,000 words), a fixed prompt instructing "summarize using only the information in the given passage" with a 20% length limit, **temperature 0**, refusals and under-length outputs excluded, single automatic judge. Current top hallucination rates run 1.8–4.1%.

### 5.4 Implementation cost, as reported by primary sources

This table records reported cost and hardware requirements from the sources. It is **not** a recommendation.

| Option | Effort | Budget | Basis |
|---|---|---|---|
| Vectara HHEM-2.1-Open [48] | Lowest | $0 | 0.1B params, <600MB RAM, CPU-only, ~1.5s/2k tokens, Apache-2.0, two lines of `transformers` |
| MiniCheck-Flan-T5-Large [44] | Low | $0 | 770M, 74.7% BAcc vs GPT-4's 75.3%, MIT weights, free Colab T4 or CPU, pip-installable |
| SummaC ZS/Conv [41] | Low–medium | $0 | `pip install summac`, CPU supported, Apache-2.0; ZS needs no training; BERT-Large backbone is slower on CPU than HHEM |
| RAGAS `FaithfulnesswithHHEM` [47] | Medium | $0 for verification | Apache-2.0; gives a defined, citable faithfulness formula; claim decomposition still needs an LLM |
| SelfCheckGPT (NLI variant) [46] | Medium | N× generation | MIT, pip-installable, reference-free; a DeBERTa-v3-large pass per sentence-sample pair |
| FActScore [45] | Medium–high | LLM API | Needs a capable LLM for decomposition plus a retrieval corpus |
| FactCC released checkpoint [37] | Medium | $0 | Free checkpoint (BSD-3) but only 62.8 BAcc in the SummaC benchmark — outclassed by everything above |
| QAGS / FEQA / QAFactEval [38, 39, 40] | High | $0–API | Multi-stage pipelines, 20–40 docs/min vs SummaC's 430, more failure modes |
| Training a detector | Highest | GPU | FactCC needed 1M synthetic examples on 8× V100; MiniCheck needed 35K curated examples plus synthesis infrastructure |

### 5.5 Measuring a *reduction*, which is what NFR-02 actually demands

**What published mitigation papers do.** Chain-of-Verification (Dhuliawala, Komeili, Xu, Raileanu, Li, Celikyilmaz & Weston) [53] is the cleanest template: a **paired before/after comparison on a fixed prompt set, same base model, metric held constant**. Results: Wikidata list-question precision **0.17 → 0.36** (hallucinated entities per answer 2.95 → 0.68) — but **correct entities also fell 0.59 → 0.38**, so the precision/recall trade-off must be reported; MultiSpanQA F1 0.39 → 0.48; longform biography FActScore 55.9 (Llama-65B few-shot) → 63.7 (CoVe factored) → 71.4 (factor+revise). Sample sizes are small: CoVe's Wikidata set is **56 test questions**, MultiSpanQA 418; Maynez used 500 documents; QAGS 235/239 summaries; FaithBench 660 samples. **A team annotating 200–500 items is squarely within published norms** — this is the most reassuring finding for scoping.

**Significance testing is usually absent from this literature.** CoVe reports none. Shuster, Poff, Chen, Kiela & Weston [54] claim retrieval "substantially reduce[s]" hallucination "as verified by human evaluations" with no percentage in the abstract. Reporting a significance test would place this project above median published practice.

**Guidance if the team chooses to test properly.** Dror, Baumer, Shlomov & Reichart (ACL 2018) [57] surveyed ACL/TACL/EMNLP 2017 and found significance testing "is often ignored or misused"; they give a test-selection protocol driven by the test statistic's distribution and the measure type — parametric t-test only under approximate normality, otherwise non-parametric (Wilcoxon signed-rank or sign test for paired comparisons, **McNemar for binary per-item correct/incorrect labels**, bootstrap or permutation as distribution-free defaults for aggregate measures such as F1). Deutsch, Dror & Roth (TACL 2021) [9] provide bootstrap and permutation methods for confidence intervals on metric correlations and warn the intervals are wide.

**The counter-evidence a report must include.** FaithBench (Bao et al., NAACL 2025) [52] built 660 samples from *modern LLM* summaries where SOTA detectors disagree, with a four-level severity taxonomy (Consistent → Benign → Questionable → Unwanted{Intrinsic, Extrinsic}) that separates harmless from harmful hallucination. Detector balanced accuracy / macro-F1: GPT-4o zero-shot **56.29 / 40.75**, HHEM-2.1 **55.68 / 40.86**, TrueTeacher 54.21 / 39.21, True-NLI 50.62 / 28.17, GPT-3.5-Turbo 44.91 / 37.41 — **near chance across the board**. HaluEval [50] measured ChatGPT fabricating unverifiable information in ~19.5% of responses; RAGTruth [51] provides ~18,000 word-level-annotated RAG responses; Kalai, Nachum, Vempala & Zhang [55] argue hallucinations persist because benchmark grading rewards guessing over abstention — "language models are optimized to be good test-takers"; HalluHard [56] measures ~30% hallucination even for the strongest 2026 configuration tested. The problem is not solved, and automatic faithfulness scores on modern LLM output are weak, noisy signals.

---

## 6. Human evaluation rubric design and inter-rater reliability

### 6.1 The canonical rubric

**SummEval [6]** is the template the field converged on. Four dimensions, defined verbatim:

- **Coherence** — "the collective quality of all sentences"; the summary "should not just be a heap of related information, but should build from sentence to sentence to a coherent body of information about a topic."
- **Consistency** — "the factual alignment between the summary and the summarized source. A factually consistent summary contains only statements that are entailed by the source document." Annotators penalise hallucinated facts.
- **Fluency** — "the quality of individual sentences"; no formatting problems, capitalisation errors or obviously ungrammatical sentences.
- **Relevance** — "selection of important content from the source"; penalise redundancy and excess information.

Protocol: Likert 1–5 per dimension; 100 articles × 16 models; **5 crowd workers and 3 experts** per summary (12,800 annotations); crowd hiring bar ≥10,000 approved HITs, ≥97% approval, ~US$12/hr; experts had published on summarisation or written a senior thesis. **"Summary grouping and order within groups were randomized for each annotator"**, with the reference summary included in each group as a fixed calibration anchor.

**The single cheapest documented intervention in this literature.** Expert Krippendorff's α was **0.4132 in round 1 and 0.7127 in round 2**. Round 2 was a targeted re-check: annotators revisited any item where their score differed from another annotator by >2 points while the others were within 1 point of each other. Crowd α was 0.4920.

**Crowd ratings did not agree with expert ratings at all** — group-averaged Pearson "close to 0" — and crowd ratings were near-uniform across the four dimensions, i.e. crowd workers did not distinguish the dimensions.

### 6.2 What the field's reporting looks like, and the low bar to clear

**Howcroft et al. (INLG 2020) [60]** reviewed all 578 INLG/ENLG papers 2000–2019 → 165 papers with human evaluations → **478 individual evaluations** (mean 2.8 criteria per paper). Findings: 478 verbatim criterion names reduce to **204 unique names** and **71 truly distinct criteria** ("fluency" alone mapped to 15 normalised meanings). **279 of 478 evaluations (58%) give no definition of the criterion; 311/478 (65%) do not report the prompt or question given to evaluators; 98/478 (20.5%) do not even name the criterion.** Instructions to evaluators are "almost never provided". Their Table 7 is a minimum-reporting list: system task, input/output, criterion name, criterion definition, rating instrument type/size, and the verbatim instructions.

"Appropriateness" is exactly the kind of overloaded term this paper indicts. NFR-02/FR-03's phrase "contextually appropriate" has no standard definition in the literature and would have to be defined by the team.

**van der Lee, Gatt, van Miltenburg, Wubben & Krahmer (INLG 2019 [61] / Computer Speech & Language 2021 [62])** surveyed NLG human evaluations: most are expert-focused with **1–4 annotators (median 4)**; only 55% specify the number of participants; **only 12.5% report inter-annotator agreement at all**, and where reported it "in most cases ranged from 0.3 to 0.5". Median **100 items** (range 2–5,400); in 83% of reporting papers all annotators saw all examples. Only 12.5% report design details (order, randomisation, counterbalancing); only 33% report any statistical analysis.

Their recommendations: difficult coding tasks — "which most NLG evaluations are" — need **three or more annotators (preferably more)**; reader-focused studies need 100+ participants (citing Brysbaert 2019: "most studies with less than 50 participants are underpowered"); report the agreement coefficient **with confidence intervals plus raw percentage agreement**; **do not use rigid thresholds** — "it is undesirable to use restrictive thresholds, since an ostensibly low IAA score could be due to a host of factors, including personal bias"; counterbalance or randomise order and report it; run a calibration practice trial showing very good and very bad outputs; Bonferroni-correct across multiple criteria; ask about each criterion **separately** rather than simultaneously, since simultaneous presentation inflates cross-criterion correlation.

**Mei et al. (ACL 2026) [76]** repeat the audit on 284 recent \*CL papers against 20 reportability criteria: **only 46% report IAA at all**; 77% report annotator count (**median 3**); 85% report sample size (**median 170 items**, range 10–23,040); **only 29% explicitly state whether the evaluators are the paper's own authors**; 29% report payment; 11% report ethics review; 6% include attention or manipulation checks; 19% discuss evaluation limitations. **Kunilovskaya et al. (2026) [78]** reach a compatible conclusion over 1,603 \*CL papers and 2,667 annotation tasks: operational details are usually reported, while validity-relevant details — training, language proficiency, compensation, adjudication and agreement — are routinely omitted.

### 6.3 The reporting template a student team can adopt wholesale

**Belz, Mille & Howcroft (INLG 2020) [63]** classify human evaluation methods along **18 properties** in three groups (3 quality-criterion properties, 3 evaluation modes, 12 experimental-design properties). The three criterion properties: (i) type of quality assessed; (ii) aspect of output — form only / content only / both; (iii) frame of reference — output in its own right, relative to the input, or relative to a system-external frame. These combine into 27 groupings. The three modes: objective vs subjective, absolute vs relative, extrinsic vs intrinsic; "quality criterion + evaluation mode = evaluation measure". Their demonstration: three papers all calling a criterion "Fluency" measured three demonstrably different things, and differently-named criteria in another paper were identical. Naming a criterion is not defining it.

**The Human Evaluation Datasheet (Shimorina & Belz, HumEval @ ACL 2022) [64]** is the ready-made artefact, built directly on [60] and [63]. Five sections — Paper and Resources; Evaluated System; Output Sample, Evaluators and Experimental Design; Quality Criteria (repeatable for up to 10); Ethics. Directly relevant question IDs: **Q3.2.1** how many evaluators, **Q3.2.2** what kind (where author status is declared), **Q3.2.4** training/practice given, **Q3.3.1** preregistration, **Q3.3.3** quality assurance, **Q3.3.4** what evaluators see during each assessment, **Q4.3.2** the criterion's definition, **Q4.3.7** the verbatim prompt shown to evaluators, **Q4.3.10** effect size and significance method, **Q4.3.11** inter-annotator agreement.

An alternative domain-specific rubric structure: **QUEST** (Tam et al., *npj Digital Medicine* 2024) [77] — Quality of Information, Understanding and Reasoning, Expression Style and Persona, Safety and Harm, Trust and Confidence — 5 principles, 17 dimensions, 4- or 5-point Likert, derived from a review of 142 studies.

### 6.4 Inter-rater reliability: statistics, thresholds, and a trap

**Canonical citations:** Cohen's κ for 2 raters on nominal data [67]; Fleiss' κ for many raters [68]; Krippendorff's α [69, 70]; Landis & Koch interpretation bands [71]; Artstein & Poesio's computational-linguistics survey [72].

**Choice of statistic for a binary "appropriate / not appropriate" judgment.** Exactly 2 raters → Cohen's κ. Three or more raters → Fleiss' κ or Krippendorff's α; α is preferable because it handles "any number of observers, not just two", "any number of categories", "any metric or level of measurement", **"incomplete or missing data"**, and "large and small sample sizes alike, not requiring a minimum" [69]. James (LREC 2026) [79] provides a current decision guide for metric selection.

**A correction worth knowing.** The widely cited α thresholds (≥.800 good, .667–.800 tentative) are **not** in Krippendorff's *Computing Krippendorff's Alpha-Reliability* [69], which is purely computational (coincidence matrices, difference functions, bootstrapping). Artstein & Poesio trace the .667/.8 convention back through Carletta (1996) to Krippendorff (1980) and add the caveat that "the description of the 0.67 boundary in Krippendorff (1980) was actually 'highly tentative and cautious'", and that Krippendorff later considers 0.8 the absolute minimum: "Even a cutoff point of α = .800 … is a pretty low standard" [70, 72].

**Landis & Koch bands** [71]: <0.00 Poor · 0.00–0.20 Slight · 0.21–0.40 Fair · 0.41–0.60 Moderate · 0.61–0.80 Substantial · 0.81–1.00 Almost Perfect. Artstein & Poesio §5.3 is the authoritative caution: interpreting agreement magnitudes is "little more than a black art"; "we doubt that a single cutoff point is appropriate for all purposes … setting a specific agreement threshold should not be a prerequisite for publication." Instead report the number of coders, whether they coded independently, whether they relied exclusively on an annotation manual, whether agreement was statistically significant, and a confusion matrix [72].

**Amidei, Piwek & Willis [65, 66]** surveyed 135 NLG papers (2008–2018): only **18% (24 papers) report IAA at all**. Across those: percent agreement 0.69 (range 0.44–0.94), Cohen's κ **0.40** (0.10–0.88), Krippendorff's α 0.62 (0.37–0.90), Fleiss' κ 0.53 (0.29–0.78), Pearson's r 0.42 (0.20–0.71). Only 20% of the IAA-reporting papers reference any interpretation scale. In their own 7-annotator study every criterion scored **below 0.67, lowest 0.11**. Their argument: NLG has no gold standard for criteria like ambiguity, relevance, usefulness or overall quality, so "reliability as reproducibility" is the wrong frame; legitimate divergence comes from style/taste, background knowledge, personal assumptions, common-sense inference and attention to detail, and "language variability must be preserved by NLG systems". Their proposal: **report correlation alongside agreement**. One of their case studies had IAA <0.4 with perfect (1.0) correlation; another had Fleiss' κ = 0.52 with Goodman–Kruskal γ = 0.98. A rater who consistently scores one point below another has zero agreement and perfect correlation — and is a perfectly usable rater.

**The trap specific to a ≥90% appropriateness target — the kappa paradox.** If "appropriate" is the overwhelmingly common label (which it will be if the system works), expected chance agreement is very high and κ collapses even when raters agree on nearly everything. Feinstein & Cicchetti [73]: "a high value of p₀ can be drastically lowered by a substantial imbalance in the table's marginal totals." Artstein & Poesio work the arithmetic: if 95% of items fall in one category, random coding alone yields ≥85.7% accuracy, so "coders may agree on a high proportion of items while producing annotations that are indeed correct to a high degree, yet the reliability coefficients remain low" [72]. Their defence of the paradox is the load-bearing point: "Reliability implies the ability to distinguish between categories … The test for reliability in such cases is the ability to agree on the *rare* categories." A low κ on a skewed binary judgment says the raters may not reliably identify the *inappropriate* drafts — precisely what NFR-02 cares about. Byrt, Bishop & Carlin [74] define a **bias index** and **prevalence index** and derive **PABAK**, recommending κ be reported together with quantitative bias and prevalence indicators, never alone.

### 6.5 Raters who cannot detect the thing, and raters who are the authors

**Clark et al. (ACL 2021) [75]** is the sobering result. Untrained non-expert evaluators distinguishing human- from machine-authored text: **57.9% correct for GPT-2** but **49.9% for GPT-3 — indistinguishable from the 50% chance baseline**, across stories, news and recipes. Agreement among untrained evaluators was **Krippendorff's α ≈ 0**. Three cheap training interventions (extended instructions naming quality dimensions; 3 annotated practice examples with explanations; paired human/machine comparison with the answer revealed) were tested on 1,170 evaluators / 5,850 annotations: all raised accuracy, but only *Examples* significantly (Tukey's HSD adjusted p < 0.003, **d = 0.25**), reaching ~55%, and **agreement stayed at α ≤ 0.11 even with training**; "higher agreement did not correspond to higher accuracy". Untrained raters "mainly focused on the *format* of the text", with content comments only ~25% of labels; the *Examples* training roughly doubled content comments. Their recommendations: train with examples; ask evaluators *why* and confirm the explanation; report the full instructions and any training given.

**Author-as-rater.** There is **no paper devoted to author-as-rater bias in NLG evaluation** — a genuine gap. What exists:

- Mei et al. [76]: only **29% of 284 recent \*CL papers explicitly state whether their evaluators are the paper's authors.** Stating it plainly already exceeds 71% of published practice.
- Tam et al. [77] (n = 142 studies): **only 41 studies (29%) explicitly used blinded evaluation; 20 (14%) were explicitly unblinded; 80 (56%) gave no information.** Their recommendation is that evaluators be "unaware of the source of the responses they are assessing" with the blinding procedure documented in the methodology. Most studies used fewer than 20 evaluators (medians 2–8 by application type).
- Artstein & Poesio [72] defend small expert panels explicitly — "A rigorous methodology for reliability testing does not, in our opinion, exclude the use of expert coders" — with a precise caveat: expert/trained annotation "means that results are not replicable across sites, and are therefore less reliable than annotation by naive coders adhering to written instructions." The remedy they name is a self-contained written annotation manual a stranger could execute, plus agreement studies assuring replicability "when the annotators are chosen from the same population as the original annotators". They also note **increasing the number of annotators is the single best strategy** because "it reduces the chances of accidental personal biases".
- van der Lee et al. [61]: experts "approach evaluation differently from general readers, injecting their own opinions and biases", and may not be representative when the system targets a general population.

**Order effects and blinding, concretely** [61]. Within-subjects designs (all raters see all items — 83% of surveyed papers) are "susceptible to order effects: over the course of an experiment, annotators can change their responses due to fatigue, practice, carryover effects", and with a fixed order "differences found between systems may be due to order effects rather than differences in the output itself." Full counterbalancing is impractical (4 items → 24 orders); the practical guidance is to **group items randomly into sets and counterbalance set order**, with the bottom line that "in most cases, randomising the order of examples should be sufficient." A between-subjects design is the alternative when order effects are expected across many conditions. A calibration trial reduces practice effects. Attention checks carry their own risk: excluding failers "introduces a demographic bias, and attention checks actually induce low-effort responses or socially desirable responses."

### 6.6 Sample size and statistical power for the ≥90% target

**Card, Henderson, Khandelwal, Jia, Mahowald & Jurafsky (EMNLP 2020) [59]** meta-analysed 117 Likert comparisons from 41 EMNLP 2019 papers: **69% used ≤100 items; only 18% used >200; 57% collected 3 annotations per item.** Their headline: "the most common design at EMNLP 2019 (**3 workers, 100 items**) is **underpowered unless the effect size is quite large (0.2 or higher on the [0,1] scale)**". Even in the low-variance case, detecting a 0.05 effect needs "10+ [ratings per item] for 100 items". Recommendations: run a power analysis before collecting data and pre-write an analysis plan; expect to need more workers and items than is typical in NLP, "particularly by using more workers per item"; analyse with hierarchical mixed-effects models; release anonymised raw ratings and analysis code. 80% power at α = 0.05 is the standard bar.

**The binomial-proportion arithmetic for "≥90% of drafts rated contextually appropriate".** Brown, Cai & DasGupta [58] show the standard Wald interval has "chaotic coverage properties" that are "far more persistent than is appreciated", and recommend the **Wilson** interval (small samples) or Agresti–Coull (larger). Wilson 95% intervals at an observed ~92% appropriateness rate:

| n | k (≈92%) | 95% Wilson CI |
|---|---|---|
| 20 | 18 (90.0%) | [0.699, 0.972] |
| 30 | 28 (93.3%) | [0.787, 0.982] |
| 50 | 46 (92.0%) | [0.812, 0.968] |
| 100 | 92 (92.0%) | [0.850, 0.959] |
| 200 | 184 (92.0%) | [0.874, 0.950] |
| 384 | 353 (91.9%) | [0.888, 0.943] |

To claim ≥90% with a 95% lower bound above 0.90 requires **n ≥ 35 at a perfect 100% score**, or **n ≈ 140 at a 95% observed rate**. At n = 50 the interval spans 0.812–0.968: the data cannot distinguish a 90% system from an 82% one. (Computed with the standard Wilson score formula; reproducible in three lines of Python.)

### 6.7 Domain precedent: how industry evaluated Gmail assistance

Gmail Smart Compose (Chen et al., KDD 2019) [118] used **log perplexity** and **ExactMatch@N** (percentage of predicted N-word phrases exactly matching the first N ground-truth words) offline, and **click-through rate** plus ExactMatch online; personalisation gave ~6% relative CTR gain and 10% relative ExactMatch gain. The paper is also the clearest industry statement of the privacy constraint the team faces in a different form: "we had to develop this system **without anyone on the project being able to look at the underlying data**." Smart Reply (Kannan et al., KDD 2016) [119] is the companion system paper; **neither released any data**.

---

## 7. Candidate datasets

### 7.1 Real email corpora

| Dataset | Introducing paper | Size | Licence | PII status | Obtainable? |
|---|---|---|---|---|---|
| **Enron Email Dataset** [80, 81] | Klimt & Yang, ECML 2004 | ~0.5M messages, ~150 users | **No licence stated anywhere.** The CMU page has no terms of use, no copyright grant, no CC mark. Only a moral request: "please be sensitive to the privacy of the people involved" | **Severe — see §7.4.** Verified credit card numbers, SSNs, DOBs, medical/legal matters; residual PII survives professional cleansing | Free direct download, no agreement |
| **AESLC** (Annotated Enron Subject Line Corpus) [93] | Zhang & Tetreault, ACL 2019 | 18,302 emails (14,436/1,960/1,906); dev+test have 3 extra MTurk subject lines each | Repo `LICENSE.md`: **CC BY-NC-SA 4.0**. The HuggingFace card `Yale-LILY/aeslc` declares `license: unknown` — contradicts upstream; cite the GitHub file | **Inherits full Enron PII with zero mitigation.** The paper never mentions anonymisation, privacy, consent or PII. Sender/recipient fields dropped as a side effect of keeping subject+body; **bodies untouched** | Free, ungated |
| **EmailSum** [7] | Zhang, Celikyilmaz, Gao & Bansal, ACL-IJCNLP 2021 | 2,549 threads (3–10 emails); 1,800/249/500; short (<30w) + long (<100w) human summary each | Repo `LICENSE` = **MIT**, © Microsoft and UNC NLP — **covers summaries and code only**. Email text governed by the LDC Avocado agreements | Best-documented here. §2.1: "To protect privacy, we anonymize all email threads before annotation: (1) only keep first names; (2) remove threads that have 'password', 'pwd', 'confidential', etc.; (3) replace email address, physical address, phone number, URL, IP address, local path, and other sensitive numbers with placeholders" | **Gated.** "We only release the summaries we collected and provide scripts to extract email threads from flat email corpus (Avocado or W3C), because Avocado's copyright is protected by Linguistic Data Consortium." Requires LDC2015T03 |
| **Avocado Research Email Collection** LDC2015T03 [95] | Oard, Webber, Kirsch & Golitsynskiy, 2015 | 2,033,740 items from **279 custodians**; after redaction/dedup **614,461 emails** + 89,072 attachments | **Two signed agreements** (Organizational Licence + End User Agreement). **Fee login-gated — no public price.** §3 forbids publishing examples even in papers; §4 forbids derived artefacts on a public server | **Real non-public corporate email; no employee consent claimed.** Agreement header: "The Collection may contain sensitive personally identifiable information that requires protections different from, and in some cases more restrictive than, other types of linguistic resources." Credit cards, SSNs, contact-record home addresses/birthdays redacted; **names, bodies and business addresses NOT redacted** | Requires institutional signature |
| **EnronSR** [96] | Shay, Davidson & Grinberg, ICWSM 2024 | 34,626 incoming messages; 3,406 with both a human reply and a Gmail Smart Reply suggestion | **CC BY-NC-SA 4.0** (consistent across Dataverse, repo LICENSE, CITATION.cff) | Ethics statement: approved by Ben-Gurion University ethics board (protocol #344-1); "No personally identifying information (PII) is released as part of this dataset." But it is a *layer over* raw Enron | Free, ungated |
| **BC3** (BC Conversation Corpus) [97] | Ulrich, Murray & Carenini, AAAI 2008 EMAIL Workshop | **40 threads, 3,222 sentences**, 3 annotators each; extractive + abstractive summaries, speech acts, subjectivity | **CC BY-SA 3.0** for the corpus, MIT for the framework — permissive, no NC clause | **Real email from real named people.** W3C public mailing lists, **zero anonymisation** — the paper's own figures show real names and addresses | Free after a registration form (landing page 404s; the download form is live) |
| **W3C corpus** (TREC Enterprise 2005–06) [98] | TREC Enterprise Track | 198,394 mailing-list documents (1.855 GB); 331,037 docs total | **No licence stated.** The page says only "These mailing lists are public and no usage agreement is necessary to obtain them" — a posture, not a grant | Real names and addresses of identifiable people | Free tarballs |

### 7.2 Non-email conversational proxies

| Dataset | Paper | Size | Licence | Provenance / PII |
|---|---|---|---|---|
| **SAMSum** [99] | Gliwa, Mochol, Biesek & Wawer, New Frontiers in Summarization @ EMNLP-IJCNLP 2019 | 16,369 dialogues (14,732/818/819) | **CC BY-NC-ND 4.0** (verbatim from the card: "non-commercial licence: CC BY-NC-ND 4.0") | **Confirmed synthetic — see §7.5.** No real personal data |
| **DialogSum** [100] | Chen, Liu, Chen & Zhang, Findings of ACL-IJCNLP 2021 | 13,460 dialogues (12,460/500/500) | README (no LICENSE file in repo): "This dataset is under CC BY-NC-SA 4.0 license. The copyright of dialogue data in DialogSum dataset belongs to users who created them." | ESL teaching material and listening-exam transcripts (DailyDialog 58.2%, DREAM 16.9%, MuTual 13.9%, tingroom.com 12.8%). Not real private conversation, but **no anonymisation claim is made**; speaker tags are a fallback "if real names cannot be detected" |
| **QMSum** [101] | Zhong et al., NAACL 2021 | 1,808 query–summary pairs over 232 meetings (137 AMI + 59 ICSI + 25 Welsh Parliament + 11 Parliament of Canada) | **MIT** — covers the repo/annotations only, not the underlying meetings | **Contains real named living politicians** (e.g. named MPs with constituency and party). Public record, but still personal data |
| **AMI Meeting Corpus** [102] | Carletta et al. | ~100 hours, ~171 meetings | **CC BY 4.0**, verbatim: "All of the signals and transcription, and some of the annotations, have been released publicly under the Creative Commons Attribution 4.0 International Licence (CC BY 4.0)." An older NC-SA 2.5 statement survives on the page inside an HTML comment and is not operative | Real people, with **documented written informed consent** and European Commission ethics review; the consent form and ethics annex are published. Ethically the cleanest corpus here — but still real PII (voice, faces, names) |
| **ICSI Meeting Corpus** [103] | Janin et al. | 75 meetings, ~72h, ~795k words, 53 speakers | LDC route (LDC2004S02/T04) is fee-gated; **also free under CC BY 4.0 from Edinburgh**, which is the route QMSum used | Real weekly research-group meetings; LDC states participants were "fully cognizant of the recording process". Real PII |

### 7.3 Synthetic email

| Dataset | Size | Licence | Notes |
|---|---|---|---|
| `argilla/FinePersonas-Synthetic-Email-Conversations` [104] | 313,663 rows / 1.73 GB | **`license: llama3.1`** (Llama 3.1 Community License — *not* an open licence) | Generated by Hermes-3-Llama-3.1-70B from FinePersonas personas. Provides real **thread structure** (`formatted_emails` = list of `{sender, recipient, subject, body}`). **No reference summaries, no gold replies** |
| `argilla/FinePersonas-Conversations-Email-Summaries` [104] | 363,584 rows | **`license: other`, `license_name: qwen`** | Qwen2.5-72B-Instruct. Has `summary` (≤3 sentences) + `maximum_brevity_summary`. **Per-email, not per-thread** — requires re-aggregation on `conversation_id`. Gold summaries are unverified LLM output |
| `nvidia/Nemotron-PII` [105] | 200,000 rows | **CC BY 4.0** | Fully synthetic, census-grounded personas, 55+ PII span categories including email documents. Suited to testing a redaction layer, not to summarisation |
| `nvidia/Nemotron-Personas-USA` [105] | ~6M personas | **CC BY 4.0** | The clean primitive if a team generates its own corpus |

**Verified NOT to exist** (do not cite): "MailBench", "EmailAgentBench", any public Google Smart Reply training data. tau-bench and successors have no email domain. **There is no established synthetic email-thread summarisation or reply-drafting benchmark** — nothing that is to synthetic email what SAMSum is to dialogue.

### 7.4 Enron, assessed squarely

**Provenance, verbatim from the CMU distribution page [81]:**

> "This dataset was collected and prepared by the **CALO Project (A Cognitive Assistant that Learns and Organizes)**. It contains data from about 150 users, mostly senior management of Enron, organized into folders. The corpus contains a total of about 0.5M messages."

> "This data was originally **made public, and posted to the web, by the Federal Energy Regulatory Commission during its investigation.**"

> "The dataset here does not include attachments, and **some messages have been deleted 'as part of a redaction effort due to requests from affected employees'**."

> "This data is valuable; **to my knowledge it is the only substantial collection of 'real' email that is public. The reason other datasets are not public is because of privacy concerns. In using this dataset, please be sensitive to the privacy of the people involved (and remember that many of these people were certainly not involved in any of the actions which precipitated the investigation.)**"

Note the removal process is **passive and retrospective**: it existed only for employees who learned of the corpus and asked. The page also records that the maintainer cannot answer questions about the corpus's preparation, and (as of April 2026) carries an authenticity caveat about a historic Enron mail-system flaw permitting untraceable impersonation — the page judges this "probably does not affect NLP uses of the corpus".

**There is no licence.** The page contains no terms of use, no copyright grant, no public-domain declaration. The common claim that Enron is "public domain" is a legal misstatement, and there is a citable source saying so — Levendowski [85], at 610–612:

> "The Enron emails are often colloquially referred to as being in the 'public domain,' but that is a legal misstatement. While the Enron emails are available online publicly, **they are more like orphan works: using the works still carries some risk, as getting permission from each of the authors is highly unlikely**…"

The correct characterisation: FERC released the emails into a US federal agency's public investigative record in 2003. That makes the documents publicly accessible; it does not transfer or extinguish copyright, and it says nothing about data-protection obligations, which are a separate legal regime.

**Redistribution platforms decline to grant a licence.** Kaggle's most-downloaded copy (`wcukierski/enron-email-dataset`) has the licence field **"Data files © Original Authors"** — Kaggle's placeholder for *no licence granted, copyright retained*. On HuggingFace there is no canonical Enron dataset; ~50 user re-uploads carry mutually contradictory tags (`unknown`, `apache-2.0`, `mit`, or none). **No uploader has standing to grant Apache-2.0 or MIT over other people's email.** Those tags are noise.

**PII — the primary evidence.** EDRM/Nuix, 15 May 2013 [82], verbatim:

> "Nuix consultants Matthew Westwood-Hill and Ady Cassidy identified more than 10,000 items including: • **60 items containing credit card numbers**, including departmental contact lists that each contained hundreds of individual credit cards • **572 containing Social Security or other national identity numbers** — thousands of individuals' identity numbers in total • **292 containing individuals' dates of birth** • **532 containing information of a highly personal nature such as medical or legal matters**"

> "The investigative team also clearly demonstrated that these items did not stay within the Enron firewall. For example, some staff emailed 'convenience copies' of documents containing private data to their personal addresses."

**Residual PII survives the cleansing.** Noever [83] (arXiv preprint, not peer-reviewed) reports that beyond EDRM's 10,000 elements, "**the present work identifies nearly 50,000 additional items that might qualify as PII**", including "potentially 86 new credit cards, 30 passport numbers, 18 international bank accounts and 4 social security numbers", and that clear examples of raw credit-card information appear "in both the original 2003 **and cleansed 2016** Enron email corpus". **The forensically cleansed corpus is not clean.** "Use the cleaned version" is not a mitigation for NFR-01.

**Consent — the critique literature is thinner than expected, and that is itself a finding.** Verified sources:

- **The Pile [84]**, §6.5 "Author Consent and Public Data", is the clearest explicit statement: "**The Enron Emails dataset was not collected with the permission of the authors, but was collected by the U.S. government as part of a criminal investigation. While the people whose emails are in the Enron dataset are aware of this fact, they were not given the ability to consent to its inclusion in any way.**" The authors add: "We adopted a strict model of consent, where ambiguous or unknown consent is treated as nonconsensual."
- **Levendowski [85]** on representativeness: "The quintessential example of BLFD [biased, low-friction data] is familiar to computer scientists: the Enron emails … **The Enron emails are simply not representative — not geographically, not socioeconomically, not even in terms of race or gender.** And yet the Enron emails remain a go-to dataset for training AI systems." The empirical basis for the gender skew is Mohammad & Yang [86]: "41 employees as female and 89 as male; 20 were left gender-untagged" — roughly 2:1 male among identifiable users, all skewed toward senior management.
- **Sayed et al. (SIGIR 2020) [87]** is a top-venue refusal to use Enron: "Since our goal is to protect the sensitive information in the collection then the last thing we would want to do is to highlight where to find that sensitive content. **Doing so in a public test collection such as Enron thus raises some ethical concerns that do not seem to us to have yet been adequately commented upon.** We have therefore chosen to annotate the Avocado Research Email Collection…" That final clause is a peer-reviewed acknowledgement, by a team including an ethics specialist, that the critique literature is thin.
- **The published counter-argument**, for balance — McKechnie, McDonald & Macdonald (SIGIR 2026) [88], §7: "However, the Enron Email Collection has been publicly available for over a decade and has undergone numerous redaction efforts. Therefore, those ex-Enron employees who felt that they did not want their emails to be read by others have an opportunity over the last 10 years to request the removal of their emails. … Consequently, we argue that the use of the Enron Email Collection … is justified."
- **Zimmer (2026) [89]** in *Big Data & Society* is the only journal article devoted to a critical reading of the corpus. Its abstract asks: "Why is it that theft, scandal, and fraud lie at the heart of so many of the most prominent training sets?" (Full text was not retrievable — publisher blocked. Do not quote its interior.)
- **Active harm from the corpus.** Huang, Shao & Chang (Findings of EMNLP 2022) [90] build a (name, email) leakage benchmark of 3,238 pairs from the Enron portion of The Pile, demonstrating PII extraction from pretrained models. Note the irony in their own Limitations: Enron is chosen precisely because the authors need not seek consent.
- **The human dimension.** Pat Wood III, FERC Chairman at the time of the release, on the record [91]: "**Man, I was a huge accomplice in doing that to a lot of people**, a lot of whom live in the town where I now live." And: "if you did something wrong damn it, I got you. **But for all those people in the middle who just had a normal expectation of privacy…**" Cite as journalism, not scholarship; the same episode includes a dissenting ex-Enron voice who reports no harm.
- **Craig Ball (EDRM, 2025) [92]** argues for retiring the corpus, but primarily on technical-obsolescence grounds: "Post-2000 privacy laws, heightened sensitivity to privilege and aggressive litigation strategies make a wholesale release of modern corporate mailboxes virtually impossible… Chances are we will never see the likes of the Enron email release."

**Australian privacy law is the binding regime for a Monash project [113].** The OAIC states plainly that "Personal information can range from sensitive and confidential information to **information that is publicly available**" — there is no general public-availability exemption. APP Guidelines Chapter B, **B.29**: an entity does not collect personal information where it is acquired but not included in a record — but a generally available publication *does* become a record if, for example, "the article is scanned and saved into the entity's electronic database". **B.82**: an entity "holds" personal information if it "has possession or control of a record that contains the personal information". **The moment Enron is downloaded into the repository, the "generally available publication" carve-out from "record" no longer applies and the team holds a record of personal information**, engaging APP 3 (collection), APP 6 (use) and APP 11 (security).

The NHMRC National Statement (2025) [114] permits a review body to waive consent only if satisfied, among other things, that "it is impracticable to obtain consent" **and** that "there is no known or likely reason for thinking that participants would not have consented if they had been asked". For Enron the first is easily met; the second is arguably not, given the documented removal requests and Pat Wood's own account. On the EU side, EDPB Guidelines 1/2026 on scientific research [115] address the impracticability of informing data subjects in research but are **silent on leaked or court-released data** — do not stretch them.

**Net assessment.** For a team with a hard "no real PII processed" requirement, Enron fails on every axis at once: no licence, no consent, verified live financial and identity data surviving a professional forensic cleansing, a passive-only removal process, and an Australian statutory regime under which downloading creates a record the team holds. Every Enron derivative inherits the problem; **AESLC is the worst case** because it is the most convenient (free, ungated, email-shaped) and its authors never addressed PII at all. Whether that is disqualifying is a decision for the decision ticket; the evidence is not ambiguous.

**A second-order consequence worth noting.** BC3 — the closest thing to a purpose-built email-thread summarisation benchmark with human summaries — is un-anonymised W3C mail with real names and addresses. QMSum, AMI and ICSI likewise contain real PII despite excellent licences and, for AMI, genuinely exemplary documented consent. Under a literal reading of NFR-01, the standard benchmarks for this task are ones the project cannot use.

### 7.5 SAMSum: the synthetic-provenance claim verifies

From the paper [99], verbatim:

> "Our dialogue summarization dataset contains natural messenger-like conversations **created and written down by linguists fluent in English**."

> "We asked linguists to create conversations similar to those they write on a daily basis, reflecting the proportion of topics of their real-life messenger conversations. … **Therefore, this dataset does not contain any sensitive data or fragments of other corpora.**"

They explicitly considered and rejected real data (chatbot dialogues, SMS corpora, IRC/chat, movie dialogues, tweets), and validated realism: "the results revealed that 94% of examined dialogues were classified by both annotators as good."

**Licence caveats that matter.** The string is `non-commercial licence: CC BY-NC-ND 4.0`. **NC** is fine for coursework but bites on any commercial trajectory or sponsor demo. **ND is the sharper constraint**: a cleaned, re-split, re-formatted or augmented version may not be published, and publishing a checkpoint fine-tuned on SAMSum is legally untested and, read conservatively, is distribution of adapted material. **Availability has degraded**: `huggingface.co/datasets/Samsung/samsum` and `huggingface.co/datasets/samsum` both return HTTP 401, the Samsung HF org lists zero public datasets, and ELRA returns no result for "SAMSum". The dataset survives via community mirrors, and third-party redistribution is exactly what ND makes questionable. The verbatim licence string above was read from a mirror, not from a live Samsung-controlled page.

### 7.6 Synthetic email as a candidate — the methodological caveats

**(i) Diversity limits.** Liu et al. (COLM 2024) [106]: "the potential for synthetic data to amplify biases or introduce new biases if not carefully designed and validated", and on evaluation specifically, "Synthetic data might include rephrased versions of the benchmark data, rendering token-level decontamination ineffective." Most directly on point, because it tests the exact persona-prompting method the FinePersonas corpora use — Kambhatla, Shaib & Govindarajan (Findings of EMNLP 2025) [107]: "we find that synthetic prompts/instructions are significantly less diverse than human-written ones", and "adding fine-grained persona details yields minimal gains in diversity compared to simply specifying a length cutoff in the prompt." Richer personas do not buy an escape from homogeneity.

**(ii) Circularity.** Panickssery et al. [18] and Zheng et al. [16] establish self-preference. Wataoka, Takahashi & Ri [112] establish the mechanism and the sharper warning: the bias tracks **perplexity, not identity** — "regardless of whether the outputs were self-generated". If the corpus is LLM-generated, every system under test summarises unusually low-perplexity, stylistically homogeneous text and every LLM judge scores it generously. Generating with one vendor, summarising with a second and judging with a third makes the circularity less visible, not less real.

**(iii) Model collapse — with its correct scope.** Shumailov et al. (*Nature* 2024) [108] show recursive training on generated data produces "irreversible defects in the resulting models, in which tails of the original content distribution disappear." **Scope warning:** this is about *training*, specifically recursive training. It establishes nothing directly about *evaluating* on synthetic data, and citing it to argue "our synthetic eval set is invalid" over-claims. The legitimate transfer is the mechanism, not the conclusion: generative models under-represent distribution tails, so a one-generation synthetic email corpus inherits that tail loss — rare phrasings, unusual thread structures, messy real-world email — and evaluation on it over-samples the easy centre. A published critique exists (Borji, arXiv:2410.12954).

**(iv) Benchmark contamination — an argument that runs the other way.** Xu, Guan, Greene & Kechadi [109] define the problem: models "inadvertently incorporate evaluation benchmark information from their training data, leading to inaccurate or unreliable performance during the evaluation phase." A freshly generated synthetic corpus is **contamination-free by construction**. Enron and its derivatives are almost certainly in every frontier model's pretraining corpus — Enron is a named component of The Pile [84]. The advantage holds only if generation is genuinely persona-driven rather than a rewrite of an existing benchmark, per [106].

**(v) Direct guidance on synthetic data for *evaluation*.** Gill, Ravichander & Marasović [110] are the single best source on point: prompting LLMs "can produce variants of these datasets that are often valid according to the annotation guidelines, at a fraction of the cost of the original crowdsourcing effort. **However, we show that they are less challenging for LLMs than their human-authored counterparts.** This finding sheds light on what may have been lost by generating evaluation data with LLMs, and calls for critically reassessing the immediate use of this increasingly prevalent approach to benchmark creation." Their criteria: "Benchmarks must target specific phenomena, penalize exploiting shortcuts, and be challenging." Wang, Maddi, Lin & Fanti (SynAE) [111] address almost exactly this project's situation — "internal production datasets are often insufficient or unusable for testing; for example, they may contain sensitive or proprietary data … practitioners are increasingly replacing or augmenting real datasets with synthetic ones for evaluation purposes" — and conclude "no single metric is sufficient to fully characterize synthetic data quality, motivating a multi-axis evaluation" along validity, fidelity and diversity.

---

## 8. What the sources do NOT settle

1. **No source establishes a valid metric or threshold for *email* summarisation.** EmailSum [7] shows ROUGE and BERTScore fail on this task; Dai et al. [10] show metrics are meta-evaluated on news; DIAL-SUMMER [14] shows dialogue error profiles differ from news. Nothing in the located literature tells you what a *good* score looks like on email threads under any metric. Any threshold the project sets will be a project convention, not a literature-backed bar.
2. **No source establishes what "contextually appropriate" means for an email draft.** Howcroft et al. [60] show "appropriateness"-class terms are among the field's most overloaded. No rubric for email reply appropriateness was located in the peer-reviewed literature. SummEval's four dimensions [6] and QUEST's seventeen [77] are the nearest transferable structures, and neither was designed for reply drafting.
3. **Whether an LLM judge is *acceptable to a Monash marker* is not a literature question.** Dietz et al. [30] answer "it depends" for research publication. Nothing addresses undergraduate assessment. This needs a supervisor conversation, not more reading.
4. **Temperature and decoding for an LLM judge are contested.** Stureborg et al. [19] recommend temperature 0 and no CoT; Yamauchi et al. [32] find non-deterministic sampling improves human alignment and CoT adds little. No source reconciles these.
5. **The self-preference literature does not tell you how to break the loop when your corpus is also LLM-generated.** Wataoka et al. [112] show the bias is perplexity-driven, not identity-driven, which implies vendor diversity is not a fix — but no source proposes a validated mitigation for the corpus-and-judge-both-synthetic case.
6. **Automatic faithfulness detectors are not validated on modern LLM output.** FaithBench [52] puts the best of them near chance on exactly the kind of text this project will generate. AggreFact [43] shows apparent progress is concentrated on pre-transformer outputs. No source establishes that HHEM or MiniCheck numbers are trustworthy on 2026-vintage LLM email summaries.
7. **No source gives a validated sample size for a human validation subset of an LLM judge.** Calderon et al. [27] give the statistical test but their concrete minimum-*n* recommendation was not extracted; Unell et al. [35] give a selection method, not a number.
8. **Author-as-rater bias in NLG has no dedicated study.** The nearest evidence is that 71% of papers do not even disclose it [76] and that blinding is unreported in 56% of medical LLM evaluations [77]. There is no measured effect size.
9. **No PII-free email-thread summarisation benchmark exists.** Every human-annotated option is Enron-derived, Avocado-gated, or un-anonymised. The team must either accept a proxy domain, accept the Enron/Avocado provenance, or build a corpus — and no source validates a synthetic email corpus for this task, because none has been published.
10. **The Avocado fee is unknown and Monash's LDC membership status is unverified.** LDC shows "Login for the applicable fee" for LDC2015T03 [95]. Whether Monash's membership tier covers it must be checked with the library.
11. **FERC's own primary release statement could not be read** (the ferc.gov page is Cloudflare-blocked and archive retrieval failed), so the exact terms and any disclaimer attached to the original 2003 release are second-hand via Noever [83].
12. **GDPR's application to research reuse of leaked or court-released personal data is unresolved in the sources located.** No DPA decision, EDPB opinion or CJEU judgment on point was found; EDPB Guidelines 1/2026 [115] are silent on leaked data.
13. **Whether Monash ethics review applies** to the human evaluation and the simulated user study is out of scope for a literature search and is already flagged as fog on map #80.
14. **Several citations could not be fully verified** and are marked in §9 with ⚠. Notably: peer-reviewed venues for Stureborg et al. [19] and Verga et al. [23] (both appear to be arXiv-only); the interior of Zimmer [89]; the SAMSum licence string, verified only from a community mirror because all Samsung-controlled channels return 401 [99]; and MiniCheck's licence, which is inconsistent across repo, model card and the 7B variant [44].

---

## 9. Sources

All URLs accessed **5 August 2026**. ⚠ marks an item whose bibliographic details or content could not be fully verified against a primary source; the specific gap is noted.

### Metric validity

1. Goyal, T., Li, J. J., & Durrett, G. (2023). *News Summarization and Evaluation in the Era of GPT-3*. arXiv:2209.12356 (v1 26 Sep 2022; v2 23 May 2023). DOI 10.48550/arXiv.2209.12356. https://arxiv.org/abs/2209.12356
2. Lin, C.-Y. (2004). *ROUGE: A Package for Automatic Evaluation of Summaries*. In *Text Summarization Branches Out*, pp. 74–81. ACL. Anthology W04-1013. https://aclanthology.org/W04-1013/
3. Google Research. *rouge_score* (Python reference implementation). Apache-2.0; pip package `rouge-score`. https://github.com/google-research/google-research/tree/master/rouge
4. Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). *BERTScore: Evaluating Text Generation with BERT*. ICLR 2020. arXiv:1904.09675. https://arxiv.org/abs/1904.09675 · https://openreview.net/forum?id=SkeHuCVFDr
5. Zhang, T., et al. *bert_score* repository (MIT) and `journal/rescale_baseline.md`. https://github.com/Tiiiger/bert_score · https://github.com/Tiiiger/bert_score/blob/master/journal/rescale_baseline.md
6. Fabbri, A. R., Kryściński, W., McCann, B., Xiong, C., Socher, R., & Radev, D. (2021). *SummEval: Re-evaluating Summarization Evaluation*. *Transactions of the ACL*, 9, 391–409. DOI 10.1162/tacl_a_00373. arXiv:2007.12626. https://aclanthology.org/2021.tacl-1.24/
7. Zhang, S., Celikyilmaz, A., Gao, J., & Bansal, M. (2021). *EmailSum: Abstractive Email Thread Summarization*. ACL-IJCNLP 2021, pp. 6895–6909. Anthology 2021.acl-long.537. arXiv:2107.14691. https://arxiv.org/abs/2107.14691 · https://github.com/ZhangShiyue/EmailSum
8. Deutsch, D., Dror, R., & Roth, D. (2022). *On the Limitations of Reference-Free Evaluations of Generated Text*. EMNLP 2022, pp. 10960–10977. DOI 10.18653/v1/2022.emnlp-main.753. arXiv:2210.12563. https://aclanthology.org/2022.emnlp-main.753/
9. Deutsch, D., Dror, R., & Roth, D. (2021). *A Statistical Analysis of Summarization Evaluation Metrics Using Resampling Methods*. *TACL*, 9, 1132–1146. DOI 10.1162/tacl_a_00417. arXiv:2104.00054.
10. Dai, X., Karimi, S., & Fang, B. (2024). *A Critical Look at Meta-evaluating Summarisation Evaluation Metrics*. Findings of EMNLP 2024. arXiv:2409.19507. https://arxiv.org/abs/2409.19507
11. van Schaik, T. A., & Pugh, B. (2024). *A Field Guide to Automatic Evaluation of LLM-Generated Summaries*. SIGIR 2024. DOI 10.1145/3626772.3661346. https://doi.org/10.1145/3626772.3661346 ⚠ ACM DL returned 403; page range not verified.
12. Nguyen, H., Chen, H., Pobbathi, L., & Ding, J. (2024). *A Comparative Study of Quality Evaluation Methods for Text Summarization*. arXiv:2407.00747. https://arxiv.org/abs/2407.00747 ⚠ listed as under EMNLP 2024 review; final venue unverified.
13. Liu, H., Brahma, D., & Henao, R. (2026). *Calibrating Model-Based Evaluation Metrics for Summarization*. arXiv:2604.17200 (19 Apr 2026). https://arxiv.org/abs/2604.17200 ⚠ preprint; no venue listed.
14. Ramnath, S., Chitsazan, N., Zhou, M., Lee, C.-H., Zhang, S.-X., Rawls, S., Sahu, S., Cho, S., Ren, X., Winata, G. I., & Veldanda, A. K. (2026). *DIAL-SUMMER: A Structured Evaluation Framework of Hierarchical Errors in Dialogue Summaries*. arXiv:2602.08149 (8 Feb 2026). https://arxiv.org/abs/2602.08149 ⚠ preprint; no venue listed.

### LLM-as-judge and reference-free evaluation

15. Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., & Zhu, C. (2023). *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment*. EMNLP 2023, pp. 2511–2522. DOI 10.18653/v1/2023.emnlp-main.153. arXiv:2303.16634. https://aclanthology.org/2023.emnlp-main.153/
16. Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., & Stoica, I. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. NeurIPS 2023 Datasets & Benchmarks. arXiv:2306.05685. https://arxiv.org/abs/2306.05685
17. Wang, P., Li, L., Chen, L., Cai, Z., Zhu, D., Lin, B., Cao, Y., Kong, L., Liu, Q., Liu, T., & Sui, Z. (2024). *Large Language Models are not Fair Evaluators*. ACL 2024, pp. 9440–9450. DOI 10.18653/v1/2024.acl-long.511. arXiv:2305.17926. https://aclanthology.org/2024.acl-long.511/
18. Panickssery, A., Bowman, S. R., & Feng, S. (2024). *LLM Evaluators Recognize and Favor Their Own Generations*. NeurIPS 2024. arXiv:2404.13076. https://arxiv.org/abs/2404.13076
19. Stureborg, R., Alikaniotis, D., & Suhara, Y. (2024). *Large Language Models are Inconsistent and Biased Evaluators*. arXiv:2405.01724. https://arxiv.org/abs/2405.01724 ⚠ no peer-reviewed venue located.
20. Chiang, C.-H., & Lee, H.-y. (2023). *Can Large Language Models Be an Alternative to Human Evaluations?* ACL 2023, pp. 15607–15631. DOI 10.18653/v1/2023.acl-long.870. arXiv:2305.01937. https://aclanthology.org/2023.acl-long.870/
21. Bavaresco, A., Bernardi, R., Bertolazzi, L., Elliott, D., Fernández, R., Gatt, A., Ghaleb, E., Giulianelli, M., Hanna, M., Koller, A., Martins, A. F. T., Mondorf, P., Neplenbroek, V., Pezzelle, S., Plank, B., Schlangen, D., Suglia, A., Surikuchi, A. K., Takmaz, E., & Testoni, A. (2025). *LLMs instead of Human Judges? A Large Scale Empirical Study across 20 NLP Evaluation Tasks*. ACL 2025 (Short Papers). arXiv:2406.18403. https://arxiv.org/abs/2406.18403 ⚠ anthology ID 2025.acl-short.20 obtained via search, not direct fetch.
22. Kim, S., Suk, J., Longpre, S., Lin, B. Y., Shin, J., Welleck, S., Neubig, G., Lee, M., Lee, K., & Seo, M. (2024). *Prometheus 2: An Open Source Language Model Specialized in Evaluating Other Language Models*. EMNLP 2024. arXiv:2405.01535. https://arxiv.org/abs/2405.01535 · weights: https://huggingface.co/prometheus-eval
23. Verga, P., Hofstatter, S., Althammer, S., Su, Y., Piktus, A., Arkhangorodsky, A., Xu, M., White, N., & Lewis, P. (2024). *Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models*. arXiv:2404.18796. https://arxiv.org/abs/2404.18796 ⚠ no peer-reviewed venue located.
24. Hashemi, H., Eisner, J., Rosset, C., Van Durme, B., & Kedzie, C. (2024). *LLM-Rubric: A Multidimensional, Calibrated Approach to Automated Evaluation of Natural Language Texts*. ACL 2024, pp. 13806–13834. arXiv:2501.00274. https://arxiv.org/abs/2501.00274
25. Song, H., Su, H., Shalyminov, I., Cai, J., & Mansour, S. (2024). *FineSurE: Fine-grained Summarization Evaluation using LLMs*. ACL 2024, pp. 906–922. DOI 10.18653/v1/2024.acl-long.51. arXiv:2407.00908. https://aclanthology.org/2024.acl-long.51/ · https://github.com/DISL-Lab/FineSurE-ACL24
26. Thakur, A. S., Choudhary, K., Ramayapally, V. S., Vaidyanathan, S., & Hupkes, D. (2025). *Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges*. GEM 2025, pp. 404–430. arXiv:2406.12624.
27. Calderon, N., Reichart, R., & Dror, R. (2025). *The Alternative Annotator Test for LLM-as-a-Judge: How to Statistically Justify Replacing Human Annotators with LLMs*. ACL 2025, pp. 16051–16081. DOI 10.18653/v1/2025.acl-long.782.
28. Haldar, R., & Hockenmaier, J. (2025). *Rating Roulette: Self-Inconsistency in LLM-As-A-Judge Frameworks*. Findings of EMNLP 2025, pp. 24986–25004. DOI 10.18653/v1/2025.findings-emnlp.1361. ⚠ concrete inconsistency numbers not extracted from the PDF.
29. Norman, J. D., Rivera, M. U., & Hughes, D. A. (2026). *Reliability without Validity: A Systematic, Large-Scale Evaluation of LLM-as-a-Judge Models Across Agreement, Consistency, and Bias*. arXiv:2606.19544 (17 Jun 2026). https://arxiv.org/abs/2606.19544 ⚠ preprint.
30. Dietz, L., Zendel, O., Bailey, P., Clarke, C. L. A., Cotterill, E., Dalton, J., Hasibi, F., Sanderson, M., & Craswell, N. (2025). *Principles and Guidelines for the Use of LLM Judges*. ICTIR '25, Padua, Italy. ACM, 12 pp. ISBN 979-8-4007-1861-8. DOI 10.1145/3731120.3744588. Author copy: https://www.cs.unh.edu/~dietz/papers/dietz2025principles.pdf ⚠ ACM DL returned 403; details taken from the CC BY-SA authors' PDF.
31. Rao, D., & Callison-Burch, C. (2026). *Agreement Metrics for LLM-as-Judge Evaluation: What to Report and Why*. arXiv:2606.00093 (v1 25 May 2026; v2 31 Jul 2026). https://arxiv.org/abs/2606.00093 ⚠ preprint.
32. Yamauchi, Y., Yano, T., & Oyamada, M. (2025). *An Empirical Study of LLM-as-a-Judge: How Design Choices Impact Evaluation Reliability*. arXiv:2506.13639. https://arxiv.org/abs/2506.13639 ⚠ preprint.
33. Gu, J., Jiang, X., Shi, Z., Tan, H., Zhai, X., Xu, C., Li, W., Shen, Y., Ma, S., Liu, H., Wang, S., Zhang, K., Wang, Y., Gao, W., Ni, L., & Guo, J. (2024/2025). *A Survey on LLM-as-a-Judge*. arXiv:2411.15594 (v6, 19 Oct 2025). https://arxiv.org/abs/2411.15594 ⚠ preprint. See also Li, H., et al. (2024). *LLMs-as-Judges: A Comprehensive Survey on LLM-based Evaluation Methods*. arXiv:2412.05579.
34. Evaluation tooling (official repositories/docs): **DeepEval** (Apache-2.0) https://github.com/confident-ai/deepeval · **OpenAI Evals** (MIT) https://github.com/openai/evals · **Hugging Face `evaluate`** (Apache-2.0) https://huggingface.co/docs/evaluate ⚠ current version numbers not pinned.
35. Unell, A., Dullerud, N., Boneh, N., Jagadeesan, M., Hashimoto, T., Shah, N., & Koyejo, S. (2026). *Metric Match: A Subset Selection Approach to Evaluating LLM Judge Reliability*. arXiv:2606.15029 (12 Jun 2026). https://arxiv.org/abs/2606.15029 ⚠ preprint.

### Hallucination and faithfulness

36. Maynez, J., Narayan, S., Bohnet, B., & McDonald, R. (2020). *On Faithfulness and Factuality in Abstractive Summarization*. ACL 2020, pp. 1906–1919. DOI 10.18653/v1/2020.acl-main.173. arXiv:2005.00661. https://aclanthology.org/2020.acl-main.173/
37. Kryściński, W., McCann, B., Xiong, C., & Socher, R. (2020). *Evaluating the Factual Consistency of Abstractive Text Summarization*. EMNLP 2020. arXiv:1910.12840. https://github.com/salesforce/factCC (BSD-3-Clause)
38. Wang, A., Cho, K., & Lewis, M. (2020). *Asking and Answering Questions to Evaluate the Factual Consistency of Summaries*. ACL 2020. arXiv:2004.04228. https://arxiv.org/abs/2004.04228
39. Durmus, E., He, H., & Diab, M. (2020). *FEQA: A Question Answering Evaluation Framework for Faithfulness Assessment in Abstractive Summarization*. ACL 2020. arXiv:2005.03754. ⚠ own correlation table not extracted; SummaC reports FEQA at 58.7% balanced accuracy.
40. Fabbri, A. R., Wu, C.-S., Liu, W., & Xiong, C. (2022). *QAFactEval: Improved QA-Based Factual Consistency Evaluation for Summarization*. NAACL 2022. arXiv:2112.08542. ⚠ code repository not confirmed.
41. Laban, P., Schnabel, T., Bennett, P. N., & Hearst, M. A. (2022). *SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization*. *TACL* 2022. arXiv:2111.09525. https://github.com/tingofurro/summac (Apache-2.0)
42. Honovich, O., Aharoni, R., Herzig, J., Taitelbaum, H., Kukliansy, D., Cohen, V., Scialom, T., Szpektor, I., Hassidim, A., & Matias, Y. (2022). *TRUE: Re-evaluating Factual Consistency Evaluation*. NAACL 2022. arXiv:2204.04991.
43. Tang, L., Goyal, T., Fabbri, A. R., Laban, P., Xu, J., Yavuz, S., Kryściński, W., Rousseau, J. F., & Durrett, G. (2023). *Understanding Factual Errors in Summarization: Errors, Summarizers, Datasets, Error Detectors* (AggreFact). ACL 2023. arXiv:2205.12854.
44. Tang, L., Laban, P., & Durrett, G. (2024). *MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents*. EMNLP 2024. arXiv:2404.10774. https://github.com/Liyan06/MiniCheck · benchmark: https://huggingface.co/datasets/lytang/LLM-AggreFact (CC-BY-ND-4.0) ⚠ licence inconsistent across repo (Apache-2.0), FT5 model card (MIT), and Bespoke-MiniCheck-7B (CC BY-NC 4.0).
45. Min, S., Krishna, K., Lyu, X., Lewis, M., Yih, W.-t., Koh, P. W., Iyyer, M., Zettlemoyer, L., & Hajishirzi, H. (2023). *FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation*. EMNLP 2023. arXiv:2305.14251.
46. Manakul, P., Liusie, A., & Gales, M. J. F. (2023). *SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models*. EMNLP 2023. arXiv:2303.08896. https://github.com/potsawee/selfcheckgpt (MIT)
47. Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). *Ragas: Automated Evaluation of Retrieval Augmented Generation*. arXiv:2309.15217. Docs: https://docs.ragas.io · code: https://github.com/explodinggradients/ragas (Apache-2.0) ⚠ EACL 2024 demo venue not confirmed from a primary source.
48. Vectara. *HHEM-2.1-Open* model card. https://huggingface.co/vectara/hallucination_evaluation_model (Apache-2.0; base google/flan-t5-base)
49. Vectara. *Hallucination Leaderboard*. https://github.com/vectara/hallucination-leaderboard (Apache-2.0; last updated 11 May 2026)
50. Li, J., Cheng, X., Zhao, W. X., Nie, J.-Y., & Wen, J.-R. (2023). *HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models*. EMNLP 2023. arXiv:2305.11747.
51. Niu, C., Wu, Y., Zhu, J., Xu, S., Shum, K., Zhong, R., Song, J., & Zhang, T. (2024). *RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models*. arXiv:2401.00396.
52. Bao, F. S., Li, M., Qu, R., Luo, G., Wan, E., Tang, Y., Fan, W., Tamber, M. S., Kazi, S., Sourabh, V., Qi, M., Tu, R., Xu, C., Gonzales, M., Mendelevitch, O., & Ahmad, A. (2025). *FaithBench: A Diverse Hallucination Benchmark for Summarization by Modern LLMs*. NAACL 2025 (Short Papers), pp. 448–461. DOI 10.18653/v1/2025.naacl-short.38. arXiv:2410.13210.
53. Dhuliawala, S., Komeili, M., Xu, J., Raileanu, R., Li, X., Celikyilmaz, A., & Weston, J. (2023). *Chain-of-Verification Reduces Hallucination in Large Language Models*. arXiv:2309.11495.
54. Shuster, K., Poff, S., Chen, M., Kiela, D., & Weston, J. (2021). *Retrieval Augmentation Reduces Hallucination in Conversation*. arXiv:2104.07567.
55. Kalai, A. T., Nachum, O., Vempala, S. S., & Zhang, E. (2025). *Why Language Models Hallucinate*. arXiv:2509.04664.
56. Fan, D., Delsad, S., Flammarion, N., & Andriushchenko, M. (2026). *HalluHard: A Hard Multi-Turn Hallucination Benchmark*. arXiv:2602.01031 (1 Feb 2026). ⚠ preprint.

### Statistics and experimental design

57. Dror, R., Baumer, G., Shlomov, S., & Reichart, R. (2018). *The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing*. ACL 2018, pp. 1383–1392. DOI 10.18653/v1/P18-1128. https://aclanthology.org/P18-1128/ ⚠ the test-selection protocol is paraphrased from a poorly-extracting PDF; verify the exact decision table before quoting.
58. Brown, L. D., Cai, T. T., & DasGupta, A. (2001). *Interval Estimation for a Binomial Proportion*. *Statistical Science*, 16(2), 101–133. DOI 10.1214/ss/1009213286. https://projecteuclid.org/journals/statistical-science/volume-16/issue-2/Interval-Estimation-for-a-Binomial-Proportion/10.1214/ss/1009213286.full
59. Card, D., Henderson, P., Khandelwal, U., Jia, R., Mahowald, K., & Jurafsky, D. (2020). *With Little Power Comes Great Responsibility*. EMNLP 2020, pp. 9263–9274. arXiv:2010.06595. https://aclanthology.org/2020.emnlp-main.745/ · notebooks: https://github.com/dallascard/NLP-power-analysis

### Human evaluation

60. Howcroft, D. M., Belz, A., Clinciu, M.-A., Gkatzia, D., Hasan, S. A., Mahamood, S., Mille, S., van Miltenburg, E., Santhanam, S., & Rieser, V. (2020). *Twenty Years of Confusion in Human Evaluation: NLG Needs Evaluation Sheets and Standardised Definitions*. INLG 2020, pp. 169–182. DOI 10.18653/v1/2020.inlg-1.23. https://aclanthology.org/2020.inlg-1.23/ ⚠ the paper is internally inconsistent ("more than half" in §5 vs "about two-thirds" in the conclusion); cite the unambiguous 279/478 = 58% figure.
61. van der Lee, C., Gatt, A., van Miltenburg, E., Wubben, S., & Krahmer, E. (2019). *Best practices for the human evaluation of automatically generated text*. INLG 2019, pp. 355–368. https://aclanthology.org/W19-8643/
62. van der Lee, C., Gatt, A., van Miltenburg, E., & Krahmer, E. (2021). *Human evaluation of automatically generated text: Current trends and best practice guidelines*. *Computer Speech & Language*, 67, 101151. DOI 10.1016/j.csl.2020.101151
63. Belz, A., Mille, S., & Howcroft, D. M. (2020). *Disentangling the Properties of Human Evaluation Methods*. INLG 2020, pp. 183–194. https://aclanthology.org/2020.inlg-1.24/
64. Shimorina, A., & Belz, A. (2022). *The Human Evaluation Datasheet: A Template for Recording Details of Human Evaluation Experiments in NLP*. HumEval @ ACL 2022. arXiv:2103.09710. Scripts: https://github.com/Shimorina/human-evaluation-datasheet
65. Amidei, J., Piwek, P., & Willis, A. (2018). *Rethinking the Agreement in Human Evaluation Tasks*. COLING 2018, pp. 3318–3329. https://aclanthology.org/C18-1281/
66. Amidei, J., Piwek, P., & Willis, A. (2019). *Agreement is overrated: A plea for correlation to assess human evaluation reliability*. INLG 2019, pp. 344–354. https://aclanthology.org/W19-8642/
67. Cohen, J. (1960). *A coefficient of agreement for nominal scales*. *Educational and Psychological Measurement*, 20(1), 37–46. DOI 10.1177/001316446002000104
68. Fleiss, J. L. (1971). *Measuring nominal scale agreement among many raters*. *Psychological Bulletin*, 76(5), 378–382. DOI 10.1037/h0031619
69. Krippendorff, K. (2011). *Computing Krippendorff's Alpha-Reliability*. Departmental Papers (ASC), University of Pennsylvania. https://repository.upenn.edu/asc_papers/43 — **cite for computation only; it does not contain the .800/.667 thresholds.**
70. Krippendorff, K. (2004). *Reliability in content analysis: Some common misconceptions and recommendations*. *Human Communication Research*, 30(3), 411–433. DOI 10.1111/j.1468-2958.2004.tb00738.x; and *Content Analysis: An Introduction to Its Methodology* (2nd ed.), pp. 241–242 — **cite for the thresholds.**
71. Landis, J. R., & Koch, G. G. (1977). *The measurement of observer agreement for categorical data*. *Biometrics*, 33(1), 159–174. PMID 843571. ⚠ the "arbitrary benchmarks" framing is confirmed via secondary reproduction ([65], [72]); the paywalled original was not read.
72. Artstein, R., & Poesio, M. (2008). *Survey Article: Inter-Coder Agreement for Computational Linguistics*. *Computational Linguistics*, 34(4), 555–596. DOI 10.1162/coli.07-034-R2
73. Feinstein, A. R., & Cicchetti, D. V. (1990). *High agreement but low kappa: I. The problems of two paradoxes*. *Journal of Clinical Epidemiology*, 43(6), 543–549. DOI 10.1016/0895-4356(90)90158-L. (Companion: Cicchetti & Feinstein, ibid., 551–558.)
74. Byrt, T., Bishop, J., & Carlin, J. B. (1993). *Bias, prevalence and kappa*. *Journal of Clinical Epidemiology*, 46(5), 423–429. DOI 10.1016/0895-4356(93)90018-V
75. Clark, E., August, T., Serrano, S., Haduong, N., Gururangan, S., & Smith, N. A. (2021). *All That's 'Human' Is Not Gold: Evaluating Human Evaluation of Generated Text*. ACL-IJCNLP 2021, pp. 7282–7296. arXiv:2107.00061. https://aclanthology.org/2021.acl-long.565/
76. Mei, K. X., Hsu, Y.-L., Choi, M., Cao, Z., Xu, C., Wen, B., Blodgett, S. L., & Wang, L. L. (2026). *Illusions of the Gold Standard: A Large-scale Analysis of Human Evaluation Protocols for Long-form Text Generation*. ACL 2026 Main. arXiv:2606.07936.
77. Tam, T. Y. C., Sivarajkumar, S., Kapoor, S., et al. (2024). *A framework for human evaluation of large language models in healthcare derived from literature review*. *npj Digital Medicine*, 7, 258. DOI 10.1038/s41746-024-01258-7. arXiv:2405.02559.
78. Kunilovskaya, M., Bhatia, G., et al. (2026). *Who Annotates in NLP? A Large-scale Assessment of Human Annotation Reporting between 2018 and 2025*. arXiv:2606.02255. ⚠ per-item percentages not extracted from the full text.
79. James, J. (2026). *Counting on Consensus: Selecting the Right Inter-annotator Agreement Metric for NLP Annotation and Evaluation*. LREC 2026. arXiv:2603.06865. ⚠ summarised from the PDF, not verbatim-quoted.

### Datasets, licensing and privacy law

80. Klimt, B., & Yang, Y. (2004). *The Enron Corpus: A New Dataset for Email Classification Research*. In *Machine Learning: ECML 2004*, LNCS 3201, Springer, pp. 217–226. DOI 10.1007/978-3-540-30115-8_22. (A companion version was presented at CEAS 2004.)
81. Cohen, W. W. *Enron Email Dataset* (distribution page; May 7 2015 version, ~1.7 GB). Carnegie Mellon University. https://www.cs.cmu.edu/~enron/ — **no licence or terms of use stated.**
82. EDRM / Nuix (15 May 2013). *Nuix and EDRM republish Enron data set cleansed of more than 10,000 items containing private, health and financial information* (press release). Also Business Wire 20130515006369. ⚠ the referenced Nuix methodology whitepaper at `nuix.com/enron` is dead and no archive copy was retrievable; cite the press release only. The release reports **no** finding of resumes.
83. Noever, D. (2020). *The Enron Corpus: Where the Email Bodies are Buried?* arXiv:2001.10374. ⚠ arXiv preprint, not peer-reviewed.
84. Gao, L., Biderman, S., Black, S., et al. (2021). *The Pile: An 800GB Dataset of Diverse Text for Language Modeling*. arXiv:2101.00027, §6.5.
85. Levendowski, A. (2018). *How Copyright Law Can Fix Artificial Intelligence's Implicit Bias Problem*. *Washington Law Review*, 93, 579, at 610–612.
86. Mohammad, S. M., & Yang, T. (W.) (2011). *Tracking Sentiment in Mail: How Genders Differ on Emotional Axes*. WASSA 2011, pp. 70–79. Anthology W11-1709.
87. Sayed, M. F., Cox, W., Rivera, J. L., Christian-Lamb, C., Iqbal, M., Oard, D. W., & Shilton, K. (2020). *A Test Collection for Relevance and Sensitivity*. SIGIR '20. DOI 10.1145/3397271.3401284.
88. McKechnie, J., McDonald, G., & Macdonald, C. (2026). *A Sensitivity-Aware Test Collection for Search Among Personal Information*. SIGIR '26. DOI 10.1145/3805712.3808619. arXiv:2606.27559.
89. Zimmer, Z. (2026). *Outlier and collapse: The Enron corpus and foundation model training data*. *Big Data & Society*, 13(1). DOI 10.1177/20539517261421474. ⚠ publisher blocked; metadata and abstract verified via Crossref/OpenAlex/DOAJ, full text unread — do not quote its interior.
90. Huang, J., Shao, H., & Chang, K. C.-C. (2022). *Are Large Pre-Trained Language Models Leaking Your Personal Information?* Findings of EMNLP 2022, pp. 2038–2047. DOI 10.18653/v1/2022.findings-emnlp.148. arXiv:2205.12628.
91. 99% Invisible (9 Nov 2020). *You've Got Enron Mail!* (episode transcript; contains on-record remarks by Pat Wood III, FERC Chairman at the time of the release). https://99percentinvisible.org/episode/youve-got-enron-mail/ — journalism, not scholarship.
92. Ball, C. (15 Aug 2025). *Still on Dial-Up: Why It's Time to Retire the Enron Email Corpus*. EDRM. ⚠ contains no PII counts; the argument is primarily technical obsolescence.
93. Zhang, R., & Tetreault, J. (2019). *This Email Could Save Your Life: Introducing the Task of Email Subject Line Generation* (AESLC). ACL 2019, pp. 446–456. DOI 10.18653/v1/P19-1043. arXiv:1906.03497. https://github.com/ryanzhumich/AESLC (repo `LICENSE.md` = CC BY-NC-SA 4.0) ⚠ the HuggingFace card `Yale-LILY/aeslc` declares `license: unknown`, contradicting upstream.
94. *(reserved — EmailSum is cited at [7])*
95. Oard, D., Webber, W., Kirsch, D. A., & Golitsynskiy, S. (2015). *Avocado Research Email Collection*. LDC2015T03. DOI 10.35111/wqt6-jg60. ISBN 1-58563-704-1. https://catalog.ldc.upenn.edu/LDC2015T03 ⚠ fee is login-gated; no public price obtained; Monash membership coverage unverified.
96. Shay, M., Davidson, R., & Grinberg, N. (2024). *EnronSR: A Benchmark for Evaluating AI-Generated Email Replies*. ICWSM 2024, 18, 2063–2075. DOI 10.1609/icwsm.v18i1.31448. Data: https://doi.org/10.7910/DVN/RQBWAC (CC BY-NC-SA 4.0)
97. Ulrich, J., Murray, G., & Carenini, G. (2008). *A Publicly Available Annotated Corpus for Supervised Email Summarization* (BC3). AAAI 2008 EMAIL Workshop. Download form: https://www.cs.ubc.ca/labs/lci/bc3/download.html (corpus CC BY-SA 3.0; framework MIT) ⚠ the landing page 404s; the download form is live.
98. TREC Enterprise Track. *W3C corpus*. https://ir.nist.gov/w3c/ — **no licence stated**; the page says only that the mailing lists "are public and no usage agreement is necessary to obtain them."
99. Gliwa, B., Mochol, I., Biesek, M., & Wawer, A. (2019). *SAMSum Corpus: A Human-annotated Dialogue Dataset for Abstractive Summarization*. 2nd Workshop on New Frontiers in Summarization @ EMNLP-IJCNLP 2019, pp. 70–79. DOI 10.18653/v1/D19-5409. arXiv:1911.12237. ⚠ the CC BY-NC-ND 4.0 string was read from a community mirror; all Samsung-controlled channels return HTTP 401 and ELRA has no entry.
100. Chen, Y., Liu, Y., Chen, L., & Zhang, Y. (2021). *DialogSum: A Real-Life Scenario Dialogue Summarization Dataset*. Findings of ACL-IJCNLP 2021, pp. 5062–5074. arXiv:2105.06762. ⚠ licence stated in the README only (CC BY-NC-SA 4.0); no LICENSE file in the repo.
101. Zhong, M., et al. (2021). *QMSum: A New Benchmark for Query-based Multi-domain Meeting Summarization*. NAACL 2021. arXiv:2104.05938. (Repo MIT; underlying meetings separately licensed.)
102. Carletta, J., et al. *AMI Meeting Corpus*. https://groups.inf.ed.ac.uk/ami/corpus/ — CC BY 4.0; consent form and ethics annex published. ⚠ the 138/33/171 meeting breakdown is a count of distinct meeting IDs from the official manifest; the site itself says only "around two-thirds".
103. Janin, A., et al. *ICSI Meeting Corpus*. LDC2004S02 / LDC2004T04 (fee-gated) and free under CC BY 4.0 at https://groups.inf.ed.ac.uk/ami/icsi/
104. Argilla. *FinePersonas-Synthetic-Email-Conversations* (`license: llama3.1`) and *FinePersonas-Conversations-Email-Summaries* (`license: other` / `license_name: qwen`). https://huggingface.co/datasets/argilla
105. NVIDIA. *Nemotron-PII* (200,000 rows) and *Nemotron-Personas-USA* (~6M personas), both **CC BY 4.0**. https://huggingface.co/datasets/nvidia/Nemotron-PII · https://huggingface.co/datasets/nvidia/Nemotron-Personas-USA
106. Liu, R., Wei, J., Liu, F., Si, C., Zhang, Y., Rao, J., Zheng, S., Peng, D., Yang, D., Zhou, D., & Dai, A. M. (2024). *Best Practices and Lessons Learned on Synthetic Data*. COLM 2024. arXiv:2404.07503.
107. Kambhatla, G., Shaib, C., & Govindarajan, V. (2025). *Measuring Lexical Diversity of Synthetic Data Generated through Fine-Grained Persona Prompting*. Findings of EMNLP 2025. arXiv:2505.17390.
108. Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., & Gal, Y. (2024). *AI models collapse when trained on recursively generated data*. *Nature*, 631(8022), 755–759. **DOI 10.1038/s41586-024-07566-y**. (Critique: Borji, A. (2024). *A Note on Shumailov et al. (2024)*. arXiv:2410.12954.) — **scope: training, not evaluation.**
109. Xu, C., Guan, S., Greene, D., & Kechadi, M-T. (2024). *Benchmark Data Contamination of Large Language Models: A Survey*. arXiv:2406.04244. ⚠ preprint.
110. Gill, A., Ravichander, A., & Marasović, A. (2025). *What Has Been Lost with Synthetic Evaluation?* arXiv:2505.22830. ⚠ v3 marked "Camera Ready"; venue not named on arXiv.
111. Wang, S., Maddi, A., Lin, Z., & Fanti, G. (2026). *SynAE: A Framework for Measuring the Quality of Synthetic Data for Tool-Calling Agent Evaluations*. arXiv:2605.22564. ⚠ preprint.
112. Wataoka, K., Takahashi, T., & Ri, R. (2024). *Self-Preference Bias in LLM-as-a-Judge*. NeurIPS 2024 Safe Generative AI Workshop. arXiv:2410.21819.
113. Office of the Australian Information Commissioner. *What is personal information?* and *Australian Privacy Principles Guidelines*, Chapter B (Key concepts), v1.4, December 2022, ¶B.29 and ¶B.82. https://www.oaic.gov.au/privacy/australian-privacy-principles/australian-privacy-principles-guidelines
114. National Health and Medical Research Council (2025). *National Statement on Ethical Conduct in Human Research*, ¶2.3.10. https://www.nhmrc.gov.au/about-us/publications/national-statement-ethical-conduct-human-research
115. European Data Protection Board (adopted 15 April 2026). *Guidelines 1/2026 on processing of personal data for scientific research purposes*, ¶¶98–99. — **silent on leaked or court-released data.**
116. Google. *Gemini API Additional Terms of Service*, effective 23 March 2026. https://ai.google.dev/gemini-api/terms
117. Google. *Gemini API pricing*. Last updated 30 July 2026. https://ai.google.dev/gemini-api/docs/pricing

### Domain precedent

118. Chen, M. X., Lee, B. N., Bansal, G., Cao, Y., Zhang, S., Lu, J., Tsay, J., Wang, Y., Dai, A. M., Chen, Z., Sohn, T., & Wu, Y. (2019). *Gmail Smart Compose: Real-Time Assisted Writing*. KDD 2019. arXiv:1906.00080. https://arxiv.org/abs/1906.00080
119. Kannan, A., Kurach, K., Ravi, S., Kaufmann, T., Tomkins, A., Miklos, B., Corrado, G., Lukacs, L., Ganea, M., Young, P., & Ramavajjala, V. (2016). *Smart Reply: Automated Response Suggestion for Email*. KDD 2016. arXiv:1606.04870. — **no data released.**
