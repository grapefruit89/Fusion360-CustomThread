# Wie Fusion aus fünf Zahlen ein Gewindeprofil macht

> Die Frage, die dieses Dokument beantwortet: *Sind die Gewindearten in Fusion
> verschiedene physikalische Formen — oder ist ein Trapezgewinde einfach ein Spitzgewinde
> ohne Spitzen?*
>
> **Kurz: Letzteres. Und das lässt sich nachrechnen.**

---

## Es gibt nur eine Form

Fusion hat **keine** Sammlung verschiedener Gewindegeometrien. Es gibt genau eine Grundform,
und alle Gewindearten sind Parametersätze davon:

```
                  ├────────── P ──────────┤
     MajorDia/2 ──┬───── c ─────┬─────────┬──   ← Kopf, gekappt
                  │            ╱ ╲        │
     PitchDia/2 ──┼──────────╱ A ╲────────┼──   ← Flankenlinie
                  │        ╱       ╲      │
     MinorDia/2 ──┴──────╱─── f ────╲─────┴──   ← Fuß, gekappt

     A = Flankenwinkel (voll, beide Flanken zusammen)
     c = Kopffase      f = Fußfase
```

Ein **Spitzgewinde** ist diese Form mit kleinen Fasen. Ein **Trapezgewinde** ist dieselbe
Form mit großen Fasen und flacherem Winkel. Ein **Vierkantgewinde** wäre der Grenzfall mit
sehr flachem Winkel. Es ist immer dasselbe Werkzeug.

## Die fünf Zahlen bestimmen das Profil vollständig

| Zahl | Was sie festlegt |
|------|------------------|
| `Pitch` | Wie breit eine Periode ist |
| `Angle` | Wie steil die Flanken stehen |
| `MajorDia − MinorDia` | Wie tief das Gewinde ist — also **wie viel vom V stehen bleibt** |
| `PitchDia` | Auf welcher Höhe die Flankenlinie liegt — und damit, **wie sich die übrige Breite auf Kopf- und Fußfase verteilt** |

Das ist nicht eine Zahl zu viel und keine zu wenig. Rechnung:

Die radiale Gewindetiefe ist $h = \frac{\text{Major} - \text{Minor}}{2}$.

Jede Flanke läuft dabei um $h \cdot \tan(A/2)$ zur Seite. Was von der Steigung übrig bleibt,
verteilt sich auf Kopf- und Fußfase:

$$c + f = P - 2 \cdot h \cdot \tan(A/2)$$

**Aber wie viel auf Kopf und wie viel auf Fuß entfällt, sagt diese Gleichung nicht.** Genau
diese eine verbleibende Freiheit legt `PitchDia` fest:

$$c = \frac{P}{2} - 2 \cdot \frac{\text{Major} - \text{Pitch}}{2} \cdot \tan(A/2)
\qquad
f = \frac{P}{2} - 2 \cdot \frac{\text{Pitch} - \text{Minor}}{2} \cdot \tan(A/2)$$

Deshalb ist `PitchDia` kein redundanter Wert, den man aus den anderen ableiten könnte. Es ist
der Parameter für die **Asymmetrie zwischen Kopf und Fuß**.

## Gegenprobe an den Dateien dieses Projekts

Rechnet man $c$ und $f$ aus den fünf Zahlen zurück, müssen die Lehrbuchwerte der jeweiligen
Norm herauskommen. Tun sie:

| Datei | `Angle` | `c / P` | `f / P` | Sollwert nach Norm | |
|-------|--------:|--------:|--------:|--------------------|:-:|
| TR21×4 Sodastream | 30° | **0,366** | **0,366** | ISO-Trapez: 0,366 · P oben und unten | ✅ |
| TR8×2 (ISO) | 30° | **0,366** | **0,366** | dito | ✅ |
| PCO 1881 | 60° | **0,125** | **0,250** | ISO metrisch: P/8 am Kopf, P/4 am Fuß | ✅ |
| 1/4"-20 UNC | 60° | **0,125** | **0,250** | dito | ✅ |
| 3/8"-16 UNC | 60° | **0,125** | **0,250** | dito | ✅ |
| E27 | 60° | **0,125** | **0,250** | dito | ✅ |
| DIN 477 CO₂ | 55° | **0,167** | **0,167** | Whitworth: P/6 oben und unten | ✅ |
| G 3/4" Gardena | 55° | **0,167** | **0,167** | dito | ✅ |
| Trapez FDM | 45° | 0,293 | 0,293 | eigene Konvention, keine Norm | — |

Die Übereinstimmung ist exakt, nicht ungefähr. `0,366 · P` ist die
Trapez-Kopffase aus der Norm, `P/8` und `P/4` sind die metrischen Abflachungen, `P/6` ist die
Whitworth-Truncation.

