# Changelog

Alle nennenswerten Änderungen an diesem Projekt.
Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [1.0.0] — 2026-07-24

Alle bekannten Datenfehler behoben. **Die Gewindemaße haben sich geändert** — bitte den
Abschnitt „Geändert" lesen, bevor du weiterdruckst.

### Behoben

- **Toleranzklassen logen.** `0.15mm (Tight)` hat dem Innengewinde tatsächlich **+0,30 mm**
  zugeschlagen und dem Außengewinde −0,15 mm — in Summe 0,45 mm statt der angekündigten
  0,15 mm. `0.20mm (Safe)` entsprechend 0,60 mm. Die neuen Klassen halten, was ihr Name sagt.
- **`SortOrder` kollidierte mit Autodesk.** Die Werte 1–9 sind von den mitgelieferten
  Standardgewinden belegt (ANSI Unified = 1, ANSI Metric = 2, ISO Metric = 3,
  ISO Trapezoidal = 4 …). Jetzt 201–209, dadurch stehen alle `[3D-Print]`-Einträge sauber
  gruppiert am Ende der Liste.
- **Steigung von PCO 1881** von 2,508 mm auf die belegten **2,7 mm** korrigiert. Eine falsche
  Steigung führt dazu, dass das Gewinde nach wenigen Gängen klemmt, egal wie das Spiel
  eingestellt ist.
- **Datei 08 rechnete anders als alle anderen.** Sie verwendete ±Spielwert, die übrigen acht
  +2×/−1×. Jetzt einheitlich.
- Doppelte Leerzeichen in allen `<CustomName>` entfernt.

### Geändert

- **Sechs Toleranzklassen statt zwei**, aufgeteilt nach der Frage, was gedruckt wird:

  | Klasse | Versatz innen / außen |
  |--------|----------------------:|
  | `0.10 mm - stramm (gegen echtes Teil)` | +0,10 / −0,10 |
  | `0.15 mm - Standard (gegen echtes Teil)` | +0,15 / −0,15 |
  | `0.20 mm - locker (gegen echtes Teil)` | +0,20 / −0,20 |
  | `0.10 mm - stramm (beide gedruckt)` | +0,05 / −0,05 |
  | `0.15 mm - Standard (beide gedruckt)` | +0,075 / −0,075 |
  | `0.20 mm - locker (beide gedruckt)` | +0,10 / −0,10 |

  `0.00mm (Exact)` ist entfallen. Ein Gewinde ohne Spiel lässt sich nicht schrauben — der
  Name versprach das Gegenteil dessen, was passiert.

- **TR8×2-Konflikt aufgelöst.** Beide Varianten bleiben, heißen aber jetzt eindeutig:
  `Trapezoidal 30 deg (ISO)` für gekaufte Gewindestangen, `Trapezoidal 45 deg (FDM)` für
  selbst gedruckte Paare.

> [!IMPORTANT]
> Wer bisher `0.15mm (Tight)` gedruckt hat, findet `0.15 mm - Standard (gegen echtes Teil)`
> **deutlich strammer** — die alte Klasse hatte real dreimal so viel Luft. Falls es klemmt:
> eine Stufe hochgehen.

### Hinzugefügt

- `tools/validate_threads.py` — prüft alle XML-Dateien gegen Struktur- und
  Plausibilitätsregeln (Winkel, Durchmesser, Steigung, Gewindetiefe, Spiel, Profilform,
  eindeutige Namen und SortOrder, verirrte `.txt`-Dateien)
- GitHub Action `validate.yml` — läuft bei jedem Push auf `threads/`
- GitHub Action `release.yml` — baut und hängt die ZIPs automatisch an jeden Tag
- Issue-Vorlagen für Passungsprobleme, neue Gewinde und Fehler
- `CONTRIBUTING.md`
- GitHub Discussions, u. a. eine Sammelstelle für Toleranzwerte je Drucker

### Offen

- Gewinde-Außendurchmesser von PCO 1881: die Dateien rechnen mit 28 mm, Quellen nennen
  ~27,4 mm für das Gewinde (28 mm ist die Bezeichnung des Flaschenhalses). Braucht eine
  Messung am echten Teil — [Issue #1](https://github.com/grapefruit89/Fusion360-CustomThread/issues/1).

## [0.9.0] — 2026-07-24

Erste Veröffentlichung auf GitHub. Überführung der bisherigen ZIP-Sammlung
in ein Repository.

### Hinzugefügt

- 9 Gewindedefinitionen mit insgesamt 41 Größen
- Zweisprachige README (Deutsch / Englisch)
- `docs/konzept.de.md` — Architektur- und Refactoring-Konzept
- `docs/ai-assistant-prompt.de.md` — System-Prompt für KI-gestützte Gewindeerstellung
- `tools/find-threaddata.bat` — findet den ThreadData-Ordner der laufenden Fusion-Instanz
- `examples/CO2-Gewindeschutzkappe.f3d`
- MIT (Code) + CC BY 4.0 (Gewindedaten)

### Behoben

- **Das Trapezgewinde-Paket war eine `.txt`-Datei.** Fusion liest im ThreadData-Ordner
  ausschließlich `*.xml` — die 33 Trapezgrößen von TR8×2 bis TR150×16 wurden also nie
  geladen. Die Endung war ursprünglich Absicht, weil das Quellforum kein XML akzeptiert.
  Im Repo heißt die Datei jetzt korrekt `.xml`.

### Entfernt

- `neu 3.bat` — byte-identische Kopie von `Thread Data Ordner finder.bat`
- `VirusTotal - Home.url` — steht jetzt als Link in der README

[1.0.0]: https://github.com/grapefruit89/Fusion360-CustomThread/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/grapefruit89/Fusion360-CustomThread/releases/tag/v0.9.0
