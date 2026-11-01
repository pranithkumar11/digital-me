@echo off
setlocal enabledelayedexpansion

title DIGITAL ME // LOCAL DEVELOPMENT ENVIRONMENT
color 0A

echo ===============================================================================
echo            DIGITAL ME - LOCAL DEVELOPMENT RUNNER (AUTO-RELOAD)
echo            Pranith Kumar Dupuguntla ^| Data Analyst and AI
echo ===============================================================================
echo.

:: Move to script directory
cd /d "%~dp0"

:: Set Development Environment Flags
set DEBUG=true
set FLASK_ENV=development
set PYTHONUNBUFFERED=1

:: 1. Check Python installation
echo [*] Checking Python development environment...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] ERROR: Python is not detected in your system PATH.
    pause
    exit /b 1
)
python --version

:: 2. Verify or Install Dependencies
echo.
echo [*] Checking development packages...
python -c "import flask, flask_cors, chromadb, edge_tts" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [*] Installing requirements for local development...
    pip install -r requirements.txt
) else (
    echo [OK] All development packages are active.
)

:: 3. Check Ollama Local Runner
echo.
echo [*] Checking Local Ollama daemon...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Local Ollama is LIVE on http://localhost:11434.
) else (
    echo [i] Ollama is not running. 
    echo     Tip: Run 'ollama run llama3' in another window for local Llama 3 generation.
    echo     (Digital Me will use its built-in First-Person Persona RAG engine).
)

:: 4. Launch in Development Mode with Auto-Reload
echo.
echo ===============================================================================
echo  DEVELOPMENT SERVER STARTING:
echo  - Port: http://localhost:5000
echo  - Debug Mode: ON (Flask live reloads upon saving any backend Python file)
echo  - Browser Cache: DISABLED (Instant CSS/JS frontend hot-refresh)
echo  - Re-Index API: POST http://localhost:5000/api/reindex
echo  Press Ctrl+C to stop the development server.
echo ===============================================================================
echo.

:: Launch browser after brief delay
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

:: Start Flask Backend in Debug / Dev Mode
cd backend
python app.py

pause
