#!/usr/bin/env python3
"""
VinnyOS Engine — Unified MCP Server

13 layers. One server. Any client can call it.

Layers 1-4:  find-skills pipeline (query explosion, harvest, decompose, synthesize)
Layers 5-10: github-ecosystem pipeline (discover, analyze, extract, isolate, validate, integrate)
Layer 11:    SELF-HEAL (detect breaks, find fixes)
Layer 12:    DREAM (consolidate during idle)
Layer 13:    GRAPH (codebase-memory queries)

Architecture: Python MCP server that calls existing tools via subprocess.
No porting. No rewriting. Just orchestration.
"""

import subprocess
import json
import os
import sys
import time
import hashlib
import base64
import re
import importlib.util
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# ──────────────────────────────────────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────────────────────────────────────

HOME = Path.home()
FIND_SKILLS_DIR = HOME / ".agents" / "skills" / "find-skills" / "pipeline"
GITHUB_ECOSYSTEM_DIR = HOME / ".claude" / "skills" / "github-ecosystem"
CODEBASE_MEMORY = HOME / "bin" / "codebase-memory-mcp"
VINNYOS_DIR = HOME / ".vinnyos"
STATE_FILE = HOME / "VINNYOS-STATE.md"
DREAM_DIR = VINNYOS_DIR / "dream"
HEAL_DIR = VINNYOS_DIR / "heal"
CACHE_DIR = VINNYOS_DIR / "cache"

