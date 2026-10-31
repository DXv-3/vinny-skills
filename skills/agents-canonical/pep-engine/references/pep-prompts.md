# PEP Prompts — Templates and Examples

This document provides PEP-compliant prompt templates and examples for creating prompts for other AI tools and contexts.

---

## Quick Reference: PEP Structure for Prompt Creation

When user asks to "create a prompt using PEP" or similar, apply this structure:

```
1. CONTEXT FRAMEWORK (Ground the task)
   - Situation/background
   - Relevant prior context
   
2. PERSONA ACTIVATION (Who should respond)
   - Role + domain authority
   - Cognitive lens/perspective
   - Voice calibration
   
3. TASK SPECIFICATION (What to do)
   - Verb + Object + Purpose + Audience
   - Continuity connection
   
4. PROCESS DIRECTIVES (How to approach)
   - Decomposition steps
   - Synthesis approach
   - Integration method
   - Quality checks
   
5. OUTPUT SPECIFICATIONS (Format)
   - Structure/format
   - Depth level
   - Voice/tone
   - Continuity requirements
   
6. CONSTRAINTS (Boundaries)
   - Hard constraints (must follow)
   - Soft constraints (preferential)
   - What NOT to do
   
7. SCOPE DEFINITION
   - In-scope topics
   - Out-of-scope exclusions
   - Depth calibration
   
8. QUALITY VALIDATION
   - Completeness requirements
   - Continuity checks
   - Delta check standards
```

---

## Template: Universal PEP Prompt

```markdown
# [TASK NAME]

## Context
[Background, situation, and relevant prior information. 
Ground the AI in the world-state before asking it to act.]

## Persona
You are [ROLE], an expert in [DOMAIN] with [CREDENTIALS/EXPERIENCE].
Approach this from the perspective of [COGNITIVE LENS].
Your communication style should be [VOICE PARAMETERS].

## Task
[VERB] + [OBJECT] + [PURPOSE] + [AUDIENCE]

Example: "Analyze the Q3 revenue data to identify 
underperforming segments for the executive team."

## Process
1. [First step/decomposition]
2. [Second step]
3. [Synthesis/integration]
4. [Quality validation]

## Output Specifications
- **Format:** [e.g., structured report, bullet analysis, code, narrative]
- **Depth:** [Survey/Analysis/Deep Dive/Definitive]
- **Length:** [Approximate target or range]
- **Tone:** [Professional/Conversational/Technical/etc.]
- **Continuity:** [How this connects to prior work]

## Constraints
### Hard Constraints (Never Violate)
- [Critical requirement 1]
- [Critical requirement 2]
- [Factual accuracy — no fabrication]

### Soft Constraints (Directional)
- [Preferred terminology]
- [Style preferences]
- [Complexity level]

### Anti-Patterns (Avoid)
- [What NOT to do]
- [Phrases to avoid]
- [Approaches to reject]

## Scope
- **In Scope:** [Explicit topics to cover]
- **Out of Scope:** [Explicit exclusions]
- **Edge Cases:** [How to handle boundary conditions]

## Validation Criteria
Before delivering, verify:
- [ ] All explicit requirements addressed
- [ ] No contradictions with established facts
- [ ] Output provides value beyond generic response
- [ ] Appropriate evidence tier for claims
- [ ] Next logical step anticipated or addressed

## Mission
[One sentence — the single most important outcome.]
```

---

## Example 1: Technical Analysis Prompt

```markdown
# API Performance Analysis

## Context
Our REST API has experienced intermittent latency spikes 
during peak hours over the past 2 weeks. The infrastructure 
team has collected metrics but needs help interpreting patterns 
and identifying root causes. This analysis will inform a 
prioritized remediation plan.

## Persona
You are a senior Site Reliability Engineer with 10+ years 
experience diagnosing distributed system performance issues. 
Approach this as a methodical investigator who values data-driven 
conclusions over speculation. Communicate with technical precision 
but avoid unnecessary jargon.

## Task
Analyze the provided API metrics to identify the primary 
cause of latency spikes for the infrastructure team to 
prioritize fixes.

## Process
1. Decompose metrics into request patterns, response times, 
   and resource utilization dimensions
2. Map dependencies between observed symptoms and potential causes
3. Apply evidence-bound reasoning: Tier 1 (metrics), Tier 2 
   (established performance patterns), or Tier 4 (speculation 
   clearly labeled)
4. Stress-test top hypotheses: identify conditions where each 
   would fail or alternative explanations would apply
5. Synthesize findings into prioritized actionable recommendations

## Output Specifications
- **Format:** Structured technical analysis with summary, 
  detailed findings, and recommendation sections
- **Depth:** Deep Dive (include edge cases and failure modes)
- **Length:** 800-1200 words
- **Tone:** Professional, analytical, decisive
- **Continuity:** This extends the incident response started 
  in previous discussions

## Constraints
### Hard Constraints
- Base all claims on provided metrics or established SRE principles
- Flag any gaps in data that prevent definitive conclusions
- Prioritize fixes by impact × effort, not just severity

### Soft Constraints
- Use terminology from the existing runbook where applicable
- Include concrete numbers with every performance claim

### Anti-Patterns
- Don't suggest "add more resources" without identifying why 
  current resources are insufficient
- Don't present multiple options without a clear recommendation
- Avoid "it depends" without specifying exactly what it depends on

## Scope
- **In Scope:** Request latency patterns, resource bottlenecks, 
  architectural constraints revealed by metrics
- **Out of Scope:** Code-level optimizations (not enough data), 
  long-term architectural redesign
- **Uncertainty:** Flag where additional instrumentation would 
  clarify ambiguous findings

## Validation Criteria
- [ ] Every latency spike pattern mapped to a causal hypothesis
- [ ] At least one high-confidence root cause identified
- [ ] Recommendations are actionable and prioritized
- [ ] Data gaps explicitly flagged, not papered over

## Mission
Deliver a prioritized diagnosis that enables the infrastructure 
team to take immediate action on the highest-impact fix.
```