**Damit ist der Beweis geführt:** Die „verschiedenen Gewindearten" in Fusion sind kein
Formenkatalog, sondern verschiedene Zahlen in derselben Formel. Und die Dateien dieses
Projekts codieren normgerechte Geometrie.

> [!NOTE]
> Nebenbei erklärt das auch, warum bei den 60°-Dateien
> `MajorDia − PitchDia` ≠ `PitchDia − MinorDia` ist, bei den Trapezdateien aber gleich:
> Das metrische Profil ist **asymmetrisch gekappt** (Kopf P/8, Fuß P/4), das trapezoidale
> **symmetrisch**. Wer das für einen Fehler hält, hat die Norm auf seiner Seite —
> nur andersherum.

## Was daraus folgt

**Für eigene Gewinde:** Man braucht keinen Formentyp auszuwählen. Man wählt einen Winkel und
eine Tiefe, und die Form ergibt sich. Ein Profil mit sehr großer Tiefe wird spitz, eines mit
geringer Tiefe wird trapezförmig — bei identischem `Angle`.

**Für die Grenzen:** Alles, was diese eine Form nicht hergibt, geht auch nicht. Es gibt nur
**einen** `Angle` für beide Flanken, deshalb kein Sägezahn. Es gibt nur gerade Flanken,
deshalb kein echtes Rundgewinde. → siehe
[Spezifikation, NA-1 bis NA-2](spec/01-spezifikation.md#4-negativ-abgrenzung--was-ausdrücklich-nicht-gebaut-wird)

**Für den Druck:** Die Fasen sind der Grund, warum flachere Winkel besser drucken. Eine große
Kopffase gibt der Düse eine Fläche zum Aufsetzen; eine spitze Kuppe kann sie nicht legen. Und
der Überhangwinkel eines stehend gedruckten Gewindes ist

$$\text{Überhang} = 90^\circ - \frac{A}{2}$$

— bei 60° sind das 60°, bei 45° schon 67,5°. Regel aus [Q9](QUELLEN.md#q9).

## Die Fasen sind das Primitive

Der Rechner arbeitet deshalb **mit den Fasen**, nicht mit abgeleiteten Konstanten:

$$a = \frac{P/2 - c}{\tan(A/2)} \qquad b = \frac{P/2 - f}{\tan(A/2)}$$

Setzt man die Normfasen ein, fallen exakt die bekannten Konstanten heraus:

| Familie | c/P | f/P | Winkel | ergibt a/P | bekannt als |
|---|---:|---:|---:|---:|---|
| `iso-metric` | 1/8 | 1/4 | 60° | **0,64952** | ISO-Formel `d₂ = d − 0,64952·P` |
| `whitworth` | 1/6 | 1/6 | 55° | **0,640327** | Whitworth-Profiltiefe |
| `iso-trapezoidal` | 0,366 | 0,366 | 30° | **0,5** | Tiefe = P/2 |
| `fdm-45` | 0,293 | 0,293 | 45° | **0,5** | Tiefe = P/2 |
| `dans98` | 1/4 | 1/4 | 50–90° | je nach Winkel | Fasen = P/4 ([Q8](QUELLEN.md#q8)) |

Das ist mehr als Kosmetik: Die Fasen sind die Sprache, in der die Normen formuliert sind,
und sie gelten für **jeden** Winkel. Die Konstante 0,64952 dagegen gilt nur für 60°. Wer ein
80°-Profil braucht, kann `dans98` nehmen oder die Fasen direkt angeben — es muss nichts neu
hergeleitet werden.

Im Rezept:

```toml
angle   = 80
profile = "dans98"          # oder direkt:
# crest_flat = 0.25
# root_flat  = 0.25
```

## Drei Stufen der Genauigkeit

| Stufe | Was im Rezept steht | Wann |
|:-:|---|---|
| 1 | `nominal`, `pitch`, `angle` | Normalfall. Familie folgt aus dem Winkel. |
| 2 | zusätzlich `profile` oder `crest_flat`/`root_flat` | Andere Familie, oder Quelle nennt die Fasen |
| 3 | `minor` (und optional `pitch_dia`) in mm | **Genaueste Stufe.** Absolute Maße aus Norm oder Messung — der Rechner übernimmt sie unverändert und rechnet nur noch die Toleranzen. |

Stufe 3 ist der Grund, warum nichts fest verdrahtet sein muss: Wer belastbare Zahlen hat,
gibt sie an, und keine Annahme des Rechners kommt mehr zum Tragen.

## Nachrechnen

Die Tabelle oben stammt nicht aus einer Quelle, sondern aus den Dateien selbst:

```bash
python tools/show_profile.py threads/01_TR21x4_Sodastream.xml
```
