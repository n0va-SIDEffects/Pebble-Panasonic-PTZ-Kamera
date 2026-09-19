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


def hochladen(server, pfad):
    """
    Bild in den input-Ordner von ComfyUI legen (POST /upload/image).
    Multipart von Hand, damit das Skript ohne requests auskommt.
    """
    grenze = "----banner" + str(int(time.time() * 1000))
    name = os.path.basename(pfad)
    with open(pfad, "rb") as f:
        inhalt = f.read()
    teile = []
    teile.append(("--" + grenze + "\r\n"
                  'Content-Disposition: form-data; name="image"; filename="' + name + '"\r\n'
                  "Content-Type: image/png\r\n\r\n").encode("utf-8"))
    teile.append(inhalt)
    teile.append(("\r\n--" + grenze + "\r\n"
                  'Content-Disposition: form-data; name="overwrite"\r\n\r\n'
                  "true\r\n"
                  "--" + grenze + "--\r\n").encode("utf-8"))
    koerper = b"".join(teile)
    anfrage = urllib.request.Request(
        f"http://{server}/upload/image", data=koerper,
        headers={"Content-Type": "multipart/form-data; boundary=" + grenze})
    with urllib.request.urlopen(anfrage, timeout=60) as antwort:
        return json.loads(antwort.read()).get("name", name)


def veredeln(server, vorlage, workflow_pfad, ziel, staerke, prompt, seed):
    """
    Die fertige Szene noch einmal durch das Bildmodell schicken, aber nur
    leicht: So gleichen sich Licht, Schatten und Perspektive der einzeln
    erzeugten Teile an, ohne dass die Anordnung verlorengeht. Je hoeher
    die Staerke, desto freier wird das Modell - ueber etwa 0.5 erfindet
    es die Szene neu.
    """
    if not os.path.exists(workflow_pfad):
        raise SystemExit("Kein img2img-Workflow: " + workflow_pfad)
    with open(workflow_pfad, encoding="utf-8") as f:
        workflow = json.load(f)

    name = hochladen(server, vorlage)
    print("hochgeladen als:", name)
    maske_pfad = os.path.splitext(vorlage)[0] + "_maske.png"
    maske_name = None
    if os.path.exists(maske_pfad):
        maske_name = hochladen(server, maske_pfad)
        print("Maske hochgeladen als:", maske_name)
    lader = [(kid, k) for kid, k in workflow.items() if k.get("class_type") == "LoadImage"]
    for kid, knoten in lader:
        titel = (knoten.get("_meta", {}).get("title") or "").lower()
        if maske_name and "maske" in titel:
            knoten["inputs"]["image"] = maske_name
        else:
            knoten["inputs"]["image"] = name
    for knoten_id, feld in _felder(workflow, "denoise"):
        workflow[knoten_id]["inputs"][feld] = staerke
    for name_feld in ("seed", "noise_seed"):
        for knoten_id, feld in _felder(workflow, name_feld):
            workflow[knoten_id]["inputs"][feld] = seed
    texte = _text_knoten(workflow)
    if texte and prompt:
        workflow[texte[0]]["inputs"]["text"] = prompt
    return erzeugen(server, workflow, ziel)


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
    p.add_argument("--veredeln", default="",
                   help="eine fertige Szene noch einmal leicht durchs Modell schicken")
    p.add_argument("--staerke", type=float, default=0.35,
                   help="wie frei das Modell dabei sein darf (0.2 vorsichtig, 0.5 viel)")
    p.add_argument("--img2img", default=None,
                   help="Workflow fuer den Durchlauf; ohne Angabe wird der mit Maske "
                        "genommen, sobald eine Maske neben der Vorlage liegt")
    a = p.parse_args()

    if a.veredeln:
        laeuft, auskunft = erreichbar(a.server)
        if not laeuft:
            raise SystemExit(f"ComfyUI auf {a.server} nicht erreichbar: {auskunft}")
        ziel = os.path.splitext(a.veredeln)[0] + "_veredelt.png"
        # Der Stilbaustein kommt aus der Liste, wenn sie dabeiliegt -
        # zum Veredeln allein wird sie aber nicht gebraucht.
        stil = ("flat vector illustration, bold clean dark outlines, limited muted color "
                "palette, soft cel shading, no text")
        if os.path.exists(a.liste):
            with open(a.liste, encoding="utf-8") as f:
                stil = json.load(f).get("stil", stil)
        workflow_pfad = a.img2img
        if not workflow_pfad:
            mit_maske = os.path.join(HIER, "workflow_img2img_maske.json")
            hat_maske = os.path.exists(os.path.splitext(a.veredeln)[0] + "_maske.png")
            workflow_pfad = (mit_maske if hat_maske and os.path.exists(mit_maske)
                             else os.path.join(HIER, "workflow_img2img.json"))
            print("Workflow:", os.path.basename(workflow_pfad))
        veredeln(a.server, a.veredeln, workflow_pfad, ziel, a.staerke,
                 stil + ". top-down view of an electronics workbench with tools on a green "
                        "cutting mat, even light, consistent perspective",
                 7)
        print("fertig:", ziel)
        return

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
    ohne_freistellung = []
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
        if not eintrag.get("freigestellt", True):
            os.replace(roh, ziel)
            continue
        try:
            freistellen(roh, ziel, eintrag.get("hintergrund", a.hintergrund))
            print("  freigestellt:", ziel)
        except ImportError:
            # Ohne numpy/Pillow laeuft der Durchgang trotzdem zu Ende; die
            # Rohbilder liegen dann in ki/ und lassen sich spaeter oder
            # anderswo freistellen. Sonst bricht ein fehlendes Modul einen
            # halbfertigen Satz ab, und das waere der aergerlichste Abbruch.
            ohne_freistellung.append(name)
            print("  roh belassen (numpy/Pillow fehlen):", roh)

    if ohne_freistellung:
        print("\nNicht freigestellt, weil numpy oder Pillow fehlen: " +
              ", ".join(ohne_freistellung) +
              "\nNachholen mit:  python -m pip install numpy pillow\n"
              "und dann noch einmal denselben Aufruf mit --neu.")
    print("\nFertig. Danach in ki/manifest.json eintragen, was benutzt werden soll.")


if __name__ == "__main__":
    main()
