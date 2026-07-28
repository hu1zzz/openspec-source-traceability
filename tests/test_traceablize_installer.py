import importlib.util
import tempfile
import unittest
from pathlib import Path


INSTALLER_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "traceablize"
    / "scripts"
    / "install_traceable_skills.py"
)


def load_installer():
    spec = importlib.util.spec_from_file_location("traceablize_installer", INSTALLER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TraceablizeInstallerTest(unittest.TestCase):
    def test_installs_traceable_skills_schema_and_removes_legacy_tool_files(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "project"
            official_schema = Path(temp) / "official-spec-driven"
            (official_schema / "templates").mkdir(parents=True)
            (official_schema / "schema.yaml").write_text(
                "name: spec-driven\nartifacts:\n- id: proposal\n  generates: proposal.md\n",
                encoding="utf-8",
            )
            for name in ("proposal.md", "spec.md", "design.md", "tasks.md"):
                (official_schema / "templates" / name).write_text("# template\n", encoding="utf-8")

            skills = root / ".codex" / "skills"
            for name in ("openspec-propose", "openspec-apply-change", "openspec-sync-specs", "openspec-verify-change"):
                path = skills / name / "SKILL.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"---\nname: {name}\n---\n\n# Official {name}\n", encoding="utf-8")

            original_resolver = installer.resolve_official_schema
            installer.resolve_official_schema = lambda: official_schema
            try:
                result = installer.install_project(root)
            finally:
                installer.resolve_official_schema = original_resolver

            self.assertEqual(result["count"], 5)
            self.assertIn("legacyToolFilesRemoved", result)
            self.assertEqual((root / "openspec" / "config.yaml").read_text(encoding="utf-8"), "schema: traceable-spec-driven\n")
            for name in (
                "openspec-traceable-propose",
                "openspec-traceable-apply-change",
                "openspec-traceable-sync-specs",
                "openspec-verify-with-report",
                "requirement-packaging",
            ):
                self.assertTrue((skills / name / "SKILL.md").is_file())
            self.assertTrue((root / "openspec" / "schemas" / "traceable-spec-driven" / "schema.yaml").is_file())
            self.assertTrue(
                (root / "openspec" / "schemas" / "traceable-spec-driven" / "templates" / "source-inventory.yaml").is_file()
            )
            generated_propose = (skills / "openspec-traceable-propose" / "SKILL.md").read_text(encoding="utf-8")
            generated_apply = (skills / "openspec-traceable-apply-change" / "SKILL.md").read_text(encoding="utf-8")
            generated_verify = (skills / "openspec-verify-with-report" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("source-inventory.yaml", generated_propose)
            self.assertIn("externalId", generated_propose)
            self.assertIn("fixed-format parser", generated_verify)
            self.assertIn("external-adapter", generated_propose)
            self.assertIn("product-decision", generated_propose)
            self.assertIn("all executable local tasks", generated_apply)
            self.assertIn("Implementation Paused", generated_apply)
            self.assertIn("## Mandatory termination gate", generated_apply)
            self.assertIn("Before any final reply, pause report, or end-of-turn", generated_apply)
            self.assertIn("unfinished `[local]` task", generated_apply)
            self.assertIn("progress ledger", generated_apply)
            self.assertIn("external-follow-up-registry.yaml", generated_apply)
            self.assertIn("explicit user confirmation", generated_apply)
            self.assertIn("external-follow-up-registry.yaml", generated_propose)
            self.assertIn("status: approved", generated_propose)
            self.assertIn("PASS_WITH_AUTHORIZED_HANDOFF", generated_verify)
            self.assertIn("must not count as implemented", generated_verify)
            self.assertIn("unexplained task split", generated_verify)
            tool = root / "需求追踪验证工具"
            tool.mkdir(exist_ok=True)
            legacy_files = ("validate_source_traceability.py", "traceability_report_gui.py", "requirements.txt")
            for name in legacy_files:
                (tool / name).write_text("legacy", encoding="utf-8")
            saved_report = tool / "saved-report.md"
            saved_report.write_text("keep", encoding="utf-8")
            installer.install_skills(root)
            self.assertFalse(any((tool / name).exists() for name in legacy_files))
            self.assertTrue(saved_report.is_file())


if __name__ == "__main__":
    unittest.main()
