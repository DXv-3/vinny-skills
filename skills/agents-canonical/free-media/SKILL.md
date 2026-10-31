---
name: free-media
description: "Generate images and video through verified free keyless endpoints — Pollinations.ai (FLUX) for images, LTX-Video Hugging Face Space for short video clips. Use when the user wants media made via free outside models instead of the built-in media pipeline."
metadata:
  includeInPrompt: true
---

# Free Media

## Purpose
Route image/video generation requests to live-verified free keyless models, so generation isn't limited to the built-in pipeline. Nothing here needs a signup, key, or payment.

## Tooling
Helpers live in `bin/` (run from this skill's directory):

- **Images** (Pollinations.ai, FLUX, stdlib only):
  `python3 bin/free_image.py "prompt" --out /path/out.jpg [--width 1024 --height 1024 --model flux|turbo --seed 42]`
- **Video** (LTX-Video via HF Space, needs the skill venv):
  `.venv/bin/python bin/free_video.py "prompt" --out /path/clip.mp4 [--seconds 2 --width 384 --height 256 --seed 42]`
  Blocks until the clip lands (shared queue: ~30 s typical, minutes at peak). For slow queues, run in background.
- **Uncensored images** (verified HF Spaces, keyless, needs the skill venv):
  `.venv/bin/python bin/free_image_uncensored.py "prompt" --out /path/out.png [--backend fulxdev|ponyxl|wai|ponyrealism --seed 7]`
  Default `fulxdev` (simplest, 512px); `ponyxl` for 1024px. Queued ZeroGPU spaces: allow minutes.

## Auth
Pollinations: uses the stored `custom.pollinations` credential (Seed tier) when
available — `bin/free_image.py` attaches it automatically and falls back to
anonymous if the vault is unreachable. Video and uncensored endpoints stay
anonymous/keyless. Never ask the user for a raw key; the vault is the only
source. See `~/workspace/skills/pollinations/SKILL.md`.

## Operating Rules
1. **Images:** with the stored Seed credential, `nologo=true` is honored and
   standard models (flux/turbo) work; anonymous outputs carry a small
   `pollinations.ai` watermark and are currently limited to basic models.
   Tell the user about the watermark when it matters; don't surprise them.
2. **Video:** clips are short (1–3 s typical) and low-res (256–384p default, up to 1280). LTX-Video license is custom (`other` on the model card) — fine for personal use, flag before anything commercial.
3. Be polite to shared resources: one request at a time, small sizes first, never hammer the queue.
4. If an endpoint fails twice in a row, fall back to the built-in `media.generate_image` / `media.generate_video` and say so plainly.
5. **Uncensored backends:** "uncensored" means author-described only — filter behavior was never probed, so never promise a specific filter outcome. These Spaces churn (pauses/takedowns); if one dies, try the next backend. There is currently NO working uncensored video endpoint (all found are paused) — say so instead of faking it.
5. Deliver results to the user as chat attachments (`sandbox://workspace/...` links), same as built-in media output.
6. Full hunt report with signup-tier leads (Gemini API free tier for images, Zhipu CogVideoX-Flash for video): `~/workspace/your_files/free-media-models/free-media-models-report.md`. If the user offers to sign up somewhere, those are the two to start with.
