#!/usr/bin/env python3
"""
Bausteine der Werkbank-Szene: Untergrund, Schneidematte, Werkzeuge,
Kleinkram. Jedes Werkzeug zeichnet sich in einem eigenen Koordinaten-
system (Ursprung in seiner Mitte, Laengsachse entlang +x) und wird per
translate/rotate auf den Tisch gelegt. So laesst sich die Anordnung pro
Banner variieren, ohne die Zeichnungen anzufassen.
"""
import math
import random

W, H = 720, 320

# --- Untergrund -----------------------------------------------------------
HOLZ_DUNKEL = "#2e2118"
HOLZ_HELL = "#5a4230"
MATTE = "#20403a"
MATTE_HELL = "#2a5149"
RASTER = "#4d8d80"
MATTE_KANTE = "#173029"

# --- Metall / Kunststoff --------------------------------------------------
STAHL_HELL = "#d7dde4"
STAHL = "#aab3bd"
STAHL_DUNKEL = "#6a727c"
KUNSTSTOFF_DUNKEL = "#1d2229"


def defs(schriften, akzent):
    """Filter, Verlaeufe und Schriften, die die ganze Szene benutzt."""
    return f"""
<defs>
  <style>
    @font-face {{ font-family:'Titel'; src:url({schriften['titel']}) format('truetype'); }}
    @font-face {{ font-family:'Schmal'; src:url({schriften['schmal']}) format('truetype'); }}
    @font-face {{ font-family:'Mono'; src:url({schriften['mono']}) format('truetype'); }}
    @font-face {{ font-family:'Stift'; src:url({schriften['stift']}) format('truetype'); }}
    text {{ paint-order: stroke fill; }}
  </style>

  <linearGradient id="holz" x1="0" y1="0" x2="0.8" y2="1">
    <stop offset="0" stop-color="{HOLZ_HELL}"/>
    <stop offset="0.55" stop-color="#43301f"/>
    <stop offset="1" stop-color="{HOLZ_DUNKEL}"/>
  </linearGradient>

  <linearGradient id="mattenlicht" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{MATTE_HELL}"/>
    <stop offset="0.45" stop-color="{MATTE}"/>
    <stop offset="1" stop-color="#18332e"/>
  </linearGradient>

  <linearGradient id="stahl" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#7d868f"/>
    <stop offset="0.35" stop-color="{STAHL_HELL}"/>
    <stop offset="0.62" stop-color="{STAHL}"/>
    <stop offset="1" stop-color="#5c646d"/>
  </linearGradient>

  <linearGradient id="griff_dunkel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3a4250"/>
    <stop offset="0.4" stop-color="#232a34"/>
    <stop offset="1" stop-color="#11151b"/>
  </linearGradient>

  <linearGradient id="griff_gelb" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffd24a"/>
    <stop offset="0.45" stop-color="#f0a81c"/>
    <stop offset="1" stop-color="#9c6608"/>
  </linearGradient>

  <linearGradient id="griff_rot" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e8564a"/>
    <stop offset="0.45" stop-color="#c22f27"/>
    <stop offset="1" stop-color="#761713"/>
  </linearGradient>

  <linearGradient id="griff_blau" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3f9ad6"/>
    <stop offset="0.45" stop-color="#1f6ea6"/>
    <stop offset="1" stop-color="#0e3a5c"/>
  </linearGradient>

  <radialGradient id="lichtkegel" cx="0.28" cy="0.1" r="0.95">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.16"/>
    <stop offset="0.45" stop-color="#ffffff" stop-opacity="0.04"/>
    <stop offset="1" stop-color="#000000" stop-opacity="0.45"/>
  </radialGradient>

  <filter id="holzmaser" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9 0.012" numOctaves="4" seed="7"/>
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.5"/></feComponentTransfer>
  </filter>

  <filter id="koernung" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" seed="3"/>
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.35"/></feComponentTransfer>
  </filter>

  <filter id="schatten_weich" x="-60%" y="-60%" width="240%" height="240%">
    <feDropShadow dx="4" dy="7" stdDeviation="5" flood-color="#000" flood-opacity="0.55"/>
  </filter>
  <filter id="schatten_klein" x="-60%" y="-60%" width="240%" height="240%">
    <feDropShadow dx="2" dy="3" stdDeviation="2.4" flood-color="#000" flood-opacity="0.5"/>
  </filter>
  <filter id="schatten_gross" x="-60%" y="-60%" width="240%" height="240%">
    <feDropShadow dx="6" dy="11" stdDeviation="9" flood-color="#000" flood-opacity="0.6"/>
  </filter>
  <filter id="glimmen" x="-120%" y="-120%" width="340%" height="340%">
    <feGaussianBlur stdDeviation="6"/>
  </filter>
</defs>
"""


def untergrund():
    """Holzplatte mit Maserung."""
    return f"""
<g id="tisch">
  <rect width="{W}" height="{H}" fill="url(#holz)"/>
  <rect width="{W}" height="{H}" filter="url(#holzmaser)" opacity="0.30"
        style="mix-blend-mode:overlay"/>
  <g opacity="0.30" stroke="#1c130c" fill="none">
    <path d="M -20 44 C 180 30, 420 66, 760 40" stroke-width="2.2"/>
    <path d="M -20 150 C 210 168, 430 128, 760 158" stroke-width="1.6"/>
    <path d="M -20 262 C 240 244, 470 286, 760 256" stroke-width="2.6"/>
  </g>
</g>
"""


