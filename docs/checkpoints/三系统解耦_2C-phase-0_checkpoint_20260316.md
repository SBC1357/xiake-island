# 三系统解耦_2C-phase-0_checkpoint_20260316

## 阶段包
**2C-0**: 基线扫描与默认路径盘点

## 执行时间
2026-03-16 +08:00

## 完成项

### 1. V2 默认路径盘点

**当前状态**:
- 默认模式: `KNOWLEDGE_SOURCE_MODE=external` (默认值)
- 知识根: `KNOWLEDGE_ROOT` 环境变量
- 消费路径: `藏经阁/publish/current/consumers/v2/`

**Legacy 回退入口**:
- `KNOWLEDGE_SOURCE_MODE=legacy`
- `V1_BASE_PATH` 环境变量

**问题识别**:
| 位置 | 声明行为 | 实际行为 |
|------|----------|----------|
| external_resolver.py docstring | "fail-fast" | ❌ silent fallback |
| resolve_sources (83-86行) | - | 捕获异常返回 `[]` |
| resolve_facts (106-109行) | - | 捕获异常返回 `[]` |

**结论**: V2 当前是 **silent fallback**，不是 fail-fast

### 2. 侠客岛默认路径盘点

**当前状态**:
- 消费者根: `XIAGEDAO_CONSUMER_ROOT` 环境变量
- 默认路径: `藏经阁/publish/current/consumers/xiakedao/`

**问题识别**:
| 位置 | 声明行为 | 实际行为 |
|------|----------|----------|
| assembly.py (61-62行) | - | "warn but don't block" |
| get_asset_bridge | - | 允许 consumer_root=None 启动 |
| validate_consumer_config | 验证函数 | 未在启动时强制调用 |

**结论**: 侠客岛当前是 **warn-but-don't-block**，不是 fail-fast

### 3. 默认根配置源

**已创建**: `D:\汇度编辑部1\set-default-env.ps1`

```powershell
$env:KNOWLEDGE_SOURCE_MODE = "external"
$env:KNOWLEDGE_ROOT = "D:\汇度编辑部1\藏经阁"
$env:XIAGEDAO_CONSUMER_ROOT = "D:\汇度编辑部1\藏经阁\publish\current\consumers\xiakedao"
```

### 4. 收口项清单

| 系统 | 收口项 | 当前状态 |
|------|--------|----------|
| V2 | Silent fallback → Fail-fast | 待修复 |
| V2 | Legacy 显式开关 | 已存在 |
| 侠客岛 | Warn-but-don't-block → Fail-fast | 待修复 |
| 侠客岛 | Legacy 显式开关 | 待添加 |

## P1/P2 Issues

### P1-1: V2 silent fallback
**问题**: `resolve_facts` 捕获异常返回空列表，不是真正的 fail-fast

**修复方案**: 让异常向上传播，由调用方决定处理方式

### P1-2: Xiakedao warn-but-don't-block
**问题**: `get_asset_bridge` 允许 `consumer_root=None` 启动

**修复方案**: 添加严格模式，生产环境强制要求有效 consumer_root

## 下一步动作
- 2C-1: 修复 V2 silent fallback
- 2C-2: 修复 Xiakedao warn-but-don't-block

## 签名
- 阶段状态: **COMPLETED**
- 发现问题: P1-1, P1-2
- 下一阶段: **2C-1** (待执行)