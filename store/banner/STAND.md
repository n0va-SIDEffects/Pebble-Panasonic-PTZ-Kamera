# Stand der Arbeit am Banner

Notiz fuer eine Sitzung, die hier weitermacht - besonders fuer eine, die
direkt auf Mikes Rechner laeuft und damit Zugriff auf seine ComfyUI hat.

## Was fertig ist

Der Generator baut das Banner (720 x 320) aus Einzelteilen, die alle mit
Z-Image-Turbo auf dem eigenen Rechner entstanden sind. Aufbau, Regeln und
Bedienung stehen in `README.md` - bitte zuerst lesen.

Kurz:

- **Szene**: Werkbank mit Schneidematte, darauf Werkzeuge und in der
  Mitte das Geraet der App. Titel oben links, Pebble rechts.
- **Was fest ist**: Aufbau, Titelspalte, Uhr rechts, vier feste Werkzeuge.
- **Was variiert**: Geraet, Akzentfarbe, Uhrfarbe, Gimmick, Tisch,
  Werkzeuglage - alles ueber `--seed` reproduzierbar.
- **Nichts ueberlappt**: Das Geraet bekommt die Mitte und liegt vorn,
  Werkzeuge weichen aus (`silhouettenboxen`, Kollisionspruefung).
- **Logo**: sitzt auf dem Geraet, in wechselnder Form und Farbe.

## Was offen ist

1. **Logo ins Geraet einbacken.** `--logo-vorlage` gibt Geraet plus Maske
   aus, ein Durchlauf mit `--veredeln --staerke 0.25` soll das Logo ins
   Material einarbeiten. **Haengt gerade**: Der Upload nach ComfyUI
   scheitert mit HTTP 500 ("Server got itself in trouble"); der
   Stacktrace steht im ComfyUI-Fenster. `--im-input` umgeht den Upload,
   indem die Dateien von Hand in ComfyUIs input-Ordner kommen. Eine
   lokale Sitzung kann beides selbst pruefen.
2. **Dritter Tisch** (`tisch_3` in `assets_liste.json`) fehlt noch; beim
   Erzeugen kam "konnte nicht gespeichert werden", Ursache unklar.
3. **Zweite Fassungen der Werkzeuge** (`messer_2`, `loetkolben_2`,
   `dreher_rot_2`, `dreher_blau_2`) sind in der Liste, aber noch nicht
   erzeugt.
4. **Uhraufnahmen** fuer die uebrigen Plattformen: `diorite` (Pebble 2),
   `flint` (Pebble 2 Duo), `chalk` (Time Round), `aplite` (Classic).
   Gebraucht wird je eine frontale, freigestellte Aufnahme mit
   gestreckten Baendern; Anforderungen stehen in `README.md`.
5. **HELO-App** hat noch kein eigenes Repo; ihr Banner existiert nur in
   der Werkstatt.
6. **Veredelung** der fertigen Szene (Licht angleichen) ist gebaut und
   erprobt, aber noch nicht fuer PTZ und HELO durchgelaufen.

## Womit gearbeitet wird

- ComfyUI laeuft lokal auf 127.0.0.1:8188, Modell Z-Image-Turbo.
  `workflow_api.json` und `workflow_img2img_maske.json` liegen dabei.
- `comfy_assets.py` spricht ComfyUI an, `make_desk_banner.py` baut das
  Banner, `uhren.py` faerbt die Pebble um.
- Zweigstelle in beiden Repos: `claude/pebble-app-store-banner-atck9j`
  (pebble-theremin und pebble-panasonic-ptz-kamera, Inhalt identisch).
