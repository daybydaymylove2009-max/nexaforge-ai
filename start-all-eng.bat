@echo off
chcp 65001 >nul
title NexaForge AI - One-click Startup

echo.
echo ╔═══════════════════════════════════════════════════════════════════════╗
echo ║                                                                       ║
echo ║                NexaForge AI - Hardware Detection System                ║
echo ║                                                                       ║
echo ║                       Ready to Forge Intelligence                       ║
echo ║                                                                       ║
echo ╚═══════════════════════════════════════════════════════════════════════╝
echo.

echo 🎯 Starting complete system (Backend + Frontend + Browser)...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not installed or not in PATH
    pause
    exit /b 1
)
echo ✅ Python is ready
echo.

REM Check port 8000
netstat -ano | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port 8000 is occupied, terminating process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)
echo ✅ Port check completed
echo.

echo ════════════════════════════════════════════════════════════════════════
echo.
echo 🚀 Starting backend server...
echo    Backend: http://localhost:8000
echo.

REM Start backend server
start "NexaForge Backend" cmd /k "python hardware_server.py"

REM Wait for backend to start
echo ⏳ Waiting for backend server...
timeout /t 3 >nul

REM Check if backend started successfully
curl -s http://localhost:8000/api/snapshot >nul 2>&1
if errorlevel 1 (
    echo ❌ Failed to start backend server
    pause
    exit /b 1
)
echo ✅ Backend server started successfully
echo.

echo ════════════════════════════════════════════════════════════════════════
echo.
echo 🎨 Starting frontend development server...
echo    Frontend: http://localhost:5173
echo.

REM Start frontend development server
cd frontend
start "NexaForge Frontend" cmd /k "npm run dev"
cd ..

REM Wait for frontend to start
echo ⏳ Waiting for frontend server...
timeout /t 5 >nul

echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 Opening browser...
echo.

REM Open browser automatically
start http://localhost:5173

echo.
echo ╔═══════════════════════════════════════════════════════════════════════╗
echo ║                                                                       ║
echo ║                         🎉 System Started!                             ║
echo ║                                                                       ║
echo ║                    Frontend: http://localhost:5173                    ║
echo ║                    Backend:  http://localhost:8000                    ║
echo ║                    API Docs: http://localhost:8000/docs               ║
echo ║                                                                       ║
echo ╚═══════════════════════════════════════════════════════════════════════╝
echo.
echo 💡 Tip: Closing this window will not stop the services.
echo        To stop, close the respective command windows.
echo.
pause