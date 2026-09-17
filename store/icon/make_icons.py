#!/usr/bin/env python3
"""
Erzeugt alle Icon-Groessen aus einem gemeinsamen Master.

    python3 store/icon/make_icons.py

Motiv: eine PTZ-Kamera von der Seite unter einem Schwenkbogen mit zwei
Pfeilspitzen - Kamera plus Bewegung, die beiden Dinge, um die es geht.

Fuer den Launcher der Uhr (25 Pixel) wird nicht einfach verkleinert, sondern
eine eigene, vereinfachte Fassung gezeichnet: bei dieser Groesse ueberleben
nur wenige, dicke Formen.
"""
from PIL import Image, ImageDraw
import os

S = 1024
DARK = (26, 34, 48)
ACCENT = (240, 122, 40)     # SIDE effect's Orange
LIGHT = (238, 242, 247)
HIER = os.path.dirname(os.path.abspath(__file__))


def master():
    img = Image.new("RGBA", (S, S), DARK + (255,))
    d = ImageDraw.Draw(img)

    # Schwenkbogen mit Pfeilspitzen links und rechts
    d.arc([150, 170, 874, 894], 200, 340, fill=ACCENT, width=48)
    d.polygon([(138, 520), (206, 462), (206, 578)], fill=ACCENT)
    d.polygon([(886, 520), (818, 462), (818, 578)], fill=ACCENT)

    # Kameragehaeuse mit Objektiv nach rechts
    d.rounded_rectangle([320, 430, 620, 640], 30, fill=LIGHT)
    d.polygon([(620, 468), (772, 408), (772, 662), (620, 602)], fill=LIGHT)
    # Stativ
    d.rectangle([450, 640, 508, 726], fill=LIGHT)
    d.rounded_rectangle([360, 726, 598, 776], 16, fill=LIGHT)
    return img


def launcher_25():
    """
    Eigene Fassung fuer den Launcher.

    Bei 25 Pixeln zerfaellt der Schwenkbogen des grossen Icons zu einem
    Haken. Deshalb hier nur die Kamera, formatfuellend, flankiert von zwei
    massiven Dreiecken - die Bewegungsrichtung bleibt lesbar, ohne dass
    duenne Linien noetig waeren.
    """
    n = 200                       # gross zeichnen, dann verkleinern
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    B = (0, 0, 0, 255)

    # Kamera, mittig und gross
    d.rounded_rectangle([54, 62, 132, 126], 10, fill=B)
    d.polygon([(132, 72), (176, 52), (176, 136), (132, 116)], fill=B)
    d.rectangle([80, 126, 106, 156], fill=B)
    d.rounded_rectangle([56, 156, 130, 176], 6, fill=B)

    # Richtungspfeile auf Kamerahoehe
    d.polygon([(4, 94), (40, 62), (40, 126)], fill=B)
    return img.resize((25, 25), Image.LANCZOS)


def runde_ecken(img, radius_anteil=0.18):
    r = int(img.size[0] * radius_anteil)
    maske = Image.new("L", img.size, 0)
    ImageDraw.Draw(maske).rounded_rectangle([0, 0, img.size[0]-1, img.size[1]-1], r, fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), maske)
    return out


def main():
    m = master()
    m.save(os.path.join(HIER, "master_1024.png"))

    for groesse in (144, 80, 48):
        icon = runde_ecken(m.resize((groesse, groesse), Image.LANCZOS))
        icon.save(os.path.join(HIER, f"icon_{groesse}_alpha.png"))
        # Das Portal verlangt das 80er ohne Alphakanal.
        weiss = Image.new("RGBA", icon.size, (255, 255, 255, 255))
        weiss.alpha_composite(icon)
        weiss.convert("RGB").save(os.path.join(HIER, f"icon_{groesse}.png"))
        print(f"icon_{groesse}.png (RGB) und icon_{groesse}_alpha.png")

    launcher_25().save(os.path.join(HIER, "menu_icon_25.png"))
    print("menu_icon_25.png (eigene, vereinfachte Zeichnung)")


if __name__ == "__main__":
    main()
