# 证据规划集成 Stage Package 1 Checkpoint

> **日期**: 2026-03-18
> **阶段包**: Stage Package 1 - 证据 + 规划集成
> **状态**: ⚠️ 完成带 P2（已修复）
> **修订**: v1.1 - 修正过度宣称，记录真实状态

---

## 1. 完成项

### 1.1 新增/修改文件

| 文件 | 类型 | 说明 |
|------|------|------|
| `src/contracts/base.py` | 修改 | 扩充 ModuleName 枚举 |
| `src/orchestrator/models.py` | 修改 | 扩展 ModuleTask.module_name |
| `src/modules/evidence/service.py` | 重写 | 补全真实查询逻辑 |
| `src/assembly.py` | 修改 | 添加 EvidenceService 共享实例 |
| `src/api/routes/evidence.py` | 新增 | 证据查询 API 路由 |
| `src/api/routes/planning.py` | 新增 | 规划生成 API 路由 |
| `src/api/app.py` | 修改 | 注册新路由 |

### 1.2 功能特性

#### Evidence 模块
1. **EvidenceService 真实查询逻辑**
   - `resolve_facts()`: 从藏经阁读取 L4 产品证据
   - `resolve_sources()`: 解析证据来源
   - `query_facts_by_domain()`: 按领域查询事实
   - `get_fact_lineage()`: 获取事实溯源信息
   - `list_available_products()`: 列出可用产品

2. **Evidence API 端点**
   - `POST /v1/evidence/query`: 查询证据
   - `GET /v1/evidence/fact/{fact_id}`: 获取事实详情
   - `GET /v1/evidence/products`: 列出产品
   - `GET /v1/evidence/sources/{product_id}`: 获取来源

#### Planning 模块
1. **PlanningService 接入**
   - 复用现有 `PlanningService` 逻辑
   - 支持基于 Evidence 输出生成规划

2. **Planning API 端点**
   - `POST /v1/planning/plan`: 生成编辑计划
   - `POST /v1/planning/persona`: 获取人格画像
   - `GET /v1/planning/health`: 健康检查

### 1.3 模块枚举扩充

```python
class ModuleName(str, Enum):
    OPINION = "opinion"
    SEMANTIC_REVIEW = "semantic_review"
    WRITING = "writing"
    ORCHESTRATOR = "orchestrator"
    PLANNING = "planning"      # 新增
    EVIDENCE = "evidence"      # 新增
    QUALITY = "quality"        # 新增
    DELIVERY = "delivery"      # 新增
```

---

## 2. 发现与修复的问题

### P2: Evidence 产品发现/文件名适配缺陷

**问题描述**:
- `list_available_products()` 返回异常产品名 `lecanemab_evidence_v2_sample.json` 而非 `lecanemab`
- `_load_evidence_file()` 无法处理带 `_sample` 后缀的文件名
- 导致 `lecanemab facts=0`，而 `pluvicto facts=2`

**修复内容** (`src/modules/evidence/service.py`):
1. `list_available_products()` (行 291-298): 修正文件名解析，正确移除 `_evidence_v2.json` 和 `_evidence_v2_sample.json`
2. `_load_evidence_file()` (行 37-66): 添加 fallback 逻辑，主文件不存在时尝试 `_sample` 版本
3. `get_fact_lineage()` (行 252-255): 同步修正文件名解析逻辑

**验证结果**:
```
Available products: ['donanemab', 'furmonertinib', 'lecanemab', 'lemborexant', 'pluvicto', 'test_product', 'trastuzumab_deruxtecan_gastric']
lecanemab facts count: 2  # 修复前为 0
pluvicto facts count: 2
```

---

## 3. 未完成项

| 项目 | 说明 | 优先级 |
|------|------|--------|
| 新模块 API 接入编排器统一任务日志 | planning API 直接调 service，未走 orchestrator 跟踪 | P2 |
| 集成测试覆盖 | evidence/planning API 缺少集成测试 | P2 |

---

## 4. 关键证据路径或命令

### 后端测试
```
pytest tests -q
# 358 passed, 1 skipped, 5 warnings in 8.50s
```

### 前端测试
```
npm run test:run
# 33 passed (5 test files)

npm run build
# built in 187ms
```

### API 路由验证
```
Evidence routes: ['/v1/evidence/query', '/v1/evidence/fact/{fact_id}', '/v1/evidence/products', '/v1/evidence/sources/{product_id}']
Planning routes: ['/v1/planning/plan', '/v1/planning/persona', '/v1/planning/health']
```

---

## 5. 自审结果

### 已验证项

| 检查项 | 结果 |
|--------|------|
| Evidence API 可用 | ✅ POST /v1/evidence/query |
| Planning API 可用 | ✅ POST /v1/planning/plan |
| lecanemab 产品可正确解析 | ✅ facts count: 2 |
| 数据流符合 Evidence → Planning 方向 | ✅ Planning 接受 evidence_facts 参数 |
| 无新路径硬编码 | ✅ 通过 AssetBridge 和环境变量 |

### 待改进项

| 检查项 | 当前状态 |
|--------|----------|
| 新模块 API 走 orchestrator 跟踪 | ❌ 直接调 service |
| 集成测试覆盖 | ❌ 缺失 |

---

## 6. SP-1 退出门禁检查

| 门禁条件 | 状态 |
|----------|------|
| Evidence API 可用 | ✅ |
| Planning API 可用 | ✅ |
| 后端测试通过 | ✅ 358 passed |
| P2 问题已修复 | ✅ lecanemab 可正确解析 |
| 剩余 P2 已记录 | ✅ API 跟踪、测试覆盖 |

---

## 7. 下一步动作

可进入 **Stage Package 2: 写作 + 质量 + 交付 + 标准链闭环**

### SP-2 任务预览

1. Writing 模块接入
2. Quality 模块接入
3. Delivery 模块接入
4. orchestrator/service.py 扩展标准五段链
5. API 路由扩展

---

> **文档版本**: v1.1
> **创建日期**: 2026-03-18
> **修订日期**: 2026-03-18
> **编写者**: Sisyphus Agent
> **修订说明**: 修正 v1.0 过度宣称，记录 P2 问题及修复