<#
NexaForge AI - Hardware Detection System
One-click Startup Script
#>

Write-Host "`n═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "                     NexaForge AI - Hardware Detection System" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "Starting complete system..." -ForegroundColor Yellow

# Check Python
Write-Host "Checking Python..." -NoNewline
try {
    python --version | Out-Null
    Write-Host " OK" -ForegroundColor Green
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Read-Host 'Press Enter to exit'
    exit 1
}

# Check port 8000
Write-Host "Checking port 8000..." -NoNewline
$portUsed = netstat -ano | Select-String ':8000'
if ($portUsed) {
    Write-Host " occupied, terminating..." -ForegroundColor Yellow
    $pid = ($portUsed | Select-Object -First 1).Line -split '\s+' | Select-Object -Last 1
    taskkill /F /PID $pid | Out-Null
    Start-Sleep -Seconds 2
}
Write-Host " OK" -ForegroundColor Green

Write-Host "`n═══════════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Start backend server
Write-Host "Starting backend server..." -ForegroundColor Yellow
Write-Host "   Backend: http://localhost:8000`n"
Start-Process -FilePath 'cmd.exe' -ArgumentList '/k python hardware_server.py' -WindowStyle Normal

# Wait for backend to start
Write-Host "Waiting for backend..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Check if backend started successfully
Write-Host "Checking backend..." -NoNewline
try {
    Invoke-WebRequest -Uri 'http://localhost:8000/api/snapshot' -UseBasicParsing -TimeoutSec 5 | Out-Null
    Write-Host " OK" -ForegroundColor Green
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Read-Host 'Press Enter to exit'
    exit 1
}

Write-Host "`n═══════════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Start frontend development server
Write-Host "Starting frontend server..." -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:5173`n"
Set-Location frontend
Start-Process -FilePath 'cmd.exe' -ArgumentList '/k npm run dev' -WindowStyle Normal
Set-Location ..

# Wait for frontend to start
Write-Host "Waiting for frontend..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`n═══════════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Open browser automatically
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Process 'http://localhost:5173'

Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "                         System Started!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "`n                    Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "                    Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "                    API Docs: http://localhost:8000/docs`n" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "Tip: Closing this window will not stop services." -ForegroundColor Gray
Write-Host "     To stop, close the respective command windows.`n" -ForegroundColor Gray

Read-Host 'Press Enter to continue'