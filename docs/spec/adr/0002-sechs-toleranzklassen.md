# ADR-0002 — Sechs Toleranzklassen: zwei Fälle × drei Spielwerte

**Status:** ✅ angenommen · **Datum:** 2026-07-24

## Kontext

Bis v0.9.0 hatte jede Datei zwei bis drei Klassen: `0.00mm (Exact)`, `0.15mm (Tight)`,
`0.20mm (Safe)`. Beim Nachrechnen stellte sich heraus:

- `0.15mm (Tight)` gab dem Innengewinde real **+0,30 mm** und dem Außengewinde −0,15 mm.
  Gesamtspiel **0,45 mm** statt der angekündigten 0,15 mm.
- Datei 08 rechnete als einzige mit ±0,15 mm, also anders als die übrigen acht.
- `0.00mm (Exact)` beschreibt ein Gewinde, das sich **nicht schrauben lässt** — der Name
  versprach das Gegenteil dessen, was passiert.

Zusätzlich fehlte eine Unterscheidung, die praktisch entscheidend ist: Ob das Gegenstück
gedruckt oder real ist, ändert, **wohin** das Spiel gehört.

## Die Fallunterscheidung

| Fall | Nutzer druckt | Spiel gehört auf |
|:-:|---|---|
| A | nur den Deckel, Flasche ist echt | nur `internal` — `external` muss auf Nennmaß bleiben |
| B | nur den Bolzen, Gegenstück ist echt | nur `external` |
| C | beide Teile | halbes Spiel auf jede Seite |

**A und B fallen numerisch zusammen.** Wer nur den Deckel druckt, benutzt in Fusion
ausschließlich die `internal`-Hälfte der Klasse; die `external`-Hälfte sieht er nie. Eine
Klasse mit `internal +δ` und `external −δ` bedient also Fall A und Fall B gleichzeitig
korrekt — sie ist nur für Fall C zu locker, weil sich dort beide Abweichungen addieren.

Damit bleiben **zwei** Fälle statt drei.

## Entscheidung

Sechs Klassen je Datei — zwei Fälle × drei Spielwerte:

| `<Class>` | δ innen | δ außen | Wirksames Spiel |
|-----------|--------:|--------:|-----------------|
| `0.10 mm - stramm (gegen echtes Teil)` | +0,10 | −0,10 | 0,10 mm gegen das echte Teil |
| `0.15 mm - Standard (gegen echtes Teil)` | +0,15 | −0,15 | 0,15 mm ← Voreinstellung |
| `0.20 mm - locker (gegen echtes Teil)` | +0,20 | −0,20 | 0,20 mm gegen das echte Teil |
| `0.10 mm - stramm (beide gedruckt)` | +0,05 | −0,05 | 0,10 mm zwischen zwei gedruckten Teilen |
| `0.15 mm - Standard (beide gedruckt)` | +0,075 | −0,075 | 0,15 mm zwischen zwei gedruckten Teilen |
| `0.20 mm - locker (beide gedruckt)` | +0,10 | −0,10 | 0,20 mm zwischen zwei gedruckten Teilen |

`0.00mm (Exact)` entfällt ersatzlos.

**Beschriftungen tragen das Gefühl, nicht nur die Zahl.** Der Nutzer wählt nach „soll stramm
sitzen", nicht nach 0,15. Umlaute werden vermieden, weil die Darstellung in Fusions Dropdown
nicht überprüfbar ist.

## Warum kein `Exact`

Ein Gewinde mit 0,00 mm Spiel lässt sich nicht schrauben — nicht straff, sondern gar nicht.
Der Name „Exact" lockt aber ausgerechnet die Leute an, die es besonders genau haben wollen.
Ein Label, das in die Falle führt.

Das Nennmaß bleibt trotzdem verfügbar: In den Fällen A und B steht es als nicht bedruckte
Seite ohnehin in der Datei.

## Warum nicht mehr Klassen

Sechs ist die Obergrenze für ein brauchbares Dropdown. Feinere Abstufung bringt nichts,
solange die Streuung des Druckers größer ist als der Abstand zwischen den Stufen.

## Konsequenzen

- **Verhaltensänderung.** Wer bisher `Tight` gedruckt hat, findet `0.15 Standard` deutlich
  strammer — die alte Klasse hatte dreifaches Spiel. Prominent dokumentiert in README,
  CHANGELOG und Release-Notes, mit dem Hinweis „falls es klemmt, eine Stufe hochgehen".
- Zwei Klassen haben identische Zahlen (`0.10 gegen echtes Teil` = `0.20 beide gedruckt`,
  beide δ = 0,10). Das ist korrekt und kein Fehler.
- Der Validator prüft ab v1.1, ob die Zahl in der Beschriftung zum tatsächlichen Spiel
  passt — genau der Check, der den ursprünglichen Fehler sofort gefunden hätte.
- Bei Durchmessern über ~40 mm kann eine vierte Stufe `0.30 locker` sinnvoll sein, weil der
  Schwund beim Abkühlen dazukommt.
