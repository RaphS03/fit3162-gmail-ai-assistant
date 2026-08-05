/**
 * Throwaway Gmail add-on probe. Not product code — delete once #100 and #84 close.
 *
 * Exists to answer two questions that documentation cannot:
 *   #100 — can accounts other than the publisher install and run this?
 *   #84  — what `allow` attribute does Google put on the add-on's iframe?
 *
 * Deliberately requests only the two scopes a contextual Gmail add-on needs, so
 * the consent screen other accounts see is the minimal one (risk T5).
 */

var BUILD = 'probe-1';

function onGmailMessage(e) {
  var section = CardService.newCardSection()
    .addWidget(CardService.newTextParagraph().setText(
      '<b>The add-on rendered.</b><br><br>' +
      'Build: ' + BUILD + '<br>' +
      'Message context: ' + (e && e.gmail && e.gmail.messageId ? 'yes' : 'no') + '<br>' +
      'Host: ' + (e && e.clientPlatform ? e.clientPlatform : 'unknown')))
    .addWidget(CardService.newTextParagraph().setText(
      '<font color="#5f6368"><i>Sign-in identity is deliberately not requested — ' +
      'it would add a scope. Note which account you are signed in as.</i></font>'));

  return [CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle('S1_CS_15 probe'))
    .addSection(section)
    .build()];
}
