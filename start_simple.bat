@echo off

REM ==============================================================================
REM HAK-GAL Suite - SIMPLIFIED LAUNCHER (Problem-Free Version)
REM ==============================================================================

title HAK-GAL Suite Launcher v3.2 SIMPLIFIED
color 0A

REM Wechsle ins Batch-Verzeichnis
cd /d "%~dp0"

cls
echo.
echo ================================================================
echo           HAK-GAL Suite - Simplified Launcher v3.2           
echo ================================================================
echo     Wolfram Alpha + Multi-LLM + RAG Pipeline               
echo     Vereinfachte Version ohne komplexe Scripting-Features    
echo ================================================================
echo.
echo Aktuelles Verzeichnis: %CD%
echo.

REM Basis-Variablen
set CONSOLE_SYSTEM=backend\main.py
set WEB_API=api.py
set STARTUP_DEBUG=test_startup_debug.py

:MAIN_MENU
echo Verfuegbare Optionen:
echo.
echo    [1] Konsolen-System starten
echo    [2] Web-Interface starten  
echo    [3] Startup-Diagnose
echo    [4] Automatisches Setup
echo    [5] System-Status
echo    [6] Orchestrator V5 Test (NEU)
echo    [0] Beenden
echo.
set /p choice="Waehlen Sie eine Option (0-6): "

if "%choice%"=="1" goto START_CONSOLE
if "%choice%"=="2" goto START_WEB
if "%choice%"=="3" goto RUN_DIAGNOSIS
if "%choice%"=="4" goto RUN_SETUP
if "%choice%"=="5" goto CHECK_STATUS
if "%choice%"=="6" goto TEST_ORCHESTRATOR
if "%choice%"=="0" goto EXIT
    
    echo Ungueltige Auswahl. Bitte waehlen Sie 0-6.
timeout /t 2 /nobreak >nul
goto MAIN_MENU

:START_CONSOLE
cls
echo ================================================================
echo          Starte HAK-GAL Konsolen-System
echo ================================================================
echo.

if not exist "%CONSOLE_SYSTEM%" (
    echo FEHLER: Konsolen-System nicht gefunden!
    echo Datei fehlt: %CD%\%CONSOLE_SYSTEM%
    echo.
    echo Fuehren Sie Setup aus (Option 4) oder Diagnose (Option 3)
    pause
    goto MAIN_MENU
)

echo Teste Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python nicht gefunden!
    echo Installieren Sie Python und fuegen Sie es zum PATH hinzu.
    pause
    goto MAIN_MENU
)

echo Teste Backend-Import...
python -c "from backend.services import KAssistant" 2>nul
if errorlevel 1 (
    echo FEHLER: Backend-Import fehlgeschlagen!
    echo Fuehren Sie Setup aus (Option 4) oder Diagnose (Option 3)
    pause
    goto MAIN_MENU
)

echo.
echo Starte Konsolen-System...
echo Verwenden Sie 'help' fuer verfuegbare Befehle.
echo.
python "%CONSOLE_SYSTEM%"

echo.
echo Konsolen-System beendet.
pause
goto MAIN_MENU

:START_WEB
cls
echo ================================================================
echo              Starte HAK-GAL Web-Interface
echo ================================================================
echo.

if not exist "%WEB_API%" (
    echo FEHLER: Web-API nicht gefunden!
    echo Datei fehlt: %CD%\%WEB_API%
    pause
    goto MAIN_MENU
)

echo Teste Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python nicht gefunden!
    pause
    goto MAIN_MENU
)

echo Teste Flask...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask nicht gefunden. Installiere...
    pip install flask flask-cors
)

echo.
echo Starte Backend-Server...
echo Backend-URL: http://localhost:5001
echo.
start "HAK-GAL Backend" cmd /k "cd /d "%CD%" && python %WEB_API%"

echo Warte 10 Sekunden auf Backend-Start...
timeout /t 10 /nobreak >nul

if exist "frontend" (
    echo.
    echo Teste Node.js...
    node --version >nul 2>&1
    if errorlevel 1 (
        echo Node.js nicht gefunden. Nur Backend verfuegbar.
        echo Backend-URL: http://localhost:5001
    ) else (
        echo Starte Frontend...
        cd frontend
        if not exist "node_modules" (
            echo Installiere Frontend-Dependencies...
            npm install
        )
        start "HAK-GAL Frontend" cmd /k "npm run dev"
        cd ..
        
        echo.
        echo Frontend-URL: http://localhost:3000
        timeout /t 15 /nobreak >nul
        start http://localhost:3000
    )
) else (
    echo Frontend-Verzeichnis nicht gefunden.
    echo Nur Backend verfuegbar: http://localhost:5001
)

echo.
echo Web-Interface gestartet!
pause
goto MAIN_MENU

:RUN_DIAGNOSIS
cls
echo ================================================================
echo              Startup-Diagnose
echo ================================================================
echo.

if exist "%STARTUP_DEBUG%" (
    echo Fuehre Diagnose aus...
    python "%STARTUP_DEBUG%"
) else (
    echo Diagnose-Script nicht gefunden.
    echo Fuehre Basis-Diagnose aus...
    echo.
    
    echo Python-Version:
    python --version
    
    echo.
    echo Teste kritische Imports:
    python -c "import z3; print('z3-solver: OK')" 2>nul || echo "z3-solver: FEHLER"
    python -c "import lark; print('lark: OK')" 2>nul || echo "lark: FEHLER"  
    python -c "import flask; print('flask: OK')" 2>nul || echo "flask: FEHLER"
    python -c "from backend.services import KAssistant; print('Backend: OK')" 2>nul || echo "Backend: FEHLER"
    
    echo.
    echo Teste Dateien:
    if exist "%CONSOLE_SYSTEM%" (echo Konsolen-System: OK) else (echo Konsolen-System: FEHLER)
    if exist "%WEB_API%" (echo Web-API: OK) else (echo Web-API: FEHLER)
    if exist "requirements.txt" (echo requirements.txt: OK) else (echo requirements.txt: FEHLER)
)

