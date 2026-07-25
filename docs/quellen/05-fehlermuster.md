# 05 — Fehlermuster

Was in allen Projekten dieses Umfelds immer wieder schiefgeht — und was wir jeweils daraus
gebaut haben. Das ist der wertvollste Teil der Quellensammlung: Fehler, die andere schon
gemacht haben, muss man nicht wiederholen.

← zurück zur [Quellenübersicht](README.md)

---

## 1. Eine kaputte XML nimmt die ganze Gewindeliste mit

**Symptom:** Nach dem Einspielen einer Datei zeigt Fusion **gar keine** Gewinde mehr — auch
keine Standardgewinde.

**Belegt in:**
[ThreadKeeper #11](https://github.com/thomasa88/ThreadKeeper/issues/11) ✅ („I installed
ThreadKeeper and now I haven't any kind of thread"),
[ThreadKeeper #1](https://github.com/thomasa88/ThreadKeeper/issues/1) ✅,
[BalzGuenat #12](https://github.com/BalzGuenat/CustomThreads/issues/12) ✅ (Absturz beim
Öffnen des Werkzeugs).

**Ursachen:** Syntaxfehler im XML, doppelter `<Name>`, leere Datei nach fehlgeschlagenem
Kopieren.

**Was wir daraus gebaut haben:**

- [`validate_threads.py`](../../tools/validate_threads.py) prüft Wohlgeformtheit, eindeutige
  `<Name>`, `SortOrder` und Geometrie — **bevor** eine Datei irgendwo landet
- [ADR-0004](../spec/adr/0004-kein-autofix.md): kein automatisches Umschreiben. Das
  Schadenspotenzial steht in keinem Verhältnis zum Nutzen.
- [ADR-0009](../spec/adr/0009-dateioperationen.md): nach dem Kopieren Prüfsumme vergleichen,
  bei Abweichung die Zieldatei löschen
- Die Issue-Vorlage nennt dieses Symptom als **erste** Verdachtsdiagnose

---

## 2. Die Beschriftung der Toleranzklasse lügt

**Symptom:** Die Klasse heißt „0.15 mm", das tatsächliche Spiel ist ein Vielfaches davon.

**Belegt in:** [BalzGuenat #16](https://github.com/BalzGuenat/CustomThreads/issues/16) ✅
(seit März 2026 offen) — **und in diesem Projekt selbst**, bis v1.0.0: `0.15mm (Tight)` gab
real 0,45 mm.

Zwei unabhängige Projekte, derselbe Fehler, jahrelang unbemerkt. Das ist kein Zufall,
sondern eine strukturelle Schwäche: Niemand rechnet Beschriftungen nach.

**Was wir daraus gebaut haben:**

- Der Validator liest die Zahl aus dem `<Class>`-Text und vergleicht sie mit der
  tatsächlichen Differenz `internal − external`. Als **Fehler**, nicht als Warnung.
- [ADR-0002](../spec/adr/0002-sechs-toleranzklassen.md): Klassennamen sagen den Anwendungsfall,
  nicht nur die Zahl
- `0.00 mm (Exact)` gestrichen — ausgerechnet die „genaueste" Klasse ist die, die nicht
  funktioniert

---

## 3. Fest verdrahtete Pfade brechen

**Symptom:** Nach einem Fusion-Update erscheint beim Start ein Python-Traceback.

**Belegt in:** [ThreadKeeper #7](https://github.com/thomasa88/ThreadKeeper/issues/7) ✅ —
Autodesk benennt das macOS-Bundle mal `Autodesk Fusion.app`, mal
`Autodesk Fusion 360.app`. Der erste Fix hardcodierte den neuen Namen und brach dadurch bei
allen, die noch den alten hatten:

> „I'm on v1.2.2 of this plugin and I'm having this same issue because my app _does_ have
> the `360` suffix."

**Es gibt keinen korrekten festen Namen.** Beide existieren gleichzeitig im Feld.

**Was wir daraus gebaut haben:** [ADR-0009](../spec/adr/0009-dateioperationen.md) — Pfade
werden **gesucht statt geraten**, per Glob über `production` *und* `pre-production`, ohne
`.app`-Namen im Quelltext.

---

## 4. Kopieren über die Shell erzeugt stille Fehler

**Symptom:** Die Datei ist da, aber leer. Keine Fehlermeldung.

**Belegt in:** [ThreadKeeper #9](https://github.com/thomasa88/ThreadKeeper/issues/9) ✅ —
`subprocess.check_call(f'copy "{src}" "{dst}"', shell=True)` erzeugte unter bestimmten
Bedingungen ein leeres Dokument. Der Vorschlag, auf `shutil.copy` umzustellen, ist seit über
einem Jahr offen.

Eine leere XML ist der schlimmstmögliche Ausgang: Sie löst Fehlermuster 1 aus, ohne dass
irgendwo ein Fehler gemeldet wurde.

**Was wir daraus gebaut haben:** [ADR-0009](../spec/adr/0009-dateioperationen.md) — nur
`shutil.copy2`, nie `subprocess`, und nach jedem Kopieren Größe und Prüfsumme vergleichen.

---

## 5. „Thread size is bigger than the body"

**Symptom:** Fusion verweigert das Gewinde mit dieser Meldung.

**Belegt in:** [BalzGuenat #9](https://github.com/BalzGuenat/CustomThreads/issues/9) ✅

**Ursache:** Kein Fehler der Datei. Grobe Steigung bedeutet tiefes Gewinde bedeutet, dass der
Kerndurchmesser die Wandstärke sprengt. Betrifft uns unmittelbar, weil unsere Trapezdatei bis
TR150×16 reicht — bei 16 mm Steigung sind das 8 mm Gewindetiefe je Seite.

**Was daraus folgt:** gehört in ein Troubleshooting-Kapitel. **Noch offen.**

---

## 6. macOS ist überall die schwächere Seite

**Belegt in:** ThreadKeeper #7, #8, #14 ✅ — Installation und Pfade. Dazu unser eigener
`find-threaddata.bat`, den es für macOS schlicht nicht gibt.

**Was daraus folgt:** `find-threaddata.sh` steht auf der Liste
([Ü-4](../spec/03-review-2026-07.md)). **Noch offen.**

---

## 7. „Außerhalb des Anwendungsfalls" ist kein Ersatz für „korrekt"

**Belegt in:** [BalzGuenat #2](https://github.com/BalzGuenat/CustomThreads/issues/2) ✅ — Ein
Nutzer meldete `PitchDia < MinorDia`, also geometrisch unmögliche Werte. Der Maintainer wies
das zunächst zurück, weil so feine Steigungen ohnehin nicht zum Zweck des Projekts passten.

Der Fehler war trotzdem real und wurde später per Pull Request behoben. Der Melder druckte
die feinen Gewinde nämlich sehr wohl — auf einem Ender 3, mit funktionierendem Ergebnis.

**Was daraus folgt:** Wenn jemand einen Rechenfehler meldet, ist die Frage „ist die Rechnung
richtig?" — nicht „gehört der Anwendungsfall zu uns?". Der Zuschnitt des Projekts steht in
der [Spezifikation](../spec/01-spezifikation.md); er ist ein Argument über *Aufnahme*, nicht
über *Korrektheit*.

---

## Übersicht: Muster → Gegenmaßnahme

| # | Fehlermuster | Umgesetzt in | Status |
|:-:|---|---|:-:|
| 1 | Kaputte XML killt Gewindeliste | Validator, ADR-0004, ADR-0009 | ✅ |
| 2 | Beschriftung lügt | Validator-Prüfung `<Class>` ↔ Spiel | ✅ |
| 3 | Fest verdrahtete Pfade | ADR-0009 | 📝 geplant |
| 4 | Shell-Kopieren | ADR-0009 | 📝 geplant |
| 5 | Wandstärke zu dünn | Troubleshooting | ❌ offen |
| 6 | macOS schwächer | `find-threaddata.sh` | ❌ offen |
| 7 | Scope-Argument statt Korrektheit | [CONTRIBUTING](../../CONTRIBUTING.md) | ❌ offen |
