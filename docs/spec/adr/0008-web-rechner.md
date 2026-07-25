# ADR-0008 — Web-Rechner als Hauptweg für Endnutzer

**Status:** 📌 vorgeschlagen · **Datum:** 2026-07-25

## Kontext

Der Rechner `tools/build_thread.py` löst das Rechenproblem ([ADR-0007](0007-ki-recherchiert-rechner-rechnet.md)),
aber er ist ein Python-Skript auf der Kommandozeile. Verfassung § 4 sagt: Der Nutzer kann kein
CAD und will es nicht lernen — Kommandozeile ist für ihn keine Option, und Python hat er
nicht installiert.

Damit steht der Workflow auf halbem Weg: Die KI liefert ein sauberes Rezept, und dann bricht
die Kette ab.

Gleichzeitig kommt bei Leuten, die den Prompt ohne unser Werkzeug benutzen, ein zweiter Fall
auf: Sie haben von *irgendeiner* KI eine fertige XML bekommen, die vermutlich Rechenfehler
enthält, und wissen nicht, ob sie ihr trauen können.

## Entscheidung

Eine **einzelne HTML-Datei** `werkzeug/gewinde-rechner.html`, die beides kann:

| Eingabe | Was passiert |
|---------|--------------|
| **Rezept** (TOML oder JSON) | erzeugt die vollständige XML |
| **Fertige XML** von irgendeiner KI | prüft sie, rechnet abgeleitete Werte **neu**, gibt eine korrigierte Datei aus und listet auf, was falsch war |

Ausgabe: Download-Knopf mit fertigem Dateinamen, plus eine maßstäbliche SVG-Vorschau des
Profils.

**Zwei Betriebsarten, gleicher Code:**

- **Offline** — Datei aus dem Release herunterladen, doppelklicken, Browser öffnet sie.
  Kein Server, kein Internet, keine Installation.
- **Online** — dieselbe Datei über GitHub Pages, damit man sie nur verlinken muss.

Der zweite Modus ist der eigentliche Gewinn: Die Antwort auf „wie kriege ich das jetzt in
eine Datei" wird ein Link statt einer Anleitung.

## Warum eine einzelne HTML-Datei

| Kriterium | HTML | Python-CLI | `.exe` | Webdienst mit Backend |
|---|:-:|:-:|:-:|:-:|
| Nichts zu installieren | ✅ | ❌ | ✅ | ✅ |
| Quelltext lesbar (§ 3) | ✅ | ✅ | ❌ | teilweise |
| Kein SmartScreen / AV-Alarm | ✅ | ✅ | ❌ | ✅ |
| Offline benutzbar | ✅ | ✅ | ✅ | ❌ |
| Keine Daten verlassen den Rechner | ✅ | ✅ | ✅ | ❌ |
| Laufende Kosten | keine | keine | keine | Hosting |
| Live-Vorschau des Profils | ✅ | ❌ | schwer | ✅ |

Alles läuft im Browser, nichts wird hochgeladen — das ist auch die ehrliche Antwort auf die
Datenschutzfrage: Es gibt keinen Server, der etwas sehen könnte.

## Der Preis: doppelte Rechenlogik

Die Klassen, Profilfaktoren und Plausibilitätsgrenzen existieren dann zweimal — in Python für
CI und Beitragende, in JavaScript für Endnutzer. Zwei Implementierungen driften
erfahrungsgemäß auseinander.

**Gegenmaßnahme:** Die Regeln wandern in eine gemeinsame Datendatei `tools/rules.json`
(sechs Klassen mit ihren δ, Profilfaktoren je Winkel, Plausibilitätsgrenzen). Beide Seiten
lesen sie, statt sie zu enthalten. Für die Offline-HTML wird die JSON beim Bauen eingebettet;
ein CI-Schritt prüft, dass die eingebettete Fassung mit der Quelle übereinstimmt.

Damit bleibt genau eine Stelle, an der eine Toleranzklasse geändert wird.

## Abgrenzung

Ausdrücklich **nicht**:

- **Kein Backend, keine Datenbank, kein Login.** Nichts zu betreiben, nichts zu warten.
- **Keine Telemetrie.** Verfassung, NA-9.
- **Kein freies Eingabeformular mit allen Durchmessern.** Das wäre der Blanko-Generator
  aus NA-8. Eingabe ist ein Rezept oder eine XML, nicht 20 leere Felder.
- **Kein Schreiben in den ThreadData-Ordner.** Der Browser darf das nicht und soll es nicht.
  Der Nutzer lädt die Datei herunter und kopiert sie — oder das Add-in nimmt sie entgegen.

## Konsequenzen

**Gut:**
- Die Kette KI → Rezept → Datei ist ohne Installation vollständig
- Der Modus „prüfe diese KI-XML" fängt genau die Nutzer ab, die den Prompt woanders
  benutzt haben
- Die SVG-Vorschau ist nebenbei die beste Dokumentation: Wer zehn Minuten am
  Flankenwinkel schiebt, hat verstanden, wie ein Profil funktioniert
- GitHub Pages ist kostenlos und braucht keine Wartung

**Schlecht:**
- Zwei Implementierungen der Rechenregeln, abgesichert durch `rules.json` und CI
- JavaScript hat keine `Decimal`-Klasse; die Rundung muss bewusst nachgebaut werden, damit
  beide Wege bitgleiche Ergebnisse liefern. Ein CI-Test vergleicht die Ausgabe beider
  Rechner für alle Rezepte im Repo.

## Umsetzungsreihenfolge

1. `tools/rules.json` einführen, Python liest daraus
2. HTML-Rechner: Rezept → XML, Download
3. Modus „XML prüfen und neu rechnen"
4. SVG-Profilvorschau
5. GitHub Pages einschalten, aus der README prominent verlinken
6. CI-Test: Python-Rechner und JS-Rechner liefern identische Ausgabe
