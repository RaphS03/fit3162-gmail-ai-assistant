# Add-on probe — procedure for #100 and #84

A throwaway Gmail add-on that renders one card and does nothing else. It exists so two
questions can be answered empirically, because the documentation does not settle either.

Delete this directory once both tickets close.

---

## Setup (~10 minutes, once)

Do all of this signed in as the **dedicated project account**, not a personal one.

1. Go to <https://script.new> — this creates a new Apps Script project.
2. Rename it `S1_CS_15 Probe` (click "Untitled project").
3. **Project Settings** (left sidebar, gear icon) → tick **"Show 'appsscript.json' manifest file in editor"**.
4. Back in **Editor**, open `appsscript.json` and replace its entire contents with this
   directory's [`appsscript.json`](./appsscript.json).
5. Open `Code.gs` and replace its contents with this directory's [`Code.gs`](./Code.gs).
6. Save (⌘S / Ctrl+S).
7. **Deploy → Test deployments → Install**. Open Gmail, open any message. The probe should
   appear in the right-hand sidebar.

If step 7 fails, record the exact error — that alone is a finding.

---

## #100 — can other accounts install and run it?

The question is whether an add-on published from one personal account can be installed by
others, given Google's documentation states test users must belong to the same domain as
the script owner, and consumer Gmail accounts have no domain in the sense that rule assumes.

**Path A — project sharing (try this first).** In the Apps Script editor, use the project's
**Share** control to add accounts B, C and D as editors. Each then opens the project and runs
**Deploy → Test deployments → Install** on their own account.

For each of B, C and D, record:

- Did the install succeed? If not, the verbatim error.
- What consent screen appeared, and exactly which permissions it listed.
- Did an "unverified app" warning appear, and did it require clicking through *Advanced*?
- Did the card render on opening a message?

**Path B — only if A fails.** Publishing through the Google Workspace Marketplace SDK requires
a Cloud project and an OAuth consent screen. It does not require billing, but an unverified
external app shows the warning screen to everyone including the publisher and is capped at
100 users lifetime. Record how far you get and where it stops.

**The assessor question.** Try installing on an account the team does not control — a personal
account belonging to someone outside the team is a fair proxy. If that fails, the answer is
that the demonstration is screen-shared or recorded, which under the proof-of-concept framing
is a legitimate outcome rather than a failure. Decide it now rather than on 11 September.

**Also record:** if only one account can run it, who drives the demo, and how that person is
made interchangeable — the definition of done requires that someone who did not build it can
drive the demo script.

---

## #84 — what `allow` attribute is on the iframe?

Apps Script documentation lists only HTML5 `sandbox` keywords and is silent on the iframe
`allow` / Permissions Policy attribute. Two secondary sources contradict each other on whether
Google's wrapper frame includes `microphone`. This is the single empirical fact the voice
question turns on.

With the probe installed and visible in Gmail:

1. Open DevTools (⌘⌥I / Ctrl+Shift+I) → **Elements**.
2. Search the DOM for `iframe` and find the one wrapping the add-on card. There will be several
   nested frames; work outward from the card content.
3. For each frame in the chain, record the **verbatim** `allow` attribute, the `sandbox`
   attribute, and the frame's `src` origin. Screenshot it.
4. In the **Console**, with the add-on frame selected as the execution context, evaluate:

   ```js
   document.featurePolicy && document.featurePolicy.allowedFeatures()
   ```

   and record whether `microphone` appears.

`allow="microphone"` being absent anywhere in the chain means `getUserMedia` cannot work in the
card under any configuration, and FR-05 must move to a companion surface (#105) or be
renegotiated (#96). Its presence would be a surprising and very good result — verify it twice
before relying on it.

Attach the screenshots to the tickets. Do not merge this branch.
