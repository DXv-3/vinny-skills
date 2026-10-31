#!/usr/bin/env python3
"""
Chain Orchestrator — State Tracker

Manages .chain-state.json for the 4-phase orchestrator.
Tracks progress, gates, and failures across phases.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

STATE_FILE = ".chain-state.json"

def load_state(project_dir=None):
    """Load or create chain state."""
    if project_dir:
        state_path = Path(project_dir) / STATE_FILE
    else:
        state_path = Path.cwd() / STATE_FILE
    
    if state_path.exists():
        with open(state_path) as f:
            return json.load(f)
    return None

def save_state(state, project_dir=None):
    """Save chain state."""
    if project_dir:
        state_path = Path(project_dir) / STATE_FILE
    else:
        state_path = Path.cwd() / STATE_FILE
    
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    print(f"State saved to: {state_path}")

def init_state(project_name):
    """Initialize a new chain state."""
    state = {
        "project": project_name,
        "started": datetime.now().isoformat(),
        "current_phase": 1,
        "phases": {
            "1_validate": {"status": "pending"},
            "2_discover": {"status": "pending"},
            "3_build": {"status": "pending"},
            "4_verify": {"status": "pending"}
        }
    }
    save_state(state)
    print(f"Initialized chain for: {project_name}")
    return state

def update_phase(state, phase_num, updates):
    """Update a specific phase with new data."""
    phase_key = f"{phase_num}_{'validate discover build verify'.split()[phase_num-1]}"
    state["phases"][phase_key].update(updates)
    state["phases"][phase_key]["updated_at"] = datetime.now().isoformat()
    save_state(state)
    return state

def complete_phase(state, phase_num):
    """Mark a phase as complete."""
    phase_key = f"{phase_num}_{'validate discover build verify'.split()[phase_num-1]}"
    state["phases"][phase_key]["status"] = "complete"
    state["phases"][phase_key]["completed_at"] = datetime.now().isoformat()
    state["current_phase"] = phase_num + 1 if phase_num < 4 else 4
    save_state(state)
    print(f"Phase {phase_num} COMPLETE")
    return state

def fail_phase(state, phase_num, reason):
    """Mark a phase as failed."""
    phase_key = f"{phase_num}_{'validate discover build verify'.split()[phase_num-1]}"
    state["phases"][phase_key]["status"] = "failed"
    state["phases"][phase_key]["failed_at"] = datetime.now().isoformat()
    state["phases"][phase_key]["failure_reason"] = reason
    
    # Track retries
    retries = state["phases"][phase_key].get("retries", 0)
    state["phases"][phase_key]["retries"] = retries + 1
    
    save_state(state)
    
    if retries + 1 >= 3:
        print(f"Phase {phase_num} FAILED 3 times — ESCALATE TO HUMAN")
    else:
        print(f"Phase {phase_num} FAILED (attempt {retries + 1}/3): {reason}")
    
    return state

def check_gate(state, phase_num):
    """Check if a phase's gate condition is met."""
    phase_key = f"{phase_num}_{'validate discover build verify'.split()[phase_num-1]}"
    phase = state["phases"][phase_key]
    
    gates = {
        1: lambda p: p.get("status") == "complete" and p.get("code_doctor_review") == "approved",
        2: lambda p: p.get("status") == "complete" and p.get("parts_cataloged", 0) > 0,
        3: lambda p: p.get("status") == "complete" and p.get("design_approved") and p.get("tests_failing", 1) == 0,
        4: lambda p: p.get("status") == "complete" and p.get("code_doctor_review") == "approved"
    }
    
    passed = gates[phase_num](phase)
    print(f"Phase {phase_num} gate: {'PASS' if passed else 'FAIL'}")
    return passed

def get_status(state):
    """Get human-readable status."""
    lines = [f"Project: {state['project']}", f"Started: {state['started']}", ""]
    
    phase_names = ["VALIDATE", "DISCOVER", "BUILD", "VERIFY"]
    for i, name in enumerate(phase_names, 1):
        phase_key = f"{i}_{'validate discover build verify'.split()[i-1]}"
        phase = state["phases"][phase_key]
        status = phase.get("status", "pending")
        icon = {"complete": "✅", "in_progress": "🔄", "failed": "❌", "pending": "⏳"}.get(status, "❓")
        lines.append(f"  {icon} Phase {i}: {name} — {status}")
    
    lines.append(f"\nCurrent phase: {state['current_phase']}")
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: chain_state.py <command> [args]")
        print("Commands: init <name>, status, update <phase> <key> <value>, complete <phase>, fail <phase> <reason>, gate <phase>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "init":
        name = sys.argv[2] if len(sys.argv) > 2 else "unnamed-project"
        state = init_state(name)
        print(json.dumps(state, indent=2))
    
    elif cmd == "status":
        state = load_state()
        if state:
            print(get_status(state))
        else:
            print("No chain state found. Run: chain_state.py init <project-name>")
    
    elif cmd == "update":
        state = load_state()
        if state and len(sys.argv) >= 5:
            phase = int(sys.argv[2])
            key = sys.argv[3]
            value = sys.argv[4]
            # Try to parse as JSON
            try:
                value = json.loads(value)
            except:
                pass
            update_phase(state, phase, {key: value})
            print(f"Updated phase {phase}: {key} = {value}")
    
    elif cmd == "complete":
        state = load_state()
        if state and len(sys.argv) >= 3:
            complete_phase(state, int(sys.argv[2]))
    
    elif cmd == "fail":
        state = load_state()
        if state and len(sys.argv) >= 4:
            fail_phase(state, int(sys.argv[2]), sys.argv[3])
    
    elif cmd == "gate":
        state = load_state()
        if state and len(sys.argv) >= 3:
            check_gate(state, int(sys.argv[2]))
    
    else:
        print(f"Unknown command: {cmd}")
