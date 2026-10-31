import json
import os
import subprocess
import sys
import tempfile
import unittest


SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRY = os.path.join(SKILL_DIR, "code_doctor.py")


def make_project(root, files):
    for rel, content in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, ENTRY, *args],
            capture_output=True, text=True, timeout=120,
        )

    def test_scan_exits_1_on_findings(self):
        make_project(self.root, {"a.py": "try:\n    x\nexcept:\n    pass\n"})
        r = self.cli("scan", self.root)
        self.assertEqual(r.returncode, 1)

    def test_scan_json_output_shape(self):
        make_project(self.root, {"a.py": "except_msg = None\ntry:\n    x\nexcept:\n    pass\n"})
        r = self.cli("scan", "--json", self.root)
        data = json.loads(r.stdout)
        for key in ("profile", "manifest", "findings", "summary"):
            self.assertIn(key, data)
        self.assertTrue(any(f["rule_id"] == "PY002" for f in data["findings"]))
        self.assertEqual(data["summary"]["functional"], 1)

    def test_profile_clean_exit_0(self):
        make_project(self.root, {"go.mod": "module x\n"})
        r = self.cli("profile", self.root)
        self.assertEqual(r.returncode, 0)
        self.assertIn("project_type", r.stdout)

    def test_check_syntax_pass_and_fail(self):
        good = os.path.join(self.root, "good.py")
        bad = os.path.join(self.root, "bad.py")
        with open(good, "w") as f:
            f.write("x = 1\n")
        with open(bad, "w") as f:
            f.write("def (:\n")
        self.assertEqual(self.cli("check-syntax", good).returncode, 0)
        self.assertEqual(self.cli("check-syntax", bad).returncode, 1)

    def test_run_writes_state_and_report(self):
        make_project(self.root, {"m.py": "# TODO x\nv = 2\n"})
        r = self.cli("run", self.root)
        self.assertEqual(r.returncode, 1)  # findings present
        state_path = os.path.join(self.root, ".code-doctor", "state.json")
        self.assertTrue(os.path.exists(state_path))
        with open(state_path) as f:
            state = json.load(f)
        self.assertIn("profile", state["phases_done"])
        self.assertIn("issues", state["phases_done"])
        r2 = self.cli("report", self.root)
        self.assertEqual(r2.returncode, 0)
        self.assertIn("## Code Review:", r2.stdout)

    def test_missing_dir_exit_2(self):
        r = self.cli("scan", os.path.join(self.root, "ghost"))
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
