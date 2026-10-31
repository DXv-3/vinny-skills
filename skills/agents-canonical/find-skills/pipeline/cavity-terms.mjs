// pipeline/cavity-terms.mjs
// The CAVITY SEARCH term bank — max-depth GitHub queries for hunting reusable
// PARTS (not whole repos) across every tier of our build.
//
// Derived from an audit of everything we have:
//   STORM · Co-STORM · Brainstorm Layer · Deliberation Structures · Swarm Sim
//
// Each group is a "drill site" on GitHub. Run them via `gh search repos <q>` and
// `gh search code <q>` to expose the parts inside repos. Ordered high-signal
// first. These are intentionally specific — generic words ("ai", "agent") are
// noise; we want the exact mechanisms.

export const CAVITY_TERMS = {
  // --- STORM tier: research -> outline -> grounded writing ---
  storm_research: [
    "multi-perspective question asking",
    "perspective guided question generation",
    "outline generation retrieval augmented",
    "grounded long-form article generation citations",
    "knowledge curation LLM",
    "pre-writing stage LLM outline",
    "simulated conversation topic expert",
    "STORM knowledge storm",
  ],

  // --- Co-STORM tier: collaborative discourse + mind map ---
  costorm_discourse: [
    "collaborative discourse protocol LLM agents",
    "turn management policy multi agent",
    "dynamic mind map agent conversation",
    "human in the loop agent steering",
    "unknown unknowns information seeking",
    "moderator agent synthesis",
    "co-storm collaborative storm",
  ],

  // --- Brainstorm Layer: divergent ideation ---
  brainstorm_divergent: [
    "SCAMPER ideation LLM",
    "divergent thinking idea generation agent",
    "problem reframing first principles prompt",
    "worst possible idea brainstorm technique",
    "persona explosion diverse viewpoints generator",
    "random stimulus creativity prompt",
    "idea clustering deduplication scoring novelty",
    "convergence gate idea filtering",
  ],

  // --- Deliberation Structures: council / jury / panel / debate / fishbowl ---
  deliberation: [
    "llm council chairman synthesis",
    "multi agent debate judge",
    "jury panel deliberation consensus LLM",
    "reliability weighted judge aggregation",
    "adaptive stopping debate stability",
    "self consistency majority vote agents",
    "adversarial roles echo chamber prevention",
    "fishbowl discussion facilitation rotation",
    "liberating structures facilitation",
    "AI safety via debate",
    "premise recovery multi agent",
  ],

  // --- Swarm Simulation: emergent crowds / prediction ---
  swarm_sim: [
    "agent social simulation society",
    "swarm intelligence prediction engine",
    "thousands of agents persona simulation",
    "graphrag memory agent simulation",
    "emergent behavior multi agent society",
    "generative agents memory reflection",
    "digital twin society what-if scenario",
    "OASIS open agent social interaction",
    "public opinion simulation agents",
  ],

  // --- Cross-cutting infrastructure (parts EVERY tier reuses) ---
  infra: [
    "long term memory agent vector store",
    "persona generation from documents",
    "citation grounding inline references LLM",
    "openrouter model panel orchestration",
    "SSE streaming agent debate UI",
    "cost tracking token budget agents",
    "transcript management pruning agents",
    "entity relationship extraction knowledge graph",
    "report generation agent toolset",
  ],
};

// Flatten to a single ordered query list (for a full cavity sweep).
export function allCavityTerms() {
  return Object.values(CAVITY_TERMS).flat();
}

// Return the cavity groups relevant to a topic/idea (keyword-triggered).
export function cavityTermsFor(text) {
  const t = text.toLowerCase();
  const hit = {};
  const trig = {
    storm_research: /storm|outline|research|wikipedia|article|curation/,
    costorm_discourse: /co-?storm|discourse|mind ?map|steer|unknown/,
    brainstorm_divergent: /brainstorm|ideat|divergent|scamper|creativ/,
    deliberation: /council|jur|panel|debate|fishbowl|deliberat|judge|vote/,
    swarm_sim: /swarm|simulat|mirofish|oasis|emergent|predict|society|crowd/,
    infra: /memory|citation|persona|stream|cost|graph|report/,
  };
  for (const [group, re] of Object.entries(trig)) {
    if (re.test(t)) hit[group] = CAVITY_TERMS[group];
  }
  // always include infra as the shared base
  hit.infra = CAVITY_TERMS.infra;
  return hit;
}
