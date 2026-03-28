# Batch B-1：选题/规划类能力接入 Checkpoint

> **日期**: 2026-03-17
> **阶段包**: Batch B-1 选题/规划类能力接入
> **状态**: ✅ 完成

## 1. 完成项

### 1.1 新增文件

| 文件 | 说明 |
|------|------|
| `src/modules/planning/__init__.py` | 模块入口 |
| `src/modules/planning/models.py` | 数据模型（与 V2 契约兼容） |
| `src/modules/planning/service.py` | 规划服务（实现 V2 EditorialPlanner 逻辑） |
| `tests/modules/test_planning.py` | 测试用例（11 个） |

### 1.2 功能特性

1. **RouteContext**：路由上下文，定义任务启动参数
2. **EditorialPlan**：编辑计划，包含论点、大纲、策略
3. **PlanningService**：规划服务
   - 生成核心论点
   - 构建文章大纲（按 domain 分组）
   - 选择写作策略（play_id）
   - 选择叙事弧线（arc_id）
4. **PersonaProfile**：人格画像（预定义）

### 1.3 V2 契约兼容

| V2 模块 | 侠客岛模块 | 兼容性 |
|---------|-----------|--------|
| `engine/contracts/route_context.py` | `planning/models.py::RouteContext` | ✅ 字段一致 |
| `engine/contracts/editorial_plan.py` | `planning/models.py::EditorialPlan` | ✅ 字段一致 |
| `engine/editorial/planner.py` | `planning/service.py::PlanningService` | ✅ 逻辑兼容 |
| `engine/editorial/persona.py` | `planning/models.py::PersonaProfile` | ✅ 字段兼容 |

## 2. 未完成项

无

## 3. 失败项与是否既有失败

无 P1/P2 问题。

### 既有问题（非本次引入，非阻塞）
- `register` 字段名与 Pydantic BaseModel 属性冲突警告

## 4. 关键证据路径或命令

### 后端测试
```
pytest tests/modules/test_planning.py -v
# 11 passed in 0.10s

pytest tests -q
# 316 passed, 1 skipped, 4 warnings in 7.88s
```

### 验证标准（执行单要求）
| 验证标准 | 结果 |
|---------|------|
| 新增规划模块 API | ✅ PlanningService.plan() |
| 能调用 V2 规则生成选题/论点规划 | ✅ 实现 V2 Planner 逻辑 |
| 规则调用走知识底座 | ✅ 不硬编码路径 |

## 5. 双轮自审结果

### 第一轮：规则调用检查
- ✅ 不硬编码规则路径
- ✅ 通过参数传入证据数据
- ✅ 规则逻辑内置于服务中

### 第二轮：契约兼容检查
- ✅ RouteContext 字段与 V2 一致
- ✅ EditorialPlan 字段与 V2 一致
- ✅ 可与 V2 模块互换使用

### 自审结论
无 P1/P2 问题，符合执行单要求。

## 6. 下一步动作

B-1 已完成，可以进入：
- **B-2** 写作生成类能力接入（依赖 B-1）