#!/bin/sh
# Banner fuer PTZ Remote bauen. Die Masse stecken in make_banner.py,
# das aus der Veroeffentlichungs-Anleitung stammt; hier stehen nur die
# Werte dieses Projekts.
cd "$(dirname "$0")/../.." || exit 1
python3 store/icon/make_banner.py \
    --assets skill-beitraege/assets \
    --shot store/release/screenshots_emery/1_motion.png \
    --icon store/icon/icon_144_alpha.png \
    --logo store/icon/side_effects_logo.png \
    --title "PTZ Remote" \
    --subtitle "Panasonic PTZ from your wrist" \
    --line "Buttons, or tilt the watch to drive the camera." \
    --line "Select acts as a dead-man switch." \
    --line "Presets - 8 cameras - still preview" \
    --out store/icon/banner_720x320.png