---

## Example 2: Creative Writing Prompt

```markdown
# Product Launch Announcement

## Context
We're launching a new feature that allows users to export 
reports directly to Excel with one click. This addresses 
the #1 feature request from our enterprise customers. 
The announcement needs to build excitement while managing 
expectations about availability (rolling out over 2 weeks).

## Persona
You are a product marketing manager who deeply understands 
both technical capabilities and customer pain points. Write 
with genuine enthusiasm that comes from knowing this solves 
a real problem. Match the voice of our existing blog posts 
(conversational but professional).

## Task
Write a product launch announcement that generates excitement 
for the Excel export feature while clearly communicating the 
rolling rollout timeline.

## Process
1. Open with the customer pain point (the "before" state)
2. Introduce the solution with specific benefits
3. Provide clear rollout timeline and availability
4. Include a soft call-to-action
5. Validate tone matches brand voice

## Output Specifications
- **Format:** Blog post (title + body)
- **Depth:** Analysis (substantive but accessible)
- **Length:** 400-600 words
- **Tone:** Conversational, enthusiastic, transparent
- **Continuity:** Build on the "customer feedback" themes 
  from previous product updates

## Constraints
### Hard Constraints
- Must mention the 2-week rolling rollout
- Must not promise features not included (no PDF export, 
  no scheduled exports yet)
- Factually accurate about capabilities

### Soft Constraints
- Use "you" and "your" frequently (direct address)
- Include one concrete customer use case example
- Reference the #1 feature request context

### Anti-Patterns
- Avoid "revolutionary" or "game-changing" hyperbole
- No passive voice constructions
- Don't bury the rollout timeline in fine print

## Scope
- **In Scope:** Feature benefits, use cases, rollout plan, 
  brief technical context
- **Out of Scope:** Detailed technical implementation, 
  future roadmap items, pricing changes
- **Edge Cases:** Acknowledge this is v1 (future enhancements coming)

## Validation Criteria
- [ ] Would a busy customer read to the end?
- [ ] Is the rollout timeline impossible to miss?
- [ ] Does it sound like us (brand voice consistency)?
- [ ] Would this work for both technical and non-technical readers?

## Mission
Create an announcement that customers actually want to read 
and that sets appropriate expectations for rollout.
```

---

## Example 3: Code Review Prompt

```markdown
# Code Review: Authentication Module

## Context
This is a new authentication module implementing OAuth2 
with PKCE for a web application. The author is a mid-level 
developer looking for feedback on security best practices 
and code organization. This module will handle authentication 
for approximately 50,000 daily active users.

## Persona
You are a senior security engineer with expertise in OAuth2 
implementations and web application security. Review as a 
mentor — catch real issues but explain the "why" behind 
recommendations. Prioritize security concerns but also 
address maintainability.

## Task
Review the authentication module code for security 
vulnerabilities, OAuth2 compliance, and maintainability 
issues.

## Process
1. Scan for security anti-patterns (injection, exposure, 
   validation gaps)
2. Verify OAuth2/PKCE implementation correctness
3. Assess error handling and logging practices
4. Evaluate test coverage and edge cases
5. Organize findings by severity with actionable fixes

## Output Specifications
- **Format:** Structured code review (summary + line-specific 
  comments + recommendations)
- **Depth:** Deep Dive (security-critical code)
- **Length:** Comprehensive but focused on actionable items
- **Tone:** Professional, educational, direct
- **Continuity:** Build on the security standards discussed 
  in previous code reviews

## Constraints
### Hard Constraints
- Flag any security vulnerability regardless of perceived risk
- Cite specific OWASP or OAuth2 spec references for security claims
- Never suggest security-through-obscurity approaches

### Soft Constraints
- Prefer code examples over prose explanations
- Group related issues to avoid repetition
- Acknowledge what the code does well

### Anti-Patterns
- Don't nitpick style (assume linter handles that)
- Don't suggest rewrites without clear justification
- Never say "this looks fine" for security-critical code without verification

## Scope
- **In Scope:** Security, OAuth2 compliance, error handling, 
  logging, test coverage
- **Out of Scope:** Performance optimization (not the priority), 
  UI/UX concerns
- **Uncertainty:** Flag any areas where runtime behavior is unclear 
  from static review

## Validation Criteria
- [ ] Every security claim tied to a specific code location
- [ ] Severity assigned to each finding (Critical/High/Medium/Low)
- [ ] Recommendations are specific and implementable
- [ ] Tone is constructive, not punitive

## Mission
Deliver a review that improves the security posture of the 
authentication module while educating the developer for future work.
```

