# Spike #84 — can voice input run inside the Gmail add-on?

**THROWAWAY.** Evidence-gathering probe for [issue #84](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/84)
(risk T4). Not a feature. Do not merge to `main`.

## What the docs already settled — read this before running anything

The original probe order in the ticket was: (1) mic inside the rendering surface,
(2) companion window, (3) record-and-upload. **Step 1 is dead on architecture, not
on sandbox policy** — see the issue for the primary sources. In short:

A Gmail add-on card is a *declarative widget tree*. Developer code runs **server-side**
in Apps Script; nothing the team writes executes as JavaScript in the card's frame.
So `getUserMedia` has no call site — it isn't blocked, there is nowhere to call it from.

That makes the DevTools `allow=` reading in the ticket comment **moot**: even if the
wrapper frame carried `allow="microphone"`, no developer script runs there to use it.
The two contradicting secondary sources are arguing about something that cannot matter.
Do not spend a deployment proving it.

So this probe tests the **companion-window path** only, in the two hosting variants
that fail for different reasons.

## The three runs

### Run 0 — local baseline (2 minutes, no Google account needed)

Confirms your browser and mic work at all, so a later failure is attributable to
the add-on context and not to your hardware.

```
./run.sh
```

Open <http://localhost:8084/companion/>, click buttons 1–3. `localhost` is a secure
context, so this should pass. If it fails here, fix that before going further.

### Run A — companion page hosted BY Apps Script

Free hosting, and `doPost` is same-project so the return path is trivial. **But** Apps
Script serves HTML inside Google's own sandboxed iframe, so the microphone may be
denied — this is where the Permissions-Policy question actually bites.

1. Create an Apps Script project on the **personal** account (see #100).
2. Paste `addon/Code.gs` as `Code.gs`, and `companion/index.html` as an HTML file
   named `companion`.
3. Paste `addon/appsscript.json` over the manifest (Project Settings → show manifest).
4. Deploy → New deployment → **Web app**, execute as *me*, access *anyone*.
   Copy the `/exec` URL into `WEBAPP_URL` in `Code.gs`.
5. Deploy → Test deployments → install the Gmail add-on.
6. Open Gmail, open any message, open the add-on, click **Variant A**.

### Run B — companion page self-hosted

Own top-level origin, so the mic should work. The risk moves to the **return path**.

1. Push this branch and enable GitHub Pages on it (Settings → Pages → branch
   `spike/84-voice-input`, folder `/spikes/84-voice-input`).
2. Put the resulting URL into `SELF_HOSTED_URL` in `Code.gs` **and** into
   `openLinkUrlPrefixes` in the manifest — an un-allowlisted URL will not open.
3. Click **Variant B** on the card.

## What to record — all of it verbatim

For each run, in the page's own log panel (screenshot it — the report needs figures):

- `isSecureContext`, top-level?, `allowsFeature('microphone')`, and the allowlist
- The **exact** `getUserMedia` outcome. If it throws, the `Error.name` matters:
  `NotAllowedError` = policy or user denial; `NotFoundError` = no device.
- Whether `SpeechRecognition` exists and produced a transcript
- The POST status and body, **or the CORS error verbatim** if it failed
- **The COOP line.** If the host sets `Cross-Origin-Opener-Policy`, `OnClose.RELOAD`
  will not fire and the transcript never returns. GitHub Pages does not set it by
  default; many other hosts do.
- Finally: close the tab, and record **whether the card reloaded and showed the text**.

Then the UX question the ticket asks, which no log answers: write down what the flow
actually *felt* like. A voice feature that throws the user out of Gmail into another
tab and back is a different product from one that works in the sidebar, and the
11 Sep demo has to survive it on a projector.

Put the findings in `RESULTS.md` and paste them onto the issue.
