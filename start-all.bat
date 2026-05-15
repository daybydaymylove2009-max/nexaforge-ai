@echo off
chcp 65001 >nul
title 智核万炼 NexaForge AI - 一键启动

echo.
echo ╔═══════════════════════════════════════════════════════════════════════╗
echo ║                                                                       ║
echo ║              智核万炼® NexaForge AI - 智能硬件检测系统                 ║
echo ║                                                                       ║
echo ║                    开箱即用，智核万炼                                 ║
echo ║                                                                       ║
echo ╚═══════════════════════════════════════════════════════════════════════╝
echo.

echo 🎯 正在启动完整系统（后端 + 前端 + 浏览器）...
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)
echo ✅ Python已就绪
echo.

REM 检查端口8000
netstat -ano | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ 端口8000已被占用，正在终止进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)
echo ✅ 端口检查完成
echo.

echo ════════════════════════════════════════════════════════════════════════
echo.
echo 🚀 正在启动后端服务器...
echo    后端地址: http://localhost:8000
echo.

REM 启动后端服务器
start "NexaForge Backend" cmd /k "python hardware_server.py"

REM 等待后端启动
echo ⏳ 等待后端服务器启动...
timeout /t 3 >nul

REM 检查后端是否启动成功
curl -s http://localhost:8000/api/snapshot >nul 2>&1
if errorlevel 1 (
    echo ❌ 后端服务器启动失败
    pause
    exit /b 1
)
echo ✅ 后端服务器启动成功
echo.

echo ════════════════════════════════════════════════════════════════════════
echo.
echo 🎨 正在启动前端开发服务器...
echo    前端地址: http://localhost:5173
echo.

REM 启动前端开发服务器
cd frontend
start "NexaForge Frontend" cmd /k "npm run dev"
cd ..

REM 等待前端启动
echo ⏳ 等待前端服务器启动...
timeout /t 5 >nul

echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 正在打开浏览器...
echo.

REM 自动打开浏览器
start http://localhost:5173

echo.
echo ╔═══════════════════════════════════════════════════════════════════════╗
echo ║                                                                       ║
echo ║                    🎉 系统启动完成!                                   ║
echo ║                                                                       ║
echo ║                    前端界面: http://localhost:5173                    ║
echo ║                    后端服务: http://localhost:8000                    ║
echo ║                    API文档:  http://localhost:8000/docs               ║
echo ║                                                                       ║
echo ╚═══════════════════════════════════════════════════════════════════════╝
echo.
echo 💡 提示: 关闭此窗口不会停止服务，如需停止请关闭对应的命令行窗口
echo.
pause
