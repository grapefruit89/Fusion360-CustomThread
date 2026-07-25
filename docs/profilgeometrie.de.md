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

— bei 60° sind das 60°, bei 45° schon 67,5°.

## Nachrechnen

Die Tabelle oben stammt nicht aus einer Quelle, sondern aus den Dateien selbst:

```bash
python tools/show_profile.py threads/01_TR21x4_Sodastream.xml
```
