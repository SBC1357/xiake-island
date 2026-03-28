# 质量治理协作 Stage Package 4 Checkpoint

> **日期**: 2026-03-19
> **阶段包**: Stage Package 4 - 质量 / 治理 / 协作增强
> **状态**: ✅ 完成（按 2026-03-19 用户显式 override 推进；本文件不宣称 `SP-3` 浏览器/manual 门禁已闭合）
> **修订**: v1.0

---

## 0. 执行前提说明

- 原计划文件要求 `SP-3` 完成后再进入 `SP-4`
- 2026-03-19 用户显式要求：`SP-3` 不作为主线阻塞项
- 因此本 checkpoint 只确认 `SP-4` 范围内实现与验收结果
- `SP-3` 仍保持“部分完成”口径，相关浏览器/manual E2E 现状继续以 `docs/checkpoints/前端产品化_stage-3_checkpoint_20260319.md` 为准

## 1. 完成项

### 1.1 合规红线检查增强

- 新增 `src/contracts/m5_compliance_schema.py`
- 落地 `ComplianceRule` / `ComplianceViolation` / `ComplianceResult`
- 落地 `ComplianceChecker`
- 默认规则已覆盖绝对化疗效宣称、未经批准宣称、恐吓性表述、处方药直接面向患者宣传、虚假对比

### 1.2 质量门禁接线

- `src/modules/quality/orchestrator.py` 已接入 `ComplianceChecker`
- `run_gates_on_content()` 现在会执行 `compliance_check()`
- critical 违规会把结果打成 error，warning 违规保持 warning

### 1.3 版本管理增强

- `src/runtime_logging/hash_utils.py` 已提供 `compute_output_hash()`
- `src/runtime_logging/__init__.py` 已导出 `compute_output_hash`
- `src/runtime_logging/task_logger.py` 在 `complete_task(output_data=...)` 且未显式传入 `output_hash` 时会自动计算输出哈希

### 1.4 协作 / 追溯能力验证

- `GET /v1/tasks/versions/{input_hash}` 相关测试通过
- `POST /v1/tasks/{task_id}/feedback` 相关测试通过
- `POST /v1/tasks/{task_id}/copy` 相关测试通过

## 2. 未完成项

- 本 checkpoint 不覆盖 `SP-5` 的统一终审、前端构建验证、最终汇报
- 本 checkpoint 不把 `SP-3` 浏览器/manual E2E 写成已闭合

## 3. 失败项与是否既有失败

### 已闭合 P1

1. `src/contracts/m5_compliance_schema.py` 在 `ComplianceChecker.check()` 内错误导入 `.hash_utils`
   - 定性：本轮新增实现缺陷
   - 结果：已修复为 `from src.runtime_logging.hash_utils import compute_input_hash`

2. `src/modules/quality/orchestrator.py` 新接入合规门禁后调用了不存在的 `self.compliance_check(...)`
   - 定性：本轮新增接线缺陷
   - 结果：已补齐 `compliance_check()` 并通过 focused tests

3. `output_hash` 只补了工具函数，未完成包级导出和 `complete_task()` 自动计算
   - 定性：本轮新增的版本管理半接线问题
   - 结果：已补齐导出、自动计算逻辑和 focused tests

### 当前未闭合 P1/P2

- 无本轮已证实且未修复的 `SP-4` 范围内 P1/P2

## 4. 关键证据路径或命令

### Focused 验收

```bash
"C:\Users\96138\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m pytest tests/modules/test_quality.py tests/contracts/test_compliance_schema.py tests/runtime_logging/test_contract_upgrade.py tests/runtime_logging/test_output_hash.py tests/api/test_tasks.py -q
# 53 passed, 5 warnings in 0.69s
```

### 后端全量验收

```bash
"C:\Users\96138\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m pytest tests -q
# 393 passed, 1 skipped, 5 warnings in 12.82s
```

### 运行探针

```bash
"C:\Users\96138\AppData\Local\Python\pythoncore-3.14-64\python.exe" -c "from src.runtime_logging import compute_output_hash; from src.runtime_logging.task_logger import TaskLogger; from src.contracts.base import ModuleName; logger=TaskLogger(); tid=logger.start_task(module=ModuleName.OPINION); logger.complete_task(tid, output_data={'content':'abc'}); entry=logger.get_task(tid); print('export', callable(compute_output_hash), 'output_hash', entry.output_hash)"
# export True output_hash 31ac110e63618c9a
```

## 5. 双轮自审结果

### 第一轮自审

- 逐项核查 `SP-4` 范围：合规红线、版本管理、反馈/复制/版本查询
- 发现并回写了 3 个窄 fix batch
- 每个 fix batch 都用真实运行路径或 focused pytest 复验，不靠文案判断

### 第二轮自审

- 用 focused 套件确认 `quality + compliance + runtime_logging + tasks API` 主链闭合
- 用全量 `pytest tests -q` 确认后端未被 `SP-4` 回归打坏
- 二次确认本文件未把 `SP-3` 的浏览器/manual 状态误写为已通过

### 自审结论

- `SP-4` 范围内目标已闭合
- 当前具备进入 `SP-5` 统一终审的条件

## 6. 下一步动作

- 进入 `SP-5`：统一终审
- 执行全量前后端验证、文档一致性检查、P1/P2 清零确认
- `SP-5` 通过后，读取 `docs/archive/root-historical/侠客岛SP-6核心去黑箱与正式交付目标与要求_20260319.md`，先规划再执行 `SP-6`

## Evidence Summary

1. `tests/modules/test_quality.py`、`tests/contracts/test_compliance_schema.py`、`tests/runtime_logging/test_contract_upgrade.py`、`tests/runtime_logging/test_output_hash.py`、`tests/api/test_tasks.py` 联合验证结果：`53 passed, 5 warnings in 0.69s`。
2. 后端全量：`pytest tests -q` -> `393 passed, 1 skipped, 5 warnings in 12.82s`。
3. 运行探针确认 `compute_output_hash` 已导出，且 `complete_task(output_data=...)` 会自动写出 `output_hash 31ac110e63618c9a`。
