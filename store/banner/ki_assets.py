#!/usr/bin/env python3
"""
Assets fuer das Banner mit einem Bildmodell auf Hugging Face erzeugen und
freistellen.

Der Stilbaustein STIL steckt in jedem Prompt - nur so sehen die Teile
hinterher aus einem Guss aus. Ergebnisse landen in ki/ und werden von
Hand gesichtet; das Banner selbst baut weiterhin make_desk_banner.py.
"""
import os
import shutil
import sys

from gradio_client import Client, handle_file

HIER = os.path.dirname(os.path.abspath(__file__))
KI = os.path.join(HIER, "ki")
def _token():
    """
    Hugging-Face-Token aus der Umgebung, sonst aus einer Datei daneben.
    Das Token gehoert nicht ins Repo - hf_token steht in .gitignore.
    """
    if os.environ.get("HF_TOKEN"):
        return os.environ["HF_TOKEN"].strip()
    for pfad in (os.path.join(HIER, "hf_token"), os.path.join(os.path.dirname(HIER), "hf_token")):
        if os.path.exists(pfad):
            return open(pfad).read().strip()
    raise SystemExit("Kein Hugging-Face-Token. HF_TOKEN setzen oder in store/banner/hf_token legen.\n"
                     "Token erstellen: https://huggingface.co/settings/tokens (Typ Read)")


TOKEN = None

SCHNELL = "black-forest-labs/FLUX.1-schnell"
QWEN = "Qwen/Qwen-Image"
FREISTELLEN = "not-lain/background-removal"

# Gemeinsamer Stil aller Assets: flache Illustration, kraeftige Kanten,
# gedaempfte Farben - passt zum Pebble-Charme und bleibt bei 720 px lesbar.
STIL = ("flat vector illustration, bold clean dark outlines, limited muted color palette, "
        "soft cel shading, simple shapes, technical illustration, no text, no watermark")

FREI = "centered on a plain pure white background, full object visible, no shadow"


def erzeugen(prompt, datei, breite=768, hoehe=768, seed=7, space=SCHNELL, schritte=4):
    ziel = os.path.join(KI, datei)
    os.makedirs(KI, exist_ok=True)
    c = Client(space, token=_token(), verbose=False)
    if space == SCHNELL:
        ergebnis = c.predict(prompt=prompt, seed=seed, randomize_seed=False,
                             width=breite, height=hoehe, num_inference_steps=schritte,
                             api_name="/infer")
    else:
        ergebnis = c.predict(prompt=prompt, seed=seed, randomize_seed=False,
                             width=breite, height=hoehe, api_name="/infer")
    quelle = ergebnis[0] if isinstance(ergebnis, (list, tuple)) else ergebnis
    if isinstance(quelle, dict):
        quelle = quelle.get("path") or quelle.get("url")
    shutil.copy(quelle, ziel)
    return ziel


def freistellen(pfad, datei):
    """Hintergrund per BiRefNet entfernen, Ergebnis als transparentes PNG."""
    ziel = os.path.join(KI, datei)
    c = Client(FREISTELLEN, token=_token(), verbose=False)
    # /png liefert direkt ein PNG mit Alphakanal
    frei = c.predict(f=handle_file(pfad), api_name="/png")
    if isinstance(frei, (list, tuple)):
        frei = frei[0]
    if isinstance(frei, dict):
        frei = frei.get("path") or frei.get("url")
    shutil.copy(frei, ziel)
    zuschneiden(ziel)
    return ziel


def zuschneiden(pfad):
    """Transparenten Rand wegschneiden, damit die Mitte wirklich die Mitte ist."""
    from PIL import Image
    im = Image.open(pfad).convert("RGBA")
    kasten = im.getbbox()
    if kasten:
        im.crop(kasten).save(pfad)
    return pfad
