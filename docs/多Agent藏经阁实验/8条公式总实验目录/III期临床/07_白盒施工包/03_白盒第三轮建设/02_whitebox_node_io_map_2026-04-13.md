# Whitebox Node I/O Map（Audit View）

- Visual HTML entry: [02_whitebox_node_io_view_2026-04-13.html](<02_whitebox_node_io_view_2026-04-13.html>)
- 用途：前台 / 聊天 / IDE 点击入口（纯跳转，不承载主链口径）。
- 中文真相源：`02_白盒各节点输入输出一览_2026-04-13.md`
- **当前冻结主链以 `../00_入口索引.md` 三、当前冻结主链 为唯一真相源。本页不再维护主链描述。**

## 打开中文真相源

- [02_白盒各节点输入输出一览_2026-04-13.md](<02_白盒各节点输入输出一览_2026-04-13.md>)

## 4 个代码侧审计入口

1. 主控脚本：`侠客岛白盒编排器/run_whitebox_main_chain.ps1`
2. 冻结协议：`侠客岛白盒编排器/config/node_io_protocol.json`
3. Profile 绑定：`侠客岛白盒编排器/config/whitebox_llm_profiles.json`
4. 提示词目录：`侠客岛白盒编排器/prompts/`

本页不承载主链流程描述、后审流向或节点级 IO 详情。一切回中文真相源。
- `prompt_prefix`

## Evidence Summary

1. Flow anchor:
   `run_whitebox_main_chain.ps1` directly shows the real order `materials -> layer1 -> writing_contract -> pre_review(parallel) -> outline -> draft(first) -> post_review -> flow back`.
2. Prompt binding anchor:
   `whitebox_llm_profiles.json` directly binds prompt file, model env, base url env, protocol env, and API key env for each LLM node.
3. Node implementation anchor:
   `run_whitebox_layer1.ps1`, `run_whitebox_writing_contract.ps1`, `run_whitebox_outline.ps1`, `run_whitebox_draft_node.ps1`, `run_whitebox_pre_review.ps1`, `run_whitebox_post_review.ps1`, `run_whitebox_local_patch_loop.ps1`, and `run_whitebox_supplementary_evidence.ps1` were directly checked for read/write behavior.
