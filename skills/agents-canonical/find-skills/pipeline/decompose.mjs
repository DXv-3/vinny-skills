// pipeline/decompose.mjs
// Stage 4: break a repo's text into PARTS and tag each.
// Part types: feature | prompt | workflow | table | snippet | mental-model | edge-case
//
// Works on ANY repo (skills package, video editor, CLI, library). A "video
// editor" repo becomes N feature-parts; the synthesizer later keeps only the
// ones we want. Heuristic (regex + section cues) — enough to build a Parts
// Index across the whole corpus.

import { PART_TYPES } from "./lib.mjs";

function tagFor(line, heading) {
  const l = line.toLowerCase();
  const h = (heading || "").toLowerCase();
  if (/^```|^function |^const |^import |^export |\$\{|\brequire\(|<\w+>/.test(line)) return "snippet";
  if (/\|\s.*\|/.test(line)) return "table";
  if (/(step|then|next|loop|repeat|workflow|procedure|checklist|if .* then)/.test(l)) return "workflow";
  if (/(avoid|never|edge|fail|error|unless|caution|warning|limitation|if .* not)/.test(l + h)) return "edge-case";
  if (/(model|pattern|mental|idea|treat .* as|think of .* as|concept)/.test(l + h)) return "mental-model";
  if (/(you (must|should|are|will)|always|do not|forbid|instruction|system)/.test(l)) return "prompt";
  return "feature";
}

// Split markdown into heading-delimited chunks, then sentence/bullet-level parts.
export function decompose(pkg, text) {
  const parts = [];
  if (!text) return parts;
  const chunks = text.split(/^#{1,6}\s+/m);
  for (const chunk of chunks) {
    const heading = chunk.split("\n")[0].slice(0, 60);
    const body = chunk.slice(heading.length);
    // capture bullet lines (common in feature lists) and sentences
    const lines = body.split("\n").map((s) => s.replace(/^[-*]\s+/, "").trim());
    const units = [];
    for (const ln of lines) {
      if (ln.length > 6) units.push(ln);
      // also split long lines into sentences
      if (ln.length > 120) {
        ln.split(/(?<=[.!?])\s+/).forEach((s) => s.trim().length > 24 && units.push(s.trim()));
      }
    }
    for (const u of units) {
      if (u.length < 12 || u.length > 400) continue;
      const type = tagFor(u, heading);
      parts.push({ source: pkg, type, heading, text: u });
    }
  }
  const seen = new Set();
  return parts.filter((p) => {
    const k = p.text.toLowerCase();
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

export { PART_TYPES };