def schneidematte(zufall):
    """
    Grosse Schneidematte, leicht schraeg, laeuft rechts und unten aus dem
    Bild. Oben links bleibt Holz frei - dort steht der Titel.
    """
    drehung = round(-2.1 + zufall.uniform(-0.7, 0.7), 2)
    x0, y0 = 56 + zufall.uniform(-8, 8), 62 + zufall.uniform(-6, 6)
    breite, hoehe = 780, 340

    raster = []
    for i in range(1, 40):
        x = i * 20
        if x >= breite:
            break
        dick = 1.5 if i % 5 == 0 else 0.7
        raster.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{hoehe}" stroke-width="{dick}"/>')
    for i in range(1, 18):
        y = i * 20
        if y >= hoehe:
            break
        dick = 1.5 if i % 5 == 0 else 0.7
        raster.append(f'<line x1="0" y1="{y}" x2="{breite}" y2="{y}" stroke-width="{dick}"/>')

    # Schnittspuren: kurze helle Kratzer, damit die Matte benutzt aussieht
    spuren = []
    for _ in range(14):
        sx = zufall.uniform(30, breite - 40)
        sy = zufall.uniform(30, hoehe - 40)
        laenge = zufall.uniform(18, 70)
        winkel = zufall.choice([0, 0, 90, zufall.uniform(-40, 40)])
        dx = laenge * math.cos(math.radians(winkel))
        dy = laenge * math.sin(math.radians(winkel))
        spuren.append(f'<line x1="{sx:.0f}" y1="{sy:.0f}" x2="{sx+dx:.0f}" y2="{sy+dy:.0f}" '
                      f'stroke-width="{zufall.uniform(0.8,1.6):.1f}" opacity="{zufall.uniform(0.10,0.26):.2f}"/>')

    # Massskala am oberen und linken Rand
    skala = []
    for i in range(1, 38):
        x = i * 20
        if x >= breite:
            break
        lang = i % 5 == 0
        skala.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{10 if lang else 5}" stroke-width="1.2"/>')
    for i in range(1, 17):
        y = i * 20
        if y >= hoehe:
            break
        lang = i % 5 == 0
        skala.append(f'<line x1="0" y1="{y}" x2="{10 if lang else 5}" y2="{y}" stroke-width="1.2"/>')

    return f"""
<g id="matte" transform="translate({x0:.1f},{y0:.1f}) rotate({drehung})" filter="url(#schatten_gross)">
  <rect x="0" y="0" width="{breite}" height="{hoehe}" rx="10" fill="url(#mattenlicht)"/>
  <g stroke="{RASTER}" opacity="0.38">{''.join(raster)}</g>
  <g stroke="#e6f6f0" opacity="0.65">{''.join(skala)}</g>
  <g stroke="#dff3ec">{''.join(spuren)}</g>
  <rect x="0" y="0" width="{breite}" height="{hoehe}" rx="10" filter="url(#koernung)"
        opacity="0.22" style="mix-blend-mode:overlay"/>
  <rect x="0.5" y="0.5" width="{breite-1}" height="{hoehe-1}" rx="10" fill="none"
        stroke="{MATTE_KANTE}" stroke-width="2"/>
  <rect x="2.5" y="2.5" width="{breite-5}" height="{hoehe-5}" rx="8" fill="none"
        stroke="#6fb3a4" stroke-width="1" opacity="0.35"/>
</g>
"""


# --- Werkzeuge ------------------------------------------------------------

def teppichmesser(laenge=150):
    """Cuttermesser: Klinge zeigt nach +x."""
    g = laenge / 150
    return f"""
<g class="werkzeug" transform="scale({g:.3f})" filter="url(#schatten_klein)">
  <!-- Klinge -->
  <path d="M 46 -9 L 104 -9 L 104 3 L 46 9 Z" fill="url(#stahl)"/>
  <path d="M 104 -9 L 128 -2.5 L 128 2 L 104 3 Z" fill="#e9eef3"/>
  <path d="M 46 -9 L 104 -9 L 104 -5 L 46 -5 Z" fill="#ffffff" opacity="0.45"/>
  <g stroke="#7d868f" stroke-width="1.1" opacity="0.8">
    <line x1="60" y1="-9" x2="66" y2="8"/>
    <line x1="78" y1="-9" x2="84" y2="7"/>
    <line x1="96" y1="-9" x2="102" y2="4"/>
  </g>
  <!-- Griff -->
  <rect x="-75" y="-15" width="128" height="30" rx="9" fill="url(#griff_gelb)"/>
  <rect x="-75" y="-15" width="128" height="9" rx="6" fill="#ffffff" opacity="0.22"/>
  <rect x="-72" y="-9" width="46" height="18" rx="4" fill="{KUNSTSTOFF_DUNKEL}" opacity="0.85"/>
  <g fill="{KUNSTSTOFF_DUNKEL}" opacity="0.7">
    <rect x="-16" y="-11" width="24" height="22" rx="4"/>
  </g>
  <g stroke="#6b4708" stroke-width="1.4" opacity="0.6">
    <line x1="14" y1="-12" x2="14" y2="12"/>
    <line x1="22" y1="-12" x2="22" y2="12"/>
    <line x1="30" y1="-12" x2="30" y2="12"/>
  </g>
  <rect x="38" y="-11" width="16" height="22" rx="3" fill="#8f9aa5"/>
</g>
"""


