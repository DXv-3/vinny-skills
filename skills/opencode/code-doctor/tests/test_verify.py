import os
import tempfile
import unittest


class TestVerify(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, content):
        path = os.path.join(self.root, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def verify(self, *files):
        from codedoctor.verify import verify_files
        return verify_files(files)

    def test_valid_python_passes(self):
        p = self.write("ok.py", "x = 1\n")
        results = self.verify(p)
        self.assertTrue(results[0]["ok"])
        self.assertEqual(results[0]["status"], "pass")

    def test_invalid_python_fails(self):
        p = self.write("bad.py", "def f(:\n")
        results = self.verify(p)
        self.assertFalse(results[0]["ok"])
        self.assertEqual(results[0]["status"], "fail")

    def test_missing_tool_is_tool_missing_not_failure(self):
        from codedoctor.verify import verify_files
        p = self.write("main.rs", "fn main() {}\n")
        results = verify_files([p], tool_lookup=lambda _bin: None)
        self.assertEqual(results[0]["status"], "tool-missing")
        self.assertTrue(results[0]["ok"])

    def test_unsupported_extension(self):
        p = self.write("data.csv", "a,b\n1,2\n")
        results = self.verify(p)
        self.assertEqual(results[0]["status"], "unsupported")

    def test_nonexistent_file_errors(self):
        results = self.verify(os.path.join(self.root, "nope.py"))
        self.assertFalse(results[0]["ok"])
        self.assertEqual(results[0]["status"], "error")

    def test_result_has_file_key_with_original_path(self):
        p = self.write("ok2.py", "y = 2\n")
        results = self.verify(p)
        self.assertEqual(results[0]["file"], p)


if __name__ == "__main__":
    unittest.main()
