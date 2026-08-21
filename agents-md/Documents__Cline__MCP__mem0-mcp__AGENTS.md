# AGENTS.md - Agent Configuration and Behavior

## Purpose

This document defines how AI agents should interact with the Mem0 MCP Server. It provides patterns, best practices, and guidance for effective memory management.

## Agent Types

### Conversational Agents
Agents that maintain ongoing dialogues with users.

**Memory Pattern:** Store user preferences, facts, and conversation context.

**Example Workflow:**
```
1. User mentions: "I'm allergic to peanuts"
2. Agent calls: add_memory(text="User is allergic to peanuts", user_id="john")
3. Later conversation: Agent calls search_memories(query="allergies", user_id="john")
4. Agent recalls allergy and avoids peanut-related suggestions
```

### Research Agents
Agents that gather and synthesize information across sessions.

**Memory Pattern:** Store research findings, sources, and conclusions.

**Example Workflow:**
```
1. Research session: Agent discovers key findings
2. Agent calls: add_memory(text="Key finding: X correlates with Y", metadata={"source": "paper-123", "confidence": 0.85})
3. Future session: Agent calls get_memories(filters={"AND": [{"metadata.source": "paper-123"}]})
4. Agent builds on previous research
```

### Task Agents
Agents that execute multi-step workflows over time.

**Memory Pattern:** Store task state, progress, and outcomes.

**Example Workflow:**
```
1. Task started: Agent stores initial state
2. Agent calls: add_memory(text="Task: Build feature X. Status: In progress. Step: 2/5", metadata={"task_id": "task-001", "step": 2})
3. Session ends, new session begins
4. Agent calls: get_memory(memory_id="task-001-state")
5. Agent resumes from saved state
```

## Memory Organization Strategies

### User-Centric Organization

```python
# All memories for a specific user
user_id = "user-123"

# Store various types of memories
add_memory(text="User prefers dark mode", user_id=user_id, metadata={"type": "preference"})
add_memory(text="User works in healthcare", user_id=user_id, metadata={"type": "profession"})
add_memory(text="User asked about project timeline", user_id=user_id, metadata={"type": "query", "project": "alpha"})
```

### Agent-Centric Organization

```python
# All memories for a specific agent
agent_id = "research-agent-v1"

# Store agent's learned patterns
add_memory(text="Effective prompt pattern: Start with context", agent_id=agent_id, metadata={"type": "pattern"})
add_memory(text="Common error: API timeout on large requests", agent_id=agent_id, metadata={"type": "error", "solution": "batch requests"})
```

### Topic-Centric Organization

```python
# Use metadata for topic organization
add_memory(
    text="Python 3.14 introduces pattern matching improvements",
    metadata={"topic": "python", "subtopic": "language-features", "version": "3.14"}
)
```

### Temporal Organization

```python
# Use metadata for time-based organization
add_memory(
    text="Q1 revenue exceeded targets by 15%",
    metadata={"quarter": "Q1", "year": "2026", "category": "financial"}
)
```

## Search Strategies

### Exact Match Search
```python
search_memories(
    query="user dietary preferences",
    filters={"AND": [{"user_id": "john"}]},
    limit=5
)
```

### Semantic Search
```python
search_memories(
    query="what does the user like to eat",
    filters={"AND": [{"user_id": "john"}]},
    limit=5
)
```

### Filtered Search
```python
search_memories(
    query="project status",
    filters={"AND": [
        {"metadata.project": "alpha"},
        {"created_at": {"gte": "2026-01-01"}}
    ]},
    limit=10
)
```

## Memory Lifecycle Management

### Creation
- Always include descriptive text
- Use metadata for structured data
- Assign appropriate user_id, agent_id, or other scope identifiers
- Consider future searchability when writing memory text

### Retrieval
- Use search_memories for discovery
- Use get_memory when you know the exact ID
- Use get_memories for filtered browsing
- Implement pagination for large result sets

### Update
- Use update_memory when information changes
- Preserve the memory_id for continuity
- Update metadata alongside text when appropriate

### Deletion
- Use delete_memory for single obsolete memories
- Use delete_all_memories to clear a scope
- Use delete_entities to remove an entire entity
- Deletions are permanent; verify before executing

## Error Handling Patterns

### Missing API Key
```
Error: MEM0_API_KEY is required
Action: Prompt user to configure their API key
Recovery: Cannot proceed without valid key
```

### Memory Not Found
```
Error: Memory with ID xyz not found
Action: Verify memory_id is correct
Recovery: Search for the memory instead
```

### Rate Limiting
```
Error: API rate limit exceeded
Action: Implement exponential backoff
Recovery: Retry after delay
```

### Network Errors
```
Error: Connection timeout
Action: Retry with shorter timeout
Recovery: Log error and continue
```

## Best Practices

### 1. Be Specific in Memory Text
```
Bad:  "User preference noted"
Good: "User prefers email notifications over push notifications for marketing updates"
```

### 2. Use Metadata Consistently
```
Establish conventions:
- type: "preference", "fact", "observation", "task"
- source: "user-stated", "inferred", "external"
- confidence: 0.0-1.0
```

### 3. Scope Memories Appropriately
```
User-specific: user_id="john"
Agent-specific: agent_id="my-agent"
Session-specific: run_id="session-123"
```

### 4. Handle Empty Results Gracefully
```
results = search_memories(query="preferences", user_id="john")
if not results:
    # Don't assume user has no preferences
    # Ask user or use defaults
```

### 5. Clean Up Obsolete Memories
```
# When information becomes outdated
delete_memory(memory_id="old-project-status")
add_memory(text="Project X is now complete", metadata={"status": "complete"})
```

## Integration Patterns

### With Claude Desktop
```json
{
  "mcpServers": {
    "github.com/mem0ai/mem0-mcp": {
      "command": "mem0-mcp-server",
      "env": {
        "MEM0_API_KEY": "m0-..."
      }
    }
  }
}
```

### With Custom Agents
```python
# Pseudo-code for agent integration
def on_conversation_start():
    memories = search_memories(query="user context", user_id=current_user)
    inject_context(memories)

def on_important_fact_learned(fact):
    add_memory(text=fact, user_id=current_user, metadata={"type": "fact"})

def on_conversation_end():
    # Optionally summarize and store conversation
    pass
```

## Anti-Patterns to Avoid

1. **Storing sensitive data without encryption**: Mem0 is not a secure vault
2. **Creating duplicate memories**: Search before creating
3. **Over-relying on memory**: Always verify critical information
4. **Ignoring metadata**: Structured data enables better retrieval
5. **Deleting without confirmation**: Confirm with user before destructive operations