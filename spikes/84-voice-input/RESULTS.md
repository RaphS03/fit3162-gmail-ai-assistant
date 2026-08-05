# Spike #84 — results

Fill in verbatim. Paste onto the issue when complete. "Worked / didn't work" is not
evidence; the exact error string is.

| | Run 0 (localhost) | Run A (Apps Script hosted) | Run B (self-hosted) |
|---|---|---|---|
| origin | | `https://n-…-script.googleusercontent.com` (`/userCodeAppPanel`) | |
| `isSecureContext` | | true | |
| top-level? (`self === top`) | | **false — framed** | |
| `allowsFeature('microphone')` | | **false** | |
| microphone allowlist | | **`[]` (empty)** | |
| `getUserMedia` outcome | | **FAILED** (twice, consistent) | |
| …verbatim error name + message | | `NotAllowedError: Permission denied` | |
| `SpeechRecognition` present? | | not reached | |
| transcript produced? | | not reached | |
| COOP header present? | | none | |
| POST status / body | | not reached | |
| …verbatim CORS error if failed | | n/a | |
| **card reloaded with transcript on tab close?** | n/a | not reached | |

### Run A verdict — Variant A is dead, and not recoverable

The microphone Permissions-Policy allowlist is **empty**, not `self`. The feature is
disabled for every origin in that frame, so `NotAllowedError` here is a **policy denial,
not a user denial** — no prompt was ever shown, and no Chrome site setting can change it.

This settles the contradiction recorded on the issue: Google's wrapper frame does **not**
delegate `microphone`. Combined with the architectural finding that cards run no developer
JavaScript at all, **every Google-hosted surface is closed to voice capture**. Only the
self-hosted top-level page (Variant B) remains.

`COOP header: none` is the one encouraging line — the return path's prerequisite is
checkable and was satisfied here.

## Screenshots

- [ ] Run A log panel
- [ ] Run B log panel
- [ ] The card showing a returned transcript (the money shot for the pitch deck)

## UX notes

What the round trip actually felt like. Count the clicks. Time it. Note anything that
would be awkward on a projector on 11 Sep.

## Verdict

Which of the four options in the ticket survives, and what "voice interaction" honestly
means for FR-05 given the evidence. **Evidence only — the FR-05 priority decision is #96.**
