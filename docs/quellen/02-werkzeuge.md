# 02 — Werkzeuge

Add-ins und Generatoren, auch die außerhalb von GitHub.

← zurück zur [Quellenübersicht](README.md) · weiter zu [Referenzen](03-referenzen.md)

---

## ThreadKeeper — Wiederherstellung nach Updates

[github.com/thomasa88/ThreadKeeper](https://github.com/thomasa88/ThreadKeeper) ✅ · MIT · 90 ★

Das einzige weit verbreitete Add-in für das Update-Problem. Details in
[01 — Projekte](01-projekte.md#thomasa88threadkeeper--infrastruktur).

Auch im [Autodesk App Store](https://apps.autodesk.com/FUSION/en/Detail/Index?id=1725038115223093226) 📋 —
dort aber **veraltet**, siehe Hinweis in 01.

## Marcus Wakefield — Custom Thread Utility

📋 **Nicht selbst geprüft.** Aus der Zusammenstellung vom 25.07.2026:

- Desktop-Anwendung für Windows und macOS
- Konvertiert Fusion-XML nach CSV, lässt bearbeiten, exportiert zurück nach XML
- Kann Durchmesser global versetzen — genau der Anwendungsfall FDM-Spiel
- Vertrieb über [Ko-fi](https://ko-fi.com/marcuswakefield) 📋, kein öffentliches Repository
- Vorstellung im [Autodesk-Forum](https://forums.autodesk.com/t5/fusion-design-validate-document/fusion-360-custom-thread-utility/td-p/11722781) 📋

**Warum das für uns interessant ist:** Es ist funktional das nächste Gegenstück zu
`tools/build_thread.py` — und es ist **nicht quelloffen**. Damit ist es zugleich der stärkste
Beleg für die Lücke, die [ADR-0008](../spec/adr/0008-web-rechner.md) schließen soll: ein
offenes Werkzeug, das dasselbe kann, ohne Installation und ohne Bezahlschranke.

> [!NOTE]
> Vor einer Erwähnung in der README sollte jemand das Werkzeug tatsächlich ausprobiert
> haben. Bis dahin steht es nur hier.

## Generatoren in den Repos

| Werkzeug | Sprache | Bedienung |
|---|---|---|
| [BalzGuenat `main.py`](https://github.com/BalzGuenat/CustomThreads) ✅ | Python | Konstanten am Dateikopf editieren, Skript starten |
| [dans98 Generator](https://github.com/dans98/Fusion-360-FDM-threads) ✅ | Python | dito |
| [matthewmcneill Web-App](https://github.com/matthewmcneill/FusionThreadsGenerator) ✅ | React | Echte Oberfläche, drei Schritte |
| **[`tools/build_thread.py`](../../tools/build_thread.py)** (dieses Projekt) | Python | Rezept als TOML, Daten getrennt vom Code |

Der Unterschied unseres Ansatzes: Die Parameter liegen in
[`recipes/`](../../recipes/) als eigene Dateien, nicht als Konstanten im Skript. Dadurch
lässt sich in der CI prüfen, ob die ausgelieferten XML noch zu ihren Rezepten passen — wer
eine XML von Hand ändert, fällt auf.

## Ältere und verstreute Werkzeuge

📋 Alle nicht geprüft:

- [C#-Trapezgenerator von 2020](https://forums.autodesk.com/t5/fusion-design-validate-document/custom-threads-xml-generator/td-p/9594220) — Windows-`.exe` mit Quelltext. Veraltet.
- [Bambu-Lab-Forum: „True 3D Printable Thread Generator" (2025)](https://forum.bambulab.com/t/true-3d-printable-thread-generator-for-fusion360/194518) — neueres Python-Skript, metrisch.
- Diverse Einzelskripte auf Reddit und in Foren. Kommen und gehen.
