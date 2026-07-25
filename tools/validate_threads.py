#!/usr/bin/env python3
"""
Validator fuer Fusion-Gewindedefinitionen / Validator for Fusion thread definitions.

Prueft alle XML-Dateien in threads/ auf die Fehler, die Fusions Gewindeliste
zerschiessen oder unbrauchbare Profile erzeugen koennen.

Aufruf:  python tools/validate_threads.py [ordner]
Exit 0 = alles gut, Exit 1 = Fehler gefunden.
"""

from __future__ import annotations

import glob
import re
import os
import sys
import xml.etree.ElementTree as ET

# Autodesk belegt SortOrder 1-63 in den mitgelieferten Dateien.
MIN_SORT_ORDER = 200

# Flankenwinkel, die Fusion in seinen Standarddateien verwendet.
KNOWN_ANGLES = {29.0, 30.0, 45.0, 55.0, 60.0}

# --------------------------------------------------------------------------
# Plausibilitaetsgrenzen. Ausserhalb der harten Grenzen ist mit Sicherheit
# etwas kaputt, ausserhalb der weichen Grenzen sehr wahrscheinlich.
# (hart_min, weich_min, weich_max, hart_max)
# --------------------------------------------------------------------------
RANGES = {
    # Flankenwinkel in Grad. Unter 10 Grad ist das Profil eine Nadel,
    # ueber 120 Grad praktisch flach.
    "angle":      (10.0, 25.0, 90.0, 120.0),
    # Nenndurchmesser in mm.
    "size_mm":    (0.5, 3.0, 200.0, 500.0),
    # Steigung in mm. Unter 0.2 mm kann kein Drucker, ueber 20 mm gibt es nicht.
    "pitch_mm":   (0.2, 1.0, 16.0, 30.0),
    # Gaenge pro Zoll.
    "tpi":        (2.0, 8.0, 40.0, 100.0),
    # Gewindetiefe je Flanke, als Vielfaches der Steigung.
    "depth_ratio": (0.05, 0.2, 1.0, 2.0),
    # Spiel zwischen internal und external derselben Klasse, in mm.
    "clearance":  (0.0, 0.02, 0.6, 2.0),
}


def bounded(f: "Findings", where: str, label: str, value: float, key: str,
            unit: str = "") -> None:
    """Prueft einen Wert gegen RANGES und meldet Fehler bzw. Warnung."""
    hard_lo, soft_lo, soft_hi, hard_hi = RANGES[key]
    if value < hard_lo or value > hard_hi:
        f.error(where, f"{label} = {value:g}{unit} liegt ausserhalb des moeglichen "
                       f"Bereichs {hard_lo:g}-{hard_hi:g}{unit}")
    elif value < soft_lo or value > soft_hi:
        f.warn(where, f"{label} = {value:g}{unit} ist unueblich "
                      f"(erwartet {soft_lo:g}-{soft_hi:g}{unit}) - bitte pruefen")


REQUIRED_ROOT = ("Name", "CustomName", "Unit", "Angle", "SortOrder")
DIA_TAGS = ("MajorDia", "PitchDia", "MinorDia")

# Erlaubte Abweichung zwischen Beschriftung und tatsaechlichem Spiel.
LABEL_TOLERANCE_MM = 0.011


def check_label_matches_clearance(f: "Findings", where: str, cls: str,
                                  clearance: float) -> None:
    """Prueft, ob die Zahl in der Klassenbeschriftung zum echten Spiel passt.

    Genau dieser Check haette den Fehler in v0.9.0 sofort gefunden: Die Klasse
    hiess '0.15mm (Tight)' und lieferte real 0.45 mm. Eine Beschriftung, die
    luegt, ist kein Schoenheitsfehler - sie ist der Grund, warum jemand drei
    Stunden umsonst druckt. Deshalb Fehler, nicht Warnung.
    """
    m = re.search(r"(\d+[.,]\d+)\s*mm", cls)
    if not m:
        return  # Klasse ohne Zahl - nicht unsere Konvention, nichts zu pruefen

    claimed = float(m.group(1).replace(",", "."))

    # "beide gedruckt": beide Seiten bekommen das halbe Spiel, in Summe der
    # genannte Wert. "gegen echtes Teil": die gedruckte Seite allein traegt es,
    # also entspricht der Versatz je Seite dem genannten Wert - und die
    # Differenz internal/external ist doppelt so gross.
    both_printed = "beide gedruckt" in cls.lower()
    expected = claimed if both_printed else claimed * 2

    if abs(clearance - expected) > LABEL_TOLERANCE_MM:
        hint = ("bei 'beide gedruckt' bekommt jede Seite das halbe Spiel"
                if both_printed else
                "bei 'gegen echtes Teil' traegt die gedruckte Seite den vollen Wert, "
                "die Differenz innen/aussen ist daher doppelt so gross")
        f.error(f"{where} [{cls}]",
                f"Beschriftung verspricht {claimed:g} mm, die Datei liefert aber "
                f"{clearance:.3g} mm Differenz innen/aussen (erwartet {expected:g} mm). "
                f"Merke: {hint}. Entweder die Durchmesser oder die Beschriftung korrigieren.")


