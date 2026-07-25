#!/usr/bin/env python3
"""
Rechner: Rezept (TOML) -> fertige Fusion-Gewinde-XML.

Arbeitsteilung mit der KI (siehe docs/spec/adr/0007-ki-recherchiert-rechner-rechnet.md):

    KI      -> findet heraus, WELCHES Gewinde und liefert 4-6 Kennzahlen
    Rechner -> macht daraus alle 6 Klassen x internal/external, exakt

Damit muss ein Sprachmodell nie mehr als eine Handvoll Zahlen ausgeben, und
keine davon ist gerechnet. Alles Gerechnete passiert hier, mit Decimal.

    python tools/build_thread.py rezept.toml                 # nach stdout
    python tools/build_thread.py rezept.toml -o threads/     # als Datei
    python tools/build_thread.py rezept.toml --explain       # Rechenweg zeigen

Rezeptformat siehe docs/rezept-vorlage.toml
"""

from __future__ import annotations

import argparse
import math
import sys
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path

try:                        # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # aeltere Interpreter, u.a. der in Fusion
    tomllib = None


class TomlError(Exception):
    pass


def load_recipe(text: str) -> dict:
    """TOML lesen. Ohne tomllib greift ein Mini-Parser fuer genau die
    Teilmenge, die ein Rezept braucht: Kommentare, key = value und [[size]]."""
    if tomllib is not None:
        try:
            return tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            raise TomlError(str(exc)) from exc

    data: dict = {}
    current = data
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip() if not raw.strip().startswith("#") else ""
        if not line:
            continue
        if line == "[[size]]":
            current = {}
            data.setdefault("size", []).append(current)
            continue
        if line.startswith("["):
            raise TomlError(f"Zeile {lineno}: nur [[size]] wird unterstuetzt, nicht {line!r}")
        if "=" not in line:
            raise TomlError(f"Zeile {lineno}: kein 'key = value' - {raw!r}")
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if value[:1] in ('"', "'") and value[-1:] == value[:1] and len(value) >= 2:
            current[key] = value[1:-1]
        elif value in ("true", "false"):
            current[key] = value == "true"
        else:
            try:
                current[key] = int(value) if value.lstrip("+-").isdigit() else float(value)
            except ValueError as exc:
                raise TomlError(f"Zeile {lineno}: {value!r} ist keine Zahl") from exc
    return data

# --------------------------------------------------------------------------
# Die sechs Toleranzklassen. delta = Versatz je Seite in mm.
# Siehe docs/spec/adr/0002-sechs-toleranzklassen.md
# --------------------------------------------------------------------------
CLASSES = [
    ("0.10 mm - stramm (gegen echtes Teil)",   D("0.10")),
    ("0.15 mm - Standard (gegen echtes Teil)", D("0.15")),
    ("0.20 mm - locker (gegen echtes Teil)",   D("0.20")),
    ("0.10 mm - stramm (beide gedruckt)",      D("0.05")),
    ("0.15 mm - Standard (beide gedruckt)",    D("0.075")),
    ("0.20 mm - locker (beide gedruckt)",      D("0.10")),
]

# --------------------------------------------------------------------------
# Profilform je Flankenwinkel, als Vielfaches der Steigung P.
#   a = MajorDia - PitchDia   (Durchmesserdifferenz, nicht radial)
#   b = PitchDia - MinorDia
#
# 60 Grad: ISO-Innengewindegeometrie. D2 = D - 0.64952*P, D1 = D - 1.0825*P
# 55 Grad: Whitworth, Profiltiefe 0.640327*P, Flankenlinie mittig
# 30/45/29 Grad: Trapez-Konvention, Gesamttiefe = P, Flankenlinie mittig
# --------------------------------------------------------------------------
PROFILE = {
    D("60"): (D("0.64952"), D("0.43301")),
    D("55"): (D("0.640327"), D("0.640327")),
    D("30"): (D("0.5"), D("0.5")),
    D("45"): (D("0.5"), D("0.5")),
    D("29"): (D("0.5"), D("0.5")),
}

