@echo off
REM CareerLaunch AI Backend - One-Click Launcher
REM Just double-click this file to start the API server!

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo =====================================
echo CareerLaunch AI Backend - Launcher
echo =====================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python is installed and in your PATH
        pause
        exit /b 1
    )
)

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

if not exist "venv\Lib\site-packages\fastapi" (
    echo [3/3] Installing dependencies...
    pip install -q fastapi uvicorn
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo =====================================
echo ✓ Starting API Server...
echo =====================================
echo.
echo 📚 Documentation: http://localhost:8000/docs
echo 🏥 Health Check: http://localhost:8000/api/v1/health
echo.
echo Press CTRL+C to stop the server
echo.

REM Run the server
uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000

pause
