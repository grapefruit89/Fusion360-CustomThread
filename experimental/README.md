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

Noch leer. Vorgemerkte Kandidaten:

| Gewinde | Was unsicher ist | Was fehlt |
|---------|------------------|-----------|
| 28-400 / 38-400 / 45-400 (Schraubgläser) | Steigung und Flankenwinkel sind herstellerabhängig, keine öffentliche Norm | Messwerte von mehreren Gläsern verschiedener Hersteller |
| PCO 1810 | Steigung 3,18 mm ist belegt, der Gewindedurchmesser schwankt je nach Quelle zwischen 27,4 und 28,0 mm | Messung an einer echten alten PET-Flasche |

Messwerte gern als [Issue](../../../issues/new/choose) oder in den
[Discussions](../../../discussions/1).
