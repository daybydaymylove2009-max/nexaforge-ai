# NexaForge AI Auto Starter
Write-Host "Initializing NexaForge environment..." -ForegroundColor Cyan

# 1. Clear port 8000
$port = 8000
$connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($connection) {
    Write-Host "Port $port is occupied. Killing process (PID: $($connection.OwningProcess[0]))..." -ForegroundColor Yellow
    Stop-Process -Id $connection.OwningProcess[0] -Force
    Start-Sleep -Seconds 1
}

# 2. Start Backend
Write-Host "Starting Backend Service..." -ForegroundColor Cyan
python -m backend.main
