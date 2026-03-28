@echo off
setlocal
cd /d "%~dp0"
title Xiakedao Web

echo ================================================
echo Xiakedao unified web server
echo ================================================
echo.

set "PYTHON_CMD=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_CMD=%CD%\.venv\Scripts\python.exe"

"%PYTHON_CMD%" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not available in PATH.
    echo Install Python 3.10+ and try again.
    pause
    exit /b 1
)

if not exist "src" (
    echo [ERROR] src directory not found.
    pause
    exit /b 1
)

for %%I in ("%CD%") do set "REPO_NAME=%%~nxI"
for %%I in ("%CD%\..") do set "REPO_PARENT=%%~fI"
if not defined XIAGEDAO_RUNTIME_ROOT set "XIAGEDAO_RUNTIME_ROOT=%REPO_PARENT%\%REPO_NAME%-runtime"
if not exist "%XIAGEDAO_RUNTIME_ROOT%" mkdir "%XIAGEDAO_RUNTIME_ROOT%" >nul 2>&1

set "WEB_HOST=127.0.0.1"
if defined XIAGEDAO_HOST if /i not "%XIAGEDAO_HOST%"=="0.0.0.0" set "WEB_HOST=%XIAGEDAO_HOST%"
set "WEB_PORT=8000"
if defined XIAGEDAO_PORT set "WEB_PORT=%XIAGEDAO_PORT%"
set "FRONTEND_DIST=frontend\dist"
if defined XIAGEDAO_FRONTEND_DIST set "FRONTEND_DIST=%XIAGEDAO_FRONTEND_DIST%"

if not exist "%FRONTEND_DIST%" (
    if defined XIAGEDAO_FRONTEND_DIST (
        echo [ERROR] Configured frontend dist not found: %FRONTEND_DIST%
        echo Set XIAGEDAO_FRONTEND_DIST to a valid path, or unset it to use frontend\dist.
        pause
        exit /b 1
    )

    echo [INFO] Frontend dist not found. Building...
    echo.

    if not exist "frontend\node_modules" (
        echo [ERROR] frontend\node_modules not found.
        echo Run: cd frontend ^&^& npm install
        pause
        exit /b 1
    )

    pushd frontend
    call npm run build
    set "build_exit=%errorlevel%"
    popd

    if not "%build_exit%"=="0" (
        echo [ERROR] Frontend build failed.
        pause
        exit /b 1
    )
    echo [OK] Frontend built successfully.
    echo.
)

echo [INFO] Web:  http://%WEB_HOST%:%WEB_PORT%
echo [INFO] Docs: http://%WEB_HOST%:%WEB_PORT%/docs
echo [INFO] Runtime root: %XIAGEDAO_RUNTIME_ROOT%
echo [INFO] Default provider: fake
echo [INFO] Local and Tailscale now share the same entry.
echo.

"%PYTHON_CMD%" -m src.main
set "exit_code=%errorlevel%"

if not "%exit_code%"=="0" (
    echo.
    echo [ERROR] Web server exited with code %exit_code%.
    pause
)

exit /b %exit_code%
