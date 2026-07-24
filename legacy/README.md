# 📚 Legacy — die ursprüngliche Forum-Fassung

> [!WARNING]
> **Hier nichts installieren.** Dieser Ordner ist ein Archiv. Die aktuellen Gewinde liegen
> in [`../threads/`](../threads/) — die hier beschriebenen Dateien sind inhaltlich identisch,
> heißen aber anders und haben einen Fehler (siehe unten).

Bevor dieses Projekt ein Repository wurde, war es ein ZIP-Paket aus dem
[drucktipps3d-Forum](https://forum.drucktipps3d.de/). `Info BITTE lesen.txt` ist die
Original-Anleitung von damals — aufbewahrt, weil sie erklärt, wie und warum das Projekt
entstanden ist.

## Was sich geändert hat

| Damals | Heute | Warum |
|--------|-------|-------|
| `Info BITTE lesen.txt` | [`README.de.md`](../README.de.md) | Markdown, zweisprachig, auf GitHub lesbar |
| `[3D-Print]  TR21x4 - Sodastream.xml` | `threads/01_TR21x4_Sodastream.xml` | Keine doppelten Leerzeichen, keine Klammern in Dateinamen — die machen in URLs und Skripten Ärger |
| `[3D-Print]  W 21,8 x 1_14 - CO2 Gasgewinde.xml` | `threads/02_DIN477_CO2.xml` | dito |
| `[3D-Print]  PCO1881 - PET Bottle.xml` | `threads/03_PCO1881_PET.xml` | dito |
| `[3D-Print]  G3-4 - Water-Gardena.xml` | `threads/04_G34_Gardena.xml` | dito |
| `[3D-Print]  1-4 - Photo Tripod.xml` | `threads/05_UNC_1-4_Tripod.xml` | dito |
| `[3D-Print]  3-8 - Pro Tripod.xml` | `threads/06_UNC_3-8_Tripod.xml` | dito |
| `[3D-Print]  E27 - Edison Lamp Socket.xml` | `threads/07_E27_LampSocket.xml` | dito |
| **`[3D-Print] Trapezgewinde FDM only.txt`** | **`threads/08_Trapezoidal_FDM_TR8-TR150.xml`** | ⚠️ **siehe unten** |
| `[3D-Print] TR8x2 .xml` | `threads/09_TR8x2_ISO30.xml` | Leerzeichen vor der Endung entfernt |
| `Thread Data Ordner finder.bat` | `tools/find-threaddata.bat` | Umbenannt, sonst unverändert |
| `neu 3.bat` | — | Byte-identische Kopie des Finders, nur zwei Kommentare anders. Entfernt. |
| `VirusTotal - Home.url` | Link in der [README](../README.de.md#-sicherheit) | Eine Verknüpfungsdatei im Repo bringt niemandem etwas |

Die Inhalte der XML-Dateien sind **unverändert** übernommen — nur die Dateinamen wurden
bereinigt. Wer die alte Fassung installiert hat, hat exakt dieselben Gewinde.

## ⚠️ Der Fehler in der alten Fassung

Das Trapezgewinde-Paket hieß **`[3D-Print] Trapezgewinde FDM only.txt`** — mit der Endung
`.txt`.

Fusion liest im `ThreadData`-Ordner **ausschließlich `*.xml`**. Diese Datei wurde also nie
geladen. Betroffen sind **33 Trapezgrößen von TR8×2 bis TR150×16** — der umfangreichste
Teil des ganzen Pakets.

Die Endung war seinerzeit kein Versehen: Das Forum akzeptierte beim Upload keine
XML-Anhänge. Wer die Datei von dort hat, muss sie also lokal auf `.xml` umbenennen, damit
sie funktioniert.

Im Repository heißt sie korrekt `.xml` — [`threads/08_Trapezoidal_FDM_TR8-TR150.xml`](../threads/08_Trapezoidal_FDM_TR8-TR150.xml).
