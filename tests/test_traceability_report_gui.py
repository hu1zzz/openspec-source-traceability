import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from traceability_report_gui import discover_changes  # noqa: E402


class TraceabilityReportGuiTest(unittest.TestCase):
    def test_discovers_only_changes_with_source_requirements(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            changes = root / "openspec" / "changes"
            (changes / "alpha").mkdir(parents=True)
            (changes / "alpha" / "source-requirements.yaml").write_text("requirements: []", encoding="utf-8")
            (changes / "beta").mkdir()
            archived = changes / "archive" / "2026-01-01-old"
            archived.mkdir(parents=True)
            (archived / "source-requirements.yaml").write_text("requirements: []", encoding="utf-8")

            result = discover_changes(root)

            self.assertEqual(result, ["alpha"])


if __name__ == "__main__":
    unittest.main()
