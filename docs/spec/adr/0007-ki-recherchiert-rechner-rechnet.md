# ADR-0007 — Die KI recherchiert, der Rechner rechnet

**Status:** ✅ angenommen · **Datum:** 2026-07-25

## Kontext

Der ursprüngliche KI-Prompt ließ das Sprachmodell die **komplette XML** ausgeben: alle
Größen, sechs Klassen, je zwei Geschlechter, drei Durchmesser pro Eintrag. Für ein einzelnes
Gewinde sind das rund 40 gerechnete Zahlen, für die Trapez-Datei über 1.200.

Sprachmodelle rechnen unzuverlässig. Nicht katastrophal falsch, aber eben auch nicht
verlässlich richtig — und der Nutzer kann es nicht prüfen, weil er uns ja gerade deshalb
fragt. Bei 40 Zahlen genügt **ein** Ausrutscher, damit das Gewinde klemmt.

Dass dieses Risiko real ist, zeigt das Projekt an sich selbst: Bei der Korrektur von
PCO 1881 wurde die Steigung von 2,508 auf 2,7 mm gesetzt — die daraus abgeleiteten
Durchmesser aber nicht. Die Datei war danach in sich widersprüchlich, und zwar durch
Handarbeit, nicht durch eine KI. Genau diese Klasse von Fehlern entsteht immer dann, wenn
abgeleitete Werte einzeln angefasst werden.

## Entscheidung

> Dass abgeleitete Werte beim Handanfassen veralten, ist auch anderswo belegt →
> [QUELLEN.md F2](../../QUELLEN.md#f2)

Die Arbeit wird an der Stelle geschnitten, an der die Fähigkeiten wechseln:

| | Aufgabe | Wer kann das gut |
|---|---|---|
| **Erkennen** | „Wasserflasche" → PCO 1881 | Sprachmodell. Weltwissen, Synonyme, Rückfragen. |
| **Recherchieren** | Nennmaß 28 mm, Steigung 2,7 mm, 60° | Sprachmodell, mit Quellen. |
| **Rechnen** | daraus 72 Zahlen ableiten | Rechner. Deterministisch, prüfbar, `Decimal`. |
| **Prüfen** | Ergebnis gegen Plausibilität | Validator. |

Die KI gibt kein XML mehr aus, sondern ein **Rezept**: vier bis sechs Zahlen in TOML.

```toml
name        = "PCO1881_PET_3DPrint"
custom_name = "[3D-Print] PCO1881 - PET Bottle"
angle       = 60
sort_order  = 203

[[size]]
designation = "PCO 1881"
nominal     = 28.0
pitch       = 2.7
```

`tools/build_thread.py` macht daraus die vollständige Datei — sechs Klassen, beide
Geschlechter, alle Durchmesser, exakt gerundet.

## Warum das deutlich besser ist

**Weniger Angriffsfläche.** Statt 40 gerechneter Zahlen sind es 4 recherchierte. Rund ein
Zehntel der Gelegenheiten, danebenzuliegen.

**Der Nutzer kann gegenprüfen.** „28 mm, 2,7 mm Steigung, 60°" kann jeder mit einem
Messschieber oder einer Websuche nachvollziehen. `<PitchDia>26.346</PitchDia>` kann niemand
im Kopf verifizieren.

**Konsistenz ist erzwungen.** Ändert sich die Steigung, werden alle abgeleiteten Werte neu
gerechnet. Der PCO-1881-Folgefehler kann strukturell nicht mehr passieren.

**Der Rechner ist testbar.** Ein Sprachmodell lässt sich nicht in CI prüfen, eine Funktion
schon.

**Die Profilform steckt an einer Stelle.** Die Ableitungsregeln je Flankenwinkel
(60° → ISO-Innengewinde, 55° → Whitworth, 30/45/29° → Trapez) stehen in einer Tabelle im
Rechner, nicht verstreut in neun Dateien und einem Prompt.

## Konsequenzen

- **Der Prompt wird kürzer und einfacher.** Keine Rechenanleitung mehr, keine
  XML-Schemaregeln, kürzere Few-Shot-Beispiele. Er handelt nur noch von Erkennen, Fragen und
  Recherchieren.
- **`recipes/` wird die Quelle der Wahrheit**, `threads/*.xml` ist erzeugt. Beides liegt im
  Repo, damit Nutzer weiterhin einfach eine XML herunterladen können.
- **CI prüft, dass beides zusammenpasst.** Wer die XML von Hand ändert, fällt auf.
- **Der Rechner braucht Standardprofile je Winkel.** Für ungewöhnliche Winkel muss das Rezept
  `minor` explizit angeben — der Rechner verweigert dann lieber, als zu raten.
- **Ein Zwischenschritt mehr für den Nutzer**: Rezept kopieren, Rechner laufen lassen. Im
  geplanten Add-in verschwindet dieser Schritt wieder, weil die Einfüge-Box das Rezept direkt
  entgegennimmt (→ FA-6).

## Verworfene Alternative

**Die KI weiterhin alles ausgeben lassen und nur schärfer validieren.** Der Validator würde
grobe Fehler fangen — aber nicht die subtilen. Eine PitchDia, die 0,2 mm danebenliegt, ist
geometrisch plausibel, besteht jede Plausibilitätsprüfung und macht das Gewinde trotzdem
schlechter. Prüfen kann fehlende Korrektheit nicht ersetzen.