class Findings:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


def num(el: ET.Element | None) -> float | None:
    if el is None or el.text is None:
        return None
    try:
        return float(el.text.strip())
    except ValueError:
        return None


def check_file(path: str, f: Findings, seen_names: dict, seen_orders: dict) -> None:
    fn = os.path.basename(path)

    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        f.error(fn, f"kein wohlgeformtes XML - {exc}")
        return

    if root.tag != "ThreadType":
        f.error(fn, f"Wurzelelement ist <{root.tag}>, erwartet <ThreadType>")
        return

    for tag in REQUIRED_ROOT:
        if root.findtext(tag) is None:
            f.error(fn, f"Pflichtfeld <{tag}> fehlt")

    # <Name> muss projektweit eindeutig sein - Kollisionen koennen Fusions
    # gesamte Gewindeliste unbrauchbar machen.
    name = (root.findtext("Name") or "").strip()
    if name:
        if name in seen_names:
            f.error(fn, f"<Name>{name}</Name> kollidiert mit {seen_names[name]}")
        seen_names[name] = fn
        if " " in name:
            f.warn(fn, f"<Name> enthaelt Leerzeichen: {name!r}")

    unit = (root.findtext("Unit") or "").strip()
    if unit not in ("mm", "in"):
        f.error(fn, f"<Unit> ist {unit!r}, erlaubt sind 'mm' oder 'in'")

    angle = num(root.find("Angle"))
    if angle is None:
        f.error(fn, "<Angle> ist keine Zahl")
    else:
        bounded(f, fn, "<Angle>", angle, "angle", " Grad")
        if angle not in KNOWN_ANGLES:
            # Kein Fehler: Fusions Generator akzeptiert auch andere Winkel.
            # dans98/Fusion-360-FDM-threads liefert 70, 80 und 90 Grad.
            f.warn(fn, f"<Angle>{angle:g}</Angle> ist kein Winkel aus Fusions "
                       f"Standarddateien {sorted(KNOWN_ANGLES)} - funktioniert, "
                       f"aber bitte begruenden")

    order = num(root.find("SortOrder"))
    if order is None:
        f.error(fn, "<SortOrder> ist keine Zahl")
    else:
        if order < MIN_SORT_ORDER:
            f.error(fn, f"<SortOrder>{order:g}</SortOrder> < {MIN_SORT_ORDER} - "
                        "kollidiert mit Autodesks Standardgewinden (1-63)")
        if order in seen_orders:
            f.error(fn, f"<SortOrder>{order:g}</SortOrder> kollidiert mit {seen_orders[order]}")
        seen_orders[order] = fn

    external_only = (root.findtext("ExternalOnly") or "").strip().lower() == "yes"

    sizes = root.findall("ThreadSize")
    if not sizes:
        f.error(fn, "keine <ThreadSize> vorhanden")

    for ts in sizes:
        size = num(ts.find("Size"))
        if size is None or size <= 0:
            f.error(fn, "<Size> fehlt oder ist nicht positiv")
        elif unit == "mm":
            bounded(f, fn, "<Size>", size, "size_mm", " mm")

        for des in ts.findall("Designation"):
            ctd = (des.findtext("CTD") or "?").strip()
            where = f"{fn} [{ctd}]"

            if des.findtext("ThreadDesignation") is None:
                f.error(where, "<ThreadDesignation> fehlt")

            has_pitch = des.find("Pitch") is not None
            has_tpi = des.find("TPI") is not None
            if not (has_pitch or has_tpi):
                f.error(where, "weder <Pitch> noch <TPI> vorhanden")
            if has_pitch and has_tpi:
                f.error(where, "<Pitch> und <TPI> gleichzeitig gesetzt")

            pitch = num(des.find("Pitch"))
            tpi = num(des.find("TPI"))
            if tpi is not None:
                bounded(f, where, "<TPI>", tpi, "tpi")
                pitch = 25.4 / tpi if tpi else None
            elif pitch is not None:
                bounded(f, where, "<Pitch>", pitch, "pitch_mm", " mm")
            if pitch is not None and pitch < 1.5 and unit == "mm":
                f.warn(where, f"Steigung {pitch:.3g} mm - unter ~1.5 mm "
                              f"verschmiert FDM das Profil")

            by_class: dict[str, set[str]] = {}
            by_class_dia: dict[tuple[str, str], float] = {}
            shapes: set[tuple[float, float]] = set()

            threads = des.findall("Thread")
            if not threads:
                f.error(where, "keine <Thread>-Bloecke")

            for th in threads:
                gender = (th.findtext("Gender") or "").strip()
                cls = (th.findtext("Class") or "").strip()
                w2 = f"{where} {cls or '?'}/{gender or '?'}"

                if gender not in ("internal", "external"):
                    f.error(w2, f"<Gender> ist {gender!r}")
                if not cls:
                    f.error(w2, "<Class> fehlt oder ist leer")

                dias = {t: num(th.find(t)) for t in DIA_TAGS}
                if any(v is None for v in dias.values()):
                    missing = [t for t, v in dias.items() if v is None]
                    f.error(w2, f"fehlende/ungueltige Durchmesser: {', '.join(missing)}")
                    continue
                if any(v <= 0 for v in dias.values()):
                    f.error(w2, "Durchmesser muss positiv sein")
                    continue

                ma, pi, mi = dias["MajorDia"], dias["PitchDia"], dias["MinorDia"]
                if not (ma > pi > mi):
                    f.error(w2, f"MajorDia > PitchDia > MinorDia verletzt "
                                f"({ma} / {pi} / {mi}) - Profil waere nach innen gestuelpt")
                else:
                    shapes.add((round(ma - pi, 4), round(pi - mi, 4)))

                # Durchmesser darf nicht weit vom Nennmass abweichen - sonst ist
                # entweder <Size> falsch oder es wurde eine Stelle vertippt.
                if size and abs(ma - size) > max(1.0, size * 0.05):
                    f.error(w2, f"MajorDia {ma:g} weicht stark von <Size> {size:g} ab")

                # Gewindetiefe je Flanke, ins Verhaeltnis zur Steigung gesetzt.
                if pitch:
                    depth = (ma - mi) / 2.0
                    bounded(f, w2, f"Gewindetiefe/Steigung ({depth:.3g} mm / {pitch:.3g} mm)",
                            depth / pitch, "depth_ratio")

                if cls and gender:
                    by_class_dia[(cls, gender)] = ma

                tap = th.find("TapDrill")
                if gender == "internal":
                    if tap is None:
                        f.error(w2, "<TapDrill> fehlt (bei internal Pflicht)")
                    elif num(tap) is not None and abs(num(tap) - mi) > 1e-6:
                        f.warn(w2, f"<TapDrill> {num(tap)} weicht von MinorDia {mi} ab")
                elif tap is not None:
                    f.error(w2, "<TapDrill> ist bei external nicht zulaessig")

                if cls and gender:
                    by_class.setdefault(cls, set()).add(gender)

            # Jede Klasse braucht beide Geschlechter, sonst fehlt im Dialog die Haelfte.
            for cls, genders in by_class.items():
                need = {"external"} if external_only else {"internal", "external"}
                missing = need - genders
                if missing:
                    f.error(f"{where} [{cls}]", f"fehlende Gender: {', '.join(sorted(missing))}")
                if external_only and "internal" in genders:
                    f.error(f"{where} [{cls}]",
                            "internal vorhanden, obwohl <ExternalOnly>yes</ExternalOnly> gesetzt ist")

                # Spiel = Innen- minus Aussendurchmesser derselben Klasse.
                mi_d = by_class_dia.get((cls, "internal"))
                ex_d = by_class_dia.get((cls, "external"))
                if mi_d is not None and ex_d is not None:
                    clearance = mi_d - ex_d
                    if clearance < 0:
                        f.error(f"{where} [{cls}]",
                                f"Innengewinde ist {abs(clearance):.3g} mm KLEINER als das "
                                f"Aussengewinde - laesst sich nicht zusammenschrauben")
                    else:
                        bounded(f, f"{where} [{cls}]", "Spiel innen/aussen",
                                clearance, "clearance", " mm")
                        check_label_matches_clearance(f, where, cls, clearance)

            # Alle Klassen einer Groesse sollten dasselbe Profil verschieben,
            # nicht die Form aendern.
            if len(shapes) > 1:
                f.warn(where, f"Profilform variiert zwischen den Klassen: {sorted(shapes)}")


def main() -> int:
    folder = sys.argv[1] if len(sys.argv) > 1 else "threads"
    paths = sorted(glob.glob(os.path.join(folder, "*.xml")))

    f = Findings()

    if not paths:
        print(f"Keine XML-Dateien in {folder!r} gefunden.")
        return 1

    # Fusion liest ausschliesslich *.xml - eine .txt hier waere unsichtbar.
    for stray in glob.glob(os.path.join(folder, "*.txt")):
        f.error(os.path.basename(stray),
                "liegt als .txt in threads/ - Fusion liest dort nur *.xml und "
                "wuerde die Datei niemals laden")

    seen_names: dict[str, str] = {}
    seen_orders: dict[float, str] = {}
    for path in paths:
        check_file(path, f, seen_names, seen_orders)

    for w in f.warnings:
        print(f"WARN  {w}")
    for e in f.errors:
        print(f"ERROR {e}")

    print(f"\n{len(paths)} Dateien geprueft - "
          f"{len(f.errors)} Fehler, {len(f.warnings)} Warnungen.")
    return 1 if f.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
