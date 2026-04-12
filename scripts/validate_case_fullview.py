from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_HEADER_FIELDS = ("状态：", "日期：", "用途：")
REQUIRED_METADATA = ("case_id:", "task_id:", "run_dir:")
REQUIRED_TOP_LEVEL_HEADINGS = ("当前有效口径", "当前明确缺项", "主阅读层", "工程附录")
REQUIRED_SUBSECTIONS = (
    "人工审核先看",
    "本轮真正喂给写手的材料（人工整理版）",
    "本轮给模型的 prompt 全文",
    "当前稿件全文",
    "当前审核意见与返修抓手",
    "Runtime 指针",
    "本轮关键证据",
    "materials 指针",
    "prompt 指针",
    "评分结果",
    "本轮真实 blocker",
    "证据摘要",
)
REQUIRED_RUNTIME_ARTIFACTS = (
    "run_summary.md",
    "task_detail.json",
    "generated.txt",
    "review_bundle.json",
    "score.json",
)
REQUIRED_SCORE_DIMENSIONS = (
    "任务完成度",
    "关键事实与关键数字覆盖",
    "受众匹配与文风匹配",
    "AI味儿控制",
    "结构与信息取舍",
    "标题角度与稿型适配",
    "幻觉与越界编造控制",
)
KNOWN_HEADINGS = set(REQUIRED_TOP_LEVEL_HEADINGS) | set(REQUIRED_SUBSECTIONS)


class ValidationIssue:
    def __init__(self, path: Path, message: str) -> None:
        self.path = path
        self.message = message


def normalize_heading_name(name: str) -> str:
    normalized = name.strip()
    normalized = re.sub(r"^[（(]?[一二三四五六七八九十0-9]+[)）.、]\s*", "", normalized)
    return normalized.strip()


def extract_heading_sections(text: str) -> dict[str, str]:
    matches = []
    for match in re.finditer(r"^(#{2,3})\s+(.+?)\s*$", text, flags=re.MULTILINE):
        heading_name = normalize_heading_name(match.group(2))
        if heading_name in KNOWN_HEADINGS:
            matches.append((match, heading_name))
    sections: dict[str, str] = {}
    for index, (match, heading_name) in enumerate(matches):
        heading_level = len(match.group(1))
        start = match.end()
        end = len(text)
        for next_match, _next_name in matches[index + 1 :]:
            next_level = len(next_match.group(1))
            if next_level <= heading_level:
                end = next_match.start()
                break
        sections[heading_name] = text[start:end].strip()
    return sections


def has_numbered_items(section_text: str, minimum: int = 1) -> bool:
    return len(re.findall(r"(?m)^\s*\d+\.\s+", section_text)) >= minimum


def looks_like_full_article(section_text: str) -> bool:
    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", section_text)
        if paragraph.strip()
    ]
    prose_paragraphs = [
        paragraph
        for paragraph in paragraphs
        if not re.match(r"^\s*(\d+\.|- |\* |```)", paragraph)
    ]
    total_chars = sum(len(paragraph) for paragraph in prose_paragraphs)
    return len(prose_paragraphs) >= 3 and total_chars >= 250


def count_fenced_blocks(section_text: str) -> int:
    return len(re.findall(r"(?ms)^```.+?^```", section_text))


