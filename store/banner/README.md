# Store-Banner: die Werkbank-Serie

Ein Banner (720 x 320) fuer den Pebble Appstore, das fuer alle SIDE
effect's Apps gleich aufgebaut ist: Draufsicht auf den Basteltisch, auf
dem gerade genau diese App entsteht.

![Beispiel](banner_720x320.png)

## Was die Serie zusammenhaelt

| Element | Platz |
|---|---|
| Holzplatte mit Schneidematte | ganze Flaeche, Matte leicht schraeg |
| Titel, Unterzeile, Plattformzeile | oben links, auf dem freien Holz |
| Pebble mit dem Screenshot im Display | rechts, gekippt, Armbaender laufen aus dem Bild |
| Teppichmesser, Loetkolben | die beiden langen Plaetze oben und unten |
| Zwei Feinschraubendreher | zwei der mittleren Plaetze |
| Das Geraet der App | Bildmitte |
| SIDE effect's Logo | auf dem Geraet selbst |

## Was sich je App aendert

- **Das Geraet in der Bildmitte** - darum geht es.
- **Die Akzentfarbe** - Unterzeile, Leuchtpunkte, Strich unter dem Titel.
- **Die Form des Logos.** Voreingestellt traegt das Geraet es selbst:
  beim Theremin ins Holz gelasert, bei der PTZ-Kamera auf den Sockel
  gedruckt, beim HELO in die Frontplatte geaetzt. Es soll beim zweiten
  Hinsehen gefunden werden, nicht beim ersten. Wo das nicht passt, gibt
  es das Logo weiterhin als Aufkleber, Alu-Plakette, Notizzettel,
  Tintenstempel oder Siebdruck auf der Matte (`--logo-art`).
- **Der Tisch selbst.** `--seed` verteilt die Werkzeuge neu: welcher
  Platz belegt wird, in welcher Richtung ein Werkzeug liegt, was aus dem
  Vorrat dazukommt (Pinzette, Seitenschneider, Entloetpumpe, Bleistift,
  Messkabel) und welche Kleinteile herumliegen (Loetzinn, Schrauben,
  Widerstaende, Kabelbinder, Stiftleiste, Kaffeetasse). Gleicher Seed
  heisst gleiches Bild - das Banner bleibt reproduzierbar.

Ein paar Seeds durchprobieren lohnt sich; die Anordnungen unterscheiden
sich deutlich.

## Bauen

```bash
python3 make_desk_banner.py \
    --projekt ptz \
    --shot ../release/screenshots_emery/1_motion.png \
    --titel "PTZ Remote" \
    --unterzeile "PAN, TILT AND ZOOM FROM THE WRIST" \
    --seed 11 \
    --out banner_720x320.png
```

| Schalter | Wirkung |
|---|---|
| `--projekt` | `theremin`, `ptz`, `helo` - das Geraet in der Mitte |
| `--shot` | Screenshot fuer das Display, in nativer Aufloesung |
| `--seed` | Anordnung der Werkzeuge; einfach durchprobieren |
| `--logo-art` | `auto` (Voreinstellung, Logo am Geraet) oder `geraet`, `sticker`, `plakette`, `kritzel`, `stempel`, `druck` |
| `--akzent` | Akzentfarbe ueberschreiben, z. B. `"#ff8a1e"` |
| `--uhr` | `pebble_time_2` (Voreinstellung) oder `pebble_time_steel` |
| `--plattform` | die kleine Zeile unter dem Titel |

Fertiges Banner vor dem Release an seinen Platz kopieren:

```bash
cp banner_720x320.png ../release/banner_720x320.png
```

## Ein neues Projekt aufnehmen

1. In `scene.py` eine Funktion `projekt_<name>(akzent, logo="")` schreiben,
   die das Geraet um den Nullpunkt herum zeichnet (etwa 260 x 180
   Bannereinheiten). `{logo}` an der Stelle einsetzen, an der das
   Typenschild sitzen soll.
2. Den Namen in `PROJEKTE` eintragen und in `PROJEKT_LOGOPLATZ` festlegen,
   wo und wie das Logo auf dem Geraet sitzt (`gravur_holz`,
   `druck_dunkel` fuer helle Gehaeuse, `aetzung_hell` fuer dunkle).
3. In `make_desk_banner.py` eine Akzentfarbe in `AKZENTE` hinterlegen.

Ein neues Werkzeug kommt genauso dazu: zeichnen, entlang +x um die eigene
Mitte, und in `werkzeug_vorrat()` als `lang`, `kurz` oder `kram`
eintragen.

## Voraussetzungen

- Python 3 mit Pillow (`pip install pillow`)
- Chromium, Chrome oder Edge. Wird automatisch gesucht; sonst den Pfad in
  `BANNER_CHROME` setzen.

## Dateien

```
make_desk_banner.py   Zusammenbau, Plaetze, Titel, Logo-Formen, Kommandozeile
scene.py              Tisch, Matte, Werkzeuge, Kleinkram, Projektgeraete
render.py             SVG -> PNG ueber den Browser, 2-fach ueberabgetastet
assets/               freigestellte Uhraufnahmen, uhren.json, Logo
fonts/                eingebettete Schriften (siehe SCHRIFTEN.md)
```
