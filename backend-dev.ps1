# Xiakedao local launcher
# Starts the unified web service

param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: .\backend-dev.ps1" -ForegroundColor Cyan
    Write-Host "Start the unified web service (frontend + FastAPI)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Requirements:" -ForegroundColor Yellow
    Write-Host "  - Python 3.10+ installed" -ForegroundColor Gray
    Write-Host "  - Python deps installed (pip install -e .)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Web:  http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
    exit 0
}

$pythonCmd = "python"
if (Test-Path ".venv\Scripts\python.exe") {
    $pythonCmd = (Resolve-Path ".venv\Scripts\python.exe").Path
}

try {
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Error "Python is not available in PATH or .venv\Scripts\python.exe is invalid."
    exit 1
}

if (-not (Test-Path "src")) {
    Write-Error "src directory not found."
    exit 1
}

$repoRoot = (Resolve-Path ".").Path
$repoName = Split-Path $repoRoot -Leaf
if (-not $env:XIAGEDAO_RUNTIME_ROOT) {
    $repoParent = Split-Path $repoRoot -Parent
    $env:XIAGEDAO_RUNTIME_ROOT = Join-Path $repoParent "$repoName-runtime"
}
New-Item -ItemType Directory -Force -Path $env:XIAGEDAO_RUNTIME_ROOT | Out-Null

$webHost = if ($env:XIAGEDAO_HOST -and $env:XIAGEDAO_HOST -ne "0.0.0.0") { $env:XIAGEDAO_HOST } else { "127.0.0.1" }
$webPort = if ($env:XIAGEDAO_PORT) { $env:XIAGEDAO_PORT } else { "8000" }
$frontendDist = if ($env:XIAGEDAO_FRONTEND_DIST) { $env:XIAGEDAO_FRONTEND_DIST } else { "frontend\dist" }

if (-not (Test-Path $frontendDist)) {
    if ($env:XIAGEDAO_FRONTEND_DIST) {
        Write-Error "Configured frontend dist not found: $frontendDist"
        Write-Host "Set XIAGEDAO_FRONTEND_DIST to a valid path, or unset it to use frontend\dist." -ForegroundColor Yellow
        exit 1
    }

    Write-Host "frontend/dist not found. Building frontend..." -ForegroundColor Cyan
    if (-not (Test-Path "frontend\node_modules")) {
        Write-Error "frontend/node_modules not found. Run npm install in frontend first."
        exit 1
    }

    Push-Location frontend
    npm run build
    $buildExit = $LASTEXITCODE
    Pop-Location

    if ($buildExit -ne 0) {
        Write-Error "Frontend build failed."
        exit $buildExit
    }
}

Write-Host "Starting unified web service..." -ForegroundColor Cyan
Write-Host "Web:  http://$webHost`:$webPort" -ForegroundColor Green
Write-Host "Docs: http://$webHost`:$webPort/docs" -ForegroundColor Green
Write-Host "Runtime root: $env:XIAGEDAO_RUNTIME_ROOT" -ForegroundColor Gray
Write-Host ""
Write-Host "Local and Tailscale now share the same entry." -ForegroundColor Yellow
Write-Host ""

& $pythonCmd -m src.main
