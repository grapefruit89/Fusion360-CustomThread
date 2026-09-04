# experimental/ — Gewinde mit unsicheren Maßen

> [!WARNING]
> Diese Gewinde sind **Näherungen**. Ihre Maße stammen nicht aus einer Norm oder Messung,
> sondern aus Quellen, die Bereiche statt Werte nennen. Sie sind bewusst **nicht** im
> Release-ZIP enthalten. Wer sie benutzt, sollte großzügiges Spiel wählen und mit
> Fehlversuchen rechnen.

Warum es diesen Ordner gibt, steht in [ADR-0006](../docs/spec/adr/0006-experimental-ordner.md).

## Regeln

| | `../threads/` | hier |
|---|---|---|
| Datenlage | Norm, Datenblatt oder Messung | Näherung, herstellerabhängig |
| `<CustomName>` | `[3D-Print] …` | `[3D-Print] … (exp.)` |
| `<SortOrder>` | 201–299 | 300+ |
| Im Release-ZIP | ✅ | ❌ |
| Validator | muss grün sein | muss grün sein |

**Aufstieg nach `threads/`** nur mit zwei unabhängigen Messungen oder einer Normquelle.

## Aktueller Inhalt

| Datei | SortOrder | Was unsicher ist |
|-------|----------:|------------------|
| `11_PCO1810_PET.xml` | 301 | Steigung 3,18 mm belegt, Außen-Ø je nach Quelle 27,4–28,0 mm |
| `12_ContinuousThread_28_38_45.xml` | 302 | Steigung und Winkel herstellerabhängig, keine öffentliche Norm |
| `303_KleanKanteen_Classic.xml` | 303 | Eine Flasche, 2013 ([bgamari](https://github.com/bgamari/klean-kanteen-cap)). Winkel 60° angenommen. Nur Classic, nicht Wide/TKWide. |

Messwerte gern als [Issue](../../../issues/new/choose) oder in den
[Discussions](../../../discussions/1).