def validate_doc(path: Path) -> list[ValidationIssue]:
    text = path.read_text(encoding="utf-8")
    issues: list[ValidationIssue] = []

    for marker in REQUIRED_METADATA:
        if marker not in text:
            issues.append(ValidationIssue(path, f"缺少元数据 `{marker}`"))
    for field in REQUIRED_HEADER_FIELDS:
        if field not in text:
            issues.append(ValidationIssue(path, f"缺少头部字段 `{field}`"))

    sections = extract_heading_sections(text)
    for heading in REQUIRED_TOP_LEVEL_HEADINGS:
        if heading not in sections:
            issues.append(ValidationIssue(path, f"缺少章节 `## {heading}`"))
    for heading in REQUIRED_SUBSECTIONS:
        if heading not in sections:
            issues.append(ValidationIssue(path, f"缺少章节 `### {heading}`"))

    scope_section = sections.get("当前有效口径", "")
    if not has_numbered_items(scope_section, minimum=2):
        issues.append(ValidationIssue(path, "`当前有效口径` 至少需要 2 条编号口径"))

    missing_section = sections.get("当前明确缺项", "")
    if not has_numbered_items(missing_section, minimum=2):
        issues.append(ValidationIssue(path, "`当前明确缺项` 至少需要 2 条编号缺项"))

    reviewer_section = sections.get("人工审核先看", "")
    if len(reviewer_section.strip()) < 120 or not has_numbered_items(reviewer_section, minimum=4):
        issues.append(ValidationIssue(path, "`人工审核先看` 过短，未形成可执行审稿入口"))

    materials_section = sections.get("本轮真正喂给写手的材料（人工整理版）", "")
    if "人工阅读提示" not in materials_section:
        issues.append(ValidationIssue(path, "`本轮真正喂给写手的材料（人工整理版）` 缺少 `人工阅读提示`"))
    if len(materials_section.strip()) < 180:
        issues.append(ValidationIssue(path, "`本轮真正喂给写手的材料（人工整理版）` 过短，疑似只有路径"))

    prompt_body_section = sections.get("本轮给模型的 prompt 全文", "")
    if "system prompt" not in prompt_body_section.lower():
        issues.append(ValidationIssue(path, "`本轮给模型的 prompt 全文` 缺少 system prompt"))
    if "user prompt" not in prompt_body_section.lower():
        issues.append(ValidationIssue(path, "`本轮给模型的 prompt 全文` 缺少 user prompt"))
    if count_fenced_blocks(prompt_body_section) < 2:
        issues.append(ValidationIssue(path, "`本轮给模型的 prompt 全文` 至少需要 2 个代码块承载 prompt 正文"))

    article_section = sections.get("当前稿件全文", "")
    if not looks_like_full_article(article_section):
        issues.append(ValidationIssue(path, "`当前稿件全文` 看起来不像完整正文，疑似只写了路径或摘要"))

    review_section = sections.get("当前审核意见与返修抓手", "")
    if len(review_section.strip()) < 150 or not has_numbered_items(review_section, minimum=4):
        issues.append(ValidationIssue(path, "`当前审核意见与返修抓手` 过短，未形成返修抓手"))
    if "返修" not in review_section and "改" not in review_section:
        issues.append(ValidationIssue(path, "`当前审核意见与返修抓手` 未写出明确修改动作"))

    runtime_section = sections.get("Runtime 指针", "")
    for artifact in REQUIRED_RUNTIME_ARTIFACTS:
        if artifact not in runtime_section:
            issues.append(ValidationIssue(path, f"`Runtime 指针` 缺少 `{artifact}`"))

    materials_pointer_section = sections.get("materials 指针", "")
    if "materials_full.json" not in materials_pointer_section and "本轮未生成 materials_full.json" not in materials_pointer_section:
        issues.append(ValidationIssue(path, "`materials 指针` 未写出 `materials_full.json` 或明确缺项"))

    prompt_pointer_section = sections.get("prompt 指针", "")
    if "writing_system_prompt.txt" not in prompt_pointer_section and "writing.system_prompt" not in prompt_pointer_section:
        issues.append(ValidationIssue(path, "`prompt 指针` 未写出 system prompt 指针"))
    if "writing_user_prompt.txt" not in prompt_pointer_section and "writing.user_prompt" not in prompt_pointer_section:
        issues.append(ValidationIssue(path, "`prompt 指针` 未写出 user prompt 指针"))

    score_section = sections.get("评分结果", "")
    if "本轮未执行评分" in score_section:
        if "原因" not in score_section:
            issues.append(ValidationIssue(path, "`评分结果` 标记未评分时必须补充原因"))
    else:
        for required_label in ("总分", "达标结论", "评分状态", "各维度"):
            if required_label not in score_section:
                issues.append(ValidationIssue(path, f"`评分结果` 缺少 `{required_label}`"))
        for dimension in REQUIRED_SCORE_DIMENSIONS:
            if dimension not in score_section:
                issues.append(ValidationIssue(path, f"`评分结果` 缺少维度 `{dimension}`"))

    blocker_section = sections.get("本轮真实 blocker", "")
    if len(blocker_section.strip()) < 10 or not has_numbered_items(blocker_section):
        issues.append(ValidationIssue(path, "`本轮真实 blocker` 为空或未写成可核对条目"))

    evidence_section = sections.get("证据摘要", "")
    if not has_numbered_items(evidence_section, minimum=2):
        issues.append(ValidationIssue(path, "`证据摘要` 至少需要 2 条编号证据"))

    return issues


def iter_docs(paths: list[Path]) -> list[Path]:
    docs: list[Path] = []
    for path in paths:
        if path.is_dir():
            docs.extend(
                candidate
                for candidate in sorted(path.glob("*.md"))
                if candidate.name != "00_单题全貌模板.md"
            )
        else:
            docs.append(path)
    return docs


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Validate case fullview markdown files.")
    parser.add_argument("paths", nargs="+", help="Markdown file or directory to validate")
    args = parser.parse_args(argv)

    targets = [Path(raw).resolve() for raw in args.paths]
    docs = iter_docs(targets)
    if not docs:
        print("No markdown files found.", file=sys.stderr)
        return 1

    all_issues: list[ValidationIssue] = []
    for doc in docs:
        all_issues.extend(validate_doc(doc))

    if all_issues:
        for issue in all_issues:
            print(f"{issue.path}: {issue.message}")
        return 1

    for doc in docs:
        print(f"OK {doc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
