@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0.."

echo ================================================
echo Xiakedao - Beta Health Check
echo ================================================
echo.

set "errors=0"

:: Ensure Tailscale is reachable even if installer path is not in PATH yet
where tailscale >nul 2>&1
if errorlevel 1 (
    if exist "%ProgramFiles%\Tailscale\tailscale.exe" (
        set "PATH=%ProgramFiles%\Tailscale;%PATH%"
    ) else if exist "%ProgramFiles(x86)%\Tailscale\tailscale.exe" (
        set "PATH=%ProgramFiles(x86)%\Tailscale;%PATH%"
    )
)

:: Check backend API
echo [CHECK] Backend API...
curl --noproxy "*" -s http://127.0.0.1:8000/health >nul 2>&1
if not errorlevel 1 (
    echo [OK] Backend API is responding
) else (
    echo [FAIL] Backend API not responding
    set /a errors+=1
)

:: Check frontend
echo [CHECK] Frontend static files...
curl --noproxy "*" -s -o nul -w "%%{http_code}" http://127.0.0.1:8000/ 2>nul | findstr "200" >nul
if not errorlevel 1 (
    echo [OK] Frontend is accessible
) else (
    echo [FAIL] Frontend not accessible
    set /a errors+=1
)

:: Check listener exposure for Tailscale
echo [CHECK] Port 8000 exposure...
call :capture_listener
if not defined listener_pid (
    echo [FAIL] No listening process found on port 8000
    set /a errors+=1
) else (
    call :capture_process_cmdline !listener_pid!
    call :listener_is_public
    if not errorlevel 1 (
        echo [OK] Port 8000 is reachable beyond localhost
    ) else (
        echo [FAIL] Port 8000 is listening on localhost only
        if defined process_cmdline (
            echo [INFO] Command:
            echo(!process_cmdline!
        )
        set /a errors+=1
    )
)

:: Check Tailscale IP
echo.
echo [INFO] Tailscale IP:
for /f "tokens=*" %%i in ('tailscale ip -4 2^>nul') do (
    echo        %%i
)

echo.
if "%errors%"=="0" (
    echo ================================================
    echo [RESULT] All checks passed!
    echo ================================================
    exit /b 0
) else (
    echo ================================================
    echo [RESULT] %errors% checks failed.
    echo ================================================
    echo.
    echo Run scripts\beta-start.bat to start the server.
    exit /b 1
)

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
