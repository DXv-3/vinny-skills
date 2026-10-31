---
name: swarm
description: "Swarm Multi-Agent Orchestration Skill"
---

# Swarm Multi-Agent Orchestration Skill

A Model Context Protocol (MCP) skill for implementing OpenAI Swarm-like multi-agent coordination in Kimi CLI.

## Overview

This skill enables Kimi CLI to operate as a coordinated swarm of specialized agents, each with distinct responsibilities and constraints. It implements the core Swarm primitives:

- **Agents**: Specialized personas with specific capabilities
- **Handoffs**: Formal transfer of control between agents
- **Context Passing**: Information flow between specialized agents

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  [TriageAgent]                                               │
│  - Analyzes request                                          │
│  - Determines which agent should handle it                   │
│  - Coordinates the workflow                                  │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ [Investigator]  │ │   [FixerAgent]  │ │ [VerifierAgent] │
│   (Read-Only)   │ │ (State-Changing)│ │   (Testing)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Agent Definitions

### TriageAgent
The orchestrator. Analyzes requests and delegates to specialized agents.
- **Never** executes commands directly
- **Always** delegates to appropriate sub-agent
- **Maintains** workflow state

### InvestigatorAgent
Read-only information gatherer.
- **Allowed**: `ls`, `cat`, `find`, `grep`, `stat`, `file`
- **Forbidden**: Any state-changing command
- **Reports**: Structured findings to TriageAgent

### FixerAgent
State-changing execution specialist.
- **Allowed**: `chmod`, `chown`, `rm`, `mkdir`, `npm install`, builds
- **Requires**: Explicit authorization from TriageAgent
- **Reports**: Success/failure of each operation

### VerifierAgent
Quality assurance and validation.
- **Allowed**: Tests, builds, verification commands
- **Confirms**: Fixes work and goals are met
- **Reports**: Pass/fail status with details

## Usage

### Method 1: Agent Files

Use specific agent definitions for different tasks:

```bash
# Investigation phase
kimi --agent-file ~/.kimi/agents/InvestigatorAgent.yml -p "Analyze /workspace permissions"

# Fix phase
kimi --agent-file ~/.kimi/agents/FixerAgent.yml -p "Execute: chmod 755 /workspace/scripts"

# Verification phase
kimi --agent-file ~/.kimi/agents/VerifierAgent.yml -p "Run npm test and npm run build"
```

### Method 2: Swarm Mode (Interactive)

Start a session with the multi-agent system prompt:

```bash
kimi --skills-dir ~/.kimi/skills -p "@workspace I want you to operate as a Swarm of agents...

1. The **TriageAgent** will read my request and decide who acts next.
2. The **InvestigatorAgent** will run read-only commands to gather context.
3. The **FixerAgent** will run commands to modify files.
4. The **VerifierAgent** will run tests to confirm fixes.

Do not proceed until the TriageAgent has formally handed off the task.

My request: [YOUR TASK HERE]"
```

### Method 3: Full Swarm Workflow

Use the complete workflow template:

```bash
kimi --skills-dir ~/.kimi/skills -p "@workspace We are going to implement a task using the 'Swarm' multi-agent methodology.

**The Goal:** [Insert your complex goal here]

**The Swarm Architecture:**
1. **TriageAgent**: Analyzes and delegates
2. **InvestigatorAgent**: Read-only investigation
3. **FixerAgent**: Execute state changes
4. **VerifierAgent**: Validate and test

**Current Task:** [Specific task]

Please begin by invoking the InvestigatorAgent to assess the current state."
```

## Handoff Protocol

Agents communicate using formal handoff syntax:

```
[AGENT_A -> AGENT_B] Handoff message
```

Examples:
- `[TRIAGE -> INVESTIGATOR] Please analyze /workspace`
- `[INVESTIGATOR -> TRIAGE] Found permission issues. Details:...`
- `[TRIAGE -> FIXER] Authorized to execute: chmod 755 /workspace`
- `[FIXER -> VERIFIER] Changes complete. Please verify.`
- `[VERIFIER -> TRIAGE] All checks passed. Task complete.`

## Example Workflow

### Scenario: Fix EPERM errors and build Tauri app

