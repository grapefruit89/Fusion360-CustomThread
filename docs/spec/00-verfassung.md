# Verfassung

> Die obersten Regeln des Projekts. Alles andere — Spezifikation, technischer Plan, jeder
> ADR, jeder Pull Request und jeder KI-generierte Vorschlag — muss sich hieran messen lassen.
> Wenn etwas hiermit kollidiert, verliert das andere.

**Version 1.0 · Stand 25.07.2026**

---

## Warum es dieses Dokument gibt

Dieses Projekt wird zu großen Teilen mit KI-Unterstützung entwickelt. Das ist schnell und
produziert plausibel aussehende Ergebnisse — auch dort, wo niemand nachgemessen hat. Genau
dieser Fehler ist bereits passiert: Die Toleranzklassen hießen „0.15mm", gaben real 0,45 mm,
und drei Versionen lang ist es niemandem aufgefallen. Die Steigung von PCO 1881 war schlicht
falsch.

Die Verfassung existiert, damit so etwas nicht durch Bequemlichkeit wieder hereinrutscht.
Sie ist **absichtlich einschränkend**.

---

> Belege und Fehlermuster, auf die sich diese Verfassung stützt: [QUELLEN.md](../QUELLEN.md)

## § 1 — Messwerte schlagen Plausibilität

**Keine Zahl kommt in eine ausgelieferte Gewindedatei, die nicht aus einer Norm, einem
Datenblatt oder einer Messung am realen Teil stammt.**

Eine Zahl, die „richtig aussieht", ist keine Quelle. Eine KI-Antwort ist keine Quelle. Ein
Forenbeitrag ohne Zeichnung ist keine Quelle.

Wo die Datenlage unklar ist, gilt § 6 (`experimental/`) — nicht Raten.

*Warum:* Eine falsche Zahl kostet den Nutzer Stunden Druckzeit und Material. Er merkt es
erst nach dem Druck, und er kann sie nicht überprüfen, weil er uns ja gerade deshalb fragt.

## § 2 — Sicherheit ist nicht verhandelbar

Diese Gewinde sind für **Schutzkappen, Deko und unbelastete Mechanik**. Es kommt nichts ins
Projekt, das seinen Hauptzweck in einer dieser Anwendungen hätte:

- **Druckführende Teile** — CO₂, Sodastream, Druckluft, Sprudler, unter Druck stehende PET
- **Stromführende Teile** — Lampenfassungen im Betrieb
- **Tragende Verschraubungen** — Klettern, Fahrzeug, Kindersitz, Last über Kopf
- **Lebensmittelkontakt** als beworbener Zweck

Die zugehörigen *Gewindeprofile* dürfen existieren — jemand will eine Staubschutzkappe, eine
Deko-Fassung oder eine Fake-Glühbirne drucken, und das ist legitim. Was nicht passiert:
Bewerbung für den gefährlichen Zweck, Weglassen der Warnung, oder Bevormundung durch
technische Sperren.

**Warnen statt sperren.** Eine Warnung informiert, eine ausgegraute Auswahl hilft niemandem
und erfindet Grenzen, wo keine hingehören.

## § 3 — Nichts, was der Nutzer nicht lesen kann

Alles, was ausgeliefert wird, ist **Klartext**: XML, Python, Batch, Markdown.

**Keine kompilierten Binaries.** Kein `.exe`, kein PyInstaller, kein obfuskierter Code.

*Warum:* Das Projekt bittet die Nutzer ausdrücklich, die Dateien bei VirusTotal zu prüfen.
Eine unsignierte `.exe` löst SmartScreen aus und schlägt bei Heuristik-Scannern an — das
zerstört genau das Vertrauen, um das hier gebeten wird. Wer eine Datei nicht im Editor öffnen
kann, muss uns glauben. Das soll niemand müssen.

## § 4 — Der Nutzer kann kein CAD und will es nicht lernen

Zielgruppe ist jemand, der einen Deckel drucken will. Nicht jemand, der Gewindegeometrie
studieren will.

- **Doppelklick oder Menüeintrag.** Keine Kommandozeile für Endnutzer.
- **Keine AppData-Pfade zum Selbstsuchen**, wenn ein Werkzeug es übernehmen kann.
- **Beschriftungen sagen, wie es sich anfühlt**, nicht nur, welche Zahl dahintersteckt.
  `0.15 mm - Standard (Handkraft)`, nicht `0.15`.
- **Jede Fehlermeldung sagt, was zu tun ist.** „Ungültig" ist keine Fehlermeldung.

Werkzeuge für Mitwirkende (Validator, CI, Generatoren) dürfen Kommandozeile sein. Werkzeuge
für Nutzer nicht.

## § 5 — Ehrliche Grenzen

Was das Projekt nicht kann, steht in der Dokumentation — an prominenter Stelle, nicht im
Kleingedruckten.

