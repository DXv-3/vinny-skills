---
name: ai
description: "The AI Toolkit for TypeScript. From the creators of Next.js, the AI SDK is a free open-source library for building AI-powered applications and agents "
forge_provenance:
  repo: "vercel/ai"
  license: "NOASSERTION"
  stars: 27041
  pushed: "2026-09-29"
  forged_at: "2026-09-29T16:57:32"
  license_note: "IDEAS ONLY — restrictive/unverified license; do not ship this repo's code, extract mechanisms and rewrite from scratch."
---

# ai

> FORGED DRAFT — authored from vercel/ai. IDEAS ONLY — restrictive/unverified license; do not ship this repo's code, extract mechanisms and rewrite from scratch.

## What it is

Vercel's AI SDK is a provider-agnostic TypeScript toolkit: a uniform interface in front of dozens of model providers (OpenAI, Anthropic, Google, Bedrock, Azure, Groq, DeepSeek, and many more via per-provider `@ai-sdk/*` packages), core generation primitives (`generateText`, `streamText`, schema-driven structured output, tool calling, agent classes), and a UI layer that streams model output into React/Vue/Svelte/Angular components through hooks like `useChat`. It is the de-facto standard glue between TS backends and streaming chat/generative-UI frontends.

## Why it exists as a skill

Load when building or reviewing TS/JS AI applications: streaming LLM responses into React/Next (or Vue/Svelte/Angular) UIs, provider-swappable model backends, multi-step tool/agent loops, schema-constrained structured output, or custom streaming endpoints — including non-TypeScript backends that need to speak the SDK's stream protocol. Also load when reading code that imports `ai`, `@ai-sdk/react`, or `@ai-sdk/<provider>` so you use current APIs rather than stale ones (the surface churns fast).

## The parts worth keeping

- **Provider Language Model Specification** (`packages/provider`): a formal, versioned spec of what a "language model" is — the operations, streaming chunk shapes, and error semantics every provider adapter implements. Core functions stay provider-agnostic because every `@ai-sdk/*` package is just an adapter conforming to this spec; that contract is the reusable design idea, not any one adapter.
- **Model-string routing with gateway-first default**: a model is addressed as a `provider/model` string resolved through a gateway (Vercel AI Gateway by default), or bound directly via a provider package's factory. Swapping models or moving to a gateway is a one-token change at the edge; call sites never learn a provider SDK.
- **UI Message Stream Protocol**: an SSE-based, versioned wire format (`x-vercel-ai-ui-message-stream: v1` header) of typed parts — message `start`, `text-start/delta/end`, `reasoning-*`, `source-url`, `file`, `tool-input-start/delta`, tool-output states, typed `data-*` custom parts, `error` — documented precisely so any backend, even FastAPI in Python, can serve it. A plain-text stream protocol (`streamProtocol: 'text'`, pluggable transports) is the degenerate fallback.
- **Typed message anatomy**: client messages are `{ id, role, parts }` where parts are a discriminated union (`text`, `tool-<name>`, `data-<name>`, …), so UIs render by switching on `part.type` instead of parsing strings; type inference chains from server agent definition to client via `InferAgentUIMessage`, keeping tool UI type-safe end to end.
- **Tool abstraction with a three-part contract**: a tool is `description` + `inputSchema` (Zod or JSON Schema) + optional async `execute`, where the schema doubles as the model-facing declaration and the runtime validator of model-generated calls. The taxonomy of four tool classes is the keepable idea: function tools (yours), dynamic tools (runtime-discovered, e.g. MCP), provider-defined tools (provider ships the schema, you execute — "client tools" like Anthropic's bash), provider-executed tools (server-side, e.g. web search).
- **Bounded agent loop**: tool results are automatically appended and the model re-invoked, with `stopWhen` bounding the loop; agent classes like `ToolLoopAgent` bundle model + system prompt + tools into a reusable unit that works identically server-side or streamed to UI. The docs' workflow-pattern taxonomy (sequential chains, routing, parallel, evaluation loops, orchestration) is a compact decision guide adapted from Anthropic's "building effective agents".
- **`useChat` hook contract**: the hook owns the message list, a status state machine gating input (`ready` before send, busy while streaming), a `sendMessage` action, and a pluggable transport that maps UI events to an endpoint. Tool invocations arrive as parts with their own lifecycle states (`input-available` → `output-available`), enabling progressive tool UI — placeholders while args stream in, real content on completion.
- **Schema-first structured output**: pass a Zod schema (`Output.object`, legacy `generateObject`) to constrain and validate generation; the same schema mechanism drives tool inputs, making "describe the shape once, get prompting + validation + types" a single move.

## How to use

1. **Choose model binding**: gateway model strings (`'anthropic/claude-…'`) for zero-setup, or a direct provider package (`@ai-sdk/openai`, `@ai-sdk/anthropic`, `@ai-sdk/google`, `@ai-sdk/amazon-bedrock`, …). Decide at the composition edge; keep all call sites provider-agnostic so swapping is trivial.
2. **Pick the server primitive**: `generateText` for one-shot calls, `streamText` for streaming, an agent class (`ToolLoopAgent`) when tools + looping are involved. Attach Zod schemas via `Output.object` for structured results.
3. **Define tools** with description + `inputSchema` (+ `execute`), choosing deliberately among the four tool classes; bound every loop with `stopWhen` and a sensible step budget.
4. **Bridge server to client**: expose a route that converts incoming `UIMessage` history (`convertToModelMessages`) and returns a UI message stream response (`createAgentUIStreamResponse` / `createTextStreamResponse` + `toTextStream`). For non-TS or custom backends, implement the SSE protocol directly — start/delta/end parts plus the version header — instead of importing the server library.
5. **Wire the client**: `useChat` from `@ai-sdk/react` (framework siblings exist for Vue, Svelte, Angular), typed with the agent's `InferAgentUIMessage`; pass a transport (`TextStreamChatTransport` for plain-text backends); render by switching on `message.parts[].type`; gate the input on `status`; render each tool part according to its invocation state.
6. **Verify names at build time**: this API surface moves fast — agent classes, the `Output` API, and the SSE protocol version are recent (repo pushed 2026-09-29); check ai-sdk.dev before emitting code, since older tutorials still show `useCompletion`-era and `generateObject`-era patterns.

Verdict: PROMOTE WITH ADVISORY FLAGS — pure pattern knowledge, safe under the NOASSERTION ideas-only rule, but flag that API names churn quickly and must be re-checked against ai-sdk.dev at use time.
