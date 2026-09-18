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
- **Die Uhr.** Jede App zeigt die Pebble in einer anderen Farbe: Gehaeuse
  schwarz oder silber (beides offizielle Varianten von Core Devices),
  dazu ein Armband aus der Palette - Baender sind Wechselteile, die
  duerfen frei variieren. `--uhr-gehaeuse` und `--uhr-band` setzen es von
  Hand, sonst entscheidet die Zuordnung in `UHR_JE_PROJEKT`.
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
    --projekt theremin \
    --shot ../release/screenshots_en/03_playing_sine.png \
    --titel "Theremin" \
    --unterzeile "PLAY IT WITH YOUR WRIST" \
    --seed 7 \
    --out banner_720x320.png
```

| Schalter | Wirkung |
|---|---|
| `--projekt` | `theremin`, `ptz`, `helo` - das Geraet in der Mitte |
| `--shot` | Screenshot fuer das Display, in nativer Aufloesung |
| `--seed` | Anordnung der Werkzeuge; einfach durchprobieren |
| `--logo-art` | `auto` (Voreinstellung, Logo am Geraet) oder `geraet`, `sticker`, `plakette`, `kritzel`, `stempel`, `druck` |
| `--akzent` | Akzentfarbe ueberschreiben, z. B. `"#ff8a1e"` |
| `--uhr` | `pebble_time_2`, `pebble_time_steel`, `pebble_round_2_gold`, `pebble_round_2_schwarz` |
| `--plattform` | die kleine Zeile unter dem Titel; leer heisst: aus der Uhr ableiten |

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

## Farbvarianten der Uhr

Die Form kommt immer aus einer echten Aufnahme (`assets/`), nur die Farbe
wird umgerechnet: `uhren.py` nimmt die Helligkeit des Originals und legt
den Farbton der gewuenschten Variante darueber, Gehaeuse und Armband
getrennt, das Display bleibt ausgespart. Ein Bildmodell taugt dafuer
nicht - es kennt kein Pebble-Gehaeuse und erfindet eine beliebige
Smartwatch.

| | |
|---|---|
| Gehaeuse | `schwarz`, `silber`, `graphit`, `gold` |
| Baender | `band_schwarz`, `band_weiss`, `band_rot`, `band_blau`, `band_orange`, `band_gruen`, `band_grau`, `band_sand`, `band_leder` |

Jede Uhr bringt in `uhren.json` ihre eigenen Bannermasse mit (Hoehe,
Platz, Neigung) und den Namen fuer die Zeile unter dem Titel - eine
Round 2 ist breiter als eine Time 2 und wuerde sonst rechts aus dem Bild
laufen.

Runde Uhren (Round 2, Time Round) tragen statt `display` eine
`display_ellipse` mit Zentrum, Halbachsen und Winkel. Der Screenshot wird
darauf gestaucht und mitgedreht, damit er der Perspektive der Aufnahme
folgt statt wie ein Aufkleber auf dem Glas zu liegen.

Eine weitere Uhr aufnehmen: freistellen, nach `assets/`, Eintrag in
`assets/uhren.json` (Displayflaeche ausmessen, Bannermasse, `anzeige`,
`quelle`), und fuer die Umfaerbung in `uhren.GEHAEUSE` die beiden
Bildzeilen hinterlegen, zwischen denen das Gehaeuse sitzt.

Die Aufnahme sollte frontal sein, mit gestreckten Baendern, diffusem
Licht und dunklem Display - je schraeger das Foto, desto mehr sieht der
eingesetzte Screenshot nach Aufkleber aus. Welche Uhr zu welcher
SDK-Plattform gehoert, steht in `assets/uhren.json` unter `plattform`.

## Erzeugte Assets

Tisch, Werkzeuge und Kleinteile kommen aus einem Bildmodell. Was in
`ki/manifest.json` steht und als Datei vorliegt, benutzt das Banner
automatisch; `--gezeichnet` ignoriert alles davon und zeichnet wie
frueher. Der gemeinsame Stilbaustein steht in `assets_liste.json` unter
`stil` und steckt in jedem Prompt - ohne ihn passen die Teile nicht
zusammen.

### Mit der eigenen ComfyUI (der Weg, der nichts kostet)

`comfy_assets.py` spricht eine lokale ComfyUI ueber ihre API an.
`workflow_api.json` liegt fertig daneben: Z-Image-Turbo, aufgebaut nach
der offiziellen Vorlage `image_z_image_turbo` aus der Comfy-Galerie -
UNETLoader, CLIPLoader (qwen_3_4b, Typ lumina2), VAE, KSampler mit 8
Schritten, cfg 1, res_multistep/simple. Also einfach:

```bash
cd store/banner
python3 comfy_assets.py --server 127.0.0.1:8188
```

Heissen die Modelldateien bei dir anders (etwa die Int8-Variante), die
drei Namen oben in `workflow_api.json` anpassen. Und wer lieber seinen
eigenen Workflow fahren moechte: in ComfyUI **Workflow -> Export (API)**
und die Datei als `workflow_api.json` ablegen - das Skript sucht darin
selbst die Felder fuer Prompt, Groesse, Seed und Dateiname, egal welche
Nodes darin stehen.

Das Skript sucht im Workflow die Felder fuer Prompt, Bildgroesse, Seed
und Dateinamen, setzt pro Asset neue Werte ein, holt das fertige Bild ab
und stellt es frei. Ergebnisse landen in `ki/` als `roh_<name>.png` und
`a_<name>.png`. Was schon freigestellt vorliegt, wird uebersprungen;
`--neu` erzwingt einen neuen Durchgang, `--nur messer,pinzette` nimmt
einzelne Stuecke.

Helle Objekte bekommen in `assets_liste.json` `"hintergrund": "gruen"` -
vor Weiss laesst sich eine weisse Kamera nicht freistellen.

Was erzeugt wird, steht in `assets_liste.json`. Ein neues Stueck ist ein
Eintrag mehr: `was` beschreibt das Objekt, `seed` haelt es
reproduzierbar, `liegend: false` stellt es auf statt es hinzulegen.

### Ueber Hugging Face

`ki_assets.py` macht dasselbe mit Spaces auf Hugging Face, falls keine
ComfyUI zur Hand ist. Dafuer wird ein Token gebraucht (Typ Read,
huggingface.co/settings/tokens): entweder in `HF_TOKEN` oder als Datei
`store/banner/hf_token`. Die Datei steht in `.gitignore`. Die kostenlose
GPU-Quota reicht fuer wenige Bilder pro Tag.

## Voraussetzungen

- Python 3 mit Pillow (`pip install pillow`)
- Chromium, Chrome oder Edge. Wird automatisch gesucht; sonst den Pfad in
  `BANNER_CHROME` setzen.

## Dateien

```
make_desk_banner.py   Zusammenbau, Plaetze, Titel, Logo-Formen, Kommandozeile
scene.py              Tisch, Matte, Werkzeuge, Kleinkram, Projektgeraete
render.py             SVG -> PNG ueber den Browser, 2-fach ueberabgetastet
uhren.py              Farbvarianten der Pebble aus den echten Aufnahmen
comfy_assets.py       Bildteile mit der eigenen ComfyUI erzeugen
ki_assets.py          dasselbe ueber Hugging Face, wenn keine ComfyUI da ist
assets_liste.json     was erzeugt wird: Stil, Prompts, Groessen, Seeds
assets/               freigestellte Uhraufnahmen, uhren.json, Logo
ki/                   erzeugte Assets und ihr manifest.json
fonts/                eingebettete Schriften (siehe SCHRIFTEN.md)
```