Q = D("0.001")


def r(v: D) -> D:
    return D(v).quantize(Q, rounding=ROUND_HALF_UP)


def fmt(v: D) -> str:
    s = f"{r(v):f}".rstrip("0").rstrip(".")
    return s or "0"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class RecipeError(Exception):
    pass


def resolve_size(size: dict, angle: D, explain: list[str]) -> dict:
    """Ergaenzt fehlende Masse aus Winkel und Steigung."""
    name = size.get("designation", "?")

    nominal = D(str(size["nominal"]))

    if "pitch" in size and "tpi" in size:
        raise RecipeError(f"{name}: pitch und tpi gleichzeitig gesetzt - nur eines angeben")
    if "tpi" in size:
        tpi = D(str(size["tpi"]))
        pitch = r(D("25.4") / tpi)
        explain.append(f"  Steigung aus {tpi} TPI: 25.4 / {tpi} = {pitch} mm")
    elif "pitch" in size:
        pitch = D(str(size["pitch"]))
    else:
        raise RecipeError(f"{name}: weder pitch noch tpi angegeben")

    # a und b: entweder explizit ueber minor/pitch_dia, oder aus dem Profil.
    if "minor" in size:
        minor0 = D(str(size["minor"]))
        if "pitch_dia" in size:
            pitch0 = D(str(size["pitch_dia"]))
        else:
            pitch0 = r((nominal + minor0) / 2)
            explain.append(f"  PitchDia nicht angegeben -> Mittelwert "
                           f"({nominal} + {minor0}) / 2 = {pitch0}")
        explain.append(f"  Profil aus gemessenen Werten uebernommen")
    else:
        if angle not in PROFILE:
            raise RecipeError(
                f"{name}: fuer Winkel {angle} gibt es keine hinterlegte Profilform. "
                f"Bekannt: {', '.join(fmt(a) for a in PROFILE)}. "
                f"Bitte 'minor' (und optional 'pitch_dia') explizit angeben.")
        fa, fb = PROFILE[angle]
        a, b = r(fa * pitch), r(fb * pitch)
        pitch0 = r(nominal - a)
        minor0 = r(pitch0 - b)
        H = pitch / (2 * D(str(math.tan(math.radians(float(angle) / 2)))))
        explain.append(f"  Theoretische Profilhoehe H = P / (2*tan(A/2)) = {r(H)} mm")
        explain.append(f"  Profil fuer {fmt(angle)} Grad: a = {fa}*P = {a}, b = {fb}*P = {b}")
        explain.append(f"  -> Major {nominal} / Pitch {pitch0} / Minor {minor0} (Nennmass)")

    if not (nominal > pitch0 > minor0):
        raise RecipeError(
            f"{name}: Major {nominal} > Pitch {pitch0} > Minor {minor0} ist verletzt. "
            f"Pruefe 'minor' und 'pitch_dia'.")

    depth = (nominal - minor0) / 2
    if pitch and not (D("0.2") <= depth / pitch <= D("1.0")):
        explain.append(f"  ACHTUNG Gewindetiefe {r(depth)} mm ist "
                       f"{r(depth / pitch)}x die Steigung - unueblich, bitte pruefen")

    return {
        "designation": size.get("designation", name),
        "ctd": size.get("ctd", name),
        "pitch_tag": ("TPI", size["tpi"]) if "tpi" in size else ("Pitch", size["pitch"]),
        "nominal": nominal, "pitch0": pitch0, "minor0": minor0,
    }


