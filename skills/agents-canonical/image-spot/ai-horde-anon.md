# AI Horde — anonymous image API (verified 2026-09-20 ~18:20 EDT)

Keyless (anonymous key `0000000000`), non-HF, community GPU network.
Benign test passed: 512x512 webp of a red cube, viewed and confirmed.

## Submit
POST https://stablehorde.net/api/v2/generate/async
Headers: apikey: 0000000000, Content-Type: application/json
Body:
{
  "prompt": "a small red cube on a white table, photorealistic",
  "params": {"n": 1, "width": 512, "height": 512, "steps": 20,
             "sampler_name": "k_euler", "cfg_scale": 7.0, "seed": "7"},
  "nsfw": false,
  "models": ["stable_diffusion"],
  "r2": true
}
-> {"id": "<job-id>", ...}

## Poll
GET https://stablehorde.net/api/v2/generate/check/<job-id>  -> {"done": true, ...}

## Fetch
GET https://stablehorde.net/api/v2/generate/status/<job-id>
-> generations[0].img is a SIGNED R2 URL (keep the ?X-Amz-... query string!)

## Timed run
- submit accepted in ~11s
- queue: position 146 -> processing at ~67s -> done at ~116s
- total submit-to-image-bytes: ~2.5 min (anonymous, low priority)
- worker: squeeko, model: stable_diffusion

## Notes
- Anonymous = lowest priority; queue_position hit 146. Expect 1-5 min typically.
- The request schema supports "nsfw": true; workers opt into NSFW models.
  Filter behavior NOT probed (benign test only).
- Python urllib POST hung twice (60s, 240s timeouts); curl worked first try.
  Prefer curl or requests with generous timeouts for the submit call.
