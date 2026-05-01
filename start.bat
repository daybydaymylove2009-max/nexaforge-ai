@echo off
chcp 65001 >nul
title 智核万炼 NexaForge AI - 智能训练平台
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                                                                      ║
echo ║              智核万炼® NexaForge AI 智能训练平台                      ║
echo ║                                                                      ║
echo ║                    开箱即用，智核万炼                                 ║
echo ║                                                                      ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

:: 检查Python环境
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python环境正常

:: 检查虚拟环境
if not exist venv (
    echo 🔄 创建虚拟环境...
    python -m venv venv
)

echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat

:: 运行智核万炼
echo.
echo 🚀 启动智核万炼 AI训练平台...
echo.

python nexaforge.py --auto

echo.
echo 按任意键退出...
pause >nul
