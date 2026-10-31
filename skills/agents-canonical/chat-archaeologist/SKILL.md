---
name: chat-archaeologist
description: "Skill: chat-archaeologist"
---

# Skill: chat-archaeologist

Digs through old chats, figures out what was being done, tells you in plain English whether it's worth finishing or scrapping. Use when the user says "what was I working on", "find that old chat", "did we finish that thing", "what happened last time", or wants to resurrect abandoned work.

## When to Use

- User asks "what was I working on in that old chat"
- User wants to find a specific conversation from days/weeks ago
- User says "did we ever finish X" or "what happened with Y"
- User wants to know if old work is still relevant
- User is starting something new and wants to check if it was attempted before
- User says "find that chat where we were talking about..."
- User wants a plain-English summary of abandoned work

---

## How It Works

```
1. DISCOVER  → Find old chats from any source
2. EXTRACT   → Pull out what was being done
3. CLASSIFY  → Mark each task as DONE / PARTIAL / NOT DONE
4. ASSESS    → Is this worth finishing? Does it fit current work?
5. TRANSLATE → Explain it all like you're talking to a friend
```

---

## 1. Discovery: Where Old Chats Live

### Claude Code Sessions

```bash
# Find all session files
find ~/.claude -name "*.jsonl" -type f 2>/dev/null | head -20

# Sessions are stored per-project
ls ~/.claude/projects/

# Search for specific topics in session files
grep -rl "topic keyword" ~/.claude/projects/*/sessions/ 2>/dev/null

# List recent sessions by modification time
find ~/.claude -name "*.jsonl" -type f -exec ls -lt {} + 2>/dev/null | head -20
```

### OpenCode Sessions

```bash
# OpenCode session storage
find ~/.opencode -name "*.json" -type f 2>/dev/null | head -20

# Or check the current project
ls .opencode/sessions/ 2>/dev/null
```

### Cursor Sessions

```bash
# Cursor chat history
find ~/Library/Application\ Support/Cursor/User/workspaceStorage -name "*.json" 2>/dev/null | head -20

# Check for exported chats
find ~ -name "*cursor*chat*" -o -name "*cursor*session*" 2>/dev/null | head -10
```

### Handoff Files

```bash
# Check for existing handoff files
find . -name "handoff.md" -o -name "*.handoff" -o -name "context*.md" 2>/dev/null | head -10

# Check .handoffs directory
ls .handoffs/ 2>/dev/null

# Check .claude/context-transfers
ls .claude/context-transfers/ 2>/dev/null
```

### Git History (Infer from Commits)

```bash
# Recent work
git log --oneline -20

# What changed in each commit
git log --stat -5

# Find abandoned branches
git branch --no-merged main

# Find stashed work
git stash list
```

---

## 2. Extraction: Pull Out What Was Being Done

### From Session Files

```bash
# Extract user messages from a Claude session
cat ~/.claude/projects/*/sessions/*.jsonl | \
  jq -r 'select(.type == "user") | .message.content' 2>/dev/null | \
  head -100

# Extract tool calls (what the agent actually did)
cat session.jsonl | \
  jq -r 'select(.type == "assistant") | .message.content[] | select(.type == "tool_use") | .name' 2>/dev/null

# Extract file changes
cat session.jsonl | \
  jq -r 'select(.type == "assistant") | .message.content[] | select(.type == "tool_use") | select(.name == "write" or .name == "edit") | .input.file_path' 2>/dev/null
```

### From Git History

```bash
# What files changed recently
git log --oneline --name-only -10

# What was the last thing worked on
git log -1 --stat

# Find commits that mention specific keywords
git log --all --oneline --grep="feature" --grep="fix" --grep="WIP"

# Check diff of uncommitted work
git diff --stat
git diff --cached --stat
```

---

## 3. Classification: Task Status

For each task found, classify it:

| Status | Meaning | How to Detect |
|--------|---------|---------------|
| **DONE** | Completed and working | Tests pass, no TODOs, committed |
| **PARTIAL** | Started but not finished | Uncommitted changes, WIP commits, TODOs in code |
| **NOT DONE** | Planned but never started | Only in discussion, no code changes |
| **BLOCKED** | Can't finish without X | Comments say "waiting for", "blocked by" |
| **ABANDONED** | Was working, stopped mid-way | Last activity was a while ago, no follow-up |

---

## 4. Assessment: Is This Worth Finishing?

### Fit Check

```bash
# What are we currently working on?
git log --oneline -5
git branch --show-current
ls -lt | head -10

# Does the old work overlap?
# Compare file paths from old session with current files
```

### Quality Check

```bash
# Does the old code compile/build?
xcodebuild build 2>&1 | tail -5

# Are there tests?
find . -name "*Test*" -o -name "*Spec*" | head -10

# Is the code style consistent with current codebase?
# (Compare naming conventions, patterns)
```

### Effort Estimate

| Factor | Low Effort | High Effort |
|--------|-----------|-------------|
| Files changed | < 5 | > 20 |
| Time since work | < 1 week | > 1 month |
| Dependencies | None added | New packages |
| Breaking changes | None | API changes |
| Test coverage | Has tests | No tests |

