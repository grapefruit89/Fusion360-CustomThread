# ADR-0003 — Das Add-in wird Importer, nicht zweiter Keeper

**Status:** 📌 vorgeschlagen · **Datum:** 2026-07-25

## Kontext

Nach jedem Fusion-Update sind die Gewinde weg, weil Fusion sich in einen neuen Ordner mit
neuem Hash installiert und `ThreadData` nicht mitnimmt. Das ist der größte verbliebene
Schmerzpunkt des Projekts.

[ThreadKeeper](https://github.com/thomasa88/ThreadKeeper) von Thomas Axelsson löst das seit
2020: MIT-Lizenz, 90 Sterne, Windows und macOS, im Autodesk App Store. Es bringt **keine
eigenen Gewinde** mit — es stellt nur wieder her, was in seinem `Threads`-Ordner liegt.

Zur Diskussion standen drei Wege:

1. **Eigenes Add-in bauen und ThreadKeeper zusätzlich empfehlen**
2. **Die Wiederherstellungslogik aus ThreadKeeper übernehmen** (MIT erlaubt das)
3. **ThreadKeeper erweitern** (Pull Request nach oben)

## Analyse der drei Wege

**Weg 1 hat ein Problem, das auf den ersten Blick nicht sichtbar ist.** Zwei Add-ins, die
beide in denselben `ThreadData`-Ordner synchronisieren, spielen unter Umständen dieselbe
Datei doppelt ein — unter verschiedenen Dateinamen, aber mit identischem `<Name>`. Eine
`<Name>`-Kollision kann Fusions **komplette** Gewindeliste unbrauchbar machen. „Beides
installieren" wäre also nicht doppelt sicher, sondern gefährlicher als eines.

**Weg 2 ist lizenzrechtlich sauber**, aber langfristig der schlechteste. Man übernähme
ausgerechnet den kniffligsten Teil — die Pfadsuche über Fusion-Versionen und zwei
Betriebssysteme hinweg — und pflegte ihn ab dann als Kopie weiter, ohne dass Korrekturen von
oben nachfließen. ThreadKeepers Changelog zeigt genau solche Nachbesserungen (`Fix for new
Fusion deploy folder on Mac`). Diese Arbeit noch einmal zu machen, wäre reine Dopplung.

**Weg 3 passt nicht für alles.** Eine Einfüge-Box für KI-generierte XML ist Scope-Creep für
ein Add-in, das bewusst generisch und inhaltsfrei ist. Außerdem: letzter Commit Januar 2025,
sechs offene Issues — ein PR könnte lange liegen bleiben, und das Projekt wäre blockiert.

Für **einen Teil** ist Weg 3 aber ausgezeichnet: ThreadKeeper hat offene Issues, die genau
dadurch entstehen, dass eine fehlerhafte XML eingespielt wird
([#1](https://github.com/thomasa88/ThreadKeeper/issues/1),
[#11](https://github.com/thomasa88/ThreadKeeper/issues/11)). Eine **Validierung vor dem
Synchronisieren** wäre dort thematisch genau richtig.

## Entscheidung

Die Wertschöpfung wird aufgeteilt:

| Aufgabe | Wer | Warum |
|---------|-----|-------|
| **Wiederherstellen nach Update** | ThreadKeeper | Gelöstes Problem, fremd gepflegt, plattformübergreifend. Wir bauen es nicht nach. |
| **Kuratierte Bibliothek, Import, Validierung, Vorschau** | unser Add-in | Das kann ThreadKeeper nicht und soll es auch nicht. Hier liegt unser Beitrag. |

Konkret:

- Unser Add-in ist ein **Editor und Importeur**, kein Keeper. Es besitzt einen
  Bibliotheksordner, prüft, was hineinkommt, und zeigt eine Vorschau.
- **Erkennt es ThreadKeeper**, überlässt es diesem das Wiederherstellen und weist einmalig
  darauf hin, ThreadKeepers Ordner auf unsere Bibliothek zu zeigen — ThreadKeeper hat seit
  v1.2.0 „Change ThreadKeeper directory…". Dann synchronisiert genau **ein** Add-in.
- **Ohne ThreadKeeper** kopiert unser Add-in selbst, mit Backup. Diese Logik darf schlicht
  bleiben, weil sie nur der Fallback ist.
- Die Validierung wird zusätzlich als **Pull Request an ThreadKeeper** angeboten. Nimmt
  Thomas ihn an, profitieren alle und wir haben nichts verloren.

## Konsequenzen

**Gut:**
- Kein Konkurrenzprodukt zu einem funktionierenden Projekt
- Kein Doppelsync, keine `<Name>`-Kollisionen
- Die aufwendige Pfadlogik bleibt fremd gepflegt
- Unser Alleinstellungsmerkmal — geprüfte Daten und geprüfter Import — bleibt bei uns

**Schlecht:**
- Abhängigkeit von einem Projekt mit geringer Aktivität. Fällt ThreadKeeper dauerhaft aus,
  muss der Fallback-Pfad wachsen. Das ist beherrschbar, weil er ohnehin existiert.
- Die Erkennung von ThreadKeeper ist eine Kopplung an dessen Ordnerstruktur und kann brechen.
  Fehlerfall: nicht erkannt → wir kopieren selbst → funktioniert trotzdem, nur doppelt. Das
  ist der harmlose Ausgang, solange die Bibliothek dieselbe ist.

**Umgangsform:** Übernommener Code behält seinen Copyright-Header und wird in `NOTICE`
genannt. ThreadKeeper wird in der README weiter prominent empfohlen — auch von Leuten, die
unser Add-in nie installieren. Und es wird ein Issue drüben aufgemacht mit dem Angebot,
diese Gewindesammlung zu verlinken; zwei andere Sammlungen sind dort bereits genannt.
