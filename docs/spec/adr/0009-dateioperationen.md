# ADR-0009 — Regeln für Dateioperationen, gelernt aus ThreadKeepers Fehlern

**Status:** ✅ angenommen · **Datum:** 2026-07-25

## Kontext

[ADR-0003](0003-threadkeeper-statt-eigenem-keeper.md) legt fest, dass wir das
Wiederherstellen nach Fusion-Updates ThreadKeeper überlassen und nur einen einfachen Fallback
bauen. Beim Durchsehen der Issues und App-Store-Bewertungen von ThreadKeeper zeigt sich
allerdings, dass genau dieser „einfache Teil" in der Praxis dreimal auf dieselbe Art
gebrochen ist.

Das sind keine Nachlässigkeiten von Thomas Axelsson — es sind die Fallen, in die jeder tappt,
der Dateien in Fusions Installationsordner kopiert. Deshalb festgehalten, **bevor** wir
denselben Code schreiben.

## Die drei Befunde

### 1. Ein fest verdrahteter Ordnername bricht

`ThreadKeeper.py` enthielt auf macOS den Pfad `Autodesk Fusion 360.app`. Autodesk hat den
Bundle-Namen bei manchen Installationen zu `Autodesk Fusion.app` geändert — das Add-in warf
beim Start einen Traceback-Dialog
([Issue #7](https://github.com/thomasa88/ThreadKeeper/issues/7), App-Store-Bewertung vom
02.02.2025).

Der Fix hardcodierte den *neuen* Namen — woraufhin es bei allen brach, die noch den alten
hatten. Erst danach wurden **beide Pfade** probiert.

> „I'm on v1.2.2 of this plugin and I'm having this same issue because my app _does_ have
> the `360` suffix."

Es gibt also **keinen** korrekten festen Namen. Beide existieren gleichzeitig im Feld.

### 2. Kopieren über die Shell erzeugt stillschweigend leere Dateien

ThreadKeeper kopiert mit `subprocess.check_call(f'cp -- "{src}" "{dst}"', shell=True)`
bzw. `copy` unter Windows. In
[Issue #9](https://github.com/thomasa88/ThreadKeeper/issues/9) berichtet ein Nutzer:

> „apparently in this configuration it only copied a blank document"

Eine **leere Datei** im ThreadData-Ordner ist der schlimmstmögliche Ausgang: kein Fehler,
kein Hinweis — aber ein kaputtes XML, das Fusions komplette Gewindeliste mitreißen kann.
Genau das beschreibt
[Issue #11](https://github.com/thomasa88/ThreadKeeper/issues/11) („I installed ThreadKeeper
and now I haven't any kind of thread").

Der Vorschlag im Issue lautet, auf `shutil.copy` umzustellen. Er ist seit über einem Jahr
offen.

### 3. Ein Fehler beim Start reißt alles mit

Der Traceback aus Befund 1 erscheint als Fehlerdialog beim Fusion-Start. Eine einzelne nicht
kopierbare Datei bricht damit den gesamten Vorgang ab — die anderen Gewinde werden nicht mehr
eingespielt, und der Nutzer bekommt einen Python-Stacktrace zu sehen, mit dem er nichts
anfangen kann.

## Entscheidung

Für jeden Code dieses Projekts, der Gewindedateien kopiert — Add-in wie Skript:

| Regel | Warum |
|-------|-------|
| **Pfade werden gesucht, nicht geraten.** Unter jedem Ordner in `webdeploy/production` **und** `webdeploy/pre-production` wird nach dem Muster `*/Fusion/Server/Fusion/Configuration/ThreadData` gesucht. Kein `.app`-Name, kein Versions-Hash im Quelltext. | Befund 1. Der Name ändert sich und ist nicht einmal einheitlich. |
| **Kopiert wird mit `shutil.copy2`.** Niemals `subprocess`, niemals `shell=True`. | Befund 2. Shell-Aufrufe verschlucken Fehler, brechen an Leerzeichen und Sonderzeichen und liefern kein verwertbares Exception-Objekt. |
| **Nach dem Kopieren wird verifiziert**: Zielgröße > 0, Größe gleich Quelle, Prüfsumme gleich. Schlägt das fehl, wird die Zieldatei **gelöscht**. | Befund 2. Eine halb geschriebene XML ist gefährlicher als eine fehlende. |
| **Vor dem Überschreiben wird gesichert** nach `ThreadData/_backup_JJMMTT/`. | Rückweg, wenn doch etwas schiefgeht. |
| **Jede Datei einzeln, Fehler werden gesammelt.** Eine kaputte Datei überspringen, die übrigen einspielen, am Ende eine Liste zeigen. Niemals eine Exception nach oben durchreichen. | Befund 3. Ein Stacktrace beim Start hilft niemandem. |
| **Meldungen im Klartext**, mit Dateiname und was zu tun ist. Kein Traceback im Dialog. | Verfassung § 4. |
| **Vor dem Kopieren validieren.** Die Prüfregeln aus `validate_threads.py` laufen über jede Datei, bevor sie in den ThreadData-Ordner geht. | Verhindert Befund 2 an der Wurzel — auch bei fremden Dateien. |

## Konsequenzen

**Gut:**
- Unser Fallback wird robuster als der Stand der Technik, ohne mehr Code zu sein.
  `shutil.copy2` plus eine Prüfsumme sind kürzer als der `subprocess`-Aufruf.
- Die Validierung vor dem Kopieren ist der Punkt, an dem sich unser Projekt tatsächlich von
  ThreadKeeper unterscheidet — und der Grund, den PR aus ADR-0003 anzubieten.

**Schlecht:**
- Die Pfadsuche per Glob ist langsamer als ein fester Pfad. Bei einer Handvoll
  Versionsordner ist das messbar irrelevant.
- Mehrere gefundene ThreadData-Ordner müssen behandelt werden. Entscheidung: **alle**
  patchen, nicht nur den neuesten — dann überlebt die Installation auch ein Rollback.

## Auswirkung auf ADR-0003

Die Empfehlung „für das Wiederherstellen auf ThreadKeeper setzen" bleibt bestehen, wird aber
mit einem Hinweis versehen: ThreadKeeper hat aktuell **sechs offene Issues**, darunter
Installationsprobleme unter macOS (#14), Abstürze (#10, #13) und den Kopierbefehl (#9).
Es funktioniert für die Mehrheit, ist aber kein Fels.

**Praktisch wichtig für unsere Nutzer:** Die Fassung im Autodesk App Store hinkt der auf
GitHub um Wochen hinterher — Thomas selbst schreibt „I expect it to be approved in around
2 weeks". Wer ein Problem hat, sollte zuerst die GitHub-Release ausprobieren, nicht die aus
dem App Store. Das gehört in unsere README.