---

## Example 4: Strategic Planning Prompt

```markdown
# Q4 Marketing Strategy Review

## Context
We need to finalize Q4 marketing strategy. Q1-Q3 focused on 
brand awareness; Q4 needs to shift toward conversion. The 
budget is flat QoQ but we've learned what channels perform 
best. Sales team feedback indicates enterprise prospects want 
more technical content. We're competing against two well-funded 
competitors who are aggressively pricing.

## Persona
You are a strategic marketing consultant with experience in 
B2B SaaS growth. Approach this as a data-informed strategist 
who isn't afraid to recommend bold moves when justified. 
Balance analytical rigor with creative thinking.

## Task
Develop a Q4 marketing strategy that shifts focus from 
awareness to conversion while addressing competitive 
pressure and sales feedback.

## Process
1. Analyze current state (Q1-Q3 learnings, market position, 
   competitive dynamics)
2. Define strategic priorities given constraints
3. Develop channel-specific tactics with resource allocation
4. Identify risks and mitigation strategies
5. Define success metrics and review cadence

## Output Specifications
- **Format:** Strategic plan (executive summary + detailed tactics 
  + metrics + risks)
- **Depth:** Definitive (the working document for Q4)
- **Length:** 1500-2000 words + tables/figures as needed
- **Tone:** Strategic, decisive, data-driven
- **Continuity:** Build on Q1-Q3 learnings, don't restart from scratch

## Constraints
### Hard Constraints
- Budget must remain flat QoQ
- Must address the awareness→conversion shift explicitly
- Must incorporate sales team feedback on technical content

### Soft Constraints
- Prefer actionable tactics over theoretical frameworks
- Include specific metrics/KPIs for each initiative
- Acknowledge competitive pressure without being defensive

### Anti-Patterns
- Don't spread budget thin across too many channels
- Don't recommend tactics without justification
- Don't ignore the constraints and propose an "ideal" plan

## Scope
- **In Scope:** Channel strategy, content strategy, budget 
  allocation, metrics, risk mitigation
- **Out of Scope:** Product roadmap changes, pricing strategy 
  (different workstream), org structure
- **Uncertainty:** Flag where market response is unpredictable 
  and suggest test/learn approaches

## Validation Criteria
- [ ] Every recommendation includes rationale and expected impact
- [ ] Budget allocation sums correctly and stays flat
- [ ] Awareness→conversion shift is explicit in tactics
- [ ] Competitive dynamics addressed, not ignored
- [ ] Metrics are measurable and time-bound

## Mission
Deliver a Q4 strategy that the marketing team can execute 
immediately with confidence in its alignment to business goals.
```

---

## Mini-Template: Quick PEP Enhancement

For users who just want to "PEP-ify" an existing prompt:

```markdown
# Enhanced Prompt Structure

Take this basic prompt and add PEP structure:

[BASIC PROMPT]

Enhanced version:

---

## Context
[What situation or background does the AI need to know?]

## Persona  
[What role should the AI adopt? What expertise?]

## Task
[Clear, specific task statement]

## Output
- Format: [desired format]
- Length: [approximate target]
- Tone: [voice parameters]

## Constraints
- Must include: [requirements]
- Must avoid: [anti-patterns]

## Mission
[Single most important outcome]
```

---

## PEP Trigger Patterns

When user says any of these, activate the full prompt-builder workflow:

- "Create a prompt for [X]"
- "Write a system prompt"
- "Help me craft a prompt"
- "PEP-ify this prompt"
- "Apply PEP structure to this"
- "I need a prompt that does [X]"

**Response pattern:**
1. Acknowledge you're applying PEP structure
2. Detect implied tier (usually Tier 2-3 for prompt creation)
3. Build the full structured prompt
4. Briefly explain the structural choices made
