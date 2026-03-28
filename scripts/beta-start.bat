@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0.."
title Xiakedao Beta Server

echo ================================================
echo Xiakedao - Tailscale Beta Deployment
echo ================================================
echo.

:: Ensure Tailscale is reachable even if installer path is not in PATH yet
where tailscale >nul 2>&1
if errorlevel 1 (
    if exist "%ProgramFiles%\Tailscale\tailscale.exe" (
        set "PATH=%ProgramFiles%\Tailscale;%PATH%"
    ) else if exist "%ProgramFiles(x86)%\Tailscale\tailscale.exe" (
        set "PATH=%ProgramFiles(x86)%\Tailscale;%PATH%"
    )
)

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH.
    echo Install Python 3.10+ and try again.
    pause
    exit /b 1
)

:: Check frontend dist exists
if not exist "frontend\dist" (
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
    set "build_exit=!errorlevel!"
    popd
    
    if not "!build_exit!"=="0" (
        echo [ERROR] Frontend build failed.
        pause
        exit /b 1
    )
    echo [OK] Frontend built successfully.
    echo.
)

:: Check Tailscale
tailscale version >nul 2>&1
if errorlevel 1 (
    echo [WARN] Tailscale not found. Access will be localhost only.
    echo.
)

echo [INFO] Starting server...
echo.

:: Load .env file if it exists
if exist ".env" (
    echo [INFO] Loading .env configuration...
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "line=%%A"
        if not "!line:~0,1!"=="#" (
            if not "%%A"=="" (
                set "%%A=%%B"
            )
        )
    )
)

:: Set environment for beta testing (non-strict mode if no consumer config)
if not defined XIAGEDAO_CONSUMER_ROOT (
    echo [INFO] XIAGEDAO_CONSUMER_ROOT not set, using non-strict mode
    set XIAGEDAO_STRICT_MODE=false
)

call :capture_listener
if defined listener_pid (
    call :capture_process_cmdline !listener_pid!
    echo !process_cmdline! | find /I "src.main" >nul
    if errorlevel 1 (
        echo [ERROR] Port 8000 is already in use by another process.
        echo [INFO] Listener PID: !listener_pid!
        if defined process_cmdline (
            echo [INFO] Command:
            echo(!process_cmdline!
        )
        echo [TIP] Stop the existing backend on port 8000 before starting Tailscale mode.
        pause
        exit /b 1
    ) else (
        call :listener_is_public
        if not errorlevel 1 (
            echo [INFO] Unified web server is already running on port 8000.
            goto server_ready
        )
        echo [ERROR] Port 8000 is occupied by a localhost-only Xiakedao process.
        echo [INFO] Listener PID: !listener_pid!
        if defined process_cmdline (
            echo [INFO] Command:
            echo(!process_cmdline!
        )
        echo [TIP] Stop the existing process and rerun this script to expose the site to Tailscale.
        pause
        exit /b 1
    )
)

:: Start server in background window
start "Xiakedao Beta Server" cmd /k "python -m src.main"

:: Wait for server to be ready
echo [INFO] Waiting for server to start...
set "retry=0"
set "max_retries=30"

:wait_loop
timeout /t 1 /nobreak >nul
curl --noproxy "*" -s http://127.0.0.1:8000/health >nul 2>&1
if errorlevel 1 goto wait_retry
call :listener_is_public
if not errorlevel 1 goto server_ready

:wait_retry
set /a retry+=1
if %retry% geq %max_retries% goto timeout_error
echo   ... waiting %retry%/%max_retries%
goto wait_loop

:server_ready
echo.
echo ================================================
echo [OK] Server is running!
echo ================================================
echo.
echo [INFO] Local access:  http://localhost:8000
echo [INFO] API docs:      http://localhost:8000/docs
echo.

:: Try to get Tailscale IP
for /f "tokens=*" %%i in ('tailscale ip -4 2^>nul') do (
    set "ts_ip=%%i"
)
if defined ts_ip (
    echo [INFO] Tailscale:    http://!ts_ip!:8000
    echo.
    echo Share this URL with your team!
) else (
    echo [TIP] Run 'tailscale ip -4' to get your Tailscale IP
)
echo.
echo To stop: run scripts\beta-stop.bat
echo ================================================
echo.
pause
exit /b 0

:timeout_error
echo.
echo [ERROR] Server did not expose port 8000 for Tailscale within %max_retries% seconds.
call :capture_listener
if defined listener_pid (
    call :capture_process_cmdline !listener_pid!
    echo [INFO] Current listener PID: !listener_pid!
    if defined process_cmdline (
        echo [INFO] Command:
        echo(!process_cmdline!
    )
)
echo [TIP] If port 8000 is occupied by `python -m src.main`, stop it first and rerun this script.
pause
exit /b 1

:capture_listener
set "listener_pid="
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "$c = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess; if ($null -ne $c) { Write-Output $c }"`) do (
    set "listener_pid=%%i"
)
exit /b 0

:capture_process_cmdline
set "process_cmdline="
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "$p = Get-CimInstance Win32_Process -Filter 'ProcessId=%~1' -ErrorAction SilentlyContinue; if ($null -ne $p) { Write-Output $p.CommandLine }"`) do (
    set "process_cmdline=%%i"
)
exit /b 0

:listener_is_public
powershell -NoProfile -Command "$c = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalAddress -ne '127.0.0.1' -and $_.LocalAddress -ne '::1' } | Select-Object -First 1; if ($null -ne $c) { exit 0 } else { exit 1 }" >nul 2>&1
exit /b %errorlevel%
