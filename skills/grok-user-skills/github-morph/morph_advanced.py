#!/usr/bin/env python3
"""
Advanced GitHub Morph - Enhanced version with smart composition and pattern detection.
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path
from collections import defaultdict

try:
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.tree import Tree
    from rich.panel import Panel
    from rich.progress import Progress
except ImportError:
    print("Missing dependencies. Install with: pip install --user requests rich")
    sys.exit(1)

console = Console()

# Known GitHub tools for integration
GITHUB_TOOLS = {
    "gitreverse": {
        "url": "https://gitreverse.com",
        "description": "Reverse engineer any repo into its original prompt",
        "repo": "filiksyos/gitreverse"
    },
    "gitingest": {
        "url": "https://gitingest.com",
        "description": "Replace 'hub' with 'ingest' in any GitHub URL to get a prompt-friendly extract",
        "repo": "coderamp-labs/gitingest"
    },
    "repodissect": {
        "url": "https://github.com/antryu/repodissect",
        "description": "Decompose any GitHub repo into functional blocks",
        "repo": "antryu/repodissect"
    },
    "repo-lyzer": {
        "url": "https://github.com/agnivo988/Repo-lyzer",
        "description": "CLI tool for analyzing and comparing GitHub repositories",
        "repo": "agnivo988/Repo-lyzer"
    },
    "snippets": {
        "url": "https://github.com/cheolwanpark/snippets",
        "description": "Extracts and indexes code snippets from GitHub repositories",
        "repo": "cheolwanpark/snippets"
    }
}

@dataclass
class CodePattern:
    """Represents a detected code pattern."""
    name: str
    pattern_type: str  # design_pattern, architecture, framework
    files: List[str]
    confidence: float
    description: str

@dataclass
class ComponentLibrary:
    """A library of components from multiple repositories."""
    name: str
    components: Dict[str, List[Any]] = field(default_factory=dict)
    patterns: List[CodePattern] = field(default_factory=list)

class AdvancedGitHubMorph:
    """Advanced GitHub Morph with smart composition capabilities."""
    
    GITHUB_API = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}" if self.token else None
        }
        self.headers = {k: v for k, v in self.headers.items() if v}
        self.component_library = ComponentLibrary("github-library")
    
    def discover_tools(self) -> List[Dict]:
        """Discover and list available GitHub tools."""
        console.print("[bold blue]Discovering GitHub tools...[/bold blue]")
        
        tools = []
        for name, info in GITHUB_TOOLS.items():
            tools.append({
                "name": name,
                "description": info["description"],
                "url": info["url"],
                "repo": info["repo"]
            })
        
        return tools
    
    def analyze_with_tool(self, repo_url: str, tool: str) -> str:
        """Analyze a repository using a specific tool."""
        if tool == "gitreverse":
            return f"https://gitreverse.com/{repo_url.split('github.com/')[-1]}"
        elif tool == "gitingest":
            return repo_url.replace("github.com", "gitingest.com")
        else:
            return f"Tool {tool} not directly supported. Use the tool's URL: {GITHUB_TOOLS.get(tool, {}).get('url', 'Unknown')}"
    
    def detect_patterns(self, repo_url: str) -> List[CodePattern]:
        """Detect design patterns and architecture in a repository."""
        console.print(f"[bold blue]Detecting patterns in:[/bold blue] {repo_url}")
        
        # Parse repo URL
        match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
        if not match:
            return []
        
        owner, name = match.groups()
        
        # Get repository tree
        response = requests.get(
            f"{self.GITHUB_API}/repos/{owner}/{name}/git/trees/main?recursive=1",
            headers=self.headers
        )
        
        if response.status_code != 200:
            # Try master branch
            response = requests.get(
                f"{self.GITHUB_API}/repos/{owner}/{name}/git/trees/master?recursive=1",
                headers=self.headers
            )
        
        if response.status_code != 200:
            return []
        
        tree = response.json().get("tree", [])
        patterns = []
        
        # Detect patterns based on file structure
        file_names = [item["path"].lower() for item in tree if item["type"] == "blob"]
        
        # Detect common patterns
        if any("controller" in f for f in file_names):
            patterns.append(CodePattern(
                name="MVC",
                pattern_type="architecture",
                files=[f for f in file_names if "controller" in f],
                confidence=0.8,
                description="Model-View-Controller architecture detected"
            ))
        
        if any("service" in f or "services" in f for f in file_names):
            patterns.append(CodePattern(
                name="Service Layer",
                pattern_type="architecture",
                files=[f for f in file_names if "service" in f],
                confidence=0.7,
                description="Service layer pattern detected"
            ))
        
        if any("component" in f for f in file_names):
            patterns.append(CodePattern(
                name="Component-Based",
                pattern_type="architecture",
                files=[f for f in file_names if "component" in f],
                confidence=0.75,
                description="Component-based architecture detected"
            ))
        
        # Detect framework patterns
        if any("next.config" in f for f in file_names):
            patterns.append(CodePattern(
                name="Next.js",
                pattern_type="framework",
                files=[f for f in file_names if "next" in f],
                confidence=0.9,
                description="Next.js framework detected"
            ))
        
        if any("package.json" in f for f in file_names):
            patterns.append(CodePattern(
                name="Node.js",
                pattern_type="framework",
                files=["package.json"],
                confidence=0.85,
                description="Node.js project detected"
            ))
        
        return patterns
    
    def compose_components(self, components: List[str], target_language: str = "python") -> str:
        """Compose multiple components into a cohesive implementation."""
        console.print(f"[bold blue]Composing {len(components)} components...[/bold blue]")
        
        composed = []
        imports = set()
        
        for comp in components:
            # Extract imports and code
            if "import" in comp:
                import_lines = [l for l in comp.split("\n") if "import" in l]
                imports.update(import_lines)
            
            composed.append(comp)
        
        # Build composed output
        output = "# Composed Component\n\n"
        output += "\n".join(sorted(imports)) + "\n\n"
        output += "\n\n".join(composed)
        
        return output
    
    def smart_morph(self, source: str, target: str, context: Optional[Dict] = None) -> str:
        """Intelligently morph code based on context and target patterns."""
        console.print(f"[bold blue]Smart morphing to:[/bold blue] {target}")
        
        # Analyze source
        source_lang = self._detect_language(source)
        
        # Apply transformations
        result = source
        
        if target == "async":
            result = self._morph_to_async(result, source_lang)
        elif target == "class":
            result = self._morph_to_class(result, source_lang)
        elif target == "functional":
            result = self._morph_to_functional(result, source_lang)
        elif target == "typescript":
            result = self._morph_to_typescript(result, source_lang)
        elif target == "react":
            result = self._morph_to_react(result, source_lang)
        
        return result
    
    def _detect_language(self, code: str) -> str:
        """Detect the language of the code."""
        if "def " in code and "import " in code:
            return "python"
        elif "function " in code or "const " in code:
            return "javascript"
        elif "public class" in code or "public static" in code:
            return "java"
        return "unknown"
    
    def _morph_to_async(self, code: str, lang: str) -> str:
        if lang == "python":
            code = re.sub(r"def (\w+)\(", r"async def \1(", code)
            # Add await to function calls
            code = re.sub(r"(\w+)\(([^)]*)\)", r"await \1(\2)", code)
        return code
    
    def _morph_to_class(self, code: str, lang: str) -> str:
        if lang == "python":
            # Wrap in a class
            lines = code.split("\n")
            indented = "\n".join(f"    {line}" for line in lines)
            return f"class GeneratedClass:\n{indented}"
        return code
    
    def _morph_to_functional(self, code: str, lang: str) -> str:
        if lang == "python":
            # Add functional style comments
            return f"# Functional approach\n{code}"
        return code
    
    def _morph_to_typescript(self, code: str, lang: str) -> str:
        if lang == "python":
            code = code.replace("def ", "function ")
            code = re.sub(r"(\w+): str", r"\1: string", code)
            code = re.sub(r"(\w+): int", r"\1: number", code)
            code = re.sub(r"(\w+): bool", r"\1: boolean", code)
        return code
    
    def _morph_to_react(self, code: str, lang: str) -> str:
        if lang in ["javascript", "typescript"]:
            return f"const Component = () => {{\n  return (\n    <div>{code}</div>\n  );\n}};"
        return code


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced GitHub Morph")
    subparsers = parser.add_subparsers(dest="command")
    
    # Discover tools
    subparsers.add_parser("tools", help="List available GitHub tools")
    
    # Detect patterns
    pattern_parser = subparsers.add_parser("patterns", help="Detect patterns in a repository")
    pattern_parser.add_argument("repo", help="GitHub repository URL")
    
    # Smart morph
    morph_parser = subparsers.add_parser("smart-morph", help="Intelligently morph code")
    morph_parser.add_argument("source", help="Source code or file")
    morph_parser.add_argument("--to", "-t", required=True, help="Target pattern")
    
    args = parser.parse_args()
    
    morph = AdvancedGitHubMorph()
    
    if args.command == "tools":
        tools = morph.discover_tools()
        table = Table(title="Available GitHub Tools")
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("URL", style="blue")
        
        for tool in tools:
            table.add_row(tool["name"], tool["description"], tool["url"])
        
        console.print(table)
    
    elif args.command == "patterns":
        patterns = morph.detect_patterns(args.repo)
        
        tree = Tree("Detected Patterns")
        for p in patterns:
            pattern_tree = tree.add(f"[bold]{p.name}[/bold] ({p.pattern_type})")
            pattern_tree.add(f"Confidence: {p.confidence}")
            pattern_tree.add(f"Description: {p.description}")
        
        console.print(tree)
    
    elif args.command == "smart-morph":
        if Path(args.source).exists():
            with open(args.source, "r") as f:
                source_code = f.read()
        else:
            source_code = args.source
        
        result = morph.smart_morph(source_code, args.to)
        console.print(Panel(result, title=f"Smart Morphed to {args.to}", border_style="green"))


if __name__ == "__main__":
    main()