def schraubendreher(laenge=130, griff="griff_rot"):
    """Feinschraubendreher mit Drehkappe, Klinge zeigt nach +x."""
    g = laenge / 130
    return f"""
<g class="werkzeug" transform="scale({g:.3f})" filter="url(#schatten_klein)">
  <rect x="18" y="-3" width="62" height="6" rx="2" fill="url(#stahl)"/>
  <path d="M 80 -3 L 92 -2 L 92 2 L 80 3 Z" fill="#eef2f6"/>
  <rect x="-58" y="-11" width="78" height="22" rx="8" fill="url(#{griff})"/>
  <g stroke="#000" stroke-width="1.2" opacity="0.28">
    <line x1="-40" y1="-10" x2="-40" y2="10"/>
    <line x1="-30" y1="-10.5" x2="-30" y2="10.5"/>
    <line x1="-20" y1="-11" x2="-20" y2="11"/>
    <line x1="-10" y1="-11" x2="-10" y2="11"/>
    <line x1="0" y1="-11" x2="0" y2="11"/>
  </g>
  <rect x="-58" y="-11" width="78" height="7" rx="6" fill="#fff" opacity="0.2"/>
  <circle cx="-62" cy="0" r="7.5" fill="#cfd6de"/>
  <circle cx="-62" cy="0" r="3.4" fill="#8b949e"/>
  <rect x="12" y="-6" width="10" height="12" rx="2" fill="#9aa4ae"/>
</g>
"""


def loetkolben(laenge=190, kabel="M 0 6 C -40 30, -86 8, -128 40"):
    """
    Loetkolben, Spitze nach +x. Das Kabel ist das, was ihn auf einen Blick
    vom Schraubendreher unterscheidet - deshalb dick, dunkel und bis aus
    dem Bild hinaus.
    """
    g = laenge / 190
    return f"""
<g class="werkzeug" transform="scale({g:.3f})">
  <g transform="translate(-96,0)">
    <path d="{kabel}" transform="translate(3,7)" fill="none" stroke="#000"
          stroke-width="11" stroke-linecap="round" opacity="0.45"/>
    <path d="{kabel}" fill="none" stroke="#0b0f14" stroke-width="10" stroke-linecap="round"/>
    <path d="{kabel}" transform="translate(0,-2)" fill="none" stroke="#39424e"
          stroke-width="4" stroke-linecap="round" opacity="0.85"/>
  </g>
  <g filter="url(#schatten_klein)">
    <!-- Knickschutz -->
    <path d="M -108 -9 L -96 -13 L -96 13 L -108 9 Z" fill="#11161c"/>
    <rect x="-98" y="-14" width="22" height="28" rx="7" fill="#161c24"/>
    <!-- Griff -->
    <rect x="-80" y="-17" width="104" height="34" rx="13" fill="url(#griff_blau)"/>
    <rect x="-80" y="-17" width="104" height="11" rx="8" fill="#fff" opacity="0.25"/>
    <rect x="-80" y="8" width="104" height="9" rx="6" fill="#000" opacity="0.25"/>
    <g stroke="#08243a" stroke-width="2" opacity="0.5">
      <line x1="-60" y1="-16" x2="-60" y2="16"/>
      <line x1="-48" y1="-16.5" x2="-48" y2="16.5"/>
      <line x1="-36" y1="-17" x2="-36" y2="17"/>
      <line x1="-24" y1="-17" x2="-24" y2="17"/>
    </g>
    <!-- Huelse und Rohr -->
    <rect x="16" y="-14" width="20" height="28" rx="5" fill="#cfd6de"/>
    <rect x="16" y="-14" width="20" height="9" rx="4" fill="#fff" opacity="0.5"/>
    <path d="M 34 -9 L 82 -6.5 L 82 6.5 L 34 9 Z" fill="url(#stahl)"/>
    <g stroke="#79828c" stroke-width="1.2" opacity="0.85">
      <line x1="48" y1="-8.2" x2="48" y2="8.2"/>
      <line x1="60" y1="-7.6" x2="60" y2="7.6"/>
      <line x1="72" y1="-7" x2="72" y2="7"/>
    </g>
    <!-- Kupferspitze -->
    <path d="M 82 -6.5 L 104 -3.6 L 108 0 L 104 3.6 L 82 6.5 Z" fill="#b07a3c"/>
    <path d="M 82 -6.5 L 104 -3.6 L 104 -1 L 82 -2 Z" fill="#e2a862"/>
    <path d="M 100 -2.6 L 110 0 L 100 2.6 Z" fill="#6f4a20"/>
  </g>
</g>
"""


# --- Kleinkram ------------------------------------------------------------

