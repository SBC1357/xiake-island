# 三系统解耦_2C-phase-1-2_checkpoint_20260316

## 阶段包
**2C-1 + 2C-2**: V2 与侠客岛默认切换收口

## 执行时间
2026-03-16 +08:00

## 完成项

### 2C-1: V2 Silent Fallback → Fail-Fast

**问题**: `external_resolver.py` 在 `resolve_sources` 和 `resolve_facts` 中捕获异常返回空列表

**修复**:
- 移除 lines 83-86 try/except (resolve_sources)
- 移除 lines 106-109 try/except (resolve_facts)
- 更新 docstrings 添加 Raises 说明

**验证**:
```
Total facts: 159
L3 facts: 16
L4 facts: 29
has_l3: True
has_l4: True
```

**Legacy 回退**:
- 仍可通过 `KNOWLEDGE_SOURCE_MODE=legacy` 显式启用

### 2C-2: Xiakedao Warn-But-Don't-Block → Strict Mode

**问题**: `assembly.py` 在 `consumer_root=None` 时仅打印警告，不阻止启动

**修复**:
- 添加 `XIAGEDAO_STRICT_MODE` 环境变量 (默认: true)
- 严格模式下调用 `validate_consumer_config()` 并在失败时抛出 `ValueError`
- 非严格模式 (dev/test) 保留 warn-but-continue 行为

**新增配置**:
```bash
XIAGEDAO_STRICT_MODE=true   # 生产环境，fail-fast
XIAGEDAO_STRICT_MODE=false  # 开发/测试环境
```

**验证**:
```
pytest: 239 passed, 1 skipped, 5 warnings
```

## 回退开关说明

| 系统 | 回退开关 | 默认值 | 说明 |
|------|----------|--------|------|
| V2 | `KNOWLEDGE_SOURCE_MODE=legacy` | external | 显式启用 legacy 模式读取旧路径 |
| 侠客岛 | `XIAGEDAO_STRICT_MODE=false` | true | 非严格模式允许无 consumer 启动 |

## P1/P2 Issues
无

## 下一步动作
- 2C-3: fail-fast 行为清单与回退开关文档化
- 2C-4: current 切换与回滚演练
- 2C-5: 旧路径降级说明

## 签名
- 阶段状态: **COMPLETED**
- V2 fail-fast: **VERIFIED**
- Xiakedao strict mode: **VERIFIED**
- 回归测试: **PASSED (239)**