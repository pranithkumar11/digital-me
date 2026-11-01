@echo off
setlocal enabledelayedexpansion

title DIGITAL ME // PRANITH KUMAR DUPUGUNTLA
color 0B

echo ===============================================================================
echo                DIGITAL ME - PERSONAL AI DIGITAL TWIN                         
echo                Pranith Kumar Dupuguntla ^| Data Analyst and AI                  
echo ===============================================================================
echo.

:: Move to script directory
cd /d "%~dp0"

:: 1. Check Python installation
echo [*] Checking Python runtime...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] ERROR: Python is not detected in your system PATH.
    echo     Please install Python 3.10+ from https://www.python.org/ and check "Add to PATH".
    pause
    exit /b 1
)
python --version

:: 2. Check virtual environment or install dependencies if missing
echo.
echo [*] Verifying core packages...
python -c "import flask, flask_cors, chromadb, edge_tts" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [*] Installing missing Python requirements from requirements.txt...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Warning: Encountered package installation warnings. Proceeding...
    )
) else (
    echo [OK] Core packages verified.
)

:: 3. Check Ollama daemon status
echo.
echo [*] Checking Local Ollama Inference Runner (Llama 3)...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Local Ollama daemon is ACTIVE.
) else (
    echo [i] Ollama is not currently running on http://localhost:11434.
    echo     (Note: Digital Me will use its built-in first-person Persona RAG fallback.
    echo      To enable local Llama 3 inference, run 'ollama run llama3' in a new terminal.)
)

:: 4. Launch Digital Me Backend and open browser
echo.
echo ===============================================================================
echo  Launching Digital Me Server at: http://localhost:5000
echo  Press Ctrl+C at any time to shut down the server.
echo ===============================================================================
echo.

:: Launch browser in background after brief delay
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

:: Start Flask Backend
cd backend
python app.py

pause
