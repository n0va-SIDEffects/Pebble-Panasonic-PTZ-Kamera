# Grafiken für die Store-Listung

| Datei | Größe | Format | Hinweis |
|-------|-------|--------|---------|
| icon_80.png | 80 × 80 | PNG **RGB ohne Alpha** | Pflichtfeld im Portal (2026) |
| icon_144.png / icon_48.png | 144 × 144 / 48 × 48 | PNG | „Large/Small Icon“, falls abgefragt |
| menu_icon.png | 25 × 25 | PNG | Launcher der Uhr, in `resources/images/`, `"menuIcon": true` in package.json |
| banner_720x320.png | 720 × 320 | PNG | Marketing-Banner, Kopfbild der Listung |
| Screenshots | native Auflösung | PNG oder GIF | max. 5 pro Plattform |

Native Auflösungen: emery (Pebble Time 2) 200 × 228, basalt/diorite/flint
144 × 168, chalk 180 × 180 rund, gabbro 260 × 260 rund.

## Icon-Gestaltung

- Ein Motiv, eine Hauptfarbe, ein Akzent. Bei 25 px überleben nur dicke
  Striche; deshalb für den Launcher eine vereinfachte Variante (weniger
  Elemente, dickere Linien) rendern statt nur zu verkleinern.
- Aus einem 1024-px-Master mit Pillow zeichnen und per LANCZOS verkleinern.
  Dicke Kurven als Polygon zwischen Ober- und Unterkante zeichnen oder
  3-fach überabtasten, `ImageDraw.line` mit großer Breite zackt.
- Für „ohne Alpha“: auf weißen Hintergrund kompositieren und als RGB
  speichern (`bg.alpha_composite(icon); bg.convert('RGB').save(...)`).
- Firmen-/Personenlogo nicht ins Icon; ins Banner, klein, unten links.
  Auf dunklem Grund die schwarzen Linien eines Logos aufhellen, aber
  charakteristische schwarze Elemente (z. B. ein X im Logo) unverändert
  lassen.

## SIDE effect's Logo im Banner (Vorgabe des Nutzers)

Das Logo (orangener Pac-Man mit schwarzem X, Schriftzug "SIDE effect's" mit
Pulslinie und Pfeil) liegt im Theremin-Repo unter
`store/icon/side_effects_logo.png`. So will der Nutzer es im Banner haben:

- **Position**: unten links, in voller Deckkraft, **kein Wasserzeichen**
  (das wurde ausprobiert und abgelehnt).