def loetzinn(r=28):
    """Spule Loetzinn von oben: Kern, gewickelter Draht, loses Ende."""
    return f"""
<g class="kram" filter="url(#schatten_klein)">
  <circle r="{r}" fill="#262d36"/>
  <circle r="{r}" fill="none" stroke="#12161c" stroke-width="2"/>
  <circle r="{r*0.86:.1f}" fill="none" stroke="#c3ccd6" stroke-width="{r*0.34:.1f}"/>
  <circle r="{r*0.96:.1f}" fill="none" stroke="#8d97a2" stroke-width="1.4" opacity="0.8"/>
  <circle r="{r*0.74:.1f}" fill="none" stroke="#6e7883" stroke-width="1.4" opacity="0.7"/>
  <g stroke="#7e879242" stroke-width="1" opacity="0.55">
    <circle r="{r*0.80:.1f}" fill="none"/>
    <circle r="{r*0.92:.1f}" fill="none"/>
  </g>
  <circle r="{r*0.56:.1f}" fill="#39414b"/>
  <circle r="{r*0.56:.1f}" fill="none" stroke="#1b2028" stroke-width="1.5"/>
  <circle r="{r*0.20:.1f}" fill="#0e1116"/>
  <path d="M {r*0.86:.0f} {-r*0.36:.0f} C {r*1.5:.0f} {-r*1.0:.0f}, {r*2.1:.0f} {r*0.5:.0f}, {r*2.8:.0f} {-r*0.1:.0f}"
        fill="none" stroke="#0f1318" stroke-width="4" stroke-linecap="round" opacity="0.4"/>
  <path d="M {r*0.86:.0f} {-r*0.36:.0f} C {r*1.5:.0f} {-r*1.0:.0f}, {r*2.1:.0f} {r*0.5:.0f}, {r*2.8:.0f} {-r*0.1:.0f}"
        fill="none" stroke="#dce3ea" stroke-width="2.6" stroke-linecap="round"/>
</g>
"""


def schrauben(zufall, anzahl=5):
    """Ein paar Schrauben und Muttern, zufaellig gestreut."""
    teile = []
    for _ in range(anzahl):
        x = zufall.uniform(-34, 34)
        y = zufall.uniform(-20, 20)
        dreh = zufall.uniform(0, 360)
        if zufall.random() < 0.45:
            r = zufall.uniform(4.4, 6.0)
            ecken = " ".join(
                f"{x + r*math.cos(math.radians(a+dreh)):.1f},{y + r*math.sin(math.radians(a+dreh)):.1f}"
                for a in range(0, 360, 60))
            teile.append(f'<polygon points="{ecken}" fill="#98a2ad" stroke="#5a626c" stroke-width="1"/>'
                         f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*0.45:.1f}" fill="#242a32"/>')
        else:
            laenge = zufall.uniform(13, 21)
            dx, dy = laenge*math.cos(math.radians(dreh)), laenge*math.sin(math.radians(dreh))
            teile.append(
                f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x+dx:.1f}" y2="{y+dy:.1f}" '
                f'stroke="#aab3bd" stroke-width="3.2" stroke-linecap="round"/>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="#c3ccd5" stroke="#5a626c" stroke-width="0.8"/>'
                f'<line x1="{x-2.6:.1f}" y1="{y-2.6:.1f}" x2="{x+2.6:.1f}" y2="{y+2.6:.1f}" '
                f'stroke="#4a515a" stroke-width="1.2"/>')
    return f'<g class="kram" filter="url(#schatten_klein)">{"".join(teile)}</g>'


def kaffeering(r=30):
    return f"""
<g opacity="0.30">
  <circle r="{r}" fill="none" stroke="#7a4a1e" stroke-width="3.4"/>
  <circle r="{r-2.4:.1f}" fill="none" stroke="#3a2410" stroke-width="1" opacity="0.6"/>
  <circle r="{r}" fill="#5a3413" opacity="0.10"/>
</g>
"""


def zettel(zufall, text_zeilen, breite=112, hoehe=86, akzent="#ffffff"):
    """Karierter Notizzettel mit Handschrift."""
    linien = "".join(
        f'<line x1="0" y1="{y}" x2="{breite}" y2="{y}" stroke="#9fb0c4" stroke-width="0.7" opacity="0.5"/>'
        for y in range(14, hoehe - 4, 14))
    schrift = "".join(
        f'<text x="9" y="{26 + i*17}" font-family="Stift" font-size="12" fill="#2c3a4b" '
        f'opacity="0.85">{t}</text>' for i, t in enumerate(text_zeilen))
    return f"""
<g class="zettel" filter="url(#schatten_klein)">
  <rect width="{breite}" height="{hoehe}" rx="2" fill="#eee7d5"/>
  <rect width="{breite}" height="{hoehe}" rx="2" fill="#000" opacity="0.06"
        style="mix-blend-mode:multiply"/>
  {linien}
  <path d="M 0 0 L {breite} 0 L {breite} 4 L 0 6 Z" fill="#ffffff" opacity="0.5"/>
  {schrift}
  <rect width="{breite}" height="{hoehe}" rx="2" fill="none" stroke="#c9c0a8" stroke-width="1"/>
</g>
"""


# --- Projektobjekte -------------------------------------------------------