**Step 1: Triage analyzes request**
```
[TriageAgent] New request: Fix EPERM errors in /workspace and build Tauri app.

Analysis: Need to investigate permissions first.

[TRIAGE -> INVESTIGATOR] Please examine /workspace and report:
1. Current directory listing with permissions
2. Any existing build artifacts
3. Log files with error details
```

**Step 2: Investigator gathers info**
```
[InvestigatorAgent] Beginning investigation...

$ ls -la /workspace
[output]

$ cat /workspace/error.log
[output]

[INVESTIGATOR -> TRIAGE] Investigation complete. Found:
- Root ownership on user files
- npm modules with wrong permissions
- Build directory missing
```

**Step 3: Triage authorizes fix**
```
[TriageAgent] Received investigator report.

Issues identified:
1. Wrong ownership on files
2. Permission issues in node_modules

[TRIAGE -> FIXER] Authorized to execute:
1. sudo chown -R $(whoami):staff /workspace
2. rm -rf /workspace/node_modules
3. npm install

Report back each command result.
```

**Step 4: Fixer executes**
```
[FixerAgent] Executing authorized commands...

$ sudo chown -R $(whoami):staff /workspace
[success]

$ rm -rf /workspace/node_modules
[success]

$ npm install
[success]

[FIXER -> VERIFIER] Execution complete. Please verify build works.
```

**Step 5: Verifier validates**
```
[VerifierAgent] Beginning verification...

$ npm run tauri build
[output: success]

$ ls -la src-tauri/target/release/
[output: artifacts present]

[VERIFIER -> TRIAGE] ✅ All checks passed. Task complete.
```

**Step 6: Triage closes workflow**
```
[TriageAgent] Workflow complete.

Summary:
- ✅ Permissions fixed
- ✅ Dependencies reinstalled
- ✅ Tauri app builds successfully

[TRIAGE -> USER] Task accomplished. The EPERM issues are resolved.
```

## Safety Features

1. **Role Segregation**: Agents cannot perform actions outside their scope
2. **Authorization Chain**: FixerAgent requires TriageAgent authorization
3. **Read-Only Investigation**: InvestigatorAgent cannot accidentally modify state
4. **Verification Gate**: VerifierAgent confirms before declaring success
5. **Audit Trail**: Handoff syntax creates clear execution log

## Best Practices

1. **Always start with InvestigatorAgent**: Never fix what you haven't examined
2. **Specific authorizations**: TriageAgent should specify exact commands
3. **Verify after fix**: Always run VerifierAgent after FixerAgent
4. **Report failures clearly**: Failed commands should include full error output
5. **Maintain handoff discipline**: Use formal syntax for clarity

## Configuration

Agent files are located at:
- `~/.kimi/agents/TriageAgent.yml`
- `~/.kimi/agents/InvestigatorAgent.yml`
- `~/.kimi/agents/FixerAgent.yml`
- `~/.kimi/agents/VerifierAgent.yml`

Modify these files to customize agent behavior for your specific use cases.

## Advanced Usage

### Custom Agents

Create additional specialized agents by adding new `.yml` files to `~/.kimi/agents/`:

```yaml
name: "DatabaseAgent"
description: "Database migration and schema specialist"
instructions: |
  You are the DatabaseAgent...
```

### Conditional Workflows

TriageAgent can implement conditional logic:

```
If permission error -> [TRIAGE -> FIXER]
If missing info -> [TRIAGE -> INVESTIGATOR]
If ready to test -> [TRIAGE -> VERIFIER]
```

### Parallel Execution

For independent tasks, TriageAgent can spawn multiple agents:

```
[TRIAGE -> INVESTIGATOR_A] Check frontend permissions
[TRIAGE -> INVESTIGATOR_B] Check backend permissions
```

## Troubleshooting

### Agent doesn't hand off properly
- Ensure handoff syntax is exact: `[AGENT_A -> AGENT_B]`
- Check that target agent name matches definition

### FixerAgent runs without authorization
- Remind FixerAgent of its instructions
- Reiterate that it requires TriageAgent authorization

### InvestigatorAgent tries to fix
- Stop and remind of read-only constraint
- Redirect to TriageAgent for FixerAgent handoff

## References

- OpenAI Swarm: https://github.com/openai/swarm
- Model Context Protocol: https://modelcontextprotocol.io
- Kimi CLI Documentation: https://docs.kimi.io
