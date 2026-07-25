# ADR-0005 — Kein Packaging zu ausführbaren Dateien

**Status:** ✅ angenommen · **Datum:** 2026-07-24

## Kontext

Das Installationswerkzeug soll per Doppelklick startbar sein. Naheliegend wäre ein
Python-Skript, mit PyInstaller zu einer `.exe` gepackt — technisch eine Zeile
(`pyinstaller --onefile`).

## Entscheidung

**Keine kompilierten Binaries.** Windows-Werkzeuge sind `.bat` als Starter plus PowerShell
für die Logik, macOS bekommt ein Shell-Skript. Der Add-in-Code läuft in Fusions eigenem
Python.

## Begründung

| Problem | Auswirkung |
|---------|-----------|
| Größe | 30–80 MB für ein 200-Zeilen-Skript — der ganze Interpreter wandert mit |
| SmartScreen | Blockt jede unsignierte `.exe` beim ersten Start. Zertifikat kostet 200–400 €/Jahr |
| **Virenscanner** | PyInstaller-`--onefile` löst notorisch Fehlalarme aus; der Entpackmechanismus sieht für Heuristiken aus wie ein Malware-Packer |

Der letzte Punkt ist entscheidend: Das Projekt **bittet seine Nutzer ausdrücklich**, die
Dateien bei VirusTotal zu prüfen. Eine `.exe`, die dort mit 5–15 Treffern rot leuchtet,
zerstört genau das Vertrauen, um das gebeten wird — bei völlig harmlosem Code.

Ein „transparentes Binary" gibt es nicht. Eine Datei ist entweder ausführbar und für Menschen
unlesbar, oder Quelltext und braucht einen Interpreter. Der Ausweg ist nicht besseres
Packaging, sondern **einen Interpreter zu benutzen, der schon da ist**: PowerShell auf
Windows, bash auf macOS, Fusions Python im Add-in.

## Konsequenzen

- Kein Build-Schritt, keine Signatur, keine Release-Pipeline für Binaries
- Jede Datei bleibt im Editor lesbar — das ist Feature, nicht Kompromiss
- PowerShell-Skripte brauchen `-ExecutionPolicy Bypass` im Starter
- Ein plattformübergreifendes Einzelwerkzeug ist damit nicht möglich; Windows und macOS
  bekommen getrennte Skripte
