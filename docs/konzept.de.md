# Konzept: `fusion-fdm-threads`

Refactoring des Projekts *[3D-Print] Custom Threads für Fusion 360* zu einem GitHub-Repository
mit Doppelklick-Installer und optionalem Update-Schutz.

Stand: 24.07.2026 · Status: **Entwurf zur Abstimmung** (noch nichts umgesetzt)

---

## 1. Ausgangslage — was ich vorgefunden habe

| Datei | Befund |
|---|---|
| `Info BITTE lesen.txt` | Inhaltlich gut, aber Inventarliste stimmt nicht mit den Dateien überein |
| `Thread Data Ordner finder.bat` | Funktioniert, aber fragil (siehe §3) |
| `neu 3.bat` | **Byte-identisch** mit dem Finder bis auf einen Kommentar → Leiche |
| 8 × `*.xml` | Sauber aufgebaut, konsistente Struktur |
| `[3D-Print] Trapezgewinde FDM only.txt` | **Bug: das ist eine XML-Datei mit `.txt`-Endung** |
| `[3D-Print] TR8x2 .xml` | Leerzeichen vor `.xml` im Dateinamen |
| `VirusTotal - Home.url` | Verknüpfung, gehört in die README |
| `CO2 Gewindeschutzkappe.f3d` | Beispieldatei, gut — braucht ein Vorschaubild |

### Gefundene inhaltliche Fehler (wichtig)

1. **`Trapezgewinde FDM only.txt` wird von Fusion niemals geladen.** Fusion liest im
   `ThreadData`-Ordner ausschließlich `*.xml`. Die Datei enthält 33 Trapezgewinde
   (TR8×2 bis TR150×16). *Nachtrag: Die `.txt`-Endung war Absicht — das Forum akzeptiert
   kein XML.* Für das Repo trotzdem `.xml`, und in der README ein Satz dazu, dass die
   Forum-Version umbenannt werden muss. Sonst stolpert jeder darüber, der sie von dort hat.
2. **`TR8x2` existiert doppelt und widersprüchlich:** einmal mit `<Angle>30</Angle>`
   (ISO-Trapez, korrekt) in `[3D-Print] TR8x2 .xml`, einmal mit `<Angle>45</Angle>` im
   Trapez-Paket. Beide gleichzeitig installiert = zwei fast gleich heißende Einträge im
   Fusion-Dropdown. Muss entschieden werden: das 45°-Paket ist die druckfreundliche
   Variante, das 30°-Einzelfile die normgerechte.
3. **Inkonsistente Toleranzklassen:** nur das Trapez-Paket bietet `0.00mm (Exact)`, alle
   anderen nur `0.15mm (Tight)` und `0.20mm (Safe)`. Vereinheitlichen — aber *nicht* über
   `Exact`, siehe §8.
4. **Doppelte Leerzeichen** in fast allen `<CustomName>` (`[3D-Print]  1/4"`) — sieht im
   Fusion-Dropdown unsauber aus.
5. Die README nennt `[3D-Print] ISO Trapezoidal - Generic.xml` und `ThreadData-Finder.bat`
   — beide Dateinamen gibt es nicht.

### Zwei Funde aus deinem echten ThreadData-Ordner

Ich habe `…\production\441fa886…\ThreadData` durchgesehen — 18 Dateien von Autodesk.
Zwei Dinge fallen im Vergleich zu unseren XMLs auf:

6. **`<SortOrder>` kollidiert.** Autodesk belegt 1–63:
   ANSI Unified = 1, ANSI Metric = 2, ISO Metric = 3, ISO Trapezoidal = 4, Inch Tapping = 5,
   Metric Forming = 6, ISO Pipe = 9 … unsere Dateien benutzen 1–9 und rangeln damit direkt
   mit den Standardgewinden um die Position im Dropdown. **Empfehlung: 200 aufwärts** —
   dann stehen alle `[3D-Print]`-Einträge sauber gruppiert am Ende der Liste.

