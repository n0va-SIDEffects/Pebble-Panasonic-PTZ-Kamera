#!/usr/bin/env python3
"""
Baut das Store-Banner (720 x 320).

    python3 store/icon/make_banner.py

Zwei Vorgaben des Nutzers, die fuer jedes kuenftige Banner gelten:

1. Der Screenshot wird **in einer Uhr** gezeigt, nicht als nacktes
   Rechteck. Grundlage ist die freigestellte Aufnahme des Nutzers in
   `pebble_watch.png`; der Screenshot wird in ihre Displayflaeche gesetzt.
2. Das SIDE effect's Logo ist **immer** dabei, unten links, 185 Pixel
   breit, in voller Deckkraft. Fehlt die Datei, bricht das Skript ab -
   ein Banner ohne Logo soll gar nicht erst entstehen.

Layout: dunkler Grund, ein grosser Schwenkbogen als Hintergrundmotiv,
links Icon, Titel und Slogan, rechts die Uhr mit dem Screenshot.
"""
from PIL import Image, ImageDraw, ImageFont
import os, sys, math

W, H = 720, 320
DARK = (22, 30, 42)
ACCENT = (240, 122, 40)
LIGHT = (238, 242, 247)
MUTED = (150, 162, 180)
HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(os.path.dirname(HIER)) if False else os.path.dirname(HIER)

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def schrift(pfad, groesse):
    try:
        return ImageFont.truetype(pfad, groesse)
    except OSError:
        return ImageFont.load_default()


def bogen(img):
    """
    Schwenkbogen als Hintergrundmotiv, dreifach ueberabgetastet.

    Orange mit Deckkraft unter hundert Prozent mischt sich auf dem dunklen
    Grund zu Braun - es sieht schmutzig aus, egal welcher Wert. Deshalb der
    breite Bogen in hellem Grau mit wenig Deckkraft und darunter eine
    duenne, voll deckende Linie in der Akzentfarbe.
    """
    f = 3
    lein = Image.new("RGBA", (W * f, H * f), (0, 0, 0, 0))
    d = ImageDraw.Draw(lein)
    cx, cy = int(W * 0.72 * f), int(H * 1.30 * f)

    r = int(H * 1.02 * f)
    d.arc([cx - r, cy - r, cx + r, cy + r], 232, 308,
          fill=LIGHT + (26,), width=int(18 * f))

    r2 = int(H * 0.80 * f)
    d.arc([cx - r2, cy - r2, cx + r2, cy + r2], 228, 312,
          fill=ACCENT + (255,), width=int(3 * f))

    img.alpha_composite(lein.resize((W, H), Image.LANCZOS))


# Displayflaeche in pebble_watch.png, ausgemessen an der freigestellten
# Aufnahme: links, oben, rechts, unten.
DISPLAY = (34, 138, 299, 449)
ECKRADIUS = 20


def uhr_mit_screenshot(shot, hoehe):
    """
    Setzt den Screenshot in die Displayflaeche der fotografierten Uhr.

    Der Screenshot wird auf die Displaybreite gebracht und mittig gesetzt;
    sein Seitenverhaeltnis bleibt erhalten, der schmale Rest oben und unten
    bleibt schwarz und faellt auf dem ohnehin schwarzen Display nicht auf.
    Die abgerundeten Ecken des Displays werden nachgebildet, sonst legt sich
    ein hartes Rechteck ueber die Rundung.
    """
    uhr = Image.open(os.path.join(HIER, "pebble_watch.png")).convert("RGBA")

    x0, y0, x1, y1 = DISPLAY
    dw, dh = x1 - x0 + 1, y1 - y0 + 1

    innen = Image.new("RGBA", (dw, dh), (0, 0, 0, 255))
    sh = shot.resize((dw, max(1, round(dw * shot.height / shot.width))), Image.LANCZOS)
    if sh.height > dh:
        schnitt = (sh.height - dh) // 2
        sh = sh.crop((0, schnitt, sh.width, schnitt + dh))
    innen.alpha_composite(sh.convert("RGBA"), (0, (dh - sh.height) // 2))

    maske = Image.new("L", (dw, dh), 0)
    ImageDraw.Draw(maske).rounded_rectangle([0, 0, dw - 1, dh - 1], ECKRADIUS, fill=255)
    uhr.paste(innen, (x0, y0), maske)

    breite = max(1, round(uhr.width * hoehe / uhr.height))
    return uhr.resize((breite, hoehe), Image.LANCZOS)


def main(logo_pfad=None):
    img = Image.new("RGBA", (W, H), DARK + (255,))
    bogen(img)
    d = ImageDraw.Draw(img)

    # Der Screenshot rechts belegt rund 250 Pixel. Alles Geschriebene
    # bleibt links davon - Text unter einem Bild ist der haeufigste Fehler
    # bei solchen Bannern.
    TEXT_MAX = 452

    icon = Image.open(os.path.join(HIER, "icon_144_alpha.png")).convert("RGBA")
    icon = icon.resize((88, 88), Image.LANCZOS)
    img.alpha_composite(icon, (40, 30))

    d.text((142, 38), "PTZ Remote", font=schrift(F_BOLD, 40), fill=LIGHT)
    d.text((144, 86), "Panasonic PTZ from your wrist",
           font=schrift(F_REG, 16), fill=ACCENT)

    zeilen = [
        "Buttons, or tilt the watch to drive the camera",
        "\u2014 select acts as a dead-man switch.",
        "Presets, up to 8 cameras, still preview.",
    ]
    y = 150
    for z in zeilen:
        d.text((42, y), z, font=schrift(F_REG, 15), fill=MUTED)
        y += 24

    # Der Screenshot sitzt in der Uhr, nicht in einem nackten Rahmen.
    shot_pfad = os.path.join(WURZEL, "release", "screenshots_emery", "1_motion.png")
    if not os.path.exists(shot_pfad):
        raise SystemExit("Screenshot fehlt: " + shot_pfad)

    # Hoeher als das Banner, damit die Armbaender oben und unten sauber aus
    # dem Bild laufen - ein Band, das mittendrin aufhoert, sieht abgeschnitten
    # aus statt angeschnitten.
    uhr = uhr_mit_screenshot(Image.open(shot_pfad), hoehe=372)
    versatz = (H - uhr.height) // 2
    if versatz < 0:
        uhr = uhr.crop((0, -versatz, uhr.width, -versatz + H))
        versatz = 0
    img.alpha_composite(uhr, (W - uhr.width - 40, versatz))

    # Das Logo gehoert auf jedes Banner, immer an dieselbe Stelle.
    if logo_pfad is None:
        logo_pfad = os.path.join(HIER, "side_effects_logo.png")
    if not os.path.exists(logo_pfad):
        raise SystemExit(
            "Logo fehlt: " + logo_pfad + "\n"
            "Es gehoert auf jedes Banner. Datei ablegen oder Pfad uebergeben.")
    logo = aufbereiten(Image.open(logo_pfad).convert("RGBA"))
    img.alpha_composite(logo, (30, H - logo.height - 8))

    ziel = os.path.join(HIER, "banner_720x320.png")
    img.convert("RGB").save(ziel)
    print("geschrieben:", ziel)


def aufbereiten(logo, breite=185):
    """Weissen Grund entfernen, zuschneiden, rechten Teil aufhellen."""
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
    hoehe = int(logo.height * breite / logo.width)
    return logo.resize((breite, hoehe), Image.LANCZOS)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
