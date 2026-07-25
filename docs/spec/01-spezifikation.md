# Spezifikation

> **Was** das Projekt leisten muss und **warum** — bewusst ohne Technologie.
> Die Umsetzung steht im [technischen Plan](02-technischer-plan.md).
> Übergeordnet gilt die [Verfassung](00-verfassung.md).

**Version 1.0 · Stand 25.07.2026**

---

## 1. Problem

Wer in Autodesk Fusion ein Gewinde für den 3D-Druck braucht, hat drei Probleme:

1. **Fusions Standardgewinde sind für Metall gerechnet.** Sie klemmen im Druck, weil
   Kunststoff quillt, die Düse Spitzen verrundet und die erste Schicht ausbeult.
2. **Sondergewinde fehlen komplett.** Sodastream, PET-Flasche, Gardena, Stativ, Gasflasche —
   nichts davon ist in Fusion enthalten, obwohl es genau die Teile sind, für die Privatleute
   Adapter drucken.
3. **Selbst modellieren scheitert.** Der übliche Weg (Profil zeichnen, Spirale, Erhebung
   entlang Pfad) verdreht das Profil unterwegs.

Dazu kommt ein viertes, das erst nach der Lösung auftritt: **Nach jedem Fusion-Update sind
die Gewinde weg**, weil Fusion sich in einen neuen Ordner installiert.

## 2. Zielgruppe

**Primär:** Privatanwender mit FDM-Drucker, der einen Adapter oder Deckel für ein reales
Objekt braucht. Kann Fusion bedienen, kennt aber keine Gewindegeometrie. Findet AppData
nicht. Will nicht rechnen.

**Sekundär:** Fortgeschrittene, die ein eigenes Gewinde ableiten wollen und eine verlässliche
Vorlage plus Erklärung suchen.

**Ausdrücklich nicht:** Maschinenbauer, die normgerechte Metallgewinde brauchen. Für die ist
Fusions Standardbestand richtig.

## 3. Funktionale Anforderungen

### FA-1 — Gewindebibliothek

| ID | Anforderung |
|----|-------------|
| FA-1.1 | Gewindeprofile liegen als Fusion-`ThreadType`-XML vor, die Fusion ohne Zusatzsoftware liest. |
| FA-1.2 | Jede Datei bringt **alle sechs Toleranzklassen** mit, damit ohne Dateitausch durchprobiert werden kann. |
| FA-1.3 | Klassen sind nach dem Anwendungsfall benannt, nicht nur nach der Zahl → siehe [ADR-0002](adr/0002-sechs-toleranzklassen.md). |
| FA-1.4 | `<CustomName>` beginnt mit `[3D-Print]`, damit alle Einträge im Dropdown zusammenstehen. |
| FA-1.5 | `<SortOrder>` ≥ 200, damit die Reihenfolge der Standardgewinde unberührt bleibt. |
| FA-1.6 | Jede Datei ist einzeln installierbar. Wer nur PET braucht, kopiert eine Datei. |

### FA-2 — Installation

| ID | Anforderung |
|----|-------------|
| FA-2.1 | Der Nutzer findet den ThreadData-Ordner, ohne ihn zu kennen. |
| FA-2.2 | Der Weg dorthin ist **ein Doppelklick** (Windows) bzw. ein Menüpunkt (Add-in). |
| FA-2.3 | Das Werkzeug meldet ausführlich, was es gefunden und getan hat — welche Fusion-Instanz, welcher Pfad, welche Dateien neu/ersetzt/unverändert. |
| FA-2.4 | Der nötige Neustart wird unübersehbar angesagt. |
| FA-2.5 | macOS wird zumindest dokumentiert abgedeckt. |

### FA-3 — Eigene Gewinde ableiten

| ID | Anforderung |
|----|-------------|
| FA-3.1 | Der Nutzer beschreibt in normaler Sprache, was er drucken will, und bekommt eine fertige XML → KI-Prompt. |
| FA-3.2 | Der Prompt enthält den Katalog bekannter Gewinde, damit die KI nicht raten muss. |
| FA-3.3 | Der Prompt fragt **zuerst**, ob das Gegenstück echt ist — das entscheidet, wohin das Spiel kommt. |
| FA-3.4 | Der Prompt sagt klar, was Fusion **nicht** kann (asymmetrisch, rund, variable Steigung). |
| FA-3.5 | Es gibt eine Messanleitung für unbekannte Gewinde: Steigung über zehn Gänge, nicht über einen. |

