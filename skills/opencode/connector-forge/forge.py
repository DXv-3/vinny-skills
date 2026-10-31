#!/usr/bin/env python3
"""forge.py -- stamp a Keychain-backed REST CLI for any API (OpenCode edition).

Usage:
    forge.py --provider <slug> --name "Display Name" --hosts api.example.com[,api2]
             --placement bearer_header | custom_header:<Name> | query_param:<name>

Writes ~/.config/opencode/connectors/<slug>/<slug>.py (stdlib only; the key is
read from the macOS Keychain at runtime, never stored in a file).
Safe to re-run: it only rewrites that one file.
"""
import argparse
import os
import py_compile
import sys

CONNECTORS = os.path.expanduser("~/.config/opencode/connectors")

CLI_TEMPLATE = '''#!/usr/bin/env python3
"""__SLUG__.py -- minimal REST CLI for __NAME__.

The API key lives in the macOS Keychain (service "connector-__SLUG__") and is
read at runtime; it never appears in chat, files, env vars, or logs.

Usage:
    __SLUG__.py get <path>
    __SLUG__.py post <path> [json-body]
    __SLUG__.py put <path> [json-body]
    __SLUG__.py patch <path> [json-body]
    __SLUG__.py delete <path>

Prints "HTTP <status>" then the JSON body.
"""
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

SERVICE = "connector-__SLUG__"
BASE = "https://__BASE_HOST__"
PLACEMENT = "__PLACEMENT__"  # bearer_header | custom_header:<Name> | query_param:<name>


def get_key():
    r = subprocess.run(
        ["security", "find-generic-password", "-s", SERVICE, "-w"],
        capture_output=True, text=True,
    )
    key = r.stdout.strip()
    if r.returncode != 0 or not key:
        sys.exit(
            "no key in Keychain for '%s'. Add it with:\\n"
            "  security add-generic-password -s %s -a __SLUG__ -w" % (SERVICE, SERVICE)
        )
    return key


def build_request(method, path, key, body=None):
    if PLACEMENT.startswith("query_param:"):
        param = PLACEMENT.split(":", 1)[1]
        sep = "&" if "?" in path else "?"
        path = "%s%s%s=%s" % (path, sep, param, urllib.parse.quote(key, safe=""))
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "opencode-connector/__SLUG__")
    if PLACEMENT == "bearer_header":
        req.add_header("Authorization", "Bearer " + key)
    elif PLACEMENT.startswith("custom_header:"):
        req.add_header(PLACEMENT.split(":", 1)[1], key)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req.add_header("Content-Type", "application/json")
        req.data = data
    return req


def call(method, path, body=None):
    key = get_key()
    req = build_request(method, path, key, body)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read().decode("utf-8"))
        except Exception:
            detail = {"message": "HTTPError %s" % e.code}
        return e.code, detail


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip())
        return 2
    cmd = argv[1]
    if cmd in ("get", "post", "put", "patch", "delete"):
        body = json.loads(argv[3]) if len(argv) > 3 else None
        status, data = call(cmd.upper(), argv[2], body)
    else:
        print("unknown command: %s" % cmd)
        return 2
    print("HTTP %s" % status)
    print(json.dumps(data, indent=2)[:4000])
    return 0 if status < 400 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
'''

PLACEMENTS = ("bearer_header",)


def valid_placement(p):
    return p == "bearer_header" or p.startswith("custom_header:") or p.startswith("query_param:")


def render_cli(slug, name, hosts, placement):
    return (
        CLI_TEMPLATE.replace("__SLUG__", slug)
        .replace("__NAME__", name)
        .replace("__BASE_HOST__", hosts[0])
        .replace("__PLACEMENT__", placement)
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stamp a Keychain-backed REST CLI.")
    ap.add_argument("--provider", required=True, help="connector slug, e.g. stripe")
    ap.add_argument("--name", required=True, help='display name, e.g. "Stripe"')
    ap.add_argument("--hosts", required=True, help="comma-separated API hosts")
    ap.add_argument("--placement", required=True,
                    help="bearer_header | custom_header:<Name> | query_param:<name>")
    args = ap.parse_args(argv)

    slug = args.provider
    hosts = [h.strip() for h in args.hosts.split(",") if h.strip()]
    if not hosts:
        ap.error("--hosts needs at least one hostname")
    if not valid_placement(args.placement):
        ap.error("--placement must be bearer_header, custom_header:<Name>, or query_param:<name>")

    dest_dir = os.path.join(CONNECTORS, slug)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, slug + ".py")
    with open(dest, "w") as f:
        f.write(render_cli(slug, args.name, hosts, args.placement))
    os.chmod(dest, 0o755)
    py_compile.compile(dest, doraise=True)

    print("wrote %s" % dest)
    print("key needed in Keychain: security add-generic-password -s connector-%s -a %s -w" % (slug, slug))
    print("then test: %s get /<profile-or-list-endpoint>" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
