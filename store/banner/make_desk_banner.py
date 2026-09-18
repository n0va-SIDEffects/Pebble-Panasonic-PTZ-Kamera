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


def ki_untergrund(eintrag):
    """Tischbild als Hintergrund, so skaliert dass die Matte das Bild fuellt."""
    bild = Image.open(os.path.join(KI_ORDNER, eintrag["datei"])).convert("RGB")
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
    ("oben", 426, 64, -17, 14, 10, "lang"),
    ("unten", 300, 294, -5, 22, 8, "lang"),
    ("links", 86, 208, -78, 12, 12, "kurz"),
    ("linksoben", 106, 182, -58, 10, 14, "kurz"),
    ("linksunten", 142, 292, 14, 16, 16, "kurz"),
    ("rechts", 458, 210, 66, 12, 16, "kurz"),
    ("kram_oben", 374, 120, 0, 18, 0, "kram"),
    ("kram_untenrechts", 452, 290, 0, 12, 0, "kram"),
    ("kram_untenlinks", 54, 292, 0, 10, 0, "kram"),
    ("kram_links", 58, 248, 0, 12, 0, "kram"),
]


def tisch_decken(zufall, projekt, ki=None):
    """
    Werkzeuge auf die Plaetze verteilen. Teppichmesser, Loetkolben und
    zwei Feinschraubendreher sind immer dabei - sie tragen die Serie.
    Dazu kommen ein bis zwei Stuecke aus dem Vorrat und zwei bis drei
    Kleinteile, damit kein Tisch wie der vorige aussieht.

    Werkzeuge duerfen um 180 Grad gedreht liegen; beim Loetkolben ist das
    keine Laune, sondern Pflicht: sein Kabel soll zum Bildrand laufen und
    nicht quer ueber das Geraet.
    """
    ki = ki or {}
    vorrat = scene.werkzeug_vorrat()
    frei = {art: [p for p in PLAETZE if p[6] == art] for art in ("lang", "kurz", "kram")}
    for art in frei:
        zufall.shuffle(frei[art])

    gelegt = []

    def hinlegen(art, zeichnung, tiefe, flip="zufall"):
        """flip: 'zufall', 'nie' oder eine Liste von Plaetzen, die kippen."""
        if not frei[art]:
            return None
        name, x, y, dreh, streu, drehstreu, _ = frei[art].pop()
        x += zufall.uniform(-streu, streu)
        y += zufall.uniform(-streu, streu)
        dreh += zufall.uniform(-drehstreu, drehstreu)
        if flip == "zufall":
            gekippt = zufall.random() < 0.5
        elif flip == "nie":
            gekippt = False
        else:
            gekippt = name in flip
        if gekippt:
            dreh += 180
        gelegt.append((tiefe, f'<g transform="translate({x:.0f},{y:.0f}) '
                              f'rotate({dreh:.1f})">{zeichnung}</g>'))
        return name

    def werkzeug(name, gezeichnet, groesse):
        """KI-Asset, wenn eines vorliegt - sonst die Zeichnung."""
        if name in ki:
            return ki_bild(ki[name], breite=groesse)
        return gezeichnet

    # fester Bestand
    hinlegen("lang", werkzeug("messer", scene.teppichmesser(136 + zufall.uniform(-8, 10)),
                              136 + zufall.uniform(-8, 10)), zufall.uniform(0.55, 0.9))
    hinlegen("lang", werkzeug("loetkolben", scene.loetkolben(178 + zufall.uniform(-10, 12)),
                              176 + zufall.uniform(-10, 12)), zufall.uniform(0.55, 0.9),
             flip=("oben",))
    hinlegen("kurz", werkzeug("dreher_rot",
                              scene.schraubendreher(120 + zufall.uniform(-8, 10), "griff_rot"),
                              120 + zufall.uniform(-8, 10)), zufall.uniform(0.2, 0.9))
    hinlegen("kurz", werkzeug("dreher_blau",
                              scene.schraubendreher(112 + zufall.uniform(-8, 10), "griff_blau"),
                              112 + zufall.uniform(-8, 10)), zufall.uniform(0.2, 0.9))

    # Gaeste aus dem Vorrat
    # Gaeste: erst schauen, ob es das Stueck als Asset gibt
    fest = {"messer", "loetkolben", "dreher_rot", "dreher_blau"}
    gross = [n for n, (art, _) in vorrat.items() if art in ("lang", "kurz")]
    gross += [n for n, e in ki.items()
              if e.get("typ") in ("lang", "kurz") and n not in fest and n not in vorrat]
    zufall.shuffle(gross)
    offen = zufall.randint(1, 2)
    for name in gross:
        if offen <= 0:
            break
        art = ki[name]["typ"] if name in ki else vorrat[name][0]
        if not frei[art]:
            continue
        stueck = (ki_bild(ki[name], zufall=zufall) if name in ki
                  else vorrat[name][1](zufall))
        if hinlegen(art, stueck, zufall.uniform(0.2, 0.9)):
            offen -= 1

    # Kleinteile
    kram = [n for n, (art, _) in vorrat.items() if art == "kram"]
    kram += [n for n, e in ki.items() if e.get("typ") == "kram" and n not in vorrat]
    zufall.shuffle(kram)
    for name in kram[:zufall.randint(2, 3)]:
        stueck = (ki_bild(ki[name], zufall=zufall) if name in ki
                  else vorrat[name][1](zufall))
        hinlegen("kram", stueck, zufall.uniform(0.05, 0.18), flip="nie")

    return gelegt


