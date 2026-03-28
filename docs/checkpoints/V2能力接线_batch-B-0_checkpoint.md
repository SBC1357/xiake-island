# Batch B-0：V2 能力接入规划 Checkpoint

> **日期**: 2026-03-17
> **阶段包**: Batch B-0 V2 能力接入规划
> **状态**: ✅ 完成

## 1. V2 能力清单

### 1.1 Engine 模块 (41 个 Python 文件)

| 分类 | 模块 | 文件数 | 接入优先级 | 接入方式 |
|------|------|--------|-----------|---------|
| **选题/规划类** | `engine/editorial/` | 2 | P1 | 新增 `src/modules/planning/` |
| **写作生成类** | `engine/prompt/` | 1 | P1 | 新增 `src/modules/writing/` |
| **质量审校类** | `engine/quality/` | 1 | P2 | 增强 `src/modules/semantic_review/` |
| **交付整理类** | `engine/delivery/` | 2 | P2 | 新增 `src/modules/delivery/` |
| **证据管理类** | `engine/evidence/` | 8 | P3 | 新增 `src/modules/evidence/` |
| **摄入处理类** | `engine/intake/` | 6 | P3 | 新增 `src/modules/intake/` |
| **合约定义类** | `engine/contracts/` | 6 | - | 引用，不独立接入 |
| **配置类** | `engine/config/` | 1 | - | 已有知识底座配置 |
| **运行时类** | `engine/runtime/` | 2 | - | 不直接接入 |

### 1.2 Rules 目录 (18 个规则文件)

| 层级 | 目录 | 文件数 | 接入优先级 | 接入方式 |
|------|------|--------|-----------|---------|
| **L1 写作工艺** | `rules/l1_writing_craft/` | 9 | P1 | 知识底座已接 |
| **L2 医学手册** | `rules/l2_medical_playbook/core/` | 9 | P1 | 知识底座已接 |

### 1.3 Structured 目录 (40 个结构化数据文件)

| 层级 | 目录 | 文件数 | 接入优先级 | 接入方式 |
|------|------|--------|-----------|---------|
| **L3 疾病知识** | `structured/l3/` | 13 | P2 | 知识底座已接 |
| **L4 产品证据** | `structured/l4/` | 27 | P2 | 知识底座已接 |

## 2. 接入优先级清单

### P1 - 立即接入（B-1, B-2）
| 能力 | V2 来源 | 侠客岛目标 | 理由 |
|------|--------|-----------|------|
| 选题/规划 | `engine/editorial/planner.py`, `persona.py` | `src/modules/planning/` | 核心写作能力前置 |
| 论点推导规则 | `structured/l3/*/m1_thesis_derivation_rules.json` | 知识底座引用 | 规划依赖 |
| Prompt 编译 | `engine/prompt/compiler.py` | `src/modules/writing/` | 写作生成核心 |

### P2 - 次要接入（B-3, B-4）
| 能力 | V2 来源 | 侠客岛目标 | 理由 |
|------|--------|-----------|------|
| 质量审校 | `engine/quality/orchestrator.py` | 增强 `semantic_review` | 质量增强 |
| 交付整理 | `engine/delivery/markdown_writer.py` | `src/modules/delivery/` | 输出格式化 |

### P3 - 后续接入
| 能力 | V2 来源 | 侠客岛目标 | 理由 |
|------|--------|-----------|------|
| 证据管理 | `engine/evidence/` | `src/modules/evidence/` | 高级功能 |
| 摄入处理 | `engine/intake/` | `src/modules/intake/` | 高级功能 |

## 3. 接入顺序确认

```
B-0: 规划 ← 当前
  ↓
B-1: 选题/规划类 (依赖: A-2 ✅)
  ↓
B-2: 写作生成类 (依赖: B-1)
  ↓
B-3: 质量审校类 (依赖: B-2)
  ↓
B-4: 交付整理类 (依赖: B-2)
```

## 4. 不接入项

| 模块 | 原因 |
|------|------|
| `engine/contracts/` | 仅定义数据结构，不独立接入 |
| `engine/config/` | 已有知识底座配置，无需重复 |
| `engine/runtime/` | 运行时管理，侠客岛有自己的运行时 |

## 5. 验证

- [x] V2 目录扫描完成
- [x] 能力清单与目录一致
- [x] 优先级排序合理
- [x] 接入方式明确

## 6. 下一步动作

进入 **B-1：选题/规划类能力接入**