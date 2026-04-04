@echo off
REM CareerLaunch AI Backend - Windows Setup Script
REM This script automates the setup process

echo.
echo =====================================
echo CareerLaunch AI Backend - Setup
echo =====================================
echo.

REM Check Python installation
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo.
echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [3/5] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Create environment file
echo [4/5] Creating environment configuration...
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please edit it with your configuration.
) else (
    echo .env file already exists
)

REM Verify installation
echo [5/5] Verifying installation...
python -c "import fastapi; import sqlalchemy; import pydantic; print('✓ All dependencies installed successfully')"
if errorlevel 1 (
    echo ERROR: Dependency verification failed
    pause
    exit /b 1
)

echo.
echo =====================================
echo Setup Complete!
echo =====================================
echo.
echo Next steps:
echo 1. Edit the .env file with your configuration
echo 2. Run: python app/main.py
echo 3. Visit: http://localhost:8000/docs
echo.
echo For Docker setup, run: docker-compose up -d
echo.
pause
