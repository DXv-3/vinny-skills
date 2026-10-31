#!/usr/bin/env python3
"""gh.py -- minimal GitHub REST CLI backed by the stored custom.github credential.

Usage:
    gh.py get <path>
    gh.py post <path> [json-body]
    gh.py put <path> [json-body]
    gh.py put-file <owner> <repo> <repo-path> <message> <branch> <content>
        # content is plain text; it gets base64-encoded automatically

Prints "HTTP <status>" then the JSON body. Auth goes through the authd
surrogate helper -- this script never sees the real token.
"""
import base64
import json
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import (
    add_surrogate_to_request,
    read_json_response,
)

CRED = "custom.github"
HOSTS = ["api.github.com"]
BASE = "https://api.github.com"


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "muse-github-skill/1.0")
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
            detail = {"message": f"HTTPError {e.code}"}
        return e.code, detail


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip())
        return 2
    cmd, path = argv[1], argv[2]
    if cmd == "put-file":
        if len(argv) < 8:
            print("put-file needs: owner repo repo-path message branch content")
            return 2
        owner, repo, repo_path, message, branch, content = argv[2:8]
        if not content.endswith("\n"):
            content += "\n"
        body = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        status, data = call("PUT", f"/repos/{owner}/{repo}/contents/{repo_path}", body)
    elif cmd in ("get", "post", "put", "patch", "delete"):
        body = json.loads(argv[3]) if len(argv) > 3 else None
        status, data = call(cmd.upper(), path, body)
    else:
        print(f"unknown command: {cmd}")
        return 2
    print(f"HTTP {status}")
    print(json.dumps(data, indent=2)[:4000])
    return 0 if status < 400 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
