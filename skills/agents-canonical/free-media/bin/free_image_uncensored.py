#!/usr/bin/env python3
"""Uncensored image generation via verified Hugging Face Spaces (keyless).

Backends (all verified 2026-09-17, anonymous Gradio API):
  fulxdev     alexander00001/Adult.NSFW.Image.FULX1dev      (simplest, 512px)
  ponyxl      artificialguybr/PonyDiffusion-XL-Free-DEMO    (1024px)
  wai         IbarakiDouji/WAI-NSFW-illustrious-SDXL        (1024px anime)
  ponyrealism gokaygokay/PonyRealism                        (512px, prefix tags)

"Uncensored" = author-described only; filter behavior was not probed.
These Spaces churn (pauses/takedowns) — if one fails twice, try another.

Usage:
    .venv/bin/python bin/free_image_uncensored.py "prompt" --out out.png
    .venv/bin/python bin/free_image_uncensored.py "prompt" --backend ponyxl --out out.png
"""
import argparse
import os
import sys

# Sandbox quirk: httpx chokes on bracketed IPv6 entries in NO_PROXY.
_np = os.environ.get("NO_PROXY", "")
_np = ",".join(p for p in _np.split(",") if not (p.startswith("[") and p.endswith("]")))
os.environ["NO_PROXY"] = _np
os.environ["no_proxy"] = _np


def _first_file(obj):
    """Walk gradio_client's return value to find a real local file path."""
    if isinstance(obj, str):
        return obj if os.path.exists(obj) else None
    if isinstance(obj, dict):
        for key in ("path", "url", "orig_name"):
            v = obj.get(key)
            if isinstance(v, str) and os.path.exists(v):
                return v
        for v in obj.values():
            f = _first_file(v)
            if f:
                return f
        return None
    if isinstance(obj, (list, tuple)):
        for v in obj:
            f = _first_file(v)
            if f:
                return f
        return None
    return None


def _gen_fulxdev(c, prompt, seed):
    r = c.predict(prompt, "Realistic", "", 12, 3.5, seed,
                  "512x512 (Ultra Fast)", api_name="/generate_wrapper")
    return _first_file(r)


def _gen_ponyxl(c, prompt, seed):
    r = c.predict(prompt, api_name="/run")
    return _first_file(r)


def _gen_wai(c, prompt, seed):
    r = c.predict(prompt, "", seed, 1024, 1024, 7.0, 20, "DPM++ 2M Karras",
                  "v12", "Custom", False, 0.55, 1.5, True, api_name="/generate")
    return _first_file(r)


def _gen_ponyrealism(c, prompt, seed):
    r = c.predict("Pony Realism v22", prompt, "worst quality", 512, 512, 20, 6.0,
                  1, True, 0, "Euler a", 2, False, False, False, False,
                  True, True, False, "2", api_name="/generate_image")
    return _first_file(r)


BACKENDS = {
    "fulxdev": ("alexander00001/Adult.NSFW.Image.FULX1dev", _gen_fulxdev),
    "ponyxl": ("artificialguybr/PonyDiffusion-XL-Free-DEMO", _gen_ponyxl),
    "wai": ("IbarakiDouji/WAI-NSFW-illustrious-SDXL", _gen_wai),
    "ponyrealism": ("gokaygokay/PonyRealism", _gen_ponyrealism),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--out", required=True)
    ap.add_argument("--backend", default="fulxdev", choices=list(BACKENDS))
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    from gradio_client import Client

    space, gen = BACKENDS[args.backend]
    c = Client(space, httpx_kwargs={"timeout": 600})
    src = gen(c, args.prompt, args.seed)
    if not src:
        print(f"ERROR: backend {args.backend} returned no file", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(args.out):
        # copy (gradio temp files may be cleaned); fall back to replace on same fs
        try:
            os.replace(src, args.out)
        except OSError:
            import shutil
            shutil.copyfile(src, args.out)
    print(f"OK {args.out} ({os.path.getsize(args.out)} bytes, backend={args.backend})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
