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
            inner = value[1:-1]
            # Ein " im Inneren eines "..."-Strings ist kein gueltiges TOML.
            # tomllib wuerde hier abbrechen - der Mini-Parser meldet dasselbe,
            # damit beide Wege sich gleich verhalten.
            if value[0] == '"' and '"' in inner:
                raise TomlError(
                    f"Zeile {lineno}: {key} enthaelt ein Anfuehrungszeichen. "
                    f"Nimm einen Literal-String mit einfachen Anfuehrungszeichen: "
                    f"{key} = '{inner}'")
            current[key] = inner
        elif value.startswith("[") and value.endswith("]"):
            items = [v.strip() for v in value[1:-1].split(",") if v.strip()]
            out = []
            for it in items:
                if it[:1] in ('"', "'") and it[-1:] == it[:1]:
                    out.append(it[1:-1])
                else:
                    try:
                        out.append(float(it))
                    except ValueError as exc:
                        raise TomlError(
                            f"Zeile {lineno}: {it!r} in {key} ist weder Zahl "
                            f"noch Text in Anfuehrungszeichen") from exc
            current[key] = out
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
DEFAULT_CLEARANCES = [D("0.10"), D("0.15"), D("0.20")]
DEFAULT_CASES = ["real", "both"]

# Gelaeufige Werte bekommen ein Adjektiv, damit der Nutzer nach Gefuehl waehlen
# kann statt nach Zahl. Alles andere laeuft ohne Adjektiv.
ADJECTIVE = {D("0.10"): "stramm", D("0.15"): "Standard", D("0.20"): "locker"}

CASE_LABEL = {"real": "gegen echtes Teil", "both": "beide gedruckt"}

# Sinnvoller Bereich fuer FDM. Ausserhalb wird gewarnt, aber nicht verweigert -
# wer 0.5 mm will, bekommt 0.5 mm.
CLEARANCE_SANE = (D("0.05"), D("0.40"))


def build_classes(clearances: list[D], cases: list[str],
                  explain: list[str]) -> list[tuple[str, D]]:
    """Erzeugt (Beschriftung, Versatz-je-Seite) fuer jede Kombination.

    'real'  = nur ein Teil wird gedruckt, das Gegenstueck ist echt.
              Die gedruckte Seite traegt das volle Spiel -> delta = Spiel.
    'both'  = beide Teile gedruckt, jede Seite die Haelfte -> delta = Spiel/2.
    """
    out: list[tuple[str, D]] = []
    for case in cases:
        if case not in CASE_LABEL:
            raise RecipeError(
                f"Unbekannter Fall {case!r} - erlaubt sind "
                f"{' und '.join(repr(c) for c in CASE_LABEL)}")
        for c in clearances:
            adj = ADJECTIVE.get(c)
            name = f"{c:.2f} mm" + (f" - {adj}" if adj else "")
            label = f"{name} ({CASE_LABEL[case]})"
            delta = c if case == "real" else r(c / 2)
            out.append((label, delta))
            if not (CLEARANCE_SANE[0] <= c <= CLEARANCE_SANE[1]):
                explain.append(
                    f"  ACHTUNG Spiel {c} mm liegt ausserhalb des ueblichen "
                    f"Bereichs {CLEARANCE_SANE[0]}-{CLEARANCE_SANE[1]} mm - "
                    f"wird erzeugt, aber auf eigene Gefahr")
    if not out:
        raise RecipeError("Keine Toleranzklassen - clearances oder cases ist leer")
    return out

# --------------------------------------------------------------------------
# Profilfamilien, definiert ueber Kopf- und Fussfase als Vielfaches der
# Steigung P. Das ist die Sprache, in der die Normen selbst formuliert sind -
# und daraus folgt alles andere:
#
#     a = MajorDia - PitchDia = (P/2 - c) / tan(A/2)
#     b = PitchDia - MinorDia = (P/2 - f) / tan(A/2)
#
# Nachgerechnet: ISO metrisch mit c=P/8, f=P/4 bei 60 Grad ergibt exakt
# a = 0.64952*P und b = 0.43301*P, also die bekannten ISO-Konstanten.
# Siehe docs/profilgeometrie.de.md
# --------------------------------------------------------------------------
PROFILES = {
    #  Name              Kopffase c/P   Fussfase f/P   Beleg
    "iso-metric":       (D("0.125"),   D("0.25")),    # P/8 und P/4
    "whitworth":        (D("0.166667"), D("0.166667")),  # P/6 oben und unten
    "iso-trapezoidal":  (D("0.366"),   D("0.366")),   # DIN 103
    "acme":             (D("0.366"),   D("0.366")),   # wie Trapez, 29 Grad
    "fdm-45":           (D("0.29289"), D("0.29289")), # entspricht Tiefe = P/2
    "dans98":           (D("0.25"),    D("0.25")),    # P/4, tiefer als Norm
}

