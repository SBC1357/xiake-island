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


def baseline_fullview_path(candidate_id: str) -> str:
    base_dir = Path(
        r"D:\汇度编辑部1\侠客岛\docs\多Agent藏经阁实验\8条公式总实验目录\III期临床\07_白盒施工包\01_第一轮白盒完整可实验版\02_单题全貌档案"
    )
    return str(base_dir / case_file_name(candidate_id))


def code_block(text: str, info: str = "text") -> list[str]:
    return [f"```{info}", text, "```"]


def round_summaries(manifest: dict) -> list[str]:
    items = []
    for round_info in manifest.get("rounds", []):
        items.append(
            "第 {round} 轮：{before} -> {after}；qualified={qualified}；缺项 {missing_before} -> {missing_after}".format(
                round=round_info["round"],
                before=round_info["score_before"],
                after=round_info["score_after"],
                qualified=str(round_info["qualified_after"]).lower(),
                missing_before=round_info["missing_before"],
                missing_after=round_info["missing_after"],
            )
        )
    return items


def build_fullview(case_dir: Path) -> str:
    contract = read_json(case_dir / "whitebox_contract.json")
    revise_manifest = read_json(case_dir / "revise_manifest.json")
    final_score = read_json(case_dir / "score.json")
    writing_user_prompt = read_text(case_dir / "writing_user_prompt.txt")
    final_round = revise_manifest["rounds"][-1]
    final_round_path = Path(final_round["revised_draft_path"])
    final_draft = read_text(final_round_path)
    final_round_score_path = final_round_path.parent / "score.json"
    final_review = read_json(final_round_score_path)
    summaries = round_summaries(revise_manifest)

    lines: list[str] = []
    lines.append(f"# {contract['candidate_name']}（返修 Loop 单题全貌）")
    lines.append("")
    lines.append("状态：fixed-baseline 返修实验结果")
    lines.append("日期：2026-04-12")
    lines.append("用途：人工直接评估返修 loop 是否真的把同一份基线稿修好。本文只认固定基线稿上的返修轨迹，不拿整题重跑漂移冒充 loop 效果。")
    lines.append("")
    lines.append("## 当前有效口径")
    lines.append("")
    lines.append("1. 当前口径只认固定基线返修实验：同一份基线稿、同一份基线 prompt、同一路评分器，观察 `review -> revise -> rescore` 是否真正提分。")
    lines.append("2. 本文不替代白盒第一轮基线全貌；基线稿的完整首轮上下文仍回看基线全貌。")
    lines.append("3. 如果最终 `qualified=true` 但 `missing_or_misaligned` 仍残留，只能判定为“返修有用/能提分”，不能偷换成“题目已经完全收口”。")
    lines.append("4. fixed-baseline 返修实验当前以最终轮 `round_N/score.json` 作为最终缺口口径；根目录 `review_bundle.json` 仍停在基线稿口径，不能拿来冒充最终审稿结论。")
    lines.append("")
    lines.append(f"case_id: ``{contract['candidate_id']}``")
    lines.append(f"baseline_fullview: ``{baseline_fullview_path(contract['candidate_id'])}``")
    lines.append(f"eval_dir: ``{case_dir}``")
    lines.append("")
    lines.append("## 主阅读层")
    lines.append("")
    lines.append("### 一、人工审核先看")
    lines.append("")
    lines.append(
        "1. 基线分数：`{}`；最终分数：`{}`；最终达标：`{}`；实际返修轮次：`{}`。".format(
            revise_manifest["rounds"][0]["score_before"],
            revise_manifest["final_weighted_total"],
            str(revise_manifest["final_qualified"]).lower(),
            revise_manifest["actual_rounds"],
        )
    )
    if revise_manifest["final_qualified"]:
        lines.append("2. 当前裁定：这题在固定基线稿上经返修后从 `FAIL` 拉到 `PASS`，说明返修 loop 对本题有用。")
    else:
        lines.append("2. 当前裁定：这题在固定基线稿上经返修后仍未达标，说明返修 loop 对本题暂未形成有效闭环。")
    lines.append(f"3. 当前仍残留缺项：{join_inline(final_review.get('missing_or_misaligned', []))}")
    lines.append("4. 建议阅读顺序：先看“轮次轨迹”，再看每轮修稿任务书，最后看最终成稿全文和最终剩余缺口。")
    lines.append("")
    lines.append("### 二、轮次轨迹")
    lines.append("")
    for index, summary in enumerate(summaries, start=1):
        lines.append(f"{index}. {summary}")
    lines.append("")
    lines.append("### 三、基线写作合同与基线 prompt")
    lines.append("")
    wc = contract["writing_contract"]
    lines.append(
        "1. 受众：`{audience}`；体裁：`{genre}`；目标字数：`{target_word_count}`；写作目的：{purpose}".format(
            **wc
        )
    )
    lines.append("2. 基线 user prompt 全文：")
    lines.extend(code_block(writing_user_prompt))
    lines.append("")
    lines.append("### 四、每轮修稿任务书")
    lines.append("")
    for round_info in revise_manifest.get("rounds", []):
        round_dir = case_dir / "revise" / f"round_{round_info['round']}"
        revise_prompt = read_text(round_dir / "revise_prompt.md")
        lines.append(f"#### 第 {round_info['round']} 轮修稿任务书（全文）")
        lines.append("")
        lines.append(
            "本轮评分变化：`{}` -> `{}`；本轮缺项变化：`{}` -> `{}`；本轮达标：`{}`。".format(
                round_info["score_before"],
                round_info["score_after"],
                round_info["missing_before"],
                round_info["missing_after"],
                str(round_info["qualified_after"]).lower(),
            )
        )
        lines.extend(code_block(revise_prompt))
        lines.append("")
    lines.append("### 五、最终成稿全文")
    lines.append("")
    lines.extend(code_block(final_draft))
    lines.append("")
    lines.append("### 六、最终审核意见与剩余缺口")
    lines.append("")
    lines.append(
        "1. 最终总分与判定：`{}`；`qualified={}`。".format(
            final_score["weighted_total"], str(final_score["qualified"]).lower()
        )
    )
    lines.append(f"2. 最终 blocker：{join_inline(final_review.get('blocking_issues', []))}")
    lines.append(f"3. 最终剩余缺项：{join_inline(final_review.get('missing_or_misaligned', []))}")
    lines.append(f"4. 最终下一刀：{join_inline(final_review.get('next_actions', [])[:5])}")
    lines.append("")
    lines.append("## 工程附录")
    lines.append("")
    lines.append("### Runtime 指针")
    lines.append("")
    lines.append(f"1. `revise_manifest.json`：`{case_dir / 'revise_manifest.json'}`")
    lines.append(f"2. `score.json`：`{case_dir / 'score.json'}`")
    lines.append(f"3. `review_bundle.json`（基线口径，未自动刷新）：`{case_dir / 'review_bundle.json'}`")
    lines.append(f"4. `最终轮 score.json`（当前最终缺口口径）：`{final_round_score_path}`")
    lines.append(f"5. `writing_user_prompt.txt`：`{case_dir / 'writing_user_prompt.txt'}`")
    lines.append(f"6. `generated.txt`（基线稿）：`{case_dir / 'generated.txt'}`")
    counter = 7
    for round_info in revise_manifest.get("rounds", []):
        round_dir = case_dir / "revise" / f"round_{round_info['round']}"
        lines.append(f"{counter}. `round_{round_info['round']}\\revise_prompt.md`：`{round_dir / 'revise_prompt.md'}`")
        counter += 1
        lines.append(f"{counter}. `round_{round_info['round']}\\revised_draft.txt`：`{round_dir / 'revised_draft.txt'}`")
        counter += 1
        lines.append(f"{counter}. `round_{round_info['round']}\\score.json`：`{round_dir / 'score.json'}`")
        counter += 1
    lines.append("")
    lines.append("### 证据摘要")
    lines.append("")
    lines.append(
        "1. 已直接核对：`{}` 中轮次轨迹为 `{}`，最终 `weighted_total={}`、`qualified={}`。".format(
            case_dir / "revise_manifest.json",
            join_inline(summaries),
            revise_manifest["final_weighted_total"],
            revise_manifest["final_qualified"],
        )
    )
    lines.append(
        "2. 已直接核对：最终轮 `score.json` 为 `{}`，当前剩余缺项为 `{}`；根目录 `review_bundle.json` 仍停在基线口径。".format(
            final_round_score_path,
            join_inline(final_review.get("missing_or_misaligned", []))
        )
    )
    lines.append(
        "3. 已直接核对：每轮 `revise_prompt.md` 与最终 `revised_draft.txt` 已落盘，人工可直接顺着“基线稿 -> 修稿任务书 -> 最终稿”复盘 loop 过程。"
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
        manifest_path = case_dir / "revise_manifest.json"
        contract_path = case_dir / "whitebox_contract.json"
        if not manifest_path.exists() or not contract_path.exists():
            continue
        contract = read_json(contract_path)
        out_path = output_dir / case_file_name(contract["candidate_id"])
        out_path.write_text(build_fullview(case_dir), encoding="utf-8")

    print(f"[INFO] revise fullviews generated: {output_dir}")


if __name__ == "__main__":
    main()
