# ADR-0004 — Der Validator repariert nicht selbsttätig

**Status:** ✅ angenommen · **Datum:** 2026-07-25

## Kontext

Beim Review im Juli 2026 kam der Vorschlag, dem Validator einen `--fix`-Modus zu geben:
`TapDrill` automatisch auf `MinorDia` setzen, doppelte Leerzeichen entfernen, kollidierende
`SortOrder` nach oben schieben. Alles davon ist trivial umsetzbar und würde Arbeit sparen.

## Entscheidung

**Nein.** Der Validator liest, prüft, erklärt und schlägt vor. Er schreibt nicht.

Ein `--suggest`-Modus, der die *vorgeschlagene* Korrektur auf der Konsole ausgibt, ist
erlaubt und erwünscht. Der Nutzer überträgt sie selbst.

## Begründung

Der Schadensfall ist asymmetrisch. Eine fehlerhafte XML im ThreadData-Ordner lässt nicht nur
das eigene Gewinde verschwinden — sie kann **Fusions komplette Gewindeliste** unbrauchbar
machen, Standardgewinde eingeschlossen. Genau das steht hinter mehreren offenen Issues bei
ThreadKeeper.

Dagegen steht als Nutzen: ein paar Minuten gesparte Handarbeit für eine Handvoll Leute, die
neue Gewinde beitragen.

Dazu kommt ein zweiter Punkt: Ein Auto-Fix, der `SortOrder` verschiebt oder `TapDrill`
angleicht, **verdeckt die eigentliche Frage** — nämlich ob die Datei insgesamt durchdacht
ist. Wer seine Zahlen selbst korrigiert, schaut sie noch einmal an. Wer `--fix` laufen lässt,
nicht.

## Konsequenzen

- Beitragende haben etwas mehr Handarbeit
- Dafür bleibt jede Änderung an Gewindedaten eine bewusste Entscheidung mit Diff
- Fehlermeldungen müssen dafür **umso besser** sein: nicht „ungültig", sondern was falsch
  ist, warum, und welcher Wert stattdessen plausibel wäre
