# Changelog

Alle nennenswerten Änderungen an diesem Projekt.
Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

Geplant für v1.0 — siehe [Roadmap](README.de.md#roadmap).

### Geplant

- `SortOrder` auf 200+ umstellen (kollidiert derzeit mit Autodesks 1–63)
- Toleranzklassen vereinheitlichen: `0.10 stramm` / `0.15 Standard` / `0.20 leichtgängig`
- Spiel nach Fall A/B/C aufteilen statt pauschal auf beide Seiten
- TR8×2-Konflikt auflösen (30°- und 45°-Variante liegen beide bei)
- Steigung von PCO 1881 nachmessen (Datei sagt 2,508 mm, Literatur ~2,7 mm)
- GitHub Action zur XML-Validierung

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

### Bekannte Probleme

- `SortOrder` 1–9 kollidiert mit Autodesks Standardgewinden
- Toleranzklassen sind über die Dateien hinweg uneinheitlich
- Das Spiel liegt auf beiden Gewindeseiten, was für „gedrucktes Teil auf echtes
  Gegenstück" doppelt so viel Luft ergibt wie beabsichtigt

[Unreleased]: https://github.com/grapefruit89/Fusion360-CustomThread/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/grapefruit89/Fusion360-CustomThread/releases/tag/v0.9.0
