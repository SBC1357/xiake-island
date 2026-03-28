@echo off
setlocal
cd /d "%~dp0"
title Xiakedao Launcher

echo ================================================
echo Xiakedao one-click web startup
echo ================================================
echo.

set "WEB_HOST=127.0.0.1"
if defined XIAGEDAO_HOST if /i not "%XIAGEDAO_HOST%"=="0.0.0.0" set "WEB_HOST=%XIAGEDAO_HOST%"
set "WEB_PORT=8000"
if defined XIAGEDAO_PORT set "WEB_PORT=%XIAGEDAO_PORT%"

echo [INFO] Web:  http://%WEB_HOST%:%WEB_PORT%
echo [INFO] Docs: http://%WEB_HOST%:%WEB_PORT%/docs
echo [INFO] Default provider: fake
echo.

if not exist "backend-dev.bat" (
    echo [ERROR] backend-dev.bat not found.
    pause
    exit /b 1
)

call :is_web_ready
if not errorlevel 1 goto open_browser

echo [START] Launching unified web window...
start "Xiakedao Web" cmd /k call "%~dp0backend-dev.bat"

echo.
echo [WAIT] Waiting for web service to be ready (max 45 seconds)...
set "retry_count=0"
set "max_retries=45"

:wait_loop
timeout /t 1 /nobreak >nul
call :is_web_ready
if not errorlevel 1 goto open_browser
set /a retry_count+=1
if %retry_count% geq %max_retries% goto timeout_error
echo   ... waiting %retry_count%/%max_retries%
goto wait_loop

:open_browser
echo.
echo [OK] Web service is ready! Opening browser...
start http://%WEB_HOST%:%WEB_PORT%
goto done

:timeout_error
echo.
echo [WARNING] Web service did not become ready within 45 seconds.
echo [TIP] Check the Xiakedao Web window for errors.
echo [TIP] If port 8000 is already occupied, close the other process first.
echo.
pause
exit /b 0

:done
echo.
echo [DONE] Xiakedao is running!
echo [URL]  http://%WEB_HOST%:%WEB_PORT%
echo.
echo Close the Xiakedao Web window to stop the server.
echo.
pause
exit /b 0

:is_web_ready
curl --noproxy "*" -s http://%WEB_HOST%:%WEB_PORT%/health >nul 2>&1
if errorlevel 1 exit /b 1
curl --noproxy "*" -s -o nul -w "%%{http_code}" http://%WEB_HOST%:%WEB_PORT%/ 2>nul | findstr "200" >nul
if errorlevel 1 exit /b 1
exit /b 0
