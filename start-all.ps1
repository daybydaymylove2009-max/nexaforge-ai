# 智核万炼 NexaForge AI - 一键启动脚本
# 功能：启动后端服务器、前端开发服务器、自动打开浏览器

param(
    [switch]$Backend,      # 只启动后端
    [switch]$Frontend,     # 只启动前端
    [switch]$Production,   # 生产模式（构建并启动）
    [string]$Port = "5173" # 前端端口，默认5173
)

# 颜色定义
$Colors = @{
    Title = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "White"
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Start-Backend {
    Write-ColorOutput "`n🚀 启动后端服务器..." $Colors.Info
    Write-ColorOutput "   后端地址: http://localhost:8000" $Colors.Info

    # 检查端口8000是否被占用
    $process = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($process) {
        $pid = ($process | Select-Object -First 1).OwningProcess
        Write-ColorOutput "   ⚠️ 端口8000已被占用，正在终止进程(PID: $pid)..." $Colors.Warning
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }

    # 启动后端
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python hardware_server.py" -WindowStyle Normal
    Start-Sleep -Seconds 2

    # 检查后端是否启动成功
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/snapshot" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "   ✅ 后端服务器启动成功!" $Colors.Success
            return $true
        }
    } catch {
        Write-ColorOutput "   ❌ 后端服务器启动失败: $_" $Colors.Error
        return $false
    }
}

function Start-Frontend {
    param([string]$Port = "5173")

    Write-ColorOutput "`n🎨 启动前端开发服务器..." $Colors.Info
    Write-ColorOutput "   前端地址: http://localhost:$Port" $Colors.Info

    # 检查端口是否被占用
    $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($process) {
        $pid = ($process | Select-Object -First 1).OwningProcess
        Write-ColorOutput "   ⚠️ 端口$Port已被占用，正在终止进程(PID: $pid)..." $Colors.Warning
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }

    # 启动前端
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev" -WindowStyle Normal
    Start-Sleep -Seconds 3

    # 检查前端是否启动成功
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "   ✅ 前端开发服务器启动成功!" $Colors.Success
            return $true
        }
    } catch {
        Write-ColorOutput "   ❌ 前端开发服务器启动失败: $_" $Colors.Error
        return $false
    }
}

function Start-Production {
    Write-ColorOutput "`n🏭 启动生产模式..." $Colors.Info

    Write-ColorOutput "`n📦 构建前端..." $Colors.Info
    if (Test-Path "$PSScriptRoot\frontend\node_modules") {
        Set-Location "$PSScriptRoot\frontend"
        npm run build
        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "   ❌ 前端构建失败!" $Colors.Error
            return $false
        }
        Write-ColorOutput "   ✅ 前端构建成功!" $Colors.Success
        Set-Location $PSScriptRoot
    } else {
        Write-ColorOutput "   ⚠️ 未安装前端依赖，请先运行: cd frontend; npm install" $Colors.Warning
        return $false
    }

    Write-ColorOutput "`n🚀 启动后端服务器(生产模式)..." $Colors.Info
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python hardware_server.py" -WindowStyle Normal

    Start-Sleep -Seconds 3
    Write-ColorOutput "   ✅ 生产服务器启动成功!" $Colors.Success
    return $true
}

function Open-Browser {
    param([string]$Url = "http://localhost:5173")

    Write-ColorOutput "`n🌐 打开浏览器..." $Colors.Info
    Start-Process $Url
    Write-ColorOutput "   ✅ 浏览器已打开: $Url" $Colors.Success
}

# 主程序
Clear-Host

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                       ║" -ForegroundColor Cyan
Write-Host "║              智核万炼® NexaForge AI - 智能硬件检测系统                 ║" -ForegroundColor Cyan
Write-Host "║                                                                       ║" -ForegroundColor Cyan
Write-Host "║                    开箱即用，智核万炼                                 ║" -ForegroundColor Cyan
Write-Host "║                                                                       ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 检查Python环境
try {
    $pythonVersion = python --version 2>&1
    Write-ColorOutput "🐍 Python版本: $pythonVersion" $Colors.Success
} catch {
    Write-ColorOutput "❌ Python未安装或未添加到PATH" $Colors.Error
    exit 1
}

