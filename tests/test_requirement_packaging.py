import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "traceablize"
    / "assets"
    / "requirement-packaging"
    / "scripts"
    / "package_requirements.py"
)
SPEC = importlib.util.spec_from_file_location("package_requirements", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PackageRequirementsTest(unittest.TestCase):
    def setUp(self):
        self.output_dir = Path(tempfile.mkdtemp()) / "packages"

    def tearDown(self):
        shutil.rmtree(self.output_dir.parent)

    def test_writes_executable_package_and_global_audit_files(self):
        source = """# Brand management
- Requirement ID: SRC-1
- Revision: 1

The system shall create, list, and delete brands.
"""

        result = MODULE.package_requirements(source, "sample.md", self.output_dir)

        self.assertEqual(result["executablePackages"], 1)
        self.assertTrue((self.output_dir / "manifest.yaml").exists())
        self.assertTrue((self.output_dir / "validation-report.md").exists())
        self.assertTrue((self.output_dir / "unresolved-items.md").exists())
        package_inputs = list(self.output_dir.glob("01-*/input.md"))
        self.assertEqual(len(package_inputs), 1)


if __name__ == "__main__":
    unittest.main()
