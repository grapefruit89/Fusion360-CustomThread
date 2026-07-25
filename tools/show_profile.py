#!/usr/bin/env python3
"""
Zeigt, welches Profil in einer Gewinde-XML wirklich steckt.

Rechnet aus den fuenf Zahlen (Pitch, Angle, Major, Pitch, Minor) die Kopf- und
Fussfase zurueck und vergleicht sie mit den Lehrbuchwerten der Normen. Damit
laesst sich pruefen, ob eine Datei normgerechte Geometrie enthaelt - oder ob
jemand Zahlen zusammengewuerfelt hat, die zufaellig plausibel aussehen.

Hintergrund: docs/profilgeometrie.de.md

    python tools/show_profile.py threads/01_TR21x4_Sodastream.xml
    python tools/show_profile.py threads/            # alle Dateien
"""

from __future__ import annotations

import glob
import math
import os
import sys
import xml.etree.ElementTree as ET

# Bekannte Normprofile: (Kopffase/P, Fussfase/P, Name)
KNOWN_PROFILES = [
    (0.366, 0.366, "ISO-Trapezgewinde (DIN 103)"),
    (0.125, 0.250, "ISO metrisch / UN (P/8 Kopf, P/4 Fuss)"),
    (0.167, 0.167, "Whitworth (P/6 oben und unten)"),
    (0.250, 0.250, "dans98-Konvention (P/4 oben und unten)"),
]
TOL = 0.01


def identify(c_rel: float, f_rel: float) -> str:
    for c, f, name in KNOWN_PROFILES:
        if abs(c_rel - c) < TOL and abs(f_rel - f) < TOL:
            return name
    return "eigene Konvention - keine Norm erkannt"


def show(path: str) -> None:
    root = ET.parse(path).getroot()
    angle = float(root.findtext("Angle"))
    half = math.tan(math.radians(angle / 2))

    print(f"\n=== {os.path.basename(path)} ===")
    print(f"{root.findtext('CustomName')}")
    print(f"Flankenwinkel {angle:g} Grad   "
          f"Ueberhang beim stehenden Druck: {90 - angle / 2:g} Grad")

    for ts in root.findall("ThreadSize"):
        for des in ts.findall("Designation"):
            pitch_txt = des.findtext("Pitch")
            pitch = float(pitch_txt) if pitch_txt else 25.4 / float(des.findtext("TPI"))
            th = des.find("Thread")
            ma, pi, mi = (float(th.findtext(t)) for t in
                          ("MajorDia", "PitchDia", "MinorDia"))

            depth = (ma - mi) / 2
            c = pitch / 2 - (ma - pi) * half
            f = pitch / 2 - (pi - mi) * half

            print(f"\n  {des.findtext('ThreadDesignation')}")
            print(f"    Steigung        {pitch:.4f} mm")
            print(f"    Gewindetiefe    {depth:.3f} mm  ({depth / pitch:.3f} x Steigung)")
            print(f"    Kopffase c      {c:.3f} mm  ({c / pitch:.3f} x Steigung)")
            print(f"    Fussfase  f     {f:.3f} mm  ({f / pitch:.3f} x Steigung)")
            print(f"    Profil          {identify(c / pitch, f / pitch)}")

            if c < 0 or f < 0:
                print("    ACHTUNG: negative Fase - Flanken schneiden sich. "
                      "Gewindetiefe ist fuer diesen Winkel zu gross.")
            elif c < 0.05 * pitch:
                print("    Hinweis: sehr spitzer Kopf - im FDM-Druck kaum darstellbar.")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    target = sys.argv[1]
    paths = sorted(glob.glob(os.path.join(target, "*.xml"))) if os.path.isdir(target) \
        else [target]
    if not paths:
        print(f"Keine XML-Dateien in {target!r}")
        return 1
    for p in paths:
        show(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