def banner(projekt, shot, titel, unterzeile, plattform, logo_pfad, seed,
           akzent=None, logo_art="auto", uhr_name="pebble_time_2",
           logo_farbe="auto", ki_nutzen=True, uhr_farben="auto",
           nur_szene=False):
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
    if projekt in ki:
        projekt_svg = ki_bild(ki[projekt], zufall=zufall,
                              logo_uri=logo_uri if logo_im_geraet else None)
        logo_im_geraet = ""
    else:
        projekt_svg = scene.PROJEKTE[projekt](akzent, logo_im_geraet)
    px = 272 + zufall.uniform(-10, 10)
    py = 196 + zufall.uniform(-8, 8)
    pd = zufall.uniform(-4, 4)

    # Werkzeuge und Geraet nach Tiefe stapeln: manches liegt unter dem
    # Geraet, manches darueber - das macht den Tisch erst unaufgeraeumt.
    stapel = tisch_decken(zufall, projekt, ki)
    stapel.append((0.5, f'<g transform="translate({px:.0f},{py:.0f}) '
                        f'rotate({pd:.1f})">{projekt_svg}</g>'))
    if logo_svg:
        stapel.append((0.22, logo_svg))
    stapel.sort(key=lambda e: e[0])
    tisch = "\n".join(svg for _, svg in stapel)

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{scene.defs(schriften, akzent)}
{ki_untergrund(ki["tisch"]) if "tisch" in ki else scene.untergrund() + scene.schneidematte(zufall)}
{tisch}

<!-- Pebble: liegt obenauf, Armbaender laufen aus dem Bild -->
{'' if nur_szene else f'''<g transform="translate({uhr_x:.0f},{uhr_y:.0f}) rotate({uhr_dreh})" filter="url(#schatten_gross)">
  <image href="{uhr_uri}" x="{-uhr_b/2:.1f}" y="{-uhr_h/2:.1f}" width="{uhr_b}" height="{uhr_h}"/>
</g>'''}

<!-- Licht und Titel zuletzt -->
<rect width="{W}" height="{H}" fill="url(#lichtkegel)" style="mix-blend-mode:soft-light"/>
<rect width="{W}" height="{H}" fill="url(#lichtkegel)" opacity="0.55"/>
{'' if nur_szene else titelblock(titel, unterzeile, akzent, plattform)}
</svg>
"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--projekt", required=True, choices=sorted(scene.PROJEKTE))
    p.add_argument("--shot", required=True)
    p.add_argument("--titel", required=True)
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

    farben = "auto"
    if a.uhr_gehaeuse or a.uhr_band:
        vorgabe = UHR_JE_PROJEKT.get(a.projekt, ("schwarz", "band_schwarz"))
        farben = (a.uhr_gehaeuse or vorgabe[0], a.uhr_band or vorgabe[1])
    svg = banner(a.projekt, a.shot, a.titel, a.unterzeile, a.plattform, a.logo,
                 a.seed, a.akzent, a.logo_art, a.uhr, a.logo_farbe,
                 ki_nutzen=not a.gezeichnet, uhr_farben=farben,
                 nur_szene=a.nur_szene)
    rendern(svg, a.out)
    print("geschrieben:", a.out)


if __name__ == "__main__":
    main()
