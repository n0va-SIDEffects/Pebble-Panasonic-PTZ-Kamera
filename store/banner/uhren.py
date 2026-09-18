#!/usr/bin/env python3
"""
Farbvarianten der Pebble aus den freigestellten Aufnahmen.

Das Bildmodell kennt kein Pebble-Gehaeuse - es erfindet eine beliebige
Smartwatch. Deshalb bleibt die Form die echte Aufnahme, und nur die
Farbe wird umgerechnet: Helligkeit des Originals rein, Farbton der
gewuenschten Variante raus. Gehaeuse und Armband getrennt, damit sich
beide unabhaengig kombinieren lassen.
"""
import colorsys
import json
import os

import numpy as np
from PIL import Image

HIER = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HIER, "assets")

# Wo bei welcher Aufnahme das Gehaeuse aufhoert und das Band anfaengt
# (aus der Breite pro Bildzeile ermittelt, siehe uhren.json).
GEHAEUSE = {
    "pebble_time_2": (199, 776),
    "pebble_time_steel": (174, 413),
}

# Farbrezepte: Farbton, Saettigung, dunkelster und hellster Wert.
# Ein mattes Silikonband hat wenig Spielraum nach oben, Metall viel.
FARBEN = {
    # Gehaeuse
    "schwarz":   (0.00, 0.00, 0.03, 0.62),
    "silber":    (0.58, 0.05, 0.26, 1.00),
    "graphit":   (0.60, 0.07, 0.10, 0.68),
    "gold":      (0.11, 0.42, 0.22, 1.00),
    # Baender
    "band_schwarz": (0.00, 0.00, 0.04, 0.60),
    "band_weiss":   (0.10, 0.04, 0.42, 1.00),
    "band_rot":     (0.99, 0.78, 0.16, 0.92),
    "band_blau":    (0.58, 0.72, 0.16, 0.92),
    "band_orange":  (0.07, 0.85, 0.20, 0.98),
    "band_gruen":   (0.36, 0.62, 0.14, 0.82),
    "band_grau":    (0.60, 0.06, 0.26, 0.78),
    "band_sand":    (0.09, 0.30, 0.34, 0.95),
    "band_leder":   (0.07, 0.55, 0.12, 0.70),
}


def _rezept(name):
    if name not in FARBEN:
        raise SystemExit("Unbekannte Farbe: " + name + "\nBekannt: " + ", ".join(FARBEN))
    return FARBEN[name]


def _einfaerben(rgb, maske, rezept):
    """Helligkeit behalten, Farbton ersetzen - nur wo die Maske greift."""
    h, s, v_min, v_max = rezept
    grau = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]) / 255.0
    # Das Original ist dunkel; die Wurzel hebt die Mitteltoene an, sonst
    # wird jede Farbe zu Schwarzrot oder Schwarzblau.
    v = v_min + (v_max - v_min) * np.power(np.clip(grau, 0, 1), 0.62)
    # Glanzlichter duerfen ausbleichen, sonst wirkt Silikon wie Plastilin
    s_pixel = s * (1.0 - 0.55 * np.clip((grau - 0.55) / 0.45, 0, 1))
    r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
    grund = np.stack([np.full_like(v, r), np.full_like(v, g), np.full_like(v, b)], axis=-1)
    bunt = (1.0 - s_pixel[..., None]) + grund * s_pixel[..., None]
    neu = np.clip(bunt * v[..., None] * 255.0, 0, 255)
    m = maske[..., None]
    return rgb * (1 - m) + neu * m


def variante(name, gehaeuse="schwarz", band="band_schwarz", weich=16):
    """
    Eine Aufnahme in der gewuenschten Kombination. Der Uebergang zwischen
    Gehaeuse und Band wird weich verlaufen, damit an der Bandbefestigung
    keine Kante entsteht.
    """
    with open(os.path.join(ASSETS, "uhren.json"), encoding="utf-8") as f:
        meta = json.load(f)[name]
    bild = Image.open(os.path.join(ASSETS, meta["datei"])).convert("RGBA")
    arr = np.asarray(bild).astype(np.float32)
    rgb, alpha = arr[..., :3], arr[..., 3]
    h = bild.height

    oben, unten = GEHAEUSE[name]
    zeile = np.arange(h, dtype=np.float32)
    # 1 im Gehaeuse, 0 im Band, dazwischen ein weicher Verlauf
    g_maske = (np.clip((zeile - (oben - weich)) / (2 * weich), 0, 1) *
               np.clip(((unten + weich) - zeile) / (2 * weich), 0, 1))
    g_maske = np.repeat(g_maske[:, None], bild.width, axis=1)
    sichtbar = (alpha > 8).astype(np.float32)

    # Display aussparen - der Screenshot kommt spaeter hinein
    x0, y0, x1, y1 = meta["display"]
    schirm = np.zeros((h, bild.width), dtype=np.float32)
    schirm[max(0, y0 - 6):y1 + 6, max(0, x0 - 6):x1 + 6] = 1.0

    rgb = _einfaerben(rgb, g_maske * sichtbar * (1 - schirm), _rezept(gehaeuse))
    rgb = _einfaerben(rgb, (1 - g_maske) * sichtbar * (1 - schirm), _rezept(band))

    neu = np.concatenate([rgb, alpha[..., None]], axis=-1).astype(np.uint8)
    return Image.fromarray(neu, "RGBA")
