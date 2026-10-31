# Local install note (added by Vinny's setup, 2026-09-26)

The `forge/` tooling this skill drives (`python3 forge/next.py`, `forge/state.py`, …) lives in the full clone at:

**`~/Projects/img2threejs/`** (shallow clone of img2threejs/img2threejs @ v2.0.0, Apache-2.0)

When the skill says `python3 forge/next.py --state .img2threejs/state.json`, run it with the clone's forge, e.g.:

```
python3 ~/Projects/img2threejs/forge/next.py --state <project>/.img2threejs/state.json
```

…or `cd` into the target project and point `forge` at the clone. Update the clone with `git -C ~/Projects/img2threejs pull` to pick up upstream gates.
