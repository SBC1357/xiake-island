# 三系统解耦_2C-phase-3_checkpoint_20260316

## 阶段包
**2C-3**: fail-fast 与显式回退开关收口

## 执行时间
2026-03-16 +08:00

## 完成项

### 1. Fail-Fast 行为清单

**V2**:
- `KnowledgeRootNotConfiguredError`: KNOWLEDGE_ROOT 未配置
- `KnowledgeRootNotFoundError`: 知识根目录不存在
- `KnowledgeRootNotReadableError`: 知识根目录不可读

**侠客岛**:
- `ValueError`: XIAGEDAO_CONSUMER_ROOT 未配置或无效 (严格模式)

### 2. 显式回退开关

| 系统 | 开关 | 默认值 | 用途 |
|------|------|--------|------|
| V2 | `KNOWLEDGE_SOURCE_MODE=legacy` | external | 紧急回退到旧路径 |
| 侠客岛 | `XIAGEDAO_STRICT_MODE=false` | true | 开发/测试环境 |

### 3. 运行口径说明

**文件**: `侠客岛/docs/archive/root-historical/三系统解耦_2C运行口径说明_20260316.md`

包含:
- 默认配置源
- Fail-Fast 行为清单
- 显式回退开关说明
- 当前版本信息
- 旧路径状态
- 验证命令
- 故障排查

## P1/P2 Issues
无

## 下一步动作
- 2C-4: current 切换与回滚演练

## 签名
- 阶段状态: **COMPLETED**
