# ADR-0006 — Unsichere Maße kommen nach `experimental/`

**Status:** ✅ angenommen · **Datum:** 2026-07-25

## Kontext

Für manche naheliegenden Gewinde gibt es schlicht keine belastbare öffentliche Norm. Die
Schraubglas-Gewinde 28-400, 38-400 und 45-400 sind das beste Beispiel: Der Außendurchmesser
ist grob bekannt, Steigung und Flankenwinkel sind herstellerabhängig, und Quellen nennen
Bereiche statt Werte („ca. 3,2–3,6 mm").

Gleichzeitig sind genau das Gewinde, für die Leute Deckel drucken wollen.

Verfassung § 1 verbietet Zahlen ohne Quelle. Damit wären diese Gewinde dauerhaft
ausgeschlossen — was den Nutzern nicht hilft.

## Entscheidung

Zwei Ordner mit unterschiedlichem Versprechen:

| | `threads/` | `experimental/` |
|---|---|---|
| Datenlage | Norm, Datenblatt oder Messung | Näherung, herstellerabhängig |
| `<CustomName>` | `[3D-Print] …` | `[3D-Print] … (exp.)` |
| `<SortOrder>` | 201–299 | 300+ |
| Im Release-ZIP | ✅ | ❌ |
| Validator | muss grün sein | muss grün sein |

`experimental/` bekommt eine eigene README, die je Gewinde festhält, **was** unsicher ist und
**welche Messung fehlt**.

## Aufstieg

Von `experimental/` nach `threads/` nur mit **zwei unabhängigen Messungen** oder einer
Normquelle. Der Aufstieg ist ein eigener Changelog-Eintrag mit altem und neuem Wert.

## Begründung

Die Alternative wäre gewesen, Näherungen mit einem „(ca.)" im Hauptbestand zu führen. Das
verwässert aber das Versprechen von `threads/` — und erfahrungsgemäß liest niemand die
Klammer. Eine Ordnertrennung ist unmissverständlich, und der Ausschluss aus dem Release-ZIP
sorgt dafür, dass der Standardweg nur geprüfte Daten liefert.

## Konsequenzen

- Zwei Qualitätsstufen müssen erklärt werden — Aufwand in der Doku
- Nutzer von `experimental/` müssen bewusst dorthin greifen. Das ist gewollt.
- Der Validator läuft über beide Ordner, mit `SortOrder`-Bereichen als Unterschied
