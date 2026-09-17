#!/usr/bin/env python3
"""
Baut das Store-Banner (720 x 320).

    python3 store/icon/make_banner.py

Zwei Vorgaben des Nutzers, die fuer jedes kuenftige Banner gelten:

1. Der Screenshot wird **in einer Pebble Time 2** gezeigt, nicht als
   nacktes Rechteck.
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


def pebble_time_2(shot, band=16):
    """
    Zeichnet den Screenshot in ein stilisiertes Pebble-Time-2-Gehaeuse.

    Rechteckiges Gehaeuse mit Metallrand, ein Knopf links, drei rechts,
    dazu die Bandansaetze. Dreifach ueberabgetastet, sonst zacken die
    Rundungen.

    `band` ist die Laenge der Bandansaetze. Wird sie so gross gewaehlt,
    dass das Band oben und unten aus dem Banner laeuft, wirkt der Anschnitt
    gewollt - ein Band, das mitten im Bild aufhoert, sieht abgeschnitten aus.
    """
    f = 3
    bezel_x, bezel_y = 12, 14

    W_ = shot.width + 2 * bezel_x
    H_ = shot.height + 2 * bezel_y
    ges_h = H_ + 2 * band

    lein = Image.new("RGBA", (W_ * f, ges_h * f), (0, 0, 0, 0))
    d = ImageDraw.Draw(lein)

    # Bandansaetze oben und unten, etwas schmaler als das Gehaeuse
    band_w = int(W_ * 0.54)
    bx = (W_ - band_w) // 2
    d.rounded_rectangle([bx * f, 0, (bx + band_w) * f, (band + 14) * f],
                        int(6 * f), fill=(48, 53, 62, 255))
    d.rounded_rectangle([bx * f, (ges_h - band - 14) * f, (bx + band_w) * f, ges_h * f],
                        int(6 * f), fill=(48, 53, 62, 255))

    # Gehaeuse
    oben = band * f
    unten = (band + H_) * f
    d.rounded_rectangle([0, oben, W_ * f, unten], int(14 * f), fill=(86, 93, 104, 255))
    # Schmaler heller Streifen oben als Lichtkante des Metalls
    d.rounded_rectangle([0, oben, W_ * f, oben + int(5 * f)], int(5 * f),
                        fill=(122, 130, 142, 255))
    # Displayfassung
    d.rounded_rectangle([int(6 * f), oben + int(7 * f), (W_ - 6) * f, unten - int(7 * f)],
                        int(9 * f), fill=(18, 20, 24, 255))

    # Knoepfe: einer links (Back), drei rechts (Auf, Select, Ab)
    mitte = oben + (unten - oben) // 2
    knopf = (150, 158, 170, 255)
    d.rounded_rectangle([-int(3 * f), mitte - int(13 * f), int(3 * f), mitte + int(13 * f)],
                        int(3 * f), fill=knopf)
    for dy in (-34, 0, 34):
        y0 = mitte + int((dy - 11) * f)
        y1 = mitte + int((dy + 11) * f)
        d.rounded_rectangle([(W_ - 3) * f, y0, (W_ + 3) * f, y1], int(3 * f), fill=knopf)

    gehaeuse = lein.resize((W_, ges_h), Image.LANCZOS)
    gehaeuse.alpha_composite(shot.convert("RGBA"), (bezel_x, band + bezel_y))
    return gehaeuse


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

    # Der Screenshot sitzt in einer Uhr, nicht in einem nackten Rahmen.
    shot_pfad = os.path.join(WURZEL, "release", "screenshots_emery", "1_motion.png")
    if not os.path.exists(shot_pfad):
        raise SystemExit("Screenshot fehlt: " + shot_pfad)

    shot = Image.open(shot_pfad).convert("RGBA")
    shot = shot.resize((int(shot.width * 0.78), int(shot.height * 0.78)), Image.LANCZOS)
    # Bandansaetze absichtlich laenger als das Banner hoch ist, damit sie
    # oben und unten sauber aus dem Bild laufen.
    uhr = pebble_time_2(shot, band=70)
    if uhr.height > H:
        ueber = (uhr.height - H) // 2
        uhr = uhr.crop((0, ueber, uhr.width, ueber + H))
    img.alpha_composite(uhr, (W - uhr.width - 44, (H - uhr.height) // 2))

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