def build(recipe: dict, explain: list[str]) -> str:
    for key in ("name", "custom_name", "angle", "sort_order"):
        if key not in recipe:
            raise RecipeError(f"Pflichtfeld '{key}' fehlt im Rezept")

    angle = D(str(recipe["angle"]))
    unit = recipe.get("unit", "mm")
    sort_order = int(recipe["sort_order"])
    if sort_order < 200:
        raise RecipeError(
            f"sort_order {sort_order} < 200 - kollidiert mit Autodesks Standardgewinden. "
            f"Nimm 201-299 fuer threads/ oder 300+ fuer experimental/.")

    sizes = recipe.get("size")
    if not sizes:
        raise RecipeError("Kein [[size]]-Block im Rezept")

    out = ['<?xml version="1.0" encoding="UTF-8"?>', "<ThreadType>",
           f"  <Name>{esc(recipe['name'])}</Name>",
           f"  <CustomName>{esc(recipe['custom_name'])}</CustomName>",
           f"  <Unit>{unit}</Unit>", f"  <Angle>{fmt(angle)}</Angle>",
           f"  <SortOrder>{sort_order}</SortOrder>"]
    if recipe.get("external_only"):
        out.append("  <ExternalOnly>yes</ExternalOnly>")

    for raw in sizes:
        explain.append(f"\n{raw.get('designation', '?')}:")
        s = resolve_size(raw, angle, explain)
        out.append("  <ThreadSize>")
        out.append(f"    <Size>{fmt(s['nominal'])}</Size>")
        out.append("    <Designation>")
        out.append(f"      <ThreadDesignation>{esc(s['designation'])}</ThreadDesignation>")
        out.append(f"      <CTD>{esc(s['ctd'])}</CTD>")
        tag, val = s["pitch_tag"]
        out.append(f"      <{tag}>{val}</{tag}>")

        for label, delta in CLASSES:
            for gender, sign in (("internal", 1), ("external", -1)):
                if recipe.get("external_only") and gender == "internal":
                    continue
                ma = r(s["nominal"] + sign * delta)
                pi = r(s["pitch0"] + sign * delta)
                mi = r(s["minor0"] + sign * delta)
                out.append("      <Thread>")
                out.append(f"        <Gender>{gender}</Gender>")
                out.append(f"        <Class>{esc(label)}</Class>")
                out.append(f"        <MajorDia>{fmt(ma)}</MajorDia>")
                out.append(f"        <PitchDia>{fmt(pi)}</PitchDia>")
                out.append(f"        <MinorDia>{fmt(mi)}</MinorDia>")
                if gender == "internal":
                    out.append(f"        <TapDrill>{fmt(mi)}</TapDrill>")
                out.append("      </Thread>")
        out.append("    </Designation>")
        out.append("  </ThreadSize>")

    out.append("</ThreadType>")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Rezept (TOML) -> Fusion-Gewinde-XML")
    ap.add_argument("recipe", help="Pfad zur TOML-Datei")
    ap.add_argument("-o", "--out", help="Zielordner oder Zieldatei")
    ap.add_argument("--explain", action="store_true", help="Rechenweg ausgeben")
    args = ap.parse_args()

    try:
        recipe = load_recipe(Path(args.recipe).read_text(encoding="utf-8"))
    except TomlError as exc:
        print(f"FEHLER: {args.recipe} ist kein gueltiges Rezept - {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 1

    explain: list[str] = []
    try:
        xml = build(recipe, explain)
    except (RecipeError, KeyError, ValueError) as exc:
        print(f"FEHLER im Rezept: {exc}", file=sys.stderr)
        return 1

    if args.explain:
        print("Rechenweg:", file=sys.stderr)
        print("\n".join(explain), file=sys.stderr)
        print(file=sys.stderr)

    if args.out:
        dest = Path(args.out)
        if dest.is_dir():
            dest = dest / (recipe.get("filename") or f"{recipe['name']}.xml")
        dest.write_text(xml, encoding="utf-8", newline="\n")
        print(f"Geschrieben: {dest}", file=sys.stderr)
        print(f"Jetzt pruefen:  python tools/validate_threads.py {dest.parent}",
              file=sys.stderr)
    else:
        sys.stdout.write(xml)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
