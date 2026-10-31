import json
import os
import tempfile
import unittest


class TestState(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def test_roundtrip_save_load(self):
        from codedoctor.state import SessionState
        s = SessionState(project_path=self.root)
        s.profile = {"project_type": "CLI", "languages": ["python"]}
        s.findings = [{"rule_id": "PY002", "file": "a.py", "line": 3,
                       "col": 1, "severity": "functional", "message": "m"}]
        s.phases_done.append("profile")
        s.save()
        self.assertTrue(os.path.exists(os.path.join(self.root, ".code-doctor", "state.json")))
        s2 = SessionState.load(self.root)
        self.assertEqual(s2.profile["project_type"], "CLI")
        self.assertEqual(s2.phases_done, ["profile"])
        self.assertEqual(s2.findings[0]["rule_id"], "PY002")

    def test_load_missing_returns_fresh_state(self):
        from codedoctor.state import SessionState
        s = SessionState.load(self.root)
        self.assertEqual(s.phases_done, [])
        self.assertIsNone(s.profile)

    def test_load_corrupt_json_returns_fresh_state(self):
        from codedoctor.state import SessionState
        d = os.path.join(self.root, ".code-doctor")
        os.makedirs(d)
        with open(os.path.join(d, "state.json"), "w") as f:
            f.write("{not json!!")
        s = SessionState.load(self.root)
        self.assertEqual(s.phases_done, [])

    def test_summary_counts_by_severity(self):
        from codedoctor.state import SessionState
        s = SessionState(project_path=self.root)
        s.findings = [
            {"severity": "critical"}, {"severity": "critical"},
            {"severity": "functional"}, {"severity": "quality"},
        ]
        self.assertEqual(s.severity_counts(), {"critical": 2, "functional": 1, "quality": 1})


if __name__ == "__main__":
    unittest.main()
