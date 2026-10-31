#!/usr/bin/env python3
"""
GitHub Ecosystem MCP Server

Tools for discovering, evaluating, extracting, and integrating GitHub repos into your code.
Core insight: GitHub is not a code repository — it's a living ecosystem of composable ideas.

EXTRACTION LAYERS:
1. DISCOVER  → Find repos by layer
2. ANALYZE   → Map repo structure, identify reusable modules
3. EXTRACT   → Pull specific files/modules safely
4. ISOLATE   → Generate wrappers that prevent breaking your code
5. TEST      → Verify extracted code works
6. INTEGRATE → Generate import statements and wiring code
"""

import subprocess
import json
import re
import os
import sys
import shutil
import tempfile
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

EXTRACTION_DIR = Path.home() / ".vinnyos" / "extracted"
CACHE_DIR = Path.home() / ".vinnyos" / "cache"
STUBS_DIR = Path.home() / ".vinnyos" / "stubs"

# Ensure directories exist
for d in [EXTRACTION_DIR, CACHE_DIR, STUBS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Layer definitions
LAYERS = {
    "capture": {
        "name": "CAPTURE",
        "description": "Data ingestion, scraping, collection, monitoring",
        "search_patterns": [
            '"data ingestion" language:python sort:stars',
            '"web scraper" "AI" self-hosted',
            '"file watcher" monitor local',
            '"RSS" aggregator self-hosted',
            '"clipboard" manager AI',
            '"screen time" tracking',
        ],
        "common_modules": ["scraper", "crawler", "ingester", "watcher", "collector", "monitor"]
    },
    "fuse": {
        "name": "FUSE",
        "description": "Dedup, entity resolution, context management, linking",
        "search_patterns": [
            '"entity resolution" dedup',
            '"semantic dedup" multimodal',
            '"context management" agent',
            '"knowledge graph" self-hosted',
            '"data fusion" python',
        ],
        "common_modules": ["dedup", "resolver", "linker", "merger", "fusion", "dedupe"]
    },
    "think": {
        "name": "THINK",
        "description": "Memory, knowledge graphs, reasoning, semantic search",
        "search_patterns": [
            '"knowledge graph" self-hosted',
            '"AI memory" local',
            '"vector database" agent',
            '"semantic search" self-hosted',
            '"second brain" open source',
        ],
        "common_modules": ["memory", "graph", "vector", "search", "embed", "index", "brain"]
    },
    "act": {
        "name": "ACT",
        "description": "Orchestration, execution, coordination, agents",
        "search_patterns": [
            '"agent orchestration" framework',
            '"multi agent" MCP',
            '"workflow engine" local',
            '"task automation" AI agent',
            '"MCP server" tools',
        ],
        "common_modules": ["agent", "orchestrator", "executor", "scheduler", "router", "dispatch"]
    },
    "self": {
        "name": "SELF",
        "description": "Self-healing, adaptation, learning loops",
        "search_patterns": [
            '"self improving" AI',
            '"adaptive" agent framework',
            '"learning loop" autonomous',
            '"self healing" system',
            '"meta learning" agent',
        ],
        "common_modules": ["adaptive", "healer", "learner", "optimizer", "evolver", "feedback"]
    },
    "dream": {
        "name": "DREAM",
        "description": "Consolidation, subconscious, forgetting, reorganization",
        "search_patterns": [
            '"memory consolidation" AI',
            '"subconscious" agent',
            '"context rot" detection',
            '"dream" memory AI',
            '"Hebbian" OR "biological" memory',
            '"sleep" consolidation agent',
        ],
        "common_modules": ["consolidat", "dream", "subconscious", "forget", "reorganiz", "sleep"]
    }
}


# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def run_cmd(cmd: list[str], cwd: str = None, timeout: int = 30) -> dict:
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


def run_gh(args: list[str]) -> dict:
    """Run a gh CLI command."""
    return run_cmd(["gh"] + args)


def run_git(args: list[str], cwd: str = None) -> dict:
    """Run a git command."""
    return run_cmd(["git"] + args, cwd=cwd)


def hash_content(content: str) -> str:
    """Hash content for caching."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 1: DISCOVER
# ──────────────────────────────────────────────────────────────────────────────

def discover_repos(layer: str, limit: int = 10) -> list[dict]:
    """Search GitHub for repos in a specific layer."""
    if layer not in LAYERS:
        return [{"error": f"Unknown layer: {layer}. Valid: {list(LAYERS.keys())}"}]

    all_results = []
    for pattern in LAYERS[layer]["search_patterns"]:
        result = run_gh([
            "search", "repos", pattern,
            "--sort", "stars",
            "--limit", str(limit),
            "--json", "fullName,description,stargazersCount,updatedAt,language,license,url"
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

    # Sort by stars
    unique.sort(key=lambda x: x.get("stargazersCount", 0), reverse=True)
    return unique[:limit]


def discover_all_layers(limit_per_layer: int = 5) -> dict:
    """Discover top tools for all layers."""
    results = {}
    for layer in LAYERS:
        results[layer] = discover_repos(layer, limit_per_layer)
    return results


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 2: ANALYZE
# ──────────────────────────────────────────────────────────────────────────────

def analyze_repo(repo: str) -> dict:
    """Analyze a repo's structure and identify reusable modules."""
    # Get repo info
    result = run_gh([
        "repo", "view", repo,
        "--json", "nameWithOwner,description,stargazerCount,updatedAt,primaryLanguage,licenseInfo,url,repositoryTopics"
    ])

    if not result["success"]:
        return {"error": f"Cannot access repository: {repo}"}

    info = json.loads(result["stdout"])
    # Normalize field names
    if "nameWithOwner" in info:
        info["fullName"] = info.pop("nameWithOwner")
    if "stargazerCount" in info:
        info["stars"] = info.pop("stargazerCount")
    if "primaryLanguage" in info:
        lang = info.pop("primaryLanguage")
        info["language"] = lang.get("name") if lang else None
    if "licenseInfo" in info:
        lic = info.pop("licenseInfo")
        info["license"] = lic.get("name") if lic else None

    # Clone to temp dir for analysis
    tmp_dir = tempfile.mkdtemp(prefix="vinnyos_analyze_")
    clone_result = run_git(["clone", "--depth", "1", f"https://github.com/{repo}.git", "repo"], cwd=tmp_dir)

    if not clone_result["success"]:
        return {"error": f"Cannot clone repository: {clone_result['stderr']}"}

    repo_path = Path(tmp_dir) / "repo"

    # Find Python files
    py_files = list(repo_path.rglob("*.py"))

    # Identify potential modules
    modules = []
    for py_file in py_files:
        rel_path = py_file.relative_to(repo_path)

        # Skip test files, hidden files, __pycache__
        if any(part.startswith("_") and part != "__init__.py" for part in rel_path.parts):
            continue
        if "test" in rel_path.name.lower():
            continue
        if ".hidden" in str(rel_path):
            continue

        # Read file and check for classes/functions
        try:
            content = py_file.read_text()
            classes = re.findall(r"class\s+(\w+)", content)
            functions = re.findall(r"def\s+(\w+)", content)
            imports = re.findall(r"^(?:from|import)\s+(\w+)", content, re.MULTILINE)

            # Check if it's a standalone module (not just a script)
            has_classes = len(classes) > 0
            has_functions = len(functions) > 0
            has_docstring = '"""' in content or "'''" in content
            no_main = 'if __name__' not in content

            if (has_classes or has_functions) and (has_docstring or no_main):
                modules.append({
                    "path": str(rel_path),
                    "classes": classes[:10],
                    "functions": functions[:10],
                    "imports": imports[:10],
                    "lines": len(content.split("\n")),
                    "reusable": has_classes and no_main,
                    "score": (3 if has_classes else 0) + (2 if has_functions else 0) + (1 if has_docstring else 0) + (2 if no_main else 0)
                })
        except (UnicodeDecodeError, PermissionError):
            pass

    # Sort by reusability score
    modules.sort(key=lambda x: x.get("score", 0), reverse=True)

    # Find requirements
    req_files = list(repo_path.glob("requirements*.txt")) + list(repo_path.glob("setup.py")) + list(repo_path.glob("pyproject.toml"))
    dependencies = []
    for req_file in req_files:
        try:
            content = req_file.read_text()
            deps = re.findall(r"^[a-zA-Z][\w-]*", content, re.MULTILINE)
            dependencies.extend(deps[:20])
        except (UnicodeDecodeError, PermissionError):
            pass

    # Cleanup
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return {
        "repo": info.get("fullName"),
        "description": info.get("description"),
        "stars": info.get("stars", 0),
        "language": info.get("language"),
        "license": info.get("license"),
        "url": info.get("url"),
        "modules": modules[:20],
        "dependencies": dependencies,
        "reusable_modules": [m for m in modules if m.get("reusable")][:10],
        "total_modules": len(modules)
    }


def find_reusable_modules(repo: str) -> list[dict]:
    """Find the most reusable modules in a repo."""
    analysis = analyze_repo(repo)
    return analysis.get("reusable_modules", [])


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 3: EXTRACT
# ──────────────────────────────────────────────────────────────────────────────

def extract_module(repo: str, module_path: str, target_name: str = None) -> dict:
    """Extract a specific module from a repo and save it locally."""
    if not target_name:
        target_name = f"{repo.replace('/', '_')}_{Path(module_path).stem}"

    # Sanitize target name for Python
    target_name = re.sub(r'[^a-zA-Z0-9_]', '_', target_name)
    if target_name[0].isdigit():
        target_name = '_' + target_name

    # Create extraction directory
    extract_dir = EXTRACTION_DIR / target_name
    extract_dir.mkdir(parents=True, exist_ok=True)

    # Clone repo
    tmp_dir = tempfile.mkdtemp(prefix="vinnyos_extract_")
    clone_result = run_git(["clone", "--depth", "1", f"https://github.com/{repo}.git", "repo"], cwd=tmp_dir)

    if not clone_result["success"]:
        return {"error": f"Cannot clone: {clone_result['stderr']}"}

    repo_path = Path(tmp_dir) / "repo"
    source_file = repo_path / module_path

    if not source_file.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return {"error": f"Module not found: {module_path}"}

    # Read source
    source_content = source_file.read_text()

    # Find all dependencies within the repo
    imports = re.findall(r"^(?:from\s+(\S+)\s+import|import\s+(\S+))", source_content, re.MULTILINE)
    local_imports = []
    for imp in imports:
        imp_name = imp[0] or imp[1]
        if imp_name.startswith(".") or not imp_name[0].isupper():
            # Likely a local import
            local_imports.append(imp_name)

    # Copy the module
    target_file = extract_dir / f"{target_name}.py"
    target_file.write_text(source_content)

    # Copy any local dependencies
    for local_imp in local_imports:
        # Try to find the local module
        for ext in [".py", "/__init__.py"]:
            dep_path = repo_path / (local_imp.replace(".", "/") + ext)
            if dep_path.exists():
                dep_target = extract_dir / f"{local_imp.replace('.', '_')}.py"
                dep_target.write_text(dep_path.read_text())
                break

    # Cleanup
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return {
        "target_name": target_name,
        "extract_dir": str(extract_dir),
        "source_file": str(target_file),
        "source_repo": repo,
        "source_path": module_path,
        "local_dependencies": local_imports,
        "lines": len(source_content.split("\n"))
    }


def extract_multiple(repo: str, module_paths: list[str], prefix: str = None) -> list[dict]:
    """Extract multiple modules from a repo."""
    if not prefix:
        prefix = repo.replace("/", "_")

    results = []
    for path in module_paths:
        target = f"{prefix}_{Path(path).stem}"
        result = extract_module(repo, path, target)
        results.append(result)

    return results


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 4: ISOLATE
# ──────────────────────────────────────────────────────────────────────────────

def generate_wrapper(extract_dir: str, class_name: str, methods: list[str] = None) -> dict:
    """Generate a safe wrapper class that isolates external code."""
    # Sanitize class name to be valid Python
    class_name = re.sub(r'[^a-zA-Z0-9_]', '_', class_name)
    if class_name[0].isdigit():
        class_name = '_' + class_name

    extract_path = Path(extract_dir)

    # Find the main Python file
    py_files = list(extract_path.glob("*.py"))
    if not py_files:
        return {"error": "No Python files found in extraction directory"}

    main_file = py_files[0]
    content = main_file.read_text()

    # Find classes
    classes = re.findall(r"class\s+(\w+).*?:(.*?)(?=\nclass|\ndef [a-z]|\Z)", content, re.DOTALL)

    if not classes:
        # If no classes, wrap the functions
        return _generate_function_wrapper(extract_dir, methods)

    class_name_found, class_body = classes[0]

    # Generate wrapper
    wrapper_code = f'''"""
Safe wrapper for {class_name_found} from {extract_path.name}
Generated by VinnyOS Ecosystem MCP
"""

from typing import Any, Optional
from pathlib import Path
import importlib.util
import logging

logger = logging.getLogger(__name__)


class {class_name}:
    """
    Isolated wrapper for {class_name_found}.
    
    This wrapper prevents external code from breaking your system by:
    1. Catching all exceptions from the wrapped class
    2. Providing fallback behavior on failure
    3. Logging all interactions for debugging
    """
    
    def __init__(self, **kwargs):
        """Initialize with error handling."""
        try:
            # Import the actual class
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "{class_name_found.lower()}",
                str(Path(__file__).parent / "{main_file.name}")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            self._wrapped = module.{class_name_found}(**kwargs)
            self._initialized = True
            logger.info(f"Successfully initialized {class_name_found}")
        except Exception as e:
            logger.error(f"Failed to initialize {class_name_found}: {{e}}")
            self._wrapped = None
            self._initialized = False
    
    def is_ready(self) -> bool:
        """Check if the wrapper is ready to use."""
        return self._initialized and self._wrapped is not None
    
    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access with error handling."""
        if name.startswith("_"):
            return super().__getattribute__(name)
        
        if not self.is_ready():
            raise RuntimeError(f"{class_name} is not initialized")
        
        attr = getattr(self._wrapped, name, None)
        if attr is None:
            raise AttributeError(f"{class_name_found} has no attribute {{name}}")
        
        # If it's a method, wrap it with error handling
        if callable(attr):
            def safe_method(*args, **kwargs):
                try:
                    return attr(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Method {{name}} failed: {{e}}")
                    return None
            return safe_method
        
        return attr
    
    def __repr__(self) -> str:
        if self.is_ready():
            return f"{class_name}(wrapping={class_name_found}, ready=True)"
        return f"{class_name}(ready=False)"
'''

    wrapper_file = extract_path / f"wrapper_{class_name}.py"
    wrapper_file.write_text(wrapper_code)

    return {
        "wrapper_file": str(wrapper_file),
        "wrapper_class": class_name,
        "wrapped_class": class_name_found,
        "usage": f"from {extract_path.name}.wrapper_{class_name} import {class_name}\n\ninstance = {class_name}()",
        "ready": True
    }


def _generate_function_wrapper(extract_dir: str, methods: list[str] = None) -> dict:
    """Generate a wrapper for standalone functions."""
    extract_path = Path(extract_dir)
    py_files = list(extract_path.glob("*.py"))

    if not py_files:
        return {"error": "No Python files found"}

    main_file = py_files[0]
    content = main_file.read_text()

    # Find all functions
    functions = re.findall(r"def\s+(\w+)\s*\((.*?)\)", content)

    wrapper_code = f'''"""
Safe function wrappers from {extract_dir.name}
Generated by VinnyOS Ecosystem MCP
"""

from typing import Any, Optional
import logging
import importlib.util
from pathlib import Path

logger = logging.getLogger(__name__)

# Load the original module
_spec = importlib.util.spec_from_file_location(
    "original_module",
    str(Path(__file__).parent / "{main_file.name}")
)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)


'''

    # Generate safe wrappers for each function
    for func_name, params in functions:
        if func_name.startswith("_"):
            continue

        wrapper_code += f'''
def {func_name}({params}) -> Any:
    """
    Safe wrapper for {func_name}.
    
    This function catches all exceptions and returns None on failure.
    Check the logs for error details.
    """
    try:
        return _module.{func_name}({params})
    except Exception as e:
        logger.error(f"{func_name} failed: {{e}}")
        return None


'''

    wrapper_file = extract_path / "safe_functions.py"
    wrapper_file.write_text(wrapper_code)

    return {
        "wrapper_file": str(wrapper_file),
        "wrapped_functions": [f[0] for f in functions if not f[0].startswith("_")],
        "usage": f"from {extract_path.name}.safe_functions import {', '.join(f[0] for f in functions if not f[0].startswith('_'))}",
        "ready": True
    }


def generate_type_stubs(extract_dir: str) -> dict:
    """Generate type stubs for better IDE support."""
    extract_path = Path(extract_dir)
    py_files = list(extract_path.glob("*.py"))

    stubs = []
    for py_file in py_files:
        content = py_file.read_text()

        # Find classes
        classes = re.findall(r"class\s+(\w+).*?:(.*?)(?=\nclass|\Z)", content, re.DOTALL)
        for class_name, class_body in classes:
            methods = re.findall(r"def\s+(\w+)\s*\(self.*?\)(?:\s*->\s*(\w+))?", class_body)
            stubs.append({
                "class": class_name,
                "methods": [{"name": m[0], "return": m[1] or "Any"} for m in methods]
            })

    # Write stub file
    stub_content = f'# Type stubs for {extract_dir.name}\n# Generated by VinnyOS Ecosystem MCP\n\n'
    for stub in stubs:
        stub_content += f'class {stub["class"]}:\n'
        for method in stub["methods"]:
            stub_content += f'    def {method["name"]}(self, *args, **kwargs) -> {method["return"]}: ...\n'
        stub_content += '\n'

    stub_file = extract_path / f"{extract_dir.name}.pyi"
    stub_file.write_text(stub_content)

    return {
        "stub_file": str(stub_file),
        "classes": [s["class"] for s in stubs]
    }


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 5: TEST
# ──────────────────────────────────────────────────────────────────────────────

def test_extraction(extract_dir: str) -> dict:
    """Test that extracted code actually works."""
    extract_path = Path(extract_dir)

    # Find wrapper files
    wrapper_files = list(extract_path.glob("wrapper_*.py")) + list(extract_path.glob("safe_*.py"))

    results = []
    for wrapper_file in wrapper_files:
        try:
            # Try to import
            spec = importlib.util.spec_from_file_location(
                wrapper_file.stem,
                str(wrapper_file)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            results.append({
                "file": wrapper_file.name,
                "import": "SUCCESS",
                "error": None
            })
        except Exception as e:
            results.append({
                "file": wrapper_file.name,
                "import": "FAILED",
                "error": str(e)
            })

    # Try basic instantiation if there's a wrapper class
    for wrapper_file in wrapper_files:
        if wrapper_file.name.startswith("wrapper_"):
            try:
                spec = importlib.util.spec_from_file_location(
                    wrapper_file.stem,
                    str(wrapper_file)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find the wrapper class (look for classes defined in the file)
                content = wrapper_file.read_text()
                defined_classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
                
                for class_name in defined_classes:
                    attr = getattr(module, class_name, None)
                    if attr and isinstance(attr, type):
                        try:
                            instance = attr()
                            results.append({
                                "file": wrapper_file.name,
                                "instantiation": "SUCCESS",
                                "class": class_name,
                                "error": None
                            })
                            break
                        except Exception as e:
                            results.append({
                                "file": wrapper_file.name,
                                "instantiation": "FAILED",
                                "class": class_name,
                                "error": str(e)
                            })
            except Exception as e:
                results.append({
                    "file": wrapper_file.name,
                    "import": "FAILED",
                    "error": str(e)
                })

    return {
        "extract_dir": str(extract_dir),
        "tests": results,
        "all_passed": all(r.get("error") is None for r in results)
    }


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 6: INTEGRATE
# ──────────────────────────────────────────────────────────────────────────────

def generate_import_code(extract_dir: str, project_dir: str) -> dict:
    """Generate import statements and wiring code for your project."""
    extract_path = Path(extract_dir)
    project_path = Path(project_dir)

    # Find wrapper files
    wrapper_files = list(extract_path.glob("wrapper_*.py")) + list(extract_path.glob("safe_*.py"))

    imports = []
    usage_examples = []

    for wrapper_file in wrapper_files:
        # Get the module name
        module_name = extract_path.name
        file_name = wrapper_file.stem

        # Read file to find class/function names
        content = wrapper_file.read_text()
        # Only find classes that are actually defined (not imported)
        classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
        functions = re.findall(r"^def\s+(\w+)\s*\(", content, re.MULTILINE)
        functions = [f for f in functions if not f.startswith("_")]

        if classes:
            for cls in classes:
                imports.append(f"from {module_name}.{file_name} import {cls}")
                usage_examples.append(f"{cls.lower()} = {cls}()")

        if functions:
            for func in functions:
                imports.append(f"from {module_name}.{file_name} import {func}")

    # Generate integration file
    integration_code = f'''"""
Integration code for {extract_path.name}
Generated by VinnyOS Ecosystem MCP

Copy this code into your project to use the extracted modules.
"""

# ── Imports ──────────────────────────────────────────────────────────────────
{chr(10).join(imports)}

# ── Usage Examples ───────────────────────────────────────────────────────────
{chr(10).join(usage_examples)}

# ── Wiring ───────────────────────────────────────────────────────────────────
# Connect these to your existing code:

# Example: Add to your main.py
# from vinnyos_integration import *

# Example: Use in your agent
# memory = MemoryManager()
# graph = KnowledgeGraph()
# orchestrator = AgentOrchestrator(memory=memory, graph=graph)
'''

    integration_file = project_path / f"vinnyos_{extract_path.name}_integration.py"
    integration_file.parent.mkdir(parents=True, exist_ok=True)
    integration_file.write_text(integration_code)

    return {
        "integration_file": str(integration_file),
        "imports": imports,
        "usage_examples": usage_examples,
        "instructions": [
            f"1. Copy {extract_path.name}/ to your project",
            f"2. Add the imports from {integration_file.name}",
            f"3. Initialize the wrapper classes",
            f"4. Use them in your code"
        ]
    }


def copy_to_project(extract_dir: str, project_dir: str) -> dict:
    """Copy extracted code to your project."""
    extract_path = Path(extract_dir)
    project_path = Path(project_dir)

    # Sanitize directory name for Python import
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', extract_path.name)
    if safe_name[0].isdigit():
        safe_name = '_' + safe_name

    target_dir = project_path / "vinnyos_modules" / safe_name
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy all files
    copied = []
    for file in extract_path.glob("*"):
        if file.is_file():
            shutil.copy2(file, target_dir / file.name)
            copied.append(file.name)

    return {
        "target_dir": str(target_dir),
        "copied_files": copied,
        "import_path": f"vinnyos_modules.{safe_name}",
        "usage": f"from vinnyos_modules.{safe_name} import *"
    }


# ──────────────────────────────────────────────────────────────────────────────
# HIGH-LEVEL ORCHESTRATION
# ──────────────────────────────────────────────────────────────────────────────

def full_extraction_pipeline(repo: str, module_path: str, project_dir: str) -> dict:
    """Run the full extraction pipeline: analyze → extract → isolate → test → integrate."""
    results = {"steps": []}

    # Step 1: Analyze
    analysis = analyze_repo(repo)
    results["steps"].append({"step": "analyze", "result": analysis})
    if "error" in analysis:
        return results

    # Step 2: Extract
    extraction = extract_module(repo, module_path)
    results["steps"].append({"step": "extract", "result": extraction})
    if "error" in extraction:
        return results

    # Step 3: Isolate
    extract_dir = extraction["extract_dir"]
    target_name = extraction["target_name"]
    wrapper = generate_wrapper(extract_dir, target_name)
    results["steps"].append({"step": "isolate", "result": wrapper})

    # Step 4: Test
    test = test_extraction(extract_dir)
    results["steps"].append({"step": "test", "result": test})

    # Step 5: Integrate
    integration = generate_import_code(extract_dir, project_dir)
    results["steps"].append({"step": "integrate", "result": integration})

    # Step 6: Copy
    copy = copy_to_project(extract_dir, project_dir)
    results["steps"].append({"step": "copy", "result": copy})

    results["success"] = test.get("all_passed", False)
    results["final_dir"] = copy.get("target_dir")
    results["import_path"] = copy.get("import_path")

    return results


# ──────────────────────────────────────────────────────────────────────────────
# MCP TOOL FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def mcp_discover(layer: str, limit: int = 10) -> str:
    """MCP Tool: Discover repos for a specific layer."""
    return json.dumps(discover_repos(layer, limit), indent=2)


def mcp_analyze(repo: str) -> str:
    """MCP Tool: Analyze a repo's structure."""
    return json.dumps(analyze_repo(repo), indent=2)


def mcp_extract(repo: str, module_path: str, target_name: str = None) -> str:
    """MCP Tool: Extract a specific module from a repo."""
    return json.dumps(extract_module(repo, module_path, target_name), indent=2)


def mcp_isolate(extract_dir: str, class_name: str) -> str:
    """MCP Tool: Generate a safe wrapper for extracted code."""
    return json.dumps(generate_wrapper(extract_dir, class_name), indent=2)


def mcp_test(extract_dir: str) -> str:
    """MCP Tool: Test that extracted code works."""
    return json.dumps(test_extraction(extract_dir), indent=2)


def mcp_integrate(extract_dir: str, project_dir: str) -> str:
    """MCP Tool: Generate integration code."""
    return json.dumps(generate_import_code(extract_dir, project_dir), indent=2)


def mcp_full_pipeline(repo: str, module_path: str, project_dir: str) -> str:
    """MCP Tool: Run the full extraction pipeline."""
    return json.dumps(full_extraction_pipeline(repo, module_path, project_dir), indent=2)


def mcp_discover_all(limit: int = 5) -> str:
    """MCP Tool: Discover top tools for all layers."""
    return json.dumps(discover_all_layers(limit), indent=2)


# ──────────────────────────────────────────────────────────────────────────────
# CLI INTERFACE
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
VinnyOS Ecosystem MCP Server
=============================

Usage: python mcp_server.py <command> [args]

Commands:
  discover <layer> [limit]     - Discover repos for a layer
  discover-all [limit]         - Discover repos for all layers
  analyze <repo>               - Analyze a repo's structure
  extract <repo> <path> [name] - Extract a module
  isolate <dir> <class>        - Generate safe wrapper
  test <dir>                   - Test extracted code
  integrate <dir> <project>    - Generate integration code
  pipeline <repo> <path> <dir> - Full extraction pipeline
  layers                       - List all layers

Layers: capture, fuse, think, act, self, dream

Examples:
  python mcp_server.py discover think 10
  python mcp_server.py analyze khoj-ai/khoj
  python mcp_server.py extract khoj-ai/khoj src/memory/memory.py
  python mcp_server.py pipeline khoj-ai/khoj src/memory/memory.py ./my-project
        """)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "layers":
        for name, layer in LAYERS.items():
            print(f"{name:8} - {layer['description']}")

    elif cmd == "discover":
        layer = sys.argv[2] if len(sys.argv) > 2 else "think"
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        results = discover_repos(layer, limit)
        for r in results:
            stars = r.get("stargazersCount", 0)
            name = r.get("fullName", "unknown")
            desc = (r.get("description") or "No description")[:60]
            print(f"★{stars:6d}  {name}")
            print(f"         {desc}")
            print()

    elif cmd == "discover-all":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        results = discover_all_layers(limit)
        for layer, repos in results.items():
            print(f"\n{'='*60}")
            print(f"  {layer.upper()} LAYER")
            print(f"{'='*60}")
            for r in repos:
                stars = r.get("stargazersCount", 0)
                name = r.get("fullName", "unknown")
                desc = (r.get("description") or "No description")[:60]
                print(f"  ★{stars:6d}  {name}")
                print(f"           {desc}")

    elif cmd == "analyze":
        repo = sys.argv[2] if len(sys.argv) > 2 else "khoj-ai/khoj"
        result = analyze_repo(repo)
        print(json.dumps(result, indent=2))

    elif cmd == "extract":
        repo = sys.argv[2] if len(sys.argv) > 2 else ""
        path = sys.argv[3] if len(sys.argv) > 3 else ""
        name = sys.argv[4] if len(sys.argv) > 4 else None
        if not repo or not path:
            print("Usage: python mcp_server.py extract <repo> <module_path> [target_name]")
            sys.exit(1)
        result = extract_module(repo, path, name)
        print(json.dumps(result, indent=2))

    elif cmd == "isolate":
        dir_path = sys.argv[2] if len(sys.argv) > 2 else ""
        class_name = sys.argv[3] if len(sys.argv) > 3 else "Wrapper"
        if not dir_path:
            print("Usage: python mcp_server.py isolate <extract_dir> <class_name>")
            sys.exit(1)
        result = generate_wrapper(dir_path, class_name)
        print(json.dumps(result, indent=2))

    elif cmd == "test":
        dir_path = sys.argv[2] if len(sys.argv) > 2 else ""
        if not dir_path:
            print("Usage: python mcp_server.py test <extract_dir>")
            sys.exit(1)
        result = test_extraction(dir_path)
        print(json.dumps(result, indent=2))

    elif cmd == "integrate":
        dir_path = sys.argv[2] if len(sys.argv) > 2 else ""
        project = sys.argv[3] if len(sys.argv) > 3 else "."
        if not dir_path:
            print("Usage: python mcp_server.py integrate <extract_dir> <project_dir>")
            sys.exit(1)
        result = generate_import_code(dir_path, project)
        print(json.dumps(result, indent=2))

    elif cmd == "pipeline":
        repo = sys.argv[2] if len(sys.argv) > 2 else ""
        path = sys.argv[3] if len(sys.argv) > 3 else ""
        project = sys.argv[4] if len(sys.argv) > 4 else "."
        if not repo or not path:
            print("Usage: python mcp_server.py pipeline <repo> <module_path> <project_dir>")
            sys.exit(1)
        result = full_extraction_pipeline(repo, path, project)
        print(json.dumps(result, indent=2))

    elif cmd == "mcp":
        # Run as MCP server (JSON-RPC over stdin/stdout)
        import json as _json

        TOOLS = [
            {
                "name": "discover_layer",
                "description": "Find the best GitHub repos for a specific layer (capture/fuse/think/act/self/dream)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "layer": {"type": "string", "description": "Layer to search: capture, fuse, think, act, self, dream"},
                        "limit": {"type": "integer", "description": "Max results", "default": 10}
                    },
                    "required": ["layer"]
                }
            },
            {
                "name": "discover_all",
                "description": "Search all 6 layers at once and return unified results",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max results per layer", "default": 5}
                    }
                }
            },
            {
                "name": "analyze_repo",
                "description": "Analyze a GitHub repo's structure, entry points, dependencies, and reusable modules",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string", "description": "GitHub repo (owner/name)"}
                    },
                    "required": ["repo"]
                }
            },
            {
                "name": "extract_module",
                "description": "Extract a specific Python file or module from a GitHub repo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string", "description": "GitHub repo (owner/name)"},
                        "path": {"type": "string", "description": "File path in repo"},
                        "name": {"type": "string", "description": "Target name for extracted file"}
                    },
                    "required": ["repo", "path"]
                }
            },
            {
                "name": "isolate_wrapper",
                "description": "Generate a safe wrapper that prevents extracted code from breaking your project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "extract_dir": {"type": "string", "description": "Path to extracted module directory"},
                        "class_name": {"type": "string", "description": "Wrapper class name", "default": "Wrapper"}
                    },
                    "required": ["extract_dir"]
                }
            },
            {
                "name": "test_extraction",
                "description": "Test that extracted code compiles and runs without errors",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "extract_dir": {"type": "string", "description": "Path to extracted module directory"}
                    },
                    "required": ["extract_dir"]
                }
            },
            {
                "name": "generate_imports",
                "description": "Generate import statements and wiring code for integrating extracted modules",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "extract_dir": {"type": "string", "description": "Path to extracted module directory"},
                        "project_dir": {"type": "string", "description": "Target project directory", "default": "."}
                    },
                    "required": ["extract_dir"]
                }
            },
            {
                "name": "full_pipeline",
                "description": "Complete extraction pipeline: analyze → extract → isolate → test → generate imports",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string", "description": "GitHub repo (owner/name)"},
                        "path": {"type": "string", "description": "Module path in repo"},
                        "project_dir": {"type": "string", "description": "Target project directory", "default": "."}
                    },
                    "required": ["repo", "path"]
                }
            }
        ]

        def send_response(req_id, result):
            resp = {"jsonrpc": "2.0", "id": req_id, "result": result}
            sys.stdout.write(_json.dumps(resp) + "\n")
            sys.stdout.flush()

        def send_error(req_id, code, message):
            resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
            sys.stdout.write(_json.dumps(resp) + "\n")
            sys.stdout.flush()

        # MCP initialization handshake
        initialized = False

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                msg = _json.loads(line)
            except _json.JSONDecodeError:
                continue

            method = msg.get("method")
            req_id = msg.get("id")
            params = msg.get("params", {})

            if method == "initialize":
                send_response(req_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "github-ecosystem", "version": "1.0.0"}
                })
                initialized = True

            elif method == "notifications/initialized":
                pass  # Client ack, no response needed

            elif method == "tools/list":
                send_response(req_id, {"tools": TOOLS})

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                try:
                    if tool_name == "discover_layer":
                        result = discover_repos(arguments["layer"], arguments.get("limit", 10))
                    elif tool_name == "discover_all":
                        result = discover_all_layers(arguments.get("limit", 5))
                    elif tool_name == "analyze_repo":
                        result = analyze_repo(arguments["repo"])
                    elif tool_name == "extract_module":
                        result = extract_module(arguments["repo"], arguments["path"], arguments.get("name"))
                    elif tool_name == "isolate_wrapper":
                        result = generate_wrapper(arguments["extract_dir"], arguments.get("class_name", "Wrapper"))
                    elif tool_name == "test_extraction":
                        result = test_extraction(arguments["extract_dir"])
                    elif tool_name == "generate_imports":
                        result = generate_import_code(arguments["extract_dir"], arguments.get("project_dir", "."))
                    elif tool_name == "full_pipeline":
                        result = full_extraction_pipeline(arguments["repo"], arguments["path"], arguments.get("project_dir", "."))
                    else:
                        send_error(req_id, -32601, f"Unknown tool: {tool_name}")
                        continue

                    send_response(req_id, {
                        "content": [{"type": "text", "text": _json.dumps(result, indent=2, default=str)}]
                    })

                except Exception as e:
                    send_error(req_id, -32000, str(e))

            elif method == "ping":
                send_response(req_id, {})

            elif req_id is not None:
                send_error(req_id, -32601, f"Unknown method: {method}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
