#!/usr/bin/env python3
"""
Werkbank-Banner (720 x 320) fuer den Pebble Appstore.

Immer gleich (Wiedererkennung): Schneidematte auf der Holzplatte, die
festen Werkzeuge (Teppichmesser, zwei Feinschraubendreher, Loetkolben),
die Pebble rechts mit dem Screenshot im Display, Titel oben links, das
SIDE-effect's-Logo dezent im Bild.

Anders je Banner: das Projekt in der Mitte, die Akzentfarbe, und ueber
--seed die genaue Anordnung der Werkzeuge - leicht verschoben und
verdreht, so wie ein Schreibtisch nie zweimal gleich aussieht.

    python3 make_desk_banner.py --projekt theremin \
        --shot store/release/screenshots_en/03_playing_sine.png \
        --titel "Theremin" --unterzeile "Play it with your wrist" \
        --out out/banner_theremin.png
"""
import argparse
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)

import scene
import uhren
from render import data_uri, font_uri, rendern, W, H

# Uhraufnahmen und Logo liegen neben diesem Skript, damit das Banner ohne
# weitere Ablage reproduzierbar ist. Ein Ordner aus dem pebble-publish-Skill
# laesst sich mit --assets stattdessen einhaengen.
UHREN = os.path.join(HIER, "assets")
KI_ORDNER = os.path.join(HIER, "ki")


def ki_manifest():
    """Was an KI-Assets vorliegt. Fehlt der Ordner, wird gezeichnet."""
    pfad = os.path.join(KI_ORDNER, "manifest.json")
    if not os.path.exists(pfad):
        return {}
    with open(pfad, encoding="utf-8") as f:
        eintraege = json.load(f)
    fertig = {}
    for name, eintrag in eintraege.items():
        if name.startswith("_"):
            continue
        if "dateien" in eintrag:
            da = [d for d in eintrag["dateien"]
                  if os.path.exists(os.path.join(KI_ORDNER, d))]
            if da:
                fertig[name] = dict(eintrag, dateien=da)
        elif os.path.exists(os.path.join(KI_ORDNER, eintrag["datei"])):
            fertig[name] = eintrag
    return fertig


def ki_bild(eintrag, breite=None, dreh=0, logo_uri=None, zufall=None):
    """
    Ein KI-Asset als SVG-Gruppe, um die eigene Mitte gelegt - genau wie
    die gezeichneten Werkzeuge, damit beide durch dieselben Plaetze
    laufen. Traegt das Asset ein Logo, kommt es gleich mit hinein.

    Stehen unter "dateien" mehrere Fassungen (die volle Tasse, die halbe,
    die leere, der ueberquellende Aschenbecher), waehlt der Seed eine aus
    - dieselbe Stelle im Bild, jedes Mal ein anderes Detail.
    """
    dateien = eintrag.get("dateien")
    if dateien:
        datei = (zufall or random).choice(dateien)
    else:
        datei = eintrag["datei"]
    bild = Image.open(os.path.join(KI_ORDNER, datei)).convert("RGBA")
    b = breite or eintrag.get("breite", 160)
    h = b * bild.height / bild.width
    dreh = eintrag.get("dreh", 0) + dreh
    logo = ""
    platz = eintrag.get("logo")
    if logo_uri and platz:
        lb = platz["breite"] * b
        logo = logo_auf_geraet(logo_uri, {
            "x": -b / 2 + platz["x"] * b, "y": -h / 2 + platz["y"] * h,
            "breite": lb, "stil": platz.get("stil", "gravur_holz")})
    innen = (f'<image href="{data_uri(bild)}" x="{-b/2:.1f}" y="{-h/2:.1f}" '
             f'width="{b:.1f}" height="{h:.1f}"/>{logo}')
    if dreh:
        innen = f'<g transform="rotate({dreh})">{innen}</g>'
    return f'<g filter="url(#schatten_weich)">{innen}</g>'


def ki_untergrund(eintrag, zufall=None):
    """
    Tischbild als Hintergrund. Liegen mehrere Tische vor, waehlt der Seed
    einen davon - so wechselt auch der Untergrund von App zu App.
    """
    dateien = eintrag.get("dateien")
    datei = (zufall or random).choice(dateien) if dateien else eintrag["datei"]
    bild = Image.open(os.path.join(KI_ORDNER, datei)).convert("RGB")
    zoom = eintrag.get("zoom", 1.0)
    b = W * zoom
    h = b * bild.height / bild.width
    return (f'<image href="{data_uri(bild)}" x="{eintrag.get("x", 0)}" '
            f'y="{eintrag.get("y", 0)}" width="{b:.1f}" height="{h:.1f}" '
            f'preserveAspectRatio="xMidYMid slice"/>')

SCHRIFTEN = {
    "titel": os.path.join(HIER, "fonts/archivo_black.ttf"),
    "schmal": os.path.join(HIER, "fonts/barlow_cond_700.ttf"),
    "mono": os.path.join(HIER, "fonts/spacemono_700.ttf"),
    "stift": os.path.join(HIER, "fonts/marker.ttf"),
}

# Akzentfarbe je Projekt: klar unterscheidbar, damit die Banner in der
# Store-Liste nebeneinander nicht verschwimmen.
_LAGE = {}

LOGO_ARTEN = ["geraet", "sticker", "plakette", "kritzel", "stempel", "druck"]

# Jede App bekommt ihre eigene Erscheinungsform des Logos - das Logo ist
# immer da, aber nie zweimal gleich. Unbekannte Projekte bekommen eine
# Form zugelost, die ueber die Laufzeit stabil bleibt.
LOGO_JE_PROJEKT = {
    "theremin": "geraet",
    "ptz": "geraet",
    "helo": "geraet",
}

