#!/usr/bin/env python3
"""cast.py — assemble an Image Spot scene from the cast library and generate it.

A scene is "programmed" from named blocks:
    style + setting + characters + act + global_guards  ->  free-media backend

Usage:
    bin/cast.py --style bara --setting showers --cast coach swimmer \
        --act blowjob --out ~/workspace/your_files/scene.png
    bin/cast.py --style bara --setting dunes --cast youngman older \
        --act "custom freeform act description" --out out.png --seed 7
    bin/cast.py --print ...        # show the assembled prompt, don't generate
    bin/cast.py --list             # show library contents

Act templates use {a} {b} {c} for the cast members in order; a custom --act
string is used verbatim. New characters/settings/styles/acts are defined in
chat and appended to cast.yaml — never hand-edit prompts per scene.
"""
import argparse
import os
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(SKILL_DIR, "cast.yaml")
FREE_MEDIA = os.path.expanduser("~/workspace/skills/free-media")
GEN = os.path.join(FREE_MEDIA, "bin", "free_image_uncensored.py")
VENV_PY = os.path.join(FREE_MEDIA, ".venv", "bin", "python")


def load_lib():
    import yaml
    with open(LIB) as f:
        return yaml.safe_load(f)


def build_prompt(lib, style, setting, cast, act):
    parts = []
    st = lib["styles"].get(style)
    if not st:
        raise SystemExit(f"unknown style '{style}' (see --list)")
    parts.append(st["prompt"])
    if setting:
        se = lib["settings"].get(setting)
        if not se:
            raise SystemExit(f"unknown setting '{setting}' (see --list)")
        parts.append(se["prompt"])
    descs = []
    shorts = []
    for name in cast:
        ch = lib["characters"].get(name)
        if not ch:
            raise SystemExit(f"unknown character '{name}' (see --list)")
        descs.append(ch["prompt"])
        shorts.append(ch.get("short", name))
    parts.extend(descs)
    if act:
        tpl = lib.get("acts", {}).get(act, {}).get("prompt", act)
        subs = {"a": shorts[0] if len(shorts) > 0 else "",
                "b": shorts[1] if len(shorts) > 1 else "",
                "c": shorts[2] if len(shorts) > 2 else ""}
        parts.append(tpl.format(**subs))
    parts.append(lib["global_guards"])
    backend = st["backend"]
    return " ".join(parts), backend


def main():
    ap = argparse.ArgumentParser(description="Assemble and generate an Image Spot scene.")
    ap.add_argument("--style", default="bara", help="style block from library")
    ap.add_argument("--setting", default=None, help="setting block from library")
    ap.add_argument("--cast", nargs="*", default=[], help="character names in order")
    ap.add_argument("--act", default=None, help="named act or freeform description")
    ap.add_argument("--out", default=None, help="output path")
    ap.add_argument("--seed", type=int, default=None, help="seed (random if omitted)")
    ap.add_argument("--backend", default=None, help="override the style's backend")
    ap.add_argument("--print", action="store_true", help="print prompt only")
    ap.add_argument("--list", action="store_true", help="list library contents")
    args = ap.parse_args()

    lib = load_lib()
    if args.list:
        for section in ("styles", "settings", "characters", "acts"):
            print(f"[{section}]")
            for name, entry in lib.get(section, {}).items():
                note = f"  # {entry.get('notes')}" if isinstance(entry, dict) and entry.get("notes") else ""
                be = f" -> {entry['backend']}" if isinstance(entry, dict) and entry.get("backend") else ""
                print(f"  {name}{be}{note}")
        return

    prompt, backend = build_prompt(lib, args.style, args.setting, args.cast, args.act)
    if args.backend:
        backend = args.backend
    if args.print or not args.out:
        print(f"backend: {backend}")
        print(prompt)
        return

    cmd = [VENV_PY, GEN, prompt, "--out", os.path.expanduser(args.out),
           "--backend", backend]
    if args.seed is not None:
        cmd += ["--seed", str(args.seed)]
    r = subprocess.run(cmd, cwd=FREE_MEDIA, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        raise SystemExit(f"generator failed (exit {r.returncode})")
    print(f"prompt used: {prompt[:160]}...")


if __name__ == "__main__":
    main()
