#!/usr/bin/env python3
"""One-shot generation via ClickyGPT/NSFW_Z-Image-Turbo (Gradio /infer)."""
import os
import sys

# Sandbox quirk: httpx chokes on bracketed IPv6 entries in NO_PROXY.
_np = os.environ.get("NO_PROXY", "")
_np = ",".join(p for p in _np.split(",") if not (p.startswith("[") and p.endswith("]")))
os.environ["NO_PROXY"] = _np
os.environ["no_proxy"] = _np

PROMPT = (
    "Bold cartoon illustration, thick black outlines, flat vibrant colors, white background. "
    "Exactly TWO men. MAN 1: completely bald head, thick black mustache, pearl necklace, "
    "shirtless, standing. MAN 2: black hair in a topknot man bun, short black beard, black "
    "tank top, kneeling in front of MAN 1, MAN 1's hard erect cock inside MAN 2's mouth, "
    "MAN 2 actively giving MAN 1 a blowjob. Explicit gay adult cartoon, both men masculine."
)
NEGATIVE = "woman, female, 1girl, girl, extra limbs, deformed anatomy, blurry, photorealistic, text, watermark"

if "--check" in sys.argv:
    from gradio_client import Client
    Client("ClickyGPT/NSFW_Z-Image-Turbo")
    print("Z-IMAGE CONNECT OK")
    sys.exit(0)

from gradio_client import Client

out = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "/tmp/zimage-test.png")
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7

print("connecting to ClickyGPT/NSFW_Z-Image-Turbo ...", flush=True)
import httpx
c = Client(
    "ClickyGPT/NSFW_Z-Image-Turbo",
    httpx_kwargs={"timeout": httpx.Timeout(300.0, connect=30.0)},
)
print("calling /infer ...", flush=True)
r = c.predict(PROMPT, NEGATIVE, seed, False, 1024, 1024, 0.0, 4, api_name="/infer")
print("raw result type:", type(r))


def first_file(o):
    if isinstance(o, str):
        return o if os.path.exists(o) else None
    if isinstance(o, dict):
        for k in ("path", "url", "orig_name"):
            v = o.get(k)
            if isinstance(v, str) and os.path.exists(v):
                return v
        for v in o.values():
            f = first_file(v)
            if f:
                return f
        return None
    if isinstance(o, (list, tuple)):
        for v in o:
            f = first_file(v)
            if f:
                return f
        return None
    return None


src = first_file(r)
if not src:
    print("NO FILE in result:", str(r)[:500])
    sys.exit(1)
import shutil
shutil.copy(src, out)
print("OK", out, os.path.getsize(out), "bytes")