### FA-4 — Prüfung

| ID | Anforderung |
|----|-------------|
| FA-4.1 | Ein Werkzeug prüft XML-Dateien auf Struktur- und Geometriefehler. |
| FA-4.2 | Es prüft **Plausibilitätsgrenzen**: Winkel, Durchmesser, Steigung, Gewindetiefe im Verhältnis zur Steigung, Spiel. |
| FA-4.3 | Es prüft, ob das **Spiel zur Klassenbeschriftung passt**. Genau dieser Check hätte den Toleranzfehler in v0.9.0 sofort gefunden. |
| FA-4.4 | Fehlermeldungen sagen, **was zu tun ist**, nicht nur was falsch ist. |
| FA-4.5 | Die Prüfung läuft automatisch bei jeder Änderung (CI). |
| FA-4.6 | Sie erkennt `.txt`-Dateien im Gewindeordner — der Fehler, der 33 Größen unsichtbar gemacht hat. |

### FA-5 — Update-Festigkeit

| ID | Anforderung |
|----|-------------|
| FA-5.1 | Es gibt einen dokumentierten Weg, Gewinde nach einem Fusion-Update wiederherzustellen. |
| FA-5.2 | Dieser Weg ist **nicht aufdringlich**: kein Autostart, kein Hintergrunddienst, kein Dateiwächter. |
| FA-5.3 | Die Bibliothek liegt an einem Ort, der Fusion-Updates überlebt. |
| FA-5.4 | Es entsteht **kein Konflikt** mit ThreadKeeper, wenn beide installiert sind → [ADR-0003](adr/0003-threadkeeper-statt-eigenem-keeper.md). |

### FA-6 — Import geprüfter Fremd-XML *(geplant, v2)*

| ID | Anforderung |
|----|-------------|
| FA-6.1 | Der Nutzer kann XML-Text (z. B. aus einer KI-Antwort) einfügen, ohne eine Datei anzulegen. |
| FA-6.2 | Vor dem Speichern wird **hart validiert**. Bei Fehlern wird nicht geschrieben. |
| FA-6.3 | Vor dem Speichern wird eine Zusammenfassung gezeigt: Winkel, Steigung, errechnete Tiefe, Spiel je Klasse. |
| FA-6.4 | Die Fehlermeldung ist so formuliert, dass der Nutzer sie der KI zurückgeben kann. |

## 4. Negativ-Abgrenzung — was ausdrücklich NICHT gebaut wird

> Diese Liste ist so wichtig wie die Anforderungen. Sie verhindert, dass das Projekt
> ausufert, und sie ist die Antwort auf jeden gut gemeinten KI-Vorschlag.

| ID | Wird nicht gebaut | Warum |
|----|-------------------|-------|
| NA-1 | **Asymmetrische Profile** (Sägezahn, Buttress) | Fusion kennt genau einen `<Angle>` für beide Flanken. Technisch unmöglich, nicht nur unbequem. |
| NA-2 | **Echte Rundprofile** | Gleicher Grund. E27 ist und bleibt eine V-Näherung, und das steht auch so da. |
| NA-3 | **Kompilierte Programme** | Verfassung § 3. SmartScreen und AV-Fehlalarme zerstören das Vertrauensversprechen. |
| NA-4 | **Automatisches Umschreiben von Gewindedateien** | Verfassung § 7. Eine kaputte XML nimmt die ganze Gewindeliste mit. |
| NA-5 | **Hintergrunddienst, Autostart, Dateiwächter** | Nichts läuft, wenn Fusion nicht läuft. Ein CAD-Hilfsprojekt hat im Systemstart nichts verloren. |
| NA-6 | **Ein zweiter ThreadKeeper** | Zwei Add-ins, die in denselben Ordner synchronisieren, erzeugen doppelte `<Name>` — und die können die Gewindeliste abschießen. |
| NA-7 | **Generische ISO-Metric-Bibliothek** | Verfassung § 9. Zwei etablierte Repos decken das ab. |
| NA-8 | **Blanko-Generator mit freier Zahleneingabe** | Wer Major, Pitch, PitchDia und Tiefe exakt kennt, braucht kein Werkzeug. Wer sie nicht kennt, kommt damit nicht weiter. Der Bedarf ist Diagnose, nicht Erzeugung. |
| NA-9 | **Telemetrie, Netzwerkzugriff ohne Nutzeraktion** | Ein Gewindewerkzeug hat nichts zu senden. |
| NA-10 | **Gewinde ohne Quelle im Hauptbestand** | Verfassung § 1 und § 6. Unsicheres kommt nach `experimental/`. |
| NA-11 | **Technische Sperren aus Sicherheitsgründen** (z. B. `<ExternalOnly>` beim E27) | Verfassung § 2: warnen statt bevormunden. Wer eine Deko-Fassung drucken will, soll das können. |
| NA-12 | **Mehrgängige und Linksgewinde in der XML** | Stellt Fusion im Dialog ein. Gehört nicht in die Definition. |

