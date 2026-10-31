#!/usr/bin/env python3
"""forge.py -- stamp a generic REST CLI into a scaffolded connector skill.

Usage:
    forge.py --provider <slug> --name "Display Name" --hosts api.example.com[,api2.example.com]

Expects the connector custom.<slug> to be connected already (the scaffold
script reads it from authd and fails honestly if it isn't). Safe to re-run:
it only writes bin/<slug>.py and patches the SKILL.md Tooling section.
"""
import argparse
import os
import py_compile
import subprocess
import sys

SKILLS_DIR = os.path.expanduser("~/workspace/skills")
SCAFFOLD = "/opt/hatch/skills/skill-creator/bin/scaffold-connector-skill"

CLI_TEMPLATE = '''#!/usr/bin/env python3
"""__SLUG__.py -- minimal REST CLI for __NAME__, backed by the stored
custom.__SLUG__ credential.

Usage:
    __SLUG__.py get <path>
    __SLUG__.py post <path> [json-body]
    __SLUG__.py put <path> [json-body]
    __SLUG__.py patch <path> [json-body]
    __SLUG__.py delete <path>
    __SLUG__.py put-file <owner> <repo> <repo-path> <message> <branch> <content>

(put-file is a GitHub-ism; ignore it for non-GitHub providers.)
Prints "HTTP <status>" then the JSON body. Auth goes through the authd
surrogate helper -- this script never sees the real credential.
"""
import base64
import json
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

CRED = "custom.__SLUG__"
HOSTS = [__HOSTS__]
BASE = "https://__BASE_HOST__"


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "muse-connector/__SLUG__")
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        req.add_header("Content-Type", "application/json")
        req.data = payload
    add_surrogate_to_request(req, CRED, allowed_hosts=HOSTS)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, read_json_response(resp)
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
    if cmd == "put-file":
        if len(argv) < 8:
            print("put-file needs: owner repo repo-path message branch content")
            return 2
        owner, repo, repo_path, message, branch, content = argv[2:8]
        if not content.endswith("\\n"):
            content += "\\n"
        body = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        status, data = call("PUT", "/repos/%s/%s/contents/%s" % (owner, repo, repo_path), body)
    elif cmd in ("get", "post", "put", "patch", "delete"):
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


def render_cli(slug, name, hosts):
    hosts_py = ", ".join('"%s"' % h for h in hosts)
    return (
        CLI_TEMPLATE.replace("__SLUG__", slug)
        .replace("__NAME__", name)
        .replace("__HOSTS__", hosts_py)
        .replace("__BASE_HOST__", hosts[0])
    )


def patch_tooling(skill_dir, slug):
    skill_md = os.path.join(skill_dir, "SKILL.md")
    with open(skill_md) as f:
        text = f.read()
    marker = "Add service-specific CLIs under"
    if marker in text:
        lines = text.splitlines(keepends=True)
        out = []
        for line in lines:
            out.append(line)
            if marker in line:
                out.append(
                    "`bin/%s.py` -- generic REST CLI (get/post/put/patch/delete/put-file).\n"
                    "Run it with no args for usage. Auth is automatic via the authd\n"
                    "surrogate helper; the script never sees the real credential.\n" % slug
                )
        with open(skill_md, "w") as f:
            f.writelines(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stamp a REST CLI into a connector skill.")
    ap.add_argument("--provider", required=True, help="connector slug, e.g. github")
    ap.add_argument("--name", required=True, help="display name, e.g. GitHub")
    ap.add_argument("--hosts", required=True, help="comma-separated API hosts")
    args = ap.parse_args(argv)

    slug = args.provider
    hosts = [h.strip() for h in args.hosts.split(",") if h.strip()]
    if not hosts:
        ap.error("--hosts needs at least one hostname")

    print("scaffolding custom.%s ..." % slug)
    r = subprocess.run([SCAFFOLD, "--provider", "custom." + slug])
    if r.returncode != 0:
        print("scaffold failed (exit %d) -- is custom.%s connected?" % (r.returncode, slug))
        return 1

    skill_dir = os.path.join(SKILLS_DIR, slug)
    if not os.path.isdir(skill_dir):
        print("scaffold did not create %s -- aborting" % skill_dir)
        return 1

    bin_dir = os.path.join(skill_dir, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    cli_path = os.path.join(bin_dir, slug + ".py")
    with open(cli_path, "w") as f:
        f.write(render_cli(slug, args.name, hosts))
    os.chmod(cli_path, 0o755)
    py_compile.compile(cli_path, doraise=True)
    patch_tooling(skill_dir, slug)

    print("wrote %s" % cli_path)
    print("next: test with a cheap read, e.g. %s get /<profile-or-list-endpoint>" % cli_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
