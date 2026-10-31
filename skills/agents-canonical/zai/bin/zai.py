#!/usr/bin/env python3
"""zai.py -- minimal REST CLI for Z.ai, backed by the stored
custom.zai credential.

Usage:
    zai.py get <path>
    zai.py post <path> [json-body]
    zai.py put <path> [json-body]
    zai.py patch <path> [json-body]
    zai.py delete <path>
    zai.py put-file <owner> <repo> <repo-path> <message> <branch> <content>

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

CRED = "custom.zai"
HOSTS = ["api.z.ai"]
BASE = "https://api.z.ai"


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "muse-connector/zai")
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
        if not content.endswith("\n"):
            content += "\n"
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