def projekt_theremin(akzent, logo=""):
    """
    Selbstbau-Theremin: Holzkasten mit offener Platine, Stabantenne fuer
    die Tonhoehe, Schleifenantenne fuer die Lautstaerke. Die Stabantenne
    laeuft absichtlich aus dem Kasten heraus - sie macht das Geraet auf
    einen Blick erkennbar.
    """
    return f"""
<g class="projekt">
  <!-- Stabantenne (Tonhoehe) -->
  <g transform="rotate(-27)" filter="url(#schatten_klein)">
    <rect x="70" y="-3.4" width="196" height="6.8" rx="3.4" fill="url(#stahl)"/>
    <rect x="70" y="-3.4" width="196" height="2.4" rx="1.2" fill="#fff" opacity="0.5"/>
    <circle cx="266" cy="0" r="5.4" fill="#e7edf3"/>
    <rect x="62" y="-7" width="16" height="14" rx="3" fill="#2b323b"/>
  </g>
  <!-- Schleifenantenne (Lautstaerke) -->
  <g transform="translate(-116,26) rotate(14)" filter="url(#schatten_klein)">
    <ellipse rx="40" ry="25" fill="none" stroke="#9aa4ae" stroke-width="7"/>
    <ellipse rx="40" ry="25" fill="none" stroke="#e3e9ef" stroke-width="3"/>
    <rect x="30" y="-4" width="40" height="8" rx="4" fill="url(#stahl)"/>
    <rect x="62" y="-8" width="14" height="16" rx="3" fill="#2b323b"/>
  </g>
  <!-- Gehaeuse -->
  <g transform="rotate(-3)" filter="url(#schatten_weich)">
    <rect x="-78" y="-52" width="178" height="104" rx="8" fill="#7a5433"/>
    <rect x="-78" y="-52" width="178" height="104" rx="8" filter="url(#holzmaser)"
          opacity="0.40" style="mix-blend-mode:overlay"/>
    <rect x="-78" y="-52" width="178" height="16" rx="8" fill="#fff" opacity="0.12"/>
    <rect x="-73" y="-47" width="168" height="94" rx="6" fill="none" stroke="#3a2614"
          stroke-width="2" opacity="0.6"/>
    <!-- offene Platine -->
    <rect x="-68" y="-40" width="96" height="62" rx="4" fill="#10402e"/>
    <rect x="-68" y="-40" width="96" height="62" rx="4" fill="none" stroke="#0a2a1e" stroke-width="1.5"/>
    <g fill="#1d1f24">
      <rect x="-60" y="-33" width="30" height="15" rx="2"/>
      <rect x="-24" y="-33" width="17" height="15" rx="2"/>
      <rect x="-60" y="-12" width="21" height="21" rx="2"/>
    </g>
    <g fill="#c8b06a" opacity="0.95">
      <rect x="-1" y="-33" width="24" height="9" rx="1.5"/>
      <rect x="-1" y="-20" width="24" height="9" rx="1.5"/>
    </g>
    <g stroke="#cbb06a" stroke-width="1.6" opacity="0.9" fill="none">
      <path d="M -60 4 H -34 V 16 H -6"/>
      <path d="M -24 -14 H -6 V 16"/>
      <path d="M 12 -6 V 16 H -34"/>
    </g>
    <g fill="#e3c87a">
      <circle cx="-60" cy="4" r="2.2"/><circle cx="-34" cy="16" r="2.2"/>
      <circle cx="-6" cy="16" r="2.2"/><circle cx="12" cy="-6" r="2.2"/>
    </g>
    <!-- Drehknoepfe -->
    <g filter="url(#schatten_klein)">
      <circle cx="58" cy="-22" r="19" fill="#1b2029"/>
      <circle cx="58" cy="-22" r="19" fill="none" stroke="#586271" stroke-width="2.4"/>
      <circle cx="58" cy="-22" r="10" fill="#2f3742"/>
      <line x1="58" y1="-22" x2="68" y2="-37" stroke="{akzent}" stroke-width="3.2" stroke-linecap="round"/>
      <circle cx="62" cy="22" r="14" fill="#1b2029"/>
      <circle cx="62" cy="22" r="14" fill="none" stroke="#586271" stroke-width="2"/>
      <line x1="62" y1="22" x2="53" y2="13" stroke="{akzent}" stroke-width="2.6" stroke-linecap="round"/>
    </g>
    {logo}
    <circle cx="90" cy="40" r="4" fill="{akzent}"/>
    <circle cx="90" cy="40" r="9" fill="{akzent}" opacity="0.4" filter="url(#glimmen)"/>
  </g>
</g>
"""


