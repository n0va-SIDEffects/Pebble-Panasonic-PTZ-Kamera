#!/usr/bin/env python3
"""
Banner-Assets mit einer lokalen ComfyUI erzeugen.

Statt einen Workflow fest einzubauen, nimmt dieses Skript den Workflow,
der bei dir laeuft: in ComfyUI die Z-Image-Vorlage oeffnen, einmal
ausprobieren, dann ueber "Workflow -> Export (API)" als
workflow_api.json neben dieses Skript legen. Das Skript sucht darin die
Stellen fuer Prompt, Seed und Bildgroesse und setzt pro Asset neue Werte
ein. So bleibt es egal, welches Modell und welche Nodes du benutzt.

    python3 comfy_assets.py --server 127.0.0.1:8188
    python3 comfy_assets.py --nur messer,pinzette --neu

Ergebnisse landen in ki/ - roh als roh_<name>.png, freigestellt als
a_<name>.png. Was schon freigestellt vorliegt, wird uebersprungen
(--neu erzwingt neu).
"""
import argparse
import json
import os
import random
import time
import urllib.parse
import urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
KI = os.path.join(HIER, "ki")
LISTE = os.path.join(HIER, "assets_liste.json")


# --- ComfyUI ansprechen ---------------------------------------------------

def _post(server, pfad, daten):
    anfrage = urllib.request.Request(
        f"http://{server}{pfad}", data=json.dumps(daten).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(anfrage, timeout=30) as antwort:
        return json.loads(antwort.read())


def _get(server, pfad):
    with urllib.request.urlopen(f"http://{server}{pfad}", timeout=30) as antwort:
        return json.loads(antwort.read())


def erreichbar(server):
    try:
        stats = _get(server, "/system_stats")
        geraete = ", ".join(g.get("name", "?") for g in stats.get("devices", []))
        return True, geraete or "unbekannt"
    except Exception as fehler:
        return False, str(fehler)


# --- Workflow anpassen ----------------------------------------------------

def _felder(workflow, name):
    """Alle (node_id, feld) im Workflow, die so heissen."""
    treffer = []
    for knoten_id, knoten in workflow.items():
        for feld in knoten.get("inputs", {}):
            if feld == name:
                treffer.append((knoten_id, feld))
    return treffer


def _text_knoten(workflow):
    """
    Die Textfelder des Workflows, laengster Text zuerst. Der positive
    Prompt ist praktisch immer der laengere - der negative ist leer oder
    eine kurze Liste. Ein Knoten, dessen Titel 'negativ' enthaelt, wird
    ausgeschlossen.
    """
    kandidaten = []
    for knoten_id, knoten in workflow.items():
        titel = (knoten.get("_meta", {}).get("title") or "").lower()
        if "negativ" in titel or "negative" in titel:
            continue
        wert = knoten.get("inputs", {}).get("text")
        if isinstance(wert, str):
            kandidaten.append((len(wert), knoten_id))
    kandidaten.sort(reverse=True)
    return [knoten_id for _, knoten_id in kandidaten]


def vorbereiten(vorlage, prompt, breite, hoehe, seed, praefix):
    """Vorlage kopieren und Prompt, Groesse, Seed und Dateiname einsetzen."""
    workflow = json.loads(json.dumps(vorlage))

    texte = _text_knoten(workflow)
    if not texte:
        raise SystemExit("Im Workflow ist kein Textfeld zu finden - ist es wirklich "
                         "der API-Export (Workflow -> Export (API))?")
    workflow[texte[0]]["inputs"]["text"] = prompt

    for knoten_id, feld in _felder(workflow, "width"):
        workflow[knoten_id]["inputs"][feld] = breite
    for knoten_id, feld in _felder(workflow, "height"):
        workflow[knoten_id]["inputs"][feld] = hoehe
    for name in ("seed", "noise_seed"):
        for knoten_id, feld in _felder(workflow, name):
            workflow[knoten_id]["inputs"][feld] = seed
    for knoten_id, feld in _felder(workflow, "filename_prefix"):
        workflow[knoten_id]["inputs"][feld] = praefix
    return workflow


def erzeugen(server, workflow, ziel, wartezeit=600):
    """Auftrag abschicken, auf das Bild warten, herunterladen."""
    auftrag = _post(server, "/prompt", {"prompt": workflow})
    if "prompt_id" not in auftrag:
        raise SystemExit("ComfyUI hat den Auftrag abgelehnt: " + json.dumps(auftrag)[:400])
    kennung = auftrag["prompt_id"]

    ende = time.time() + wartezeit
    while time.time() < ende:
        verlauf = _get(server, f"/history/{kennung}")
        if kennung in verlauf:
            ausgaben = verlauf[kennung].get("outputs", {})
            for knoten in ausgaben.values():
                for bild in knoten.get("images", []):
                    frage = urllib.parse.urlencode({
                        "filename": bild["filename"], "subfolder": bild.get("subfolder", ""),
                        "type": bild.get("type", "output")})
                    with urllib.request.urlopen(f"http://{server}/view?{frage}", timeout=60) as a:
                        daten = a.read()
                    os.makedirs(os.path.dirname(os.path.abspath(ziel)), exist_ok=True)
                    with open(ziel, "wb") as f:
                        f.write(daten)
                    return ziel
            raise SystemExit("Auftrag fertig, aber ohne Bild. Hat der Workflow einen "
                             "SaveImage-Knoten?")
        time.sleep(1.5)
    raise SystemExit("Zeitueberschreitung beim Warten auf ComfyUI")


# --- Freistellen ----------------------------------------------------------

def freistellen(pfad, ziel, hintergrund="weiss", toleranz=18):
    """
    Den einfarbigen Hintergrund entfernen und zuschneiden. Bei hellen
    Objekten (weisse Kamera) im Prompt einen gruenen Hintergrund
    verlangen und hier --hintergrund gruen benutzen, sonst frisst die
    Freistellung das Objekt mit.
    """
    import numpy as np
    from PIL import Image, ImageFilter

    bild = Image.open(pfad).convert("RGBA")
    feld = np.asarray(bild).astype(np.int16)
    r, g, b = feld[..., 0], feld[..., 1], feld[..., 2]

    if hintergrund == "gruen":
        weg = (g > 90) & (g > r + 40) & (g > b + 40)
    else:
        weg = (r > 255 - toleranz) & (g > 255 - toleranz) & (b > 255 - toleranz)

    alpha = np.where(weg, 0, 255).astype(np.uint8)
    frei = Image.fromarray(np.dstack([feld[..., :3].astype(np.uint8), alpha]), "RGBA")
    # Kante eine Spur weichzeichnen, sonst franst sie im Banner aus
    kante = frei.getchannel("A").filter(ImageFilter.GaussianBlur(0.8))
    frei.putalpha(kante)
    kasten = frei.getbbox()
    if kasten:
        frei = frei.crop(kasten)
    frei.save(ziel)
    return ziel


# --- Ablauf ---------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--server", default="127.0.0.1:8188")
    p.add_argument("--workflow", default=os.path.join(HIER, "workflow_api.json"))
    p.add_argument("--liste", default=LISTE)
    p.add_argument("--nur", default="", help="nur diese Assets, mit Komma getrennt")
    p.add_argument("--neu", action="store_true", help="auch schon vorhandene neu erzeugen")
    p.add_argument("--hintergrund", default="weiss", choices=["weiss", "gruen"])
    a = p.parse_args()

    laeuft, auskunft = erreichbar(a.server)
    if not laeuft:
        raise SystemExit(f"ComfyUI auf {a.server} nicht erreichbar: {auskunft}\n"
                         "Laeuft es? Sonst --server anpassen.")
    print(f"ComfyUI auf {a.server} erreichbar ({auskunft})")

    if not os.path.exists(a.workflow):
        raise SystemExit(
            "Keine Workflow-Vorlage: " + a.workflow + "\n"
            "In ComfyUI den Z-Image-Workflow oeffnen, einmal laufen lassen, dann\n"
            "Workflow -> Export (API) und die Datei hier ablegen.")
    with open(a.workflow, encoding="utf-8") as f:
        vorlage = json.load(f)

    with open(a.liste, encoding="utf-8") as f:
        daten = json.load(f)
    stil = daten["stil"]
    lage = daten["lage"]
    assets = {k: v for k, v in daten["assets"].items()}

    gewuenscht = [n.strip() for n in a.nur.split(",") if n.strip()] or list(assets)
    os.makedirs(KI, exist_ok=True)

    for name in gewuenscht:
        if name not in assets:
            print("unbekannt, uebersprungen:", name)
            continue
        eintrag = assets[name]
        ziel = os.path.join(KI, f"a_{name}.png")
        if os.path.exists(ziel) and not a.neu:
            print("liegt schon vor:", name)
            continue

        teile = [stil, eintrag["was"]]
        if eintrag.get("freigestellt", True):
            hg = eintrag.get("hintergrund", a.hintergrund)
            rumpf = lage if eintrag.get("liegend", True) else daten["stehend"]
            if hg == "gruen":
                rumpf = rumpf.replace("plain pure white background",
                                      "plain flat chroma green background")
            teile.append(rumpf)
        prompt = ". ".join(teile)

        breite = eintrag.get("breite", 768)
        hoehe = eintrag.get("hoehe", 512)
        seed = eintrag.get("seed", random.randint(1, 2 ** 31))
        print(f"\n{name}: {breite}x{hoehe}, Seed {seed}")
        roh = os.path.join(KI, f"roh_{name}.png")
        erzeugen(a.server, vorbereiten(vorlage, prompt, breite, hoehe, seed, "banner/" + name), roh)
        print("  erzeugt:", roh)
        if eintrag.get("freigestellt", True):
            freistellen(roh, ziel, eintrag.get("hintergrund", a.hintergrund))
            print("  freigestellt:", ziel)
        else:
            os.replace(roh, ziel)

    print("\nFertig. Danach in ki/manifest.json eintragen, was benutzt werden soll.")


if __name__ == "__main__":
    main()
