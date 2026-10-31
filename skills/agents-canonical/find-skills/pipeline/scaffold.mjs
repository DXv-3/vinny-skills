// pipeline/scaffold.mjs
// Stage 7: emit the synthesized CUSTOM BUILD to out/scaffold/.
// We do NOT install a whole repo. We assemble the chosen parts into a real,
// usable skill: SKILL.md (structured workflow) + prompts/ + workflows/ +
// snippets/ + RECIPE.md (provenance).

import { write, ensureDir } from "./lib.mjs";
import { join } from "node:path";

const TYPE_ORDER = ["mental-model", "prompt", "workflow", "feature", "table", "snippet", "edge-case"];
const TYPE_HEADING = {
  "mental-model": "Core Model",
  prompt: "Agent Roles & Instructions",
  workflow: "Workflow Steps",
  feature: "Capabilities",
  table: "Evaluation & Metrics",
  snippet: "Code / Templates",
  "edge-case": "Failure Modes & Guards",
};

function bySelected(parts) {
  const g = {};
  for (const t of TYPE_ORDER) g[t] = [];
  for (const p of parts) (g[p.type] ||= []).push(p);
  return g;
}

export async function emitScaffold(outDir, { topic, idea, synth }) {
  const base = join(outDir, "scaffold");
  await ensureDir(base);

  const selected = [...synth.recipe.lift, ...synth.recipe.adapt];
  const invent = synth.recipe.invent.filter((g) => !/No obvious gap/.test(g));
  const grouped = bySelected(selected);

  // Build a structured, actually-usable SKILL.md ordered as a real pipeline.
  const sections = TYPE_ORDER
    .filter((t) => grouped[t] && grouped[t].length)
    .map((t) => {
      const items = grouped[t]
        .map((p) => `- ${p.text}  \n  _(source: ${p.source})_`)
        .join("\n");
      return `## ${TYPE_HEADING[t]}\n${items}`;
    })
    .join("\n\n");

  const inventSection = invent.length
    ? `\n\n## Invent (gaps not covered by any source)\n${invent.map((g) => `- ${g}`).join("\n")}`
    : "";

  const skillMd = `---
name: custom-${slug(topic)}
description: Custom Stanford-tuned build synthesized from STORM/Co-STORM parts. ${idea}
---

# Custom Build: ${title(topic)}

Assembled from the corpus (STORM + Co-STORM papers/repo) — not adopted whole.

## Idea
${idea}

${sections}${inventSection}

## Provenance
Every part above was pulled off the GitHub/paper shelf, decomposed, and matched
to this idea. See ../report.html for the full Parts Catalog and Ideas-vs-Parts
analysis, and RECIPE.md for lift/adapt/invent classification.
`;

  // Split parts into the sub-files by type.
  let prompts = "", workflows = "", snippets = "";
  for (const p of selected) {
    if (p.type === "prompt") prompts += `- [${p.source}] ${p.text}\n`;
    if (p.type === "workflow") workflows += `- [${p.source}] ${p.text}\n`;
    if (p.type === "snippet") snippets += `# from ${p.source}\n${p.text}\n\n`;
  }

  const recipe = `# RECIPE — custom build for: ${topic}

## LIFT (use verbatim) — ${synth.recipe.lift.length}
${synth.recipe.lift.map((p) => `- [${p.source}] (${p.type}) ${p.text}`).join("\n") || "- none"}

## ADAPT (modify before use) — ${synth.recipe.adapt.length}
${synth.recipe.adapt.map((p) => `- [${p.source}] (${p.type}) ${p.text}`).join("\n") || "- none"}

## INVENT (corpus gap) — ${invent.length}
${invent.length ? invent.join("\n") : "- none (idea fully covered)"}

## How to finish
1. LIFT parts are ready to use — they're already grouped in SKILL.md by role.
2. Rewrite ADAPT parts for our context.
3. Build INVENT parts from scratch.
4. Wire prompts/ + workflows/ into the SKILL.md pipeline.
`;

  await write(join(base, "SKILL.md"), skillMd);
  await write(join(base, "prompts", "PROMPTS.md"), prompts || "# (no prompt parts selected)\n");
  await write(join(base, "workflows", "WORKFLOWS.md"), workflows || "# (no workflow parts selected)\n");
  await write(join(base, "snippets", "SNIPPETS.md"), snippets || "# (no snippet parts selected)\n");
  await write(join(base, "RECIPE.md"), recipe);
  return base;
}

function slug(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40); }
function title(s) { return s.replace(/\b\w/g, (c) => c.toUpperCase()); }
