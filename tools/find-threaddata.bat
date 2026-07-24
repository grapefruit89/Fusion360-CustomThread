@echo off
setlocal enabledelayedexpansion
title Fusion 360 - Smart Thread Finder
color 0b

:START
cls

echo ===================================================
echo FUSION 360 - LIVE PFAD FINDER (3D-DRUCK)
echo ===================================================
echo.

:: Prüfung: Läuft Fusion 360?
tasklist /FI "IMAGENAME eq Fusion360.exe" 2>NUL | find /I "Fusion360.exe" >NUL
if "%ERRORLEVEL%"=="1" (
    echo [!] Fusion 360 wurde nicht gefunden.
    echo.
    echo BITTE STARTEN: Fusion 360 muss im Hintergrund laufen,
    echo damit ich den exakten Pfad finden kann.
    echo.
    echo Druecke eine Taste zum erneuten Pruefen...
    pause >nul
    goto START
)

echo [+] Fusion 360 Instanz erkannt!
echo [*] Suche den korrekten Pfad... bitte warten...
timeout /t 2 >nul

:: Pfad ermitteln
for /f "usebackq delims=" %%a in (`powershell -command "(Join-Path (Split-Path (Get-Process Fusion360).Path) 'Fusion\Server\Fusion\Configuration\ThreadData') "`) do set "FPATH=%%a"

if not exist "!FPATH!" (
    echo [!] FEHLER: Der ThreadData-Ordner wurde nicht gefunden.
    pause
    exit
)

cd /d "!FPATH!"

echo.
echo [ERFOLG] Pfad erfolgreich ermittelt!
echo.
echo Der Ordner wurde im Explorer geoeffnet und die
echo Kommandozeile wurde dorthin navigiert.
echo.

:: Explorer öffnen
explorer .

echo Aktueller Inhalt des ThreadData-Ordners:
echo ---------------------------------------------------
tree /f
echo ---------------------------------------------------
echo.
echo KOPIEREN: Schiebe jetzt deine neuen XML-Dateien
echo in den geoeffneten Explorer-Ordner.
echo.
echo WICHTIG: Danach Fusion 360 neu starten!
echo.
pause