<!-- filename: code-review.md -->
# Code Review & Optimization

## When to use
Use when the user provides implementation(s) to review and improve—source files, diffs, snippets, or architecture + code. Scope is **code quality, security, performance, maintainability**, not conversation-to-skill packaging.

## Do not use
- Turning a chat into a skill (use `conversation-to-skill.md`)
- Review with no code or architecture in context (ask for the implementation first)
- Pure product/strategy brainstorming with no code artifact

## Inputs required
- Code (or clear file paths + contents)
- Optional: language, constraints, performance targets, threat model, “don’t change public API” rules

## Objective
Comprehensive review of granular details **and** overall architecture for optimal performance, security, and long-term maintainability.

## How to execute (all five axes)
1. **Bug Detection & Resolution:** Identify all bugs, logical inconsistencies, runtime errors. Provide corrected snippets per issue with root-cause explanation.
2. **Security & Hardening:** Audit input handling for injection, buffer overflows, unsafe deserialization. Implement robust input validation, secure error handling, mitigations for common exploits.
3. **Performance Optimization:** Refactor inefficient algorithms/segments for speed and lower resource use. Where applicable, highlight measurable metrics.
4. **Code Quality & Maintainability:** Enforce consistent standards and best practices. Improve readability; eliminate smells; remove redundant/deprecated components.
5. **Refactoring & Simplification:** Simplify complex logic; restructure to cut technical debt. Justify each refactor by long-term scalability and sustainability.

## Output / deliverable
Provide a fully optimized, hardened, and refactored version of the code, clearly annotated with key changes and the rationale behind each improvement.

Recommended structure:
1. Findings summary (severity-ordered)
2. Axis-by-axis notes (bugs → security → perf → quality → refactor)
3. Final code (or unified diff) with annotations
4. Residual risks / out-of-scope items

## Mistakes to avoid
- Style nits only; missing bugs/security
- Rewrites without root-cause
- “Optimizations” with no measurable claim when claims are easy
- Silent API breaks
- Inventing requirements not in the code or user constraints

## Adaptation
If only a snippet is given, review the snippet and list what full-file context would change. If multiple modules, prioritize critical path and shared trust boundaries first.
