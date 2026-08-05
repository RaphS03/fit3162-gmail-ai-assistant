/**
 * PROTOTYPE — THROWAWAY. Spike for issue #84 (risk T4). Do not merge to main.
 *
 * Probes whether voice input can reach a Gmail add-on, and whether the
 * transcript can get back into a card.
 *
 * Two companion-hosting variants are tested, because they fail differently:
 *   A) served BY Apps Script (doGet + HtmlService) — free, but runs inside
 *      Google's sandboxed iframe, where the microphone may be denied.
 *   B) self-hosted static page (GitHub Pages) — own top-level origin, mic
 *      almost certainly works, but must not send a COOP header or
 *      OnClose.RELOAD silently stops firing.
 */

// ---- CONFIG — fill these in before deploying -------------------------------
// Variant B page, e.g. https://<user>.github.io/<repo>/companion/index.html
// Must also appear in appsscript.json openLinkUrlPrefixes.
var SELF_HOSTED_URL = 'https://REPLACE-ME.github.io/fit3162-gmail-ai-assistant/companion/index.html';
// This script's own Web App /exec URL, after you deploy it. Used for variant A.
var WEBAPP_URL = 'https://script.google.com/macros/s/REPLACE-ME/exec';
// ---------------------------------------------------------------------------

/** Per-user token so doPost can route a transcript back to the right card. */
function getToken() {
  var props = PropertiesService.getUserProperties();
  var t = props.getProperty('probe_token');
  if (!t) {
    t = Utilities.getUuid().slice(0, 8);
    props.setProperty('probe_token', t);
  }
  return t;
}

function openLink(url) {
  return CardService.newOpenLink()
    .setUrl(url)
    .setOpenAs(CardService.OpenAs.FULL_SIZE)   // full tab => top-level browsing context
    .setOnClose(CardService.OnClose.RELOAD);   // documented return trigger
}

/** Entry point declared in the manifest. */
function onGmailMessage(e) {
  var token = getToken();
  // doPost writes here; the card reads it after OnClose.RELOAD re-renders.
  var transcript = PropertiesService.getScriptProperties().getProperty('transcript_' + token);

  var section = CardService.newCardSection()
    .addWidget(CardService.newDecoratedText()
      .setTopLabel('Token — paste into the companion page')
      .setText(token))
    .addWidget(CardService.newDecoratedText()
      .setTopLabel('Transcript received')
      .setWrapText(true)
      .setText(transcript ? transcript : '(none yet)'))
    .addWidget(CardService.newTextParagraph()
      .setText('Open a variant, speak, post the transcript, then <b>close the tab</b> ' +
               'and watch whether this card reloads with the text.'))
    .addWidget(CardService.newTextButton()
      .setText('Variant A — Apps Script hosted')
      .setOpenLink(openLink(WEBAPP_URL + '?page=companion')))
    .addWidget(CardService.newTextButton()
      .setText('Variant B — self hosted')
      .setOpenLink(openLink(SELF_HOSTED_URL)))
    .addWidget(CardService.newTextButton()
      .setText('Clear transcript')
      .setOnClickAction(CardService.newAction().setFunctionName('clearTranscript')));

  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle('#84 voice probe'))
    .addSection(section)
    .build();
}

function clearTranscript() {
  PropertiesService.getScriptProperties().deleteProperty('transcript_' + getToken());
  return CardService.newActionResponseBuilder()
    .setNavigation(CardService.newNavigation().updateCard(onGmailMessage({})))
    .build();
}

/** Variant A: serve the companion page from Apps Script itself. */
function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('companion')
    .setTitle('#84 voice probe — variant A')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/** Receives the transcript from either variant. Body is text/plain JSON. */
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    if (!data.token) throw new Error('no token');
    PropertiesService.getScriptProperties()
      .setProperty('transcript_' + data.token, data.transcript || '');
    return ContentService.createTextOutput(
      JSON.stringify({ ok: true, stored: (data.transcript || '').length + ' chars' })
    ).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ ok: false, error: String(err) })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}