# Ensure directories exist
for d in [VINNYOS_DIR, DREAM_DIR, HEAL_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def get_cache(key: str, max_age_hours: int = 24) -> dict | None:
    """Get cached result if exists and not expired."""
    cache_file = CACHE_DIR / f"{hashlib.md5(key.encode()).hexdigest()}.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text())
            cached_time = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
            if datetime.now() - cached_time < timedelta(hours=max_age_hours):
                return data.get("result")
        except (json.JSONDecodeError, ValueError):
            pass
    return None


def set_cache(key: str, result: dict):
    """Cache a result with timestamp."""
    cache_file = CACHE_DIR / f"{hashlib.md5(key.encode()).hexdigest()}.json"
    data = {
        "cached_at": datetime.now().isoformat(),
        "result": result
    }
    cache_file.write_text(json.dumps(data, indent=2))


def run_cmd(cmd: list[str], cwd: str = None, timeout: int = 60) -> dict:
    """Run a command and return stdout, stderr, and return code."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Command timed out", "returncode": -1, "success": False}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "returncode": -1, "success": False}


def run_node(script: str, args: list[str], timeout: int = 60) -> dict:
    """Run a Node.js script from find-skills pipeline."""
    script_path = FIND_SKILLS_DIR / script
    if not script_path.exists():
        return {"stdout": "", "stderr": f"Script not found: {script_path}", "returncode": -1, "success": False}
    return run_cmd(["node", str(script_path)] + args, cwd=str(FIND_SKILLS_DIR), timeout=timeout)


def run_codebase_memory(args: list[str], timeout: int = 30) -> dict:
    """Run codebase-memory-mcp CLI command."""
    return run_cmd([str(CODEBASE_MEMORY)] + args, timeout=timeout)


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 1: EXPLORE (Query Explosion)
# ──────────────────────────────────────────────────────────────────────────────

def explore(topic: str, max_queries: int = 12) -> dict:
    """
    Generate diverse search queries from a topic.
    Uses find-skills explode.mjs to create synonyms, adjacent domains, creative mashups.
    """
    # Call find-skills explode via wrapper script
    wrapper_script = FIND_SKILLS_DIR / "explode_wrapper.mjs"
    if wrapper_script.exists():
        result = run_cmd(["node", str(wrapper_script), topic], cwd=str(FIND_SKILLS_DIR))
        
        if result["success"] and result["stdout"]:
            try:
                queries = json.loads(result["stdout"])
                return {
                    "topic": topic,
                    "queries": queries[:max_queries],
                    "source": "find-skills",
                    "count": min(len(queries), max_queries)
                }
            except json.JSONDecodeError:
                pass
    
    # Fallback: generate queries ourselves
    queries = _generate_queries_fallback(topic)
    return {
        "topic": topic,
        "queries": queries[:max_queries],
        "source": "fallback",
        "count": min(len(queries), max_queries)
    }


def _generate_queries_fallback(topic: str) -> list[str]:
    """Fallback query generation when find-skills is unavailable."""
    words = topic.lower().split()
    queries = [topic]
    
    # Add synonyms and variations
    for word in words:
        if len(word) > 3:
            queries.append(f"{word} library")
            queries.append(f"{word} framework")
            queries.append(f"{word} tool")
            queries.append(f"best {word}")
            queries.append(f"{word} alternative")
    
    # Add domain crossovers
    queries.append(f"{topic} python")
    queries.append(f"{topic} open source")
    queries.append(f"{topic} self-hosted")
    queries.append(f"{topic} agent")
    queries.append(f"{topic} MCP")
    
    return list(set(queries))


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 2: HARVEST (Multi-Shelf Search)
# ──────────────────────────────────────────────────────────────────────────────

def harvest(queries: list[str], seeds_only: bool = False, limit_per_query: int = 8, surfaces: list[str] = None) -> dict:
    """
    Search multiple sources for repos matching queries.
    Sources: GitHub repos, code, issues, PRs, gists.
    """
    if surfaces is None:
        surfaces = ["repos", "code", "issues"]
    
    candidates = []
    
    for query in queries[:10]:  # Limit to 10 queries
        # Check cache first
        cache_key = f"harvest:{query}:{limit_per_query}"
        cached = get_cache(cache_key, max_age_hours=6)
        if cached:
            candidates.extend(cached)
            continue
        
        query_candidates = []
        
        # Search repos
        if "repos" in surfaces:
            result = run_cmd([
                "gh", "search", "repos", query,
                "--sort", "stars",
                "--limit", str(limit_per_query),
                "--json", "fullName,description,stargazersCount,updatedAt,language,url"
            ])
            
            if result["success"] and result["stdout"]:
                try:
                    repos = json.loads(result["stdout"])
                    for repo in repos:
                        query_candidates.append({
                            "repo": repo.get("fullName", ""),
                            "description": repo.get("description", ""),
                            "stars": repo.get("stargazersCount", 0),
                            "language": repo.get("language", ""),
                            "url": repo.get("url", ""),
                            "query": query,
                            "surface": "repo",
                            "source": "github"
                        })
                except json.JSONDecodeError:
                    pass
        
        # Search code
        if "code" in surfaces:
            result = run_cmd([
                "gh", "search", "code", query,
                "--limit", str(limit_per_query),
                "--json", "repository,path,textMatches"
            ])
            
            if result["success"] and result["stdout"]:
                try:
                    code_results = json.loads(result["stdout"])
                    for code in code_results:
                        repo_name = code.get("repository", {}).get("fullName", "")
                        query_candidates.append({
                            "repo": repo_name,
                            "description": f"Code: {code.get('path', '')}",
                            "stars": 0,
                            "language": "",
                            "url": f"https://github.com/{repo_name}/blob/main/{code.get('path', '')}",
                            "query": query,
                            "surface": "code",
                            "path": code.get("path", ""),
                            "source": "github"
                        })
                except json.JSONDecodeError:
                    pass
        
        # Search issues
        if "issues" in surfaces:
            result = run_cmd([
                "gh", "search", "issues", query,
                "--sort", "created",
                "--limit", str(limit_per_query),
                "--json", "repository,title,url,createdAt,state"
            ])
            
            if result["success"] and result["stdout"]:
                try:
                    issues = json.loads(result["stdout"])
                    for issue in issues:
                        repo_name = issue.get("repository", {}).get("fullName", "")
                        query_candidates.append({
                            "repo": repo_name,
                            "description": f"Issue: {issue.get('title', '')}",
                            "stars": 0,
                            "language": "",
                            "url": issue.get("url", ""),
                            "query": query,
                            "surface": "issue",
                            "state": issue.get("state", ""),
                            "source": "github"
                        })
                except json.JSONDecodeError:
                    pass
        
        # Cache the results for this query
        if query_candidates:
            set_cache(cache_key, query_candidates)
            candidates.extend(query_candidates)
    
    # Deduplicate by repo name
    seen = set()
    unique = []
    for c in candidates:
        key = f"{c['repo']}:{c.get('surface', 'repo')}:{c.get('path', '')}"
        if key not in seen:
            seen.add(key)
            unique.append(c)
    
    # Sort by stars
    unique.sort(key=lambda x: x.get("stars", 0), reverse=True)
    
    return {
        "queries": queries,
        "candidates": unique[:50],  # Top 50
        "total": len(unique),
        "source": "github"
    }


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 3: DECOMPOSE (Parts Extraction)
# ──────────────────────────────────────────────────────────────────────────────

def decompose(repo: str) -> dict:
    """
    Extract reusable parts from a repo's README/docs.
    Parts: features, workflows, prompts, mental models, code snippets.
    """
    # Get README content
    result = run_cmd([
        "gh", "api", f"repos/{repo}/contents/README.md",
        "--jq", ".content"
    ])
    
    if not result["success"]:
        return {"repo": repo, "parts": [], "error": "Could not fetch README"}
    
    # Decode base64
    try:
        content = base64.b64decode(result["stdout"]).decode("utf-8")
    except Exception:
        content = result["stdout"]
    
    # Extract parts using heuristics
    parts = _extract_parts_from_text(content, repo)
    
    return {
        "repo": repo,
        "parts": parts,
        "total": len(parts)
    }


def _extract_parts_from_text(text: str, source: str) -> list[dict]:
    """Extract parts from text using heuristics."""
    parts = []
    lines = text.split("\n")
    
    current_section = ""
    current_type = "feature"
    
    for line in lines:
        # Detect section headers
        if line.startswith("## ") or line.startswith("### "):
            current_section = line.lstrip("#").strip()
            
            # Infer type from section name
            lower = current_section.lower()
            if any(w in lower for w in ["workflow", "process", "step", "how"]):
                current_type = "workflow"
            elif any(w in lower for w in ["prompt", "instruction", "system"]):
                current_type = "prompt"
            elif any(w in lower for w in ["feature", "capability", "what"]):
                current_type = "feature"
            elif any(w in lower for w in ["code", "example", "snippet"]):
                current_type = "snippet"
            elif any(w in lower for w in ["mental", "model", "concept", "idea"]):
                current_type = "mental-model"
            elif any(w in lower for w in ["edge", "case", "limitation", "warning"]):
                current_type = "edge-case"
        
        # Extract bullet points as parts
        if line.strip().startswith(("- ", "* ", "• ")):
            part_text = line.strip()[2:].strip()
            if len(part_text) > 20:  # Minimum length
                parts.append({
                    "type": current_type,
                    "text": part_text[:500],  # Limit length
                    "section": current_section,
                    "source": source
                })
    
    return parts


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 4: SYNTHESIZE (Idea Matching)
# ──────────────────────────────────────────────────────────────────────────────

def synthesize(idea: str, parts: list[dict]) -> dict:
    """
    Match an idea against harvested parts.
    Returns: relevant parts, confirmed parts, contradicted parts, gaps to invent.
    """
    idea_tokens = set(idea.lower().split())
    
    scored = []
    for part in parts:
        part_text = (part.get("text", "") + " " + part.get("section", "")).lower()
        part_tokens = set(part_text.split())
        
        # Calculate overlap
        overlap = len(idea_tokens & part_tokens) / max(1, len(idea_tokens))
        
        # Determine relationship
        if part.get("seeded"):
            rel = "EXTEND"
            score = max(overlap, 0.2)
        elif overlap >= 0.18:
            rel = "EXTEND"
            score = overlap
        elif overlap >= 0.08:
            rel = "COMBINE"
            score = overlap
        else:
            rel = "CONFIRM"
            score = overlap
        
        scored.append({**part, "rel": rel, "score": score})
    
    # Filter to wanted parts
    wanted = [p for p in scored if p["rel"] in ("EXTEND", "COMBINE")]
    wanted.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    confirmed = [p for p in scored if p["rel"] == "CONFIRM"]
    contradicted = [p for p in scored if p["rel"] == "CONTRADICT"]
    
    # Find gaps
    covered_words = set()
    for p in wanted:
        covered_words.update(p.get("text", "").lower().split())
    
    gaps = [w for w in idea_tokens if w not in covered_words and len(w) > 3]
    
    return {
        "idea": idea,
        "wanted": wanted[:25],
        "confirmed": len(confirmed),
        "contradicted": contradicted,
        "gaps": gaps,
        "recipe": {
            "lift": [p for p in wanted if p.get("trust") in ("HIGH", "MED")][:10],
            "adapt": [p for p in wanted if p.get("trust") == "LOW"][:10],
            "invent": [f"INVENT: no existing part covers '{g}'" for g in gaps[:5]]
        }
    }


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 5: DISCOVER (GitHub Layer Search)
# ──────────────────────────────────────────────────────────────────────────────

# Layer definitions (from github-ecosystem)
LAYERS = {
    "capture": {
        "description": "Data ingestion, scraping, collection, monitoring",
        "patterns": ['"data ingestion" language:python sort:stars', '"web scraper" AI self-hosted']
    },
    "fuse": {
        "description": "Dedup, entity resolution, context management",
        "patterns": ['"entity resolution" dedup', '"knowledge graph" self-hosted']
    },
    "think": {
        "description": "Memory, knowledge graphs, reasoning",
        "patterns": ['"AI memory" local', '"vector database" agent']
    },
    "act": {
        "description": "Orchestration, execution, coordination",
        "patterns": ['"agent orchestration" framework', '"multi agent" MCP']
    },
    "self": {
        "description": "Self-healing, adaptation, learning loops",
        "patterns": ['"self improving" AI', '"self healing" system']
    },
    "dream": {
        "description": "Consolidation, subconscious, reorganization",
        "patterns": ['"memory consolidation" AI', '"dream" memory AI']
    }
}


def discover(layer: str, limit: int = 10) -> dict:
    """Discover top repos for a specific layer."""
    if layer not in LAYERS:
        return {"error": f"Unknown layer: {layer}. Valid: {list(LAYERS.keys())}"}
    
    all_results = []
    for pattern in LAYERS[layer]["patterns"]:
        result = run_cmd([
            "gh", "search", "repos", pattern,
            "--sort", "stars",
            "--limit", str(limit),
            "--json", "fullName,description,stargazersCount,updatedAt,language,url"
        ])
        
        if result["success"] and result["stdout"]:
            try:
                repos = json.loads(result["stdout"])
                all_results.extend(repos)
            except json.JSONDecodeError:
                pass
    
    # Deduplicate
    seen = set()
    unique = []
    for r in all_results:
        name = r.get("fullName", "")
        if name and name not in seen:
            seen.add(name)
            unique.append(r)
    
    unique.sort(key=lambda x: x.get("stargazersCount", 0), reverse=True)
    
    return {
        "layer": layer,
        "description": LAYERS[layer]["description"],
        "repos": unique[:limit],
        "total": len(unique)
    }


def discover_all(limit: int = 5) -> dict:
    """Discover top tools for all layers."""
    results = {}
    for layer in LAYERS:
        results[layer] = discover(layer, limit)
    return results


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 6: ANALYZE (Repo Structure Analysis)
# ──────────────────────────────────────────────────────────────────────────────

def analyze(repo: str) -> dict:
    """Analyze a repo's structure and identify reusable modules."""
    # Get repo info
    result = run_cmd([
        "gh", "repo", "view", repo,
        "--json", "nameWithOwner,description,stargazerCount,updatedAt,primaryLanguage,licenseInfo,url"
    ])
    
    if not result["success"]:
        return {"error": f"Cannot access repository: {repo}"}
    
    info = json.loads(result["stdout"])
    
    # Use codebase-memory for deep analysis
    graph_result = run_codebase_memory([
        "cli", "get_architecture",
        "--repo-path", str(HOME / "Projects" / "GitHub-Repos" / repo.split("/")[-1])
    ])
    
    graph_data = {}
    if graph_result["success"]:
        try:
            graph_data = json.loads(graph_result["stdout"])
        except json.JSONDecodeError:
            pass
    
    return {
        "repo": repo,
        "info": info,
        "architecture": graph_data,
        "has_graph": bool(graph_data)
    }


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 7: EXTRACT (Code Extraction)
# ──────────────────────────────────────────────────────────────────────────────

def extract(repo: str, path: str) -> dict:
    """Extract a specific file from a repo."""
    result = run_cmd([
        "gh", "api", f"repos/{repo}/contents/{path}",
        "--jq", ".content"
    ])
    
    if not result["success"]:
        return {"error": f"Cannot fetch: {path}"}
    
    try:
        content = base64.b64decode(result["stdout"]).decode("utf-8")
    except Exception:
        content = result["stdout"]
    
    # Save to extraction directory
    extract_dir = VINNYOS_DIR / "extracted" / repo.replace("/", "_")
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    target_file = extract_dir / Path(path).name
    target_file.write_text(content)
    
    return {
        "repo": repo,
        "path": path,
        "extract_dir": str(extract_dir),
        "file": str(target_file),
        "lines": len(content.split("\n"))
    }


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 8: ISOLATE (Safe Wrappers)
# ──────────────────────────────────────────────────────────────────────────────

def isolate(extract_dir: str, class_name: str = "Wrapper") -> dict:
    """Generate a safe wrapper for extracted code."""
    extract_path = Path(extract_dir)
    py_files = list(extract_path.glob("*.py"))
    
    if not py_files:
        return {"error": "No Python files found"}
    
    main_file = py_files[0]
    content = main_file.read_text()
    
    # Find classes
    classes = re.findall(r"class\s+(\w+)", content)
    
    if classes:
        class_name_found = classes[0]
        wrapper_code = f'''"""
Safe wrapper for {class_name_found}
Generated by VinnyOS Engine
"""

import importlib.util
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class {class_name}:
    """Isolated wrapper with error handling."""
    
    def __init__(self, **kwargs):
        try:
            spec = importlib.util.spec_from_file_location(
                "original",
                str(Path(__file__).parent / "{main_file.name}")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._wrapped = module.{class_name_found}(**kwargs)
            self._ready = True
        except Exception as e:
            logger.error(f"Init failed: {{e}}")
            self._wrapped = None
            self._ready = False
    
    def is_ready(self) -> bool:
        return self._ready
    
    def __getattr__(self, name):
        if not self._ready:
            raise RuntimeError("Wrapper not initialized")
        attr = getattr(self._wrapped, name)
        if callable(attr):
            def safe(*args, **kwargs):
                try:
                    return attr(*args, **kwargs)
                except Exception as e:
                    logger.error(f"{{name}} failed: {{e}}")
                    return None
            return safe
        return attr
'''
    else:
        wrapper_code = f'''"""
Safe function wrappers
Generated by VinnyOS Engine
"""

import importlib.util
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_spec = importlib.util.spec_from_file_location(
    "original",
    str(Path(__file__).parent / "{main_file.name}")
)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
'''
    
    wrapper_file = extract_path / f"wrapper_{class_name}.py"
    wrapper_file.write_text(wrapper_code)
    
    return {
        "wrapper_file": str(wrapper_file),
        "wrapped_class": classes[0] if classes else None,
        "ready": True
    }


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 9: VALIDATE (Import Testing)
# ──────────────────────────────────────────────────────────────────────────────

def validate(extract_dir: str) -> dict:
    """Test that extracted code compiles and runs."""
    extract_path = Path(extract_dir)
    
    results = []
    for py_file in extract_path.glob("*.py"):
        try:
            spec = importlib.util.spec_from_file_location(py_file.stem, str(py_file))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            results.append({"file": py_file.name, "status": "OK"})
        except Exception as e:
            results.append({"file": py_file.name, "status": "ERROR", "error": str(e)})
    
    return {
        "extract_dir": str(extract_dir),
        "results": results,
        "all_passed": all(r["status"] == "OK" for r in results)
    }


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 10: INTEGRATE (Project Wiring)
# ──────────────────────────────────────────────────────────────────────────────

def integrate(extract_dir: str, project_dir: str) -> dict:
    """Generate import statements and copy code to project."""
    extract_path = Path(extract_dir)
    project_path = Path(project_dir)
    
    # Copy extracted code
    target_dir = project_path / "vinnyos_modules" / extract_path.name
    target_dir.mkdir(parents=True, exist_ok=True)
    
    copied = []
    for file in extract_path.glob("*"):
        if file.is_file():
            shutil.copy2(file, target_dir / file.name)
            copied.append(file.name)
    
    # Generate import code
    imports = []
    for py_file in extract_path.glob("wrapper_*.py"):
        module_name = py_file.stem
        imports.append(f"from vinnyos_modules.{extract_path.name}.{module_name} import *")
    
    integration_code = f'''"""
Integration for {extract_path.name}
Generated by VinnyOS Engine
"""

{chr(10).join(imports)}
'''
    
    integration_file = project_path / f"vinnyos_{extract_path.name}_integration.py"
    integration_file.write_text(integration_code)
    
    return {
        "target_dir": str(target_dir),
        "integration_file": str(integration_file),
        "copied": copied,
        "imports": imports
    }


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 11: SELF-HEAL (Detect Breaks, Find Fixes)
# ──────────────────────────────────────────────────────────────────────────────

def self_heal(problem: str = None) -> dict:
    """
    Detect system issues and find fixes.
    Checks: MCP servers, installed tools, indexed projects, disk space.
    """
    issues = []
    fixes = []
    
    # Check codebase-memory
    result = run_codebase_memory(["--version"])
    if not result["success"]:
        issues.append("codebase-memory-mcp not responding")
        fixes.append("Reinstall: curl -sL <release-url> -o ~/bin/codebase-memory-mcp")
    
    # Check MCP servers
    for client, config_path in [
        ("opencode", HOME / ".config" / "opencode" / "opencode.json"),
        ("kilo", HOME / ".config" / "kilo" / "kilo.jsonc"),
        ("hermes", HOME / ".hermes" / "config.yaml"),
        ("grok", HOME / ".grok" / "config.toml"),
    ]:
        if config_path.exists():
            content = config_path.read_text()
            if "github-ecosystem" not in content:
                issues.append(f"{client} missing github-ecosystem MCP")
                fixes.append(f"Add github-ecosystem to {config_path}")
            if "codebase-memory" not in content:
                issues.append(f"{client} missing codebase-memory MCP")
                fixes.append(f"Add codebase-memory to {config_path}")
    
    # Check disk space
    stat = os.statvfs("/")
    free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
    if free_gb < 20:
        issues.append(f"Low disk space: {free_gb:.1f}GB free")
        fixes.append("Run disk cleanup: delete old backups, caches")
    
    # Check indexed projects
    result = run_codebase_memory(["cli", "list_projects"])
    if result["success"]:
        try:
            # Handle both JSON and non-JSON output
            stdout = result["stdout"].strip()
            if stdout.startswith("{"):
                data = json.loads(stdout)
            else:
                # Skip first line if it's a header
                lines = stdout.split("\n")
                if len(lines) > 1:
                    data = json.loads(lines[1])
                else:
                    data = json.loads(stdout)
            project_count = len(data.get("projects", []))
            if project_count < 10:
                issues.append(f"Only {project_count} projects indexed")
                fixes.append("Index more projects: codebase-memory-mcp cli index_repository --repo-path <path>")
        except (json.JSONDecodeError, IndexError):
            pass
    
    return {
        "status": "healthy" if not issues else "issues_found",
        "issues": issues,
        "fixes": fixes,
        "checked_at": datetime.now().isoformat()
    }


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 12: DREAM (Consolidate During Idle)
# ──────────────────────────────────────────────────────────────────────────────

def dream() -> dict:
    """
    Consolidate knowledge during idle time.
    - Merge duplicate indexed projects
    - Update VINNYOS-STATE.md
    - Clean up temporary files
    - Generate morning report
    """
    actions = []
    
    # Clean up temp extraction files
    extracted_dir = VINNYOS_DIR / "extracted"
    if extracted_dir.exists():
        count = 0
        for item in extracted_dir.iterdir():
            if item.is_dir():
                # Check if older than 7 days
                if time.time() - item.stat().st_mtime > 7 * 24 * 3600:
                    shutil.rmtree(item, ignore_errors=True)
                    count += 1
        if count > 0:
            actions.append(f"Cleaned {count} old extraction directories")
    
    # Update state file
    if STATE_FILE.exists():
        try:
            content = STATE_FILE.read_text()
            # Update timestamp — find "Last updated:" line and replace date
            import re as _re
            content = _re.sub(
                r"Last updated:\s*\d{4}-\d{2}-\d{2}",
                f"Last updated: {datetime.now().strftime('%Y-%m-%d')}",
                content
            )
            STATE_FILE.write_text(content)
            actions.append("Updated VINNYOS-STATE.md timestamp")
        except Exception as e:
            actions.append(f"Failed to update state file: {e}")
    
    # Generate dream report
    report = {
        "timestamp": datetime.now().isoformat(),
        "actions": actions,
        "status": "consolidation_complete"
    }
    
    # Save dream report
    report_file = DREAM_DIR / f"dream_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(json.dumps(report, indent=2))
    
    return report


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 13: GRAPH (Codebase-Memory Queries)
# ──────────────────────────────────────────────────────────────────────────────

def graph_search(project: str, pattern: str) -> dict:
    """Search the knowledge graph for symbols matching a pattern."""
    result = run_codebase_memory([
        "cli", "search_graph",
        "--project", project,
        "--name_pattern", pattern
    ])
    
    if not result["success"]:
        return {"error": result["stderr"]}
    
    try:
        return json.loads(result["stdout"].split("\n", 1)[1])
    except (json.JSONDecodeError, IndexError):
        return {"raw": result["stdout"]}


def graph_list_projects() -> dict:
    """List all indexed projects."""
    result = run_codebase_memory(["cli", "list_projects"])
    
    if not result["success"]:
        return {"error": result["stderr"]}
    
    try:
        return json.loads(result["stdout"].split("\n", 1)[1])
    except (json.JSONDecodeError, IndexError):
        return {"raw": result["stdout"]}


def graph_architecture(project: str) -> dict:
    """Get architecture overview of a project."""
    result = run_codebase_memory([
        "cli", "get_architecture",
        "--project", project
    ])
    
    if not result["success"]:
        return {"error": result["stderr"]}
    
    try:
        return json.loads(result["stdout"].split("\n", 1)[1])
    except (json.JSONDecodeError, IndexError):
        return {"raw": result["stdout"]}


# ──────────────────────────────────────────────────────────────────────────────
# HIGH-LEVEL ORCHESTRATION
# ──────────────────────────────────────────────────────────────────────────────

def full_pipeline(topic: str, idea: str, project_dir: str = ".") -> dict:
    """
    Complete pipeline: explore → harvest → decompose → synthesize → discover → extract → integrate
    """
    results = {"steps": []}
    
    # Step 1: Explore
    explore_result = explore(topic)
    results["steps"].append({"step": "explore", "result": explore_result})
    
    # Step 2: Harvest
    harvest_result = harvest(explore_result["queries"])
    results["steps"].append({"step": "harvest", "result": harvest_result})
    
    # Step 3: Decompose top candidates
    all_parts = []
    for candidate in harvest_result["candidates"][:5]:
        decomp = decompose(candidate["repo"])
        all_parts.extend(decomp.get("parts", []))
    results["steps"].append({"step": "decompose", "result": {"total_parts": len(all_parts)}})
    
    # Step 4: Synthesize
    synth = synthesize(idea, all_parts)
    results["steps"].append({"step": "synthesize", "result": synth})
    
    # Step 5: Discover best layer
    discover_result = discover("think", 5)
    results["steps"].append({"step": "discover", "result": discover_result})
    
    results["summary"] = {
        "topic": topic,
        "idea": idea,
        "candidates_found": len(harvest_result["candidates"]),
        "parts_extracted": len(all_parts),
        "parts_wanted": len(synth["wanted"]),
        "gaps_to_invent": len(synth["gaps"])
    }
    
    return results


# ──────────────────────────────────────────────────────────────────────────────
# MCP SERVER
# ──────────────────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "explore",
        "description": "Generate diverse search queries from a topic (query explosion)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to explore"},
                "max_queries": {"type": "integer", "description": "Max queries to generate", "default": 12}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "harvest",
        "description": "Search GitHub for repos matching queries",
        "inputSchema": {
            "type": "object",
            "properties": {
                "queries": {"type": "array", "items": {"type": "string"}, "description": "Queries to search"},
                "limit_per_query": {"type": "integer", "description": "Max results per query", "default": 8},
                "seeds_only": {"type": "boolean", "description": "Only use cached seeds", "default": False},
                "surfaces": {"type": "array", "items": {"type": "string"}, "description": "Search surfaces (repos, code, issues)", "default": ["repos", "code", "issues"]}
            },
            "required": ["queries"]
        }
    },
    {
        "name": "decompose",
        "description": "Extract reusable parts from a repo's README/docs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "GitHub repo (owner/name)"}
            },
            "required": ["repo"]
        }
    },
    {
        "name": "synthesize",
        "description": "Match an idea against harvested parts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "idea": {"type": "string", "description": "Idea to match against parts"},
                "parts": {"type": "array", "description": "Parts to match against"}
            },
            "required": ["idea", "parts"]
        }
    },
    {
        "name": "discover_layer",
        "description": "Find best GitHub repos for a specific layer (capture/fuse/think/act/self/dream)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "layer": {"type": "string", "description": "Layer to search"},
                "limit": {"type": "integer", "description": "Max results", "default": 10}
            },
            "required": ["layer"]
        }
    },
    {
        "name": "discover_all",
        "description": "Discover top tools for all 6 layers",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max results per layer", "default": 5}
            }
        }
    },
    {
        "name": "analyze_repo",
        "description": "Analyze a repo's structure and architecture",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "GitHub repo (owner/name)"}
            },
            "required": ["repo"]
        }
    },
    {
        "name": "extract_file",
        "description": "Extract a specific file from a GitHub repo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "GitHub repo (owner/name)"},
                "path": {"type": "string", "description": "File path in repo"}
            },
            "required": ["repo", "path"]
        }
    },
    {
        "name": "isolate_wrapper",
        "description": "Generate a safe wrapper for extracted code",
        "inputSchema": {
            "type": "object",
            "properties": {
                "extract_dir": {"type": "string", "description": "Path to extracted code"},
                "class_name": {"type": "string", "description": "Wrapper class name", "default": "Wrapper"}
            },
            "required": ["extract_dir"]
        }
    },
    {
        "name": "validate_extraction",
        "description": "Test that extracted code compiles and runs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "extract_dir": {"type": "string", "description": "Path to extracted code"}
            },
            "required": ["extract_dir"]
        }
    },
    {
        "name": "integrate_code",
        "description": "Copy extracted code to project and generate imports",
        "inputSchema": {
            "type": "object",
            "properties": {
                "extract_dir": {"type": "string", "description": "Path to extracted code"},
                "project_dir": {"type": "string", "description": "Target project directory", "default": "."}
            },
            "required": ["extract_dir"]
        }
    },
    {
        "name": "self_heal",
        "description": "Check system health and find fixes for issues",
        "inputSchema": {
            "type": "object",
            "properties": {
                "problem": {"type": "string", "description": "Specific problem to investigate"}
            }
        }
    },
    {
        "name": "dream",
        "description": "Consolidate knowledge during idle time",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "graph_search",
        "description": "Search the knowledge graph for symbols",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Indexed project name"},
                "pattern": {"type": "string", "description": "Search pattern (regex)"}
            },
            "required": ["project", "pattern"]
        }
    },
    {
        "name": "graph_projects",
        "description": "List all indexed projects in the knowledge graph",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "graph_architecture",
        "description": "Get architecture overview of an indexed project",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Indexed project name"}
            },
            "required": ["project"]
        }
    },
    {
        "name": "full_pipeline",
        "description": "Complete pipeline: explore → harvest → decompose → synthesize → discover → extract → integrate",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to explore"},
                "idea": {"type": "string", "description": "Idea to match against"},
                "project_dir": {"type": "string", "description": "Target project directory", "default": "."}
            },
            "required": ["topic", "idea"]
        }
    }
]


