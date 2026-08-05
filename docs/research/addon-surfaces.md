# Research: Workspace add-on surfaces, runtimes and capability limits

**Ticket:** [#81](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/81) (part of [#80](https://github.com/RaphS03/fit3162-gmail-ai-assistant/issues/80))
**Researched:** 5 August 2026. All URLs accessed 2026-08-05.
**Status:** Evidence only. This document deliberately makes **no recommendation** — the frontend-surface choice belongs to the decision ticket.

Every claim below is tagged:

- **[DOC]** — stated explicitly in a primary Google/W3C/MDN document, quoted or closely paraphrased.
- **[INFER]** — a conclusion drawn from a documented fact plus a documented spec rule. The reasoning chain is shown so it can be checked.
- **[2ND]** — a secondary source (GitHub gist, community repo, Stack Overflow). Treated as a lead, not proof.
- **[SILENT]** — the primary docs do not address the question at all.

---

## Question

Within the Google Workspace constraint, what surfaces can a Gmail add-on actually present in 2026, and what are the hard capability limits of each — specifically around arbitrary HTML/JS, microphone access, hover interactions, and where code executes?

---

## Summary of findings

**1. A Gmail add-on's own UI is cards, and only cards. This is documented, explicit, and not a style preference.** The Google Workspace add-ons *Restrictions* page carries a restriction headed "Use HTML/CSS or client-side scripting", whose body reads: *"Google Workspace add-ons must use card-based interfaces. The HTML/CSS interfaces supported by Editor add-ons can't be used."* [DOC, S1]. The Semester 1 report §5.1 claim that a Gmail add-on renders an HTML Service sidebar is **contradicted by the current primary documentation**. HtmlService sidebars/dialogs are a capability of *Editor* add-ons (Docs, Sheets, Slides, Forms) — a different add-on type with a different host set [DOC, S2].

**2. Because there is no HTML/JS surface inside the add-on, the `getUserMedia` question does not even arise there.** There is no page, no iframe you control, and no client-side script in a card. Microphone capture cannot happen inside the add-on's sidebar under any documented configuration [INFER from S1]. FR-05 voice input, if it survives, must live on a *different surface* reached from the card.

**3. Whether microphone capture works in an Apps Script–hosted companion web app is genuinely unresolved and the sources conflict.** Apps Script's documented sandbox description lists only HTML5 `sandbox` keywords and says nothing about the iframe `allow` (Permissions Policy) attribute [DOC, S16 + SILENT]. Two secondary sources directly contradict each other on whether Google's generated wrapper iframe includes `microphone` in `allow` — one says it is omitted and `getUserMedia` throws a permissions-policy violation [2ND, S28], the other says the generated iframe carries `camera *; … microphone *; …` [2ND, S27]. **This must be tested empirically by the voice spike; do not plan against either answer.**

**4. A companion surface hosted on your own origin sidesteps the whole problem.** A card button can open an arbitrary allowlisted URL in a new tab/window (`OpenAs.FULL_SIZE`, supported by all clients) [DOC, S7/S8/S9]. A top-level page you host is a first-party browsing context, so `microphone` (default allowlist `self`) is available to it subject only to the ordinary HTTPS secure-context requirement and the user's permission prompt [DOC, S22/S23 → INFER]. The cost is that voice happens in a separate tab, not inside Gmail.

**5. FR-06's "prolonged hover preview" is not achievable in a Gmail add-on card.** The documented set of widget handler functions is exactly `setOnChangeAction`, `setOnClickAction`, `setComposeAction`, `setOnClickOpenLinkAction`, `setOpenLink`, `setSuggestionsAction` — all change- or click-triggered. There is no hover handler [DOC, S5]. The one hover-driven card surface Google ships — link previews via smart chips — is documented for **Docs, Sheets and Slides only**; Gmail is not a supported host for it [DOC, S11]. The nearest card-native substitutes are click-to-expand: collapsible card sections, `CollapseControl`, collapsible text paragraphs, peek cards, and overflow menus [DOC, S3/S4/S6/S12].

**6. HTTP ("alternate runtime") add-ons are real, documented, and change where code runs — but not what the surface can render.** You may write the add-on in any language on any HTTPS host (Cloud Run recommended), configure the manifest in the Google Cloud console under the Google Workspace Marketplace SDK, and install it unpublished from the *HTTP Deployments* tab [DOC, S13/S14]. But the response payload is still *card JSON* — the same card framework, the same widgets [DOC, S13]. Choosing HTTP buys you language choice, your own compute, no 30-second Apps Script callback ceiling, and normal source control; it buys you **zero** additional UI capability, and it adds a Google Cloud project to configure.

**7. Test-mode deployment is easy, but the documentation says testers must share the script owner's domain — this is the live T5 risk.** The Apps Script test-deployment page states as a prerequisite: *"Test users must belong to the same domain as the script owner."* [DOC, S15]. Separately, OAuth verification is *not required* when owner and users are in the same Google Workspace domain, and an add-on published from a **consumer gmail.com account shows the "unverified app" screen to every user, including the publisher's own account** [DOC, S18]. Unverified apps are capped at **100 new users in total** over the project's lifetime [DOC, S19/S20]. Reading those together: running the demo on **Monash Google Workspace accounts** avoids the unverified-app screen, the user cap, and the same-domain prerequisite in one move [INFER]. Personal @gmail.com accounts are not documented as impossible, but every doc-level friction point lands on them.

**8. Quota reality is materially better on a Workspace account than a consumer one.** UrlFetch 100,000/day vs 20,000/day; trigger runtime 6 h/day vs 90 min/day. The binding limit for an LLM-backed add-on is the **30 seconds/execution Google Workspace add-on runtime cap**, which is identical on both [DOC, S17], and the parallel documented warning that *"the Apps Script Card service limits callback functions to a maximum of 30 seconds of execution time"* [DOC, S5].

---

## 1. CardService — widgets, interaction model, and what is categorically impossible

### 1.1 What the surface is

*"A card-based Google Workspace add-on appears as a pane in the sidebar (or, on mobile, as another activity window reached through the menu)."* Cards decompose into a card header, card sections, and widgets. Structural rule: *"Cards and card sections are structural widgets, so you cannot add those to a card section."* [DOC, S3]

Hard structural limits: *"A card can have no more than 100 card sections"* and *"A card section can have no more than 100 widgets"* [DOC, S3], restated in the Restrictions page as *"you can't add more than 100 widgets or 100 card sections to a card"* [DOC, S1].

### 1.2 Gmail extension points

The Gmail overview documents four extension points [DOC, S10]:

| Extension point | Trigger |
|---|---|
| Homepages | Non-contextual card, `gmail.homepageTrigger` |
| Message UI | Contextual card shown when a user opens a message |
| Compose UI | Contextual card shown when a user composes a message or reply |
| Draft creation | Add-on creates/updates message drafts in response to user interaction |

The same page states you *"can build custom add-ons with Apps Script and the Card service to extend Gmail's functionality"* and that add-ons *"extend Gmail … on both desktop and mobile clients"* [DOC, S10]. The Restrictions page qualifies mobile: contextual triggering (message reading) works in the Gmail mobile app; **non-contextual homepages are not available on mobile**, and add-ons *"are not available from mobile web browsers"* [DOC, S1]. Peek cards also *"don't appear in mobile apps"* [DOC, S4].

### 1.3 The widget inventory

From the concepts page [DOC, S4] and the Apps Script `CardService` reference [DOC, S6]:

- **Structural** — `Card`, `CardHeader`, `CardSection` (optionally collapsible), `ButtonSet`, `FixedFooter`, `Columns`/`Column` (max 2 columns), `Grid`/`GridItem`, `Divider`, `CollapseControl`, `Carousel`/`CarouselCard`, peek cards (`DisplayStyle.PEEK`).
- **Informational** — `TextParagraph`, `DecoratedText` (top/bottom labels, icon, and an attached `Button` or `Switch`/checkbox), `Image`, `IconImage`, `Chip`/`ChipList`. `KeyValue` is deprecated.
- **Interactive** — `TextButton`, `ImageButton`, `TextInput` (with `Validation`, autocomplete `Suggestions`), `SelectionInput` (checkbox / radio / dropdown / multiselect), `Switch`, `DatePicker`, `TimePicker`, `DateTimePicker`, `CardAction` (header menu), universal actions, `OverflowMenu`/`OverflowMenuItem`.
- **Gmail-specific responses** — `ComposeActionResponse`, `UpdateDraftActionResponse`, `UpdateDraftBodyAction`, `UpdateDraftSubjectAction`, `UpdateDraftTo/Cc/BccRecipientsAction`.

Limited rich text exists: *"The content text can use HTML formatting; the top and bottom labels must use plain text"* for `DecoratedText`, and `TextParagraph` *"can include HTML formatted elements"* [DOC, S4]. This is a formatting subset inside a widget — it is not a document you control, and the Restrictions page's prohibition on client-side scripting still stands [DOC, S1].

Also documented as impossible: **SVG images** (*"You can't currently use SVG images with Card service cards and widgets"*) and **Apps Script simple triggers** [DOC, S1].

### 1.4 The interaction model — and the hover answer

The *Add-on actions* page publishes the complete handler table [DOC, S5]:

| Handler | Triggers on | Applicable widgets |
|---|---|---|
| `setOnChangeAction` | widget value changes (on blur/Enter) | `DatePicker`, `DateTimePicker`, `SelectionInput`, `Switch`, `TextInput`, `TimePicker` |
| `setOnClickAction` | user clicks the widget | `CardAction`, `Image`, `ImageButton`, `DecoratedText`, `TextButton` |
| `setComposeAction` | user clicks the widget (Gmail-only; builds a draft) | same as above |
| `setOnClickOpenLinkAction` | user clicks the widget; URL built at click time | same as above |
| `setOpenLink` | user clicks the widget; URL known ahead of time | same as above |
| `setSuggestionsAction` | user types into a text input | `TextInput` |

There is **no hover, mouseover, focus, long-press, or pointer-event handler in the table** [DOC, S5]. Reinforcing this, the Restrictions page states that except for the documented triggers, *"add-ons can't tell what a user does outside the add-on itself"* [DOC, S1].

The only hover-activated card surface Google documents is link previews with smart chips: *"When the user hovers over the chip, they see a card interface that previews more information about the file or link."* That feature is scoped to **Docs, Sheets and Slides** — the manifest fields are `addOns.docs`, `addOns.sheets`, `addOns.slides` with `linkPreviewTriggers`, and Slides supports linked titles rather than chips. **Gmail is not among the supported hosts** [DOC, S11]. The add-ons release notes trace this feature's rollout (Sheets/Slides Jan 2024, Sheets smart chips Oct 2024) and record no extension of it to Gmail through the most recent entry, 10 April 2026 [DOC, S12].

**Conclusion for FR-06 [INFER]:** a literal "hover over a message for N milliseconds and a preview appears" interaction is not expressible in a Gmail add-on card. What *is* expressible with documented primitives: a contextual card that renders automatically when a message is opened (contextual trigger), a peek-card notification, a collapsed card section or collapsible text paragraph that expands on click, or a click-to-expand `DecoratedText`/`OverflowMenu`. All are click- or context-driven, not hover-driven.

### 1.5 The 30-second wall

*"The Apps Script Card service limits callback functions to a maximum of 30 seconds of execution time. If the execution takes longer than that, your add-on UI might not update its card display properly."* [DOC, S5] The quotas page confirms a hard limit row: **"Google Workspace add-on runtime — 30 sec / execution"**, identical for consumer and Workspace accounts [DOC, S17]. General Apps Script script runtime is 6 min/execution, but the add-on path is the 30 s one.

---

## 2. HtmlService — can a Gmail add-on render arbitrary HTML/JS, and does the sandbox permit `getUserMedia`?

### 2.1 Can a Gmail add-on render HTML/JS? No.

Primary, verbatim, from *Restrictions* under the heading **"Use HTML/CSS or client-side scripting"**:

> "Google Workspace add-ons must use card-based interfaces. The HTML/CSS interfaces supported by Editor add-ons can't be used. Google Workspace add-ons use a widget-based approach to building user interfaces. This lets the add-on work well on desktop and mobile platforms without requiring you to build an interface for each." [DOC, S1]

The *Add-on types* page draws the same line from the other direction: Workspace add-ons *"Use standardized interfaces: Construct user interfaces from built-in widget elements provided by the Google Apps Script Card service. You don't need expertise with HTML or CSS"*, whereas *"Editor add-ons can create interfaces consisting of menu items, dialogs, and sidebars. Interfaces are defined using standard HTML and CSS"* [DOC, S2]. Editor add-ons extend Docs, Sheets, Slides and Forms — **not Gmail** [DOC, S2].

HtmlService's own restrictions page scopes its sandbox to exactly those hosts: *"the HTML service uses iframes to sandbox web apps or custom user interfaces for Google Docs, Google Sheets, and Forms"* [DOC, S16]. Gmail is not listed.

**This settles the Semester 1 contradiction.** Overview + resource table (CardService) match the documentation; report §5.1 (HTML Service sidebar in Gmail) does not.

### 2.2 What the HtmlService sandbox actually is (relevant only to web apps / Editor add-ons)

`IFRAME` is the only surviving sandbox mode; `NATIVE` and `EMULATED` are sunset and `setSandboxMode` *"now has no effect when called"* [DOC, S16]. The documented HTML5 `sandbox` keywords are:

```
allow-same-origin, allow-forms, allow-scripts, allow-popups,
allow-downloads, allow-modals, allow-popups-to-escape-sandbox,
allow-top-navigation-by-user-activation   (stand-alone script projects only)
```

`allow-top-navigation` is deliberately **not** set. Links must target `_top` or `_blank`. Active content (scripts, external stylesheets, XHR) must be loaded over HTTPS. [DOC, S16]

**The page says nothing whatsoever about the iframe `allow` attribute, Permissions Policy, `Permissions-Policy` response headers, CSP, or `X-Frame-Options`.** [SILENT, S16] The HTML5 `sandbox` attribute and the Permissions Policy `allow` attribute are separate mechanisms; the documented list above tells us nothing about microphone delegation.

### 2.3 What the browser specs require for `getUserMedia`

- Secure context: *"`getUserMedia()` is a powerful feature that can only be used in secure contexts; in insecure contexts, `navigator.mediaDevices` is `undefined`."* [DOC, S22]
- *"The two Permissions Policy directives that apply to `getUserMedia()` are `camera` and `microphone`."* [DOC, S22]
- *"The default allowlist for `microphone` is `self`."* [DOC, S23]
- To use it in a frame you must delegate explicitly: `<iframe src="…" allow="camera; microphone">` [DOC, S22]
- When policy blocks it: *"On browsers that support managing media permissions with Permissions Policy, this error is returned if Permissions Policy is not configured to allow access to the input source(s)"* — a `NotAllowedError` `DOMException` [DOC, S22]; the microphone-directive page repeats that blocked calls reject with `NotAllowedError` [DOC, S23].

The W3C *Media Capture and Streams* specification lists a §14 "Permissions Policy Integration" in its table of contents, but the section body was not retrievable in the fetched document, so it is cited here only as corroborating context, not as a quoted source [S26].

**[INFER]** Combining these: a **cross-origin** iframe that is not granted `allow="microphone"` by its embedder cannot obtain a microphone stream, and the call rejects with `NotAllowedError`. Content rendered by HtmlService is served from a Google user-content origin nested inside `script.google.com`, i.e. cross-origin to the page you wrote — so the outcome depends entirely on whether Google's generated wrapper iframe carries `microphone` in its `allow` attribute. **The Apps Script documentation does not say.**

### 2.4 The conflicting secondary evidence — unresolved

| Source | Claim |
|---|---|
| `joshm21/microphone-bridge` README [2ND, S28] | *"Google explicitly omits the `microphone` and `camera` directives from the `allow` attribute of the outer `sandboxFrame` template on modern deployments"*; `getUserMedia()` *"fails instantly with … `DOMException: Permissions policy violation`"*. Describes the nested `sandboxFrame → userHtmlFrame` structure and a `window.open()` + `postMessage` popup workaround hosted on GitHub Pages. |
| Apps Script feature-request gist by Martin Hawksey [2ND, S27] | *"Currently, add-on iframes are served with an extensive list of permissions (e.g. `camera`, `geolocation`, `microphone`)"*, illustrated as `<iframe allow="accelerometer *; camera *; geolocation *; microphone *; … web-share *">`. The request is to add `language-model` (Gemini Nano), implying the *existing* list already includes microphone. |

These cannot both be right about the same deployment path in the same month. Possible reconciliations — none verified here — include different frames in the nesting chain (outer `sandboxFrame` vs inner `userHtmlFrame`), different surfaces (Editor sidebar vs standalone web app `/exec`), or a change over time. **Treat as an open empirical question (§6).**

### 2.5 The part that is *not* in doubt

Even the most favourable reading of §2.4 does not help the add-on sidebar, because a Gmail add-on cannot render HtmlService content at all [DOC, S1]. HtmlService is only reachable from this project via a **standalone Apps Script web app opened as a companion surface** (§4).

---

## 3. Alternate runtimes / HTTP add-ons

### 3.1 It exists and is fully documented

*"As an alternative to Google Apps Script, you can build an add-on in any coding language you want, as long as you can return properly formatted JSON for the interface to render as cards."* [DOC, S13]

Documented setup [DOC, S13]:

1. Stand up HTTPS endpoints on your own infrastructure. *"If you want to build and host your add-on on Google Cloud, we recommend that you use Cloud Run."*
2. Create a Google Cloud project; enable the **Google Workspace Marketplace SDK**.
3. In the Cloud console: *APIs & Services → Google Workspace Marketplace SDK → HTTP Deployments → Create new deployment*, then paste the manifest as JSON.
4. Declare **all** OAuth scopes explicitly in the manifest's `oauthScopes` array.
5. Implement granular permissions: the add-on receives `authorizationEventObject.authorizedScopes` and must respond with `requesting_google_scopes` for anything missing. Since **1 December 2025 all HTTP Workspace add-ons must support granular consent** [DOC, S12 release note of 5 May 2025].
6. Validate inbound POSTs using the ID tokens (`authorizationEventObject.userIdToken`, plus a service-account email for request validation).

Documented Gmail entry points for HTTP add-ons: `contextualTrigger.onTriggerFunction` (user opens an email) and `composeTrigger` (user opens compose), both returning `renderActions`; plus the common `homepageTrigger.runFunction`, `OnClick.action.function`, and `TextInput.autoCompleteAction.function` [DOC, S13].

Testing an unpublished HTTP add-on: *"In the add-on's Cloud project, go to the Google Workspace Marketplace SDK's HTTP Deployments tab. Next to the deployment you want to test, click Install."* Uninstall is the same tab. Local debugging is documented via **ngrok** tunnels with an IDE debugger (Node.js, Python, Java walk-throughs) [DOC, S14].

### 3.2 What it does and does not change

**Does not change the surface.** *"Design your add-on interface with the card framework. Use JSON instead of the Google Apps Script Card Service to build cards."* [DOC, S13] Same widgets, same handler model, same absence of HTML/JS and hover. The *Card-based interfaces* page confirms: *"Add-ons built in other languages must return properly formatted JSON for the interface to render as cards."* [DOC, S1-adjacent, card-interfaces page]

**Does change execution location and language.** Code runs on your host, in your language, under your source control and CI. The Apps Script 30-second callback limit and Apps Script daily quotas [DOC, S17] are properties of the Apps Script runtime, so an HTTP add-on is not bound by them — but the user-facing card still has to update, and no documented replacement latency budget for HTTP add-ons was found [SILENT].

### 3.3 Free-tier viability for this team

The alternate-runtimes page contains **no statements about pricing, quotas, or a Workspace-domain requirement** [SILENT, S13]. What is documented is the mandatory shape of the setup: a Google Cloud project, the Marketplace SDK enabled, an always-reachable HTTPS endpoint, OAuth client + service-account configuration, and ID-token validation code you write yourself. Compared with Apps Script — which needs none of that, deploys from the browser, and installs from *Deploy → Test deployments* — the HTTP path is materially more setup for four part-time students. Cloud Run free-tier limits were **not verified against a primary Google Cloud pricing source in this research** and should be checked separately before anyone relies on a cost figure.

---

## 4. Companion surfaces — opening an authorised web app from a card

### 4.1 The mechanism is documented and first-class

Two handlers open URLs: `setOpenLink` (URL known ahead of time) and `setOnClickOpenLinkAction` (URL constructed at click time). For the latter, *"You can only open the URL in a new window."* For the former, *"You can open the URL in a new window or in an overlay. When closed, you can cause the UI to reload the add-on."* [DOC, S5]

`OpenLink` configuration [DOC, S7]:

- `setOpenAs(OpenAs.FULL_SIZE)` — *"Open in a full window or tab. Default."* and *"FULL_SIZE is supported by all clients."* [DOC, S8]
- `setOpenAs(OpenAs.OVERLAY)` — *"Open as an overlay such as a pop-up."* *"The implementation depends on the client platform capabilities, and the value selected may be ignored if the client does not support it."* [DOC, S8]
- `setOnClose(OnClose.RELOAD_ADD_ON)` — reloads the card when the window/tab closes, which is the documented hook for "user went away, did something, came back". Caveat: *"To reload add-ons after closing a link, don't use a link with Cross-Origin-Opener-Policy (COOP) header enabled. If COOP is enabled in a link, add-ons can't detect the window state, and the add-on card doesn't update."* [DOC, S7]
- `setUrl(url)` — *"The URL must match a prefix in the manifest allowlist."* [DOC, S7] That allowlist is `addOns.common.openLinkUrlPrefixes` in the manifest [DOC, S9]. Apps Script projects additionally use `urlFetchWhitelist` for outbound `UrlFetchApp` calls [DOC, S9].

### 4.2 Why this matters for microphone access

**[INFER, chain shown]** If the companion page is served from an origin the team controls (e.g. Cloud Run, GitHub Pages, any HTTPS host) and is opened as a **top-level** browsing context via `OpenAs.FULL_SIZE`:

1. It is a secure context (HTTPS), so `navigator.mediaDevices` is defined [DOC, S22].
2. It is the top-level document of its own origin, and the `microphone` default allowlist is `self` [DOC, S23] — so no cross-origin delegation is needed.
3. Therefore `getUserMedia({audio:true})` should succeed subject only to the browser's normal user permission prompt.

None of the Google add-on docs *state* this — it follows from the web platform specs, not from Workspace documentation. The `microphone-bridge` project [2ND, S28] uses exactly this reasoning (popup on a controlled origin, results returned by `postMessage`) as its workaround for the Apps Script sandbox, which is corroborating but secondary.

**[INFER]** The same reasoning does **not** transfer cleanly to an *Apps Script* web app opened via `OpenLink`, because Apps Script serves your HTML inside its own generated wrapper frame rather than as your top-level document — which puts it back in the §2.4 conflict.

### 4.3 Costs of the companion-tab approach

Documented, not inferred: the user leaves the Gmail sidebar; the card can only learn the interaction finished via `OnClose.RELOAD_ADD_ON`, which is defeated by COOP headers on the target [DOC, S7]; the target URL prefix must be in `openLinkUrlPrefixes` [DOC, S7/S9]; `OVERLAY` may be silently downgraded on clients that don't support it [DOC, S8]; and add-ons *"are not available from mobile web browsers"* [DOC, S1], so the mobile story is separate.

### 4.4 Voice-recognition options on such a surface (context for the spike)

- **Web Speech API `SpeechRecognition`** is marked **Limited availability / not Baseline** — *"not Baseline because it does not work in some of the most widely-used browsers"* [DOC, S25]. *"By default, using speech recognition on a web page involves a server-based recognition engine. Your audio is sent to a web service for recognition processing, so it won't work offline."* [DOC, S24] On-device mode is opt-in via `SpeechRecognition.processLocally = true`, and `available()`/`install()` are gated by the `on-device-speech-recognition` Permissions Policy whose *"default allowlist value … is `self`"* — with MDN explicitly noting you only need to adjust it *"in embedded cross-origin documents"* [DOC, S24]. This is a useful independent confirmation that the `self`-default/cross-origin-delegation model is the governing pattern for media-adjacent features.
- **`getUserMedia` + `MediaRecorder` + a server-side STT call** is the alternative, and puts the audio on a path the team controls. Not evaluated here.
- Note for NFR-01/privacy (risk P4): server-based recognition means user audio leaves the browser to a third party. Relevant to the privacy decision ticket, out of scope for this one.

---

## 5. Deployment for a student demo

### 5.1 Apps Script test deployments

Documented procedure [DOC, S15]: open the script project in the Apps Script editor → **Deploy → Test deployments** → **Install** → **Done**. *"After you install the add-on, it's immediately available in the host applications it extends. You might need to refresh the host application tab before the add-on appears."* Uninstall is the same dialog. Installing the *Latest Version (Head)* means code changes apply immediately without reinstalling.

Documented prerequisites, verbatim [DOC, S15]:

> - "You must have editor access to the script project."
> - "To let others test the add-on, grant them editor access to the project."
> - **"Test users must belong to the same domain as the script owner."**

The third bullet is the T5 finding. The docs assert it as a flat prerequisite and do **not** explain how it evaluates for consumer `gmail.com` accounts [SILENT] — whether `gmail.com` counts as a shared "domain" for this check is not addressed anywhere in the primary documentation reviewed.

For HTTP add-ons the equivalent is the Marketplace SDK **HTTP Deployments → Install** flow, with no same-domain prerequisite stated on that page [DOC, S14; SILENT on domain].

### 5.2 OAuth verification and the unverified-app screen

*"Verification isn't required for Google Apps Script projects whose owner and users belong to the same Google Workspace domain or customer."* Otherwise, *"users outside your domain see an unverified app screen … The total number of unverified app users is also capped."* [DOC, S18]

The applicability table [DOC, S18], reproduced:

| | Client is verified | Publisher is a Workspace account of customer A | Script is in a shared drive of customer A | Publisher is a Gmail account |
|---|---|---|---|---|
| User is a Workspace account of customer A | Normal | **Normal** | Normal | Unverified |
| User is a Workspace account **not** of customer A | Normal | Unverified | Unverified | Unverified |
| User is a Gmail account¹ | Normal | Unverified | Unverified | Unverified |

¹ *"Any Gmail account, including the account used to publish the app."* [DOC, S18]

Read directly: **publish from a personal Gmail account and every single user — including you — hits the unverified-app screen.** Publish from a Monash Workspace account and use Monash accounts, and the flow is normal with no verification required.

The cap: *"apps that present the unverified app screen to users"* are limited to **"100 new users in total, after the app presents the unverified app screen"**, and the escape is verification [DOC, S19]. The rate-limits page cross-references the same cap [DOC, S20]. Verification itself requires a **verified website on a domain you own**, a public privacy-policy page, and a standard (non-default) Google Cloud project [DOC, S18] — several days to weeks of process, and out of scope per ticket #80.

Gmail scopes fall in the sensitive/restricted band that triggers all of this; the restricted-scope-verification page also documents explicit **exceptions** for *"personal use, development/testing/staging environments, … internal use within an organization, and domain-wide installation"* [DOC, S29].

### 5.3 Marketplace publication (for completeness — #80 rules this out of scope)

Apps are **public** or **private**, and *"After you publish your app as either public or private, you can't change this setting."* Private publication is conditional: *"If you built your app using a Google Workspace account, you can publish the app privately to your Google Workspace organization."* Private listings are available immediately with no Google review; public listings require Marketplace review and possibly an OAuth review [DOC, S21].

### 5.4 Quotas that bound a demo

From the Apps Script quotas page [DOC, S17]:

| | Consumer (gmail.com) | Google Workspace |
|---|---|---|
| UrlFetch calls | 20,000 / day | 100,000 / day |
| Email read/write (excl. send) | 20,000 / day | 50,000 / day |
| Triggers total runtime | 90 min / day | 6 hr / day |
| Properties read/write | 50,000 / day | 500,000 / day |
| Script runtime | 6 min / execution | 6 min / execution |
| **Workspace add-on runtime** | **30 sec / execution** | **30 sec / execution** |
| Simultaneous executions per user | 30 | 30 |

*"All quotas are subject to elimination, reduction, or change at any time, without notice."* [DOC, S17]

Also relevant: since 7 August 2024, *"Google Workspace administrators can now turn on an allowlist in the admin console to control which external domains users can access through Apps Script's URL Fetch service"* [DOC, S12]. **If Monash IT has that allowlist enabled, outbound calls to an LLM provider from an Apps Script add-on could be blocked until the domain is allowlisted.** This is a documented mechanism; whether Monash uses it is unknown [SILENT].

---

## 6. What the sources do NOT settle

Explicit list of open questions the **voice-feasibility spike** must answer empirically. None of these can be closed by reading more documentation.

1. **Does `navigator.mediaDevices.getUserMedia({audio:true})` succeed inside an Apps Script web app served from `/exec`?** Primary docs are silent; two secondary sources contradict each other (§2.4). *Test:* deploy a minimal HtmlService web app that calls `getUserMedia` and logs the outcome; in DevTools, inspect the actual `allow` attribute on both the `sandboxFrame` and `userHtmlFrame` elements and record them verbatim. Test in Chrome and at least one other browser.
2. **Does the same answer hold for a web app opened from a card via `OpenLink` versus navigated to directly?** Whether the framing differs by entry path is undocumented.
3. **Does `getUserMedia` succeed on a self-hosted HTTPS page opened via `OpenAs.FULL_SIZE` from a Gmail add-on card?** This is the §4.2 inference and should still be verified end-to-end, including that the URL prefix allowlist accepts the host.
4. **Does `OnClose.RELOAD_ADD_ON` actually fire** when the companion tab closes, given the COOP caveat [DOC, S7]? Whether Cloud Run / GitHub Pages default responses carry COOP headers was not checked.
5. **Does `window.open()` + `postMessage` work from within the add-on context at all?** The `microphone-bridge` workaround assumes a page that can call `window.open` — a Gmail *card* cannot run script, so this only applies on a companion page, and the whole chain needs a real test.
6. **Is `gmail.com` "the same domain" for the test-deployment prerequisite?** [DOC, S15 asserts the rule; SILENT on interpretation]. *Test:* have a second personal Gmail account attempt to install the unpublished add-on after being granted editor access, and record the exact behaviour and any error.
7. **Can the team publish/deploy under Monash's Workspace tenancy at all?** Monash may restrict Apps Script, add-on installation, or Marketplace installs by admin policy. Documented mechanisms exist (app allowlists [DOC, S21], UrlFetch domain allowlists [DOC, S12]); Monash's actual configuration is unknown and must be checked with Monash IT / the supervisor.
8. **Whether an LLM round trip fits inside the 30-second add-on execution limit** [DOC, S5/S17] for realistic thread sizes, and what the card does when it doesn't. No documented async/"still working" card pattern was found in the pages reviewed [SILENT].
9. **Cloud Run (or equivalent) free-tier headroom** for an HTTP add-on. Not verified against a primary pricing source in this research.
10. **Whether any card-native construct produces a hover-like affordance in Gmail in practice** — e.g. does a `Chip` or `DecoratedText` render a native browser tooltip from alt text? The `CardService` reference mentions `setImageAltText()` only in a Chat sample [DOC, S6] and no tooltip behaviour is documented [SILENT]. Worth a 10-minute check before FR-06 is re-scoped.

---

## Sources

All accessed **2026-08-05**.

**Primary — Google Workspace add-ons documentation**

- **S1.** Restrictions | Google Workspace add-ons — https://developers.google.com/workspace/add-ons/guides/workspace-restrictions
- **S2.** Add-on types — https://developers.google.com/workspace/add-ons/concepts/types
- **S3.** Cards — https://developers.google.com/workspace/add-ons/concepts/cards (and Card-based interfaces — https://developers.google.com/workspace/add-ons/concepts/card-interfaces)
- **S4.** Widgets — https://developers.google.com/workspace/add-ons/concepts/widgets
- **S5.** Add-on actions — https://developers.google.com/workspace/add-ons/concepts/actions
- **S9.** Manifests for Google Workspace add-ons — https://developers.google.com/workspace/add-ons/concepts/gsuite-manifests
- **S10.** Extend Gmail with Google Workspace add-ons — https://developers.google.com/workspace/add-ons/gmail
- **S11.** Preview links with smart chips — https://developers.google.com/workspace/add-ons/guides/preview-links-smart-chips
- **S12.** Google Workspace add-ons release notes — https://developers.google.com/workspace/add-ons/release-notes (latest entry 2026-04-10)
- **S13.** Build a Google Workspace add-on using HTTP endpoints — https://developers.google.com/workspace/add-ons/guides/alternate-runtimes
- **S14.** Test and debug HTTP Google Workspace add-ons — https://developers.google.com/workspace/add-ons/guides/debug
- **S15.** Test and debug Apps Script Google Workspace add-ons — https://developers.google.com/workspace/add-ons/how-tos/testing-workspace-addons (page last updated 2026-07-22)

**Primary — Google Apps Script reference**

- **S6.** Card Service (class index) — https://developers.google.com/apps-script/reference/card-service
- **S7.** Class OpenLink — https://developers.google.com/apps-script/reference/card-service/open-link
- **S8.** Enum OpenAs — https://developers.google.com/apps-script/reference/card-service/open-as
- **S16.** HTML Service: Restrictions — https://developers.google.com/apps-script/guides/html/restrictions
- **S17.** Quotas for Google Services — https://developers.google.com/apps-script/guides/services/quotas
- **S18.** OAuth Client Verification — https://developers.google.com/apps-script/guides/client-verification

**Primary — Google identity / Marketplace / Cloud policy**

- **S19.** Unverified apps (Google Cloud Platform Console Help) — https://support.google.com/cloud/answer/7454865
- **S20.** OAuth Application Rate Limits — https://support.google.com/cloud/answer/9028764
- **S21.** Publish apps to the Google Workspace Marketplace — https://developers.google.com/workspace/marketplace/how-to-publish
- **S29.** Restricted scope verification — https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification

**Primary — web platform (MDN / W3C)**

- **S22.** MDN — `MediaDevices: getUserMedia()` — https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
- **S23.** MDN — `Permissions-Policy: microphone` — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Permissions-Policy/microphone
- **S24.** MDN — Using the Web Speech API — https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API/Using_the_Web_Speech_API
- **S25.** MDN — `SpeechRecognition` — https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition
- **S26.** W3C — Media Capture and Streams — https://www.w3.org/TR/mediacapture-streams/ — §14 "Permissions Policy Integration" appears in the table of contents but its body was **not retrievable** in the fetched document; cited as context only, not quoted.

**Secondary — treat as leads requiring verification**

- **S27. [SECONDARY]** M. Hawksey, "Feature Request: Allow developers to set the iframe 'allow' attribute for HtmlService" (GitHub gist) — https://gist.github.com/mhawksey/5229abc45a0c39fc7cc4b60b9145f0b7 — asserts HtmlService iframes are currently served with `camera *; … microphone *; …` in `allow`.
- **S28. [SECONDARY]** `joshm21/microphone-bridge` README (GitHub) — https://github.com/joshm21/microphone-bridge — asserts the opposite: `microphone`/`camera` are omitted from the outer `sandboxFrame` `allow` attribute and `getUserMedia` throws a permissions-policy violation; documents a `window.open()` + `postMessage` workaround.
