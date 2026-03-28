# 侠客岛

> **日期**: 2026-03-29
> **性质**: 项目入口文档
> **当前状态**: 主运行链已验证，可作为扩展前基线
> **适用范围**: 当前工作区

`侠客岛` 是一个面向中文医疗内容生产的独立能力平台，当前以“模块化内容能力底座 + 主编排器”为核心方向推进。

README 只承担入口职责：告诉你怎么启动、怎么配环境、怎么区分源码与运行态，不在这里维护第二套施工计划。

## 快速启动

### 前置条件

- Python 3.10+，推荐 `pip install -e .[dev]`
- Node.js 18+，前端依赖安装命令：`cd frontend && npm install`

### Windows 启动脚本

双击以下批处理文件即可启动：

```text
dev.bat           # 一键启动统一 Web 入口，并自动打开浏览器
backend-dev.bat   # 单独启动后端统一入口
frontend-dev.bat  # 单独启动前端开发服务器
```

PowerShell 备用脚本：

```powershell
.\dev.ps1
.\backend-dev.ps1
.\frontend-dev.ps1
```

这些脚本现在支持通过环境变量改端口、地址和运行目录，不需要再直接改脚本内容。

### 默认访问地址

- 前端开发服务器：`http://localhost:5173`
- 统一 Web 入口：`http://127.0.0.1:8000`
- API 文档：`http://127.0.0.1:8000/docs`

### 运行模式

- `XIAGEDAO_WEB_MODE=web-bundled`
  - 默认模式
  - 后端挂载 `frontend/dist`，根路径 `/` 直接返回前端页面
- `XIAGEDAO_WEB_MODE=api-only`
  - 只启动后端 API
  - 根路径 `/` 不再依赖前端构建产物

## 推荐配置方式

优先顺序如下：

1. 在系统环境变量或启动器里直接注入
2. 在仓库根目录放 `.env`
3. 通过 `XIAGEDAO_ENV_FILE` 指向外部环境文件

这三种方式的目的都是同一个：让配置留在环境层，而不是写死在脚本和代码里。

## 核心环境变量

### 运行与入口

- `XIAGEDAO_HOST`
  - 后端监听地址，默认 `0.0.0.0`
- `XIAGEDAO_PORT`
  - 后端监听端口，默认 `8000`
- `XIAGEDAO_WEB_MODE`
  - `web-bundled` 或 `api-only`
- `XIAGEDAO_FRONTEND_DIST`
  - 自定义前端构建产物目录；不设置时默认用 `frontend/dist`

### 前端开发

- `XIAGEDAO_FRONTEND_HOST`
  - 前端开发服务器监听地址，默认 `localhost`
- `XIAGEDAO_FRONTEND_PORT`
  - 前端开发服务器端口，默认 `5173`
- `XIAGEDAO_CORS_ORIGINS`
  - 显式指定后端允许的前端来源，多个值用逗号分隔

### 运行态目录

- `XIAGEDAO_RUNTIME_ROOT`
  - 运行态根目录；不设置时默认落在仓库同级 `侠客岛-runtime/`
- `XIAGEDAO_DATA_DIR`
  - 自定义任务日志目录
- `XIAGEDAO_UPLOAD_ROOT`
  - 自定义上传运行目录
- `XIAKEDAO_UPLOAD_ROOT`
  - 旧变量名，当前仍兼容，但新配置请改用 `XIAGEDAO_UPLOAD_ROOT`

### 业务配置

- `XIAGEDAO_CONSUMER_ROOT`
  - 知识消费者根目录
- `XIAGEDAO_STRICT_MODE`
  - `true` 时消费者配置无效会阻止启动；`false` 时仅警告
- `LLM_PROVIDER`
  - 开发默认 `fake`
- `LLM_MODEL`
  - 真实模型模式下需要显式指定

### 示例

```powershell
$env:XIAGEDAO_CONSUMER_ROOT = "D:\path\to\publish\current\consumers\xiakedao"
$env:XIAGEDAO_RUNTIME_ROOT = "D:\path\to\xiakedao-runtime"
$env:XIAGEDAO_WEB_MODE = "api-only"
$env:XIAGEDAO_PORT = "8000"
$env:XIAGEDAO_CORS_ORIGINS = "https://editor.example.com,https://preview.example.com"
```

## 当前基线

当前主工作区已经完成这些收口：

- 任务库和上传目录默认迁出仓库工作区
- 前后端入口支持 `web-bundled` 和 `api-only`
- 核心 app-level 回归测试已和本机 `.env` 污染解耦
- 人工启动脚本已支持通过环境变量改地址、端口和前端入口路径

这意味着后续做扩展时，优先动配置，不要再去改脚本里的固定路径和固定端口。

## 文档入口

- `docs/侠客岛系统设计图纸_20260313.md`
  - 项目总纲
- `docs/侠客岛首阶段施工图纸_20260313.md`
  - 施工与落地顺序
- `docs/ADR-001-主编排器与模块边界.md`
  - 架构决策记录
- `docs/侠客岛系统总纲评审记录_20260313.md`
  - 历史评审记录
- `侠客岛-系统优化方案_20260329.md`
  - 当前优化进展和下一步建议
- `侠客岛-分批清理验证日志.md`
  - 清理、验证和回溯证据
