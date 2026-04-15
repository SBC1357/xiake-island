# III期执行环境契约

状态：工作版 / III期总层环境契约
日期：2026-04-10
用途：把 III 期执行相关的环境、入口、配置边界一次写死；后续各阶段只允许回指本文件，不再各自发明一版环境说明。

## 这份文件解决什么

1. 统一说明 III 期执行时到底有哪几条环境链。
2. 统一说明哪些配置属于后端真相源，哪些只属于评分/CLI 辅助链。
3. 统一说明 PowerShell、shell、`.env`、`venv`、个人 CLI 配置之间的边界。
4. 防止后续阶段重复修“环境口径”。

## 这份文件不解决什么

1. 不替代当前阶段任务卡。
2. 不播报当前 blocker、当前分数、当前 smoke 结果。
3. 不替代 `02` 层规则正文。
4. 不替代阶段包里的执行计划。

## 总原则

1. III 期执行不能把“后端生成链”“评分链”“个人 CLI 配置链”混成一套。
2. 能决定后端写作行为的，只认仓库真相源。
3. 能决定评分辅助行为的，只认评分执行器自己的配置逻辑。
4. 个人 CLI / Codex / opencode 配置，只能当辅助链，不得反向冒充后端真相源。
5. 各阶段只允许补本阶段额外前置，不允许重写这份总契约。

## 三条环境链的固定边界

### 1. 后端生成链

这条链只负责：证据、规划、写作、drafting、quality、delivery。

固定真相源：

1. 仓库根目录 `.env`
2. `src\\adapters\\llm_gateway\\provider_factory.py`
3. `src\\adapters\\llm_gateway\\openai_provider.py`

当前固定口径：

1. 后端写作阶段只认仓库 `.env` 里的：
   - `LLM_PROVIDER`
   - `DRAFTING_MODE`
   - `LLM_MODEL`
   - `OPENAI_BASE_URL`
   - `OPENAI_API_KEY`
2. 当前 OpenAI-compatible 写法固定走：
   - `OPENAI_BASE_URL + /chat/completions`
3. 个人 CLI 配置文件不是后端生成链真相源。

### 2. 评分 / benchmark 辅助链

这条链只负责：对生成稿做机器评分与汇总。

固定真相源：

1. `scripts\\run_ii_benchmark.ps1`
2. `scripts\\benchmark_runner.ps1`

当前固定口径：

1. 当前评分链的真实入口是：
   - `run_ii_benchmark.ps1`
   - 它实际调用 `benchmark_runner.ps1`
2. 评分链允许使用显式 `-ScoringApiKey`。
3. 评分链也可能读取 shell 中可见的 key，或读取辅助 provider 候选。
4. 只要评分链还会尝试多个 provider，它就仍然属于“辅助链未完全单口径”，不能倒推后端生成链配置。

### 3. 个人 CLI / 本机开发配置链

这条链只负责：个人开发、外部 CLI、辅助 provider 候选，不直接决定 III 期后端写作链。

典型文件：

1. `用户主目录/.codex/config.toml`
2. `用户主目录/.config/opencode/opencode.json`
3. PowerShell profile、npm shim、Codex 宿主兜底环境

固定边界：

1. 它们可能影响：
   - 本机 shell
   - Codex / opencode CLI
   - benchmark 辅助 provider 候选
2. 它们不直接决定后端写作阶段用哪个 base URL。
3. 看到 `apps/anthropic/v1` 这类路径时，必须先判断它属于 CLI/评分辅助链，不能直接判成后端路径写错。

## 入口与执行约束

1. 当前 IIIA 预检统一入口：
   - `scripts\\iiia\\iiia_preflight.ps1`
2. 当前 smoke 统一执行入口：
   - `scripts\\run_ii_benchmark.ps1`
3. 当前 smoke 统一评分执行器：
   - `scripts\\benchmark_runner.ps1`
4. 当前外部 PowerShell 执行链必须先跑预检，再跑 smoke。
5. 任何 Agent 若未先跑预检，不得宣称“环境已就绪”。

## shell / env / venv 约束

1. PowerShell 与其他 shell 看到的环境变量可能不完全一致，不能默认互通。
2. 预检与正式 runner 都必须显式加载仓库 `.env`，不能依赖当前 shell 恰好带着变量。
3. `venv` 负责仓库 Python 解释器与依赖，不负责替你自动决定 LLM provider。
4. 任何 Agent 如果发现某条链只在自己的 shell 里可用，必须先判定它属于：
   - 仓库 `.env`
   - 评分辅助链
   - 个人 CLI 配置链
   不能直接宣布“整个 III 期环境已修复”。

## 阶段层怎么使用本契约

1. `05/IIIA/04_试运行计划.md` 只允许写：
   - 本阶段额外前置
   - 本阶段允许先冒烟的 case 集
   - 本阶段 blocked 目录形态
   - 本阶段固定输出根
2. 不允许在阶段计划里重写三条环境链的解释。
3. 后续 `IIIB/IIIC` 若被激活，也只允许回指本文件。

## 发现环境冲突时的处理顺序

1. 先判断冲突属于哪条链：
   - 后端生成链
   - 评分辅助链
   - 个人 CLI 配置链
2. 再回查该链的固定真相源。
3. 若同一问题同时涉及两条链，不准混写成一条结论。
4. 若评分链仍在猜 provider，优先修评分链，不要误伤后端生成链配置。

## 证据摘要

1. 已直接核对仓库根目录 `.env`，确认后端写作链当前由 `OPENAI_BASE_URL / OPENAI_API_KEY` 等键驱动。
2. 已直接核对 `src\\adapters\\llm_gateway\\openai_provider.py` 与 `provider_factory.py`，确认后端实际走的是 `chat/completions` 路径。
3. 已直接核对 `scripts\\run_ii_benchmark.ps1` 与 `scripts\\benchmark_runner.ps1`，确认评分链是独立执行链，且当前仍存在多 provider 候选逻辑。
4. 已直接核对个人 `opencode.json` 配置文件，确认其中的 provider 配置属于 CLI/评分辅助链，不属于后端生成链真相源。
