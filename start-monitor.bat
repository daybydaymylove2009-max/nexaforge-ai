@echo off
chcp 65001 >nul
title 智核万炼 NexaForge AI - 硬件监控服务
color 0A

echo.
echo ╔═══════════════════════════════════════════════════════════════════════╗
echo ║                                                                       ║
echo ║              智核万炼® NexaForge AI - 硬件实时监控服务                ║
echo ║                                                                       ║
echo ║                    开箱即用，智核万炼                                 ║
echo ║                                                                       ║
echo ╚═══════════════════════════════════════════════════════════════════════╝
echo.

echo 📊 正在启动硬件监控服务...
echo.
echo 🌐 监控界面地址: http://localhost:8000
echo 🔌 API文档地址: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

python hardware_server.py

echo.
echo 服务已停止
pause
