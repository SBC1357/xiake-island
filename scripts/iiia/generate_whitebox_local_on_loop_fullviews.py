from __future__ import annotations

import argparse
import json
from pathlib import Path


CASE_FILE_MAP = {
    "lecanemab_patient": "01_lecanemab_patient.md",
    "lecanemab_mechanism": "02_lecanemab_mechanism.md",
    "lecanemab_news": "03_lecanemab_news.md",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def join_inline(items) -> str:
    values = [str(item).strip() for item in items if str(item).strip()]
    return "；".join(values) if values else "无"


def case_file_name(candidate_id: str) -> str:
    return CASE_FILE_MAP.get(candidate_id, f"{candidate_id}.md")


def loop_fullview_path(candidate_id: str) -> str:
    base_dir = Path(
        r"D:\汇度编辑部1\侠客岛\docs\多Agent藏经阁实验\8条公式总实验目录\III期临床\07_白盒施工包\01_第一轮白盒完整可实验版\03_返修Loop单题全貌档案"
    )
    return str(base_dir / case_file_name(candidate_id))


def code_block(text: str, info: str = "text") -> list[str]:
    return [f"```{info}", text, "```"]


def get_patch_result_paths(round_dir: Path) -> list[Path]:
    result_dir = round_dir / "local_patch_results"
    if not result_dir.exists():
        return []
    return sorted(result_dir.glob("*.json"))


def build_round_task_summary(local_manifest: dict) -> list[str]:
    items = []
    for round_info in local_manifest.get("rounds", []):
        items.append(
            "第 {round} 轮：局部任务 {tasks} 条；应用 {applied} 条；精准执行 {precise} 条；关闭问题 {closed} 条；越界 {scope} 条；新风险 {risk} 条；分数 {before} -> {after}".format(
                round=round_info["round"],
                tasks=round_info["local_task_count"],
                applied=round_info["applied_task_count"],
                precise=round_info["precise_task_count"],
                closed=round_info["issue_closed_count"],
                scope=round_info["scope_violation_count"],
                risk=round_info["new_risk_count"],
                before=round_info["score_before"],
                after=round_info["score_after"],
            )
        )
    return items


def build_task_list_section(tasks: list[dict]) -> list[str]:
    lines: list[str] = []
    for task in tasks:
        lines.append(f"#### {task['task_id']}")
        lines.append("")
        lines.append(f"1. 级别：`{task['issue_level']}`")
        lines.append(f"2. 来源问题：{task['issue_source']}")
        lines.append(f"3. 目标段号：`{task['target_paragraph']}`")
        lines.append(f"4. 本轮只改什么：{task['instruction']}")
        lines.append(f"5. 验收标准：{join_inline(task.get('acceptance_criteria', []))}")
        lines.append(f"6. 不允许动的骨架：{join_inline(task.get('forbidden_changes', []))}")
        lines.append("")
    return lines


def build_patch_section(round_dir: Path) -> list[str]:
    lines: list[str] = []
    for result_path in get_patch_result_paths(round_dir):
        result = read_json(result_path)
        lines.append(f"#### {result['task_id']}")
        lines.append("")
        lines.append(
            "1. 核验结果：`{status}`；executed_precisely=`{precise}`；issue_addressed=`{issue}`；scope_respected=`{scope}`；introduced_new_risk=`{risk}`；applied=`{applied}`。".format(
                status=result["status"],
                precise=str(result["executed_precisely"]).lower(),
                issue=str(result["issue_addressed"]).lower(),
                scope=str(result["scope_respected"]).lower(),
                risk=str(result["introduced_new_risk"]).lower(),
                applied=str(result["applied"]).lower(),
            )
        )
        lines.append(f"2. 核验理由：{result['reason']}")
        lines.append("3. 改前段落：")
        lines.extend(code_block(result["original_paragraph"]))
        lines.append("4. 改后段落：")
        lines.extend(code_block(result["revised_paragraph"]))
        lines.append("")
    return lines


def build_fullview(case_dir: Path) -> str:
    contract = read_json(case_dir / "whitebox_contract.json")
    local_manifest = read_json(case_dir / "local_revise_manifest.json")
    final_score = read_json(case_dir / "score.json")
    current_draft = read_text(case_dir / "draft.txt")
    round_info = local_manifest["rounds"][-1]
    round_dir = case_dir / "local_revise" / f"round_{round_info['round']}"
    routing = read_json(round_dir / "revision_task_list.json")
    tasks = routing.get("tasks", [])
    summaries = build_round_task_summary(local_manifest)

    lines: list[str] = []
    lines.append(f"# {contract['candidate_name']}（整稿 Loop 后局部返修单题全貌）")
    lines.append("")
    lines.append("状态：loop 成稿后的局部返修实验结果")
    lines.append("日期：2026-04-12")
    lines.append("用途：人工直接评估“整稿 loop 成稿”再做一轮局部返修，是否真的能精准命中剩余问题。本文主判据是执行精度与问题关闭率，不拿最终分数作为唯一裁决。")
    lines.append("")
    lines.append("## 当前有效口径")
    lines.append("")
    lines.append("1. 当前口径只认：整稿 loop 成稿作为新基线，再在同一份 loop 成稿上做一轮 local revise。")
    lines.append("2. 本文不替代上一层整稿 loop 全貌；整稿 loop 本身的轮次轨迹仍回看上一层返修 Loop 全貌。")
    lines.append("3. 本文主判据：`execution_precision_rate`、`issue_close_rate`、`scope_violation_count`、`introduced_new_risk`。")
    lines.append("4. 如果分数不涨，但局部返修执行精度高、问题关闭率高、无越界、无新风险，只能判定为“局部返修执行有效但评分未继续给分”，不能偷换成“局部返修没用”。")
    lines.append("")
    lines.append(f"case_id: `{contract['candidate_id']}`")
    lines.append(f"loop_fullview: `{loop_fullview_path(contract['candidate_id'])}`")
    lines.append(f"eval_dir: `{case_dir}`")
    lines.append("")
    lines.append("## 主阅读层")
    lines.append("")
    lines.append("### 一、人工审核先看")
    lines.append("")
    lines.append(
        "1. loop 基线分数：`{before}`；局部返修后分数：`{after}`；最终达标：`{qualified}`。".format(
            before=round_info["score_before"],
            after=round_info["score_after"],
            qualified=str(round_info["qualified_after"]).lower(),
        )
    )
    lines.append(
        "2. 本轮主判据：执行精度率 `{}`；问题关闭率 `{}`；越界 `{}`；新风险 `{}`。".format(
            local_manifest["execution_precision_rate"],
            local_manifest["issue_close_rate"],
            local_manifest["total_scope_violation_count"],
            local_manifest["total_new_risk_count"],
        )
    )
    lines.append(f"3. 当前裁定：{round_info['routing_summary']}")
    lines.append("4. 建议阅读顺序：先看“轮次轨迹”，再看“局部任务清单”，然后看“逐任务执行结果”，最后看当前稿件全文和最终剩余缺口。")
    lines.append("")
    lines.append("### 二、轮次轨迹")
    lines.append("")
    for index, summary in enumerate(summaries, start=1):
        lines.append(f"{index}. {summary}")
    lines.append("")
    lines.append("### 三、本轮局部任务清单")
    lines.append("")
    lines.extend(build_task_list_section(tasks))
    lines.append("### 四、逐任务执行结果")
    lines.append("")
    lines.extend(build_patch_section(round_dir))
    lines.append("### 五、当前稿件全文（局部返修后）")
    lines.append("")
    lines.extend(code_block(current_draft))
    lines.append("")
    lines.append("### 六、当前评分与剩余缺口")
    lines.append("")
    lines.append(
        "1. 当前总分与判定：`{}`；`qualified={}`。".format(
            final_score["weighted_total"], str(final_score["qualified"]).lower()
        )
    )
    lines.append(f"2. 当前 blocker：{join_inline(final_score.get('blocking_issues', []))}")
    lines.append(f"3. 当前剩余缺项：{join_inline(final_score.get('missing_or_misaligned', []))}")
    lines.append(f"4. 当前下一刀：{join_inline(final_score.get('next_actions', [])[:5])}")
    lines.append("")
    lines.append("## 工程附录")
    lines.append("")
    lines.append("### Runtime 指针")
    lines.append("")
    lines.append(f"1. `local_revise_manifest.json`：`{case_dir / 'local_revise_manifest.json'}`")
    lines.append(f"2. `revise_manifest.json`（沿用统一入口的总返修摘要）：`{case_dir / 'revise_manifest.json'}`")
    lines.append(f"3. `score.json`：`{case_dir / 'score.json'}`")
    lines.append(f"4. `draft.txt`：`{case_dir / 'draft.txt'}`")
    lines.append(f"5. `round_1\\revision_task_list.json`：`{round_dir / 'revision_task_list.json'}`")
    lines.append(f"6. `round_1\\revised_draft.txt`：`{round_dir / 'revised_draft.txt'}`")
    result_paths = get_patch_result_paths(round_dir)
    counter = 7
    for path in result_paths:
        lines.append(f"{counter}. `{path.name}`：`{path}`")
        counter += 1
    lines.append("")
    lines.append("### 证据摘要")
    lines.append("")
    lines.append(
        "1. 已直接核对：`{}` 中执行精度率为 `{}`、问题关闭率为 `{}`、最终总分为 `{}`。".format(
            case_dir / "local_revise_manifest.json",
            local_manifest["execution_precision_rate"],
            local_manifest["issue_close_rate"],
            local_manifest["final_weighted_total"],
        )
    )
    lines.append(
        "2. 已直接核对：`{}` 中逐任务核验结果为 `{}`，可直接复盘哪些 patch 被应用、哪些被挡下。".format(
            round_dir / "local_patch_results",
            join_inline([f"{path.stem}:{read_json(path)['status']}" for path in result_paths]),
        )
    )
    lines.append(
        "3. 已直接核对：当前 `draft.txt` 与 `score.json` 已落盘，人工可顺着“loop 基线全貌 -> 本轮局部任务 -> 逐 patch 结果 -> 当前稿件”评估局部返修是否真的有效。"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-root", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    eval_root = Path(args.eval_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for case_dir in sorted(p for p in eval_root.iterdir() if p.is_dir()):
        manifest_path = case_dir / "local_revise_manifest.json"
        contract_path = case_dir / "whitebox_contract.json"
        if not manifest_path.exists() or not contract_path.exists():
            continue
        contract = read_json(contract_path)
        out_path = output_dir / case_file_name(contract["candidate_id"])
        out_path.write_text(build_fullview(case_dir), encoding="utf-8")

    print(f"[INFO] local-on-loop fullviews generated: {output_dir}")


if __name__ == "__main__":
    main()
