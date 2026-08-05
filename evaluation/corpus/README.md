# Benchmark corpus — seed matrix

Implements step 1 of #104, under the decision in #102: **team-seeded, model-rendered,
human-labelled**. The content design is human, the prose is generated, and the ground
truth is human. Only the middle step uses a model — the step least likely to bias the
evaluation.

> **Path is provisional.** #94 (repo layout) is undecided. `evaluation/corpus/` is a
> placeholder chosen to be easy to move; don't build tooling that hard-codes it.

## Files

| File | What it is |
|---|---|
| `seed-matrix-v1.csv` | The seed matrix. One row per email/thread to be rendered. |
| `README.md` | This file — schema and protocol. |

## Why seeds and not generated emails

Diversity is controlled **by construction** rather than by hoping a generator is diverse,
and it costs no API calls. A seed is a specification, not prose: it fixes who is writing
to whom, about what, at what length and register, and what the reader is missing.

## Schema

| Column | Values | Notes |
|---|---|---|
| `seed_id` | `S001`… | Stable. Never renumber — labels and summaries reference it. |
| `tier` | `dev` \| `heldout` | ~30 dev, ~150 held-out. **The split is enforced in the harness**; held-out is never used for prompt tuning. |
| `persona_from` | e.g. `student`, `unit_coordinator` | Sender role. |
| `persona_to` | e.g. `student`, `cohort` | Recipient role — the inbox owner is always `persona_to`. |
| `scenario` | free text | The situation, not the prose. One clause. |
| `thread_length` | integer ≥ 1 | Messages in the thread. >1 means the renderer produces a thread. |
| `register` | `formal`, `semi_formal`, `casual`, `terse`, `non_native`, `marketing`, `automated` | Voice of the sender. |
| `context` | `complete`, `missing_prior`, `missing_referent`, `missing_attachment` | What the reader does **not** have. Drives hallucination and summarisation failure. |
| `seeded_intent` | `high` \| `normal` \| `low` | **Provisional pending #88.** The priority the seed is *designed* to elicit. |
| `adversarial` | see below | `none` for ordinary rows. |
| `notes` | free text | The specific hook — what makes this row do its job. |

### `adversarial` values

The rows that earn the corpus its keep. These are where classification and
summarisation actually fail.

| Value | The trap |
|---|---|
| `ambiguous_urgency` | Genuinely unclear priority; two readers may reasonably disagree. |
| `buried_deadline` | The deadline appears only in an **earlier** message of the thread. |
| `polite_urgent` | Softened, courteous language wrapping something genuinely time-critical. |
| `false_urgency` | "ACT NOW" framing on something that does not matter. Marketing, mostly. |
| `resolved_thread` | The ask was already satisfied earlier in the thread; correct action is *none*. |
| `critical_automated` | Machine-generated and easy to filter, but genuinely important. |
| `buried_ask` | A long thread where the actual request is one line in the middle. |
| `non_native_register` | Non-native English phrasing that reads as brusque but is not. |

## ⚠️ `seeded_intent` is **not** ground truth

Ground truth is the **adjudicated human label on the rendered text** (step 3 of #104).
Labelling from the seed would grade the classifier against its own generator's
instruction rather than against what a reader would judge.

`seeded_intent` exists for exactly one purpose: **agreement between seeded intent and
adjudicated human label is a corpus-validity statistic**, reported per #102. It is
nearly free and it is the kind of methodological self-awareness the report is marked on.

## Protocol from here

1. **Extend this matrix to ~180 rows** (~30 dev, ~150 held-out) — see the note below.
2. **Render** (step 2) — batch ~5 seeds per call, ~36 calls.
3. **Label** (step 3) — blocked on #88's vocabulary. Two members label each item
   independently, adjudicate in a second pass, report Krippendorff's α before and after.
   SummEval's second round moved α from 0.4132 to 0.7127 (#83); it is the cheapest
   reliability win available and costs no API calls.
4. **~40 human reference summaries** (step 4) over held-out multi-message threads,
   ten per member. These validate whatever judge #92 selects.
5. **Record** the generation model and date, and the corpus-validity statistics.

## ⚠️ The seeds must stay team-written

#102's defence of this corpus rests on the phrase *team-seeded*. If the seeds are
model-written **and** the prose is model-rendered, the corpus is model-authored end to
end, the "content design is human" argument collapses, and the contamination risk #102
names — generated and evaluated by the same model family — gets materially worse.

The rows already here are **structural coverage**: every `adversarial` archetype worked
through, and the ordinary rows patterned so the rest are quick to write. **Rewrite the
`scenario` and `notes` text against inboxes you have actually seen.** A seed that
describes a real Monash situation is worth more than one that describes a plausible
generic one, and the difference will show up in the rendered prose.
