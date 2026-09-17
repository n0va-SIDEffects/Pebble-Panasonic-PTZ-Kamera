#!/usr/bin/env python3
"""
Stellt die Uhr aus einer Werbegrafik frei und vermisst ihre Displayflaeche.

    python3 store/icon/freistellen.py pebble_watch_quelle.png

Schreibt `pebble_watch.png` (freigestellt, mit Alphakanal) und nennt die
Koordinaten der Displayflaeche. Die gehoeren als DISPLAY nach
make_banner.py - dort wird der Screenshot hineingesetzt.

Der Hintergrund wird nicht ueber einen Farbschwellwert entfernt, sondern
vom Bildrand aus geflutet. Sonst verschwindet das schwarze Display gleich
mit, wenn es der Hintergrundfarbe zu nahe kommt.
"""
from PIL import Image
from collections import deque
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
TOLERANZ = 18


def aehnlich(p, q, tol=TOLERANZ):
    return all(abs(a - b) <= tol for a, b in zip(p[:3], q[:3]))


def fluten(bild, passt, start_punkte):
    """Zusammenhaengende Flaeche ab den Startpunkten, solange passt() gilt."""
    W, H = bild.size
    px = bild.load()
    besucht = bytearray(W * H)
    q = deque()
    for x, y in start_punkte:
        if not besucht[y * W + x] and passt(px[x, y]):
            besucht[y * W + x] = 1
            q.append((x, y))
    treffer = []
    while q:
        x, y = q.popleft()
        treffer.append((x, y))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and not besucht[ny * W + nx]:
                if passt(px[nx, ny]):
                    besucht[ny * W + nx] = 1
                    q.append((nx, ny))
    return treffer


def freistellen(bild):
    W, H = bild.size
    px = bild.load()
    hintergrund = px[W - 3, 3]
    rand = ([(x, y) for x in range(W) for y in (0, H - 1)] +
            [(x, y) for y in range(H) for x in (0, W - 1)])
    for x, y in fluten(bild, lambda p: aehnlich(p, hintergrund), rand):
        px[x, y] = (0, 0, 0, 0)
    return bild.crop(bild.getbbox())


def display_vermessen(uhr):
    """Displayflaeche: die dunkle Insel in der Bildmitte."""
    W, H = uhr.size
    px = uhr.load()
    mitte = (W // 2, H // 2)
    if px[mitte][3] < 200:
        raise SystemExit("Bildmitte ist durchsichtig - ist das wirklich eine Uhr?")

    # Alles, was nicht heller Rahmen ist. Der Rahmen trennt das Display vom
    # ebenfalls dunklen Armband.
    def dunkel(p):
        return p[3] > 200 and not (p[0] > 60 and p[1] > 60 and p[2] > 60)

    treffer = fluten(uhr, dunkel, [mitte])
    xs = [x for x, _ in treffer]
    ys = [y for _, y in treffer]
    return min(xs), min(ys), max(xs), max(ys)


def main():
    quelle = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HIER, "pebble_watch_quelle.png")
    if not os.path.exists(quelle):
        raise SystemExit("Quellbild fehlt: " + quelle)

    bild = Image.open(quelle).convert("RGBA")

    # Werbegrafiken haben oft eine Textspalte neben der Uhr. Wenn die linke
    # Haelfte deutlich anders gefaerbt ist als die rechte, nur rechts nehmen.
    W, H = bild.size
    links, rechts = bild.getpixel((3, 3)), bild.getpixel((W - 3, 3))
    if not aehnlich(links, rechts, 30):
        bild = bild.crop((W // 2, 0, W, H))
        print("Linke Bildhaelfte verworfen (andere Hintergrundfarbe).")

    uhr = freistellen(bild)
    ziel = os.path.join(HIER, "pebble_watch.png")
    uhr.save(ziel)
    print("geschrieben:", ziel, uhr.size)

    x0, y0, x1, y1 = display_vermessen(uhr)
    print(f"\nDISPLAY = ({x0}, {y0}, {x1}, {y1})"
          f"   # {x1-x0+1} x {y1-y0+1}, Verhaeltnis {(x1-x0+1)/(y1-y0+1):.3f}")
    print("Diesen Wert in make_banner.py eintragen.")


if __name__ == "__main__":
    main()
