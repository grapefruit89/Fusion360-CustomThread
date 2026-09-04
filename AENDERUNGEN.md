# Änderungen nach ROI

Stand: 2026-09-04. Oben = zuerst machen. ROI = Nutzen ÷ Aufwand, mit Risiko für Druckteile gewichtet.
Phasen: siehe [FAHRPLAN.md](FAHRPLAN.md).

Aufwand: **S** < 1 h · **M** 1–4 h · **L** 1–2 Tage · **XL** mehrere Tage.

---

## Sofort — Phase 0

| # | Änderung | Aufwand | Warum der ROI hoch ist |
|--:|----------|:-------:|------------------------|
| 1 | `zidWXojJ` und `Fusion360-CustomThread-v0.9.0-threads.zip` (0 Byte) löschen | S | Müll in der Root. Zwei Dateien, null Risiko. |
| 2 | `SortOrder` und Dateinummern eindeutig machen (205–208 sind doppelt) | S | Kollision kann Fusions **ganze** Gewindeliste zerschießen. Kleiner Diff, größter Schaden vermieden. Band: 201–209 Bestand, 210+ neue offizielle, 300+ experimental. |
| 3 | PCO 1810 und 28/38/45-400 aus `threads/` nach `experimental/` | S | Steht so in ADR-0006 und `experimental/README.md`. Unsichere Ø im Release = falsche Deckel. Verschieben + SortOrder ≥ 300 + `(exp.)` im Namen. |
| 4 | Neue Profile über Rezepte neu bauen, nicht von Hand | M | Generator existiert. Hand-XML hat das einseitige Spiel (Deckel ohne Luft). Rezept + `build_thread.py` zieht das Modell gerade und macht CI wieder grün. |
| 5 | G¼/G⅜/G½ und M42/M48: Quelle ins Rezept, Spiel wie der Rest (innen + / außen −) | M | Das sind die Dateien, die Leute als Nächstes drucken. Ein falsch sitzender Deckel verbrennt mehr Vertrauen als jedes Feature. |
| 6 | README.md, README.de.md, Badge, CHANGELOG an den echten Bestand | S | Texte sagen 41/9, Baum hat mehr und CI ist rot. Fünf Dateien anfassen. |

**Done, wenn:** `python tools/validate_threads.py threads` → 0 Fehler und `validate.yml` auf `main` grün.

---

## Danach — kleiner Hebel an bestehendem Werkzeug

| # | Änderung | Aufwand | Warum danach |
|--:|----------|:-------:|--------------|
| 7 | Feine Steigungen in `<CustomName>` warnen (UNC ¼-20, G¼, M48×0,75) | S | Validator warnt schon. Ein Wort im Dropdown spart Fehlversuche. |
| 8 | `docs/rezept-vorlage.toml` anlegen (steht in `build_thread.py`, Datei fehlt) | S | Ohne Vorlage erzeugt die nächste KI wieder Hand-XML. |
| 9 | CLI an `build_thread.py`: `--clearances`, `--cases`, `--sort-order`, `--name-suffix` | M | Felder gibt es im Rezept schon. Flags sparen Copy-Paste und sind Phase 1 ohne neues Skript. |
| 10 | Sidecar-Konvention dokumentieren (`user_*.xml`, SortOrder 400+) | S | Eine halbe Seite in FAHRPLAN reicht; sonst entstehen wieder `05_*.xml`-Zwillinge. |
| 11 | pytest für `build_thread.py` in `validate.yml` (ein Rezept → XML-Snapshot + Klassen-Check) | M | Der JSON-Parser in `src/` wird getestet, der echte Rechner nicht. Ein Test hätte den Toleranzbug in v0.9.0 gesehen. |
| 12 | JSON-Parser (`src/thread_recipe_parser.py`) als tot markieren oder löschen | S | Zweite Rezeptwelt. Wer sie anfasst, pflegt zwei Formate. |

**Done, wenn:** `python tools/build_thread.py recipes/01_....toml --clearances 0.25 --cases real --sort-order 401 --name-suffix u25 -o generated/` eine valide Sidecar-XML schreibt.

---

## Wenn Phase 0+1 sitzen

| # | Änderung | Aufwand | ROI |
|--:|----------|:-------:|-----|
| 13 | `find-threaddata.sh` für macOS (nur Fallback) | S | Lücke in FA-2. Hilft wenigen, kostet wenig. Hauptweg bleibt ThreadKeeper. |
| 14 | Kalibrierring `.f3d` + STL (drei Klassen + Gegenstück) | L | Spart jedem Nutzer den eigenen Testring. Einmal CAD, lange Wirkung. Nicht blockierend. |
| 15 | Issue #3: PCO-1881-Außendurchmesser messen | M + Teil | Eine Messung, dann eine Zahl im Rezept. Hoher Nutzen, aber du brauchst das Teil. |
| 16 | Englische Klassen-Aliase *oder* zweisprachige Labels | M | Alle XML neu erzeugen. Nett für Reichweite, ändert keine Passung. |
| 17 | README-Abschnitt „Warum nicht CustomThreads / ShortyCM?“ | S | Aus dem Vergleichstext, mit richtigen Star-Zahlen und Stand-Datum. |

---

## Später — nur mit UI-Grund

| # | Änderung | Aufwand | Bedingung |
|--:|----------|:-------:|-----------|
| 18 | Fusion-Add-in: Sidecar schreiben nach ThreadKeeper/`Threads/` | XL | CLI aus #9 muss stehen. Kein eigener Sync, kein Fork. |
| 19 | Web-Rechner an `build_thread.py` anbinden (eine Formel) | L | Sonst driftet JS gegen Python. Nicht vorher. |
| 20 | Plugin: Paste-Box für fremde XML + Validator | L | Roadmap v2, nachdem #18 langweilig ist. |

---

## Nicht tun (ROI negativ)

| Idee | Warum nicht |
|------|-------------|
| ThreadKeeper forken und XMLs dort einchecken | Merge-Schuld, falsches Add-in, du pflegst Thomas’ Code |
| `externalThreadOffset` auf die XML-Wurzel setzen | Fusion liest das Feld nicht |
| Material × Düse × Passung als Tabelle | Unbelegt, unverifizierbar, Verfassung § 1 |
| Eigenen Thread-Keeper / Auto-Copy in `production/<hash>` | Genau das Update-Problem, das ThreadKeeper löst |
| Trapez-Datei in viele Dateien splitten | Fusion hat Type + Size getrennt; eine Datei ist richtig |
| JSON- und TOML-Rezepte parallel ausbauen | Eine Pipeline |

---

## Empfohlene Reihenfolge diese Woche

```text
1 → 2 → 3 → 4 → 5 → 6     main grün, Zahlen wahr
7 → 8 → 9 → 10             Offset-CLI
11 → 12                     Tests, totes Holz weg
13 / 14 / 15                nach Bedarf, parallel möglich
18                          erst wenn 9 im Alltag sitzt
```

Nicht parallel zu 1–6 an Plugin oder Web-Rechner arbeiten. Solange der Validator rot ist, ist jedes neue Feature eine zweite Baustelle auf kaputtem Boden.
