<!-- filename: conversation-to-skill.md -->
# Conversation → Skill Extractor

## When to use
Use when the task is to turn a full chat into one or more reusable `skill.md` operating manuals—not a transcript summary, not a recap of the last message.

## Do not use
- Pure code review (use `code-review.md`)
- Single-turn Q&A with no multi-message arc
- Packaging only the final topic when a deeper reusable capability exists

## Inputs required
- Full conversation history (or instruction to reread it end-to-end)
- Optional: preferred skill name(s), domain constraints, multi-skill vs parent+subs preference

## Hard constraints
Stop. Before answering, go all the way back to the very first message in this conversation and reread the entire chat from start to finish.
- Do not just summarize the conversation.
- Do not only focus on the most recent request.
- Do not assume the obvious topic is the best skill.

## How to think (two levels at once)
**Street-level:** Capture concrete details—prompts, templates, examples, decisions, wording, constraints, artifacts. Preserve reusable material exactly when possible.

**High-level:** Step back and ask: “What was this conversation REALLY about?” Identify deeper pattern, workflow, strategy, or reusable capability. Package the skill most valuable for future use even if it is not the literal final topic.

**Goal:** BEST possible `skill.md`(s), not merely the most obvious one.

## Silent analysis process (do before writing)
1. **Reconstruct arc:** start; true problem; pivots; artifacts; what the user kept optimizing for.
2. **List candidates** (obvious + non-obvious)—e.g. prompt-writing, product-ideation, GitHub research prompt, conversation-to-skill extraction, meta-prompt library building, higher-order synthesis.
3. **Choose best skill(s):** most reusable, high-leverage, faithful to the full chat—not just the last topic. If multiple strong skills: multiple files **or** one parent with sub-skills.
4. **Preserve gold:** exact prompts, templates, wording, frameworks, product ideas, naming, structures; do not paraphrase away useful exact language; keep user intent and style.
5. **Extract implicit:** user preferences (depth, directness, creativity, leverage, tooling, iteration, packaging) → instructions, heuristics, decision rules inside the skill.

## What a skill.md must teach
A `skill.md` is a reusable operating manual for a future agent that never sees this chat. Teach:
- when to use the capability
- required inputs
- how to think through the task
- how to execute
- what outputs to produce
- mistakes to avoid
- how to adapt when the situation changes

## Output format
One or more complete `skill.md` files inside fenced markdown code blocks.
- One best skill → one file.
- Multiple → each preceded by: `<!-- filename: skill-name.md -->`

## Mistakes to avoid
- Transcript dump disguised as a skill
- Picking only the last topic
- Paraphrasing away gold language
- Missing when/inputs/think/execute/outputs/mistakes/adapt
- Mixing in unrelated tasks (e.g. full code review) unless the conversation’s real skill is that capability

## Adaptation
If history is truncated, state what is missing, extract only from available span, and mark low-confidence gold as provisional. If the user wants multiple skills, prefer separate files over one overloaded manual.
