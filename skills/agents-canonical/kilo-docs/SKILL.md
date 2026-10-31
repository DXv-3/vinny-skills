---
name: kilo-docs
description: Use the local Kilo Code documentation in references/ as primary context for answering questions about Kilo modes, skills, agents, tools, and configuration.
---

# Instructions

You have access to a `references/` directory containing a local mirror of the official Kilo Code documentation from https://github.com/Kilo-Org/kilocode.

When the user asks anything about:

- Kilo Code configuration, skills, modes, tools, or CLI
- Agent behavior, cloud agents, or free/budget model setup
- AI providers, models, or pricing
- Customization, theming, or settings
- Any feature that is documented in the official docs

Then:

1. First, search and read the most relevant files under `references/`.
2. Quote paths you read from (e.g. `references/customize/skills.md`) when you justify behavior or give examples.
3. Prefer answers that match the documentation exactly; if you are unsure, say you are unsure and ask the user to clarify.

When the user's question is NOT about Kilo Code, ignore this skill.

## Directory Structure

The `references/` directory mirrors the official Kilo Code docs site structure:

```
references/
├── getting-started/       # Installation, setup, migration guides
├── customize/             # Skills, modes, settings, theming
├── ai-providers/          # Provider configs, models, API keys
├── code-with-ai/          # Using Kilo (chat, edit, agent modes)
├── automate/              # MCP, tools, automation
├── collaborate/           # Sharing, version control
├── deploy-secure/         # Security, deployment options
└── contributing/          # Development, contributing guide
```

## Keeping Docs Current

To update the documentation to the latest version:

```bash
# Run the sync script
~/.kilocode/skills/kilo-docs/sync-docs.sh
```

Or manually:

```bash
cd /Users/vinnygilberti/Downloads/untitled folder/kilocode
git pull
```

The `references/` directory is a symlink, so it automatically reflects updates after pulling.
