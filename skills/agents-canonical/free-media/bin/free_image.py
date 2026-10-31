#!/usr/bin/env python3
"""Free keyless image generation via Pollinations.ai (FLUX). Stdlib only.

Usage:
    free_image.py "a small red cube on a white table" --out out.jpg
    free_image.py "sunset over Tampa bay" --width 1024 --height 1024 --model flux --seed 42 --out img.jpg
"""
import argparse
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://image.pollinations.ai/prompt"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--model", default="flux", help="flux (verified), turbo")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    q = {"width": args.width, "height": args.height, "model": args.model, "nologo": "true"}
    if args.seed is not None:
        q["seed"] = args.seed
    url = BASE + "/" + urllib.parse.quote(args.prompt) + "?" + urllib.parse.urlencode(q)

    req = urllib.request.Request(url, headers={"User-Agent": "VesperFreeMedia/1.0"})
    # Attach the stored Pollinations credential when available (Seed tier:
    # standard models, nologo honored, faster rate). Falls back to anonymous.
    try:
        sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
        from dynamic_credentials import add_surrogate_to_request

        add_surrogate_to_request(req, "custom.pollinations",
                                 allowed_hosts=["image.pollinations.ai"])
        auth_note = "auth=seed"
    except Exception:
        auth_note = "auth=anonymous"
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
    except Exception as e:
        print(f"ERROR: pollinations request failed: {e}", file=sys.stderr)
        return 1
    if len(data) < 1024 or not data[:2] == b"\xff\xd8" and data[:4] != b"\x89PNG":
        # not strictly fatal (webp possible) but suspicious if tiny
        if len(data) < 1024:
            print(f"ERROR: suspiciously small response ({len(data)} bytes)", file=sys.stderr)
            return 1
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "wb") as f:
        f.write(data)
    print(f"OK {args.out} ({len(data)} bytes, model={args.model}, {args.width}x{args.height}, {auth_note})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