echo.
pause
goto MAIN_MENU

:RUN_SETUP
cls
echo ================================================================
echo                 Automatisches Setup
echo ================================================================
echo.

echo Teste Python...
python --version 2>nul
if errorlevel 1 (
    echo FEHLER: Python nicht gefunden!
    echo Installieren Sie Python 3.8+ von https://python.org
    pause
    goto MAIN_MENU
)

echo.
echo Installiere Python-Dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Warnung: Einige Pakete konnten nicht installiert werden.
        echo Versuchen Sie: pip install flask z3-solver lark openai
    )
) else (
    echo requirements.txt nicht gefunden.
    echo Installiere Basis-Pakete...
    pip install flask flask-cors z3-solver lark openai python-dotenv
)

echo.
echo Setup .env Datei...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo .env Datei erstellt aus Vorlage.
    ) else (
        echo Erstelle minimale .env Datei...
        echo # HAK-GAL Suite Konfiguration > .env
        echo DEEPSEEK_API_KEY=your_api_key_here >> .env
        echo WOLFRAM_APP_ID=your_app_id_here >> .env
        echo .env Datei erstellt.
    )
)

echo.
echo Setup Frontend (optional)...
if exist "frontend" (
    node --version >nul 2>&1
    if not errorlevel 1 (
        cd frontend
        if not exist "node_modules" (
            echo Installiere Frontend-Dependencies...
            npm install
        )
        cd ..
        echo Frontend-Dependencies installiert.
    ) else (
        echo Node.js nicht gefunden - Frontend uebersprungen.
    )
)

echo.
echo Setup abgeschlossen!
pause
goto MAIN_MENU

:CHECK_STATUS
cls
echo ================================================================
echo                   System-Status
echo ================================================================
echo.

echo Python-Installation:
python --version 2>nul && echo "   OK" || echo "   FEHLER"

echo.
echo Python-Packages:
python -c "import z3; print('   z3-solver: OK')" 2>nul || echo "   z3-solver: FEHLER"
python -c "import lark; print('   lark: OK')" 2>nul || echo "   lark: FEHLER"
python -c "import flask; print('   flask: OK')" 2>nul || echo "   flask: FEHLER"
python -c "from backend.services import KAssistant; print('   Backend: OK')" 2>nul || echo "   Backend: FEHLER"

echo.
echo System-Dateien:
if exist "%CONSOLE_SYSTEM%" (echo "   Konsolen-System: OK") else (echo "   Konsolen-System: FEHLER")
if exist "%WEB_API%" (echo "   Web-API: OK") else (echo "   Web-API: FEHLER")
if exist ".env" (echo "   .env: OK") else (echo "   .env: FEHLER")

echo.
echo Frontend:
if exist "frontend" (echo "   Frontend-Verzeichnis: OK") else (echo "   Frontend-Verzeichnis: FEHLER")
node --version >nul 2>&1 && echo "   Node.js: OK" || echo "   Node.js: FEHLER"

echo.
pause
goto MAIN_MENU

:TEST_ORCHESTRATOR
cls
echo ================================================================
echo           Teste HAK-GAL Orchestrator V5
echo ================================================================
echo.

echo Schritt 1: Pruefe Orchestrator V5 Integration...
echo.

REM Teste imports mit Fehlerbehandlung
if exist test_imports.py (
    echo Starte Import-Test...
    python test_imports.py
    if errorlevel 1 (
        echo.
        echo FEHLER: Import-Test fehlgeschlagen!
        echo.
        echo Moegliche Loesungen:
        echo 1. Fuehren Sie Option 4 ^(Setup^) aus
        echo 2. Installieren Sie fehlende Pakete:
        echo    pip install sentence-transformers faiss-cpu prometheus-client cachetools
        echo.
        pause
        goto MAIN_MENU
    )
) else (
    echo WARNUNG: test_imports.py nicht gefunden
    echo Fahre trotzdem fort...
)

echo.
echo Schritt 2: Starte Orchestrator V5 Demo...
echo.

REM Teste ob Orchestrator-Datei existiert
if not exist tools\hak_gal_orchestrator5.py (
    echo FEHLER: tools\hak_gal_orchestrator5.py nicht gefunden!
    pause
    goto MAIN_MENU
)

echo Starte Orchestrator mit korrekten Pfaden...
echo Druecken Sie Ctrl+C zum Beenden
echo.

REM Nutze die Demo-Version oder den Launcher
if exist orchestrator_v5_demo.py (
    python orchestrator_v5_demo.py
) else if exist tools\hak_gal_orchestrator5.py (
    python tools\hak_gal_orchestrator5.py
) else (
    echo FEHLER: Keine Orchestrator-Datei gefunden!
    echo Verwende Diagnose-Tool: orchestrator_v5_diagnose.bat
)

echo.
echo Orchestrator V5 Test beendet.
pause
goto MAIN_MENU

:EXIT
cls
echo.
echo ================================================================
echo        Vielen Dank fuer die Nutzung der HAK-GAL Suite!        
echo ================================================================
echo          Konsolen-Version: python backend\main.py             
echo          Web-Interface: http://localhost:3000                 
echo          Orchestrator V5: Option 6 im Hauptmenue             
echo ================================================================
echo.
timeout /t 3 /nobreak >nul
exit /b 0