def projekt_ptz(akzent, logo=""):
    """Panasonic-artige PTZ-Kamera, schraeg von vorn."""
    return f"""
<g class="projekt" filter="url(#schatten_weich)">
  <!-- Sockel -->
  <path d="M -78 44 L 78 44 L 66 66 L -66 66 Z" fill="#c9ced6"/>
  <path d="M -78 44 L 78 44 L 78 50 L -78 50 Z" fill="#e8ecf1"/>
  <rect x="-72" y="30" width="144" height="16" rx="5" fill="#dfe4ea"/>
  <!-- Schwenkkopf -->
  <path d="M -62 -18 C -62 -54, 62 -54, 62 -18 L 62 34 C 62 44, -62 44, -62 34 Z" fill="#eef1f5"/>
  <path d="M -62 -18 C -62 -54, 62 -54, 62 -18 L 62 4 C 20 -12, -20 -12, -62 4 Z"
        fill="#ffffff" opacity="0.55"/>
  <path d="M 30 -46 C 54 -38, 62 -28, 62 -14 L 62 34 C 62 42, 40 46, 20 46 C 48 40, 52 30, 52 14 Z"
        fill="#000" opacity="0.10"/>
  <!-- Objektiv -->
  <circle cx="0" cy="-2" r="34" fill="#20252c"/>
  <circle cx="0" cy="-2" r="34" fill="none" stroke="#9aa3ad" stroke-width="3"/>
  <circle cx="0" cy="-2" r="25" fill="#0e1116"/>
  <circle cx="0" cy="-2" r="17" fill="#132a3c"/>
  <circle cx="0" cy="-2" r="17" fill="none" stroke="#2f6d93" stroke-width="2" opacity="0.8"/>
  <circle cx="-7" cy="-11" r="6" fill="#bfe4ff" opacity="0.55"/>
  <circle cx="8" cy="7" r="3" fill="{akzent}" opacity="0.5"/>
  <!-- Tally -->
  <rect x="-16" y="-48" width="32" height="9" rx="4.5" fill="{akzent}"/>
  <rect x="-16" y="-48" width="32" height="9" rx="4.5" fill="{akzent}" filter="url(#glimmen)" opacity="0.8"/>
  <!-- Typenschild: hier traegt das Geraet das Logo -->
  {logo}
</g>
"""


def projekt_helo(akzent, logo=""):
    """AJA-artiger Streaming-/Aufnahme-Recorder, halbe Rackbreite."""
    return f"""
<g class="projekt" filter="url(#schatten_weich)">
  <rect x="-116" y="-40" width="232" height="80" rx="6" fill="#20252c"/>
  <rect x="-116" y="-40" width="232" height="80" rx="6" fill="none" stroke="#454d57" stroke-width="2"/>
  <rect x="-116" y="-40" width="232" height="16" rx="6" fill="#ffffff" opacity="0.07"/>
  <!-- Rackohren -->
  <g fill="#2b313a">
    <rect x="-134" y="-34" width="20" height="68" rx="3"/>
    <rect x="114" y="-34" width="20" height="68" rx="3"/>
  </g>
  <g fill="#0d1014">
    <circle cx="-124" cy="-20" r="3"/><circle cx="-124" cy="20" r="3"/>
    <circle cx="124" cy="-20" r="3"/><circle cx="124" cy="20" r="3"/>
  </g>
  <!-- Display -->
  <rect x="-100" y="-26" width="86" height="52" rx="4" fill="#070a0d"/>
  <rect x="-96" y="-22" width="78" height="44" rx="2" fill="#0d1a17"/>
  <g font-family="Mono" font-size="9" fill="{akzent}">
    <text x="-90" y="-10">REC 00:41:12</text>
    <text x="-90" y="2" fill="#7f8c99">1080p59.94</text>
    <text x="-90" y="14" fill="#7f8c99">RTMP  OK</text>
  </g>
  <!-- Pegel -->
  <g>
    <rect x="-8" y="-26" width="8" height="52" rx="2" fill="#11161c"/>
    <rect x="-8" y="2" width="8" height="24" rx="2" fill="#39c07a"/>
    <rect x="4" y="-26" width="8" height="52" rx="2" fill="#11161c"/>
    <rect x="4" y="-6" width="8" height="32" rx="2" fill="#39c07a"/>
    <rect x="4" y="-12" width="8" height="6" rx="2" fill="#e0c23c"/>
  </g>
  <!-- Tasten -->
  <g>
    <circle cx="36" cy="-8" r="15" fill="#171c22" stroke="#3d454f" stroke-width="2"/>
    <circle cx="36" cy="-8" r="7" fill="{akzent}"/>
    <circle cx="36" cy="-8" r="12" fill="{akzent}" opacity="0.35" filter="url(#glimmen)"/>
    <circle cx="74" cy="-8" r="15" fill="#171c22" stroke="#3d454f" stroke-width="2"/>
    <path d="M 68 -15 L 82 -8 L 68 -1 Z" fill="#9aa4ae"/>
  </g>
  {logo}
</g>
"""


PROJEKTE = {
    "theremin": projekt_theremin,
    "ptz": projekt_ptz,
    "helo": projekt_helo,
}

# Wo und wie das Logo auf dem jeweiligen Geraet sitzt - im Koordinaten-
# system des Geraets, also mitgedreht. Die Stile stehen in
# make_desk_banner.logo_auf_geraet().
PROJEKT_LOGOPLATZ = {
    "theremin": {"x": -56, "y": 24, "breite": 98, "stil": "gravur_holz"},
    "ptz": {"x": -58, "y": 46, "breite": 62, "stil": "druck_dunkel"},
    "helo": {"x": 20, "y": 10, "breite": 70, "stil": "aetzung_hell"},
}


# --- Weitere Werkzeuge ----------------------------------------------------
# Alle zeichnen sich entlang +x um ihre Mitte, wie die festen Werkzeuge.

