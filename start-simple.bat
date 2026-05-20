@echo off
chcp 437 >nul
title NexaForge AI Startup

echo.
echo ================================================
echo    NexaForge AI - Hardware Detection System
echo ================================================
echo.

echo Starting system...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)
echo OK: Python ready

REM Check port 8000
netstat -ano | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo WARN: Port 8000 in use, killing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)
echo OK: Port check done

echo.
echo ================================================
echo.
echo Starting backend...
echo Backend: http://localhost:8000
echo.

start "NexaForge Backend" cmd /k python hardware_server.py

echo Waiting for backend...
timeout /t 3 >nul

curl -s http://localhost:8000/api/snapshot >nul 2>&1
if errorlevel 1 (
    echo ERROR: Backend failed to start
    pause
    exit /b 1
)
echo OK: Backend started

echo.
echo ================================================
echo.
echo Starting frontend...
echo Frontend: http://localhost:5173
echo.

cd frontend
start "NexaForge Frontend" cmd /k npm run dev
cd ..

echo Waiting for frontend...
timeout /t 5 >nul

echo.
echo ================================================
echo.
echo Opening browser...
echo.

start http://localhost:5173

echo.
echo ================================================
echo           SYSTEM STARTED SUCCESSFULLY
echo ================================================
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo ================================================
echo.
echo Tip: Close command windows to stop services.
echo.
pause