---

## 5. Translation: Explain Like You're Stupid

This is the key part. After analysis, output a plain-English summary:

### Template

```markdown
## What You Were Doing

**In one sentence:** [One line summary]

**The boring version:** [Technical summary]

**The real version:** [What you were actually trying to accomplish, in plain English]

## Where You Left Off

**What's done:**
- [Done thing 1]
- [Done thing 2]

**What's half done:**
- [Partial thing 1] — [what's missing]

**What never happened:**
- [Not done thing 1]

## The Verdict

**Is this worth finishing?** [YES / NO / MAYBE]

**Why:** [Plain English explanation]

**Does it fit what you're doing now?** [YES / NO]

**Why:** [Plain English explanation]

**If you finish it, what do you get?** [What becomes possible]

**If you scrap it, what do you lose?** [Nothing / specific things]

## What To Do Next

**Option A: Finish it**
1. [First step]
2. [Second step]
3. [Third step]

**Option B: Scrap it**
1. [What to clean up]
2. [What to save for later]

**Option C: Steal the good parts**
1. [What's worth keeping]
2. [What to throw away]
```

### Example Output

```markdown
## What You Were Doing

**In one sentence:** You were building a camera app that scans documents and saves them as PDFs.

**The boring version:** Implementing AVCaptureSession with Vision framework rectangle detection and PDFKit export pipeline.

**The real version:** You wanted to point your phone at a receipt or document, have it automatically detect the edges, straighten it out, and save it as a clean PDF. Like a portable scanner.

## Where You Left Off

**What's done:**
- Camera preview works
- Can take photos
- Basic rectangle detection works

**What's half done:**
- Perspective correction — the math is there but it crashes on some angles
- PDF export — can create a PDF but images are blurry

**What never happened:**
- Gallery view to see saved documents
- iCloud sync
- Share sheet

## The Verdict

**Is this worth finishing?** MAYBE

**Why:** The camera and detection work is solid. The two bugs (crash + blurry PDF) are probably fixable in a couple hours. But you haven't touched it in 3 weeks and you're now working on a completely different app.

**Does it fit what you're doing now?** NO

**Why:** Your current project is a SwiftUI weather app. This camera app is a separate project with no overlap.

**If you finish it, what do you get?** A working document scanner app you could ship or use personally.

**If you scrap it, what do you lose?** About 2 days of work. The camera code might be reusable for other projects.

## What To Do Next

**Option A: Finish it** (if you still want a document scanner)
1. Fix the perspective correction crash (check for edge cases in corner detection)
2. Fix blurry PDF by using higher resolution capture
3. Add a simple list view for saved documents

**Option B: Scrap it** (if you don't need this anymore)
1. Archive the branch: `git branch -m old-camera-app`
2. Save the camera code snippet for future reference
3. Move on

**Option C: Steal the good parts** (if you want the camera code for another project)
1. Copy the CameraView and RectangleDetector into your current project
2. Leave the PDF stuff behind
3. Adapt as needed
```

---

## Quick Commands

### Find Old Chats

```bash
# Search all Claude sessions for a keyword
grep -rl "keyword" ~/.claude/projects/*/sessions/ 2>/dev/null

# Search by date (find sessions from last week)
find ~/.claude -name "*.jsonl" -mtime -7 -type f 2>/dev/null

# Search by file that was worked on
grep -rl "MyView.swift" ~/.claude/projects/*/sessions/ 2>/dev/null
```

### Analyze a Specific Session

```bash
# Get summary of what happened in a session
cat session.jsonl | jq -r 'select(.type == "user") | .message.content' 2>/dev/null

# Count tool calls by type
cat session.jsonl | jq -r 'select(.type == "assistant") | .message.content[] | select(.type == "tool_use") | .name' 2>/dev/null | sort | uniq -c | sort -rn

# List all files modified
cat session.jsonl | jq -r 'select(.type == "assistant") | .message.content[] | select(.type == "tool_use") | select(.name == "write" or .name == "edit") | .input.file_path' 2>/dev/null | sort -u
```

---

## Trigger Phrases

This skill activates when the user says:

- "what was I working on"
- "find that old chat"
- "did we ever finish X"
- "what happened with Y"
- "where did we leave off"
- "resurrect that old project"
- "what's in that abandoned branch"
- "check if we already built this"
- "pull up that conversation about..."
- "remind me what we were doing"
- "is this worth continuing"
- "should I finish this or scrap it"

---

## Rules

1. **Always check git first** — commits tell you more than chat logs
2. **Always classify every task** — DONE / PARTIAL / NOT DONE / BLOCKED / ABANDONED
3. **Always give a verdict** — YES / NO / MAYBE with plain English why
4. **Always give options** — Finish / Scrap / Steal parts
5. **Never use jargon** in the summary — explain like talking to a friend
6. **Never assume old work is still valid** — verify against current codebase
7. **Always check if it fits current work** — compare with recent git activity