## 5. Qualitätsanforderungen

| ID | Anforderung | Messbar an |
|----|-------------|-----------|
| QA-1 | Jede ausgelieferte Zahl hat eine Quelle | Quellenangabe je Gewinde in `threads/README.md` |
| QA-2 | Der Validator läuft grün | CI bei jedem Push |
| QA-3 | Beschriftungen halten, was sie sagen | FA-4.3 prüft das maschinell |
| QA-4 | Doku zweisprachig | `README.md` und `README.de.md` inhaltsgleich |
| QA-5 | Änderungen an Maßen sind nachvollziehbar | CHANGELOG nennt alten und neuen Wert |
| QA-6 | Keine Datei im Gewindeordner, die Fusion nicht liest | FA-4.6 |

## 6. Aufnahmekriterien für neue Gewinde

Ein Gewinde kommt in `threads/`, wenn **alle** Punkte erfüllt sind:

- [ ] Es gibt ein **reales Gegenstück**, das Privatleute besitzen — oder eine belegte,
      häufige FDM-Nachfrage
- [ ] Maße stammen aus Norm, Datenblatt oder Messung (§ 1)
- [ ] Der Flankenwinkel ist einer der fünf aus Fusions Standarddateien (29°, 30°, 45°,
      55°, 60°) — oder ein anderer **mit Begründung**. Fusions Generator akzeptiert auch
      70°, 80° und 90°, wie `dans98/Fusion-360-FDM-threads` zeigt.
- [ ] Es ist kein weiteres generisches Metric-Gewinde (§ 9)
- [ ] Der Hauptzweck ist nicht druck-, strom- oder lastführend (§ 2)
- [ ] Validator grün

Sonst → `experimental/` mit dokumentierter offener Frage.

### Aufnahmeliste (Stand 25.07.2026)

Aus dem [Review vom Juli 2026](03-review-2026-07.md) übernommen:

| Priorität | Gewinde | Winkel | Status |
|:-:|---------|:------:|--------|
| 1 | G ¼", G ⅜", G ½" | 55° | Norm vorhanden (ISO 228), Muster = bestehendes G ¾" |
| 2 | M42 × 1 (T2), M48 × 0,75 | 60° | Norm vorhanden, Astro/Foto stark nachgefragt |
| 3 | PCO 1810 | 60° | Steigung 3,18 mm belegt, Durchmesser unsicher → messen |
| 4 | E14 | 60° | Ergänzung zu E27 |
| 5 | PG7 – PG16 (Kabelverschraubung) | 80° | Winkel ist machbar (dans98 nutzt 70/80/90°). Es fehlen belegte Maße. |
| — | 28-400 / 38-400 / 45-400 | 60° | Herstellerabhängig, keine öffentliche Norm → `experimental/` |
| — | Weitere Filtergewinde (M52–M82) | 60° | Nach Bedarf, auf Zuruf |

## 7. Erfolgskriterien

Das Projekt ist erfolgreich, wenn jemand ohne Vorwissen…

1. …in unter zehn Minuten von „ich brauche einen Deckel" zum installierten Gewinde kommt,
2. …beim ersten Testdruck eine Passung erwischt, die funktioniert oder nur eine Stufe daneben
   liegt,
3. …nach einem Fusion-Update weiß, was zu tun ist, statt zu glauben, etwas sei kaputt,
4. …und für ein *nicht* enthaltenes Gewinde einen gangbaren Weg findet.
