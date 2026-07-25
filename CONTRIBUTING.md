# Mitmachen / Contributing

Kurz: **Messwerte schlagen Meinungen.** Alles andere ergibt sich.

> Short version: **measurements beat opinions.** Everything else follows.

---

## Was am meisten hilft

1. **Gemessene Werte.** Wenn ein Gewinde nicht passt, ist die Zahl vom Messschieber
   hundertmal wertvoller als „passt nicht". → [Issue anlegen](../../issues/new/choose)
2. **Welche Klasse auf welchem Drucker funktioniert.** Das lässt sich nicht ableiten, nur
   sammeln. → [Discussions › Toleranzen](../../discussions/categories/toleranzen)
3. **Fehlende Gewinde** mit Maßen oder Normbezeichnung.

## Bevor du einen Pull Request aufmachst

```bash
python tools/validate_threads.py threads
```

Muss ohne Fehler durchlaufen — die CI prüft dasselbe. Der Validator kennt:

- wohlgeformtes XML, Pflichtfelder, eindeutige `<Name>` und `<SortOrder>`
- `SortOrder` ≥ 200 (darunter kollidiert es mit Autodesks Standardgewinden)
- `MajorDia > PitchDia > MinorDia`
- jede `<Class>` mit `internal` **und** `external`
- `<TapDrill>` nur bei `internal`, gleich `MinorDia`
- Plausibilitätsgrenzen für Winkel, Durchmesser, Steigung, Gewindetiefe und Spiel
- verirrte `.txt`-Dateien in `threads/`

## Konventionen für neue Gewinde

| Regel | Warum |
|-------|-------|
| `SortOrder` ab 200 aufwärts, eindeutig | sonst verschiebt sich die Reihenfolge der Standardgewinde |
| `<Name>` ohne Leerzeichen, projektweit eindeutig | Kollisionen können Fusions ganze Gewindeliste unbrauchbar machen |
| `<CustomName>` beginnt mit `[3D-Print]` | so gruppieren sich alle Einträge im Dropdown |
| Dateiname `NN_Kurzname.xml`, ASCII, keine Klammern | Klammern und doppelte Leerzeichen machen in URLs und Skripten Ärger |
| Alle sechs Standardklassen mitliefern | damit man im Dialog durchprobieren kann, ohne Dateien zu tauschen |
| Profilform über alle Klassen identisch | eine Klasse verschiebt das Profil, sie verformt es nicht |

Die sechs Klassen und ihre Versätze stehen in der
[README](README.de.md#toleranzklassen).

## Wenn du einen Rechenfehler meldest

Dann ist die Frage **ist die Rechnung richtig?** — nicht *gehoert der Anwendungsfall zu uns?*
Der Zuschnitt des Projekts entscheidet ueber **Aufnahme**, nicht ueber **Korrektheit**.

Warum das ausdruecklich dasteht: In einem verwandten Projekt wurde ein Bericht ueber
geometrisch unmoegliche Werte zunaechst mit *passt nicht zu unserem Zweck* zurueckgewiesen.
Der Fehler war real → [F7](docs/QUELLEN.md#f7).

## Was nicht ins Projekt kommt

- **Gewinde für sicherheitsrelevante Anwendungen.** Druckbehälter, stromführende Teile,
  tragende Verschraubungen. Auch nicht „nur zum Ausprobieren".
- **Geschätzte Maße.** Lieber ein Issue mit „gemessen habe ich das hier, kann jemand
  gegenprüfen?" als eine Datei mit erfundenen Zahlen.
- **Asymmetrische Profile.** Geht technisch nicht — Fusion kennt nur einen `<Angle>` für
  beide Flanken. Siehe [README](README.de.md#eigene-gewinde-bauen).

## Sprache

Deutsch oder Englisch, beides ist willkommen. Die Doku wird zweisprachig gepflegt
(`README.md` / `README.de.md`) — bei inhaltlichen Änderungen bitte beide anfassen oder
im PR vermerken, dass eine Seite noch fehlt.