def send_response(req_id, result):
    resp = {"jsonrpc": "2.0", "id": req_id, "result": result}
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()


def send_error(req_id, code, message):
    resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        # Run as MCP server (JSON-RPC over stdin/stdout)
        initialized = False
        
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            method = msg.get("method")
            req_id = msg.get("id")
            params = msg.get("params", {})
            
            if method == "initialize":
                send_response(req_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "vinnyos-engine", "version": "1.0.0"}
                })
                initialized = True
            
            elif method == "notifications/initialized":
                pass
            
            elif method == "tools/list":
                send_response(req_id, {"tools": TOOLS})
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                try:
                    if tool_name == "explore":
                        result = explore(arguments["topic"], arguments.get("max_queries", 12))
                    elif tool_name == "harvest":
                        result = harvest(arguments["queries"], seeds_only=arguments.get("seeds_only", False), limit_per_query=arguments.get("limit_per_query", 8), surfaces=arguments.get("surfaces"))
                    elif tool_name == "decompose":
                        result = decompose(arguments["repo"])
                    elif tool_name == "synthesize":
                        result = synthesize(arguments["idea"], arguments["parts"])
                    elif tool_name == "discover_layer":
                        result = discover(arguments["layer"], arguments.get("limit", 10))
                    elif tool_name == "discover_all":
                        result = discover_all(arguments.get("limit", 5))
                    elif tool_name == "analyze_repo":
                        result = analyze(arguments["repo"])
                    elif tool_name == "extract_file":
                        result = extract(arguments["repo"], arguments["path"])
                    elif tool_name == "isolate_wrapper":
                        result = isolate(arguments["extract_dir"], arguments.get("class_name", "Wrapper"))
                    elif tool_name == "validate_extraction":
                        result = validate(arguments["extract_dir"])
                    elif tool_name == "integrate_code":
                        result = integrate(arguments["extract_dir"], arguments.get("project_dir", "."))
                    elif tool_name == "self_heal":
                        result = self_heal(arguments.get("problem"))
                    elif tool_name == "dream":
                        result = dream()
                    elif tool_name == "graph_search":
                        result = graph_search(arguments["project"], arguments["pattern"])
                    elif tool_name == "graph_projects":
                        result = graph_list_projects()
                    elif tool_name == "graph_architecture":
                        result = graph_architecture(arguments["project"])
                    elif tool_name == "full_pipeline":
                        result = full_pipeline(arguments["topic"], arguments["idea"], arguments.get("project_dir", "."))
                    else:
                        send_error(req_id, -32601, f"Unknown tool: {tool_name}")
                        continue
                    
                    send_response(req_id, {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]
                    })
                
                except Exception as e:
                    send_error(req_id, -32000, str(e))
            
            elif method == "ping":
                send_response(req_id, {})
            
            elif req_id is not None:
                send_error(req_id, -32601, f"Unknown method: {method}")
    
    else:
        # CLI mode
        print("""
VinnyOS Engine — Unified MCP Server
====================================

Usage: python mcp_server.py mcp    # Run as MCP server
       python mcp_server.py cli    # Run in CLI mode

13 Layers:
  1. EXPLORE     - Query explosion
  2. HARVEST     - Multi-shelf search
  3. DECOMPOSE   - Parts extraction
  4. SYNTHESIZE  - Idea matching
  5. DISCOVER    - GitHub layer search
  6. ANALYZE     - Repo structure analysis
  7. EXTRACT     - Code extraction
  8. ISOLATE     - Safe wrappers
  9. VALIDATE    - Import testing
  10. INTEGRATE  - Project wiring
  11. SELF-HEAL  - Detect breaks, find fixes
  12. DREAM      - Consolidate during idle
  13. GRAPH      - Knowledge graph queries
        """)
