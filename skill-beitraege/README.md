# Beiträge zur Skill `pebble-publish`

Hier liegen Dateien, die eigentlich in die Veröffentlichungs-Skill gehören
und dort auch eingespielt sind — **aber die Skill liegt in einem
Verzeichnis, das synchronisiert wird.** Am 17.09. hat ein Abgleich dort
Ergänzungen überschrieben und eine Datei entfernt. Deshalb diese Kopie:
Was hier liegt, überlebt den nächsten Abgleich.

## Inhalt

| Datei | Zweck |
|---|---|
| `assets/pebble_time_2.png` | freigestellte Pebble Time 2, 534 × 1009 |
| `assets/pebble_time_steel.png` | freigestellte Pebble Time Steel, 336 × 581 |
| `assets/side_effects_logo.png` | das Logo, gehört auf jedes Banner |
| `assets/uhren.json` | Displayflächen und Eigenheiten je Uhr |
| `scripts/freistellen.py` | Uhr aus einer Werbegrafik freistellen und ausmessen |
| `scripts/make_banner.py` | Banner mit **gezeichneter** Uhr, nach den Maßen der Skill |
| `scripts/make_banner_fotoversion.py` | Banner mit **freigestellter** Uhr aus `assets/` |

## Displayflächen

```
pebble_time_2      (97, 302, 436, 704)   Eckradius 26
pebble_time_steel  (34, 138, 299, 449)   Eckradius 20
```

Bei der Time 2 sind Gehäuse und Display fast gleich dunkel; die
automatische Suche in `freistellen.py` findet sie dort nicht, die Werte
wurden von Hand ausgemessen. Beim Time Steel trennt der helle Metallrahmen
beides, dort findet die Automatik sie allein.

## Erkenntnisse, die in der Skill standen und überschrieben wurden

Falls sie dort wieder fehlen, gehören sie erneut hinein:

- **Sprache:** Ist die App nicht englisch, vor der Einreichung klären. Beim
  Umstellen betroffen: Texte auf der Uhr, Statusmeldungen aus PebbleKit JS,
  **und die Konfigurationsseite**. Tests, die auf Meldungstexte prüfen,
  brechen dabei.
- **Plattformen:** Jede `targetPlatform` vor der Einreichung im Emulator
  ansehen. Ein Layout für 200 × 228 überlebt 144 × 168 meist, bricht auf
  dem runden `chalk` aber zuverlässig.
- **Quellcode-URL** ist im Portal ein **Pflichtfeld**, auch wenn man keinen
  Link möchte.
- **Emulator, localStorage vorbelegen:** `dbm.dumb` unter
  `~/.local/share/pebble-sdk/<sdk>/<plattform>/localstorage/<uuid>` —
  vorher `pebble kill`, sonst überschreibt der laufende Emulator die Datei.
- **Emulator, binäre XHR-Antworten:** `responseType = "arraybuffer"`
  funktioniert dort **nicht**. pypkjs liefert einen Puffer richtiger Länge,
  gefüllt mit Nullen, ohne Fehlermeldung. Apps, die Bilder aus dem Netz
  holen, lassen sich im Emulator nicht am Stück prüfen: Telefon-Seite gegen
  einen echten HTTP-Server in Node testen, Uhr-Seite mit
  `pebble send-app-message --bytes-file` füttern.
- **Screenshots:** auf Duplikate per Prüfsumme prüfen, nicht nur hinsehen.
  Gehaltene Knöpfe mit `emu-button push/release`, dazwischen Zeit lassen.
- **Launcher-Icon** neu zeichnen statt verkleinern — bei 25 px zerfiel ein
  Schwenkbogen zu einem Haken.
- **Freistellen** per Flutfüllung vom Bildrand, nie per Farbschwellwert:
  sonst verschwindet ein schwarzes Display mit dem Hintergrund.
- **Farben auf dunklem Grund:** Eine Akzentfarbe mit Teildeckkraft wird
  braun. Stattdessen helles Grau mit wenig Deckkraft plus eine dünne, voll
  deckende Linie in der Akzentfarbe.
