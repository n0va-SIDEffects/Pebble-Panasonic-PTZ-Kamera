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

from PIL import Image, ImageChops

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)

import scene
from render import data_uri, font_uri, rendern, W, H

# Uhraufnahmen und Logo liegen neben diesem Skript, damit das Banner ohne
# weitere Ablage reproduzierbar ist. Ein Ordner aus dem pebble-publish-Skill
# laesst sich mit --assets stattdessen einhaengen.
UHREN = os.path.join(HIER, "assets")

SCHRIFTEN = {
    "titel": os.path.join(HIER, "fonts/archivo_black.ttf"),
    "schmal": os.path.join(HIER, "fonts/barlow_cond_700.ttf"),
    "mono": os.path.join(HIER, "fonts/spacemono_700.ttf"),
    "stift": os.path.join(HIER, "fonts/marker.ttf"),
}

# Akzentfarbe je Projekt: klar unterscheidbar, damit die Banner in der
# Store-Liste nebeneinander nicht verschwimmen.
LOGO_ARTEN = ["sticker", "plakette", "kritzel", "stempel", "druck"]

# Jede App bekommt ihre eigene Erscheinungsform des Logos - das Logo ist
# immer da, aber nie zweimal gleich. Unbekannte Projekte bekommen eine
# Form zugelost, die ueber die Laufzeit stabil bleibt.
LOGO_JE_PROJEKT = {
    "theremin": "sticker",
    "ptz": "plakette",
    "helo": "stempel",
}

AKZENTE = {
    "theremin": "#35b6f0",
    "ptz": "#ff4d3d",
    "helo": "#14c9a4",
}


