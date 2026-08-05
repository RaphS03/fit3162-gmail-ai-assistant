# Research: LLM access paths and quotas under a zero-budget constraint

Ticket: [#82](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/82) · Map: [#80](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/80)
All sources fetched **5 August 2026**. Evidence only — this document does not pick a provider.

---

## Question

What are the realistic LLM access paths for this system under a zero-budget constraint, and what does each cost, limit and enable? Specifically: access paths and free-tier quotas; callability from Apps Script `UrlFetchApp` versus a server; structured/JSON-schema output; current context-window sizes (and whether long-thread chunking is still a real constraint); direct audio input versus a dedicated speech-to-text service; non-Google and self-hosted alternatives; and how an API key is held safely in each path.

---

## Summary of findings

1. **A backend is not required for LLM access.** Apps Script's `UrlFetchApp` makes arbitrary HTTPS requests with custom headers and JSON payloads [S9], under the single scope `https://www.googleapis.com/auth/script.external_request` [S9]. Every hosted provider examined (Gemini, Vertex, Anthropic, OpenAI, Groq, OpenRouter, Cloudflare) is a plain HTTPS POST and is therefore reachable directly from an add-on. Google publishes a first-party Gmail add-on sample that does exactly this — Apps Script → `UrlFetchApp.fetch()` → Vertex `:generateContent` → applies Gmail labels [S12]. The backend question is therefore *not* settled by LLM access; it must be settled by other needs (secret custody, quota pooling, runtime limits, evaluation harness).
2. **The headline free-tier quota numbers are no longer published.** Google's rate-limits page states rate limits "can be viewed in Google AI Studio" and lists no per-model RPM/TPM/RPD table [S1]. Only the tier *qualification* rules and spend-based limits are published. **Any RPD figure the team uses for capacity planning must be read off their own AI Studio dashboard for their own project** — do not plan against a number from a blog post.
3. **The Gemini Developer API free tier requires no billing account.** Qualification for the Free tier is "Active project or free trial"; Tier 1 requires "Set up and link an active billing account" [S1]. AI Studio "automatically creates a project and API key for new users" [S13]. Current Flash and Flash-Lite models — and, as the pricing page renders it, Gemini 2.5 Pro — show "Free of charge" input and output on the free tier [S2].
4. **The free tier's price is your data.** Every free-tier row on the pricing page is marked "used to improve our products: **Yes**"; only the paid tier is marked **No** [S2]. This collides directly with NFR-01 / risk P4 (synthetic or anonymised data only) — it is a constraint on *what you may send*, not just a cost line.
5. **Vertex AI is a different product with different economics.** It has no free tier for Gemini [S3][S6], requires a Google Cloud project **with billing enabled** — stated verbatim as a prerequisite of both the Apps Script Vertex advanced service [S11] and the official Gmail add-on sample [S12] — and the $300 Free Trial credit is explicitly restricted: "The $300 credit can't pay for Gemini API in AI Studio costs" and cannot be used for "a generative AI partner model that is offered as a managed API" [S6].
6. **Long-thread chunking (risk T6) is very likely a solved problem.** Gemini 3 models take a **1M-token input context window and up to 64k tokens of output** [S15]. At ~4 characters per token [S16] that is ~4 million characters of input. Semester 1's planned chunking and recursive summarisation are not needed to fit an email thread; the residual constraint is tokens-per-minute rate limiting and cost, not window size.
7. **Structured output is native on every serious path.** Gemini supports JSON-Schema-constrained responses including `enum` for classification [S4]; Claude has `output_config.format` (`json_schema`) plus `strict: true` tool use [S17]; even self-hosted Ollama takes a JSON schema in `format` [S20]. A schema-constrained enum label plausibly makes Semester 1's "hardcoded logic-gate validation layer" redundant as a *format* guard (it does not validate semantic correctness).
8. **Audio can go straight into the model.** Gemini accepts audio natively at **32 tokens per second of audio (1 minute = 1,920 tokens)**, up to **9.5 hours per prompt**, in WAV/MP3/AIFF/AAC/OGG/FLAC, inline base64 under a 20 MB total request or via the free Files API above that [S5][S14]. The dedicated alternative, Cloud Speech-to-Text, has an Always-Free allowance of 60 minutes/month for the V1 API [S6] but sits behind a Cloud billing account.
9. **Non-Google free tiers exist and are real, but small.** Groq publishes explicit free-tier numbers (e.g. `llama-3.3-70b-versatile`: 30 RPM / 1K RPD / 12K TPM / 100K TPD) [S7]. OpenRouter free models: 20 RPM, 50 RPD without purchased credits, 1,000 RPD with ≥10 credits [S8]. Cloudflare Workers AI: 10,000 Neurons/day free [S19]. **OpenAI has no free API tier** — the pricing page shows only paid lanes [S18]. **Anthropic has no free API tier** either; pricing starts at $1/$5 per MTok (Haiku 4.5) [S17].
10. **Self-hosting is technically achievable and organisationally risky for this team.** Ollama runs models locally and exposes an HTTP API on `http://localhost:11434` with JSON-schema structured output [S20]. But `localhost` is unreachable from Google's Apps Script servers — self-hosting a model *forces* the backend decision plus a public endpoint, and gives four part-time students a GPU/ops problem five weeks before a demo.

---

## Comparison table of access paths

| Access path | Billing account required? | Cost | Published quotas | Callable from Apps Script `UrlFetchApp`? | Structured output | Context window | Audio input | Secret handling |
|---|---|---|---|---|---|---|---|---|
| **Gemini Developer API — free tier** (AI Studio key) | **No** — "Active project or free trial" [S1] | $0; "Free of charge" in/out for Flash, Flash-Lite, and (as rendered) 2.5 Pro [S2]. **Prompts used to improve Google products: Yes** [S2] | **Not published** — "viewed in Google AI Studio" [S1] | **Yes** — HTTPS + `x-goog-api-key` header [S13] | Yes: JSON Schema + `enum` [S4] | 1M in / 64k out (Gemini 3) [S15] | Yes, native, 32 tok/s, ≤9.5 h [S5] | Static API key. Google: "Never check API keys into source control"; "Do not hardcode API keys directly in web or mobile apps"; "run a backend proxy server" for client-side apps [S10]. In Apps Script → `PropertiesService` Script Properties, shared among **all users of the script** [S21] |
| **Gemini Developer API — Tier 1+** | **Yes** — "Set up and link an active billing account" [S1]; prepay min $10 [S13] | e.g. Gemini 3.6 Flash $1.50 / $7.50 per 1M tok; 2.5 Flash-Lite $0.10 / $0.40 [S2] | Not published per model [S1]; spend limit $10 per rolling 10 min at Tier 1 [S1] | Yes | Yes | 1M / 64k | Yes | Same as above; prompts **not** used to improve products [S2] |
| **Vertex AI (Agent Platform) via `UrlFetchApp`** | **Yes** — "A Google Cloud project with billing enabled" [S12] | No free tier for Gemini [S3][S6]; e.g. 3.5 Flash $1.50 in / $9.00 out global [S3] | Not extracted; Vertex quotas are per-project Cloud quotas | **Yes** — POST to `https://[LOCATION]-aiplatform.googleapis.com/v1/projects/[PROJECT_ID]/locations/[LOCATION]/publishers/google/models/[MODEL_ID]:generateContent` [S12] | Yes — the Google sample passes a schema constraining output to three sentiment values [S12] | 1M / 64k | Yes | **No static key**: `ScriptApp.getOAuthToken()` mints a short-lived token. Google's own caveat: "for example purposes only… we recommend authenticating using a service account" [S12] |
| **Vertex AI via Apps Script advanced service** | **Yes** — "A Google Cloud project with billing enabled" [S11] | Same as above | Same | N/A — native `VertexAI` object, no `UrlFetchApp` needed [S11] | Yes | 1M / 64k | Yes | OAuth / service account; scope `https://www.googleapis.com/auth/cloud-platform` [S11] |
| **Anthropic Claude API** | Yes (paid only; no free tier) | Haiku 4.5 $1/$5; Sonnet 5 $3/$15 ($2/$10 intro thru 2026-08-31); Opus 5 $5/$25 per MTok [S17] | Tier-based; not fetched | **Yes** — `POST https://api.anthropic.com/v1/messages` with `x-api-key` + `anthropic-version: 2023-06-01` [S17] | Yes — `output_config.format` json_schema; `strict: true` tools [S17] | 1M (Haiku 4.5: 200K) [S17] | **Not listed.** Documented file inputs are PDF, images, text — no audio [S17] | Static API key, same custody problem |
| **OpenAI API** | Yes — **no free tier shown** [S18] | gpt-5-nano $0.05/$0.40; gpt-5.6-sol $5.00/$30.00 per 1M tok [S18] | Not fetched | Yes (HTTPS) | Yes (not verified this session) | Not fetched | Not fetched | Static API key |
| **Groq (free tier)** | Not stated in docs [S7] | $0 within limits | **Yes, published**: `llama-3.3-70b-versatile` 30 RPM / 1K RPD / 12K TPM / 100K TPD; `openai/gpt-oss-120b` 30 / 1K / 8K / 200K; `whisper-large-v3` 20 RPM / 2K RPD [S7] | Yes (HTTPS) | Not verified | Not verified | Yes — Whisper models on free tier [S7] | Static API key |
| **OpenRouter (`:free` models)** | No, for the 50 RPD band | $0 | **Yes**: 20 RPM; 50 RPD (<10 credits purchased all-time), 1,000 RPD (≥10 credits) [S8] | Yes (HTTPS) | Not verified | Model-dependent | Model-dependent | Static API key |
| **Cloudflare Workers AI** | Free plan works | 10,000 Neurons/day free, then requests fail unless on Workers Paid ($0.011/1,000 Neurons) [S19] | Neuron-based, published [S19] | Yes (HTTPS) | Not verified | Model-dependent | Not verified | Static API key |
| **Self-hosted (Ollama, student laptop)** | No | $0 (hardware/electricity) | None — bounded by hardware | **No** — API is `http://localhost:11434` [S20], unreachable from Google's servers. Requires a public endpoint ⇒ forces a backend | Yes — JSON schema in `format` [S20] | Model-dependent | Not verified | No API key; the exposure risk moves to the public endpoint |

---

## Per-sub-question findings with evidence

### 1. Access paths and free-tier quotas

**Three distinct Google paths, not one.** Conflating them is the main risk:

- **Gemini Developer API** (`generativelanguage.googleapis.com`), authenticated with an **AI Studio API key**. Tier qualification, verbatim [S1]:
  - Free — "Active project or free trial"
  - Tier 1 — "Set up and link an active billing account"
  - Tier 2 — "Paid $100 + 3 days from first successful payment"
  - Tier 3 — "Paid $1,000 + 30 days from first successful payment"

  AI Studio "automatically creates a project and API key for new users"; upgrading "requires setting up Cloud Billing… and prepay a minimum of $10" [S13]. **No credit card is needed for the free tier.**

- **Vertex AI / Agent Platform** (`{location}-aiplatform.googleapis.com`), authenticated with Google Cloud OAuth/ADC. Both official Google surfaces state the prerequisite verbatim as "**A Google Cloud project with billing enabled**" [S11][S12]. No free tier for Gemini appears on the Vertex pricing page [S3], and Vertex does not appear in the Always-Free monthly usage table [S6].

- **A Workspace-native path does not exist as a distinct billing lane.** What exists is the Apps Script **Vertex AI advanced service** — a native `VertexAI` object that removes the need for `UrlFetchApp` [S11] — but it is Vertex underneath, with the same billing prerequisite. There is no "Gemini included with Workspace for add-on developers" path in any primary source read.

**On the free-tier numbers — this is the single most important caveat in this document.** The rate-limits page no longer contains a per-model Free/Tier-1/Tier-2/Tier-3 RPM/TPM/RPD table. It says rate limits "depend on a variety of factors (such as your usage tier) and can be viewed in Google AI Studio", and directs the reader to "View your active rate limits in AI Studio" [S1]. What *is* published:

| Usage tier | Spend rate limit (rolling 10 min) [S1] |
|---|---|
| Free | N/A |
| Tier 1 | $10 |
| Tier 2 | $200 |
| Tier 3 | $200 |

Widely circulated figures such as "10 RPM / 250,000 TPM / 250 RPD for 2.5 Flash" appear only in **secondary** sources and community forum posts, not in current Google documentation. **They are not cited as fact here.** The team must open AI Studio on the project behind their own key and record the live RPM/TPM/RPD for the exact model they intend to use, then re-check before M11.

**Method for the T3 (quota exhaustion) decision, once the real RPD is known.** Let `E` = emails in the benchmark set, `C` = LLM calls per email (classify + summarise + draft = 3 if not batched), `R` = full suite runs per day during M11. Required requests/day = `E × C × R`. A 200-email suite at 3 calls/email is 600 requests for a *single* run — which is the same order of magnitude as any plausible free-tier RPD. Two independent mitigations are visible in the sources and should be priced into the decision: **batch mode is 50% cheaper on the paid tier** [S2], and **multiple free-tier projects/keys** are limited *per project*, not per key (the rate-limits page frames tiers around projects [S1]).

### 2. Callability from Apps Script `UrlFetchApp` vs a server — "do we need a backend at all?"

`UrlFetchApp` "enables Google Apps Script to communicate with external hosts… through HTTP and HTTPS requests", supports GET/POST/PUT/PATCH/DELETE, JSON payloads via `contentType: 'application/json'`, and custom headers as a key/value map. Requests originate from Google's IP ranges. Required scope: `https://www.googleapis.com/auth/script.external_request` [S9].

**The existence proof is Google's own.** The "Analyze and label Gmail messages with Gemini and Vertex AI" Workspace add-on sample is an Apps Script Gmail add-on that authenticates with `ScriptApp.getOAuthToken()`, calls `UrlFetchApp.fetch()` against the Vertex `:generateContent` endpoint for Gemini 2.5 Flash with a response schema, and labels messages [S12]. That is architecturally the same shape as FR-01 (urgency classification).

**Apps Script platform limits that bound the no-backend design** [S21]:

| Quota | Consumer (gmail.com) | Google Workspace |
|---|---|---|
| URL Fetch calls | 20,000 / day | 100,000 / day |
| URL Fetch response size | 50 MB / call | 50 MB / call |
| URL Fetch POST size | 50 MB / call | 50 MB / call |
| Script runtime | 6 min / execution | 6 min / execution |
| Triggers total runtime | 90 min / day | 6 hr / day |
| Properties read/write | 50,000 / day | 500,000 / day |
| Properties total storage | 500 KB / store | 500 KB / store |

The binding one is **6 minutes per execution**. A synchronous card action that classifies + summarises + drafts in one invocation must complete within 6 minutes; a long-running evaluation loop cannot live in a single Apps Script execution and must be chunked across triggers (90 min/day on consumer accounts, 6 hr/day on Workspace) or moved off-platform. `UrlFetchApp` call volume (20,000/day even on a consumer account) is *not* the constraint — the provider's RPD is.

There is a second, non-Apps-Script way to build a Workspace add-on: **alternate runtimes / HTTP endpoints** [S22], which is where a backend would live if one is adopted. The overview page references an "alternate runtimes" quickstart and a "Build using HTTP endpoints" guide but does not, in the page fetched, state the required hosting product.

**Conclusion for the map:** LLM access does not require a backend. If a backend is adopted it must be justified by one of — secret custody (below), pooling quota across users, escaping the 6-minute execution cap, or hosting the evaluation harness — not by "we need somewhere to call the model from".

### 3. Structured / JSON-schema output

**Gemini.** Structured outputs "enable Gemini models to generate responses adhering to a provided JSON Schema, ensuring type-safe, predictable results" [S4]. The REST shape shown on the page fetched is:

```json
{ "response_format": { "type": "text", "mime_type": "application/json", "schema": { /* JSON Schema */ } } }
```

`enum` is explicitly supported — the docs describe "enum: Lists a specific set of possible strings for classification tasks" and an equivalent for numeric values [S4]. Structured outputs *with tools* is preview and Gemini-3-only [S4].

*Caveat on field names:* the quickstart shows the current REST endpoint as `https://generativelanguage.googleapis.com/v1beta/interactions` and calls the Interactions API "the recommended modern approach" [S13], while the Gmail add-on sample uses the Vertex `:generateContent` endpoint [S12]. The exact request-body field name for the schema therefore differs by endpoint (`response_format` vs the older `generationConfig.responseSchema` / `responseMimeType`). **Verify against the endpoint you actually call before writing the client.**

**Anthropic Claude.** `output_config: {format: {type: "json_schema", schema: {...}}}` on `messages.create()`, with `client.messages.parse()` as the validating helper; separately, `strict: true` on a tool definition guarantees `tool_use.input` validates exactly (schema needs `additionalProperties: false` + `required`). Supported on Fable 5, Opus 5, Opus 4.8, Sonnet 5, Haiku 4.5. Notable limits: no recursive schemas, no numeric or string length constraints, and it is **incompatible with citations** (returns 400). New schemas incur a one-time compilation latency, then a 24-hour cache. If `stop_reason` is `refusal` or `max_tokens`, output may not match the schema [S17].

**Ollama (self-hosted).** "Structured outputs are supported by providing a JSON schema in the `format` parameter" [S20].

**Bearing on the logic-gate validation layer:** a schema-constrained enum removes the class of failure where the model returns prose instead of a label, or an out-of-vocabulary label. It does **not** remove the need to check that the label is *correct*, and on Claude it explicitly does not hold under a refusal or a token cutoff [S17]. Framing the Semester 1 layer as "format validation" makes it redundant; framing it as "semantic guardrail / confidence gate" does not.

### 4. Long context — is chunking (risk T6) still real?

The Gemini 3 developer guide states that "**Gemini 3 models support a 1 million token input context window and up to 64k tokens of output**", with per-model entries reading `1M / 64k` for `gemini-3.1-flash-lite`, `gemini-3.1-pro-preview`, and `gemini-3-flash-preview` (knowledge cutoff Jan 2025); image models are lower (`128k / 32k`, `65k / 32k`) [S15]. A token is "about 4 characters… 100 tokens is equal to about 60-80 English words" [S16].

So 1M tokens ≈ **4 million characters ≈ 600,000–800,000 words** of input. A long Gmail thread is, at the extreme, tens of thousands of words. The long-context guide is explicit about the design consequence: "While these techniques remain valuable in specific scenarios, Gemini's extensive context window invites a more direct approach: providing all relevant information upfront", and it frames RAG/vector databases as no longer necessary for material that fits [S16 / long-context page]. It notes context caching still helps cost when the same context is reused.

**T6 as originally framed (window overflow on long threads) does not survive contact with a 1M-token window.** What *does* survive is a re-pointed version of the same risk: tokens-per-minute rate limiting and per-token cost both scale with how much thread you stuff in, so "send the whole thread" trades a correctness risk for a quota risk. Claude's 1M window (Haiku 4.5: 200K) is comparable [S17].

### 5. Audio input vs a dedicated speech-to-text service

**Gemini native audio** [S5]:
- Accepts audio directly; formats WAV, MP3, AIFF, AAC, OGG Vorbis, FLAC.
- "**32 tokens per second of audio (1 minute = 1,920 tokens)**" [S5], corroborated by the tokens page: "Audio: 32 tokens per second" [S16].
- "**9.5 hours of audio per prompt**".
- Inline base64 for small files — "Maximum request size is 20 MB total (including prompts and all files)"; Files API above that.
- Files API: up to 20 GB per project, 2 GB per file, files stored 48 hours, "available at no cost in all regions where the Gemini API is available" [S14].

Cost implication: a 60-second voice command is ~1,920 input tokens — trivially small, and free on the free tier. Note the Gemini Developer API pricing page prices audio input separately from text on some models (e.g. Gemini 2.5 Flash: $0.30/1M text-image-video vs **$1.00/1M audio**; 3.1 Flash-Lite: $0.25 vs $0.50) [S2] — audio is a distinct, more expensive SKU once you leave the free tier.

**Dedicated STT alternative — Cloud Speech-to-Text.** The Always-Free table row reads: "60 minutes per minute per month per account for the Speech-to-Text V1 API. 60 minutes per minute per month per account for SKU IDs `6649-62EF-CB8F` and `7247-19E1-FB4D`" [S6]. *(The "per minute per month" phrasing is almost certainly a rendering artefact of the fetched page; the substantive allowance is 60 minutes per month per account. Verify before quoting in the report.)* Direct fetches of `cloud.google.com/speech-to-text/pricing` and the V2 pricing page returned truncated or 404 responses this session, so **per-minute rates beyond the free allowance are unverified**.

**The comparison, on the evidence:** direct-to-Gemini removes a whole service, a whole set of credentials, and a whole billing dependency, and is free at the volumes a demo needs; Cloud STT adds a billing account requirement for a 60-minute-per-month allowance. Groq additionally offers Whisper on its free tier (`whisper-large-v3`: 20 RPM / 2K RPD) [S7] as a non-Google STT option.

**Unresolved and material to FR-05:** none of the sources read establishes whether a Gmail **CardService** add-on can capture microphone audio at all. CardService renders declarative cards, not arbitrary browser JavaScript. If the add-on cannot reach `getUserMedia`, the "direct audio vs STT service" comparison is moot because neither can be fed. This needs its own check before FR-05's priority is re-decided.

### 6. Alternatives worth naming

**Non-Google hosted, with a genuine free tier:**
- **Groq** — the only provider examined that still publishes an explicit free-tier table. Selected rows [S7]: `llama-3.3-70b-versatile` 30 RPM / 1K RPD / 12K TPM / 100K TPD; `openai/gpt-oss-120b` 30 / 1K / 8K / 200K; `qwen/qwen3.6-27b` 30 / 1K / 8K / 200K; `llama-3.1-8b-instant` 30 RPM / 14.4K RPD; `whisper-large-v3` 20 RPM / 2K RPD. The docs do not state whether a credit card is required.
- **OpenRouter** — `:free`-suffixed models at 20 RPM, 50 RPD if fewer than 10 credits purchased all-time, 1,000 RPD at ≥10 credits [S8]. The 1,000 RPD band is not zero-budget.
- **Cloudflare Workers AI** — 10,000 Neurons/day free; beyond it "further operations will fail with an error" unless on Workers Paid at $0.011/1,000 Neurons. Three models are paid-plan-only [S19].

**Non-Google hosted, no free tier:**
- **OpenAI** — the pricing page shows only paid lanes (Standard, Batch, Flex, Fast); no free API tier is described. gpt-5-nano $0.05/$0.40 per 1M; gpt-5.6-sol $5.00/$30.00 [S18].
- **Anthropic** — no free tier. Haiku 4.5 $1/$5, Sonnet 5 $3/$15 (introductory $2/$10 through 2026-08-31), Opus 5 $5/$25 per MTok. 1M context on current models, 200K on Haiku 4.5. Strong structured-output support. **No audio input** — documented file inputs are PDF, images and text only [S17].
- **Mistral** — a "Free mode" exists ("lets you create API keys and use included monthly usage within the limits shown on the Limits page") but the documentation **does not publish the numbers**, deferring to the Admin Panel [S23]. Unquantifiable from primary sources; same problem as Gemini's free tier, without Gemini's other advantages.

**Self-hosted open weights:**
- **Ollama** runs open models locally and exposes `POST /api/generate` and `POST /api/chat` on `http://localhost:11434`, with structured output via a JSON schema in `format` [S20]. Honest read for this team: the API surface is fine, the blocker is topological and organisational. `localhost` is not reachable from Google's Apps Script execution servers, so self-hosting **forces** a backend *and* a publicly-addressable, always-on endpoint — precisely the component count the map's standing preference argues against. Add GPU/RAM provisioning, model-quality regression against Gemini 3, and the fact that a laptop must be awake during the 23 Oct demonstration, and the cost lands on four part-time students in the five weeks before a 41%-weighted demo. It is *achievable* (Ollama is a one-command install) but it is not cheap in the currency this project is short of.

### 7. Secret handling per path

**Google's own guidance for Gemini API keys, verbatim** [S10]:
> "Never check API keys into source control systems like Git."
> "Do not hardcode API keys directly in web or mobile apps. Keys compiled in client-side code can be extracted by users."
> "To secure client-side apps, run a backend proxy server to make the actual API calls."

**The nuance that matters for this project:** an Apps Script Gmail add-on is **not** a client-side app in the sense that warning targets. Apps Script executes on Google's servers; a CardService add-on does not ship its source to the user's browser. The "run a backend proxy" recommendation is aimed at web/mobile clients where the key is extractable from shipped code. So the warning does not by itself force a backend here — but it does mean the *only* acceptable place for a static key in an Apps Script project is server-side storage, never a literal in a committed `.gs` file.

**Path-by-path:**

| Path | Credential | Where it lives | Residual risk |
|---|---|---|---|
| Gemini Developer API | Static API key | `PropertiesService.getScriptProperties()` — "Data shared among: All users of a script, add-on, or web app" [S24]. 500 KB per store, 50,000 reads/day consumer [S21] | The store is readable by anything running in the script and by anyone with edit access to the Apps Script project. **The documentation contains no security warning, no encryption claim, and no guidance on storing secrets** [S24] — absence of a warning is not a safety guarantee. One key shared by all add-on users also means one shared quota pool and one leak revoking everyone. |
| Vertex via `UrlFetchApp` | `ScriptApp.getOAuthToken()` — short-lived OAuth token derived from the invoking user's credentials | Nowhere persistent — minted per execution | **No long-lived secret at all**, which is the strongest property of this path. But Google's caveat is explicit: "Calling Vertex AI API using the getOAuthToken method is for example purposes only. To use this add-on outside of personal use, we recommend authenticating using a service account" [S12]. Following that recommendation reintroduces a static secret (a service-account key) in Script Properties. |
| Vertex advanced service | OAuth / service account, scope `https://www.googleapis.com/auth/cloud-platform` [S11] | As above | Same trade-off; the broad `cloud-platform` scope is worth noting on the OAuth consent screen. |
| Anthropic / OpenAI / Groq / OpenRouter / Cloudflare | Static API key (`x-api-key` / `Authorization: Bearer`) | Script Properties, or a backend if one exists | Identical to the Gemini key case. |
| Self-hosted | No provider key | — | Risk moves to securing the public endpoint that Apps Script must reach. |

**Cross-cutting:** a demo running on shared test accounts (per map #80, "the demo runs on test accounts") means the Script Properties store is shared across whoever holds edit access to the project. Key rotation is a manual Properties edit, not a deploy.

---

## What the sources do NOT settle

1. **The actual free-tier RPM/TPM/RPD for any Gemini model.** Google has removed the per-model table from public docs and points to a per-project AI Studio dashboard [S1]. **This is the gating unknown for risk T3 and cannot be resolved from documentation — only by reading the team's own dashboard.** Every widely-quoted number (10 RPM / 250 RPD etc.) traces to secondary sources or forum posts.
2. **Whether free-tier quota is per project or per key**, and therefore whether multiple projects is a legitimate mitigation or a ToS problem. The rate-limits page frames tiers around projects [S1] but no source read states the multiplication rule or its acceptability.
3. **Whether RPD resets at midnight Pacific.** Reported by a search-engine snippet of the rate-limits page, but not present in the page body as fetched. Confirm before building a scheduling strategy around it.
4. **Whether the $300 Cloud Free Trial credit can pay for first-party Vertex AI Gemini calls.** The page excludes "Gemini API in AI Studio costs" and "generative AI partner model[s]… offered as a managed API" [S6]. First-party Vertex Gemini is not named in either exclusion — but it is not affirmatively included either, and Vertex is absent from the Always-Free table. **Do not assume the credit covers it.**
5. **Whether Monash provides any GCP/Azure/OpenAI credit to FIT3162 students.** Not investigated; no primary source. Worth one email to the unit coordinator — it could change the whole shape of this decision.
6. **Exact per-minute Cloud Speech-to-Text rates beyond the free allowance.** `cloud.google.com/speech-to-text/pricing` returned truncated content and the V2 pricing path 404'd this session.
7. **The precise wording/units of the Speech-to-Text free-tier row.** The fetched rendering ("60 minutes per minute per month per account") appears corrupted [S6].
8. **Exact per-model context windows for Gemini 3.6 Flash and 3.5 Flash.** The family-level statement ("Gemini 3 models support a 1 million token input context window and up to 64k tokens of output") and the per-model `1M / 64k` rows cover 3.1 Flash-Lite, 3.1 Pro and 3-Flash-preview [S15]; individual model pages for 3.6/3.5 returned 404 on the URL patterns tried.
9. **Which request-body field name carries the JSON schema on the endpoint the team will actually use** — `response_format` (Interactions API [S4][S13]) vs `generationConfig.responseSchema` (`:generateContent`, used by the Gmail sample [S12]).
10. **Whether a Gmail CardService add-on can capture microphone audio at all.** Not addressed by any source read; blocks any meaningful FR-05 feasibility conclusion.
11. **Groq / Mistral free-tier signup requirements** (credit card, phone verification) — not stated in their docs [S7][S23]; Mistral's free-tier numbers are not published at all.
12. **OpenAI, Cloudflare and OpenRouter structured-output, audio, and context-window specifics** — not fetched this session; the table marks them "not verified" rather than guessing.
13. **Hosting requirements for the Workspace add-on "alternate runtimes" / HTTP-endpoint path** — the overview page references the guide but the fetched content does not name the required hosting product [S22].
14. **Vertex AI per-project quota limits** (requests/minute for Gemini on Vertex) — not fetched.

---

## Sources

All accessed **5 August 2026**.

| # | Source | URL |
|---|---|---|
| S1 | Gemini API — Rate limits (tier qualification, spend limits, "viewed in Google AI Studio") | https://ai.google.dev/gemini-api/docs/rate-limits |
| S2 | Gemini Developer API — Pricing (free tier "Free of charge", paid per-MTok rates, "used to improve our products") | https://ai.google.dev/gemini-api/docs/pricing |
| S3 | Vertex AI — Generative AI pricing | https://cloud.google.com/vertex-ai/generative-ai/pricing |
| S4 | Gemini API — Structured outputs (JSON Schema, `enum`) | https://ai.google.dev/gemini-api/docs/structured-output |
| S5 | Gemini API — Audio understanding (32 tok/s, 9.5 h, formats, 20 MB inline) | https://ai.google.dev/gemini-api/docs/audio |
| S6 | Google Cloud — Free Trial and Free Tier features ($300/90 days, credit-card requirement, credit restrictions, Always-Free table) | https://docs.cloud.google.com/free/docs/free-cloud-features |
| S7 | Groq — Rate limits (free-tier per-model table) | https://console.groq.com/docs/rate-limits |
| S8 | OpenRouter — API rate limits (free models: 20 RPM, 50/1,000 RPD) | https://openrouter.ai/docs/api-reference/limits |
| S9 | Apps Script — Class `UrlFetchApp` (HTTPS, JSON payloads, headers, `script.external_request` scope) | https://developers.google.com/apps-script/reference/url-fetch/url-fetch-app |
| S10 | Gemini API — API key best practices (never commit; don't hardcode client-side; backend proxy) | https://ai.google.dev/gemini-api/docs/api-key |
| S11 | Apps Script — Vertex AI advanced service (billing-enabled project prerequisite; `cloud-platform` scope) | https://developers.google.com/apps-script/advanced/vertex-ai |
| S12 | Workspace add-ons — "Analyze and label Gmail messages with Gemini and Vertex AI" sample (billing prerequisite, `getOAuthToken` caveat, `:generateContent` endpoint, response schema) | https://developers.google.com/workspace/add-ons/samples/gmail-sentiment-analysis-ai |
| S13 | Gemini API — Quickstart (AI Studio auto-creates key; `x-goog-api-key`; paid upgrade needs Cloud Billing + $10 prepay; Interactions endpoint) | https://ai.google.dev/gemini-api/docs/quickstart |
| S14 | Gemini API — Files API (20 GB/project, 2 GB/file, 48 h retention, no cost) | https://ai.google.dev/gemini-api/docs/files |
| S15 | Gemini 3 developer guide (1M input / 64k output; per-model spec rows; Jan 2025 cutoff) | https://ai.google.dev/gemini-api/docs/gemini-3 |
| S16 | Gemini API — Tokens ("about 4 characters"; "Audio: 32 tokens per second") and Long context guide ("providing all relevant information upfront") | https://ai.google.dev/gemini-api/docs/tokens · https://ai.google.dev/gemini-api/docs/long-context |
| S17 | Anthropic Claude API reference — model IDs, pricing, context windows, structured outputs, document input, `/v1/messages` HTTP shape (via the authoritative local `claude-api` skill, cached 2026-06-24) | https://platform.claude.com/docs/en/about-claude/models/overview · https://platform.claude.com/docs/en/build-with-claude/structured-outputs |
| S18 | OpenAI — API pricing (no free tier shown; gpt-5-nano, gpt-5.6-sol rates) | https://developers.openai.com/api/docs/pricing |
| S19 | Cloudflare — Workers AI pricing (10,000 Neurons/day free) | https://developers.cloudflare.com/workers-ai/platform/pricing/ |
| S20 | Ollama — API reference (`localhost:11434`, `/api/generate`, `/api/chat`, JSON-schema `format`) | https://github.com/ollama/ollama/blob/main/docs/api.md |
| S21 | Apps Script — Quotas for Google Services (URL Fetch, runtime, triggers, Properties) | https://developers.google.com/apps-script/guides/services/quotas |
| S22 | Workspace add-ons — Overview (Apps Script vs alternate runtimes / HTTP endpoints) | https://developers.google.com/workspace/add-ons/overview |
| S23 | Mistral Docs — Usage and limits (Free mode exists; numbers deferred to Admin Panel) | https://docs.mistral.ai/admin/user-management-finops/tier |
| S24 | Apps Script — Properties service (three stores; Script Properties "shared among: All users of a script, add-on, or web app"; no security guidance) | https://developers.google.com/apps-script/guides/properties |
