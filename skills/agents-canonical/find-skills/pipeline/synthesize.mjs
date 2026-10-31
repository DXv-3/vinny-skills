// pipeline/synthesize.mjs
// Stage 5: run the user's IDEA against the whole Parts Index.
// For each part we decide: CONFIRM (idea already does this) / EXTEND (part adds
// to idea) / CONTRADICT (part conflicts) / COMBINE (mashup candidate). Then we
// emit a custom-build recipe: which parts to LIFT, ADAPT, or INVENT.
//
// Relevance is a simple token-overlap scorer (no ML needed). The user's idea is
// the query; each part's text is scored. High score => the part is on-topic for
// the idea. There is NO fixed cap on how many parts we grab — we take however
// many the idea needs (could be 2, could be 30).

function tokenize(s) {
  return new Set(
    s.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter((w) => w.length > 2)
  );
}

function overlap(aTokens, bTokens) {
  let hit = 0;
  for (const t of aTokens) if (bTokens.has(t)) hit++;
  return hit / Math.max(1, aTokens.size);
}

// Decide the relationship of a part to the idea.
function relate(ideaTokens, ideaText, part) {
  const pTokens = tokenize(part.text + " " + part.heading);
  const score = overlap(ideaTokens, pTokens);
  const ideaWords = ideaText.toLowerCase();
  const pWords = (part.text + " " + part.heading).toLowerCase();

  // Seeded parts are pre-verified — they always pass through
  if (part.seeded) return { rel: "EXTEND", score: Math.max(score, 0.2) };

  // crude contradiction signals
  const contra = /(instead|avoid|never|don't|do not|rather than|opposite)/.test(pWords) &&
                 overlap(ideaTokens, pTokens) > 0.1;
  if (contra) return { rel: "CONTRADICT", score };
  if (score >= 0.18) return { rel: "EXTEND", score };
  if (score >= 0.08) return { rel: "COMBINE", score };
  return { rel: "CONFIRM", score }; // low overlap = idea already covers it independently
}

export function synthesize(idea, parts) {
  const ideaTokens = tokenize(idea);
  const scored = parts.map((p) => {
    const { rel, score } = relate(ideaTokens, idea, p);
    return { ...p, rel, score };
  });

  // Parts the idea actually wants (relevant): EXTEND / COMBINE, sorted by score.
  const wanted = scored
    .filter((p) => p.rel === "EXTEND" || p.rel === "COMBINE")
    .sort((a, b) => b.score - a.score);

  const confirmed = scored.filter((p) => p.rel === "CONFIRM");
  const contradicted = scored.filter((p) => p.rel === "CONTRADICT");

  // Recipe: LIFT (high trust + relevant), ADAPT (relevant but needs change),
  // INVENT (idea needs something no part covers — derived from idea words with
  // zero relevant parts).
  // Seeded parts always LIFT (they're curated from papers/repos, pre-verified).
  const seededParts = wanted.filter((p) => p.seeded);
  const nonSeeded = wanted.filter((p) => !p.seeded);
  const lift = [...seededParts, ...nonSeeded.filter((p) => p.trust === "HIGH" || p.trust === "MED")];
  const adapt = nonSeeded.filter((p) => p.trust === "LOW");
  const invent = deriveInvent(idea, wanted);

  return {
    scored,
    wanted,
    confirmed: confirmed.length,
    contradicted,
    recipe: { lift, adapt, invent },
  };
}

// Meta/stop words that are never real capability gaps.
const META_WORDS = new Set([
  "custom", "tuned", "skill", "build", "system", "tool", "the", "and", "for",
  "with", "that", "this", "into", "from", "your", "our", "using", "based",
  "want", "need", "make", "like", "type", "stuff", "thing", "then", "have",
]);

// Find idea concepts with no covering part -> things we must invent.
function deriveInvent(idea, wanted) {
  const ideaTokens = tokenize(idea);
  const covered = new Set();
  for (const w of ideaTokens) {
    for (const p of wanted) {
      if ((p.text + " " + p.heading).toLowerCase().includes(w)) covered.add(w);
    }
  }
  const gaps = [...ideaTokens].filter(
    (w) => !covered.has(w) && w.length > 3 && !META_WORDS.has(w)
  );
  return gaps.length
    ? gaps.map((g) => `INVENT: no existing part covers "${g}" — design custom.`)
    : ["No obvious gap — idea is fully covered by harvested parts."];
}