- Fusion kennt nur **symmetrische** Profile. Sägezahn geht nicht. Das wird gesagt, nicht
  umschifft.
- Nach einem Fusion-Update sind die Gewinde weg. Das wird erklärt, nicht kaschiert.
- Gewinde erscheinen erst nach **Neustart**. Auch mit Add-in. Das gilt für ThreadKeeper
  genauso und ist Fusions Architektur, nicht unsere Schwäche.
- FDM hält kein H7. Wer mit ISO-286-Toleranzen argumentiert, vergleicht die falschen Dinge.

*Warum:* Ein Projekt, das seine Grenzen verschweigt, erzeugt Issues von enttäuschten Leuten.
Ein Projekt, das sie nennt, erzeugt Vertrauen.

## § 6 — Zwei Qualitätsstufen, klar getrennt

| Ordner | Bedeutung | Im Release-ZIP |
|--------|-----------|:-:|
| `threads/` | Maße aus Norm, Datenblatt oder Messung. Validator läuft grün. | ✅ |
| `experimental/` | Maße unsicher oder herstellerabhängig. Näherung. | ❌ |

`experimental/` trägt im `<CustomName>` ein `(exp.)` und eine eigene README, die sagt, was
unsicher ist und welche Messung fehlt. Nichts wandert von `experimental/` nach `threads/`
ohne mindestens **zwei unabhängige Messungen** oder eine Normquelle.

*Warum:* Ohne diese Trennung landen Schätzwerte irgendwann unbemerkt im Hauptbestand — und
dann gilt § 1 nur noch auf dem Papier.

## § 7 — Keine automatischen Änderungen an Nutzerdaten

Werkzeuge dieses Projekts **schreiben Gewindedateien nicht selbsttätig um**.

Sie dürfen prüfen, erklären, vorschlagen, Unterschiede anzeigen. Sie dürfen Dateien anlegen
und kopieren, wenn der Nutzer das ausgelöst hat. Sie dürfen keine bestehende Datei still
korrigieren.

Wo geschrieben wird, wird vorher ein Backup angelegt.

*Warum:* Eine kaputte XML im ThreadData-Ordner kann Fusions **komplette** Gewindeliste
unbrauchbar machen, Standardgewinde eingeschlossen. Ein Werkzeug, das unbeaufsichtigt in
diesen Ordner schreibt, kann mehr kaputtmachen, als das ganze Projekt wert ist.

## § 8 — Lizenzhygiene

- Eigener Code: **MIT**. Gewindedaten und Doku: **CC BY 4.0**.
- **Kein GPL-Code wird übernommen.** Er ist mit MIT unvereinbar. Verlinken ja, kopieren nein.
- **Kein Code ohne Lizenz wird übernommen.** Ohne Lizenz gilt volles Urheberrecht.
- Übernommener MIT/BSD-Code behält seinen Copyright-Header und wird in `NOTICE` genannt.
- Fremde Projekte werden verlinkt und empfohlen, wenn sie das Problem besser lösen als wir.

## § 9 — Abgrenzung: was dieses Projekt nicht ist

- **Keine weitere generische ISO-Metric-Bibliothek.** Das decken
  [BalzGuenat/CustomThreads](https://github.com/BalzGuenat/CustomThreads) (395 ★) und
  [dans98/Fusion-360-FDM-threads](https://github.com/dans98/Fusion-360-FDM-threads) (282 ★)
  ab. Wir verlinken sie, statt sie nachzubauen.
- **Kein Ersatz für ThreadKeeper.** Siehe [ADR-0003](adr/0003-threadkeeper-statt-eigenem-keeper.md).
- **Kein CAD-Tutorial.** Wir erklären, was für die Gewinde nötig ist, nicht Fusion insgesamt.
- **Kein Blanko-Generator**, bei dem der Nutzer alle Maße selbst kennen muss. Wer sie kennt,
  braucht uns nicht.

## § 10 — Änderungen an dieser Verfassung

Änderungen brauchen einen ADR mit Begründung und eine Version hier oben. Ein Paragraph, der
still verschwindet, ist ein Fehler im Prozess.

---

## Prüfliste vor jedem Merge

- [ ] Jede neue Zahl hat eine Quelle (§ 1)
- [ ] Sicherheitshinweise vorhanden, wo einschlägig (§ 2)
- [ ] Nichts Kompiliertes hinzugekommen (§ 3)
- [ ] Endnutzer-Pfad ist Doppelklick oder Menü (§ 4)
- [ ] Neue Grenzen dokumentiert (§ 5)
- [ ] Unsicheres liegt in `experimental/` (§ 6)
- [ ] Kein Werkzeug schreibt ungefragt (§ 7)
- [ ] Lizenzen der Quellen geprüft (§ 8)
- [ ] `python tools/validate_threads.py threads` läuft grün
