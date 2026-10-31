import json
import os
import subprocess
import tempfile
import unittest


def make_project(root, files):
    for rel, content in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def manifest(self):
        from codedoctor.manifest import build_manifest
        return build_manifest(self.root)

    def entry(self, rel):
        m = self.manifest()
        for e in m["entries"]:
            if e["path"] == rel:
                return e
        raise AssertionError("entry %r not in %r" % (rel, [e["path"] for e in m["entries"]]))

    def test_walk_excludes_node_modules_and_pycache(self):
        make_project(self.root, {
            "app.py": "import os\n",
            "node_modules/lib/i.js": "x",
            "__pycache__/a.cpython-311.pyc": "x",
            ".git/config": "x",
        })
        m = self.manifest()
        paths = [e["path"] for e in m["entries"]]
        self.assertEqual(paths, ["app.py"])

    def test_includes_config_docs_build_files(self):
        make_project(self.root, {
            "README.md": "# hi\n",
            "Dockerfile": "FROM alpine\n",
            "Makefile": "all:\n\techo\n",
            "Info.plist": "<plist/>\n",
            "settings.json": "{}\n",
        })
        m = self.manifest()
        kinds = {e["path"]: e["role"] for e in m["entries"]}
        self.assertEqual(kinds["README.md"], "doc")
        self.assertEqual(kinds["Dockerfile"], "build")
        self.assertEqual(kinds["Makefile"], "build")
        self.assertEqual(kinds["Info.plist"], "config")
        self.assertEqual(kinds["settings.json"], "config")

    def test_python_imports_extracted(self):
        make_project(self.root, {"a.py": "import os\nimport mypkg.sub\nfrom flask import Flask\n"})
        e = self.entry("a.py")
        self.assertIn("os", e["imports"])
        self.assertIn("mypkg.sub", e["imports"])
        self.assertIn("flask", e["imports"])
        self.assertEqual(e["lang"], "python")

    def test_python_exports_public_defs(self):
        make_project(self.root, {"a.py": "def pub(): pass\ndef _priv(): pass\nclass Thing: pass\n"})
        e = self.entry("a.py")
        self.assertIn("pub", e["exports"])
        self.assertIn("Thing", e["exports"])
        self.assertNotIn("_priv", e["exports"])

    def test_js_imports_extracted(self):
        make_project(self.root, {
            "i.js": "const x = require('lodash');\nimport y from './util.js';\n",
        })
        e = self.entry("i.js")
        self.assertIn("lodash", e["imports"])
        self.assertIn("./util.js", e["imports"])

    def test_js_exports_extracted(self):
        make_project(self.root, {"i.js": "export function f() {}\nexport const c = 1;\n"})
        e = self.entry("i.js")
        self.assertTrue(any("f" in s for s in e["exports"]))
        self.assertTrue(any("c" in s for s in e["exports"]))

    def test_go_imports_extracted(self):
        make_project(self.root, {
            "main.go": 'package main\n\nimport (\n\t"fmt"\n\t"net/http"\n)\n',
        })
        e = self.entry("main.go")
        self.assertIn("fmt", e["imports"])
        self.assertIn("net/http", e["imports"])
        self.assertEqual(e["lang"], "go")

    def test_swift_imports_extracted(self):
        make_project(self.root, {"App.swift": "import SwiftUI\nimport Combine\n"})
        e = self.entry("App.swift")
        self.assertEqual(e["imports"], ["SwiftUI", "Combine"])

    def test_entry_point_detection(self):
        make_project(self.root, {
            "main.go": "package main\nfunc main(){}\n",
            "cli.py": "if __name__ == '__main__':\n    pass\n",
            "index.js": "console.log(1)\n",
        })
        m = self.manifest()
        eps = set(m["entry_points"])
        self.assertEqual(eps, {"main.go", "cli.py", "index.js"})

    def test_unreadable_file_counted_as_warning(self):
        make_project(self.root, {"ok.py": "x=1\n"})
        bad = os.path.join(self.root, "bad.rs")
        with open(bad, "w") as f:
            f.write("fn main(){}")
        os.chmod(bad, 0o000)
        try:
            m = self.manifest()
        finally:
            os.chmod(bad, 0o644)
        self.assertGreaterEqual(len(m["warnings"]), 1)

    def test_git_ls_files_preferred_when_repo(self):
        make_project(self.root, {"tracked.py": "x=1\n", "untracked.py": "y=2\n"})
        for args in (("init",), ("add", "tracked.py"), ("-c", "user.email=t@t"), ("commit", "-m", "x")):
            subprocess.run(["git", *args], cwd=self.root, capture_output=True)
        m = self.manifest()
        paths = [e["path"] for e in m["entries"]]
        self.assertEqual(paths, ["tracked.py"])


if __name__ == "__main__":
    unittest.main()
