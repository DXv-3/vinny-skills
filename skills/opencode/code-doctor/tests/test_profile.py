import json
import os
import tempfile
import unittest


def make_project(root, files):
    for rel, content in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)


class TestProfile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def profile(self):
        from codedoctor.profile import profile_project
        return profile_project(self.root)

    def test_python_project_detected(self):
        make_project(self.root, {
            "pyproject.toml": "[project]\nname = 'x'\n",
            "main.py": "print(1)\n",
        })
        p = self.profile()
        self.assertIn("python", p["languages"])

    def test_node_project_detected_from_package_json(self):
        make_project(self.root, {
            "package.json": json.dumps({"name": "x", "dependencies": {"react": "^18"}}),
        })
        p = self.profile()
        self.assertIn("javascript", p["languages"])

    def test_go_project_detected(self):
        make_project(self.root, {"go.mod": "module x\n\ngo 1.21\n"})
        p = self.profile()
        self.assertIn("go", p["languages"])

    def test_rust_project_detected(self):
        make_project(self.root, {"Cargo.toml": "[package]\nname = \"x\"\n"})
        p = self.profile()
        self.assertIn("rust", p["languages"])

    def test_swift_mobile_app_detected(self):
        make_project(self.root, {"App.xcodeproj/project.pbxproj": "// !$*UTF8*$!\n"})
        p = self.profile()
        self.assertIn("swift", p["languages"])
        self.assertEqual(p["project_type"], "mobile app")

    def test_web_type_for_react_deps(self):
        make_project(self.root, {
            "package.json": json.dumps({"dependencies": {"react": "^18", "next": "^14"}}),
        })
        p = self.profile()
        self.assertEqual(p["project_type"], "web app")

    def test_cli_type_for_python_console_script(self):
        make_project(self.root, {
            "pyproject.toml": "[project.scripts]\nmytool = 'pkg:main'\n",
            "pkg/__init__.py": "",
        })
        p = self.profile()
        self.assertEqual(p["project_type"], "CLI")

    def test_scope_counts_files_and_sets_mode(self):
        make_project(self.root, {
            "a.py": "x=1\n",
            "b.py": "x=2\n",
            "sub/c.py": "x=3\n",
            "node_modules/junk/index.js": "junk",
        })
        p = self.profile()
        self.assertLessEqual(p["file_count"], 3)
        self.assertEqual(p["scope"], "full")

    def test_na_flags_populated(self):
        make_project(self.root, {"go.mod": "module x\n"})
        p = self.profile()
        self.assertIsInstance(p["na_flags"], list)
        joined = " ".join(p["na_flags"])
        self.assertTrue(len(joined) > 0)
        self.assertIn("[Web]", joined or "N/A")

    def test_pitfall_checklist_added_per_language(self):
        make_project(self.root, {"main.py": "print(1)\n"})
        p = self.profile()
        self.assertTrue(any("Python" in s or "python" in s for s in p["pitfalls"]))
        self.assertGreaterEqual(len(p["pitfalls"]), 3)

    def test_empty_dir_handled(self):
        p = self.profile()
        self.assertEqual(p["languages"], [])
        self.assertEqual(p["file_count"], 0)


if __name__ == "__main__":
    unittest.main()