# Farbe des Logos je App. Grau ist nur eine Moeglichkeit von vieren.
LOGO_FARBE_JE_PROJEKT = {
    "theremin": "original",   # oranger Aufdruck auf dem Holzgehaeuse
    "ptz": "dunkel",          # dunkles Typenschild auf dem weissen Korpus
    "helo": "akzent",         # in der Akzentfarbe in die Frontplatte geaetzt
}

AKZENTE = {
    "theremin": "#35b6f0",
    "ptz": "#ff4d3d",
    "helo": "#14c9a4",
}


# Gehaeusefarben, die es wirklich gibt (Core Devices: Time 2 in schwarz
# und silber, jeweils mit farbigen Akzenten; Time Steel silber, schwarz,
# gold). Baender sind Wechselteile und duerfen frei variieren.
UHR_JE_PROJEKT = {
    "theremin": ("schwarz", "band_rot"),
    "ptz": ("silber", "band_blau"),
    "helo": ("schwarz", "band_gruen"),
}
UHR_KOMBIS = [
    ("schwarz", "band_schwarz"), ("schwarz", "band_rot"), ("schwarz", "band_sand"),
    ("silber", "band_blau"), ("silber", "band_weiss"), ("silber", "band_grau"),
    ("graphit", "band_orange"),
]


