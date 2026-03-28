# 侠客岛 - 本地开发启动脚本
# 启动前端开发服务器

param(
    [switch]$Help
)

if ($Help) {
    Write-Host "用法: .\frontend-dev.ps1" -ForegroundColor Cyan
    Write-Host "启动前端开发服务器 (Vite)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "前置条件:" -ForegroundColor Yellow
    Write-Host "  - Node.js 已安装" -ForegroundColor Gray
    Write-Host "  - frontend/node_modules 已安装 (运行 npm install)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "前端默认访问地址: http://localhost:5173" -ForegroundColor Green
    exit 0
}

# 检查 frontend 目录是否存在
if (-not (Test-Path "frontend")) {
    Write-Error "错误: frontend 目录不存在"
    exit 1
}

$frontendHost = if ($env:XIAGEDAO_FRONTEND_HOST) { $env:XIAGEDAO_FRONTEND_HOST } else { "localhost" }
$frontendPort = if ($env:XIAGEDAO_FRONTEND_PORT) { $env:XIAGEDAO_FRONTEND_PORT } else { "5173" }

# 进入 frontend 目录
Set-Location frontend

# 检查 node_modules 是否存在
if (-not (Test-Path "node_modules")) {
    Write-Error "错误: frontend/node_modules 不存在，请先运行 'npm install'"
    exit 1
}

# 启动前端开发服务器
Write-Host "启动前端开发服务器..." -ForegroundColor Cyan
Write-Host "默认访问地址: http://$frontendHost`:$frontendPort" -ForegroundColor Green
npm run dev -- --host $frontendHost --port $frontendPort --strictPort
