# Xiakedao one-click launcher
# Starts the unified web service and opens the page

param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: .\dev.ps1" -ForegroundColor Cyan
    Write-Host "Start the unified web service and open the page" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Web:  http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
    exit 0
}

if (-not (Test-Path "src")) {
    Write-Error "src directory not found."
    exit 1
}

$webHost = if ($env:XIAGEDAO_HOST -and $env:XIAGEDAO_HOST -ne "0.0.0.0") { $env:XIAGEDAO_HOST } else { "127.0.0.1" }
$webPort = if ($env:XIAGEDAO_PORT) { $env:XIAGEDAO_PORT } else { "8000" }

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Xiakedao one-click web startup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Web:  http://$webHost`:$webPort" -ForegroundColor Green
Write-Host "Docs: http://$webHost`:$webPort/docs" -ForegroundColor Green
Write-Host ""

function Test-WebReady {
    try {
        $health = Invoke-WebRequest -Uri "http://$webHost`:$webPort/health" -UseBasicParsing -TimeoutSec 2
        if ($health.StatusCode -ne 200) {
            return $false
        }

        $root = Invoke-WebRequest -Uri "http://$webHost`:$webPort/" -UseBasicParsing -TimeoutSec 2
        return $root.StatusCode -eq 200
    } catch {
        return $false
    }
}

if (-not (Test-WebReady)) {
    Write-Host "Starting unified web service..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$PWD\backend-dev.ps1" -WindowStyle Normal

    for ($i = 0; $i -lt 45; $i++) {
        Start-Sleep -Seconds 1
        if (Test-WebReady) {
            break
        }
    }
}

if (Test-WebReady) {
    Start-Process "http://$webHost`:$webPort"
    Write-Host ""
    Write-Host "Page opened." -ForegroundColor Green
    Write-Host "Single-service launcher: .\backend-dev.ps1" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Warning "Web page did not become ready within 45 seconds. Check the Xiakedao Web window."
}
