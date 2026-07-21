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
    def test_installs_traceable_skills_schema_and_validator_into_project(self):
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
            for name in ("openspec-propose", "openspec-sync-specs", "openspec-verify-change"):
                path = skills / name / "SKILL.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"---\nname: {name}\n---\n\n# Official {name}\n", encoding="utf-8")

            original_resolver = installer.resolve_official_schema
            installer.resolve_official_schema = lambda: official_schema
            try:
                result = installer.install_project(root)
            finally:
                installer.resolve_official_schema = original_resolver

            self.assertEqual(result["count"], 4)
            self.assertTrue(result["toolInstalled"])
            self.assertEqual((root / "openspec" / "config.yaml").read_text(encoding="utf-8"), "schema: traceable-spec-driven\n")
            for name in (
                "openspec-traceable-propose",
                "openspec-traceable-sync-specs",
                "openspec-verify-with-report",
                "requirement-packaging",
            ):
                self.assertTrue((skills / name / "SKILL.md").is_file())
            self.assertTrue((root / "openspec" / "schemas" / "traceable-spec-driven" / "schema.yaml").is_file())
            tool = root / "需求追踪验证工具"
            for name in ("validate_source_traceability.py", "traceability_report_gui.py", "requirements.txt"):
                self.assertTrue((tool / name).is_file())


if __name__ == "__main__":
    unittest.main()
