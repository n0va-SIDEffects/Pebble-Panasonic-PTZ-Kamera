#!/usr/bin/env python3
"""
SVG -> PNG. Gerendert wird im Browser, weil er Verlaeufe, Filter und
Schatten sauber zeichnet; doppelte Aufloesung und Verkleinern per LANCZOS
nehmen die Treppen aus schraegen Kanten.
"""
import base64
import io
import os
import shutil
import subprocess
import tempfile

from PIL import Image

W, H = 720, 320
SCALE = 2


def browser_finden():
    """
    Chromium/Chrome suchen: erst die Umgebungsvariable BANNER_CHROME, dann
    der PATH, dann die ueblichen Installationsorte von Linux, macOS und
    Windows.
    """
    if os.environ.get("BANNER_CHROME"):
        return os.environ["BANNER_CHROME"]
    for name in ("chromium", "chromium-browser", "google-chrome",
                 "google-chrome-stable", "chrome", "msedge"):
        pfad = shutil.which(name)
        if pfad:
            return pfad
    kandidaten = [
        "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    ]
    for pfad in kandidaten:
        if os.path.exists(pfad):
            return pfad
    raise SystemExit(
        "Kein Chromium/Chrome gefunden. Pfad in BANNER_CHROME setzen, z. B.\n"
        '  set BANNER_CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"')


def data_uri(img):
    """PIL-Bild als base64-PNG-Datenquelle fuer SVG <image>."""
    puffer = io.BytesIO()
    img.save(puffer, "PNG")
    return "data:image/png;base64," + base64.b64encode(puffer.getvalue()).decode()


def font_uri(pfad):
    """Schriftdatei als base64, damit das SVG ohne Installation rendert."""
    with open(pfad, "rb") as f:
        return "data:font/ttf;base64," + base64.b64encode(f.read()).decode()


def rendern(svg, ziel, w=W, h=H, scale=SCALE):
    """SVG in eine HTML-Seite legen, abfotografieren, auf Zielgroesse bringen."""
    seite = ("<!doctype html><html><head><meta charset='utf-8'><style>"
             "html,body{margin:0;padding:0;background:#000;overflow:hidden}"
             "svg{display:block}</style></head><body>" + svg + "</body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        quelle = os.path.join(tmp, "banner.html")
        roh = os.path.join(tmp, "banner.png")
        with open(quelle, "w", encoding="utf-8") as f:
            f.write(seite)
        subprocess.run([
            browser_finden(), "--headless=new", "--no-sandbox", "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=%d" % scale,
            "--window-size=%d,%d" % (w, h),
            "--screenshot=" + roh, "--virtual-time-budget=2000",
            "file://" + quelle,
        ], check=True, capture_output=True)
        bild = Image.open(roh).convert("RGB")
    if bild.size != (w, h):
        bild = bild.resize((w, h), Image.LANCZOS)
    ordner = os.path.dirname(os.path.abspath(ziel))
    if ordner:
        os.makedirs(ordner, exist_ok=True)
    bild.save(ziel)
    return ziel
