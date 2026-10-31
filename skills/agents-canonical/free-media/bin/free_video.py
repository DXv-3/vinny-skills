#!/usr/bin/env python3
"""Free keyless text-to-video via the LTX-Video Hugging Face Space.

Runs under the skill venv (has gradio_client). Blocks until the clip lands
(shared public queue: ~30s typical, minutes at peak).

Usage:
    .venv/bin/python bin/free_video.py "a cat leaping in slow motion" --out clip.mp4
    .venv/bin/python bin/free_video.py "ocean waves" --seconds 3 --width 512 --height 320 --out waves.mp4
"""
import argparse
import os
import re
import sys

# Sandbox quirk: httpx chokes on bracketed IPv6 entries in NO_PROXY.
_np = os.environ.get("NO_PROXY", "")
_np = ",".join(p for p in _np.split(",") if not (p.startswith("[") and p.endswith("]")))
os.environ["NO_PROXY"] = _np
os.environ["no_proxy"] = _np


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seconds", type=int, default=2)
    ap.add_argument("--width", type=int, default=384)
    ap.add_argument("--height", type=int, default=256)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--negative", default="worst quality")
    args = ap.parse_args()

    from gradio_client import Client

    c = Client("Lightricks/ltx-video-distilled")
    result = c.predict(
        args.prompt,
        args.negative,
        None, None,                      # input_image_filepath, input_video_filepath
        args.height, args.width,          # height_ui, width_ui
        "text-to-video",                  # mode
        args.seconds,                     # duration_ui
        9,                                # ui_frames_to_use
        args.seed, False,                 # seed_ui, randomize_seed
        1,                                # ui_guidance_scale
        False,                            # improve_texture_flag
        api_name="/text_to_video",
    )
    video = None
    candidates = result if isinstance(result, (list, tuple)) else [result]
    for cand in candidates:
        if isinstance(cand, dict) and cand.get("video"):
            video = cand["video"]
            break
        elif isinstance(cand, str) and cand:
            video = cand
            break
    if not video or not os.path.exists(video):
        print(f"ERROR: no video file returned: {result!r}", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    # gradio returns a local downloaded path; move it to the requested output
    if os.path.abspath(video) != os.path.abspath(args.out):
        os.replace(video, args.out)
    size = os.path.getsize(args.out)
    print(f"OK {args.out} ({size} bytes, {args.seconds}s, {args.width}x{args.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
