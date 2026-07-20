import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from validate_source_traceability import validate_change, write_markdown_report  # noqa: E402


SOURCE = """
### 协议管理接口

| **CodeBeamer reference:** | [SwRS-100](#[ISSUE:100]) |
| **Revision:** | 3 |

### 插件变更通知

| **CodeBeamer reference:** | [SwRS-200](#[ISSUE:200]) |
| **Revision:** | 5 |
"""


class TraceabilityValidationTest(unittest.TestCase):
    def make_change(self, yaml_text: str, spec_text: str):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "requirements.md").write_text(SOURCE, encoding="utf-8")
        change = root / "openspec" / "changes" / "demo"
        (change / "specs" / "demo").mkdir(parents=True)
        (change / "source-requirements.yaml").write_text(yaml_text, encoding="utf-8")
        (change / "specs" / "demo" / "spec.md").write_text(spec_text, encoding="utf-8")
        return temp, root

    def add_main_spec(self, root: Path, capability: str, spec_text: str):
        spec = root / "openspec" / "specs" / capability / "spec.md"
        spec.parent.mkdir(parents=True)
        spec.write_text(spec_text, encoding="utf-8")

    def test_complete_bidirectional_mapping_passes(self):
        yaml_text = """
source:
  document: requirements.md
  revision: v1
requirements:
  - id: SwRS-100
    revision: 3
    title: 协议管理接口
    status: mapped
    specs: [REQ-DEMO-001]
    acceptancePoints:
      - id: ACP-SwRS-100-001
        text: 返回协议列表
        status: mapped
        specs: [REQ-DEMO-001]
        scenarios: [查询成功]
  - id: SwRS-200
    revision: 5
    title: 插件变更通知
    status: excluded
    specs: []
    reason: 不属于本次能力范围
"""
        spec_text = """
## ADDED Requirements

<!--
id: REQ-DEMO-001
sources:
  - SwRS-100@3
-->

### Requirement: 查询协议
系统 SHALL 返回协议列表。

#### Scenario: 查询成功
- **WHEN** 用户查询
- **THEN** 返回列表
"""
        temp, root = self.make_change(yaml_text, spec_text)
        self.addCleanup(temp.cleanup)

        report = validate_change(root, "demo")

        self.assertTrue(report.passed)
        self.assertEqual(report.source_count, 2)
        self.assertEqual(report.registered_count, 2)
        self.assertEqual(report.status_counts["mapped"], 1)
        self.assertEqual(report.status_counts["excluded"], 1)
        self.assertEqual(report.issues, [])

    def test_reports_source_requirement_missing_from_yaml(self):
        yaml_text = """
source:
  document: requirements.md
  revision: v1
requirements:
  - id: SwRS-100
    revision: 3
    title: 协议管理接口
    status: mapped
    specs: [REQ-DEMO-001]
    acceptancePoints:
      - id: ACP-SwRS-100-001
        text: 返回协议列表
        status: mapped
        specs: [REQ-DEMO-001]
        scenarios: [查询成功]
"""
        spec_text = """
<!--
id: REQ-DEMO-001
sources:
  - SwRS-100@3
-->
### Requirement: 查询协议
系统 SHALL 返回协议列表。
#### Scenario: 查询成功
- **WHEN** 用户查询
- **THEN** 返回列表
"""
        temp, root = self.make_change(yaml_text, spec_text)
        self.addCleanup(temp.cleanup)

        report = validate_change(root, "demo")

        self.assertFalse(report.passed)
        self.assertTrue(any(i.code == "SRC_MISSING" and "SwRS-200" in i.message for i in report.issues))

    def test_mapped_requirement_requires_complete_acceptance_points(self):
        yaml_text = """
source:
  document: requirements.md
  revision: v1
requirements:
  - id: SwRS-100
    revision: 3
    title: 协议管理接口
    status: mapped
    specs: [REQ-DEMO-001]
"""
        spec_text = """
<!--
id: REQ-DEMO-001
sources: [SwRS-100@3]
-->
### Requirement: 查询协议
系统 SHALL 返回协议列表。
#### Scenario: 查询成功
- **WHEN** 用户查询
- **THEN** 返回列表
"""
        temp, root = self.make_change(yaml_text, spec_text)
        self.addCleanup(temp.cleanup)

        report = validate_change(root, "demo")

        self.assertFalse(report.passed)
        self.assertTrue(any(i.code == "MAPPED_ACCEPTANCE_POINTS_MISSING" for i in report.issues))

    def test_reports_reverse_link_and_revision_mismatch(self):
        yaml_text = """
source:
  document: requirements.md
  revision: v1
requirements:
  - id: SwRS-100
    revision: 2
    title: 协议管理接口
    status: mapped
    specs: [REQ-DEMO-001]
    acceptancePoints:
      - id: ACP-SwRS-100-001
        text: 返回协议列表
        status: mapped
        specs: [REQ-DEMO-001]
        scenarios: [查询成功]
  - id: SwRS-200
    revision: 5
    title: 插件变更通知
    status: excluded
    specs: []
    reason: 不适用
"""
        spec_text = """
<!--
id: REQ-DEMO-001
sources:
  - SwRS-200@5
-->
### Requirement: 查询协议
系统 SHALL 返回协议列表。
#### Scenario: 查询成功
- **WHEN** 用户查询
- **THEN** 返回列表
"""
        temp, root = self.make_change(yaml_text, spec_text)
        self.addCleanup(temp.cleanup)

        report = validate_change(root, "demo")

        codes = {issue.code for issue in report.issues}
        self.assertIn("REV_MISMATCH", codes)
        self.assertIn("LINK_FORWARD_ONLY", codes)
        self.assertIn("LINK_REVERSE_ONLY", codes)

    def test_parses_each_metadata_comment_in_multi_requirement_spec(self):
        yaml_text = """
source:
  document: requirements.md
  revision: v1
requirements:
  - id: SwRS-100
    revision: 3
    title: 协议管理接口
    status: mapped
    specs: [REQ-DEMO-001]
    acceptancePoints:
      - id: ACP-SwRS-100-001
        text: 返回协议列表
        status: mapped
        specs: [REQ-DEMO-001]
        scenarios: [查询成功]
  - id: SwRS-200
    revision: 5
    title: 插件变更通知
    status: mapped
    specs: [REQ-DEMO-002]
    acceptancePoints:
      - id: ACP-SwRS-200-001
        text: 通知节点
        status: mapped
        specs: [REQ-DEMO-002]
        scenarios: [通知成功]
"""
        spec_text = """
<!--
id: REQ-DEMO-001
sources: [SwRS-100@3]
-->
### Requirement: 查询协议
系统 SHALL 返回协议列表。
#### Scenario: 查询成功
- **WHEN** 用户查询
- **THEN** 返回列表

<!--
id: REQ-DEMO-002
sources: [SwRS-200@5]
-->
### Requirement: 通知节点
系统 SHALL 通知节点。
#### Scenario: 通知成功
- **WHEN** 配置变化
- **THEN** 节点收到通知
"""
        temp, root = self.make_change(yaml_text, spec_text)
        self.addCleanup(temp.cleanup)

        report = validate_change(root, "demo")

        self.assertTrue(report.passed, report.issues)
        self.assertEqual(report.spec_requirement_count, 2)

    def test_unchanged_requirement_is_covered_by_main_spec(self):
        current_yaml = """
source:
  document: requirements.md
  revision: v2
requirements:
  - id: SwRS-200
    revision: 5
    title: 插件变更通知
    status: excluded
    specs: []
    reason: 不属于本次能力范围
"""
        temp, root = self.make_change(current_yaml, "")
        self.addCleanup(temp.cleanup)
        main_spec = """
<!--
id: REQ-OLD-001
sources: [SwRS-100@3]
-->
### Requirement: 查询协议
系统 SHALL 返回协议列表。
#### Scenario: 查询成功
- **WHEN** 用户查询
- **THEN** 返回列表
"""
        self.add_main_spec(root, "demo", main_spec)

        report = validate_change(root, "demo")

        self.assertTrue(report.passed, report.issues)
        self.assertEqual(report.main_spec_covered_count, 1)
        self.assertEqual(report.current_handled_count, 1)

    def test_new_revision_in_source_must_be_handled_by_current_change(self):
        current_yaml = """
source:
  document: requirements.md
  revision: v2
requirements:
  - id: SwRS-200
    revision: 5
    title: 插件变更通知
    status: excluded
    specs: []
    reason: 不属于本次能力范围
"""
        temp, root = self.make_change(current_yaml, "")
        self.addCleanup(temp.cleanup)
        main_spec = """
<!--
id: REQ-OLD-001
sources: [SwRS-100@2]
-->
### Requirement: 查询协议
系统 SHALL 返回协议列表。
#### Scenario: 查询成功
- **WHEN** 用户查询
- **THEN** 返回列表
"""
        self.add_main_spec(root, "demo", main_spec)

        report = validate_change(root, "demo")

        self.assertFalse(report.passed)
        self.assertTrue(
            any(issue.code == "REVISION_NOT_HANDLED" and "SwRS-100" in issue.message for issue in report.issues)
        )

    def test_modified_delta_may_preserve_main_spec_source_without_current_yaml_entry(self):
        current_yaml = """
source:
  document: requirements.md
  revision: v2
requirements:
  - id: SwRS-100
    revision: 3
    title: 协议管理接口
    status: mapped
    specs: [REQ-DEMO-001]
    acceptancePoints:
      - id: ACP-SwRS-100-001
        text: 返回协议列表
        status: mapped
        specs: [REQ-DEMO-001]
        scenarios: [查询成功]
"""
        current_spec = """
<!--
id: REQ-DEMO-001
sources:
  - SwRS-100@3
  - SwRS-200@5
-->
### Requirement: 查询协议
系统 SHALL 返回协议列表。
#### Scenario: 查询成功
- **WHEN** 用户查询
- **THEN** 返回列表
"""
        temp, root = self.make_change(current_yaml, current_spec)
        self.addCleanup(temp.cleanup)
        main_spec = """
<!--
id: REQ-DEMO-001
sources:
  - SwRS-200@5
-->
### Requirement: 查询协议
系统 SHALL 返回协议列表。
#### Scenario: 查询成功
- **WHEN** 用户查询
- **THEN** 返回列表
"""
        self.add_main_spec(root, "demo", main_spec)

        report = validate_change(root, "demo")

        self.assertTrue(report.passed, report.issues)

    def test_writes_markdown_report_with_summary_and_issues(self):
        yaml_text = """
source:
  document: requirements.md
  revision: v1
requirements:
  - id: SwRS-100
    revision: 3
    title: 协议管理接口
    status: mapped
    specs: [REQ-DEMO-001]
"""
        spec_text = """
<!--
id: REQ-DEMO-001
sources: [SwRS-100@3]
-->
### Requirement: 查询协议
系统 SHALL 返回协议列表。
#### Scenario: 查询成功
- **WHEN** 用户查询
- **THEN** 返回列表
"""
        temp, root = self.make_change(yaml_text, spec_text)
        self.addCleanup(temp.cleanup)
        report = validate_change(root, "demo")
        output = root / "需求追踪验证报告.md"

        write_markdown_report(report, output)

        content = output.read_text(encoding="utf-8")
        self.assertIn("# 需求追踪验证报告", content)
        self.assertIn("demo", content)
        self.assertIn("原始文档需求数", content)
        self.assertIn("SwRS-200", content)
        self.assertIn("SRC_MISSING", content)
        self.assertIn("已完整映射到一个或多个 Spec Requirement", content)
        self.assertIn("尚未分析或映射到 Spec", content)
        self.assertIn("| `conflict` | 0 |", content)
        self.assertIn("## 验证详情", content)
        self.assertIn("### source-requirements.yaml 登记内容", content)
        self.assertIn("REQ-DEMO-001", content)
        self.assertIn("### 主规范已覆盖内容", content)


if __name__ == "__main__":
    unittest.main()