- **Größe**: 185 px breit (erst 120, dann 150, dann 185; "einen Tick
  größer" hieß jeweils ca. +25 %). Platzierung `x = 30`,
  `y = H - logo.height - 8`.
- **Aufbereitung**: weißen Hintergrund des PNG transparent machen
  (Pixel mit r, g, b > 235), dann `getbbox()`-Zuschnitt. Auf dunklem Grund
  nur den rechten Teil ab 42 % der Breite (Pulslinie, Schriftzug, Pfeil)
  von Schwarz auf Hellgrau (225, 232, 240) umfärben. **Der Pac-Man samt
  seinem schwarzen X bleibt unverändert.**
- **Keine Überlappung**: Hintergrundgrafik so legen, dass sie das Logo
  nicht berührt. Beim Theremin-Banner wurde die Welle per Phase (-0,73 rad)
  so verschoben, dass ihr Berg über dem Logo liegt.
- In Icons kommt das Logo nicht vor; Icons zeigen nur das App-Motiv.

## Banner-Layout, das funktioniert hat

Dunkler Grund (22,30,42), dezente Grafik als Hintergrund (Welle, Balken),
Icon oben links (110 px), Titel 42 pt fett weiß bei x = 166, Untertitel
20 pt in der Akzentfarbe, zwei bis drei Slogan-Zeilen 15 pt (die letzte in
der Akzentfarbe), rechts die Uhr, Logo 185 px breit unten links. Vorher dem
Nutzer 3–4 Layout-Richtungen als Übersicht zeigen und wählen lassen.

## Die Uhr im Banner: freigestellte Aufnahme (Standard)

In `assets/` liegen zwei freigestellte Aufnahmen echter Uhren, dazu das
Logo und die Masse in `uhren.json`:

| Datei | Uhr | Displayflaeche |
|---|---|---|
| `pebble_time_2.png` | Time 2, schwarz, 534 x 1009 | (97, 302, 436, 704), Eckradius 26 |
| `pebble_time_steel.png` | Time Steel, grau, 336 x 581 | (34, 138, 299, 449), Eckradius 20 |

**So will der Nutzer es.** Die Aufnahmen stammen von ihm selbst, sind also
frei verwendbar, und ein Banner damit sieht deutlich naeher am Produktfoto
aus als eine Zeichnung - der Vergleich am PTZ-Banner war eindeutig.
`scripts/make_banner.py` nimmt sie ohne weiteres Zutun (`--watch
pebble_time_2`, die Voreinstellung).

Die gezeichnete Variante (unten) bleibt fuer den Fall, dass fuer eine
Plattform keine Aufnahme vorliegt: `--watch drawn`, mit `--round` fuer
chalk und gabbro.

Screenshot in die Displayflaeche setzen: auf Displaybreite bringen,
Seitenverhaeltnis erhalten, Ecken mit dem angegebenen Radius maskieren.
Bei der schwarzen Time 2 auf dunklem Grund einen weichen hellen Schein
dahinterlegen, sonst verschwindet das Gehaeuse.

Eine weitere Uhr aufnehmen: freistellen (siehe unten), Datei nach
`assets/`, Eintrag in `uhren.json`.

## Gezeichnetes Gehaeuse (wenn keine Aufnahme vorliegt)

Liegt für eine Plattform keine freigestellte Aufnahme vor, zeichnet
`scripts/make_banner.py` das Gehäuse mit `--watch drawn`. Ein flacher
Rahmen um den Screenshot sieht daneben immer schlechter aus. Die Maße
(in Bannereinheiten, alles 3-fach überabgetastet):

- **Display** 150 px breit, Höhe aus dem Seitenverhältnis des Screenshots
  (emery 200 × 228 ergibt 171 px).
- **Rand** 15 px links und rechts, 25 px oben, 29 px unten. Ein Gehäuse mit
  überall gleichem Rand sieht falsch aus, unten ist mehr.
- **Gehäuse** abgerundetes Rechteck, Radius 26 px, 2 px helle Kante
  (120,128,142) um einen dunklen Korpus (26,29,36), darin eine vertiefte
  Displayfläche (8,9,12) mit 4 px Überstand und Radius 8.
- **Tasten** 22 × 8 px in (96,102,115): eine links auf halber Höhe, drei
  rechts bei −58, 0 und +58 px. Ohne sie wirkt es wie ein Telefon.
- **Armbänder** 56 % der Gehäusebreite, 9 % Verjüngung nach außen, Farbe
  (52,58,72), helle Kante links, dunkle rechts; sie laufen aus dem Bild,
  statt kurz vorher zu enden.
- **Schatten** dieselbe Form, 150 Alpha, 9 px Weichzeichnung, 4 px nach
  rechts und 8 px nach unten versetzt.
- **Neigung** 9° (`Image.rotate(..., expand=True)`), Mitte bei x = 590.
  Gerade (0°) wirkt wie im Schaufenster, gekippt wie getragen.
- **Rundes Display** (chalk, gabbro): Gehäuse als Ellipse, Screenshot
  quadratisch mittig beschneiden und kreisförmig maskieren.

Nicht überlappen lassen: Text endet bei x ≈ 430, die Uhr beginnt bei
x ≈ 490, Hintergrundgrafik und Logo bleiben darunter frei.
