---
name: progress-report
description: "Skill: Progress Report Generator"
---

# Skill: Progress Report Generator

# Progress Report Card Template

## Overview
Generates a comprehensive progress report card for any session, embedding metrics, achievements, and deliverables into a reusable prompt template.

## When to Use
- End of any significant workflow
- After completing multiple tasks
- When user requests a summary
- Before starting a new session
- For session archival

## The Prompt Template

```
You are a Progress Report Generator. Create a comprehensive report card for this session.

## SESSION CONTEXT
- **Session ID:** {{SESSION_ID}}
- **Date:** {{DATE}}
- **Duration:** {{DURATION}}
- **User Goal:** {{USER_GOAL}}

## COMPLETED TASKS
{{#each COMPLETED_TASKS}}
- [{{STATUS}}] {{TASK_NAME}} ({{GRADE}})
{{/each}}

## METRICS
| Metric | Value |
|--------|-------|
| **Tasks Completed** | {{TASKS_COMPLETED}}/{{TOTAL_TASKS}} |
| **Files Created** | {{FILES_CREATED}} |
| **Issues Found** | {{ISSUES_FOUND}} |
| **Issues Fixed** | {{ISSUES_FIXED}} |
| **Tests Passing** | {{TESTS_PASSING}} |
| **Research Sources** | {{RESEARCH_SOURCES}} |

## ACHIEVEMENTS
{{#each ACHIEVEMENTS}}
- ✅ {{ACHIEVEMENT}}
{{/each}}

## DELIVERABLES
### Documents
{{#each DOCUMENTS}}
| File | Location | Purpose |
|------|----------|---------|
| {{NAME}} | {{LOCATION}} | {{PURPOSE}} |
{{/each}}

### Code/Assets
{{#each ASSETS}}
| Directory | Contents |
|-----------|----------|
| {{DIR}} | {{CONTENTS}} |
{{/each}}

## QUALITY ASSURANCE
- **Code Review:** {{CODE_REVIEW_STATUS}}
- **Testing:** {{TESTING_STATUS}}
- **Documentation:** {{DOCUMENTATION_STATUS}}

## FUTURE WORK
{{#each FUTURE_WORK}}
- [ ] {{TASK}}
{{/each}}

## EFFICIENCY SCORE
| Category | Score | Notes |
|----------|-------|-------|
| **Speed** | {{SPEED_SCORE}}/10 | {{SPEED_NOTES}} |
| **Accuracy** | {{ACCURACY_SCORE}}/10 | {{ACCURACY_NOTES}} |
| **Completeness** | {{COMPLETENESS_SCORE}}/10 | {{COMPLETENESS_NOTES}} |
| **Innovation** | {{INNOVATION_SCORE}}/10 | {{INNOVATION_NOTES}} |
| **Documentation** | {{DOC_SCORE}}/10 | {{DOC_NOTES}} |

**Overall Efficiency: {{OVERALL_EFFICIENCY}}% ({{OVERALL_GRADE}})**

## FINAL VERDICT
**Status:** {{STATUS}}
**Quality:** {{QUALITY}}
**Documentation:** {{DOC_STATUS}}
**Deployment:** {{DEPLOYMENT_STATUS}}

**Session Grade: {{SESSION_GRADE}}**

---

*Report generated: {{GENERATION_DATE}}*
```

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SESSION_ID` | Unique session identifier | `aoe-engine-2026-07-31` |
| `DATE` | Session date | `July 31, 2026` |
| `DURATION` | How long the session lasted | `Single session` |
| `USER_GOAL` | What the user wanted to achieve | `Build AOE Engine` |
| `COMPLETED_TASKS` | List of completed tasks | See example |
| `TASKS_COMPLETED` | Number completed | `12` |
| `TOTAL_TASKS` | Total tasks attempted | `12` |
| `FILES_CREATED` | Files created | `15+` |
| `ISSUES_FOUND` | Issues discovered | `12` |
| `ISSUES_FIXED` | Issues resolved | `12` |
| `TESTS_PASSING` | Test results | `7/7 (100%)` |
| `RESEARCH_SOURCES` | Sources consulted | `8` |
| `ACHIEVEMENTS` | Major accomplishments | See example |
| `DOCUMENTS` | Documents created | See example |
| `ASSETS` | Code/assets created | See example |
| `CODE_REVIEW_STATUS` | Review results | `12 issues found, 12 fixed` |
| `TESTING_STATUS` | Test results | `All tests passing` |
| `DOCUMENTATION_STATUS` | Documentation quality | `Comprehensive` |
| `FUTURE_WORK` | Next steps | See example |
| `SPEED_SCORE` | Speed rating | `9` |
| `ACCURACY_SCORE` | Accuracy rating | `10` |
| `COMPLETENESS_SCORE` | Completeness rating | `9` |
| `INNOVATION_SCORE` | Innovation rating | `8` |
| `DOC_SCORE` | Documentation rating | `10` |
| `OVERALL_EFFICIENCY` | Overall percentage | `94` |
| `OVERALL_GRADE` | Letter grade | `A` |
| `STATUS` | Final status | `ALL OBJECTIVES COMPLETED` |
| `QUALITY` | Quality level | `PRODUCTION-READY` |
| `DOC_STATUS` | Documentation status | `COMPREHENSIVE` |
| `DEPLOYMENT_STATUS` | Deployment status | `GITHUB LIVE` |
| `SESSION_GRADE` | Final grade | `A` |
| `GENERATION_DATE` | When report was generated | `July 31, 2026` |

## Example Usage

### Input
```json
{
  "SESSION_ID": "aoe-engine-2026-07-31",
  "DATE": "July 31, 2026",
  "DURATION": "Single session",
  "USER_GOAL": "Build AOE Engine with full workflow",
  "COMPLETED_TASKS": [
    {"STATUS": "✅", "TASK_NAME": "Skill Review", "GRADE": "A+"},
    {"STATUS": "✅", "TASK_NAME": "Build Implementation", "GRADE": "A"}
  ],
  "TASKS_COMPLETED": 12,
  "TOTAL_TASKS": 12,
  "FILES_CREATED": "15+",
  "ISSUES_FOUND": 12,
  "ISSUES_FIXED": 12,
  "TESTS_PASSING": "7/7 (100%)",
  "RESEARCH_SOURCES": 8
}
```

### Output
A formatted progress report card like the one shown in this session.

## Integration Points

### With Session Saver
```bash
# After saving session, generate report
skill: progress-report
# Then save report to session archive
```

### With Todo System
```bash
# Read todo list and generate metrics
todowrite: get_all
# Format into report template
```

### With Codebase Memory
```bash
# Get project metrics
codebase-memory: get_architecture
# Include in report
```

## Customization

### Add Custom Sections
```markdown
## CUSTOM SECTION
{{#each CUSTOM_ITEMS}}
- {{ITEM}}
{{/each}}
```

### Modify Grades
```markdown
## GRADE SCALE
- A+ (97-100%): Exceptional
- A (93-96%): Excellent
- A- (90-92%): Very Good
- B+ (87-89%): Good
- B (83-86%): Above Average
- B- (80-82%): Average
- C+ (77-79%): Below Average
- C (73-76%): Poor
- C- (70-72%): Very Poor
- D (60-69%): Failing
- F (<60%): Failed
```

## Error Handling

### Missing Variables
- Use default values
- Skip empty sections
- Mark as "N/A"

### Invalid Data
- Validate inputs
- Use fallback values
- Log errors

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-31 | Initial template |
