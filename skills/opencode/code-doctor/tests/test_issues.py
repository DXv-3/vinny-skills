import os
import tempfile
import unittest


def make_project(root, files):
    for rel, content in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)


class RuleTest(unittest.TestCase):
    """Each test scans one synthetic file and asserts on findings."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def scan(self, files, lang_ext="py"):
        from codedoctor.issues import find_issues
        name = "sample." + lang_ext
        make_project(self.root, {name: files})
        return [f for f in find_issues(self.root) if f["file"] == name]

    def ids(self, findings):
        return sorted({f["rule_id"] for f in findings})

    # ---- Swift ----

    def test_swift_force_unwrap_flagged(self):
        out = self.scan("let url = URL(string: s)!\nprint(url)\n", "swift")
        self.assertIn("SW001", self.ids(out))

    def test_swift_bang_in_note_comment_not_flagged(self):
        out = self.scan("// wow!\nlet a = 1\n", "swift")
        self.assertNotIn("SW001", self.ids(out))

    def test_swift_try_bang_critical(self):
        out = self.scan('let s = try! String(contentsOfFile: p)\n', "swift")
        hits = [f for f in out if f["rule_id"] == "SW002"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["severity"], "critical")

    def test_swift_try_question_quality(self):
        out = self.scan("let s = try? String(contentsOfFile: p)\n", "swift")
        hits = [f for f in out if f["rule_id"] == "SW003"]
        self.assertEqual(hits[0]["severity"], "quality")

    # ---- Python ----

    def test_python_mutable_default_arg(self):
        out = self.scan("def f(x=[]):\n    return x\n")
        self.assertIn("PY001", self.ids(out))

    def test_python_bare_except(self):
        out = self.scan("try:\n    pass\nexcept:\n    pass\n")
        self.assertIn("PY002", self.ids(out))

    def test_python_broad_except_exception(self):
        out = self.scan("try:\n    pass\nexcept Exception:\n    pass\n")
        self.assertIn("PY002", self.ids(out))

    def test_python_is_boolean_comparison(self):
        out = self.scan("if flag is True:\n    pass\nif x is None:\n    pass\n")
        hits = [f for f in out if f["rule_id"] == "PY003"]
        self.assertEqual(len(hits), 1)

    def test_python_open_without_with(self):
        out = self.scan("f = open(path)\ndata = f.read()\n")
        self.assertIn("PY004", self.ids(out))

    def test_python_open_with_statement_clean(self):
        out = self.scan("with open(path) as f:\n    data = f.read()\n")
        self.assertNotIn("PY004", self.ids(out))

    def test_python_indented_with_open_clean(self):
        out = self.scan("def load():\n    with open(p) as f:\n        return f.read()\n")
        self.assertNotIn("PY004", self.ids(out))

    def test_python_method_open_not_flagged(self):
        out = self.scan("z = archive.open(member)\n")
        self.assertNotIn("PY004", self.ids(out))

    # ---- Go ----

    def test_go_discarded_err(self):
        out = self.scan("package main\n\nfunc main() {\n\tx, _ := strconv.Atoi(s)\n\t_ = err\n}\n", "go")
        self.assertIn("GO001", self.ids(out))

    def test_go_defer_inside_loop(self):
        out = self.scan(
            "package main\n\nfunc f() {\n\tfor i := range items {\n\t\tdefer mu.Unlock()\n\t}\n}\n",
            "go",
        )
        self.assertIn("GO002", self.ids(out))

    def test_go_defer_at_func_level_clean(self):
        out = self.scan(
            "package main\n\nfunc f() {\n\tdefer mu.Unlock()\n\tfor i := range items {\n\t\ttotal += i\n\t}\n}\n",
            "go",
        )
        self.assertNotIn("GO002", self.ids(out))

    # ---- Rust ----

    def test_rust_unwrap_flagged_critical(self):
        out = self.scan('fn main() {\n    let v = std::env::var("X").unwrap();\n}\n', "rs")
        hits = [f for f in out if f["rule_id"] == "RS001"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["severity"], "critical")

    # ---- JS / TS / React ----

    def test_js_env_without_fallback(self):
        out = self.scan('const k = process.env.API_KEY;\n', "js")
        self.assertIn("JS001", self.ids(out))

    def test_js_env_with_fallback_clean(self):
        out = self.scan('const k = process.env.API_KEY || "dev";\n', "js")
        self.assertNotIn("JS001", self.ids(out))

    def test_js_setinterval_without_clear(self):
        out = self.scan("setInterval(tick, 1000);\n", "js")
        self.assertIn("JS002", self.ids(out))
        sev = [f["severity"] for f in out if f["rule_id"] == "JS002"][0]
        self.assertEqual(sev, "critical")

    def test_js_setinterval_balanced_clean(self):
        out = self.scan(
            "const id = setInterval(tick, 1000);\nclearInterval(id);\n", "js"
        )
        self.assertNotIn("JS002", self.ids(out))

    def test_react_index_key(self):
        out = self.scan("items.map((it, index) => <Row key={index} item={it}/>)\n", "jsx")
        self.assertIn("REACT001", self.ids(out))

    def test_js_res_json_without_return(self):
        out = self.scan("app.get('/', (req, res) => {\n  res.json({ok: true});\n});\n", "js")
        self.assertIn("JS003", self.ids(out))

    # ---- Generic ----

    def test_hardcoded_secret(self):
        out = self.scan('api_key = "sk-a1b2c3d4e5f6g7h8i9j0k1l2m3"\n')
        self.assertIn("GEN001", self.ids(out))
        sev = [f["severity"] for f in out if f["rule_id"] == "GEN001"][0]
        self.assertEqual(sev, "critical")

    def test_aws_key_detected(self):
        out = self.scan('AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"\n')
        self.assertIn("GEN001", self.ids(out))

    def test_localhost_hardcoded(self):
        out = self.scan('resp = fetch("http://localhost:8080/api")\n', "ts")
        self.assertIn("GEN002", self.ids(out))

    def test_todo_marker(self):
        out = self.scan("# TODO: wire this up\nx = 1\n")
        self.assertIn("GEN003", self.ids(out))

    def test_fixme_marker_js(self):
        out = self.scan("// FIXME: broken\n", "js")
        self.assertIn("GEN003", self.ids(out))

    # ---- Engine behaviour ----

    def test_language_gating_swift_rule_not_on_python(self):
        out = self.scan("x = y!\n")  # python file with bang
        self.assertNotIn("SW001", self.ids(out))

    def test_findings_have_line_numbers_and_sorted(self):
        out = self.scan("try:\n    a\nexcept:\n    b\n\n# TODO later\nz = []\ndef g(q={}):\n    return q\n")
        self.assertTrue(all(f["line"] >= 1 for f in out))
        keys = [(f["file"], f["line"]) for f in out]
        self.assertEqual(keys, sorted(keys))

    def test_severities_are_valid(self):
        out = self.scan("try:\n    a\nexcept:\n    b\n")
        valid = {"critical", "functional", "quality"}
        self.assertTrue(all(f["severity"] in valid for f in out))


if __name__ == "__main__":
    unittest.main()