def pinzette(laenge=120):
    """Spitzpinzette, Spitzen nach +x."""
    g = laenge / 120
    return f"""
<g class="werkzeug" transform="scale({g:.3f})" filter="url(#schatten_klein)">
  <path d="M -60 -4 L 8 -9 L 58 -2.6 L 60 0 L 56 0.4 L 6 -4.6 L -60 -0.6 Z" fill="url(#stahl)"/>
  <path d="M -60 4 L 8 9 L 58 2.6 L 60 0 L 56 -0.4 L 6 4.6 L -60 0.6 Z" fill="#9aa4ae"/>
  <path d="M -60 -4 L 8 -9 L 8 -6.4 L -60 -1.6 Z" fill="#eaeff4" opacity="0.7"/>
  <rect x="-62" y="-5" width="12" height="10" rx="4" fill="#5d666f"/>
  <rect x="-30" y="-7" width="26" height="3" rx="1.5" fill="#000" opacity="0.18"/>
</g>
"""


def seitenschneider(laenge=132):
    """Seitenschneider, Schneide nach +x, Griffe nach -x."""
    g = laenge / 132
    return f"""
<g class="werkzeug" transform="scale({g:.3f})" filter="url(#schatten_klein)">
  <g transform="rotate(-9)">
    <rect x="-70" y="-9" width="66" height="18" rx="9" fill="#c8302a"/>
    <rect x="-70" y="-9" width="66" height="6" rx="5" fill="#fff" opacity="0.25"/>
    <rect x="-68" y="-8" width="10" height="16" rx="5" fill="#8d201c"/>
  </g>
  <g transform="rotate(9)">
    <rect x="-70" y="-9" width="66" height="18" rx="9" fill="#e0453c"/>
    <rect x="-70" y="-9" width="66" height="6" rx="5" fill="#fff" opacity="0.3"/>
    <rect x="-68" y="-8" width="10" height="16" rx="5" fill="#9c2620"/>
  </g>
  <path d="M -10 -13 L 34 -9 L 52 -2 L 52 2 L 34 9 L -10 13 Z" fill="url(#stahl)"/>
  <path d="M -10 -13 L 34 -9 L 34 -5 L -10 -7 Z" fill="#fff" opacity="0.45"/>
  <path d="M 34 -9 L 56 -1.6 L 56 1.6 L 34 9 Z" fill="#e6ebf0"/>
  <circle cx="2" cy="0" r="7.5" fill="#7d868f"/>
  <circle cx="2" cy="0" r="3.2" fill="#4c545d"/>
</g>
"""


def entloetpumpe(laenge=140):
    """Entloetpumpe, Spitze nach +x."""
    g = laenge / 140
    return f"""
<g class="werkzeug" transform="scale({g:.3f})" filter="url(#schatten_klein)">
  <rect x="-70" y="-13" width="112" height="26" rx="8" fill="#39424d"/>
  <rect x="-70" y="-13" width="112" height="9" rx="6" fill="#fff" opacity="0.18"/>
  <rect x="-66" y="-9" width="28" height="18" rx="5" fill="#e0e5eb"/>
  <rect x="-34" y="-11" width="8" height="22" rx="3" fill="#cfd6de"/>
  <rect x="-18" y="-10" width="44" height="20" rx="4" fill="#1d232b"/>
  <g stroke="#59636e" stroke-width="1.4" opacity="0.8">
    <line x1="-6" y1="-10" x2="-6" y2="10"/>
    <line x1="6" y1="-10" x2="6" y2="10"/>
  </g>
  <rect x="42" y="-7" width="18" height="14" rx="4" fill="#b8c0c9"/>
  <path d="M 60 -5 L 76 -2.2 L 76 2.2 L 60 5 Z" fill="#e6ebf0"/>
</g>
"""


def bleistift(laenge=126):
    """Angespitzter Bleistift, Spitze nach +x."""
    g = laenge / 126
    return f"""
<g class="werkzeug" transform="scale({g:.3f})" filter="url(#schatten_klein)">
  <rect x="-63" y="-7" width="106" height="14" rx="2" fill="#e8a723"/>
  <rect x="-63" y="-7" width="106" height="4.5" rx="2" fill="#fff" opacity="0.35"/>
  <rect x="-63" y="3" width="106" height="4" fill="#000" opacity="0.18"/>
  <rect x="-63" y="-7" width="13" height="14" rx="2" fill="#cf5a52"/>
  <rect x="-52" y="-7.5" width="6" height="15" fill="#b9c1ca"/>
  <path d="M 43 -7 L 60 -2.4 L 60 2.4 L 43 7 Z" fill="#e6d3a8"/>
  <path d="M 58 -1.8 L 64 0 L 58 1.8 Z" fill="#2c3138"/>
</g>
"""


def krokokabel(laenge=150, bogen="M -70 -6 C -20 -34, 20 22, 70 -4"):
    """Messkabel mit zwei Krokodilklemmen."""
    g = laenge / 150
    return f"""
<g class="werkzeug" transform="scale({g:.3f})">
  <path d="{bogen}" transform="translate(2,5)" fill="none" stroke="#000" stroke-width="7"
        stroke-linecap="round" opacity="0.35"/>
  <path d="{bogen}" fill="none" stroke="#c0392f" stroke-width="5" stroke-linecap="round"/>
  <path d="{bogen}" transform="translate(0,-1.4)" fill="none" stroke="#e6635a" stroke-width="1.8"
        stroke-linecap="round" opacity="0.8"/>
  <g filter="url(#schatten_klein)">
    <g transform="translate(-70,-6) rotate(160)">
      <path d="M 0 -6 L 22 -3 L 34 0 L 22 3 L 0 6 Z" fill="#b9c1ca"/>
      <path d="M 6 -6 L 22 -3.4 L 22 -0.6 L 6 -2 Z" fill="#eef2f6"/>
      <rect x="-12" y="-7" width="14" height="14" rx="3" fill="#c0392f"/>
    </g>
    <g transform="translate(70,-4) rotate(-14)">
      <path d="M 0 -6 L 22 -3 L 34 0 L 22 3 L 0 6 Z" fill="#b9c1ca"/>
      <path d="M 6 -6 L 22 -3.4 L 22 -0.6 L 6 -2 Z" fill="#eef2f6"/>
      <rect x="-12" y="-7" width="14" height="14" rx="3" fill="#c0392f"/>
    </g>
  </g>
</g>
"""


