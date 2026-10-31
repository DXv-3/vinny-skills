#!/usr/bin/env python3
"""
Chain Orchestrator — Gate Verifier

Checks if phase gate conditions are met before advancing.
Run this before moving to the next phase.
"""

import json
import sys
from pathlib import Path

STATE_FILE = ".chain-state.json"

def verify_gate(phase_num):
    """Verify all gate conditions for a phase."""
    state_path = Path.cwd() / STATE_FILE
    if not state_path.exists():
        print("❌ No .chain-state.json found")
        return False
    
    with open(state_path) as f:
        state = json.load(f)
    
    phase_key = f"{phase_num}_{'validate discover build verify'.split()[phase_num-1]}"
    phase = state["phases"].get(phase_key, {})
    
    checks = []
    
    if phase_num == 1:  # VALIDATE
        checks.append(("Plan file exists", phase.get("plan_path") and Path(phase["plan_path"]).exists()))
        checks.append(("Code doctor approved", phase.get("code_doctor_review") == "approved"))
        checks.append(("Phase marked complete", phase.get("status") == "complete"))
    
    elif phase_num == 2:  # DISCOVER
        checks.append(("Research complete", phase.get("research_path") is not None))
        checks.append(("Parts cataloged", phase.get("parts_cataloged", 0) > 0))
        checks.append(("Phase marked complete", phase.get("status") == "complete"))
    
    elif phase_num == 3:  # BUILD
        checks.append(("Design approved", phase.get("design_approved") == True))
        checks.append(("Tests passing", phase.get("tests_failing", 1) == 0))
        checks.append(("Phase marked complete", phase.get("status") == "complete"))
    
    elif phase_num == 4:  # VERIFY
        checks.append(("Code doctor approved", phase.get("code_doctor_review") == "approved"))
        checks.append(("Phase marked complete", phase.get("status") == "complete"))
    
    # Print results
    phase_names = ["VALIDATE", "DISCOVER", "BUILD", "VERIFY"]
    print(f"\n{'='*50}")
    print(f"Phase {phase_num}: {phase_names[phase_num-1]} — Gate Check")
    print(f"{'='*50}")
    
    all_passed = True
    for check_name, passed in checks:
        icon = "✅" if passed else "❌"
        print(f"  {icon} {check_name}")
        if not passed:
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print(f"✅ GATE PASSED — Ready for Phase {phase_num + 1}")
    else:
        print(f"❌ GATE FAILED — Fix issues before advancing")
    print(f"{'='*50}\n")
    
    return all_passed

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: gate_check.py <phase_number>")
        sys.exit(1)
    
    phase = int(sys.argv[1])
    if phase < 1 or phase > 4:
        print("Phase must be 1-4")
        sys.exit(1)
    
    verify_gate(phase)