7. **Das Spiel liegt bei uns auf beiden Seiten.** Beispiel PCO1881: `internal` +0,15 mm
   *und* `external` −0,15 mm ⇒ effektiv **0,30 mm Gesamtspiel**. Für „beide Teile gedruckt"
   ist das genau richtig. Für den weitaus häufigeren Fall „gedruckter Deckel auf echte
   PET-Flasche" ist es doppelt so viel wie beabsichtigt — und das Außengewinde weicht dann
   auch noch vom echten Flaschenhals ab. Zum Vergleich: Autodesks eigenes TR8×1.5 gibt dem
   Außengewinde nur 0,075 mm Untermaß.
   **Empfehlung:** je Gewinde entweder klar dokumentieren („Werte gelten für
   Kunststoff-auf-Kunststoff") oder zwei Varianten anbieten. Der Assistent aus §7 klärt
   genau diese Frage als erstes.

---

## 2. Was ist ThreadKeeper? (deine Frage)

[ThreadKeeper](https://github.com/thomasa88/ThreadKeeper) von Thomas Axelsson ist ein
kostenloses Fusion-Add-in (MIT-Lizenz, ~90 Stars, auch im Autodesk App Store), das **genau
dein Problem** löst — und zwar seit 2020:

- Du legst deine Gewinde-XMLs einmalig in den `Threads`-Ordner von ThreadKeeper.
- Bei **jedem Fusion-Start** prüft das Add-in, ob die Dateien im aktuellen
  `ThreadData`-Ordner fehlen, und kopiert sie zurück.
- Menüpunkt unter *UTILITIES → THREADKEEPER* mit „Force sync" und Ordner-Öffnen.
- Läuft auf Windows und macOS.

**Warum das für dich relevant ist:** ThreadKeeper enthält selbst *keine* Gewinde — es ist
reine Infrastruktur. Deine XMLs sind der Inhalt. Die beiden Projekte konkurrieren nicht,
sie ergänzen sich. In der ThreadKeeper-README werden bereits zwei fremde Gewinde-Sammlungen
verlinkt; da könnte deine als dritte dazu.

**Konsequenz für das Konzept:** Wir bauen den Update-Schutz nicht als Konkurrenz, sondern
als *optionale* Eigenlösung — und dokumentieren ThreadKeeper prominent als gleichwertige
Alternative für Leute, die schon ein Add-in-Setup haben.

---

## 3. Ausführbare Dateien — Python als `.exe`?

### Die kurze Antwort

**Technisch trivial, praktisch eine schlechte Idee** — und für dieses Projekt zum Glück
überflüssig.

`pyinstaller --onefile skript.py` und du hast eine `.exe`. Das ist eine Zeile. Alternativen
sind Nuitka (kompiliert echt, schneller, kleiner) und cx_Freeze. Der Aufwand ist nicht das
Problem, die Nebenwirkungen sind es:

| | |
|---|---|
| **Größe** | 30–80 MB für ein Skript, das 200 Zeilen hat — der komplette Python-Interpreter wandert mit hinein |
| **SmartScreen** | Windows blockt jede unsignierte `.exe` beim ersten Start mit „Unbekannter Herausgeber". Ein Code-Signing-Zertifikat kostet ~200–400 €/Jahr, EV noch mehr |
| **Virenscanner** | PyInstaller-`--onefile` ist berüchtigt für Fehlalarme. Der Entpack-Mechanismus sieht für Heuristiken exakt aus wie ein Malware-Packer. Auf VirusTotal schlagen regelmäßig 5–15 Engines an — bei völlig harmlosem Code |

Der letzte Punkt ist bei *deinem* Projekt der Sargnagel: Du verlinkst in der README selbst
VirusTotal und bittest die Leute, die Dateien zu prüfen. Eine `.exe`, die dort rot leuchtet,
zerstört genau das Vertrauen, das du dir mit diesem Hinweis aufbaust.

### „Geht bei Python auch was Transparentes?"

Nicht wirklich — und das ist kein Python-Problem, sondern ein Widerspruch in sich. Eine
Datei ist entweder ein Binary (Windows kann sie doppelklicken, Mensch kann sie nicht lesen)
oder Quelltext (lesbar, braucht einen Interpreter). Was es in Python gibt:

- **`.pyz` (zipapp)** — Quelltext im ZIP, elegant, aber braucht installiertes Python.
- **`py`-Launcher** — `.py` doppelklickbar, aber nur wenn Python installiert ist.
- **Embeddable Python beilegen** — ~15 MB Ordner mit Interpreter neben dem Skript. Lesbar,
  kein SmartScreen. Aber ein 15-MB-Ordner mit `python.exe` darin sieht für Laien noch
  suspekter aus als eine einzelne `.exe`.

### Die eigentliche Antwort: du brauchst gar kein Packaging

**Fusion bringt seinen eigenen Python-Interpreter mit.** Sobald der Code als Add-in *in*
Fusion läuft, ist die ganze Frage weg:

- kein Build, kein Compiler, kein Zertifikat, keine `.exe`
- Quelltext bleibt Klartext und für jeden im Editor lesbar
- kein SmartScreen, kein AV-Fehlalarm
- und der Interpreter ist immer der richtige, weil er von Fusion selbst kommt

Dein Instinkt, ein Plugin zu bauen, löst also nicht nur das Update-Problem, sondern
gleichzeitig die Packaging-Frage. Siehe §4.

### Was aus dem PowerShell-Patcher wird

Er wird zum **Notnagel, nicht zum Hauptweg**. Zwei Fälle bleiben, in denen ein Skript
außerhalb von Fusion sinnvoll ist:

1. Jemand will partout kein Add-in installieren.
2. Fusion startet nicht mehr, weil eine kaputte XML die Gewindeliste zerschossen hat
   (das passiert, siehe §4) — dann braucht man ein Werkzeug *außerhalb* von Fusion.

Für beides reicht ein schlankes `Notfall-Reparatur.bat` + `.ps1`. Batch allein ist zu
fragil (Codepage-Umlaute, `delims`-Fallen bei Pfaden mit Leerzeichen, kein Fehler-Handling);
PowerShell ist seit Windows 7 überall dabei und bleibt lesbarer Klartext.

### Ablauf des Notfall-Werkzeugs

```
┌─ 1. Suche Fusion-Installation ────────────────────────────────┐
│  a) läuft Fusion360.exe?  → Pfad aus dem Prozess  (sicherste  │
│     Quelle, dein bisheriger Weg)                              │
│  b) sonst: Verknüpfung im Startmenü auslesen                  │
│  c) sonst: %LOCALAPPDATA%\Autodesk\webdeploy\production\*      │
│     durchsuchen, alle Ordner mit .\Fusion\Server\Fusion\       │
│     Configuration\ThreadData sammeln                           │
└───────────────────────────────────────────────────────────────┘
                              ↓
┌─ 2. Bericht anzeigen ─────────────────────────────────────────┐
│  [OK]  Fusion läuft (Version 2.0.xxxxx)                       │
│  [OK]  ThreadData gefunden:  ...\production\a1b2c3\...        │
│  [i]   3 weitere Installationen gefunden (Altversionen)       │
│  [i]   8 Gewinde-Dateien zum Einspielen bereit                │
│  [i]   davon 5 bereits vorhanden und identisch                │
│  [i]   davon 1 vorhanden, aber älter → wird ersetzt           │
│  [i]   davon 2 fehlen komplett → werden neu angelegt          │
└───────────────────────────────────────────────────────────────┘
                              ↓
┌─ 3. Kopieren + Verifizieren ──────────────────────────────────┐
│  Backup vorhandener Dateien nach ...\ThreadData\_backup_JJMMTT│
│  Kopieren, danach Hash-Vergleich Quelle ↔ Ziel                │
└───────────────────────────────────────────────────────────────┘
                              ↓
┌─ 4. Abschluss ────────────────────────────────────────────────┐
│  [FERTIG] 3 Dateien geschrieben, 5 unverändert.               │
│                                                               │
│  >>> FUSION 360 JETZT NEU STARTEN <<<                         │
│  Die Gewinde erscheinen erst nach einem Neustart unter        │
│  ERSTELLEN → Gewinde → Typ.                                   │
│                                                               │
│  [Optional] Update-Schutz installieren? (J/N)                 │
└───────────────────────────────────────────────────────────────┘
```

**Verbesserung gegenüber jetzt:** Der Patcher kopiert selbst, statt nur den Explorer zu
öffnen und den Nutzer ziehen zu lassen. Ein Schritt weniger, keine Fehlerquelle.
Er patcht außerdem *alle* gefundenen Installationen, nicht nur die laufende — dann ist
auch nach einem Rollback alles da.

**Nicht-Ziele:** kein Admin-Recht, kein Autostart-Eintrag, keine Netzwerkverbindung,
kein Schreiben außerhalb von `ThreadData` und dem eigenen Ordner.

---

## 4. Das Plugin — jetzt der Kern des Projekts

### Warum das Problem existiert

Fusion installiert sich nach jedem Update in einen **neuen** Ordner
`%LOCALAPPDATA%\Autodesk\webdeploy\production\<neuer-Hash>\` und migriert dabei den
`ThreadData`-Ordner nicht mit. Deine Gewinde sind also nicht gelöscht — sie liegen noch im
alten Ordner, den Fusion nur nicht mehr liest. Es gibt keinen von Autodesk vorgesehenen
Ort für persistente Custom Threads.

**Der Hebel:** Der Add-in-Ordner
`%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\` liegt *außerhalb* von `webdeploy` und
**überlebt Updates**. Alles, was dort liegt, ist nach dem Update noch da. Genau das nutzt
ThreadKeeper aus — und genau das würde unser Add-in auch tun.

### Wie schwer ist so ein Add-in? (deine Frage)

Ein Fusion-Add-in ist **kein kompiliertes Plugin**, sondern ein Ordner mit Textdateien:

```
API\AddIns\FdmThreads\
├── FdmThreads.manifest        ← ~15 Zeilen JSON (Name, Version, Autostart)
├── FdmThreads.py              ← der Code
├── bibliothek/                ← DIE Gewinde-Bibliothek, überlebt Updates
└── resources/                 ← Icons für die Menüleiste
```

Kein Build, kein Compiler, keine Abhängigkeiten, kein Paketmanager. Die benötigte
API-Oberfläche ist überschaubar: `adsk.core.Application.get()`, Command-Dialoge,
`shutil.copy2()`, `xml.etree` aus der Standardbibliothek.

**Aufwandsschätzung — ehrlich, nach Ausbaustufe:**

| Stufe | Umfang | Aufwand |
|---|---|---|
| Nur Wiederherstellen beim Start | ~120 Zeilen | ein halber Tag |
| + Menü, Force-Sync, Status-Dialog | ~300 Zeilen | 1–2 Tage |
| + Einfüge-Box mit Validierung | ~500 Zeilen | 3–4 Tage |

Die letzte Stufe ist die aus deiner Roadmap. Ich hatte oben „ein halber Tag" geschrieben —
das galt für die reine Wiederherstellung. Für das, was du jetzt beschreibst, ist es
deutlich mehr. Nicht schwer, aber nicht an einem Abend fertig.

### Deine Roadmap-Idee — und warum sie den Umweg überflüssig macht

Dein Vorschlag: *Nutzer holt sich den Prompt aus dem Plugin → geht zu einer Web-KI →
kopiert den XML-Output zurück ins Plugin → Plugin speichert ihn versionsfest.*

Das ist der richtige Zuschnitt, und zwar aus einem Grund, der über Bequemlichkeit
hinausgeht: **Der Nutzer muss nie den AppData-Ordner sehen.** Kein Explorer-Pfad, kein
„Speichern unter → Alle Dateien → Endung .xml", kein Verwechseln des Versionsordners. Das
sind genau die drei Stellen, an denen die aktuelle Anleitung Leute verliert.

**Menü unter `UTILITIES → FDM THREADS`:**

| Befehl | Was passiert |
|---|---|
| **Gewinde wiederherstellen** | Bibliothek → aktueller ThreadData-Ordner. Manuell auslösbar. |
| **Neues Gewinde einfügen…** | Dialog mit großem Textfeld. KI-Output reinpasten → Prüfen → Speichern. |
| **Prompt für KI kopieren** | Zeigt den System-Prompt in einem Nur-Lese-Textfeld zum Markieren, dazu ein Link-Knopf zu ChatGPT/Claude. |
| **Bibliothek öffnen** | Explorer im Bibliotheksordner. |
| **Status / Diagnose** | Welcher ThreadData-Ordner ist aktiv, was ist installiert, was fehlt. |

**Die Einfüge-Box ist der eigentliche Gewinn — wegen der Prüfung.** Eine fehlerhafte XML im
ThreadData-Ordner lässt nicht nur das eigene Gewinde verschwinden, sondern kann **die
komplette Gewindeliste in Fusion abschießen** — inklusive aller Standardgewinde. Genau davor
warnt auch das Autodesk-Support-Dokument. Und LLM-Output ist erfahrungsgemäß in ~1 von 10
Fällen subtil kaputt.

Das Plugin prüft deshalb vor dem Speichern:

1. Wohlgeformtes XML, Wurzelelement `<ThreadType>`
2. Pflichtfelder vorhanden, `<Name>` kollidiert nicht mit vorhandenen
3. `<SortOrder>` ≥ 200 — sonst automatisch hochsetzen und Bescheid geben
4. `MajorDia > PitchDia > MinorDia`, alle Werte positiv und plausibel
5. Jede `<Class>` hat `internal` **und** `external` (bzw. `<ExternalOnly>`)
6. `<TapDrill>` nur bei internal

Bei einem Fehler: Meldung im Klartext („Zeile 23: MinorDia ist größer als MajorDia — das
Profil wäre nach innen gestülpt"), Datei wird **nicht** geschrieben. Der Nutzer kann den
Text im Feld korrigieren oder der KI die Meldung zurückgeben.

Sinnvolle Ergänzung: eine **Vorschau** des Profils als Text (Winkel, Steigung, errechnete
Gewindetiefe, Spiel je Klasse) vor dem Speichern. Dann sieht der Nutzer, ob die KI Unsinn
gerechnet hat, bevor er drei Stunden druckt.

### Was das Plugin bewusst NICHT tut

Du hattest Bedenken, ein automatischer Patch sei „zu aufdringlich" — die teile ich für alles,
was außerhalb von Fusion läuft. Deshalb ausdrücklich **nicht**: kein Windows-Autostart, keine
Scheduled Task, kein Dateisystem-Watcher, kein Dienst, keine Netzwerkverbindung ohne
Nutzeraktion. Nichts läuft, wenn Fusion nicht läuft. Deinstallation = Ordner löschen.

Beim Start ist es still, solange nichts fehlt. Erst wenn nach einem Update tatsächlich
Gewinde weg sind, meldet es sich — einmal, mit dem Hinweis auf den nötigen Neustart.

### Die zwei ernsthaften Risiken

1. **Neustart-Problem (unvermeidbar).** Fusion liest die Gewinde-Definitionen *beim Start*
   ein. Ein Add-in, das beim Start kopiert, kommt in derselben Sitzung zu spät → die
   Gewinde erscheinen erst beim *nächsten* Start. ThreadKeeper hat exakt dieselbe
   Einschränkung. Das ist keine Schwäche der Umsetzung, sondern Fusions Architektur.
   Ehrlich dokumentieren statt kaschieren.
2. **Wartungslast.** Autodesk hat die Ordnerstruktur schon mehrfach geändert (ThreadKeepers
   Changelog zeigt genau solche Fixes für macOS). Ein eigenes Add-in heißt: du bist dafür
   langfristig verantwortlich. Das ist der einzige echte Grund, stattdessen auf ThreadKeeper
   zu setzen — aber ThreadKeeper kann die Einfüge-Box nicht, und die ist dein
   Alleinstellungsmerkmal.

### Ausbaustufen des Plugins

So gebaut, dass nach jeder Stufe etwas Fertiges dasteht:

| Stufe | Inhalt | Zustand danach |
|---|---|---|
| **P1** | Manifest, Bibliothek, Wiederherstellen beim Start, Menüpunkt „Jetzt wiederherstellen" | Update-Problem gelöst. Wäre für sich genommen schon ein veröffentlichungswürdiges Add-in. |
| **P2** | Status/Diagnose-Dialog, Bibliothek öffnen, Backup vor Überschreiben | Alltagstauglich, Fehler nachvollziehbar |
| **P3** | Einfüge-Box mit Validierung + Profil-Vorschau | Nutzer kommt nie mehr an AppData |
| **P4** | „Prompt für KI kopieren" + Link-Knopf | Der Kreis aus deiner Roadmap ist geschlossen |
| **P5** | Profil-Vorschau grafisch statt als Text | Kür |

**Installation des Plugins selbst** bleibt der einzige Handgriff außerhalb von Fusion: den
Ordner nach `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\` kopieren. Dieser Pfad ist
**stabil** (kein Versions-Hash), lässt sich in die Explorer-Adressleiste einfügen und ist
einmalig. Dafür genügt entweder ein ZIP mit Anleitung wie bei ThreadKeeper oder eine
10-Zeilen-`Plugin installieren.bat`. Ich würde beides anbieten.

---

## 5. Repo-Struktur

```
fusion-fdm-threads/
├── README.md                    ← ersetzt "Info BITTE lesen.txt"
├── LICENSE                      ← Code MIT, Gewindedaten CC BY 4.0
├── CHANGELOG.md
├── .gitignore
├── .github/workflows/validate.yml
│
├── install/
│   ├── Gewinde installieren.bat        ← DAS Doppelklick-Ziel
│   └── lib/patch-threads.ps1
│
├── threads/                     ← die Gewinde-XMLs, saubere Namen
│   ├── 01_TR21x4_Sodastream.xml
│   ├── 02_DIN477_CO2.xml
│   ├── 03_PCO1881_PET.xml
│   ├── 04_G34_Gardena.xml
│   ├── 05_UNC_14_Stativ.xml
│   ├── 06_UNC_38_Stativ.xml
│   ├── 07_E27_Lampenfassung.xml
│   └── 08_Trapez_FDM_TR8-TR150.xml     ← war .txt! (33 Größen)
│
├── addin/FdmThreadGuard/        ← Stufe 2, optional
│
├── examples/
│   ├── CO2-Gewindeschutzkappe.f3d
│   └── CO2-Gewindeschutzkappe.png
│
└── docs/
    ├── 01-warum-eigene-gewinde.md   ← Verdreh-Problem, Sweep-Falle
    ├── 02-anatomie-einer-xml.md     ← Feld-für-Feld erklärt
    ├── 03-toleranzen-kalibrieren.md ← Tight/Safe/Exact, Testdruck
    ├── 04-eigene-gewinde-bauen.md   ← Anleitung zum Selbermachen
    ├── 05-fusion-update-problem.md  ← webdeploy, warum das passiert
    └── 06-troubleshooting.md
    └── SICHERHEIT.md                ← deine Warnhinweise, prominent
```

**Dateibenennung:** Der Präfix `[3D-Print]` verschwindet aus den *Dateinamen* (Klammern in
Dateinamen sind unter Windows harmlos, in URLs aber hässlich und in Skripten fehleranfällig).
Im `<CustomName>`, also dem, was der Nutzer in Fusion sieht, **bleibt** er — dort ist er
ja der Sinn der Sache. Die Nummern-Präfixe halten die Dateiliste in derselben Reihenfolge
wie `<SortOrder>`.

---

## 6. Dokumentation — „was passiert hier eigentlich"

Das war dein Wunsch nach einer ausführlichen Erklärung. Der Kern kommt in
`docs/02-anatomie-einer-xml.md`. Skizze des Inhalts:

**Ein `ThreadType` ist eine Nachschlagetabelle, kein Modell.** Fusion errechnet die
Gewindegeometrie zur Laufzeit aus fünf Zahlen. Deshalb gibt es kein Verdreh-Problem: es wird
nichts gesweept, sondern gerechnet.

| Feld | Bedeutung | Wirkung beim Druck |
|---|---|---|
| `<Angle>` | Flankenwinkel in Grad | 60° = metrisch/UNC, 55° = Whitworth/G, 30° = ISO-Trapez, **45° = FDM-Sonderprofil** — flacher, druckt sich ohne Stützen sauberer |
| `<Pitch>` / `<TPI>` | Steigung mm bzw. Gänge/Zoll | Unter ~1,5 mm Steigung verschmiert FDM das Profil |
| `<MajorDia>` | Außendurchmesser | Beim Innengewinde **größer**, beim Außengewinde **kleiner** als Nennmaß → das ist das Spiel |
| `<PitchDia>` | Flankendurchmesser | Trägt die eigentliche Kraft |
| `<MinorDia>` | Kerndurchmesser | |
| `<TapDrill>` | Bohrer-Ø | Nur bei `internal`, für Fusions Bohrungswerkzeug |
| `<Class>` | Toleranzklasse | Bei uns zweckentfremdet als **Spiel-Wähler**: `0.15mm (Tight)`, `0.20mm (Safe)` |
| `<Gender>` | internal/external | Jede Klasse braucht beide Einträge |
| `<SortOrder>` | Position im Dropdown | Muss projektweit eindeutig sein |

Dazu ein durchgerechnetes Beispiel (TR21×4 Sodastream: wie aus 21,00 mm Nennmaß
21,30 / 20,85 werden) und die Erklärung des Update-Problems in `05-`.

---

## 7. Der Custom-Teil: eigene Gewinde ableiten

Deine Idee, dem Nutzer das Ableiten eigener Profile zu ermöglichen — hier ist der ehrliche
Möglichkeitsraum, denn er ist enger, als er auf den ersten Blick aussieht.

### Was Fusion aus deiner XML wirklich macht

Wichtige Erkenntnis vorweg: **Die XML enthält keine Profilform.** Sie enthält nur Zahlen.
Fusion zeichnet daraus immer dieselbe Grundform: ein **symmetrisches, oben und unten
gekapptes V**. Wie dieses V aussieht, steuerst du über genau fünf Werte:

```
        MajorDia/2  ─────┬───────┐  ← Kappung oben (Kopfbreite)
                         │  ╱ ╲  │
        PitchDia/2  ─ ─ ─│ ╱   ╲ │ ─ ─   ← Angle = Öffnungswinkel des V
                         │╱     ╲│
        MinorDia/2  ─────┴───────┘  ← Kappung unten (Grundbreite)
                         │←Pitch→│
```

- **`Angle`** spreizt das V auf.
- **`MajorDia` − `MinorDia`** bestimmt, wie tief das V stehen bleibt, also wie stark oben
  und unten abgeschnitten wird.
- **`PitchDia`** legt fest, auf welcher Höhe die Referenzlinie liegt — verschiebt damit das
  Verhältnis von Kopf- zu Fußbreite.
- **`Pitch` / `TPI`** ist der Abstand von Gang zu Gang.

Genau deshalb funktionieren deine Trapezgewinde: Ein 30°-V, das man oben und unten kräftig
abschneidet, **ist** ein Trapez. Und dein 45°-FDM-Profil ist dasselbe Prinzip mit flacheren
Flanken — druckt sich ohne Stützen sauberer und schält beim Überhang nicht ab.

### Was damit geht — und was nicht

| Geht | Geht nicht |
|---|---|
| Jeder Flankenwinkel (spitz bis fast flach) | **Asymmetrische Profile** — dein „Zacken"/Sägezahn. Es gibt nur *einen* `Angle`, und der gilt für beide Flanken. |
| Jede Steigung | **Rundprofile** (echtes E27, Rd-Gewinde). Nur als V-Näherung möglich — genau das ist unsere E27-Datei. |
| Jede Gewindetiefe, von hauchdünn bis fast Vollprofil | **Unterschiedliche Kopf-/Fußverrundung** |
| Trapez, Vierkant-Näherung (sehr flacher Winkel), Spitzgewinde | **Variable Steigung** |
| Beliebige Durchmesser und Spielmaße | **Mehrgängig / Linksgewinde** — das stellt Fusion im Dialog ein, nicht die XML |

**Fazit für den Sägezahn:** Über die XML nicht machbar. Wer ein echtes Buttress-Gewinde
braucht, muss zurück zu Spirale + Sweep — also genau in die Verdreh-Falle, die dieses
Projekt eigentlich umgehen will. Das gehört ehrlich dokumentiert, samt dem Hinweis, dass
ein sehr flankenasymmetrisches Gewinde im FDM-Druck ohnehin selten hält, was es verspricht.

### Die Grundformen — nachgezählt, nicht geschätzt

Du hattest „5 oder 8 Grundformen" vermutet. Tatsächlich sind es **18 Dateien, aber nur
5 verschiedene Flankenwinkel**. Mehr Formen gibt Fusion strukturell nicht her:

| `Angle` | Dateien | Wofür als Vorlage |
|---|---|---|
| **60°** | ISO Metric profile, ANSI Metric M Profile, ANSI Unified Screw Threads, GB Metric profile, Inch Tapping Threads, Metric Forming Screw Threads, AFBMA Locknuts, DIN Wood Screw, GOST Self-tapping | Standard-Spitzgewinde: M, UNC/UNF, Stativ, PET |
| **55°** | ISO Pipe, BSP Pipe, DIN Pipe, JIS Pipe, GB Pipe | Whitworth-Familie: Gardena G3/4", CO2 |
| **45°** | Inch Tapping Threads **for Plastics** | Kunststoff |
| **30°** | ISO Metric Trapezoidal, Metric Tapping Threads **for Plastics** | Trapez, Bewegungsgewinde |
| **29°** | ACME Screw Threads | Zoll-Trapez |

**Bemerkenswert:** Die beiden einzigen Dateien mit „for Plastics" im Namen haben **45°**
bzw. **30°** — Autodesk selbst weicht für Kunststoff vom 60°-Standard ab. Dein 45°-FDM-Profil
ist damit keine Bastelei, sondern deckt sich mit Autodesks eigener Herangehensweise. Das
gehört so in die README, es ist das stärkste Argument für das ganze Projekt.

**Außerdem entdeckt:** Sechs Standarddateien nutzen ein Element, das in unseren XMLs fehlt:

```xml
<ExternalOnly>yes</ExternalOnly>
```

Direkt nach `<SortOrder>` gesetzt, blendet es die Innengewinde-Auswahl komplett aus.

**Für unsere Dateien aber nicht verwenden.** Ich hatte es kurz beim E27 erwogen, um das
Innengewinde aus Sicherheitsgründen zu sperren — das ist der falsche Reflex. Jemand will
eine Deko-Fassung drucken, jemand anders eine Fake-Glühbirne, ein Dritter einen Stopfen zum
Einschrauben. Wer weiß das vorher? Eine Warnung informiert, eine ausgegraute Auswahl
bevormundet nur und hilft niemandem. `<ExternalOnly>` ist für Gewinde gedacht, die es
physisch nur als Bolzen gibt (Schneidschrauben) — nicht als Erziehungsmaßnahme.

### Der Ableitungs-Assistent

Dein Vorschlag (*Nutzer beschreibt, was er will → wir wählen die Gewindeart → XML anpassen →
Toleranzen abfragen*) lässt sich sauber in einen Ablauf gießen:

```
Was soll das Gewinde tun?
├─ Etwas auf-/zuschrauben, Deckel, Kappe          → 60° Spitz oder 45° FDM
├─ Etwas bewegen, Spindel, Presse, Klemme         → 30° Trapez (oder 45° FDM)
├─ An ein vorhandenes Bauteil passen (nachbauen)  → Original ausmessen, s.u.
└─ Etwas abdichten (Rohr, Wasser)                 → 55° Whitworth
                          ↓
Nennmaß + Steigung        (gemessen oder aus Norm)
                          ↓
Gewindetiefe wählen       flach (leicht zu drucken) ↔ tief (mehr Halt)
                          ↓
Toleranz wählen           0.00 Exact · 0.15 Tight · 0.20 Safe · frei
                          ↓
fertige .xml + Einbau
```

**Wie ausmessen** (der Teil, den alle unterschätzen und der in `docs/` gehört):
Außendurchmesser mit dem Messschieber = `MajorDia`. Steigung = Länge über 10 Gänge geteilt
durch 10 — nicht ein einzelner Gang, der Messfehler ist sonst zu groß. Kerndurchmesser am
Gewindegrund. `PitchDia` ist bei symmetrischen Profilen einfach der Mittelwert aus Major und
Minor. Flankenwinkel schätzt man am Abdruck in Knetmasse oder wählt einfach die
naheliegendste Familie.

### Umsetzungsvorschlag: `Gewinde-Generator.html`

Eine einzelne HTML-Datei im Repo, die per Doppelklick im Browser aufgeht — **kein Server,
kein Internet, keine Installation.** Das passt exakt zu deiner Anforderung „maximal ein
Doppelklick" und ist für Otto Normalverbraucher deutlich zugänglicher als jedes Skript:

- Vier Eingabefelder plus Auswahlliste für die Grundform
- **Live-Vorschau des Profils als SVG**, maßstäblich — man *sieht* sofort, was ein
  45°-Winkel oder eine flachere Gewindetiefe bewirkt
- Plausibilitätsprüfung in Echtzeit (Kopfbreite < 0, Tiefe größer als geometrisch möglich,
  Steigung zu fein für FDM, …)
- Checkboxen für die Toleranzklassen; erzeugt alle `internal`/`external`-Paare automatisch
- Knopf „XML herunterladen" → fertige Datei, die der Patcher aus §3 direkt einspielen kann

Aufwand: überschaubar, weil es reine Rechnerei ohne Abhängigkeiten ist. Zusätzlicher Nutzen:
Der Generator ist gleichzeitig die beste Dokumentation — wer damit zehn Minuten spielt, hat
verstanden, wie ein Gewindeprofil funktioniert.

Ergänzend in `docs/04-eigene-gewinde-bauen.md` das Ganze als Kochbuch zum Nachlesen, mit
einem vollständig durchgerechneten Beispiel („Ich will den Deckel meiner Thermoskanne
nachbauen").

### Variante B: der LLM-Assistent — **fertig, liegt daneben**

Deine Idee mit dem Dialog-Assistenten ist die bessere Hälfte davon, weil sie den Teil
abdeckt, den ein Formular nicht kann: *„Was ist das überhaupt für ein Gewinde?"*
Der vollständige System-Prompt liegt als `Gewinde-Assistent-PROMPT.md` daneben — mit
Faktenblock, Rechenweg, Katalog bekannter Gewinde, Messanleitung, Sicherheitsregeln und
drei Few-Shot-Dialogen (bekanntes Gewinde / freies Gewinde / unmöglicher Wunsch).

Eine Sache habe ich gegenüber deinem Beispieldialog verschoben: Die Frage „Deckel oder
Bolzen?" ist richtig, aber nicht aus dem Grund, den man vermutet. **Beide Geschlechter
gehören immer in dieselbe XML** — die Frage entscheidet nicht, *was* drin steht, sondern
*wo das Spiel hinkommt*:

| Fall | gedruckt | Spiel auf |
|---|---|---|
| A | nur Deckel, Flasche ist echt | nur `internal`. `external` bleibt exakt auf Nennmaß, sonst passt die echte Flasche nicht |
| B | nur Bolzen, Gegenstück ist echt | nur `external` |
| C | beide Teile gedruckt | halbes Spiel auf jede Seite |

Genau hier liegt auch der Fehler in unseren aktuellen XMLs (siehe §1.7) — sie machen
immer Fall C, mit doppeltem Spielwert. Der Assistent stellt diese Frage deshalb als erstes.

**Arbeitsteilung der beiden Werkzeuge:**

- **Assistent** → *„Ich weiß nicht, was ich habe."* Erkennen, ausmessen, ableiten.
- **Generator** → *„Ich weiß, was ich will, aber nicht die Zahlen."* Schieberegler,
  Sofortvorschau, Kalibrieren.

**Zur Diskussion:** Der Assistent kostet nichts außer Testen und kann sofort in v1.0.
Den Generator würde ich auf v1.1 schieben — sonst verzögert er die Auslieferung der
Gewinde, die ja schon fertig sind.

---

## 8. Toleranzklassen — `Exact` fliegt raus

**Du hast recht, ich hatte zu schnell zugestimmt.** Meine Begründung war „für Leute, die
selbst kalibrieren wollen" — die trägt nicht:

- Ein Gewinde mit 0,00 mm Spiel **lässt sich nicht schrauben.** Nicht straff, sondern gar
  nicht. Niemand kalibriert damit irgendwas, er druckt nur einmal Ausschuss.
- Das Wort „Exact" verspricht dabei genau das Gegenteil von dem, was passiert. Wer es liest,
  denkt „maßhaltig, das will ich doch" — und wählt ausgerechnet die einzige Klasse, die
  garantiert nicht funktioniert. Ein Label, das den Nutzer in die Falle lockt.
- Und es ist ohnehin redundant: sobald wir die Fälle A/B aus §7 sauber bauen, steht das
  Nennmaß bereits als nicht-gedruckte Seite in der Datei.

### Zu deinem H7-Vergleich — und zu meinem IT11

**Meine IT-Angabe war auch falsch, danke fürs Nachhaken.** Gleich doppelt:

1. **IT-Grade gelten für Gewinde überhaupt nicht.** ISO 286 (IT01 … IT18) beschreibt glatte
   Maße — Bohrungen, Wellen, Längen. Gewinde haben ein eigenes System: **ISO 965**, mit
   Toleranzgraden 3–9 und Toleranzlagen (`e`, `g`, `h` außen; `G`, `H` innen). Daher
   „6H/6g" und eben nicht „H7".
2. **Ich habe zwei verschiedene Größen verglichen.** IT11 ist eine Toleranz*breite* — wie
   stark ein Maß streuen darf. 0,15 mm ist ein *Spiel* — die Lücke zwischen zwei Teilen.
   Das eine beschreibt Fertigungsstreuung, das andere eine Passung. Die kann man nicht
   gleichsetzen.

**Konsequenz: IT-Grade kommen in der README nicht vor.** Auch nicht als grober Vergleich —
das lädt nur zu Widerspruch ein.

### Was stattdessen stimmt

Der Vergleich mit der **Gewindepassung** trägt. Ein ganz normales M20×2,5 in 6H/6g, also
die Baumarktschraube:

| | Spiel am Flankendurchmesser |
|---|---|
| Mindestspiel (Grundabmaß `g`) | 0,042 mm |
| Höchstspiel (beide Toleranzen ausgereizt) | ~0,42 mm |
| typisch in der Praxis | ~0,2 mm |

Deine 0,15 mm liegen damit **in derselben Größenordnung wie eine serienmäßige
Metallverschraubung**, eher am strammen Ende. Das ist die Formulierung für die README —
„in derselben Größenordnung wie", nicht „entspricht". Eine Konformitätsaussage ist es
nicht, und die braucht es auch nicht.

### Deine eigentliche Frage: ist 0,15 mm real schraubbar?

Ja. Aber der begrenzende Faktor im FDM ist **keine Toleranzklasse**, sondern Physik des
Verfahrens — deshalb sind 0,1 / 0,15 / 0,2 empirische Werte und nicht aus einer Norm
ableitbar:

- **Düse und Extrusionsbreite.** Eine 0,4er Düse kann keine scharfe Gewindespitze legen. Die
  Flanken werden verrundet, Kopf und Fuß bekommen einen Radius. Das allein frisst je nach
  Profil schon 0,05–0,1 mm.
- **Schichthöhe quantisiert die Flanke.** Bei 0,2 mm Schicht und 2,7 mm Steigung sind das
  13,5 Schichten pro Gang — die Flanke ist eine Treppe, keine Gerade. Feine Steigungen unter
  ~1,5 mm verschmieren deshalb komplett.
- **Elefantenfuß** verzieht die ersten Schichten nach außen.
- **Schwund beim Abkühlen**, materialabhängig: PLA wenig, PETG/ABS deutlich mehr.
- **Druckorientierung.** Stehend gedruckt (Gewindeachse = Z) läuft es sauberer als liegend,
  wo die Flanken zu Überhängen werden. Ein liegendes Gewinde braucht spürbar mehr Spiel.

Deswegen ist ein Kalibrier-Testteil (siehe unten) mehr wert als jede Tabelle: Es misst
genau die Summe dieser Effekte für den konkreten Drucker.

### Die Klassen — **abgestimmt, gilt**

Deine Beobachtung, dass es am Drucker hängt, gehört ins Label. Der Nutzer wählt nicht nach
Zahl, er wählt nach Gefühl:

| `<Class>` | Für wen | Erwartung |
|---|---|---|
| `0.10 mm - stramm (guter Drucker)` | kalibrierte Maschine, 0.4er Düse, langsam | geht schwer, sitzt spielfrei; ggf. einmal einlaufen lassen |
| `0.15 mm - Standard (Handkraft)` | die meisten | dreht mit spürbarem Widerstand, kein Wackeln ← **Voreinstellung** |
| `0.20 mm - leichtgängig (sichere Wahl)` | ältere/schnelle Drucker, große Ø | läuft leicht, minimal Spiel |

Drei Einträge sind genug; jede weitere Klasse macht das Dropdown unbrauchbar. Bei
Durchmessern über ~40 mm zusätzlich `0.30 mm - locker`, weil dort der Schwund beim Abkühlen
messbar dazukommt (0,2 % von 100 mm sind schon 0,2 mm).

Zwei Details noch:

- **Sprache vereinheitlichen.** `Tight` und `Safe` in einem sonst deutschen Projekt ist
  inkonsistent. Entweder ganz deutsch oder ganz englisch — ich würde bei den Klassen
  deutsch nehmen, weil dort die Erklärung steht, und die `<CustomName>` englischsprachig
  lassen, damit die Dateien international nutzbar bleiben.
- **Material erwähnen.** PETG und ABS brauchen mehr Spiel als PLA (Schwund, Fadenzieher).
  Gehört in `docs/03-toleranzen-kalibrieren.md`, nicht ins Label.

### Empfehlung: ein Kalibrier-Testteil beilegen

Der beste Weg, die ganze Diskussion für den Nutzer zu beenden: ein kleines Druckteil mit
allen drei Passungen nebeneinander auf einer Platte, dazu ein passender Gegenring. Einmal
drucken, ausprobieren, ab dann weiß man für den eigenen Drucker ein für alle Mal, welche
Klasse man nimmt. Kostet dich eine Stunde Konstruktion und erspart hunderten Leuten je drei
Fehldrucke. Als `examples/Toleranz-Testset.f3d` plus fertige STL.

---

## 9. Qualitätssicherung

Ein GitHub-Action-Workflow prüft bei jedem Push automatisch:

1. Alle `threads/*.xml` sind wohlgeformtes XML
2. `<Name>` und `<SortOrder>` sind projektweit eindeutig
3. Jede `<Class>` hat sowohl `internal` als auch `external`
4. Plausibilität: `MajorDia > PitchDia > MinorDia`; internal-Ø > external-Ø derselben Klasse
5. Keine verirrten `.txt`-Dateien in `threads/` (verhindert genau den Fehler von oben)

Das kostet einmalig ~60 Zeilen Python im CI und fängt genau die Fehlerklasse ab, die dir
jetzt passiert ist.

---

## 10. Vorgeschlagene Reihenfolge

**v1.0 — die Daten in Ordnung bringen**

| # | Schritt | Anmerkung |
|---|---|---|
| 1 | XML-Fehler beheben (`.txt` → `.xml`, TR8x2-Konflikt, doppelte Leerzeichen) | Höchste Wirkung, kleinster Aufwand |
| 2 | `SortOrder` auf 200+ | Kollision mit Autodesk-Standards, §1.6 |
| 3 | Toleranzklassen vereinheitlichen, `Exact` raus | §8 |
| 4 | Spiel-Frage klären — Fall A/B/C | §1.7, §7 |
| 5 | Repo-Struktur, README, `docs/`, SICHERHEIT.md | |
| 6 | CI-Validierung | |
| 7 | Assistent-Prompt testen und beilegen | liegt fertig vor |
| 8 | `git init`, Push, Release v1.0 | |

**v2.0 — das Plugin** (§4). Nach jeder Stufe ist etwas Fertiges da.

| # | Schritt |
|---|---|
| 9 | P1: Manifest + Wiederherstellen beim Start |
| 10 | P2: Menü, Status/Diagnose, Backup |
| 11 | P3: Einfüge-Box mit Validierung |
| 12 | P4: „Prompt für KI kopieren" — Kreis geschlossen |

**v2.1 — Kür**

| # | Schritt |
|---|---|
| 13 | `Toleranz-Testset.f3d` + STL (könnte auch früher kommen, wenn du Lust hast) |
| 14 | `docs/04-eigene-gewinde-bauen.md` (Kochbuch, Ausmessen, Rechenbeispiel) |
| 15 | Profil-Vorschau grafisch im Plugin |
| 16 | `Gewinde-Generator.html` — nur noch, falls das Plugin die Lücke nicht schließt |
| 17 | `Notfall-Reparatur.bat` für den Fall „Fusion startet nicht mehr" (§3) |

---

## 11. Zu klären, bevor ich anfange

1. **TR8x2-Konflikt:** 30°-Einzeldatei behalten, verwerfen, oder umbenennen zu
   „TR8x2 (Norm 30°)" neben „TR8x2 (FDM 45°)"?
2. **Spielverteilung:** Bauen wir pro Gewinde Varianten für Fall A/B/C, oder bleibt es bei
   einer Datei mit dokumentierter Fall-C-Annahme? Varianten sind ehrlicher, verdreifachen
   aber die Einträge im Dropdown.
3. ~~Klassen-Labels~~ — **erledigt**, `0.10 stramm / 0.15 Standard / 0.20 leichtgängig`.
4. **v1.0 vor dem Plugin ausliefern** — oder willst du direkt aufs Plugin zugehen und die
   XML-Korrekturen mitnehmen?
5. **Lizenz:** MIT für alles, oder Code MIT + Daten CC BY 4.0?
6. **Repo-Name** und ob GitHub-Account/Sichtbarkeit schon feststehen.
