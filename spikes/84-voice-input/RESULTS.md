# Spike #84 — results

Fill in verbatim. Paste onto the issue when complete. "Worked / didn't work" is not
evidence; the exact error string is.

| | Run 0 (localhost) | Run A (Apps Script hosted) | Run B (self-hosted) |
|---|---|---|---|
| `isSecureContext` | | | |
| top-level? (`self === top`) | | | |
| `allowsFeature('microphone')` | | | |
| microphone allowlist | | | |
| `getUserMedia` outcome | | | |
| …verbatim error name + message | | | |
| `SpeechRecognition` present? | | | |
| transcript produced? | | | |
| COOP header present? | | | |
| POST status / body | | | |
| …verbatim CORS error if failed | | | |
| **card reloaded with transcript on tab close?** | n/a | | |

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
