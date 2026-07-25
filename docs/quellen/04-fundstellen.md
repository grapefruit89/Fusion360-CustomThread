# 04 — Fundstellen

Foren, Diskussionen und Einzelbeiträge. Weniger belastbar als Normen, aber oft die einzige
Stelle, an der ein konkretes Problem beschrieben ist.

← zurück zur [Quellenübersicht](README.md) · weiter zu [Fehlermustern](05-fehlermuster.md)

---

## Für dieses Projekt prägend

**[drucktipps3d.de — „Erhebung entlang Pfad verdreht Profil"](https://forum.drucktipps3d.de/forum/thread/45313-erhebung-entlang-pfad-verdreht-profil/)** 📋

Die Diskussion, aus der dieses Projekt hervorgegangen ist. Zeigt, warum der Weg über
Spirale + Sweep in der Praxis scheitert — und damit, warum die XML-Route die richtige ist.
→ [ADR-0001](../spec/adr/0001-xml-statt-sweep.md)

**[ThreadKeeper Issue #7 — Error with latest insider on MacOS](https://github.com/thomasa88/ThreadKeeper/issues/7)** ✅

Der vollständige Verlauf des `Autodesk Fusion.app` ↔ `Autodesk Fusion 360.app`-Problems,
inklusive der Erkenntnis, dass **beide Namen gleichzeitig im Feld existieren**. Grundlage für
[ADR-0009](../spec/adr/0009-dateioperationen.md).

**[ThreadKeeper Issue #9 — Robustness of copy command](https://github.com/thomasa88/ThreadKeeper/issues/9)** ✅

> „apparently in this configuration it only copied a blank document"

Der Beleg dafür, dass Kopieren über die Shell stillschweigend leere Dateien erzeugen kann.

**[BalzGuenat Issue #16 — Misleading tolerance descriptions](https://github.com/BalzGuenat/CustomThreads/issues/16)** ✅

Derselbe Fehler wie unser v0.9.0, unabhängig entstanden und dort seit Monaten offen.

## Weitere Diskussionen

📋 Nicht selbst geprüft:

| Link | Thema |
|---|---|
| [Autodesk — Fusion360 doesn't load custom threads](https://forums.autodesk.com/t5/fusion-support-forum/fusion360-doesn-t-load-custom-threads/td-p/9963329) | Klassiker: Gewinde werden nicht geladen |
| [Bambu Lab — 3D printing thread definition for Fusion](https://forum.bambulab.com/t/3d-printing-thread-definition-for-fusion-thread-tool/107715) | Installation, ThreadKeeper |
| [Bambu Lab — True 3D Printable Thread Generator (2025)](https://forum.bambulab.com/t/true-3d-printable-thread-generator-for-fusion360/194518) | Neuerer Python-Generator |
| [Reddit r/functionalprint — 3D-print-friendly thread types](https://www.reddit.com/r/functionalprint/comments/jii9e8/i_created_3dprintfriendly_thread_types_for_fusion/) | Früher Beitrag zum Thema |
| [Stargazers Lounge — Astro-threads for Fusion 360](https://stargazerslounge.com/topic/346425-astro-threads-for-fusion-360/) | M42, M48 — Bedarfsnachweis für Astro |
| [grumpytechie.net — PG Conduit Threads (2017)](https://grumpytechie.net/2017/11/05/custom-thread-definitions-in-autodesk-fusion-360-pg-conduit-threads/) | Ursprung der PG-Definitionen |
| [Gist — DIN 7756 Vg8 Reifenventil](https://gist.github.com/oliverhanka/3197f1782617faf48610397da4ce2311) | Einzelnes Sondergewinde |

## Praxiswerte aus dem Feld

Gesammelte Angaben zum tatsächlich nötigen Spiel. Solche Werte lassen sich nicht ausrechnen,
nur sammeln → [Toleranz-Sammelstelle](../../../discussions/1).

| Quelle | Drucker | Gewinde | Wert | |
|---|---|---|---|:-:|
| [BalzGuenat #2](https://github.com/BalzGuenat/CustomThreads/issues/2) | Ender 3 (Serienzustand) | Filtergewinde M39–M80, 0,75 mm Steigung | **0,2 mm innen / 0,1 mm außen** | ✅ |

> Auffällig: eine **asymmetrische** Aufteilung, mehr auf dem Innengewinde. Das deckt sich
> damit, dass Bohrungen im FDM-Druck typischerweise zu eng geraten, Außenmaße dagegen zu
> groß. Falls sich das in weiteren Berichten bestätigt, wäre es ein Argument, die
> Aufteilung bei „beide gedruckt" nicht exakt hälftig zu machen.
