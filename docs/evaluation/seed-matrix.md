# Benchmark corpus — seed matrix

**Status:** draft for review · **Owner:** GR · **Feeds:** [#104](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/104) · **Decided at:** [#102](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/102)

This document defines the *content design* of the synthetic benchmark corpus. It is step 1 of #104 and needs no API calls: the seeds are written by the team, the prose is rendered by the model, and the ground truth is labelled by humans. Only the middle step involves the model, which is the step least likely to bias the evaluation.

> **File location is provisional.** Repository layout is decided at [#94](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/94); this may move under an `eval/` tree once that lands.

---

## 1. Why a matrix rather than "generate 180 emails"

Asking a model for "180 realistic academic emails" produces a narrow, homogeneous set that flatters whatever is evaluated on it — the central weakness of synthetic data identified in the evaluation research ([#83](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/83)). Enumerating a matrix instead controls diversity **by construction**: every dimension is covered by design, the coverage is auditable, and the corpus is reproducible from the seed file rather than from a prompt someone ran once.

It is also *reportable*. "We defined six dimensions, enumerated 180 seeds, and deliberately allocated a third of the held-out set to adversarial cases" is a methodology. "We asked Gemini for some emails" is not — and the proposal report was marked down precisely for describing tools without justifying method.

## 2. The recipient is fixed

Every message is addressed to **the user**: an academic at an Australian university — lecturer, unit coordinator, and active researcher with HDR students. Fixing the recipient keeps the corpus coherent with the target user in the proposal and means the writing-style profile ([#89](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/89)) has a consistent voice to model.

## 3. Dimensions

### D1 — Sender persona (12)

| Code | Persona |
|---|---|
| `STU-UG` | Undergraduate student, coursework matter |
| `STU-HDR` | HDR/thesis student under supervision |
| `COL-PEER` | Academic colleague, same school |
| `COL-SENIOR` | Head of School, Dean, or equivalent |
| `GOV-CHAIR` | Committee or governance chair |
| `PS-ADMIN` | Professional services — timetabling, finance, HR |
| `EXT-RES` | External research collaborator |
| `EXT-PUB` | Journal editor, conference chair, reviewer coordinator |
| `EXT-IND` | Industry partner or sponsor |
| `SYS-AUTO` | Automated system — LMS, room booking, IT, compliance |
| `SYS-BULK` | Newsletter, mailing list, all-staff broadcast |
| `EXT-COLD` | Vendor or unsolicited outreach |

### D2 — Scenario (14)

`DEADLINE-EXT` extension or deadline request · `MEET-SCHED` scheduling · `GRADE-QUERY` grade or remark dispute · `REF-REQUEST` reference or recommendation · `ETHICS-ACTION` ethics/compliance action required · `REVIEW-INVITE` review or examination invitation with a due date · `BUDGET-APPROVE` procurement or budget sign-off · `ROOM-CHANGE` timetable or venue change · `WELFARE` student welfare concern · `PAPER-REVISE` co-authorship or revision round · `POLICY-FYI` policy or announcement, no action · `IT-OUTAGE` system failure or outage · `EVENT-INVITE` seminar or event invitation · `FOLLOWUP` chase on a previously agreed action

Not every persona × scenario pair is plausible. The generator (§6) only emits pairs from an allow-list, so the corpus stays realistic rather than combinatorially complete.

### D3 — Intended urgency (3)

`U-HIGH` · `U-MED` · `U-LOW`

> **These are seed *intents*, not labels.** Ground truth is the adjudicated human label applied to the *rendered* text (§5). The vocabulary itself is decided at [#88](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/88) — this document deliberately uses neutral tier names so it does not pre-empt that decision. Map them once #88 lands.

### D4 — Thread length (4)

`T1` single message (40%) · `T2` 2–3 messages (30%) · `T3` 4–6 messages (20%) · `T4` 7+ messages (10%)

The distribution is deliberately skewed short — most real inbox items are short — while guaranteeing enough long threads to exercise summarisation (FR-02) and the context-window handling that risk T6 concerns.

### D5 — Register (5)

`R-FORMAL` · `R-SEMI` · `R-CASUAL` · `R-ESL` non-native-English phrasing · `R-TERSE` blunt, minimal, possibly curt

`R-ESL` matters: a large share of any Australian university's correspondence is written by people for whom English is an additional language, and urgency cues are exactly what register variation obscures. Omitting it would make the corpus easier *and* less representative.

### D6 — Context completeness (3)

| Code | Meaning |
|---|---|
| `C-FULL` | Everything needed to reply is in the thread |
| `C-BURIED` | The key detail exists, but in an earlier message, not the latest |
| `C-MISSING` | A detail needed to reply well is absent entirely |

`C-MISSING` is the **hallucination bait**. A correct system asks the user a clarifying question rather than inventing the missing fact — which is exactly the second-pass mitigation the proposal committed to. Without these items, hallucination cannot be measured at all, so NFR-02's "measurable reduction" would have nothing to measure.

## 4. Adversarial cases

At least **one third of the held-out tier** carries an adversarial flag. These are where classifiers actually fail, and they are the direct answer to "synthetic data is too easy".

| Flag | Description |
|---|---|
| `A-POLITE-URGENT` | Softly worded ("whenever you get a chance") but carries a deadline within 24 hours |
| `A-LOUD-TRIVIAL` | Shouty framing ("ACTION REQUIRED") on something genuinely low priority |
| `A-BURIED-DEADLINE` | The only date appears in message 1 of a long thread |
| `A-CONFLICT-DATE` | Two different deadlines stated across the thread; the later message is not the correct one |
| `A-SENIOR-FYI` | Sender is senior, content requires nothing |
| `A-AUTO-URGENT` | Automated notification that genuinely is urgent — ethics approval lapsing, account suspension |
| `A-MID-THREAD-ASK` | The actual request sits in the middle of a long thread, not at the end |
| `A-REPLY-ALL` | Reply-all chain where only one message concerns the user |
| `A-SOCIAL` | Purely social — thanks, congratulations — no action of any kind |
| `A-AMBIGUOUS` | Genuinely defensible as either the top or middle urgency tier |
| `A-ESL-URGENT` | Urgency real but obscured by non-native phrasing |
| `A-INFO-GAP` | Cannot be answered without information absent from the thread (pairs with `C-MISSING`) |

`A-AMBIGUOUS` items are expected to *reduce* measured accuracy, and that is the point: they show where the human ceiling is. Report inter-rater agreement separately for adversarial and non-adversarial items — if humans disagree on a case, the classifier cannot fairly be marked wrong on it.

## 5. Ground truth

1. Two team members label each rendered item independently, blind to the seed's `U-*` intent.
2. Disagreements go to a second adjudication pass. SummEval moved Krippendorff's α from 0.4132 to 0.7127 with exactly this step ([#83](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/83)) — it is the cheapest reliability gain available and costs no API calls.
3. Report α **before and after** adjudication. Both numbers belong in the report.
4. Report **agreement between seeded intent and adjudicated label** as a corpus-validity statistic. Where the generator failed to convey the intended urgency, that is a finding about the corpus, not an error to quietly fix.

Blind labelling is what stops the evaluation being circular: without it, the classifier is graded against its own generator's instruction rather than against what a reader would judge.

## 6. Sampling plan

**180 seeds total — 150 held-out, 30 dev, disjoint.**

| Constraint | Target |
|---|---|
| Urgency intent balance | ~33% each of `U-HIGH` / `U-MED` / `U-LOW` |
| Thread length | 40 / 30 / 20 / 10% across `T1`–`T4` |
| Adversarial share, held-out | ≥ 33% (≈ 50 items) |
| `C-MISSING` share | ≥ 15% (hallucination measurement floor) |
| `R-ESL` share | ≥ 15% |
| Persona coverage | every persona appears ≥ 5 times in held-out |
| Dev tier | same distribution, disjoint seeds, never used for reported numbers |

150 is sized against the statistical power finding, not chosen for roundness: clearing ≥90% draft appropriateness as a *lower bound* needs n ≈ 140 at 95% observed. At n = 50, the 95% Wilson interval does not clear 0.90 even at 92% observed.

> **The balanced urgency split is a measurement choice, not a claim about inboxes.** Real inboxes are heavily skewed toward low priority. Balancing the corpus stops a majority-class baseline scoring well and makes accuracy meaningful — but it means the headline accuracy figure is *not* an estimate of accuracy on a real inbox. Report **per-class precision, recall and F1** alongside any overall figure, and state the skew as a limitation. Whether this stays balanced is ultimately [#92](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/92)'s call; the generator supports either.

Two plausibility constraints shape the sampler and are worth knowing when reading the distributions. Machine senders (`SYS-AUTO`, `SYS-BULK`) are restricted to formal and semi-formal register — an automated compliance notice written in non-native-English phrasing cannot be rendered plausibly. And some scenarios cannot carry some urgencies without self-contradiction: an announcement requiring no action is not "reply today". The urgent-*sounding* but low-priority case is still covered, deliberately, by `A-LOUD-TRIVIAL`.

`generate_seeds.py` expands these dimensions into the seed file deterministically from a fixed random seed, so the corpus can be regenerated identically and the file can be regenerated after review without hand-editing 180 rows.

## 7. Known limitations — state these in the report

- **Synthetic email is easier and less diverse than human-authored mail.** Results are optimistic. The adversarial allocation narrows the gap; it does not close it.
- **Contamination.** Prose rendered by the model family under evaluation may be easier for that family to process. Human seeds and human ground truth mitigate this; they do not eliminate it.
- **No comparability with published baselines.** EmailSum-style numbers cannot be compared against these results. This is a real cost of declining Enron, and it should be named rather than glossed.
- **Single institutional context.** Australian university correspondence only. Generalisation beyond it is unevidenced.

## 8. Production gap (ground rule 7)

A production system would need validation on real mail from consenting users, under ethics approval, with a data-processing agreement or self-hosted inference. Performance measured on this corpus is an **upper bound** on real-world performance, not an estimate of it.
