"""Checkpoint persistence — chains Code Doctor phases across CLI invocations."""

import json
import os
import time

STATE_DIR = ".code-doctor"
STATE_FILE = "state.json"


class SessionState:
    def __init__(self, project_path):
        self.project_path = os.path.abspath(project_path)
        self.created_at = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.phases_done = []
        self.profile = None
        self.manifest_entries = None
        self.entry_points = None
        self.findings = []

    @property
    def path(self):
        return os.path.join(self.project_path, STATE_DIR, STATE_FILE)

    def severity_counts(self):
        counts = {"critical": 0, "functional": 0, "quality": 0}
        for f in self.findings:
            if f["severity"] in counts:
                counts[f["severity"]] += 1
        return counts

    def save(self):
        d = os.path.join(self.project_path, STATE_DIR)
        os.makedirs(d, exist_ok=True)
        payload = {
            "created_at": self.created_at,
            "project_path": self.project_path,
            "phases_done": self.phases_done,
            "profile": self.profile,
            "manifest_entries": self.manifest_entries,
            "entry_points": self.entry_points,
            "findings": self.findings,
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=1)

    @classmethod
    def load(cls, project_path):
        state = cls(project_path)
        try:
            with open(state.path, encoding="utf-8") as f:
                payload = json.load(f)
        except (OSError, ValueError):
            return state
        state.created_at = payload.get("created_at", state.created_at)
        state.phases_done = payload.get("phases_done", [])
        state.profile = payload.get("profile")
        state.manifest_entries = payload.get("manifest_entries")
        state.entry_points = payload.get("entry_points")
        state.findings = payload.get("findings", [])
        return state

    @classmethod
    def clear(cls, project_path):
        try:
            os.remove(os.path.join(project_path, STATE_DIR, STATE_FILE))
        except OSError:
            pass
