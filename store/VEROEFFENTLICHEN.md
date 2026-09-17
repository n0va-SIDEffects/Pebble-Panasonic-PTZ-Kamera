# PTZ Remote 0.9 im Pebble Appstore veröffentlichen

Alles Nötige liegt in `store/release/`. Die Einreichung selbst muss von
Hand passieren — sie verlangt eine Anmeldung im Browser.

## Dateien

| Datei | Wofür |
|---|---|
| `PTZ-Remote-0.9.pbw` | die App. Beim Upload liest das Portal Version und Plattformen daraus |
| `icon_80.png` | Store-Icon, **RGB ohne Alphakanal** (Portal lehnt Alpha ab) |
| `icon_144.png`, `icon_48.png` | falls das Portal zusätzlich nach großem/kleinem Icon fragt |
| `banner_720x320.png` | Kopfbild der Listung |
| `description_en.txt` | Zeile 1 = Kurzbeschreibung, Rest = Beschreibung (1553 von 1600 Zeichen) |
| `screenshots_emery/` | 5 Bilder, 200 × 228 — für Pebble Time 2 |
| `screenshots_basalt/` | 3 Bilder, 144 × 168 — für Pebble Time |
| `screenshots_diorite/` | 3 Bilder, 144 × 168 — für Pebble 2 |
| `RELEASE_NOTES.md` | Text für das Release-Feld |

## Schritte im Portal

Portal: https://developer.repebble.com/dashboard (Konto der Pebble-Handy-App)

1. **Am Rechner einreichen, nicht am Handy.** Im mobilen Browser antwortet
   das Portal auf dieselbe Datei mit einem nichtssagenden 400er.
2. „Add Watchapp“, dann `PTZ-Remote-0.9.pbw` hochladen.
3. Grunddaten:
   - **Title:** PTZ Remote
   - **Category:** Tools & Utilities
   - **Source code URL:** Pflichtfeld. Siehe Hinweis unten.
   - **Icon:** `icon_80.png`
4. „Create“, dann „Add a release“: dieselbe `.pbw`, Release Notes aus
   `RELEASE_NOTES.md`. Seite neu laden, neben dem Release auf „Publish“.
5. „Manage Asset Collections“ → für **jede** der drei Plattformen eine
   anlegen: Description aus `description_en.txt` (ab Zeile 2), die
   Screenshots des passenden Ordners in der Reihenfolge der Dateinamen,
   dazu `banner_720x320.png`.
6. Oben auf **„Publish“**.

## Hinweis zur Source-Code-URL

Das Portal verlangt dieses Feld. Du wolltest keinen Quellcode-Link in der
Listung — dann gibt es zwei Wege:

- Repository öffentlich stellen und
  `https://github.com/n0va-SIDEffects/Pebble-Panasonic-PTZ-Kamera` eintragen.
- Oder eine andere gültige `https://`-Adresse eintragen, etwa eine
  Projekt- oder Kontaktseite.

Ein Link auf ein privates Repository führt Nutzer ins Leere — das ist die
schlechteste der drei Möglichkeiten.

## Updates später

`version` in `package.json` erhöhen (Format `Major.Minor`, also `1.0`
und nicht `1.0.0`), dann:

```bash
pebble build
pebble publish --release-notes "..."
```

Die **UUID darf sich nie ändern**, sonst gilt das Update als neue App.

## Vor dem Absenden prüfen

- [ ] Version ist `0.9`, nicht `0.9.0`
- [ ] `icon_80.png` ohne Alphakanal
- [ ] Beschreibung unter 1600 Zeichen
- [ ] Alle drei Asset Collections angelegt
- [ ] Die `.pbw` einmal auf der echten Uhr installiert und bedient
