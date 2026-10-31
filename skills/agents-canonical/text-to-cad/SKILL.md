---
name: text-to-cad
description: Umbrella catalog for the text-to-cad agent-skill library (earthtojake/text-to-cad, MIT) — parametric CAD modeling, STEP/STL/3MF/DXF export, DFM checks, G-code, 3D-printer profiles (Bambu), SendCutSend quoting, URDF/SDF/SRDF robot descriptions, engineering drawings. Use for any CAD/CAE/CAM task, machining prep, or RFQ artifact.
---

# text-to-cad — agent skills for CAD, CAE and CAM

Local clone: **`~/Projects/text-to-cad/`** (shallow clone of earthtojake/text-to-cad, MIT, 16.4k★).
Sub-skills live in the clone — when one matches the task, READ its SKILL.md and follow it:

| Sub-skill | Path | Use for |
|---|---|---|
| cad | `~/Projects/text-to-cad/skills/cad/SKILL.md` | Create/edit parametric models; export STEP/STL/3MF/GLB; measure geometry (`cadgen`) |
| step-parts | `~/Projects/text-to-cad/skills/step-parts/SKILL.md` | Organize/export multi-part STEP assemblies |
| dfm | `~/Projects/text-to-cad/skills/dfm/SKILL.md` | Design-for-manufacture checks before RFQ/machining |
| dfam-check | `~/Projects/text-to-cad/skills/dfam-check/SKILL.md` | Design-for-additive-manufacture checks |
| dxf | `~/Projects/text-to-cad/skills/dxf/SKILL.md` | 2D DXF (laser/plasma cutting) |
| gcode | `~/Projects/text-to-cad/skills/gcode/SKILL.md` | G-code generation/inspection |
| bambu-labs | `~/Projects/text-to-cad/skills/bambu-labs/SKILL.md` | Bambu 3D-printer profiles/slicing |
| sendcutsend | `~/Projects/text-to-cad/skills/sendcutsend/SKILL.md` | SendCutSend quoting/laser-cut prep |
| engineering-drawing | `~/Projects/text-to-cad/skills/engineering-drawing/SKILL.md` | Dimensioned drawings |
| cad-viewer | `~/Projects/text-to-cad/skills/cad-viewer/SKILL.md` | Preview/inspect generated geometry |
| urdf / sdf / srdf | `~/Projects/text-to-cad/skills/{urdf,sdf,srdf}/SKILL.md` | Robot descriptions (MoveIt/ sim) |

**Dependency:** the `cad` skill drives `cadgen` (Python, pip-installable, open source). If missing: `pip install cadgen` (or `pip install -r ~/Projects/text-to-cad/requirements-dev.txt` for the dev stack per the repo's AGENTS.md).

**House rule (from the vessel-pipeline Code Doctor review):** boolean/machining ops must fail loudly when a geometry kernel is missing — never fall back to returning unmodified geometry. Ensure `manifold3d` is installed for mesh booleans.
