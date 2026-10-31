# GitHub Morph

A smart morphing tool that treats GitHub as a library of parts. Extracts components, patterns, and enables intelligent code transformation.

## Features

- **Repository Analysis**: Analyze any GitHub repository structure, languages, and file organization
- **Component Extraction**: Extract functions, classes, and modules from repositories
- **Pattern Matching**: Search for code patterns across GitHub
- **Code Morphing**: Transform code between different patterns (async, class-based, functional, TypeScript, React)
- **Integration**: Works with gitreverse, gitingest, and other GitHub tools

## Installation

```bash
pip install --user requests rich
```

## Usage

```bash
# Analyze a repository
python github_morph.py analyze https://github.com/coderamp-labs/gitingest

# Extract components from a repository
python github_morph.py extract https://github.com/filiksyos/gitreverse --type function

# Find code patterns
python github_morph.py find "async def" --language python

# Morph code to a different pattern
python github_morph.py morph "def hello(): pass" --to async --language python

# Get gitingest URL
python github_morph.py gitingest https://github.com/coderamp-labs/gitingest

# Get gitreverse URL
python github_morph.py gitreverse https://github.com/filiksyos/gitreverse

# Advanced: List available GitHub tools
python morph_advanced.py tools

# Advanced: Detect patterns in a repository
python morph_advanced.py patterns https://github.com/coderamp-labs/gitingest

# Advanced: Smart morph code
python morph_advanced.py smart-morph "def hello(): pass" --to async
```

## Available Morphing Patterns

- `async` - Convert to async/await pattern
- `class` - Convert to class-based pattern
- `functional` - Convert to functional style
- `typescript` - Convert to TypeScript
- `react` - Convert to React component

## Integration with Other Tools

- **gitreverse** (https://gitreverse.com) - Reverse engineer repos into original prompts
- **gitingest** (https://gitingest.com) - Extract prompt-friendly codebase representations
- **repodissect** - Decompose repos into functional blocks
- **repo-lyzer** - CLI tool for analyzing and comparing GitHub repositories
- **snippets** - Extract and index code snippets from GitHub repositories

## Environment Variables

- `GITHUB_TOKEN` - Optional GitHub API token for higher rate limits