def widerstaende(zufall, anzahl=4):
    """Ein paar lose Widerstaende."""
    teile = []
    for _ in range(anzahl):
        x, y = zufall.uniform(-30, 30), zufall.uniform(-16, 16)
        dreh = zufall.uniform(0, 180)
        ringe = "".join(
            f'<rect x="{-5 + i*3.6:.1f}" y="-4" width="2.4" height="8" fill="{f}"/>'
            for i, f in enumerate(zufall.sample(["#2b2118", "#a8332a", "#d98b2b", "#c9b03a"], 3)))
        teile.append(
            f'<g transform="translate({x:.1f},{y:.1f}) rotate({dreh:.0f})">'
            f'<line x1="-22" y1="0" x2="22" y2="0" stroke="#b9c1ca" stroke-width="1.8"/>'
            f'<rect x="-10" y="-4.6" width="20" height="9.2" rx="4" fill="#d8c9a6"/>{ringe}</g>')
    return f'<g class="kram" filter="url(#schatten_klein)">{"".join(teile)}</g>'


def kabelbinder(zufall):
    """Aufgerollter Kabelbinder."""
    dreh = zufall.uniform(0, 360)
    return f"""
<g class="kram" transform="rotate({dreh:.0f})" filter="url(#schatten_klein)">
  <path d="M -18 8 C -26 -14, 10 -22, 16 -2 C 20 12, 2 18, -2 6"
        fill="none" stroke="#d9dee4" stroke-width="4.4" stroke-linecap="round"/>
  <rect x="-24" y="2" width="12" height="9" rx="2" fill="#e6ebf0"/>
  <rect x="-22" y="4" width="8" height="5" rx="1.5" fill="#aeb6bf"/>
</g>
"""


def stiftleiste(zufall):
    """Stueck Stiftleiste."""
    stifte = "".join(f'<rect x="{-26 + i*7.4:.1f}" y="-9" width="3" height="10" fill="#d9c07a"/>'
                     for i in range(8))
    return f"""
<g class="kram" transform="rotate({zufall.uniform(-25, 25):.0f})" filter="url(#schatten_klein)">
  {stifte}
  <rect x="-28" y="0" width="58" height="9" rx="1.5" fill="#1b1f26"/>
  <rect x="-28" y="0" width="58" height="3" fill="#2f353e"/>
</g>
"""


def kaffeetasse(r=26):
    """Tasse von oben, halb voll."""
    return f"""
<g class="kram" filter="url(#schatten_weich)">
  <ellipse cx="{r*1.1:.0f}" cy="0" rx="{r*0.5:.0f}" ry="{r*0.34:.0f}" fill="none"
           stroke="#e8eaed" stroke-width="6"/>
  <circle r="{r}" fill="#f2f4f6"/>
  <circle r="{r}" fill="none" stroke="#c9ced5" stroke-width="1.6"/>
  <circle r="{r*0.82:.1f}" fill="#4a2c16"/>
  <circle r="{r*0.82:.1f}" fill="none" stroke="#2c190c" stroke-width="1.4"/>
  <ellipse cx="{-r*0.22:.0f}" cy="{-r*0.26:.0f}" rx="{r*0.3:.0f}" ry="{r*0.18:.0f}"
           fill="#8a5a2e" opacity="0.5"/>
</g>
"""


# Vorrat, aus dem sich jedes Banner bedient. "lang" braucht einen langen
# Platz, "kurz" einen mittleren, "kram" faellt in jede Luecke.
def werkzeug_vorrat():
    return {
        "pinzette": ("kurz", lambda z: pinzette(104 + z.uniform(-6, 10))),
        "seitenschneider": ("kurz", lambda z: seitenschneider(116 + z.uniform(-6, 10))),
        "entloetpumpe": ("kurz", lambda z: entloetpumpe(128 + z.uniform(-8, 12))),
        "bleistift": ("kurz", lambda z: bleistift(112 + z.uniform(-6, 12))),
        "krokokabel": ("kurz", lambda z: krokokabel(140 + z.uniform(-10, 14))),
        "loetzinn": ("kram", lambda z: loetzinn(25 + z.uniform(-3, 4))),
        "schrauben": ("kram", lambda z: schrauben(z, z.randint(4, 7))),
        "widerstaende": ("kram", lambda z: widerstaende(z, z.randint(3, 5))),
        "kabelbinder": ("kram", lambda z: kabelbinder(z)),
        "stiftleiste": ("kram", lambda z: stiftleiste(z)),
        "kaffeetasse": ("kram", lambda z: kaffeetasse(26 + z.uniform(-2, 4))),
    }
