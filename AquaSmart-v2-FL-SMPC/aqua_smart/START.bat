@echo off
title AquaSmart - Intelligent Fish Feeding System
color 0B
cls

echo.
echo  ========================================================
echo    AquaSmart - Intelligent Fish Feeding System
echo    SESAME Engineering School
echo  ========================================================
echo.

cd /d "%~dp0"

:: ── 1. Check Python ──────────────────────────────────────────
echo  [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found. Install from https://www.python.org
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo  Found: %%v

:: ── 2. Install dependencies ──────────────────────────────────
echo.
echo  [2/3] Installing packages...
python -m pip install --upgrade pip --quiet --disable-pip-version-check 2>nul
python -m pip install flask waitress scikit-learn numpy pandas joblib python-dateutil --quiet --disable-pip-version-check
if errorlevel 1 (
    echo  ERROR: pip install failed.
    pause & exit /b 1
)
echo  Packages OK.

:: ── 3. Pre-train demo model ───────────────────────────────────
echo.
echo  [3/3] Preparing ML model...
python scripts\pretrain.py
echo.

:: ── Open browser after 8 s ────────────────────────────────────
start /B cmd /c "ping 127.0.0.1 -n 9 >nul && start http://localhost:8000"

:: ── Start server ─────────────────────────────────────────────
echo  ========================================================
echo    Server:  http://localhost:8000
echo    Browser opens in ~8 seconds.
echo    Press Ctrl+C to stop.
echo  ========================================================
echo.
python run.py

echo.
pause
