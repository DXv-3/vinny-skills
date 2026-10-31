import importlib.util
import plistlib
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECOVERY_ROOT = Path("/var/folders/cx/vsh9bgxx4ybfjc4ltqtm6r5w0000gn/T/opencode/context-surfacer-recovery")
if not (ROOT / "sources").exists():
    sys.path.insert(0, str(RECOVERY_ROOT))
else:
    sys.path.insert(0, str(ROOT))

import daily_brief
import surf
from sources import hermes_db, state


class ContextSurfacerCompatibilityTests(unittest.TestCase):
    def test_state_search_uses_system_state_file(self):
        self.assertEqual(state.STATE_PATH.name, "SYSTEM-STATE.md")
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "SYSTEM-STATE.md"
            state_path.write_text("## INSTALLED\n- context-surfacer: present\n")
            previous = state.STATE_PATH
            state.STATE_PATH = state_path
            try:
                results = state.search_state("context-surfacer")
            finally:
                state.STATE_PATH = previous
        self.assertEqual(results[0]["section"], "INSTALLED")
        self.assertIn("context-surfacer", results[0]["matches"][0]["text"])

    def test_daily_brief_handles_missing_session_database(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            previous_db = daily_brief.DB_PATH
            previous_knowledge = daily_brief.KNOWLEDGE_DB
            previous_opencode = daily_brief.OPENCODE_DB
            previous_local_recall = daily_brief.LOCAL_RECALL_DB
            previous_subagent = daily_brief.SUBAGENT_DIR
            daily_brief.DB_PATH = root / "missing.sqlite"
            daily_brief.KNOWLEDGE_DB = root / "missing-knowledge.sqlite"
            daily_brief.OPENCODE_DB = root / "missing-opencode.db"
            daily_brief.LOCAL_RECALL_DB = root / "missing-recall.sqlite"
            daily_brief.SUBAGENT_DIR = root / "subagent-sessions"
            daily_brief.SUBAGENT_DIR.mkdir()
            (daily_brief.SUBAGENT_DIR / "session.md").write_text("# Session\n")
            try:
                brief = daily_brief.generate_brief()
            finally:
                daily_brief.DB_PATH = previous_db
                daily_brief.KNOWLEDGE_DB = previous_knowledge
                daily_brief.OPENCODE_DB = previous_opencode
                daily_brief.LOCAL_RECALL_DB = previous_local_recall
                daily_brief.SUBAGENT_DIR = previous_subagent
        self.assertEqual(brief["checks"]["subagent_sessions"]["status"], "stale")

    def test_daily_brief_accepts_items_only_knowledge_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            knowledge_db = root / "knowledge.sqlite"
            db = sqlite3.connect(str(knowledge_db))
            db.execute("CREATE TABLE items (created_at TEXT)")
            db.execute("INSERT INTO items VALUES ('2026-01-01T00:00:00')")
            db.commit()
            db.close()
            previous = daily_brief.KNOWLEDGE_DB
            daily_brief.KNOWLEDGE_DB = knowledge_db
            try:
                brief = daily_brief.generate_brief()
            finally:
                daily_brief.KNOWLEDGE_DB = previous
        self.assertIn(brief["checks"]["knowledge_base"]["status"], {"fresh", "stale"})


    def test_missing_hermes_database_is_a_noop(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = hermes_db.HERMES_DB
            hermes_db.HERMES_DB = Path(directory) / "missing-state.db"
            try:
                self.assertEqual(hermes_db.search_hermes("anything"), [])
                self.assertEqual(hermes_db.get_recent_sessions(), [])
            finally:
                hermes_db.HERMES_DB = previous

    def test_surf_reports_source_errors(self):
        previous = surf.search_sessions
        surf.search_sessions = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom"))
        try:
            result = surf.surf("query", sources=["sessions"], as_json=True)
        finally:
            surf.search_sessions = previous
        self.assertIn("sessions", result["errors"])
        self.assertIn("RuntimeError", result["errors"]["sessions"])

    def test_surf_accepts_empty_source_list(self):
        result = surf.surf("query", sources=[], as_json=True)
        self.assertEqual(result["sources_searched"], [])
        self.assertEqual(result["total_results"], 0)

    def test_refresh_script_calls_valid_importer(self):
        refresh = (ROOT / "scripts" / "refresh.sh").read_text()
        self.assertIn("chat_exporters.py\" --import-all", refresh)
        self.assertNotIn("browser_bridge.py\" --import-all", refresh)

    def test_launch_agent_health_check_reports_installed_without_action(self):
        with tempfile.TemporaryDirectory() as directory:
            plist = Path(directory) / "com.vinnyos.context-surfacer.refresh.plist"
            plist.write_text("<plist></plist>")
            previous = daily_brief.LAUNCHD_PLIST
            daily_brief.LAUNCHD_PLIST = plist
            try:
                check = daily_brief.check_launchd()
            finally:
                daily_brief.LAUNCHD_PLIST = previous
        self.assertEqual(check["status"], "installed")
        self.assertIsNone(check["action"])

    def test_launch_agent_runs_refresh_every_fifteen_minutes(self):
        plist_path = ROOT / "scripts" / "com.vinnyos.context-surfacer.refresh.plist"
        self.assertTrue(plist_path.exists())
        with plist_path.open("rb") as stream:
            plist = plistlib.load(stream)
        self.assertEqual(plist["Label"], "com.vinnyos.context-surfacer.refresh")
        self.assertEqual(plist["StartInterval"], 900)
        self.assertIn("refresh.sh", plist["ProgramArguments"][-1])


if __name__ == "__main__":
    unittest.main()