def uhr_mit_screenshot(shot_pfad, name="pebble_time_2", hoehe=360,
                       gehaeuse="schwarz", band="band_schwarz"):
    """
    Screenshot in die Displayflaeche der Aufnahme setzen - eckig wie bei
    der Time 2, oder in die Ellipse einer runden Uhr. Die Form bleibt
    immer die echte Aufnahme, umgerechnet wird hoechstens die Farbe.
    """
    with open(os.path.join(UHREN, "uhren.json"), encoding="utf-8") as f:
        meta = json.load(f)[name]

    if meta.get("rund"):
        uhr = Image.open(os.path.join(UHREN, meta["datei"])).convert("RGBA")
        uhr = _rundes_display(uhr, meta, Image.open(shot_pfad).convert("RGBA"))
    else:
        uhr = uhren.variante(name, gehaeuse, band)
        x0, y0, x1, y1 = meta["display"]
        dw, dh = x1 - x0 + 1, y1 - y0 + 1
        shot = Image.open(shot_pfad).convert("RGBA")
        innen = Image.new("RGBA", (dw, dh), (0, 0, 0, 255))
        sh = shot.resize((dw, max(1, round(dw * shot.height / shot.width))), Image.LANCZOS)
        if sh.height > dh:
            rand = (sh.height - dh) // 2
            sh = sh.crop((0, rand, sh.width, rand + dh))
        innen.alpha_composite(sh, (0, (dh - sh.height) // 2))
        maske = Image.new("L", (dw, dh), 0)
        ImageDraw.Draw(maske).rounded_rectangle([0, 0, dw - 1, dh - 1], meta["eckradius"], fill=255)
        uhr.paste(innen, (x0, y0), maske)

    return uhr.resize((max(1, round(uhr.width * hoehe / uhr.height)), hoehe), Image.LANCZOS)


def _rundes_display(uhr, meta, shot):
    """
    Screenshot in das runde Display einer Round 2 setzen. Die Aufnahme ist
    schraeg, das runde Display erscheint also als gekippte Ellipse - der
    Screenshot wird entsprechend gestaucht und mitgedreht, sonst klebt er
    wie ein Aufkleber auf dem Glas.
    """
    e = meta["display_ellipse"]
    seite = min(shot.size)
    shot = shot.crop(((shot.width - seite) // 2, (shot.height - seite) // 2,
                      (shot.width + seite) // 2, (shot.height + seite) // 2))

    breite, hoehe = int(2 * e["b"]), int(2 * e["a"])
    flaeche = Image.new("RGBA", (breite, hoehe), (0, 0, 0, 0))
    flaeche.alpha_composite(shot.resize((breite, hoehe), Image.LANCZOS))
    maske = Image.new("L", (breite, hoehe), 0)
    ImageDraw.Draw(maske).ellipse([0, 0, breite - 1, hoehe - 1], fill=255)
    flaeche.putalpha(maske)

    gedreht = flaeche.rotate(e["winkel"] - 90, expand=True, resample=Image.BICUBIC)
    uhr = uhr.copy()
    uhr.alpha_composite(gedreht, (int(e["cx"] - gedreht.width / 2),
                                  int(e["cy"] - gedreht.height / 2)))
    return uhr


def logo_freistellen(pfad):
    """Weissen Hintergrund des Logo-PNG transparent machen und zuschneiden."""
    logo = Image.open(pfad).convert("RGBA")
    px = logo.load()
    for y in range(logo.height):
        for x in range(logo.width):
            r, g, b, a = px[x, y]
            if r > 235 and g > 235 and b > 235:
                px[x, y] = (r, g, b, 0)
    kasten = logo.getbbox()
    return logo.crop(kasten) if kasten else logo


def passende_groesse(text, schrift_pfad, hoechstbreite, start, kleinste):
    """Groesste Schriftgroesse, mit der der Text noch in die Spalte passt."""
    from PIL import ImageFont
    groesse = start
    while groesse > kleinste:
        if ImageFont.truetype(schrift_pfad, groesse).getbbox(text)[2] <= hoechstbreite:
            break
        groesse -= 1
    return groesse


def geraetemaske(lage, rand=10):
    """
    Schwarze Silhouette des Geraets auf weissem Grund. ComfyUI veraendert
    beim maskierten Durchlauf nur das Weisse - das Geraet bleibt damit
    unangetastet, und an seiner Stelle entsteht auch kein Loch, das das
    Modell nach eigenem Gutduenken fuellt.
    """
    from PIL import ImageFilter, ImageOps
    ki = ki_manifest()
    name = lage.get("projekt")
    if name not in ki:
        return None
    eintrag = ki[name]
    bild = Image.open(os.path.join(KI_ORDNER, eintrag.get("datei") or
                                   eintrag["dateien"][0])).convert("RGBA")
    b = eintrag.get("breite", 160)
    h = round(b * bild.height / bild.width)
    silhouette = bild.resize((round(b), h), Image.LANCZOS).getchannel("A")
    silhouette = silhouette.point(lambda w: 255 if w > 12 else 0)
    silhouette = silhouette.filter(ImageFilter.MaxFilter(2 * rand + 1))
    gedreht = silhouette.rotate(-lage.get("pd", 0), expand=True, resample=Image.BICUBIC)

    maske = Image.new("L", (W, H), 255)
    maske.paste(ImageOps.invert(gedreht),
                (round(lage["px"] - gedreht.width / 2),
                 round(lage["py"] - gedreht.height / 2)),
                gedreht)
    return maske.filter(ImageFilter.GaussianBlur(3)).convert("RGB")


def logo_vorlage(projekt, logo_pfad, logo_farbe, akzent, ziel, rand=26):
    """
    Geraet mit aufgelegtem Logo als Vorlage fuer einen kurzen Durchlauf
    durchs Bildmodell.

    Aufgelegt sieht das Logo immer aufgeklebt aus - es hat weder die
    Woelbung des Gehaeuses noch dessen Licht. Ein Durchlauf mit kleiner
    Staerke, maskiert auf genau diese Stelle, backt es ins Material ein.
    Daneben entsteht die passende Maske: weiss nur ueber dem Logo.
    """
    from PIL import ImageFilter
    ki = ki_manifest()
    if projekt not in ki or "logo" not in ki[projekt]:
        raise SystemExit("Fuer " + projekt + " ist kein Logoplatz hinterlegt.")
    eintrag = ki[projekt]
    bild = Image.open(os.path.join(KI_ORDNER, eintrag.get("datei") or
                                   eintrag["dateien"][0])).convert("RGBA")

    # auf ein Vielfaches von 16 bringen, sonst stolpert der VAE
    bw = (bild.width + 15) // 16 * 16
    bh = (bild.height + 15) // 16 * 16
    grund = Image.new("RGBA", (bw, bh), (255, 255, 255, 255))
    grund.alpha_composite(bild, ((bw - bild.width) // 2, (bh - bild.height) // 2))

    platz = eintrag["logo"]
    logo = logo_faerben(logo_freistellen(logo_pfad), logo_farbe, akzent)
    lb = round(platz["breite"] * bild.width)
    logo = logo.resize((lb, max(1, round(lb * logo.height / logo.width))), Image.LANCZOS)
    x = round(platz["x"] * bild.width) + (bw - bild.width) // 2
    y = round(platz["y"] * bild.height) + (bh - bild.height) // 2
    grund.alpha_composite(logo, (x, y))
    grund.convert("RGB").save(ziel)

    maske = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(maske).rectangle(
        [x - rand, y - rand, x + logo.width + rand, y + logo.height + rand], fill=255)
    maske.filter(ImageFilter.GaussianBlur(rand / 3)).convert("RGB").save(
        os.path.splitext(ziel)[0] + "_maske.png")
    return ziel


def titelblock(titel, unterzeile, akzent, plattform):
    """
    Titel oben links. Die Spalte endet bei x = 330, dort beginnt das
    Teppichmesser - laengere Namen werden deshalb kleiner gesetzt statt
    ins Werkzeug zu laufen.
    """
    t_groesse = passende_groesse(titel, SCHRIFTEN["titel"], 284, 43, 26)
    u_groesse = passende_groesse(unterzeile or "", SCHRIFTEN["schmal"], 278, 21, 13)
    unter = ""
    if unterzeile:
        unter = (f'<text x="34" y="92" font-family="Schmal" font-size="{u_groesse}" fill="{akzent}" '
                 f'letter-spacing="0.6" stroke="#000" stroke-width="3" stroke-opacity="0.45">'
                 f'{unterzeile}</text>')
    return f"""
<g id="titel">
  <text x="34" y="64" font-family="Titel" font-size="{t_groesse}" fill="#f4f7fa"
        stroke="#000" stroke-width="5" stroke-opacity="0.55">{titel}</text>
  {unter}
  <g font-family="Mono" font-size="10.5" fill="#cfd8e2" opacity="0.8">
    <text x="35" y="115" stroke="#000" stroke-width="3" stroke-opacity="0.4">{plattform}</text>
  </g>
  <rect x="34" y="101" width="26" height="2.4" fill="{akzent}"/>
</g>
"""


def logo_sticker(uri, x, y, dreh, breite=118):
    """Logo als aufgeklebter Sticker."""
    rand = 9
    hoehe = round(breite * 0.41)
    return f"""
<g transform="translate({x},{y}) rotate({dreh})" filter="url(#schatten_klein)">
  <rect x="{-rand}" y="{-rand}" width="{breite + 2*rand}" height="{hoehe + 2*rand}" rx="7"
        fill="#f6f8fa"/>
  <rect x="{-rand}" y="{-rand}" width="{breite + 2*rand}" height="{hoehe + 2*rand}" rx="7"
        fill="none" stroke="#c8d0d8" stroke-width="1"/>
  <image href="{uri}" x="0" y="0" width="{breite}" height="{hoehe}"/>
</g>
"""


def logo_druck(uri, x, y, dreh, breite=150):
    """Logo als heller Siebdruck auf der Matte - am dezentesten."""
    hoehe = round(breite * 0.41)
    return f"""
<g transform="translate({x},{y}) rotate({dreh})" opacity="0.36">
  <image href="{uri}" x="0" y="0" width="{breite}" height="{hoehe}"
         style="filter:grayscale(1) brightness(2.6)"/>
</g>
"""


def logo_stempel(uri, x, y, dreh, akzent, breite=124):
    """
    Logo als Tintenstempel auf der Matte: schief, ungleichmaessig
    aufgedrueckt, in der Akzentfarbe. Sehr dezent und trotzdem gewollt.
    """
    hoehe = round(breite * 0.41)
    return f"""
<g transform="translate({x},{y}) rotate({dreh})">
  <g opacity="0.62">
    <image href="{uri}" x="0" y="0" width="{breite}" height="{hoehe}"
           style="filter:grayscale(1) brightness(0.25) sepia(1) saturate(6) hue-rotate(-20deg)"/>
  </g>
  <g opacity="0.5">
    <image href="{uri}" x="1.5" y="-1" width="{breite}" height="{hoehe}"
           style="filter:grayscale(1) brightness(2.2)"/>
  </g>
  <rect x="-6" y="-5" width="{breite+12}" height="{hoehe+10}" rx="4" fill="none"
        stroke="{akzent}" stroke-width="2" opacity="0.30" stroke-dasharray="7 5"/>
</g>
"""


def logo_plakette(uri, x, y, dreh, breite=104):
    """
    Logo als gelaserte Alu-Plakette, wie sie auf Selbstbaugeraeten klebt.
    Liegt lose auf der Matte.
    """
    hoehe = round(breite * 0.41)
    rand = 10
    pb, ph = breite + 2 * rand, hoehe + 2 * rand
    return f"""
<g transform="translate({x},{y}) rotate({dreh})" filter="url(#schatten_klein)">
  <rect x="{-rand}" y="{-rand}" width="{pb}" height="{ph}" rx="5" fill="#b9c1ca"/>
  <rect x="{-rand}" y="{-rand}" width="{pb}" height="{ph}" rx="5" fill="url(#stahl)" opacity="0.65"/>
  <rect x="{-rand+3}" y="{-rand+3}" width="{pb-6}" height="{ph-6}" rx="3" fill="none"
        stroke="#7c848e" stroke-width="1.2"/>
  <g fill="#8d959e">
    <circle cx="{-rand+6}" cy="{-rand+6}" r="2.2"/>
    <circle cx="{breite+rand-6}" cy="{-rand+6}" r="2.2"/>
    <circle cx="{-rand+6}" cy="{hoehe+rand-6}" r="2.2"/>
    <circle cx="{breite+rand-6}" cy="{hoehe+rand-6}" r="2.2"/>
  </g>
  <image href="{uri}" x="0" y="0" width="{breite}" height="{hoehe}"
         style="filter:grayscale(1) brightness(0.45) contrast(1.4)" opacity="0.85"/>
  <rect x="{-rand}" y="{-rand}" width="{pb}" height="{ph*0.4:.0f}" rx="5" fill="#fff" opacity="0.18"/>
</g>
"""


def logo_gekritzelt(uri, zufall, x, y, dreh, breite=104):
    """Logo als Zeichnung auf einem Notizzettel."""
    hoehe = round(breite * 0.41)
    zettel_b, zettel_h = breite + 22, hoehe + 46
    return f"""
<g transform="translate({x},{y}) rotate({dreh})" filter="url(#schatten_klein)">
  <rect width="{zettel_b}" height="{zettel_h}" rx="2" fill="#efe8d6"/>
  <rect width="{zettel_b}" height="{zettel_h}" rx="2" fill="none" stroke="#cdc4ac" stroke-width="1"/>
  <g stroke="#9fb0c4" stroke-width="0.7" opacity="0.45">
    <line x1="0" y1="16" x2="{zettel_b}" y2="16"/>
    <line x1="0" y1="{zettel_h-16}" x2="{zettel_b}" y2="{zettel_h-16}"/>
  </g>
  <image href="{uri}" x="11" y="{(zettel_h-hoehe)/2:.0f}" width="{breite}" height="{hoehe}"
         style="filter:grayscale(0.15) contrast(1.1)" opacity="0.92"/>
  <text x="11" y="{zettel_h-5}" font-family="Stift" font-size="11" fill="#39485b"
        opacity="0.8">SIDE effect&#39;s</text>
</g>
"""


def hex_zu_rgb(wert):
    wert = wert.lstrip("#")
    return tuple(int(wert[i:i + 2], 16) for i in (0, 2, 4))


def logo_faerben(logo, modus, akzent):
    """
    Das Logo ist orange mit schwarzen Linien. Grau war nur eine von
    mehreren Moeglichkeiten - hier sind die anderen:

    original  Orange und Schwarz wie im Original
    akzent    das Orange wird zur Akzentfarbe der App, Schwarz bleibt
    hell      alles hell, fuer dunkle Gehaeuse
    dunkel    alles dunkel, fuer helle Gehaeuse und fuer Gravuren
    """
    if modus == "original":
        return logo
    ziel = hex_zu_rgb(akzent) if modus == "akzent" else None
    logo = logo.copy()
    px = logo.load()
    for y in range(logo.height):
        for x in range(logo.width):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            orange = r > 140 and b < 110 and r > b + 70
            if modus == "akzent":
                if orange:
                    # Helligkeit des Originalpixels auf die Zielfarbe uebertragen,
                    # damit Kanten und Verlauf erhalten bleiben
                    f = (0.35 + 0.65 * (r / 255.0))
                    px[x, y] = (min(255, int(ziel[0] * f)), min(255, int(ziel[1] * f)),
                                min(255, int(ziel[2] * f)), a)
            elif modus == "hell":
                hell = max(r, g, b)
                wert = 235 if orange else min(255, 170 + hell // 3)
                px[x, y] = (wert, wert, min(255, wert + 6), a)
            elif modus == "dunkel":
                dunkel = 46 if orange else 26
                px[x, y] = (dunkel, dunkel, dunkel + 4, a)
    return logo


def logo_auf_geraet(uri, platz):
    """
    Logo direkt auf dem Geraet: gelasert, gedruckt, geaetzt. Die Farbe
    kommt schon im Bild an (siehe logo_faerben); hier entsteht nur noch
    die Praegung - ein versetzter Schatten und eine Lichtkante, damit das
    Logo im Material sitzt statt darauf zu schweben.
    """
    breite = platz["breite"]
    hoehe = breite * 0.41
    stil = platz.get("stil", "gravur_holz")
    x, y = platz["x"], platz["y"]

    if stil == "gravur_holz":
        return f"""
<g transform="translate({x},{y})">
  <image href="{uri}" x="0.7" y="1.1" width="{breite}" height="{hoehe:.1f}"
         style="filter:grayscale(1) brightness(0)" opacity="0.38"/>
  <image href="{uri}" x="0" y="0" width="{breite}" height="{hoehe:.1f}" opacity="0.88"/>
</g>
"""
    if stil == "druck_dunkel":
        return f"""
<g transform="translate({x},{y})">
  <image href="{uri}" x="0" y="0" width="{breite}" height="{hoehe:.1f}" opacity="0.82"/>
</g>
"""
    return f"""
<g transform="translate({x},{y})">
  <image href="{uri}" x="0" y="1" width="{breite}" height="{hoehe:.1f}"
         style="filter:grayscale(1) brightness(0)" opacity="0.4"/>
  <image href="{uri}" x="0" y="0" width="{breite}" height="{hoehe:.1f}" opacity="0.8"/>
</g>
"""


PLAETZE = [
    # name, x, y, Drehung, Streuung in x und y, Drehstreuung, Art.
    # Grosszuegige Zonen statt enger Punkte: was wirklich passt,
    # entscheidet ohnehin die Kollisionspruefung - sie braucht nur genug
    # Vorschlaege. Die Mitte gehoert dem Geraet.
    ("oben", 400, 58, -16, 46, 12, "lang"),
    ("unten", 290, 292, -4, 60, 8, "lang"),
    ("links", 62, 196, -80, 20, 14, "kurz"),
    ("linksunten", 96, 286, 12, 34, 18, "kurz"),
    ("rechts", 444, 206, 70, 22, 18, "kurz"),
    ("rechtsoben", 428, 118, 34, 26, 24, "kurz"),
    ("untenmitte", 340, 292, 8, 50, 14, "kurz"),
    ("kram_untenrechts", 452, 290, 0, 26, 0, "kram"),
    ("kram_links", 58, 250, 0, 22, 0, "kram"),
    ("kram_oben", 372, 36, 0, 40, 0, "kram"),
    ("kram_linksoben", 62, 142, 0, 22, 0, "kram"),
    ("kram_untenlinks", 150, 294, 0, 40, 0, "kram"),
]


def masse(eintrag, breite=None):
    """Breite und Hoehe eines Assets in Bannereinheiten."""
    b = breite or eintrag.get("breite", 160)
    datei = eintrag.get("datei") or eintrag["dateien"][0]
    bild = Image.open(os.path.join(KI_ORDNER, datei))
    return b, b * bild.height / bild.width


def silhouettenboxen(eintrag, x, y, breite=None, baender=7, luft=7):
    """
    Die Sperrflaeche eines Geraets, in waagerechte Baender zerlegt.

    Eine einzelne Box um das ganze Asset waere zu grob: beim Theremin
    ragt eine duenne Antenne nach oben, und die wuerde als Klotz die
    halbe Bannerhoehe blockieren. Band fuer Band gemessen bleibt nur
    gesperrt, wo wirklich etwas liegt.
    """
    import numpy as np
    b = breite or eintrag.get("breite", 160)
    datei = eintrag.get("datei") or eintrag["dateien"][0]
    bild = Image.open(os.path.join(KI_ORDNER, datei)).convert("RGBA")
    h = b * bild.height / bild.width
    alpha = np.asarray(bild.getchannel("A")) > 30

    boxen = []
    hoch = max(1, alpha.shape[0] // baender)
    for i in range(0, alpha.shape[0], hoch):
        streifen = alpha[i:i + hoch]
        spalten = np.nonzero(streifen.any(axis=0))[0]
        if not len(spalten):
            continue
        links = spalten[0] / bild.width * b - b / 2
        rechts = (spalten[-1] + 1) / bild.width * b - b / 2
        oben = i / bild.height * h - h / 2
        unten = min(i + hoch, alpha.shape[0]) / bild.height * h - h / 2
        boxen.append((x + links - luft, y + oben - luft,
                      x + rechts + luft, y + unten + luft))
    return boxen


def huellbox(x, y, dreh, b, h, luft=6):
    """
    Achsenparallele Huelle eines gedrehten Rechtecks. Bewusst grosszuegig:
    lieber ein Platz zu viel verworfen als zwei Werkzeuge, die sich
    beruehren.
    """
    bogen = math.radians(dreh)
    c, s = abs(math.cos(bogen)), abs(math.sin(bogen))
    bb = b * c + h * s + 2 * luft
    hh = b * s + h * c + 2 * luft
    return (x - bb / 2, y - hh / 2, x + bb / 2, y + hh / 2)


def stossen(a, b):
    """Ueberschneiden sich zwei Rechtecke?"""
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def tisch_decken(zufall, projekt, ki=None, belegt=None):
    """
    Werkzeuge auf die Plaetze verteilen, ohne dass sich etwas beruehrt.

    Jeder Kandidat bekommt seine Huellbox; stoesst sie an etwas schon
    Liegendes - Titel, Uhr, das Geraet oder ein anderes Werkzeug - wird
    der Platz verworfen und der naechste probiert. Lieber liegt ein
    Werkzeug weniger auf dem Tisch, als dass sich zwei ueberlappen.
    """
    ki = ki or {}
    belegt = list(belegt or [])
    vorrat = scene.werkzeug_vorrat()
    frei = {art: [p for p in PLAETZE if p[6] == art] for art in ("lang", "kurz", "kram")}
    for art in frei:
        zufall.shuffle(frei[art])

    gelegt = []

    def hinlegen(art, name, groesse, zeichnung, tiefe, flip="zufall", versuche=16):
        """Den ersten Platz nehmen, an dem das Stueck frei liegt."""
        b, h = groesse
        for platz in list(frei[art]):
            _, px_, py_, dreh0, streu, drehstreu, _ = platz
            for _ in range(versuche):
                x = px_ + zufall.uniform(-streu, streu)
                y = py_ + zufall.uniform(-streu, streu)
                dreh = dreh0 + zufall.uniform(-drehstreu, drehstreu)
                if flip == "zufall" and zufall.random() < 0.5:
                    dreh += 180
                elif isinstance(flip, (tuple, list)) and platz[0] in flip:
                    dreh += 180
                box = huellbox(x, y, dreh, b, h)
                if box[0] < 2 or box[1] < 2 or box[2] > W - 2 or box[3] > H - 2:
                    continue
                if any(stossen(box, anderes) for anderes in belegt):
                    continue
                belegt.append(box)
                frei[art].remove(platz)
                gelegt.append((tiefe, f'<g transform="translate({x:.0f},{y:.0f}) '
                                      f'rotate({dreh:.1f})">{zeichnung}</g>'))
                return True
        return False

    def stueck(name, ersatz_fn, breite):
        """Asset, wenn vorhanden - sonst die Zeichnung."""
        if name in ki:
            b, h = masse(ki[name], breite)
            return (b, h), ki_bild(ki[name], breite=breite, zufall=zufall)
        return (breite, breite * 0.32), ersatz_fn()

    # fester Bestand
    for name, ersatz, breite, art, flip in (
            ("messer", lambda: scene.teppichmesser(132), 132, "lang", "zufall"),
            ("loetkolben", lambda: scene.loetkolben(158), 158, "lang", ("oben",)),
            ("dreher_rot", lambda: scene.schraubendreher(112, "griff_rot"), 112, "kurz", "zufall"),
            ("dreher_blau", lambda: scene.schraubendreher(106, "griff_blau"), 106, "kurz", "zufall")):
        groesse, svg = stueck(name, ersatz, breite)
        hinlegen(art, name, groesse, svg, zufall.uniform(0.2, 0.9), flip=flip)

    # Gaeste
    fest = {"messer", "loetkolben", "dreher_rot", "dreher_blau"}
    gross = [n for n, (a, _) in vorrat.items() if a in ("lang", "kurz")]
    gross += [n for n, e in ki.items()
              if e.get("typ") in ("lang", "kurz") and n not in fest and n not in vorrat]
    zufall.shuffle(gross)
    offen = zufall.randint(2, 3)
    for name in gross:
        if offen <= 0:
            break
        art = ki[name]["typ"] if name in ki else vorrat[name][0]
        if name in ki:
            groesse = masse(ki[name])
            svg = ki_bild(ki[name], zufall=zufall)
        else:
            groesse, svg = (110, 36), vorrat[name][1](zufall)
        if hinlegen(art, name, groesse, svg, zufall.uniform(0.2, 0.9)):
            offen -= 1

    # Kleinteile
    kram = [n for n, (a, _) in vorrat.items() if a == "kram"]
    kram += [n for n, e in ki.items() if e.get("typ") == "kram" and n not in vorrat]
    zufall.shuffle(kram)
    for name in kram[:zufall.randint(3, 5)]:
        if name in ki:
            groesse = masse(ki[name])
            svg = ki_bild(ki[name], zufall=zufall)
        else:
            groesse, svg = (52, 52), vorrat[name][1](zufall)
        hinlegen("kram", name, groesse, svg, zufall.uniform(0.05, 0.18), flip="nie")

    return gelegt


def banner(projekt, shot, titel, unterzeile, plattform, logo_pfad, seed,
           akzent=None, logo_art="auto", uhr_name="pebble_time_2",
           logo_farbe="auto", ki_nutzen=True, uhr_farben="auto",
           nur_szene=False, szene_datei=None, ohne_geraet=False):
    zufall = random.Random(seed)
    akzent = akzent or AKZENTE.get(projekt, "#35b6f0")

    if uhr_farben == "auto":
        uhr_farben = UHR_JE_PROJEKT.get(
            projekt, UHR_KOMBIS[sum(ord(c) for c in projekt) % len(UHR_KOMBIS)])
    with open(os.path.join(UHREN, "uhren.json"), encoding="utf-8") as f:
        uhr_meta = json.load(f)[uhr_name]
    masse = uhr_meta.get("banner", {"hoehe": 352, "x": 608, "y": 150, "dreh": 9})
    uhr = uhr_mit_screenshot(shot, uhr_name, masse["hoehe"], uhr_farben[0], uhr_farben[1])
    uhr_uri = data_uri(uhr)
    uhr_b, uhr_h = uhr.size
    uhr_x = masse["x"] + zufall.uniform(-6, 6)
    uhr_y = masse["y"] + zufall.uniform(-8, 8)
    uhr_dreh = round(masse["dreh"] + zufall.uniform(-3.5, 3.5), 1)
    if not plattform:
        plattform = uhr_meta.get("anzeige", "PEBBLE") + "  \u00b7  WATCHAPP"

    logo_bild = logo_freistellen(logo_pfad)
    if logo_farbe == "auto":
        logo_farbe = LOGO_FARBE_JE_PROJEKT.get(projekt, "original")
    logo_uri = data_uri(logo_faerben(logo_bild, logo_farbe, akzent))
    schriften = {k: font_uri(v) for k, v in SCHRIFTEN.items()}

    if logo_art == "auto":
        logo_art = LOGO_JE_PROJEKT.get(projekt, "geraet")

    # Das Logo sitzt entweder auf dem Geraet selbst oder liegt als eigenes
    # Stueck auf dem Tisch.
    logo_im_geraet, logo_svg = "", ""
    wackel = zufall.uniform(-3, 3)
    if logo_art == "geraet" and projekt in scene.PROJEKT_LOGOPLATZ:
        logo_im_geraet = logo_auf_geraet(logo_uri, scene.PROJEKT_LOGOPLATZ[projekt])
    elif logo_art == "sticker":
        logo_svg = logo_sticker(logo_uri, 30, 250, -8 + wackel, 96)
    elif logo_art == "druck":
        logo_svg = logo_druck(logo_uri, 28, 250, -2 + wackel)
    elif logo_art == "stempel":
        logo_svg = logo_stempel(logo_uri, 34, 256, -7 + wackel, akzent)
    elif logo_art == "plakette":
        logo_svg = logo_plakette(logo_uri, 38, 252, -6 + wackel, 104)
    elif logo_art == "kritzel":
        logo_svg = logo_gekritzelt(logo_uri, zufall, 32, 212, -5 + wackel)
    else:
        logo_im_geraet = logo_auf_geraet(logo_uri, scene.PROJEKT_LOGOPLATZ[projekt])

    ki = ki_manifest() if ki_nutzen else {}
    logo_lage = None
    if projekt in ki:
        if nur_szene and logo_im_geraet:
            # Lage merken, damit das Logo spaeter an dieselbe Stelle kommt
            eintrag = ki[projekt]
            bild = Image.open(os.path.join(KI_ORDNER, eintrag.get("datei") or
                                           eintrag["dateien"][0]))
            b = eintrag.get("breite", 160)
            h = b * bild.height / bild.width
            platz = eintrag["logo"]
            logo_lage = {"x": -b / 2 + platz["x"] * b, "y": -h / 2 + platz["y"] * h,
                         "breite": platz["breite"] * b,
                         "stil": platz.get("stil", "gravur_holz")}
            logo_im_geraet = ""
        projekt_svg = ki_bild(ki[projekt], zufall=zufall,
                              logo_uri=logo_uri if logo_im_geraet else None)
        logo_im_geraet = ""
    else:
        projekt_svg = scene.PROJEKTE[projekt](akzent, logo_im_geraet)
    px = 268 + zufall.uniform(-8, 8)
    py = 190 + zufall.uniform(-6, 6)
    pd = zufall.uniform(-3, 3)

    # Werkzeuge und Geraet nach Tiefe stapeln: manches liegt unter dem
    # Geraet, manches darueber - das macht den Tisch erst unaufgeraeumt.
    szene_svg = ""
    nachtraegliches_logo = ""
    if szene_datei:
        with open(szene_datei, "rb") as f:
            szene_svg = (f'<image href="{data_uri(Image.open(szene_datei).convert("RGB"))}" '
                         f'x="0" y="0" width="{W}" height="{H}"/>')
        lage_datei = os.path.splitext(szene_datei)[0].replace("_veredelt", "") + ".json"
        if os.path.exists(lage_datei):
            with open(lage_datei, encoding="utf-8") as f:
                lage = json.load(f)
            ki_jetzt = ki_manifest()
            innen = ""
            if lage.get("ohne_geraet") and lage["projekt"] in ki_jetzt:
                innen = ki_bild(ki_jetzt[lage["projekt"]], logo_uri=logo_uri)
            elif lage.get("logo"):
                innen = logo_auf_geraet(logo_uri, lage["logo"])
            if innen:
                nachtraegliches_logo = (
                    f'<g transform="translate({lage["px"]},{lage["py"]}) '
                    f'rotate({lage["pd"]})">{innen}</g>')

    # Sperrflaechen, bevor das erste Werkzeug faellt: Titel, Uhr und das
    # Geraet. Das Thema der App gehoert in den Vordergrund und bleibt frei.
    belegt = [(16, 4, 350, 134),
              (uhr_x - uhr_b / 2 - 8, 0, W, H)]
    if projekt in ki:
        belegt += silhouettenboxen(ki[projekt], px, py)
    else:
        belegt.append(huellbox(px, py, pd, 240, 170, luft=10))
    stapel = tisch_decken(zufall, projekt, ki, belegt)
    if not ohne_geraet:
        stapel.append((0.5, f'<g transform="translate({px:.0f},{py:.0f}) '
                            f'rotate({pd:.1f})">{projekt_svg}</g>'))
    if logo_svg:
        stapel.append((0.22, logo_svg))
    if nur_szene:
        _LAGE.update({"px": round(px), "py": round(py), "pd": round(pd, 1),
                      "projekt": projekt, "ohne_geraet": bool(ohne_geraet)})
        if logo_lage:
            _LAGE["logo"] = logo_lage
    stapel.sort(key=lambda e: e[0])
    tisch = "\n".join(svg for _, svg in stapel)

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{scene.defs(schriften, akzent)}
{szene_svg if szene_svg else (ki_untergrund(ki["tisch"]) if "tisch" in ki else scene.untergrund() + scene.schneidematte(zufall))}
{'' if szene_svg else tisch}

<!-- Pebble: liegt obenauf, Armbaender laufen aus dem Bild -->
{'' if nur_szene else f'''<g transform="translate({uhr_x:.0f},{uhr_y:.0f}) rotate({uhr_dreh})" filter="url(#schatten_gross)">
  <image href="{uhr_uri}" x="{-uhr_b/2:.1f}" y="{-uhr_h/2:.1f}" width="{uhr_b}" height="{uhr_h}"/>
</g>'''}

<!-- Licht und Titel zuletzt -->
<rect width="{W}" height="{H}" fill="url(#lichtkegel)" style="mix-blend-mode:soft-light"/>
<rect width="{W}" height="{H}" fill="url(#lichtkegel)" opacity="0.55"/>
{nachtraegliches_logo}
{'' if nur_szene else titelblock(titel, unterzeile, akzent, plattform)}
</svg>
"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--projekt", required=True, choices=sorted(scene.PROJEKTE))
    p.add_argument("--shot", default="")
    p.add_argument("--titel", default="")
    p.add_argument("--unterzeile", default="")
    p.add_argument("--plattform", default="",
                   help="Zeile unter dem Titel; leer heisst: aus der Uhr ableiten")
    p.add_argument("--logo", default=os.path.join(HIER, "assets/side_effects_logo.png"))
    p.add_argument("--logo-art", default="auto",
                   choices=["auto"] + LOGO_ARTEN)
    p.add_argument("--logo-farbe", default="auto",
                   choices=["auto", "original", "akzent", "hell", "dunkel"])
    p.add_argument("--uhr-gehaeuse", default=None,
                   help="schwarz, silber, graphit, gold")
    p.add_argument("--uhr-band", default=None,
                   help="band_schwarz, band_rot, band_blau, band_weiss, "
                        "band_orange, band_gruen, band_grau, band_sand, band_leder")
    p.add_argument("--nur-szene", action="store_true",
                   help="ohne Uhr und Titel - Vorlage fuer den Durchlauf "
                        "durch das Bildmodell")
    p.add_argument("--logo-vorlage", action="store_true",
                   help="Geraet mit aufgelegtem Logo plus Maske ausgeben, um das "
                        "Logo per Bildmodell ins Material einzubacken")
    p.add_argument("--ohne-geraet", action="store_true",
                   help="mit --nur-szene: das Geraet weglassen, damit es beim "
                        "Durchlauf durchs Modell nicht umgedeutet wird")
    p.add_argument("--szene", default=None,
                   help="fertige (veredelte) Szene als Untergrund benutzen")
    p.add_argument("--gezeichnet", action="store_true",
                   help="KI-Assets ignorieren und alles zeichnen")
    p.add_argument("--akzent", default=None)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--uhr", default="pebble_time_2")
    p.add_argument("--assets", default=None,
                   help="Ordner mit uhren.json und den Uhraufnahmen")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    if a.assets:
        global UHREN
        UHREN = a.assets

    if not a.logo_vorlage and not (a.shot and a.titel):
        raise SystemExit("--shot und --titel werden gebraucht "
                         "(ausser bei --logo-vorlage)")

    if a.logo_vorlage:
        farbe = a.logo_farbe
        if farbe == "auto":
            farbe = LOGO_FARBE_JE_PROJEKT.get(a.projekt, "original")
        akzent = a.akzent or AKZENTE.get(a.projekt, "#35b6f0")
        logo_vorlage(a.projekt, a.logo, farbe, akzent, a.out)
        print("geschrieben:", a.out)
        print("Maske:", os.path.splitext(a.out)[0] + "_maske.png")
        return

    farben = "auto"
    if a.uhr_gehaeuse or a.uhr_band:
        vorgabe = UHR_JE_PROJEKT.get(a.projekt, ("schwarz", "band_schwarz"))
        farben = (a.uhr_gehaeuse or vorgabe[0], a.uhr_band or vorgabe[1])
    global _LAGE
    _LAGE = {}
    svg = banner(a.projekt, a.shot, a.titel, a.unterzeile, a.plattform, a.logo,
                 a.seed, a.akzent, a.logo_art, a.uhr, a.logo_farbe,
                 ki_nutzen=not a.gezeichnet, uhr_farben=farben,
                 nur_szene=a.nur_szene, szene_datei=a.szene,
                 ohne_geraet=a.ohne_geraet)
    rendern(svg, a.out)
    if a.nur_szene and _LAGE:
        stamm = os.path.splitext(a.out)[0]
        with open(stamm + ".json", "w", encoding="utf-8") as f:
            json.dump(_LAGE, f, indent=2)
        print("Lage notiert:", stamm + ".json")
        maske = geraetemaske(_LAGE)
        if maske:
            maske.save(stamm + "_maske.png")
            print("Maske geschrieben:", stamm + "_maske.png")
    print("geschrieben:", a.out)


if __name__ == "__main__":
    main()
