// pipeline/explode.mjs
// Stage 1: turn a topic into an exhaustive query tree.
// Covers: literal, synonyms, adjacent domains, tool/library names, acronyms,
// inverse angles, creative mashups, cross-agent ecosystems. Minimum 10 queries.
//
// The tree is built from a SYNONYM/ADJACENT bank keyed on topic words, PLUS a
// set of GENERIC modifiers (academic, structured, divergent, citation-aware…)
// so we fan out into real sub-branches instead of only cross-agent repeats.

const SYNONYM_BANK = {
  brainstorm: ["ideate", "ideation", "mind-map", "think-up", "concept-generation", "whiteboard"],
  ideation: ["brainstorm", "idea-generation", "concepting", "divergent-thinking"],
  storm: ["storming", "rapid-ideation", "brainstorm-burst", "idea-storm"],
  academic: ["scholarly", "research", "university", "thesis", "paper"],
  stanford: ["university", "cs-school", "design-school", "academic", "research"],
  custom: ["tailored", "bespoke", "personalized", "specialized"],
  synthesis: ["combine", "merge", "integrate", "summarize", "conclude"],
  citation: ["reference", "cite", "source-aware", "bibliography", "footnote"],
  structured: ["guided", "step-by-step", "framework", "method"],
  divergent: ["lateral", "wild", "unconstrained", "expansive", "free-association"],
};

const ADJACENT_BANK = {
  brainstorm: ["workshop", "facilitation", "problem-framing", "questioning", "exploration"],
  storm: ["creativity", "lateral-thinking", "idea-density", "volume"],
  ideation: ["concept-map", "morphological", "scamper", "six-hats"],
};

const CROSS_AGENT = ["claude", "cursor", "copilot", "codex", "kilocode", "aider", "cline"];

function words(topic) {
  return topic.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter(Boolean);
}

function fan(synKey, base) {
  const syns = SYNONYM_BANK[synKey] || [];
  return syns.map((s) => (base ? `${s} ${base}` : s));
}

export function explode(topic) {
  const ws = words(topic);
  const all = new Set();
  const push = (...xs) => xs.forEach((x) => x && all.add(x.trim().toLowerCase()));

  push(topic);
  push(...ws);

  // synonyms + adjacent for each topic word, in both word orders
  for (const w of ws) {
    (SYNONYM_BANK[w] || []).forEach((s) => { push(`${s} ${w}`); push(`${w} ${s}`); });
    (ADJACENT_BANK[w] || []).forEach((s) => { push(`${s} ${w}`); push(`${w} ${s}`); });
  }

  // generic modifier fan-out (academic/structured/divergent/citation/synthesis)
  const mods = ["academic", "structured", "divergent", "citation", "synthesis", "custom"];
  for (const m of mods) for (const w of ws) push(`${m} ${w}`, `${w} ${m}`);

  // synonym x synonym combos (creative branches)
  const allSyns = new Set();
  for (const w of ws) (SYNONYM_BANK[w] || []).forEach((s) => allSyns.add(s));
  const synsArr = [...allSyns];
  for (let i = 0; i < synsArr.length; i++)
    for (let j = i + 1; j < synsArr.length; j++) push(`${synsArr[i]} ${synsArr[j]}`);

  // acronyms
  if (ws.length >= 2) push(ws.map((w) => w[0]).join(""));

  // cross-agent ecosystems (a few, not the whole tree)
  for (const a of CROSS_AGENT.slice(0, 4)) push(`${a} ${topic}`);

  return [...all].filter((q) => q.length >= 3).slice(0, 40);
}
