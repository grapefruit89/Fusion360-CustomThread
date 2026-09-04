# Fahrplan

Stand: 2026-09-04. Leitlinie: **je einfacher, desto weniger geht kaputt.**
Die sechs Standardklassen bleiben der Weg ohne Werkzeug. Alles hier ist nur für Zahlen, die nicht in der Liste stehen, und für eine Ablage, die Fusion-Updates überlebt.

Übergeordnet gelten [docs/spec/00-verfassung.md](docs/spec/00-verfassung.md) und die ADRs.

---

## Prinzipien

1. Basis-XMLs in `threads/` sind read-only. Nutzeroutput liegt getrennt.
2. Fusion liest `MajorDia` / `PitchDia` / `MinorDia` — keine erfundenen Attribute wie `externalThreadOffset`.
3. Passung wählt man im Fusion-Dialog unter **Class**. Ein Generator ist die Ausnahme.
4. Dateien landen im `Threads/`-Ordner von [ThreadKeeper](https://github.com/thomasa88/ThreadKeeper), nicht im hash-versionierten Fusion-Installationsordner.
5. ThreadKeeper wird benutzt, nicht geforkt.
6. Keine Material-/Düsentabelle. Testring schlägt Schätzung.

---

## Nummerierung

Autodesk belegt `SortOrder` 1–63. Kollisionen können die ganze Gewindeliste unbrauchbar machen.

| Bereich | Wer |
|--------:|-----|
| 201–299 | offizielle Bibliothek (`threads/`) |
| 300–399 | `experimental/` |
| 400–499 | vom Nutzer erzeugt |
| ≥ 500 | Reserve |

Zusätzlich, hart geprüft bevor geschrieben wird:

- `<Name>` eindeutig (kein Leerzeichen), auch gegen Dateien im Zielordner
- `<SortOrder>` eindeutig und im richtigen Band
- Dateiname ASCII, keine Klammern; Nutzerdateien `user_*.xml`
- `MajorDia > PitchDia > MinorDia`
- Klassenbeschriftung und tatsächliches Spiel stimmen überein

---

## Phase 0 — `main` wieder grün

Ohne das kein Generator und kein Plugin.

- [ ] Validator: 0 Fehler (`python tools/validate_threads.py threads`)
- [ ] Doppelte Dateinummern und doppelte `SortOrder` (205–208) auflösen
- [ ] Neue Profile nur über `recipes/*.toml` → `tools/build_thread.py` erzeugen
- [ ] PCO 1810 und 28/38/45-400 nach `experimental/`, bis Norm oder zwei Messungen da sind
- [ ] G-Serie und M42/M48: Rezepte + Quellen, Spielmodell wie der Rest (Versatz auf beide Gender)
- [ ] `zidWXojJ` und die 0-Byte-ZIP `Fusion360-CustomThread-v0.9.0-threads.zip` entfernen
- [ ] README.md, README.de.md, Badge und CHANGELOG an den tatsächlichen Dateibestand anpassen

Erledigt, wenn CI (`validate.yml`) auf `main` grün ist und `threads/` bitgleich aus den Rezepten kommt.

---

## Phase 1 — Offset aus Basis-XML

Ziel: fertige Geometrie bleibt, der Nutzer setzt nur δ.

### Rechnung

Gleiche Regel wie die sechs Klassen:

| Fall | δ je Seite |
|------|-------------|
| gegen echtes Teil | volles δ (internal +, external −) |
| beide gedruckt | δ / 2 je Seite |

Verschoben werden immer alle drei Durchmesser, Profilform bleibt.

### Variante A — Extra-Klasse in derselben Datei

Zusätzliche `<Class>`, z. B. `0.25 mm - eigen`. Gleicher `<Name>`, gleiche `<SortOrder>`. Keine Kollision. Nachteil: ein Bibliotheks-Update überschreibt die Extra-Klasse.

### Variante B — Sidecar (Standard für Nutzerpassungen)

Neue Datei, neuer Name, neue SortOrder ≥ 400:

```text
Name:       TR21x4_Sodastream_3DPrint_u25
CustomName: [3D-Print] TR21x4 - SodaStream (0.25 eigen)
SortOrder:  401
Datei:      user_TR21x4_0.25.xml
```

Variante B überlebt Updates der Bibliothek. Deshalb ist B der Weg für „meine Passung behalten“.

### CLI zuerst, kein UI

`tools/build_thread.py` erweitern, nicht ein zweites Skript bauen:

```bash
python tools/build_thread.py recipes/01_TR21x4_Sodastream.toml \
  --clearances 0.25 --cases real \
  --sort-order 401 \
  --name-suffix u25 \
  -o generated/
```

Danach `python tools/validate_threads.py generated/`. Erst wenn das sitzt, kommt eine Oberfläche daran.

Erledigt, wenn eine Testdatei mit eigenem δ den Validator übersteht und in Fusion als eigener `[3D-Print]`-Eintrag erscheint.

---

## Phase 2 — Plugin als Schreiber, nicht als Pfadsucher

Das Add-in erzeugt die Sidecar-XML und legt sie in ThreadKeepers `Threads/`-Ordner. Fusion-Neustart, fertig. Den `production/<hash>/.../ThreadData`-Ordner jagt das Plugin nicht.

Ablauf:

1. Gewinde wählen (Basisprofil)
2. Spiel in mm + Fall (echt / beide)
3. Vorschau der drei Durchmesser
4. Speichern nach ThreadKeeper/`Threads/` unter `user_*.xml`
5. Hinweis: Fusion einmal komplett beenden und neu starten

Ohne ThreadKeeper: optional denselben Fallback wie `tools/find-threaddata.bat` (laufende Fusion-Instanz). Nicht als Hauptweg versprechen.

Das Plugin ist **kein** zweiter ThreadKeeper. Kein Auto-Restore, kein Fork, kein Mitliefern von Thomas’ Code.

Mindestumfang der ersten Version:

- [ ] Basisprofile auflisten
- [ ] δ + Fall abfragen
- [ ] Sidecar schreiben (Variante B)
- [ ] gegen vorhandene `<Name>` / `<SortOrder>` im Zielordner prüfen
- [ ] Ziel: ThreadKeeper/`Threads/`, sonst Meldung mit Anleitung
- [ ] Validator-Regeln vor dem Schreiben

Nicht in v1 des Plugins: Materialmatrix, Web-Rechner, eigener Sync, Paste-Box für KI-XML.

---

## Phase 3 — erst danach

Nur wenn Phase 0–2 langweilen:

- Kalibrierring (drei Passungen nebeneinander + Gegenstück)
- `find-threaddata.sh` für macOS als dokumentierter Fallback
- Englische Klassen-Aliase
- Web-Rechner, **wenn** er dieselbe Funktion nutzt wie `build_thread.py`

---

## Ausdrücklich nicht

- ThreadKeeper forken und XMLs dort einchecken
- `externalThreadOffset` / `modelingThreadClearance` auf die XML-Wurzel setzen
- PLA/PETG/Nylon × Düse × Passung als Tabelle ausliefern
- JSON-Rezeptparser und TOML-Rechner parallel weiterwachsen lassen; eine Pipeline
- Unsichere Maße nach `threads/` statt nach `experimental/`

---

## Reihenfolge in einem Satz

Zuerst `main` reparieren. Dann denselben Rechner um ein frei wählbares δ und eine Sidecar-Datei ergänzen. Dann ein schmales Plugin, das diese Datei nach ThreadKeeper schreibt.
