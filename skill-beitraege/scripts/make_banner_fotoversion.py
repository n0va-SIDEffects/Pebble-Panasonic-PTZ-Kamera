#!/usr/bin/env python3
"""
Baut ein Store-Banner (720 x 320) nach dem Layout aus references/assets.md.

    python3 make_banner.py --titel "PTZ Remote" \
        --untertitel "Panasonic PTZ from your wrist" \
        --zeile "Buttons or wrist tilt, with a dead-man switch." \
        --zeile "Presets, 8 cameras, still preview." \
        --screenshot store/release/screenshots_emery/1_motion.png \
        --icon store/icon/icon_144_alpha.png \
        --out banner_720x320.png

Der Screenshot wird in eine freigestellte Uhr aus ../assets gesetzt, die
Uhr leicht gekippt, das Logo unten links gesetzt. Fehlt das Logo, bricht
das Skript ab - ein Banner ohne Logo soll nicht entstehen.

Das Skript misst die Textbreiten und warnt, wenn Geschriebenes in die Uhr
laufen wuerde. Diese Pruefung ist der Grund, warum es sie gibt: Der
Ueberlauf faellt sonst erst im fertigen Banner auf.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import argparse
import json
import os

W, H = 720, 320
DARK = (22, 30, 42)
ACCENT = (240, 122, 40)
LIGHT = (238, 242, 247)
MUTED = (150, 162, 180)

HIER = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HIER), "assets")

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def schrift(pfad, groesse):
    try:
        return ImageFont.truetype(pfad, groesse)
    except OSError:
        return ImageFont.load_default()


def breite(text, pfad, groesse):
    return schrift(pfad, groesse).getbbox(text)[2]


def hintergrundbogen(img):
    """
    Grosse Kurve als Hintergrundmotiv, dreifach ueberabgetastet.

    Eine Akzentfarbe mit Teildeckkraft mischt sich auf dunklem Grund zu
    Braun. Deshalb die breite Kurve in hellem Grau mit wenig Deckkraft und
    darunter eine duenne, voll deckende Linie in der Akzentfarbe.
    """
    f = 3
    lein = Image.new("RGBA", (W * f, H * f), (0, 0, 0, 0))
    d = ImageDraw.Draw(lein)
    cx, cy = int(W * 0.72 * f), int(H * 1.30 * f)
    r = int(H * 1.02 * f)
    d.arc([cx - r, cy - r, cx + r, cy + r], 232, 308, fill=LIGHT + (26,), width=int(18 * f))
    r2 = int(H * 0.80 * f)
    d.arc([cx - r2, cy - r2, cx + r2, cy + r2], 228, 312, fill=ACCENT + (255,), width=int(3 * f))
    img.alpha_composite(lein.resize((W, H), Image.LANCZOS))


def uhr_mit_screenshot(uhr_name, shot, hoehe, neigung):
    """Screenshot in die Displayflaeche der freigestellten Uhr setzen."""
    with open(os.path.join(ASSETS, "uhren.json"), encoding="utf-8") as f:
        uhren = json.load(f)
    if uhr_name not in uhren:
        raise SystemExit("Unbekannte Uhr: " + uhr_name)
    meta = uhren[uhr_name]

    uhr = Image.open(os.path.join(ASSETS, meta["datei"])).convert("RGBA")
    x0, y0, x1, y1 = meta["display"]
    dw, dh = x1 - x0 + 1, y1 - y0 + 1

    innen = Image.new("RGBA", (dw, dh), (0, 0, 0, 255))
    sh = shot.resize((dw, max(1, round(dw * shot.height / shot.width))), Image.LANCZOS)
    if sh.height > dh:
        schnitt = (sh.height - dh) // 2
        sh = sh.crop((0, schnitt, sh.width, schnitt + dh))
    innen.alpha_composite(sh.convert("RGBA"), (0, (dh - sh.height) // 2))

    maske = Image.new("L", (dw, dh), 0)
    ImageDraw.Draw(maske).rounded_rectangle([0, 0, dw - 1, dh - 1], meta["eckradius"], fill=255)
    uhr.paste(innen, (x0, y0), maske)

    uhr = uhr.resize((max(1, round(uhr.width * hoehe / uhr.height)), hoehe), Image.LANCZOS)
    if neigung:
        # Erst den Screenshot einsetzen, dann drehen: so muss die
        # Displayflaeche nicht verzerrt werden. expand haelt die Ecken drin.
        uhr = uhr.rotate(neigung, resample=Image.BICUBIC, expand=True)
    return uhr, meta


def sichtbare_kante(uhr, links, y_von, y_bis):
    """Linkeste Spalte der Uhr, in der zwischen y_von und y_bis etwas steht."""
    y_von = max(0, min(uhr.height - 1, y_von))
    y_bis = max(y_von + 1, min(uhr.height, y_bis))
    alpha = uhr.split()[-1]
    for x in range(uhr.width):
        spalte = alpha.crop((x, y_von, x + 1, y_bis))
        if spalte.getextrema()[1] > 30:
            return links + x
    return links + uhr.width


def logo_aufbereiten(pfad, breite_px=185):
    """Weissen Grund entfernen, zuschneiden, rechten Teil aufhellen."""
    logo = Image.open(pfad).convert("RGBA")
    px = logo.load()
    for y in range(logo.height):
        for x in range(logo.width):
            r, g, b, a = px[x, y]
            if r > 235 and g > 235 and b > 235:
                px[x, y] = (r, g, b, 0)
    logo = logo.crop(logo.getbbox())
    grenze = int(logo.width * 0.42)
    px = logo.load()
    for y in range(logo.height):
        for x in range(grenze, logo.width):
            r, g, b, a = px[x, y]
            if a > 0 and r < 90 and g < 90 and b < 90:
                px[x, y] = (225, 232, 240, a)
    return logo.resize((breite_px, int(logo.height * breite_px / logo.width)), Image.LANCZOS)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--titel", required=True)
    p.add_argument("--untertitel", default="")
    p.add_argument("--zeile", action="append", default=[],
                   help="Sloganzeile, zweimal angeben (mehr wird eng)")
    p.add_argument("--screenshot", required=True)
    p.add_argument("--icon", help="Icon mit Alphakanal, wird auf 120 px gebracht")
    p.add_argument("--logo", default=os.path.join(ASSETS, "side_effects_logo.png"))
    p.add_argument("--uhr", default="pebble_time_2")
    p.add_argument("--uhrhoehe", type=int, default=340)
    p.add_argument("--neigung", type=float, default=-7)
    p.add_argument("--titelgroesse", type=int, default=0,
                   help="0 = automatisch so gross wie moeglich, hoechstens 52")
    p.add_argument("--out", default="banner_720x320.png")
    a = p.parse_args()

    if not os.path.exists(a.logo):
        raise SystemExit("Logo fehlt: " + a.logo + "\nEs gehoert auf jedes Banner.")
    if not os.path.exists(a.screenshot):
        raise SystemExit("Screenshot fehlt: " + a.screenshot)

    img = Image.new("RGBA", (W, H), DARK + (255,))
    hintergrundbogen(img)
    d = ImageDraw.Draw(img)

    uhr, meta = uhr_mit_screenshot(a.uhr, Image.open(a.screenshot), a.uhrhoehe, a.neigung)
    uhr_links = W - uhr.width - 40

    # Ein dunkles Gehaeuse verschwindet auf dunklem Grund.
    if meta.get("gehaeuse") == "schwarz":
        fleck = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        mx, my = W - uhr.width // 2 - 40, H // 2
        r = int(uhr.width * 0.62)
        ImageDraw.Draw(fleck).ellipse(
            [mx - r, my - int(r * 1.25), mx + r, my + int(r * 1.25)], fill=(150, 168, 195, 46))
        img.alpha_composite(fleck.filter(ImageFilter.GaussianBlur(58)))

    versatz = (H - uhr.height) // 2
    if versatz < 0:
        uhr = uhr.crop((0, -versatz, uhr.width, -versatz + H))
        versatz = 0
    img.alpha_composite(uhr, (uhr_links, versatz))

    # Icon 120 px oben links, Titel daneben.
    text_x = 42
    if a.icon and os.path.exists(a.icon):
        ic = Image.open(a.icon).convert("RGBA").resize((120, 120), Image.LANCZOS)
        img.alpha_composite(ic, (32, 26))
        text_x = 164

    # Titel so gross wie moeglich, aber nicht in die Uhr hinein. Die 52 pt
    # der Vorlage gelten fuer einen kurzen Namen.
    #
    # Massgeblich ist nicht der Rand des Uhrenbildes, sondern die erste
    # Spalte, in der auf Titelhoehe wirklich etwas zu sehen ist: Bei einer
    # gekippten Uhr sind die Ecken des Bildes leer, der Titel darf also
    # naeher heran, als die Bildbreite vermuten laesst.
    platz = sichtbare_kante(uhr, uhr_links, 46 - versatz, 118 - versatz) - text_x - 24
    groesse = a.titelgroesse
    if not groesse:
        groesse = 52
        while groesse > 24 and breite(a.titel, F_BOLD, groesse) > platz:
            groesse -= 1
        if groesse < 52:
            print(f"Titel auf {groesse} pt verkleinert, sonst liefe er in die Uhr.")
    elif breite(a.titel, F_BOLD, groesse) > platz:
        print(f"WARNUNG: Titel ist {breite(a.titel, F_BOLD, groesse)} px breit, "
              f"es passen {platz} px. Er laeuft in die Uhr.")

    d.text((text_x, 46), a.titel, font=schrift(F_BOLD, groesse), fill=LIGHT)
    if a.untertitel:
        d.text((text_x + 2, 106), a.untertitel, font=schrift(F_REG, 20), fill=ACCENT)

    for i, zeile in enumerate(a.zeile[:3]):
        if breite(zeile, F_REG, 15) > uhr_links - 42 - 16:
            print("WARNUNG: Sloganzeile laeuft in die Uhr: " + zeile)
        d.text((42, 162 + i * 24), zeile, font=schrift(F_REG, 15), fill=MUTED)

    logo = logo_aufbereiten(a.logo)
    if 162 + len(a.zeile[:3]) * 24 > H - logo.height - 8:
        print("WARNUNG: Sloganzeilen reichen bis ins Logo.")
    img.alpha_composite(logo, (30, H - logo.height - 8))

    img.convert("RGB").save(a.out)
    print("geschrieben:", a.out)


if __name__ == "__main__":
    main()
