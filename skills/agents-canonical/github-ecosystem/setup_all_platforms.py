#!/usr/bin/env python3
"""
Setup GitHub Ecosystem MCP server for all platforms.
Run once, use everywhere.
"""

import json
import os
from pathlib import Path

SERVER_CONFIG = {
    "command": "python3",
    "args": [str(Path.home() / ".claude/skills/github-ecosystem/mcp_server.py")],
    "cwd": str(Path.home() / ".claude/skills/github-ecosystem"),
    "env": {},
    "type": "stdio"
}

PLATFORMS = {
    "Claude Code": {
        "config_path": Path.home() / ".claude.json",
        "key": "mcpServers",
        "server_name": "github-ecosystem"
    },
    "Claude Desktop": {
        "config_path": Path.home() / "Library/Application Support/Claude/claude_desktop_config.json",
        "key": "mcpServers",
        "server_name": "github-ecosystem"
    },
    "Cursor": {
        "config_path": Path.home() / ".cursor/mcp.json",
        "key": "mcpServers",
        "server_name": "github-ecosystem"
    },
    "Windsurf": {
        "config_path": Path.home() / ".codeium/windsurf/mcp_config.json",
        "key": "mcpServers",
        "server_name": "github-ecosystem"
    },
    "opencode": {
        "config_path": Path.home() / ".config/opencode/opencode.json",
        "key": "mcp",
        "server_name": "github-ecosystem",
        "alt_format": True  # opencode uses different format
    },
    "Kilo Code": {
        "config_path": Path.home() / ".config/kilo/kilo.jsonc",
        "key": "mcp",
        "server_name": "github-ecosystem",
        "alt_format": True
    },
    "Hermes": {
        "config_path": Path.home() / ".hermes" / "config.yaml",
        "key": "mcp_servers",
        "server_name": "github-ecosystem",
        "yaml_format": True
    },
    "Grok": {
        "config_path": Path.home() / ".grok" / "config.toml",
        "key": "mcp_servers",
        "server_name": "github-ecosystem",
        "toml_format": True
    }
}


def setup_platform(name: str, config: dict) -> dict:
    """Setup MCP server for a single platform."""
    result = {"platform": name, "status": "skipped", "reason": ""}

    config_path = config["config_path"]

    # Check if config file exists
    if not config_path.exists():
        result["status"] = "skipped"
        result["reason"] = f"Config file not found: {config_path}"
        return result

    # Read existing config
    try:
        if config.get("toml_format"):
            # TOML files can't be reliably modified by a generic script
            # Just report what needs to be added
            result["status"] = "manual"
            result["reason"] = f"Add to {config_path}:\n[mcp_servers.{config['server_name']}]\ncommand = \"python3\"\nargs = [\"{Path.home()}/.claude/skills/github-ecosystem/mcp_server.py\", \"mcp\"]\nenabled = true"
            return result
        elif config.get("yaml_format"):
            # YAML files can't be reliably modified by a generic script
            result["status"] = "manual"
            result["reason"] = f"Add to {config_path}:\n{config['server_name']}:\n  command: python3\n  args:\n  - {Path.home()}/.claude/skills/github-ecosystem/mcp_server.py\n  - mcp\n  enabled: true"
            return result
        else:
            with open(config_path, "r") as f:
                existing = json.load(f)
    except (json.JSONDecodeError, PermissionError) as e:
        result["status"] = "error"
        result["reason"] = f"Could not read config: {e}"
        return result

    # Get the right key
    key = config["key"]
    server_name = config["server_name"]

    if key not in existing:
        existing[key] = {}

    # Check if already configured
    if server_name in existing[key]:
        result["status"] = "already_configured"
        result["reason"] = f"Server '{server_name}' already exists in config"
        return result

    # Add server config
    if config.get("alt_format"):
        # opencode/Kilo format
        server_config = {
            "type": "local",
            "command": ["python3", SERVER_CONFIG["args"][0]],
            "enabled": True
        }
    else:
        # Standard format
        server_config = SERVER_CONFIG.copy()

    existing[key][server_name] = server_config

    # Write back
    try:
        with open(config_path, "w") as f:
            json.dump(existing, f, indent=2)
        result["status"] = "success"
        result["reason"] = f"Added '{server_name}' to {config_path}"
    except PermissionError as e:
        result["status"] = "error"
        result["reason"] = f"Permission denied: {e}"

    return result


def main():
    print("=" * 60)
    print("  GitHub Ecosystem MCP — Setup for All Platforms")
    print("=" * 60)
    print()

    results = []

    for name, config in PLATFORMS.items():
        print(f"Setting up {name}...")
        result = setup_platform(name, config)
        results.append(result)

        if result["status"] == "success":
            print(f"  ✓ {result['reason']}")
        elif result["status"] == "already_configured":
            print(f"  • {result['reason']}")
        elif result["status"] == "skipped":
            print(f"  ○ {result['reason']}")
        else:
            print(f"  ✗ {result['reason']}")

    print()
    print("=" * 60)
    print("  Summary")
    print("=" * 60)

    success = [r for r in results if r["status"] == "success"]
    skipped = [r for r in results if r["status"] == "skipped"]
    errors = [r for r in results if r["status"] == "error"]
    already = [r for r in results if r["status"] == "already_configured"]

    print(f"  ✓ Configured: {len(success)}")
    print(f"  • Already set: {len(already)}")
    print(f"  ○ Skipped (no config): {len(skipped)}")
    print(f"  ✗ Errors: {len(errors)}")

    if success:
        print()
        print("  Next steps:")
        print("  1. Restart each configured platform")
        print("  2. The 'github-ecosystem' tools will appear")
        print("  3. Use them like any other tool")

    print()
    print("  Available tools:")
    print("    discover_layer   — Find repos for a layer")
    print("    discover_all     — Search all layers")
    print("    analyze_repo     — Map a repo's structure")
    print("    extract_module   — Pull a file from a repo")
    print("    isolate_wrapper  — Generate safe wrapper")
    print("    test_extraction  — Verify code works")
    print("    generate_imports — Generate import code")
    print("    full_pipeline    — Complete extraction pipeline")


if __name__ == "__main__":
    main()