def uhr_mit_screenshot(shot_pfad, name="pebble_time_2", hoehe=360):
    """Screenshot in die Displayflaeche der freigestellten Aufnahme setzen."""
    with open(os.path.join(UHREN, "uhren.json"), encoding="utf-8") as f:
        meta = json.load(f)[name]
    uhr = Image.open(os.path.join(UHREN, meta["datei"])).convert("RGBA")
    x0, y0, x1, y1 = meta["display"]
    dw, dh = x1 - x0 + 1, y1 - y0 + 1

    shot = Image.open(shot_pfad).convert("RGBA")
    innen = Image.new("RGBA", (dw, dh), (0, 0, 0, 255))
    sh = shot.resize((dw, max(1, round(dw * shot.height / shot.width))), Image.LANCZOS)
    if sh.height > dh:
        rand = (sh.height - dh) // 2
        sh = sh.crop((0, rand, sh.width, rand + dh))
    innen.alpha_composite(sh, (0, (dh - sh.height) // 2))

    from PIL import ImageDraw
    maske = Image.new("L", (dw, dh), 0)
    ImageDraw.Draw(maske).rounded_rectangle([0, 0, dw - 1, dh - 1], meta["eckradius"], fill=255)
    uhr.paste(innen, (x0, y0), maske)
    return uhr.resize((max(1, round(uhr.width * hoehe / uhr.height)), hoehe), Image.LANCZOS)


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


def logo_plakette(uri, x, y, dreh, breite=116):
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


def banner(projekt, shot, titel, unterzeile, plattform, logo_pfad, seed,
           akzent=None, logo_art="sticker", uhr_name="pebble_time_2"):
    zufall = random.Random(seed)
    akzent = akzent or AKZENTE.get(projekt, "#35b6f0")

    uhr = uhr_mit_screenshot(shot, uhr_name, hoehe=352)
    uhr_uri = data_uri(uhr)
    uhr_b, uhr_h = uhr.size
    uhr_x = 608 + zufall.uniform(-6, 6)
    uhr_y = 150 + zufall.uniform(-8, 8)
    uhr_dreh = round(9 + zufall.uniform(-3.5, 3.5), 1)

    logo_uri = data_uri(logo_freistellen(logo_pfad))

    schriften = {k: font_uri(v) for k, v in SCHRIFTEN.items()}

    # Werkzeuge: feste Plaetze mit kleinem Spielraum, damit die Serie
    # wiedererkennbar bleibt und trotzdem jedes Banner anders liegt.
    def platz(x, y, dreh, streu=14, drehstreu=9):
        return (x + zufall.uniform(-streu, streu),
                y + zufall.uniform(-streu, streu),
                dreh + zufall.uniform(-drehstreu, drehstreu))

    mx, my, md = platz(424, 64, -17, 9, 7)          # Teppichmesser
    lx, ly, ld = platz(300, 288, -5, 16, 5)          # Loetkolben
    s1x, s1y, s1d = platz(462, 214, 64, 10, 12)      # Schraubendreher schmal
    s2x, s2y, s2d = platz(96, 186, -84, 8, 8)     # Schraubendreher zweiter
    zx, zy, zd = platz(438, 290, 0, 8, 0)           # Loetzinn
    kx, ky, _ = platz(366, 118, 0, 12, 0)            # Schrauben

    projekt_svg = scene.PROJEKTE[projekt](akzent)
    px, py, pd = platz(272, 196, 0, 8, 3)

    if logo_art == "auto":
        logo_art = LOGO_JE_PROJEKT.get(
            projekt, LOGO_ARTEN[sum(ord(c) for c in projekt) % len(LOGO_ARTEN)])
    wackel = zufall.uniform(-3, 3)
    if logo_art == "sticker":
        logo_svg = logo_sticker(logo_uri, 30, 250, -8 + wackel, 104)
    elif logo_art == "druck":
        logo_svg = logo_druck(logo_uri, 28, 250, -2 + wackel)
    elif logo_art == "stempel":
        logo_svg = logo_stempel(logo_uri, 34, 256, -7 + wackel, akzent)
    elif logo_art == "plakette":
        logo_svg = logo_plakette(logo_uri, 38, 252, -6 + wackel)
    else:
        logo_svg = logo_gekritzelt(logo_uri, zufall, 32, 212, -5 + wackel)

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{scene.defs(schriften, akzent)}
{scene.untergrund()}
{scene.schneidematte(zufall)}

<g transform="translate({zx:.0f},{zy:.0f})">{scene.loetzinn(28)}</g>
<g transform="translate({kx:.0f},{ky:.0f})">{scene.schrauben(zufall, 6)}</g>

<g transform="translate({lx:.0f},{ly:.0f}) rotate({ld:.1f})">{scene.loetkolben(196)}</g>
<g transform="translate({s2x:.0f},{s2y:.0f}) rotate({s2d:.1f})">{scene.schraubendreher(124, 'griff_blau')}</g>
<g transform="translate({px:.0f},{py:.0f}) rotate({pd:.1f})">{projekt_svg}</g>
<g transform="translate({s1x:.0f},{s1y:.0f}) rotate({s1d:.1f})">{scene.schraubendreher(132, 'griff_rot')}</g>
<g transform="translate({mx:.0f},{my:.0f}) rotate({md:.1f})">{scene.teppichmesser(148)}</g>

{logo_svg}

<!-- Pebble: liegt obenauf, Armbaender laufen aus dem Bild -->
<g transform="translate({uhr_x:.0f},{uhr_y:.0f}) rotate({uhr_dreh})" filter="url(#schatten_gross)">
  <image href="{uhr_uri}" x="{-uhr_b/2:.1f}" y="{-uhr_h/2:.1f}" width="{uhr_b}" height="{uhr_h}"/>
</g>

<!-- Licht und Titel zuletzt -->
<rect width="{W}" height="{H}" fill="url(#lichtkegel)" style="mix-blend-mode:soft-light"/>
<rect width="{W}" height="{H}" fill="url(#lichtkegel)" opacity="0.55"/>
{titelblock(titel, unterzeile, akzent, plattform)}
</svg>
"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--projekt", required=True, choices=sorted(scene.PROJEKTE))
    p.add_argument("--shot", required=True)
    p.add_argument("--titel", required=True)
    p.add_argument("--unterzeile", default="")
    p.add_argument("--plattform", default="PEBBLE TIME 2  ·  WATCHAPP")
    p.add_argument("--logo", default=os.path.join(HIER, "assets/side_effects_logo.png"))
    p.add_argument("--logo-art", default="auto",
                   choices=["auto"] + LOGO_ARTEN)
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

    svg = banner(a.projekt, a.shot, a.titel, a.unterzeile, a.plattform, a.logo,
                 a.seed, a.akzent, a.logo_art, a.uhr)
    rendern(svg, a.out)
    print("geschrieben:", a.out)


if __name__ == "__main__":
    main()
