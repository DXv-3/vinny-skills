# Image Spot — design notes

Why this skill exists: the 2026-09-17 image-spot session burned ~15 generations
learning the same lessons over and over (prompt drift, feminized figures,
unverified sends). This packages the working system so every future session
starts where that one ended.

## Architecture

```
chat ("programming") → cast.yaml (library) → bin/cast.py (assembler)
    → free-media uncensored backend → verify (human read) → user
```

The user never writes raw prompts. He names blocks; `cast.py` concatenates:

```
style.prompt + setting.prompt + character prompts + act({a},{b},{c}) + global_guards
```

New people/places/styles enter through chat ("add character X: ...") and get
appended to `cast.yaml`. The rule of thumb: described twice → named block.

## Why blocks, not prompts

Raw prompts drifted every generation — the same scene came out differently
because wording changed each time. Named blocks pin the reusable parts
(the coach is always the coach) while acts stay per-scene. Seeds make
variations reproducible.

## Backend routing (earned, not assumed)

| style     | backend     | verdict 2026-09-17                              |
|-----------|-------------|--------------------------------------------------|
| bara      | wai         | Follows scenes, strong gay-male output. Anime look only; photoreal prompts still render illustrated. |
| photoreal | ponyrealism | Can look photographic; drops characters, ignores acts, drew a woman against explicit guards. Untrusted. |
| (alt)     | fulxdev     | Same unreliability class as ponyrealism.        |
| (alt)     | ponyxl      | 1024px, anime-leaning. Untested for this content. |

Routing lives in the style block so it can change without touching scenes.

## Known model failure modes (all observed 2026-09-17)

1. **Feminization of submissive figures.** Kneeling/blindfolded/bound young men
   render female despite "no women" guards — twice on the dunes scene.
   Mitigation: masculine-coded character prompts (jaw, muscle, body hair,
   mature age); verify every output.
2. **Group collapse.** 4–5 figure prompts render 2–3. Mitigation: per-figure
   position pinning (`MAN 1: ...`); honest reporting when it still collapses.
3. **Stray limbs.** Floating hands/arms. Mitigation: anatomy guards in every
   prompt; visual check before send.
4. **Photoreal backends ignoring instructions.** Documented above; the
   verify-before-send rule exists because of this, not as bureaucracy.

## The verify loop

Generation is cheap; trust is not. After `cast.py` succeeds, the agent reads
the image and checks male-only, scene match, anatomy. Trash + retry (≤3) or
report. A failed send the user catches costs more than ten trashed renders.

## Open questions

- Better photoreal engine for gay male content (the hunt continues).
- Video: no working uncensored video endpoint exists as of 2026-09-17.
- Whether the user wants named "series" (recurring cast across scenes).
