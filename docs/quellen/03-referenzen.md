# 03 — Referenzen

Offizielle Dokumentation, Normen, Maßtabellen und Rechner.

← zurück zur [Quellenübersicht](README.md) · weiter zu [Fundstellen](04-fundstellen.md)

---

## Autodesk

[How to create custom threads and thread standards in Autodesk Fusion](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Custom-Threads-in-Fusion-360.html) ✅

Die Quelle, auf die sich alle Projekte im Umfeld berufen. Beschreibt das Ablegen der XML im
`ThreadData`-Ordner und nennt Add-ins von Drittanbietern.

**Technisch dünn:** kein Schema, keine Feldbeschreibung, kein Wort zur Validierung — und
keines dazu, dass eine fehlerhafte Datei die gesamte Gewindeliste unbrauchbar machen kann.
Thomas Axelsson schrieb im Februar 2025, der Artikel sei „not yet updated, but close
enough" ✅; die macOS-Pfade darin waren zu dem Zeitpunkt veraltet.

Damit ist [`docs/profilgeometrie.de.md`](../profilgeometrie.de.md) kein Doppel der
offiziellen Doku, sondern schließt eine Lücke.

📋 Ältere URL derselben Seite:
[knowledge.autodesk.com/…/Custom-Threads-in-Fusion-360.html](https://knowledge.autodesk.com/support/fusion-360/learn-explore/caas/sfdcarticles/sfdcarticles/Custom-Threads-in-Fusion-360.html)

## Fusions mitgelieferte Gewindedateien ✅

Selbst durchgesehen am 24.07.2026, 18 Dateien. Sie verteilen sich auf **fünf Flankenwinkel**:

| Winkel | Dateien |
|---:|---|
| 60° | ISO Metric profile, ANSI Metric M Profile, ANSI Unified Screw Threads, GB Metric profile, Inch Tapping Threads, Metric Forming Screw Threads, AFBMA Standard Locknuts, DIN Wood Screw Thread, GOST Self-tapping |
| 55° | ISO Pipe, BSP Pipe, DIN Pipe, JIS Pipe, GB Pipe Threads |
| 45° | Inch Tapping Threads **for Plastics** |
| 30° | ISO Metric Trapezoidal, Metric Tapping Threads **for Plastics** |
| 29° | ACME Screw Threads |

Zwei Befunde daraus:

1. **Die einzigen beiden „for Plastics"-Dateien nutzen 45° und 30°** — Autodesk weicht für
   Kunststoff selbst vom 60°-Standard ab. Das ist das stärkste Argument für unser
   45°-FDM-Profil.
2. **`SortOrder` 1–63 ist belegt.** ANSI Unified = 1, ANSI Metric = 2, ISO Metric = 3,
   ISO Trapezoidal = 4 … Deshalb beginnen unsere bei 201.

Zu finden unter
`%LOCALAPPDATA%\Autodesk\webdeploy\production\<hash>\Fusion\Server\Fusion\Configuration\ThreadData`.

## Normen und Formeln

| Was | Wo | |
|---|---|:-:|
| ISO 965-1 — metrische Gewindetoleranzen (6H/6g) | Grundabmaß `es(g) = −0,042 mm` bei M20×2,5 bestätigt | ✅ |
| ISO 228 — Rohrgewinde (G-Serie) | Basis für G¼ bis G¾ | 📋 |
| DIN 103 — Trapezgewinde | Kopffase 0,366 · P, nachgerechnet in [Profilgeometrie](../profilgeometrie.de.md) | ✅ |
| DIN 477 — Gasflaschenanschlüsse | W 21,8 × 1/14" | 📋 |
| ISBT Threadspecs — PET-Halsformen | PCO 1881 / 1810, [isbt.com](https://www.isbt.com/resources/isbt-threadspecs) | 📋 |

**Für 60°-Profile nützliche Formeln** ✅ (in `build_thread.py` verwendet):

- Flankendurchmesser: `d₂ = d − 0,64952 · P`
- Kerndurchmesser innen: `D₁ = D − 1,0825 · P`
- Profilhöhe: `H = P / (2 · tan(A/2))`

## Rechner und Maßtabellen

📋 Alle nicht selbst geprüft, aus der Zusammenstellung übernommen:

| Link | Wofür |
|---|---|
| [amesweb.info — Metric Thread Dimensions](https://amesweb.info/Screws/metric-thread-dimensions-calculator.aspx) | Metrische Maße und Toleranzen nach ISO 724 / 965 |
| [theoreticalmachinist.com — M Profile](https://theoreticalmachinist.com/Threads-MetricMProfile.aspx) | Metrisches Profil, Geometrie |
| [machiningdoctor.com](https://www.machiningdoctor.com/) | Sehr detaillierte Tabellen, auch BSP/G |
| [ring-plug-thread-gages.com — G-Serie](https://www.ring-plug-thread-gages.com/PDChart/G-series-Fine-thread-data.html) | BSPP-Maßtabellen |

> [!WARNING]
> Diese Rechner liefern Werte für **Metallfertigung**. Sie sind gute Ausgangspunkte für
> Nennmaße, aber ihre Toleranzen sind für FDM unbrauchbar — dafür gibt es unsere Klassen.
