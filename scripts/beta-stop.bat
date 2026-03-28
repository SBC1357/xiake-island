@echo off
setlocal
cd /d "%~dp0.."

echo ================================================
echo Xiakedao - Stop Beta Server
echo ================================================
echo.

:: Kill by window title (more reliable on Windows)
tasklist /fi "windowtitle eq Xiakedao Beta Server*" >nul 2>&1
if errorlevel 1 (
    echo [INFO] No running server found.
) else (
    taskkill /fi "windowtitle eq Xiakedao Beta Server*" /f >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Server stopped.
    ) else (
        echo [WARN] Could not stop server. Close the window manually.
    )
)

echo.
pause
exit /b 0