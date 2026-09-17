/**
 * Läuft in der Konfigurationsseite auf dem Telefon, nicht auf der Uhr.
 * Hängt die Spenden-Schaltfläche an den Klick-Weg.
 */
module.exports = function (minified) {
  var clayConfig = this;
  var URL = 'https://buymeacoffee.com/SIDEffects';

  clayConfig.on(clayConfig.EVENTS.AFTER_BUILD, function () {
    var button = clayConfig.getItemById('donate');
    if (!button) return;
    button.on('click', function () {
      // In der Pebble-App öffnet window.open den Browser. Webviews, die
      // kein zweites Fenster erlauben, fangen wir mit dem Fallback ab.
      var w = null;
      try {
        w = window.open(URL, '_blank');
      } catch (e) {
        w = null;
      }
      if (!w) {
        window.location.href = URL;
      }
    });
  });
};
