# 01 — Projekte

Repositories im Umfeld. Zahlen am 25.07.2026 über die GitHub-API abgefragt.

← zurück zur [Quellenübersicht](README.md)

---

## Überblick

| Repo | ★ | Lizenz | Letzter Push | Fokus |
|------|--:|--------|--------------|-------|
| [BalzGuenat/CustomThreads](https://github.com/BalzGuenat/CustomThreads) | 395 ✅ | MIT | 2024-09 | Metrisch grob FDM, 60° |
| [dans98/Fusion-360-FDM-threads](https://github.com/dans98/Fusion-360-FDM-threads) | 282 ✅ | BSD-3 | 2026-07 | Trapez FDM, 50–90° |
| [thomasa88/ThreadKeeper](https://github.com/thomasa88/ThreadKeeper) | 90 ✅ | MIT | 2025-02 | Add-in, keine Gewinde |
| [toddmunro/Fusion-360-Lens-Filter-Threads](https://github.com/toddmunro/Fusion-360-Lens-Filter-Threads) | 66 ✅ | **keine** | 2020-05 | Filtergewinde M37–M82 |
| [grumpytechie/Fusion360ThreadDefinitions](https://github.com/grumpytechie/Fusion360ThreadDefinitions) | 22 ✅ | GPL-3.0 | 2026-04 | PG-Gewinde, Sondergewinde |
| [matthewmcneill/FusionThreadsGenerator](https://github.com/matthewmcneill/FusionThreadsGenerator) | 4 ✅ | GPL-3.0 | 2026-06 | Britische Normen, Web-UI |

---

## BalzGuenat/CustomThreads — das populärste

**Was drin ist** ✅ (README gelesen): `3DPrintedMetricV3.xml` mit Ø 8–50 mm, Steigung nur
3,5 und 5,0 mm, durchgehend 60°. Dazu ein Python-Generator `main.py`, dessen Parameter als
Konstanten am Dateikopf stehen.

**Toleranzmodell:** Klassen `O.0` bis `O.8` verschieben Major-, Minor- **und**
Flankendurchmesser gemeinsam um Zehntelmillimeter. Das ist exakt unser Ansatz — *eine Klasse
verschiebt das Profil, sie verformt es nicht*. `O.0` ist laut README „loosely based on
ISO M30x3.5 6g/6H", also dieselbe Bezugsgröße, die wir für die Einordnung von 0,15 mm
heranziehen. → [ADR-0002](../spec/adr/0002-sechs-toleranzklassen.md)

**Die lehrreichen Issues** ✅ (abgefragt und gelesen):

| Issue | Warum es für uns zählt |
|---|---|
| [#16 Misleading tolerance descriptions](https://github.com/BalzGuenat/CustomThreads/issues/16) *(offen)* | **Identisch mit unserem v0.9.0-Fehler.** README verspricht 6g/6H, `O.0` liefert null Toleranz. Seit März 2026 offen. → begründet [FA-4.3](../spec/01-spezifikation.md#fa-4--prüfung) |
| [#2 Some combinations don't work](https://github.com/BalzGuenat/CustomThreads/issues/2) *(geschlossen)* | Generator erzeugte `PitchDia 39,23 < MinorDia 39,25` für M40×0,75 — geometrisch unmöglich. Wörtlich unsere harte Prüfung. |
| [#9 Thread size is bigger than the body](https://github.com/BalzGuenat/CustomThreads/issues/9) *(offen)* | Fusion verweigert das Gewinde, wenn die Wand zu dünn ist. Betrifft uns bis TR150×16. |
| [#12 crash](https://github.com/BalzGuenat/CustomThreads/issues/12) *(offen)* | Fusion stürzt beim Öffnen des Gewinde-Werkzeugs ab. Eine reine Konfigurationsdatei sollte das nicht können — kann es aber. |
| [#14 main.py does not create new .xml](https://github.com/BalzGuenat/CustomThreads/issues/14) *(offen)* | Generator-Bedienbarkeit |

**Praxiswert aus dem #2-Verlauf** ✅: Ein Nutzer druckt Filtergewinde M39–M80 mit 0,75 mm
Steigung **auf einem Ender 3** und nennt als eingefahrene Werte **0,2 mm innen / 0,1 mm
außen**. Belastbare Felddaten, die genau in unserem Klassenbereich liegen — und asymmetrisch
aufgeteilt. Gehört in die [Toleranz-Sammelstelle](../../../discussions/1).

---

## dans98/Fusion-360-FDM-threads — die zwei wichtigsten Erkenntnisse

**Was drin ist** ✅ (README gelesen): Trapezprofile mit Kopf- und Fußfase von je **¼ der
Steigung**, Flankenwinkel **50, 60, 70, 80, 90 Grad**, erzeugt von einem Python-Skript.
Klassen `0.###e` / `0.###i` für außen/innen, additiv.

**Erkenntnis 1 — Fusion akzeptiert mehr als fünf Winkel.** 70°, 80° und 90° kommen in keiner
Autodesk-Standarddatei vor, funktionieren hier aber seit Jahren. Das korrigierte eine falsche
Aussage in unserem KI-Prompt und beantwortet die offene Frage zu PG-Gewinden (80°).

**Erkenntnis 2 — die Überhang-Faustregel.** Aus der README:

> „the overhang angle of a thread printed in the vertical orientation is
> 90 − (threadAngle/2) degrees"

Bei 60° also 60° Überhang, bei 45° schon 67,5°. Die knappste Erklärung dafür, warum flachere
Flanken sich besser drucken. → [Profilgeometrie](../profilgeometrie.de.md)

**Nicht übernommen:** die Fasenkonvention ¼·P. Unsere Trapezprofile folgen der Norm
(0,366·P), was flachere Gewinde ergibt. Dokumentiert, falls jemand ein Profil im dans98-Stil
beitragen will.

---

## thomasa88/ThreadKeeper — Infrastruktur

Add-in, das Gewinde-XML nach jedem Fusion-Update wiederherstellt. Bringt **selbst keine
Gewinde** mit. Faktischer Standard: Sowohl BalzGuenat als auch dans98 verweisen darauf.

Ausführlich behandelt in [ADR-0003](../spec/adr/0003-threadkeeper-statt-eigenem-keeper.md)
(warum wir es nicht nachbauen) und
[ADR-0009](../spec/adr/0009-dateioperationen.md) (was wir aus seinen Fehlern gelernt haben).

**Offene Issues** ✅ (Stand 25.07.2026): #8 und #14 macOS-Installation, #9 Robustheit des
Kopierbefehls, #10 und #13 Abstürze, #11 „keine Gewinde mehr sichtbar".

> [!TIP]
> Die Fassung im **Autodesk App Store hinkt der auf GitHub um Wochen hinterher**. Anfang 2025
> war sie über einen Monat lang defekt, während GitHub bereits den Fix hatte. Bei Problemen
> zuerst die GitHub-Release probieren — dafür muss die App-Store-Version deinstalliert werden.

---

## Die kleineren

**[toddmunro/Fusion-360-Lens-Filter-Threads](https://github.com/toddmunro/Fusion-360-Lens-Filter-Threads)** — 66 ★, Filtergewinde M37–M82, letzter Push 2020.
📋 Toleranzen unklar. **Keine Lizenz** ✅ → nichts übernehmen. Als *Bedarfsnachweis*
trotzdem wertvoll: Filtergewinde werden nachgefragt.

**[grumpytechie/Fusion360ThreadDefinitions](https://github.com/grumpytechie/Fusion360ThreadDefinitions)** — 22 ★, PG-Kabelverschraubungen und Sondergewinde. GPL-3.0 ✅ → nicht übernehmbar.
Zugehöriger [Blogpost von 2017](https://grumpytechie.net/2017/11/05/custom-thread-definitions-in-autodesk-fusion-360-pg-conduit-threads/) 📋.
Für PG-Maße wäre eine Norm die bessere Quelle → [Z-2](../spec/03-review-2026-07.md).

**[matthewmcneill/FusionThreadsGenerator](https://github.com/matthewmcneill/FusionThreadsGenerator)** — 4 ★, React-Web-App für BSW, BSF, BA, ME, BSB, BSC.
📋 Laut Beschreibung mit Werkstatt-Inventarverwaltung und Live-Vorschau. GPL-3.0 ✅ →
nicht übernehmbar, aber als **Vorbild für Bedienung** interessant → [ADR-0008](../spec/adr/0008-web-rechner.md).
📋 [Live-Version](https://matthewmcneill.github.io/FusionThreadsGenerator/) — nicht geprüft.

---

## Dieses Projekt

[grapefruit89/Fusion360-CustomThread](https://github.com/grapefruit89/Fusion360-CustomThread) —
Sondergewinde des Alltags, sechs Passungsklassen, Rechner und Validator.

Alleinstellung gegenüber allen oben: **konkrete Alltagsgewinde statt generischer Normreihen**,
und die Klassenaufteilung nach der Frage *ist das Gegenstück echt oder gedruckt?*
