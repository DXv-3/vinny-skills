#!/usr/bin/env python3
"""jev.py -- ask TypeSafe's Jev decision model a typed question via OpenRouter.

Jev can't chat or write text. It answers structured decisions:
  choice -- pick one of up to 255 options (returns probabilities + confidence)
  noul   -- yes/no probability
  score  -- ordered levels + weighted score

Usage:
    jev.py choice --state "..." --question "..." --options "keep:sharp,dump:blurry,review:borderline"
    jev.py noul   --state "..." --question "Is this photo sharp?" --criterion "visible blur"
    jev.py score  --state "..." --question "Rate sharpness" --levels "1:soft,2:ok,3:tack"
    jev.py raw    --json '{"state": ..., "questions": {...}}'
    jev.py choice --state-file state.json --question "..." --options ...

Pricing: $0.042/M input tokens, output free. Prints the decision JSON.
Auth goes through the authd surrogate helper -- this script never sees the
real credential.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

CRED = "custom.openrouter"
HOSTS = ["openrouter.ai"]
BASE = "https://openrouter.ai"
MODEL = "typesafe/jev-1.13"


def call(body):
    body = dict(body)
    body.setdefault("model", MODEL)
    req = urllib.request.Request(BASE + "/api/alpha/decisions", method="POST")
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "muse-connector/jev")
    req.data = json.dumps(body).encode("utf-8")
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
    ap = argparse.ArgumentParser(description="Ask Jev a typed decision question.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("choice", "noul", "score"):
        p = sub.add_parser(name)
        p.add_argument("--state", default="")
        p.add_argument("--state-file", default="")
        p.add_argument("--question", required=True)
        p.add_argument("--name", default="q1")
        p.add_argument("--instructions", default="",
                       help="how to judge; defaults to the question text")
        p.add_argument("--criteria-json", default="",
                       help='explicit criteria record, e.g. {"keep": "sharp photo"}')
        if name == "choice":
            p.add_argument("--options", default="",
                           help='"keep:sharp photo,dump:blurry" or plain names')
        if name == "noul":
            p.add_argument("--criterion", default="",
                           help="description of the yes/no criterion")
        if name == "score":
            p.add_argument("--levels", default="",
                           help='"1:terrible,2:ok,3:great" or plain level names')

    r = sub.add_parser("raw")
    r.add_argument("--json", required=True)

    args = ap.parse_args(argv[1:])

    if args.cmd == "raw":
        body = json.loads(args.json)
    else:
        state = args.state
        if args.state_file:
            with open(args.state_file) as f:
                raw = f.read()
            try:
                state = json.loads(raw)
            except Exception:
                state = raw
        def pairs(spec):
            out = {}
            for item in spec.split(","):
                name, _, desc = item.partition(":")
                name = name.strip()
                if name:
                    out[name] = desc.strip() or name
            return out

        criteria = json.loads(args.criteria_json) if args.criteria_json else {}
        if args.cmd == "choice":
            criteria = {**pairs(args.options), **criteria}
        elif args.cmd == "noul":
            tf = pairs(args.criterion) if args.criterion else {}
            if "true" not in tf and "false" not in tf:
                desc = args.criterion or args.question
                tf = {"true": desc, "false": "the opposite is the case: " + desc}
            criteria = {**tf, **criteria}
        elif args.cmd == "score":
            # score takes criteria as an ORDERED ARRAY of level descriptions
            levels = []
            for item in args.levels.split(","):
                _, _, desc = item.partition(":")
                desc = desc.strip() or item.strip()
                if desc:
                    levels.append(desc)
            if isinstance(criteria, dict) and criteria:
                levels = list(criteria.values())
            criteria = levels
        if not criteria:
            raise SystemExit("criteria is required: pass --options/--criterion/--levels or --criteria-json")

        q = {"type": args.cmd,
             "question": args.question,
             "instructions": args.instructions or args.question,
             "criteria": criteria}
        body = {"state": state, "questions": {args.name: q}}

    status, data = call(body)
    print("HTTP", status)
    print(json.dumps(data, indent=2))
    return 0 if status == 200 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
