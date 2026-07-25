# ADR-0001 — Gewinde über XML statt Spirale + Sweep

**Status:** ✅ angenommen · **Datum:** 2026-07-24

## Kontext

Ein Gewinde in Fusion lässt sich auf zwei Wegen erzeugen: von Hand modellieren (Profil
skizzieren, Spirale anlegen, Erhebung entlang Pfad) oder Fusions eingebautes
Gewinde-Werkzeug mit einer eigenen Definitionsdatei füttern.

Der Handweg ist der, den fast alle Anleitungen empfehlen — und der, an dem fast alle
scheitern: Das Profil verdreht sich entlang des Pfades und das Ergebnis ist unbrauchbar. Im
[drucktipps3d-Forum](https://forum.drucktipps3d.de/forum/thread/45313-erhebung-entlang-pfad-verdreht-profil/)
zieht sich diese Diskussion über Seiten.

## Entscheidung

Wir liefern **`ThreadType`-XML-Dateien** und überlassen die Geometrie Fusions eigenem
Generator.

## Konsequenzen

**Gut:**
- Kein Verdrehen, weil nichts gesweept wird — Fusion rechnet das Profil
- Das Gewinde bleibt ein parametrisches Feature, nicht toter Körper
- Größe, Klasse, links/rechts und mehrgängig sind im Dialog umschaltbar
- Die Dateien sind Klartext, prüfbar und versionierbar

**Schlecht — und das ist der Preis:**
- Wir sind auf **fünf Flankenwinkel** und **symmetrische Profile** festgelegt.
  Sägezahn, Buttress und echte Rundprofile sind damit unmöglich (→ NA-1, NA-2).
- Die Dateien liegen in Fusions Versionsordner und verschwinden bei jedem Update (→ ADR-0003)
- Fusion liest sie nur beim Start — ein Neustart ist immer nötig

Der Verlust an Profilfreiheit ist der Preis dafür, dass es überhaupt zuverlässig
funktioniert. Für den Zweck des Projekts — Alltagsgewinde nachbauen — trägt der Tausch.
