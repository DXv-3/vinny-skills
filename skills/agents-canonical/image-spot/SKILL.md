---
name: image-spot
description: "Image Spot"
---

# Image Spot

The user's image-request side chat runs on this skill. Scenes are "programmed"
from a library of named blocks instead of hand-written prompts each time.

## The library — `cast.yaml`

Four block types, all defined once and reused:

- **styles** — look + backend routing. `bara` (default) routes to `wai`.
  `photoreal` routes to `ponyrealism` but is flagged unreliable.
- **settings** — places: `showers`, `dunes`, `bathhouse`.
- **characters** — named people: `coach`, `swimmer`, `older`, `youngman`.
  Character prompts are masculine-coded on purpose (see Design).
- **acts** — reusable actions with `{a}` `{b}` `{c}` placeholders for cast order:
  `blowjob`, `rimming`, `bukkake`. Or pass freeform text per scene.

`global_guards` is appended to every prompt, always.

## Programming in chat

The user programs scenes in plain chat. Translate to `bin/cast.py`:

```
bin/cast.py --style bara --setting showers --cast coach swimmer \
    --act blowjob --out ~/workspace/your_files/scene.png [--seed N]
```

- `--act` takes a library name or freeform description.
- `--print` shows the assembled prompt without generating (use for review).
- `--list` shows the library.
- `--backend` overrides the style's routing.

Defining new blocks (user says "add character/setting/style/act ..."):
append to `cast.yaml` and confirm. Never invent people per-scene — if the user
describes someone new twice, they become a named character.

## Standing rules (non-negotiable)

1. **Every person is male, always.** If anything reads female, the image is
   trashed and never sent. This is the user's hard rule, not a preference.
2. **Wai is the default engine.** It follows scenes; it cannot do photoreal.
3. **Verify every image before sending.** Read the file, check: all figures
   male, scene matches the prompt, anatomy sane (no extra/floating limbs).
   Fail → trash it, regenerate (max 3 tries), or report honestly.
4. **Photoreal backends are untrusted.** They drop characters, ignore acts,
   and have drawn women against explicit instructions. Use only with rule 3,
   and warn the user first.
5. **Group scenes collapse.** The model merges 4+ figures into 2–3. Pin each
   figure down with a distinct position (`MAN 1: ... MAN 2: ...`); if it still
   collapses, say so instead of shipping a "group" of two.
6. **Feminization trap.** Slim/pretty/young submissive figures get drawn
   female no matter the guards. Character prompts must be masculine-coded:
   square jaw, muscular, body hair, mature. When in doubt, butch it up.
7. Deliver as chat attachments (`sandbox://workspace/...`), one per line.
8. Generation runs on free-media's uncensored backends (see
   `~/workspace/skills/free-media/SKILL.md`); never promise a filter outcome.
