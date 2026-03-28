@echo off
setlocal
cd /d "%~dp0"
title Xiakedao Frontend

echo ================================================
echo Xiakedao frontend dev server
echo ================================================
echo.

if not exist "frontend" (
    echo [ERROR] frontend directory not found.
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo [ERROR] frontend\node_modules not found.
    echo Run: cd frontend ^&^& npm install
    pause
    exit /b 1
)

set "FRONTEND_HOST=localhost"
if defined XIAGEDAO_FRONTEND_HOST set "FRONTEND_HOST=%XIAGEDAO_FRONTEND_HOST%"
set "FRONTEND_PORT=5173"
if defined XIAGEDAO_FRONTEND_PORT set "FRONTEND_PORT=%XIAGEDAO_FRONTEND_PORT%"

pushd "frontend"

echo [INFO] URL: http://%FRONTEND_HOST%:%FRONTEND_PORT%
echo.

:: 启动前端，端口可通过环境变量配置；如果端口被占用则报错退出
npm run dev -- --host %FRONTEND_HOST% --port %FRONTEND_PORT% --strictPort
set "exit_code=%errorlevel%"

popd

if not "%exit_code%"=="0" (
    echo.
    echo [ERROR] Frontend exited with code %exit_code%.
    echo [TIP] If port %FRONTEND_PORT% is in use, close the other process first.
    pause
)

exit /b %exit_code%
