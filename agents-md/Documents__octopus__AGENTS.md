# Octopus — agent rules (opencode / any MCP client)

On every session that edits code on this machine:

1. Start: call `octopus_activity` / run `./octopus.sh status`
2. Before multi-file edit on a project: `octopus_lock(agent, project_path)`
3. Before exit: `octopus_report(agent, action, summary, files_changed)` then `octopus_release_lock`
4. Architecture choices: `octopus_record_decision`

Never claim Octopus reverses GitHub repos — route with `octopus_route` → gitreverse.

PROTOCOL (verbatim):

```
1. FIRST: Call octopus_activity()
2. BEFORE EDITING: Call octopus_lock(agent, project_path)
3. AFTER FINISHING: Call octopus_report(agent, action, summary, files_changed)
4. FOR DECISIONS: Call octopus_record_decision(agent, decision, rationale)
5. WHEN DONE: Call octopus_release_lock(agent, project_path)
```