# 检查Node.js环境
try {
    $nodeVersion = node --version 2>&1
    Write-ColorOutput "📦 Node.js版本: $nodeVersion" $Colors.Success
} catch {
    Write-ColorOutput "⚠️ Node.js未安装，前端功能将不可用" $Colors.Warning
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host "  使用说明:" -ForegroundColor White
Write-Host "    -Full        : 启动完整系统(后端+前端+浏览器) [默认]" -ForegroundColor Gray
Write-Host "    -Backend      : 只启动后端服务器" -ForegroundColor Gray
Write-Host "    -Frontend     : 只启动前端开发服务器" -ForegroundColor Gray
Write-Host "    -Production   : 生产模式(构建+启动)" -ForegroundColor Gray
Write-Host "    -Port <端口>  : 指定前端端口，默认5173" -ForegroundColor Gray
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""

# 根据参数决定启动模式
if ($Production) {
    # 生产模式
    $success = Start-Production
    if ($success) {
        Open-Browser -Url "http://localhost:8000"
    }
} elseif ($Backend) {
    # 只启动后端
    $success = Start-Backend
    if ($success) {
        Write-Host ""
        Write-ColorOutput "═══════════════════════════════════════════════════════════════════════" $Colors.Info
        Write-ColorOutput "  🌐 后端服务已启动!" $Colors.Success
        Write-ColorOutput "     监控界面: http://localhost:8000" $Colors.Info
        Write-ColorOutput "     API文档:  http://localhost:8000/docs" $Colors.Info
        Write-ColorOutput "═══════════════════════════════════════════════════════════════════════" $Colors.Info
        Write-ColorOutput "`n  按 Ctrl+C 停止服务" $Colors.Warning
    }
} elseif ($Frontend) {
    # 只启动前端
    $success = Start-Frontend -Port $Port
    if ($success) {
        Open-Browser -Url "http://localhost:$Port"
    }
} else {
    # 完整模式（默认）
    Write-ColorOutput "🎯 启动完整系统模式" $Colors.Info

    # 1. 启动后端
    $backendSuccess = Start-Backend
    if (-not $backendSuccess) {
        Write-ColorOutput "`n❌ 后端启动失败，请检查错误信息" $Colors.Error
        exit 1
    }

    # 2. 启动前端
    $frontendSuccess = Start-Frontend -Port $Port
    if (-not $frontendSuccess) {
        Write-ColorOutput "`n⚠️ 前端启动失败，后端仍可正常使用" $Colors.Warning
    }

    # 3. 打开浏览器
    if ($frontendSuccess) {
        Start-Sleep -Seconds 2
        Open-Browser -Url "http://localhost:$Port"
    } elseif ($backendSuccess) {
        Start-Sleep -Seconds 2
        Open-Browser -Url "http://localhost:8000"
    }

    Write-Host ""
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════════" $Colors.Success
    Write-ColorOutput "  🎉 系统启动完成!" $Colors.Success
    Write-ColorOutput "" $Colors.Success
    if ($frontendSuccess) {
        Write-ColorOutput "     前端界面: http://localhost:$Port" $Colors.Info
    }
    if ($backendSuccess) {
        Write-ColorOutput "     后端服务: http://localhost:8000" $Colors.Info
        Write-ColorOutput "     API文档:  http://localhost:8000/docs" $Colors.Info
    }
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════════" $Colors.Success
    Write-ColorOutput "`n  按 Enter 退出（或使用 Ctrl+C 停止服务）" $Colors.Warning

    # 等待用户按Enter退出
    Read-Host
}
