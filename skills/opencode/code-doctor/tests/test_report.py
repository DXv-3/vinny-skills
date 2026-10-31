import os
import tempfile
import unittest


class TestReport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def make_state(self):
        from codedoctor.state import SessionState
        s = SessionState(project_path=self.root)
        s.profile = {
            "project_type": "CLI", "languages": ["python"],
            "file_count": 3, "scope": "full",
            "na_flags": ["N/A — [Web] items"], "pitfalls": ["Python: mutable default"],
        }
        s.manifest_entries = [
            {"path": "a.py", "role": "source", "lang": "python",
             "imports": ["os"], "exports": ["main"]},
        ]
        s.findings = [
            {"severity": "critical", "file": "a.py", "line": 4, "col": 9,
             "rule_id": "GEN001", "message": "hardcoded credential"},
            {"severity": "quality", "file": "a.py", "line": 2, "col": 1,
             "rule_id": "PY004", "message": "open() without with"},
        ]
        s.phases_done = ["profile", "manifest", "issues"]
        return s

    def test_report_contains_all_phase6_sections(self):
        from codedoctor.report import generate_report
        md = generate_report(self.make_state())
        for section in ("## Code Review:", "### Profile", "### Files reviewed:",
                        "### Issues found:", "### Critical fixes:", "### Quality fixes:",
                        "### Deferred:", "### Smoke test:", "N/A items"):
            self.assertIn(section, md)

    def test_report_includes_counts_and_finding_lines(self):
        from codedoctor.report import generate_report
        md = generate_report(self.make_state())
        self.assertIn("Issues found: 2 (1 critical, 0 functional, 1 quality)", md)
        self.assertIn("a.py:4", md)
        self.assertIn("GEN001", md)
        self.assertIn("Files reviewed: 1", md)

    def test_report_na_flags_listed_with_reasons(self):
        from codedoctor.report import generate_report
        md = generate_report(self.make_state())
        self.assertIn("[Web]", md)


if __name__ == "__main__":
    unittest.main()
