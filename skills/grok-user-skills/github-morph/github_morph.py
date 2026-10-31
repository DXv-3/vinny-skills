#!/usr/bin/env python3
"""
GitHub Morph - A smart tool for treating GitHub as a library of parts.
Extracts components, patterns, and enables intelligent code transformation.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path

try:
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.panel import Panel
except ImportError:
    print("Missing dependencies. Install with: pip install --user requests rich")
    sys.exit(1)

console = Console()

@dataclass
class GitHubRepo:
    """Represents a GitHub repository."""
    owner: str
    name: str
    url: str
    default_branch: str = "main"
    description: str = ""
    language: str = ""
    stars: int = 0

@dataclass
class CodeComponent:
    """Represents an extracted code component."""
    name: str
    file_path: str
    component_type: str  # function, class, module, pattern
    language: str
    code: str
    dependencies: List[str] = field(default_factory=list)
    complexity: int = 0
    lines: int = 0

@dataclass
class PatternMatch:
    """Represents a pattern match in code."""
    pattern_name: str
    file_path: str
    matches: List[Dict[str, Any]]
    confidence: float

class GitHubMorph:
    """Main class for GitHub Morph tool."""
    
    GITHUB_API = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}" if self.token else None
        }
        self.headers = {k: v for k, v in self.headers.items() if v}
    
    def parse_repo_url(self, url: str) -> GitHubRepo:
        """Parse a GitHub URL into a GitHubRepo object."""
        patterns = [
            r"github\.com/([^/]+)/([^/]+)(?:/tree/([^/]+))?",
            r"github\.com/([^/]+)/([^/]+)$",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, name, branch = match.groups()
                return GitHubRepo(
                    owner=owner,
                    name=name,
                    url=url,
                    default_branch=branch or "main"
                )
        
        raise ValueError(f"Invalid GitHub URL: {url}")
    
    def get_repo_info(self, repo: GitHubRepo) -> GitHubRepo:
        """Fetch repository information from GitHub API."""
        response = requests.get(
            f"{self.GITHUB_API}/repos/{repo.owner}/{repo.name}",
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        
        repo.description = data.get("description", "")
        repo.language = data.get("language", "")
        repo.stars = data.get("stargazers_count", 0)
        repo.default_branch = data.get("default_branch", "main")
        
        return repo
    
    def get_repo_tree(self, repo: GitHubRepo) -> List[Dict]:
        """Get the file tree of a repository."""
        response = requests.get(
            f"{self.GITHUB_API}/repos/{repo.owner}/{repo.name}/git/trees/{repo.default_branch}?recursive=1",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get("tree", [])
    
    def get_file_content(self, repo: GitHubRepo, path: str) -> str:
        """Get the content of a file from a repository."""
        response = requests.get(
            f"{self.GITHUB_API}/repos/{repo.owner}/{repo.name}/contents/{path}",
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("encoding") == "base64":
            import base64
            return base64.b64decode(data["content"]).decode("utf-8")
        return data.get("content", "")
    
    def analyze_repo(self, repo_url: str) -> Dict[str, Any]:
        """Analyze a repository and return structure information."""
        repo = self.parse_repo_url(repo_url)
        repo = self.get_repo_info(repo)
        
        console.print(f"[bold blue]Analyzing:[/bold blue] {repo.owner}/{repo.name}")
        
        tree = self.get_repo_tree(repo)
        
        files = {"code": [], "config": [], "docs": [], "other": []}
        languages = {}
        
        for item in tree:
            if item["type"] != "blob":
                continue
            
            path = item["path"]
            ext = Path(path).suffix.lower()
            
            if ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".cpp", ".c", ".cs", ".rb", ".php", ".swift", ".kt"]:
                files["code"].append(path)
                lang = self._get_language_from_ext(ext)
                languages[lang] = languages.get(lang, 0) + 1
            elif ext in [".json", ".yaml", ".yml", ".toml", ".xml", ".ini", ".cfg"]:
                files["config"].append(path)
            elif ext in [".md", ".rst", ".txt"]:
                files["docs"].append(path)
            else:
                files["other"].append(path)
        
        return {
            "repository": f"{repo.owner}/{repo.name}",
            "description": repo.description,
            "language": repo.language,
            "stars": repo.stars,
            "default_branch": repo.default_branch,
            "file_counts": {k: len(v) for k, v in files.items()},
            "languages": languages,
            "code_files": files["code"][:20],
            "config_files": files["config"],
            "doc_files": files["docs"]
        }
    
    def _get_language_from_ext(self, ext: str) -> str:
        """Map file extension to language name."""
        mapping = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".jsx": "JavaScript", ".tsx": "TypeScript", ".go": "Go",
            ".rs": "Rust", ".java": "Java", ".cpp": "C++",
            ".c": "C", ".cs": "C#", ".rb": "Ruby", ".php": "PHP",
            ".swift": "Swift", ".kt": "Kotlin"
        }
        return mapping.get(ext, "Other")
    
    def extract_components(self, repo_url: str, component_type: Optional[str] = None) -> List[CodeComponent]:
        """Extract code components from a repository."""
        repo = self.parse_repo_url(repo_url)
        repo = self.get_repo_info(repo)
        
        console.print(f"[bold blue]Extracting components from:[/bold blue] {repo.owner}/{repo.name}")
        
        tree = self.get_repo_tree(repo)
        components = []
        
        for item in tree:
            if item["type"] != "blob":
                continue
            
            path = item["path"]
            ext = Path(path).suffix.lower()
            
            if ext not in [".py", ".js", ".ts", ".go", ".rs"]:
                continue
            
            try:
                content = self.get_file_content(repo, path)
                file_components = self._parse_components(content, path, ext)
                components.extend(file_components)
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Could not read {path}: {e}")
        
        if component_type:
            components = [c for c in components if c.component_type == component_type]
        
        return components
    
    def _parse_components(self, content: str, path: str, ext: str) -> List[CodeComponent]:
        """Parse code content to extract components."""
        components = []
        language = self._get_language_from_ext(ext)
        lines = content.split("\n")
        
        if ext == ".py":
            for i, line in enumerate(lines):
                if line.strip().startswith("def "):
                    match = re.match(r"def\s+(\w+)\s*\(([^)]*)\)", line)
                    if match:
                        name, params = match.groups()
                        components.append(CodeComponent(
                            name=name,
                            file_path=path,
                            component_type="function",
                            language=language,
                            code=line,
                            lines=1
                        ))
                elif line.strip().startswith("class "):
                    match = re.match(r"class\s+(\w+)", line)
                    if match:
                        name = match.group(1)
                        components.append(CodeComponent(
                            name=name,
                            file_path=path,
                            component_type="class",
                            language=language,
                            code=line,
                            lines=1
                        ))
        
        elif ext in [".js", ".ts"]:
            for i, line in enumerate(lines):
                if re.search(r"(?:function|const|let|var)\s+(\w+)", line):
                    match = re.search(r"(?:function|const|let|var)\s+(\w+)", line)
                    if match:
                        name = match.group(1)
                        components.append(CodeComponent(
                            name=name,
                            file_path=path,
                            component_type="function",
                            language=language,
                            code=line,
                            lines=1
                        ))
                elif line.strip().startswith("class "):
                    match = re.match(r"class\s+(\w+)", line)
                    if match:
                        name = match.group(1)
                        components.append(CodeComponent(
                            name=name,
                            file_path=path,
                            component_type="class",
                            language=language,
                            code=line,
                            lines=1
                        ))
        
        return components
    
    def find_patterns(self, pattern: str, language: Optional[str] = None) -> List[PatternMatch]:
        """Search for code patterns across GitHub repositories."""
        console.print(f"[bold blue]Searching for pattern:[/bold blue] {pattern}")
        
        search_query = f"{pattern} in:file"
        if language:
            search_query += f" language:{language}"
        
        response = requests.get(
            f"{self.GITHUB_API}/search/code",
            params={"q": search_query, "per_page": 20},
            headers=self.headers
        )
        
        if response.status_code != 200:
            console.print(f"[red]Error searching GitHub:[/red] {response.status_code}")
            return []
        
        results = response.json()
        matches = []
        
        for item in results.get("items", []):
            matches.append(PatternMatch(
                pattern_name=pattern,
                file_path=item["path"],
                matches=[{
                    "repository": item["repository"]["full_name"],
                    "url": item["html_url"]
                }],
                confidence=0.8
            ))
        
        return matches
    
    def morph_code(self, source_code: str, target_pattern: str, language: str = "python") -> str:
        """Transform code from one pattern to another."""
        console.print(f"[bold blue]Morphing code to pattern:[/bold blue] {target_pattern}")
        
        morphing_rules = {
            "async": self._to_async,
            "class": self._to_class,
            "functional": self._to_functional,
            "typescript": self._to_typescript,
            "react": self._to_react
        }
        
        if target_pattern in morphing_rules:
            return morphing_rules[target_pattern](source_code, language)
        
        return source_code
    
    def _to_async(self, code: str, language: str) -> str:
        if language == "python":
            code = re.sub(r"def (\w+)\(", r"async def \1(", code)
            return code
        return code
    
    def _to_class(self, code: str, language: str) -> str:
        if language == "python":
            return f"class GeneratedClass:\n    {code}"
        return code
    
    def _to_functional(self, code: str, language: str) -> str:
        if language == "python":
            return f"# Functional version\n{code}"
        return code
    
    def _to_typescript(self, code: str, language: str) -> str:
        code = code.replace("def ", "function ")
        code = re.sub(r"(\w+): str", r"\1: string", code)
        code = re.sub(r"(\w+): int", r"\1: number", code)
        code = re.sub(r"(\w+): bool", r"\1: boolean", code)
        return code
    
    def _to_react(self, code: str, language: str) -> str:
        if language in ["javascript", "typescript"]:
            return f"const Component = () => {{\n  return (\n    <div>{code}</div>\n  );\n}};"
        return code
    
    def run_gitingest(self, repo_url: str) -> str:
        gitingest_url = repo_url.replace("github.com", "gitingest.com")
        console.print(f"[bold blue]Gitingest URL:[/bold blue] {gitingest_url}")
        return gitingest_url
    
    def run_gitreverse(self, repo_url: str) -> str:
        gitreverse_url = f"https://gitreverse.com/{repo_url.split('github.com/')[-1]}"
        console.print(f"[bold blue]Gitreverse URL:[/bold blue] {gitreverse_url}")
        return gitreverse_url


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Morph - Treat GitHub as a library of parts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a repository")
    analyze_parser.add_argument("repo", help="GitHub repository URL")
    
    extract_parser = subparsers.add_parser("extract", help="Extract components from a repository")
    extract_parser.add_argument("repo", help="GitHub repository URL")
    extract_parser.add_argument("--type", choices=["function", "class", "module"], 
                              help="Component type to extract")
    
    find_parser = subparsers.add_parser("find", help="Find code patterns")
    find_parser.add_argument("pattern", help="Pattern to search for")
    find_parser.add_argument("--language", "-l", help="Language filter")
    
    morph_parser = subparsers.add_parser("morph", help="Morph code to a pattern")
    morph_parser.add_argument("source", help="Source code or file")
    morph_parser.add_argument("--to", "-t", required=True, help="Target pattern")
    morph_parser.add_argument("--language", "-l", default="python", help="Source language")
    
    compose_parser = subparsers.add_parser("compose", help="Compose multiple components")
    compose_parser.add_argument("components", nargs="+", help="Components to compose")
    
    gitreverse_parser = subparsers.add_parser("gitreverse", help="Get gitreverse URL for a repo")
    gitreverse_parser.add_argument("repo", help="GitHub repository URL")
    
    gitingest_parser = subparsers.add_parser("gitingest", help="Get gitingest URL for a repo")
    gitingest_parser.add_argument("repo", help="GitHub repository URL")

    handoff_parser = subparsers.add_parser(
        "handoff",
        help="Build unified HANDOFF bundle (see ~/Documents/gitreverse/git_handoff.py)",
    )
    handoff_parser.add_argument("repo", help="GitHub repository URL or owner/repo")
    handoff_parser.add_argument("-o", "--output", help="Output directory")
    handoff_parser.add_argument("--fast", action="store_true", help="Skip gitingest ingest")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    morph = GitHubMorph()
    
    if args.command == "analyze":
        result = morph.analyze_repo(args.repo)
        console.print(Panel(json.dumps(result, indent=2), title="Repository Analysis", border_style="green"))
    
    elif args.command == "extract":
        components = morph.extract_components(args.repo, args.type)
        
        table = Table(title="Extracted Components")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("File", style="yellow")
        table.add_column("Language", style="green")
        
        for comp in components[:20]:
            table.add_row(comp.name, comp.component_type, comp.file_path, comp.language)
        
        console.print(table)
    
    elif args.command == "find":
        matches = morph.find_patterns(args.pattern, args.language)
        
        table = Table(title=f"Pattern Matches: {args.pattern}")
        table.add_column("Repository", style="cyan")
        table.add_column("File", style="yellow")
        
        for match in matches[:20]:
            for m in match.matches:
                table.add_row(m["repository"], match.file_path)
        
        console.print(table)
    
    elif args.command == "morph":
        if Path(args.source).exists():
            with open(args.source, "r") as f:
                source_code = f.read()
        else:
            source_code = args.source
        
        result = morph.morph_code(source_code, args.to, args.language)
        console.print(Panel(result, title=f"Morhed to {args.to}", border_style="green"))
    
    elif args.command == "gitreverse":
        url = morph.run_gitreverse(args.repo)
        console.print(f"[bold green]Open in browser:[/bold green] {url}")
    
    elif args.command == "gitingest":
        url = morph.run_gitingest(args.repo)
        console.print(f"[bold green]Open in browser:[/bold green] {url}")

    elif args.command == "handoff":
        import subprocess
        handoff_script = Path.home() / "Documents/gitreverse/handoff"
        cmd = [str(handoff_script), "reverse", args.repo]
        if args.output:
            cmd.extend(["-o", args.output])
        if args.fast:
            cmd.append("--fast")
        subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