# Welche Familie ohne Angabe zum Winkel gehoert.
ANGLE_DEFAULT_PROFILE = {
    D("60"): "iso-metric",
    D("55"): "whitworth",
    D("30"): "iso-trapezoidal",
    D("29"): "acme",
    D("45"): "fdm-45",
}


def flats_to_ab(crest: D, root: D, pitch: D, angle: D) -> tuple[D, D]:
    """Kopf- und Fussfase -> a und b, ueber a = (P/2 - c) / tan(A/2)."""
    t = D(str(math.tan(math.radians(float(angle) / 2))))
    c, f = crest * pitch, root * pitch
    a = (pitch / 2 - c) / t
    b = (pitch / 2 - f) / t
    if a <= 0 or b <= 0:
        raise RecipeError(
            f"Kopffase {c:.3f} mm bzw. Fussfase {f:.3f} mm ist groesser als die halbe "
            f"Steigung {pitch / 2:.3f} mm - daraus laesst sich kein Profil bauen.")
    return r(a), r(b)

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


def resolve_size(size: dict, angle: D, profile_name: str | None,
                 explain: list[str]) -> dict:
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
        # Fasen: explizit im Rezept, ueber eine benannte Familie, oder ueber den Winkel.
        if "crest_flat" in size or "root_flat" in size:
            if not ("crest_flat" in size and "root_flat" in size):
                raise RecipeError(
                    f"{name}: crest_flat und root_flat muessen beide angegeben werden.")
            crest, root = D(str(size["crest_flat"])), D(str(size["root_flat"]))
            src = "aus dem Rezept"
        else:
            fam = size.get("profile") or profile_name
            if not fam:
                fam = ANGLE_DEFAULT_PROFILE.get(angle)
            if not fam:
                raise RecipeError(
                    f"{name}: fuer Winkel {fmt(angle)} Grad ist keine Profilfamilie "
                    f"hinterlegt. Gib entweder 'profile' an ({', '.join(PROFILES)}), "
                    f"oder 'crest_flat'/'root_flat', oder 'minor' direkt.")
            if fam not in PROFILES:
                raise RecipeError(
                    f"{name}: unbekannte Profilfamilie {fam!r}. "
                    f"Bekannt: {', '.join(PROFILES)}")
            crest, root = PROFILES[fam]
            src = f"Familie {fam!r}"

        a, b = flats_to_ab(crest, root, pitch, angle)
        pitch0 = r(nominal - a)
        minor0 = r(pitch0 - b)
        H = pitch / (2 * D(str(math.tan(math.radians(float(angle) / 2)))))
        explain.append(f"  Theoretische Profilhoehe H = P / (2*tan(A/2)) = {r(H)} mm")
        explain.append(f"  Fasen {src}: Kopf {crest}*P = {r(crest * pitch)} mm, "
                       f"Fuss {root}*P = {r(root * pitch)} mm")
        explain.append(f"  -> a = (P/2 - c)/tan(A/2) = {a}, b = {b}")
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

    raw_cl = recipe.get("clearances")
    clearances = [D(str(c)) for c in raw_cl] if raw_cl else list(DEFAULT_CLEARANCES)
    cases = recipe.get("cases") or list(DEFAULT_CASES)
    classes = build_classes(clearances, cases, explain)
    explain.append(f"Toleranzklassen: {len(classes)} "
                   f"({', '.join(str(c) for c in clearances)} mm x "
                   f"{', '.join(cases)})")

    out = ['<?xml version="1.0" encoding="UTF-8"?>', "<ThreadType>",
           f"  <Name>{esc(recipe['name'])}</Name>",
           f"  <CustomName>{esc(recipe['custom_name'])}</CustomName>",
           f"  <Unit>{unit}</Unit>", f"  <Angle>{fmt(angle)}</Angle>",
           f"  <SortOrder>{sort_order}</SortOrder>"]
    if recipe.get("external_only"):
        out.append("  <ExternalOnly>yes</ExternalOnly>")

    for raw in sizes:
        explain.append(f"\n{raw.get('designation', '?')}:")
        s = resolve_size(raw, angle, recipe.get("profile"), explain)
        out.append("  <ThreadSize>")
        out.append(f"    <Size>{fmt(s['nominal'])}</Size>")
        out.append("    <Designation>")
        out.append(f"      <ThreadDesignation>{esc(s['designation'])}</ThreadDesignation>")
        out.append(f"      <CTD>{esc(s['ctd'])}</CTD>")
        tag, val = s["pitch_tag"]
        out.append(f"      <{tag}>{val}</{tag}>")

        for label, delta in classes:
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
