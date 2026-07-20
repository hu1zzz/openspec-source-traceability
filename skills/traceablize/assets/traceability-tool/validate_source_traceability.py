#!/usr/bin/env python3
"""Validate source-document to OpenSpec Requirement traceability."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import yaml


VALID_STATUSES = {
    "pending",
    "mapped",
    "partial",
    "excluded",
    "not-applicable",
    "conflict",
}
STATUS_DESCRIPTIONS = {
    "pending": "已识别，但尚未分析或映射到 Spec；表示需求转换尚未完成。",
    "mapped": "已完整映射到一个或多个 Spec Requirement；必须至少关联一个 `REQ-*`。",
    "partial": "仅部分内容映射到 Spec；必须填写 `uncovered` 和 `reason`。",
    "excluded": "经明确决策不纳入当前变更；必须填写 `reason`，建议填写 `decision`。",
    "not-applicable": "不属于当前 change 的适用范围；必须填写 `reason`。",
    "conflict": "原始需求之间或与当前规范存在尚未解决的冲突；必须填写 `reason`。",
}
SOURCE_PATTERN = re.compile(
    r"CodeBeamer reference:\*\*\s*\|\s*\[?(SwRS-\d+).*?"
    r"\*\*Revision:\*\*\s*\|\s*(\d+)",
    re.DOTALL,
)
REQUIREMENT_HEADING = re.compile(r"^### Requirement:\s*(.+?)\s*$", re.MULTILINE)
COMMENT_BEFORE = re.compile(r"<!--((?:(?!-->).)*)-->\s*$", re.DOTALL)


@dataclass(frozen=True)
class Issue:
    code: str
    message: str


@dataclass
class Report:
    change: str
    source_document: str = ""
    source_count: int = 0
    registered_count: int = 0
    main_spec_covered_count: int = 0
    current_handled_count: int = 0
    spec_requirement_count: int = 0
    derived_requirement_count: int = 0
    status_counts: dict[str, int] = field(default_factory=dict)
    source_requirement_details: list[dict] = field(default_factory=list)
    main_spec_coverage_details: list[dict] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict:
        result = asdict(self)
        result["passed"] = self.passed
        return result


@dataclass(frozen=True)
class SpecRequirement:
    requirement_id: str
    sources: tuple[tuple[str, str | None], ...]
    derived: bool


def parse_source_document(text: str) -> dict[str, str]:
    return {source_id: revision for source_id, revision in SOURCE_PATTERN.findall(text)}


def parse_source_reference(value: object) -> tuple[str, str | None]:
    text = str(value).strip()
    if "@" not in text:
        return text, None
    source_id, revision = text.rsplit("@", 1)
    return source_id, revision


def parse_spec_file(path: Path, issues: list[Issue]) -> list[SpecRequirement]:
    text = path.read_text(encoding="utf-8")
    parsed: list[SpecRequirement] = []
    for heading in REQUIREMENT_HEADING.finditer(text):
        title = heading.group(1)
        comment = COMMENT_BEFORE.search(text[: heading.start()])
        if not comment:
            issues.append(Issue("REQ_METADATA_MISSING", f"{path}: Requirement“{title}”缺少追踪元数据"))
            continue
        try:
            metadata = yaml.safe_load(comment.group(1)) or {}
        except yaml.YAMLError as exc:
            issues.append(Issue("REQ_METADATA_INVALID", f"{path}: Requirement“{title}”元数据不是有效 YAML：{exc}"))
            continue
        requirement_id = metadata.get("id")
        if not requirement_id:
            issues.append(Issue("REQ_ID_MISSING", f"{path}: Requirement“{title}”缺少稳定 id"))
            continue
        sources = tuple(parse_source_reference(item) for item in (metadata.get("sources") or []))
        derived = metadata.get("origin") == "derived"
        if not sources and not derived:
            issues.append(Issue("REQ_SOURCE_MISSING", f"{requirement_id} 没有 sources，也未标记 origin: derived"))
        if derived and not metadata.get("rationale"):
            issues.append(Issue("DERIVED_REASON_MISSING", f"{requirement_id} 是派生 Requirement，但缺少 rationale"))
        parsed.append(SpecRequirement(str(requirement_id), sources, derived))
    return parsed


def resolve_source_path(project_root: Path, change_root: Path, document: str) -> Path:
    candidate = Path(document)
    if candidate.is_absolute():
        return candidate
    project_candidate = project_root / candidate
    return project_candidate if project_candidate.exists() else change_root / candidate


def load_main_spec_coverage(
    project_root: Path, issues: list[Issue]
) -> dict[tuple[str, str], set[str]]:
    """Return current (source id, revision) coverage declared by main specs."""
    coverage: dict[tuple[str, str], set[str]] = {}
    requirement_ids: set[str] = set()
    for spec_path in sorted((project_root / "openspec" / "specs").glob("**/*.md")):
        for requirement in parse_spec_file(spec_path, issues):
            if requirement.requirement_id in requirement_ids:
                issues.append(Issue("MAIN_REQ_ID_DUPLICATE", f"主规范中重复定义 {requirement.requirement_id}"))
            requirement_ids.add(requirement.requirement_id)
            for source_id, revision in requirement.sources:
                if revision is None:
                    issues.append(
                        Issue("MAIN_SOURCE_REV_MISSING", f"主规范 {requirement.requirement_id} 的来源 {source_id} 缺少 Revision")
                    )
                    continue
                coverage.setdefault((source_id, revision), set()).add(requirement.requirement_id)
    return coverage


def validate_change(project_root: Path, change_name: str) -> Report:
    project_root = Path(project_root).resolve()
    change_root = project_root / "openspec" / "changes" / change_name
    report = Report(change=change_name)
    mapping_path = change_root / "source-requirements.yaml"
    if not mapping_path.exists():
        report.issues.append(Issue("MAPPING_FILE_MISSING", f"不存在：{mapping_path}"))
        return report

    try:
        mapping = yaml.safe_load(mapping_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        report.issues.append(Issue("MAPPING_YAML_INVALID", f"source-requirements.yaml 解析失败：{exc}"))
        return report

    source_config = mapping.get("source") or {}
    document = str(source_config.get("document") or "")
    report.source_document = document
    source_path = resolve_source_path(project_root, change_root, document)
    if not document or not source_path.exists():
        report.issues.append(Issue("SOURCE_FILE_MISSING", f"找不到源需求文档：{document or '<未填写>'}"))
        source_requirements: dict[str, str] = {}
    else:
        source_bytes = source_path.read_bytes()
        source_requirements = parse_source_document(source_bytes.decode("utf-8-sig"))
        expected_hash = str(source_config.get("sha256") or "").strip()
        if expected_hash and not expected_hash.startswith("<"):
            actual_hash = hashlib.sha256(source_bytes).hexdigest()
            if actual_hash.lower() != expected_hash.lower():
                report.issues.append(Issue("SOURCE_HASH_MISMATCH", f"源需求文档 SHA-256 已变化：{source_path}"))
    report.source_count = len(source_requirements)

    entries = mapping.get("requirements") or []
    yaml_by_id: dict[str, dict] = {}
    statuses = Counter()
    for entry in entries:
        source_id = str(entry.get("id") or "").strip()
        if not source_id:
            report.issues.append(Issue("SOURCE_ID_MISSING", "YAML 中存在未填写 id 的需求"))
            continue
        if source_id in yaml_by_id:
            report.issues.append(Issue("SOURCE_ID_DUPLICATE", f"YAML 中重复登记 {source_id}"))
        yaml_by_id[source_id] = entry
        report.source_requirement_details.append(
            {
                "id": source_id,
                "revision": str(entry.get("revision") or ""),
                "title": str(entry.get("title") or ""),
                "status": str(entry.get("status") or ""),
                "specs": [str(value) for value in (entry.get("specs") or [])],
                "uncovered": str(entry.get("uncovered") or ""),
                "reason": str(entry.get("reason") or ""),
            }
        )
        status = str(entry.get("status") or "").strip()
        statuses[status] += 1
        if status not in VALID_STATUSES:
            report.issues.append(Issue("STATUS_INVALID", f"{source_id} 使用了无效状态：{status or '<空>'}"))
        specs = entry.get("specs") or []
        if status == "mapped" and not specs:
            report.issues.append(Issue("MAPPED_WITHOUT_SPEC", f"{source_id} 标记 mapped，但没有关联 Spec"))
        points = entry.get("acceptancePoints")
        if status == "mapped" and points is None:
            report.issues.append(Issue("MAPPED_ACCEPTANCE_POINTS_MISSING", f"{source_id} 标记 mapped，但缺少 acceptancePoints 验收点清单"))
        if points is not None:
            if not isinstance(points, list) or not points:
                report.issues.append(Issue("ACCEPTANCE_POINTS_INVALID", f"{source_id} 的 acceptancePoints 必须为非空列表"))
            else:
                for point in points:
                    point_id = str(point.get("id") or "<未命名>") if isinstance(point, dict) else "<无效条目>"
                    if not isinstance(point, dict) or not point.get("text"):
                        report.issues.append(Issue("ACCEPTANCE_POINT_INVALID", f"{source_id} 的 {point_id} 缺少 text"))
                        continue
                    if status == "mapped" and (point.get("status") != "mapped" or not point.get("specs") or not point.get("scenarios")):
                        report.issues.append(Issue("MAPPED_POINT_INCOMPLETE", f"{source_id} 标记 mapped，但验收点 {point_id} 未关联 Spec 和 Scenario"))
        if status in {"pending", "conflict"}:
            report.issues.append(Issue("STATUS_INCOMPLETE", f"{source_id} 状态为 {status}，需求转换尚未完成"))
        if status == "partial" and (not entry.get("uncovered") or not entry.get("reason")):
            report.issues.append(Issue("PARTIAL_DETAIL_MISSING", f"{source_id} 为 partial，但缺少 uncovered 或 reason"))
        if status in {"excluded", "not-applicable", "conflict"} and not entry.get("reason"):
            report.issues.append(Issue("STATUS_REASON_MISSING", f"{source_id} 状态为 {status}，但缺少 reason"))

    report.registered_count = len(yaml_by_id)
    report.status_counts = dict(sorted(statuses.items()))
    main_spec_coverage = load_main_spec_coverage(project_root, report.issues)
    main_spec_revisions: dict[str, set[str]] = {}
    for source_id, revision in main_spec_coverage:
        main_spec_revisions.setdefault(source_id, set()).add(revision)
    report.main_spec_coverage_details = [
        {
            "id": source_id,
            "revision": revision,
            "specs": sorted(requirement_ids),
        }
        for (source_id, revision), requirement_ids in sorted(main_spec_coverage.items())
        if source_requirements.get(source_id) == revision
    ]
    for source_id, source_revision in sorted(source_requirements.items()):
        current_entry = yaml_by_id.get(source_id)
        if current_entry is not None:
            if str(current_entry.get("revision")) == source_revision:
                report.current_handled_count += 1
            continue
        if (source_id, source_revision) in main_spec_coverage:
            report.main_spec_covered_count += 1
        elif source_id in main_spec_revisions:
            old_revisions = ", ".join(sorted(main_spec_revisions[source_id]))
            report.issues.append(
                Issue(
                    "REVISION_NOT_HANDLED",
                    f"{source_id} 当前 revision={source_revision}，主规范仅包含 revision={old_revisions}，当前 change 未处理新修订",
                )
            )
        else:
            report.issues.append(Issue("SRC_MISSING", f"原始文档中的 {source_id}@{source_revision} 未被主规范或当前 change 登记"))
    for source_id in sorted(set(yaml_by_id) - set(source_requirements)):
        report.issues.append(Issue("SRC_EXTRA", f"YAML 中的 {source_id} 不存在于原始文档"))
    for source_id in sorted(set(source_requirements) & set(yaml_by_id)):
        yaml_revision = yaml_by_id[source_id].get("revision")
        if yaml_revision is not None and str(yaml_revision) != source_requirements[source_id]:
            report.issues.append(
                Issue(
                    "REV_MISMATCH",
                    f"{source_id} 修订号不一致：原文={source_requirements[source_id]}，YAML={yaml_revision}",
                )
            )

    spec_requirements: dict[str, SpecRequirement] = {}
    for spec_path in sorted((change_root / "specs").glob("**/*.md")):
        for requirement in parse_spec_file(spec_path, report.issues):
            if requirement.requirement_id in spec_requirements:
                report.issues.append(Issue("REQ_ID_DUPLICATE", f"Spec 中重复定义 {requirement.requirement_id}"))
            spec_requirements[requirement.requirement_id] = requirement
    report.spec_requirement_count = len(spec_requirements)
    report.derived_requirement_count = sum(req.derived for req in spec_requirements.values())

    yaml_links = {
        (source_id, str(requirement_id))
        for source_id, entry in yaml_by_id.items()
        for requirement_id in (entry.get("specs") or [])
    }
    spec_links = {
        (source_id, requirement.requirement_id)
        for requirement in spec_requirements.values()
        for source_id, _ in requirement.sources
    }
    spec_link_revisions = {
        (source_id, requirement.requirement_id): revision
        for requirement in spec_requirements.values()
        for source_id, revision in requirement.sources
    }
    for source_id, requirement_id in sorted(yaml_links - spec_links):
        report.issues.append(
            Issue("LINK_FORWARD_ONLY", f"YAML 声明 {source_id} → {requirement_id}，但 Spec 没有对应反向链接")
        )
    for source_id, requirement_id in sorted(spec_links - yaml_links):
        revision = spec_link_revisions[(source_id, requirement_id)]
        if revision is not None and (source_id, revision) in main_spec_coverage:
            continue
        report.issues.append(
            Issue("LINK_REVERSE_ONLY", f"Spec 声明 {requirement_id} → {source_id}，但 YAML 没有对应正向链接")
        )
    for requirement in spec_requirements.values():
        for source_id, revision in requirement.sources:
            entry = yaml_by_id.get(source_id)
            if entry is not None and revision is not None and entry.get("revision") is not None:
                if str(entry["revision"]) != revision:
                    report.issues.append(
                        Issue(
                            "SPEC_REV_MISMATCH",
                            f"{requirement.requirement_id} 引用 {source_id}@{revision}，YAML 修订号为 {entry['revision']}",
                        )
                    )
    return report


def print_report(report: Report) -> None:
    print(f"需求追踪验证：{report.change}")
    print(f"源需求文档：{report.source_document or '<未填写>'}")
    print(f"原始文档需求数：{report.source_count}")
    print(f"YAML 登记需求数：{report.registered_count}")
    print(f"主规范覆盖数：{report.main_spec_covered_count}")
    print(f"当前 change 处理数：{report.current_handled_count}")
    print(f"Spec Requirement 数：{report.spec_requirement_count}")
    print(f"派生 Requirement 数：{report.derived_requirement_count}")
    print("状态统计：")
    if report.status_counts:
        for status, count in report.status_counts.items():
            print(f"  {status}: {count}")
    else:
        print("  <无>")
    if report.issues:
        print(f"\nFAIL：发现 {len(report.issues)} 个问题")
        for issue in report.issues:
            print(f"  [{issue.code}] {issue.message}")
    else:
        print("\nPASS：源需求登记完整，且与 Spec 的双向链接一致。")


def markdown_cell(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\r", " ").replace("\n", "<br>")


def write_markdown_report(report: Report, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = "通过" if report.passed else "未通过"
    lines = [
        "# 需求追踪验证报告",
        "",
        f"- **Change：** `{markdown_cell(report.change)}`",
        f"- **源需求文档：** `{markdown_cell(report.source_document or '<未填写>')}`",
        f"- **验证时间：** {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- **验证结果：** **{result}**",
        "",
        "## 覆盖概览",
        "",
        "| 指标 | 数量 |",
        "|---|---:|",
        f"| 原始文档需求数 | {report.source_count} |",
        f"| 当前 YAML 登记需求数 | {report.registered_count} |",
        f"| 主规范覆盖数 | {report.main_spec_covered_count} |",
        f"| 当前 change 处理数 | {report.current_handled_count} |",
        f"| 当前 change Spec Requirement 数 | {report.spec_requirement_count} |",
        f"| 派生 Requirement 数 | {report.derived_requirement_count} |",
        f"| 问题数 | {len(report.issues)} |",
        "",
        "## 当前需求状态",
        "",
        "| 状态 | 数量 | 状态说明 |",
        "|---|---:|---|",
    ]
    lines.extend(
        f"| `{status}` | {report.status_counts.get(status, 0)} | {markdown_cell(description)} |"
        for status, description in STATUS_DESCRIPTIONS.items()
    )
    lines.extend(["", "## 验证问题", ""])
    if report.issues:
        lines.extend(
            [
                "| 序号 | 代码 | 说明 |",
                "|---:|---|---|",
                *[
                    f"| {index} | `{markdown_cell(issue.code)}` | {markdown_cell(issue.message)} |"
                    for index, issue in enumerate(report.issues, start=1)
                ],
            ]
        )
    else:
        lines.append("未发现问题。源需求登记完整，且与 Spec 的双向链接一致。")
    lines.extend(
        [
            "",
            "## 判定说明",
            "",
            "- 主规范覆盖要求 `openspec/specs/**/*.md` 中存在稳定 Requirement ID 和完全匹配的 `来源ID@Revision`。",
            "- 当前 change 处理要求 `source-requirements.yaml` 与 delta Spec 的正反向链接一致。",
            "- 相同来源 ID 但 Revision 不同，不视为已覆盖。",
            "",
            "## 验证详情",
            "",
            "### source-requirements.yaml 登记内容",
            "",
        ]
    )
    if report.source_requirement_details:
        lines.extend(
            [
                "| 来源 ID | Revision | 标题 | 状态 | 关联 Spec | 未覆盖内容 | 原因/说明 |",
                "|---|---:|---|---|---|---|---|",
                *[
                    "| `{id}` | {revision} | {title} | `{status}` | {specs} | {uncovered} | {reason} |".format(
                        id=markdown_cell(detail["id"]),
                        revision=markdown_cell(detail["revision"]),
                        title=markdown_cell(detail["title"]),
                        status=markdown_cell(detail["status"]),
                        specs=markdown_cell(", ".join(detail["specs"]) or "—"),
                        uncovered=markdown_cell(detail["uncovered"] or "—"),
                        reason=markdown_cell(detail["reason"] or "—"),
                    )
                    for detail in report.source_requirement_details
                ],
            ]
        )
    else:
        lines.append("当前 `source-requirements.yaml` 没有登记需求。")
    lines.extend(["", "### 主规范已覆盖内容", ""])
    if report.main_spec_coverage_details:
        lines.extend(
            [
                "| 来源 ID | Revision | 主规范 Requirement |",
                "|---|---:|---|",
                *[
                    f"| `{markdown_cell(detail['id'])}` | {markdown_cell(detail['revision'])} | "
                    f"{markdown_cell(', '.join(detail['specs']))} |"
                    for detail in report.main_spec_coverage_details
                ],
            ]
        )
    else:
        lines.append("当前源需求文档中没有由主规范直接覆盖的需求。")
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="验证原始需求与 OpenSpec Spec 的双向追踪关系")
    parser.add_argument("--change", required=True, help="OpenSpec change 名称")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="项目根目录，默认当前目录")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    parser.add_argument(
        "--output",
        type=Path,
        help="Markdown 报告路径；相对路径基于项目根目录，默认：需求追踪验证报告.md",
    )
    args = parser.parse_args(argv)
    project_root = args.project_root.resolve()
    report = validate_change(project_root, args.change)
    output_path = args.output or Path("需求追踪验证报告.md")
    if not output_path.is_absolute():
        output_path = project_root / output_path
    write_markdown_report(report, output_path)
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print_report(report)
        print(f"\nMarkdown 报告：{output_path}")
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
