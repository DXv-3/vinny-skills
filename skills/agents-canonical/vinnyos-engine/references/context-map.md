# Context Map

When to load which skill based on what's happening.

---

## Trigger Words

| User Says | Phase | Load Skill |
|-----------|-------|------------|
| "Build X" | 1 | writing-plans |
| "Create X" | 1 | writing-plans |
| "Implement X" | 1 | writing-plans |
| "Design X" | 1 | brainstorming |
| "What exists?" | 2 | vinnyos-engine + deep-research |
| "Find tools" | 2 | vinnyos-engine |
| "Research X" | 2 | deep-research |
| "Fix this" | 3 | code-doctor |
| "Debug this" | 3 | systematic-debugging |
| "Test this" | 3 | test-driven-development |
| "What am I missing?" | 3 | brainstorming |
| "Review this" | 3 | code-doctor |

---

## Task Types

| Task Type | Phase | Skills |
|-----------|-------|--------|
| New feature | 1 → 2 → 3 | All |
| Bug fix | 3 | code-doctor + TDD |
| Refactoring | 3 | code-doctor |
| Research | 2 | deep-research + vinnyos-engine |
| Planning | 1 | writing-plans |
| Architecture | 1 → 2 | writing-plans + brainstorming |

---

## Complexity Levels

| Complexity | Phases | Skills |
|------------|--------|--------|
| Simple (1-2 files) | 3 | code-doctor + TDD |
| Medium (3-10 files) | 1 → 3 | writing-plans + code-doctor + TDD |
| Complex (10+ files) | 1 → 2 → 3 | All |

---

## Decision Tree

```
User asks to do something
    │
    ├─ Is it a new feature?
    │   ├─ Yes → Phase 1 (writing-plans) → Phase 2 (discover) → Phase 3 (build)
    │   └─ No ↓
    │
    ├─ Is it a bug?
    │   ├─ Yes → Phase 3 (code-doctor + TDD)
    │   └─ No ↓
    │
    ├─ Is it research?
    │   ├─ Yes → Phase 2 (deep-research + vinnyos-engine)
    │   └─ No ↓
    │
    ├─ Is it planning?
    │   ├─ Yes → Phase 1 (writing-plans)
    │   └─ No ↓
    │
    └─ Default → Phase 1 → Phase 2 → Phase 3
```

---

## Loading Skills

**To load a skill, use the skill tool:**
```
skill(name="writing-plans")
skill(name="systematic-debugging")
skill(name="deep-research")
skill(name="vinnyos-engine")
skill(name="web-search")
skill(name="brainstorming")
skill(name="code-doctor")
skill(name="test-driven-development")
```

**Don't load all at once.** Load on-demand based on context.
