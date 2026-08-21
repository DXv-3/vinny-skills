# AGENTS.md - Agent Configuration and Behavior

## Purpose

This document defines how AI agents should interact with the Code-Mode MCP Server. It provides patterns, best practices, and guidance for effective code execution.

## Agent Types

### Orchestrator Agents
Agents that coordinate multiple tools to accomplish complex tasks.

**Pattern:** Write code that calls multiple tools in sequence or parallel.

**Example Workflow:**
```typescript
// Register tools
await register_manual({...});

// Search for relevant tools
const tools = await search_tools({task_description: "process data"});

// Execute code that uses multiple tools
const result = await call_tool_chain({
  code: `
    const data = await tool1.getData();
    const processed = await tool2.process(data);
    await tool3.save(processed);
    return processed;
  `
});
```

### Builder Agents
Agents that create new capabilities by composing existing tools.

**Pattern:** Use call_tool_chain to create reusable workflows.

**Example Workflow:**
```typescript
// Create a custom workflow
const workflow = await call_tool_chain({
  code: `
    // Custom data pipeline
    const raw = await fetchData();
    const cleaned = raw.filter(x => x.valid);
    const enriched = await enrichData(cleaned);
    return { count: enriched.length, data: enriched };
  `,
  timeout: 60000
});
```

### Analyzer Agents
Agents that inspect and understand available tools.

**Pattern:** Use tools_info and search_tools to discover capabilities.

**Example Workflow:**
```typescript
// List all available tools
const allTools = await list_tools({});

// Get detailed info for specific tools
const info = await tools_info({tool_names: ["tool1", "tool2"]});

// Understand requirements
const keys = await get_required_keys_for_tool({tool_name: "tool1"});
```

## Code Execution Patterns

### Simple Tool Call
```typescript
const result = await call_tool_chain({
  code: `return await myTool.doSomething({param: "value"});`
});
```

### Multi-Step Workflow
```typescript
const result = await call_tool_chain({
  code: `
    const step1 = await toolA.start();
    const step2 = await toolB.process(step1);
    const step3 = await toolC.finish(step2);
    return { success: true, result: step3 };
  `,
  timeout: 120000
});
```

### Error Handling
```typescript
const result = await call_tool_chain({
  code: `
    try {
      const data = await riskyTool.operation();
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  `
});
```

## Tool Registration Patterns

### Register API Tool
```typescript
await register_manual({
  manual_call_template: {
    name: "my-api",
    url: "https://api.example.com",
    tools: [
      {
        name: "getData",
        call_template: {
          http_method: "GET",
          url: "{url}/data"
        }
      }
    ]
  }
});
```

### Register Script Tool
```typescript
await register_manual({
  manual_call_template: {
    name: "my-script",
    tools: [
      {
        name: "run",
        call_template: {
          command: "python",
          args: ["script.py", "{input}"]
        }
      }
    ]
  }
});
```

## Best Practices

### 1. Check Tool Availability First
```typescript
// Good: Verify tool exists
const tools = await list_tools({});
if (tools.includes("myTool")) {
  await call_tool_chain({code: `return await myTool.doWork();`});
}

// Bad: Assume tool exists
await call_tool_chain({code: `return await myTool.doWork();`});
```

### 2. Use Appropriate Timeouts
```typescript
// Quick operations
await call_tool_chain({code: `...`, timeout: 10000});

// Long-running operations
await call_tool_chain({code: `...`, timeout: 120000});
```

### 3. Handle Errors Gracefully
```typescript
const result = await call_tool_chain({
  code: `
    try {
      return await operation();
    } catch (e) {
      return { error: e.message };
    }
  `
});
```

### 4. Limit Output Size
```typescript
await call_tool_chain({
  code: `return largeData.slice(0, 100);`,
  max_output_size: 50000
});
```

### 5. Check Required Keys
```typescript
// Before using a tool
const keys = await get_required_keys_for_tool({tool_name: "apiTool"});
// Verify all required environment variables are set
```

## Anti-Patterns

### Don't Execute Untrusted Code
```typescript
// Bad: User input directly in code
const userInput = getUserInput();
await call_tool_chain({code: userInput});

// Good: Validate and sanitize
const safeCode = sanitize(userInput);
await call_tool_chain({code: safeCode});
```

### Don't Ignore Errors
```typescript
// Bad: Swallow errors
await call_tool_chain({code: `await tool.call(); return "done";`});

// Good: Handle errors
await call_tool_chain({code: `
  try {
    await tool.call();
    return "done";
  } catch (e) {
    return "failed: " + e.message;
  }
`});
```

### Don't Create Infinite Loops
```typescript
// Bad: Potential infinite loop
await call_tool_chain({code: `while(true) { await tool.call(); }`});

// Good: Bounded iteration
await call_tool_chain({code: `
  for (let i = 0; i < 10; i++) {
    await tool.call();
  }
`});