---
name: skill-router
description: "MUST USE before starting any task: run `skill-route \"<task>\"` to load only the 2-3 skills this task actually needs. Keeps 600+ installed skills out of context until one is relevant."
---

# Skill Router — load skills on demand, not by default

You have 600+ skills installed. Do NOT browse or guess. Route first:

```bash
skill-route "<one-line summary of the current task>"
```

- It prints up to 3 SKILL.md paths, ranked. **Read only those files**, then do the task.
- Empty output = no relevant skill. Proceed without one. Do not search the filesystem for skills.
- Multi-part task (e.g. "build an iOS widget and a landing page for it")? Run `skill-route` once per sub-task.
- Need more depth? `skill-route "<task>" --top 5`. Need archived/vendor skills? Add `--all`.

Rules:
1. Route before every new task; reuse your existing routing within the same task.
2. Never read SKILLS-INVENTORY.md or grep skills/ when the router can answer.
3. If routed skill doesn't fit after reading it, say so and continue without it — don't fish for more.
