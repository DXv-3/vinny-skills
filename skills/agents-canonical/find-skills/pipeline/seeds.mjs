// pipeline/seeds.mjs
// Known-systems seed map. Some capabilities are NAMED systems (not generic
// keywords). When the topic/idea references one, we inject the canonical repo,
// its papers, and CURATED feature-parts pulled straight from the source — so
// the parts bin contains the REAL features, not guesses from lookalike repos.
//
// Add new systems here as we learn them. Each entry:
//   match:   regexes that trigger the seed
//   sources: canonical repo + papers (for provenance / trust)
//   parts:   curated feature-parts (already decomposed), tagged like decompose()

export const KNOWN_SYSTEMS = [
  {
    id: "storm",
    match: [/\bstorm\b/i, /topic outline/i, /wikipedia.*from scratch/i],
    label: "STORM (Stanford OVAL)",
    sources: [
      { kind: "repo", ref: "stanford-oval/storm", stars: 28400, link: "https://github.com/stanford-oval/storm" },
      { kind: "paper", ref: "arXiv:2402.14207", venue: "NAACL 2024", link: "https://arxiv.org/abs/2402.14207",
        title: "Assisting in Writing Wikipedia-like Articles From Scratch with LLMs" },
    ],
    parts: [
      ["mental-model", "STORM = Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking; two stages: pre-writing (research+outline) then writing (grounded article with citations)."],
      ["workflow", "Perspective discovery: survey existing articles on similar topics to enumerate diverse viewpoints before asking questions."],
      ["workflow", "Perspective-guided question asking: each discovered persona asks questions from its own angle (beats naive 'ask 30 questions')."],
      ["workflow", "Simulated conversation: a writer-persona converses with a topic-expert grounded on trusted internet sources, updating understanding and asking follow-ups."],
      ["workflow", "Curation to outline: synthesize the collected Q&A into a structured outline (the core pre-writing artifact)."],
      ["workflow", "Grounded writing stage: expand the outline into a full article with inline citations to the retrieved references."],
      ["edge-case", "Known failure modes: source bias transfer and over-association of unrelated facts; guard against both when curating."],
      ["table", "Eval via FreshWiki dataset + rubric metrics: ROUGE, entity recall, heading entity recall, outline quality."],
    ],
  },
  {
    id: "co-storm",
    match: [/\bco[\s-]?storm\b/i, /unknown unknowns/i, /collaborative storm/i, /mind ?map.*agent/i],
    label: "Co-STORM (Stanford/Yale)",
    sources: [
      { kind: "repo", ref: "stanford-oval/storm", stars: 28400, link: "https://github.com/stanford-oval/storm" },
      { kind: "paper", ref: "arXiv:2408.15232", venue: "EMNLP 2024", link: "https://arxiv.org/abs/2408.15232",
        title: "Into the Unknown Unknowns: Engaged Human Learning through Participation in LM Agent Conversations" },
    ],
    parts: [
      ["mental-model", "Co-STORM = collaborative discourse among several LM agents that the user observes and occasionally steers, surfacing 'unknown unknowns' the user wouldn't think to ask."],
      ["workflow", "Collaborative discourse protocol: a turn-management policy decides which agent speaks next to keep the multi-agent conversation productive."],
      ["prompt", "Multi-agent roles: instantiate perspective-A agent, perspective-B agent, and a Moderator that steers and injects complementary information."],
      ["workflow", "Human-in-the-loop steering: agents ask questions on the user's behalf; the user mostly observes and can inject direction at any turn."],
      ["feature", "Dynamic mind map: organize uncovered information into a live, growing mind map as the discourse proceeds."],
      ["feature", "Report-as-takeaways: generate a comprehensive final report synthesized from the mind map."],
      ["table", "Eval via WildSeek dataset (real info-seeking goals); 70% of participants prefer Co-STORM over a search engine, 78% over a RAG chatbot."],
      ["edge-case", "Limitations: higher latency (utterance-intent decision + mind-map update), weak tailoring to user prior knowledge, English-centric."],
    ],
  },
  {
    // OUR invented layer — the divergent front-end STORM/Co-STORM lack.
    // STORM/Co-STORM are convergent (research a known topic -> grounded report).
    // BRAINSTORM blows the problem space open FIRST, then hands survivors to
    // STORM as perspectives + seed questions. This is the custom Stanford twist.
    id: "brainstorm-layer",
    match: [/\bbrainstorm\b/i, /\bideation\b/i, /\bdivergent\b/i, /\bidea storm\b/i],
    label: "Brainstorm Layer (custom)",
    invented: true,
    sources: [
      { kind: "invented", ref: "custom/brainstorm-layer", link: "",
        title: "Divergent pre-STORM ideation layer (our design)" },
    ],
    parts: [
      ["mental-model", "BRAINSTORM is the DIVERGENT front-end to STORM/Co-STORM: open the problem space wide before STORM converges. It outputs exactly what STORM consumes — perspectives + seed questions — so the two stages compose."],
      ["workflow", "Problem reframing: restate the prompt 5 ways before ideating — invert it, generalize it, tightly constrain it, analogize it to another domain, and reduce it to first principles."],
      ["workflow", "Perspective explosion: generate wildly diverse personas beyond Co-STORM's expert A/B — adversary, novice, historian, futurist, contrarian, cross-domain outsider. These feed STORM's perspective-discovery step."],
      ["workflow", "Divergent idea storm: run SCAMPER + random-stimulus + 'worst possible idea' passes to force quantity and novelty. No filtering yet — quantity first."],
      ["workflow", "Unknown-unknown probes: invert Co-STORM's mind map — explicitly ask 'what would we NOT think to ask?' to seed the multi-agent discourse with blind spots."],
      ["workflow", "Convergence gate: cluster and dedupe ideas, then score each by novelty × feasibility × fit; only survivors pass to STORM as perspectives + seed questions."],
      ["prompt", "Stanford academic framing: rewrite every surviving idea as a research question and flag its citation needs, so STORM's grounded-writing stage has concrete claims to ground."],
      ["edge-case", "Handoff contract: BRAINSTORM diverges -> convergence gate filters -> STORM/Co-STORM grounds & writes. Never let divergent noise reach the writing stage unfiltered (avoids over-association of unrelated facts)."],
    ],
  },
  {
    // Deliberation structures — richer multi-agent formats than STORM's plain
    // discourse. Each is a distinct, real protocol grounded in code + practice.
    id: "deliberation-structures",
    match: [/\bcouncil\b/i, /\bjur(y|ies)\b/i, /\bpanel\b/i, /\bfishbowl\b/i, /\bdebate\b/i, /\bdeliberat/i],
    label: "Deliberation Structures",
    sources: [
      { kind: "repo", ref: "karpathy/llm-council", stars: null, link: "https://github.com/karpathy/llm-council",
        title: "LLM Council — 3-stage deliberation (answer, peer-rank, chairman synthesis)" },
      { kind: "repo", ref: "hummaam27/llm-council", stars: null, link: "https://github.com/hummaam27/llm-council",
        title: "LLM Council fork — debate mode + moderator synthesis + interruptible panel" },
      { kind: "repo", ref: "amitpl909/llm-debate-system", stars: null, link: "https://github.com/amitpl909/llm-debate-system",
        title: "LLM Debate with Judge & Jury Panel (Irving et al. 2018 debate + jury deliberation)" },
      { kind: "paper", ref: "arXiv:1805.00899", venue: "2018", link: "https://arxiv.org/abs/1805.00899",
        title: "AI Safety via Debate (Irving et al.)" },
      { kind: "method", ref: "fishbowl/kaner-lind", link: "https://en.wikipedia.org/wiki/Fishbowl_(conversation)",
        title: "Fishbowl (Kaner & Lind; Liberating Structures #18)" },
    ],
    parts: [
      ["mental-model", "Deliberation structures are pluggable discourse formats that sit where Co-STORM's plain multi-agent conversation runs; pick the format to match the decision (converge vs diverge, judge vs consensus)."],
      // Council
      ["workflow", "COUNCIL (3-stage): each agent answers the prompt independently, then anonymously ranks the other answers, then a chairman synthesizes one final response from the ranked set."],
      ["prompt", "COUNCIL roles: N peer members + 1 chairman; optionally assign adversarial roles to peers to prevent echo chambers."],
      // Jury / Panel
      ["workflow", "JURY/PANEL: 3+ judge agents independently evaluate, surface disagreement, run deliberation rounds toward consensus; compare jury accuracy vs a single judge."],
      ["table", "JURY voting rules: majority (ties default to reject/low-confidence), unanimous (accept only if all concur), or reliability-weighted aggregation (weight each juror by an estimated reliability score)."],
      ["edge-case", "JURY caveat: correlate panel disagreement with question difficulty; use adaptive stopping (e.g., stability detection) so deliberation ends when consensus dynamics stabilize instead of running fixed rounds."],
      // Debate
      ["workflow", "DEBATE (MAD): 2+ debaters take positions and argue over N rounds with access to debate history; resolve via an LLM judge or self-consistency majority vote."],
      ["prompt", "DEBATE roles: proponent, opponent, and (optional) judge; assign adversarial personas to force genuine opposition and surface the premise left unsaid."],
      ["edge-case", "DEBATE caveat: LLMs anchor to initial positions ('hung jury' effect) and heavy RLHF alignment makes them rigid; explicitly prompt open-mindedness and prefer flexible models for mind-changing."],
      // Fishbowl
      ["mental-model", "FISHBOWL: a small inner circle actively discusses while a larger outer circle observes; an empty chair lets an observer swap in, so perspectives rotate through the conversation."],
      ["workflow", "FISHBOWL turn policy: seed the inner circle with a few agents, keep 1-2 empty chairs; an outer-circle agent may take an empty chair (an inner agent then rotates out), continuously refreshing viewpoints."],
      ["feature", "FISHBOWL variants: open (any observer joins anytime), closed (fixed inner group, rotate on a timer), tap-out (observer taps an inner agent to swap), silent (outer circle only observes and annotates)."],
      ["prompt", "FISHBOWL fit: it lives in the DIVERGENT phase (Kaner's Diamond) — surface many perspectives before converging; pairs naturally with the Brainstorm Layer's perspective explosion."],
    ],
  },
  {
    // Swarm-simulation tier — the largest deliberation scale: not a few judges
    // but thousands of persona-agents evolving in a simulated society, used to
    // predict emergent outcomes. Sits ABOVE council/jury/panel/fishbowl.
    id: "swarm-simulation",
    match: [/\bswarm\b/i, /\bsimulation\b/i, /\bmirofish\b/i, /\boasis\b/i, /\bagent society\b/i, /\bsocial simulation\b/i, /\bemergent\b/i, /\bpredict/i],
    label: "Swarm Simulation (MiroFish/OASIS)",
    sources: [
      { kind: "repo", ref: "666ghj/MiroFish", stars: 68735, link: "https://github.com/666ghj/MiroFish",
        title: "MiroFish — universal swarm-intelligence prediction engine (thousands of persona-agents)" },
      { kind: "repo", ref: "camel-ai/oasis", stars: null, link: "https://github.com/camel-ai/oasis",
        title: "OASIS — Open Agent Social Interaction Simulations (MiroFish's underlying engine)" },
    ],
    parts: [
      ["mental-model", "SWARM SIMULATION is the largest deliberation scale: instead of a few debating agents, run thousands of persona-agents with independent personalities, long-term memory, and behavioral logic that interact and socially evolve to reveal EMERGENT outcomes."],
      ["workflow", "Seed -> digital world: extract seed information (news, policy drafts, financial signals, or a story) and auto-construct a high-fidelity parallel world to run the crowd inside."],
      ["workflow", "Graph building: build a GraphRAG knowledge graph with individual + collective memory injection, then dynamic temporal memory updates as the simulation runs."],
      ["workflow", "Environment setup: extract entity relationships from the seed, auto-generate agent personas, and inject per-agent configuration before simulating."],
      ["feature", "God's-eye variable injection: dynamically inject variables mid-simulation to deduce alternative future trajectories ('what-if' rehearsal at zero real-world risk)."],
      ["feature", "ReportAgent: a post-simulation agent with a rich toolset that deeply interacts with the settled world to produce a prediction report (parallels Co-STORM's report-as-takeaways)."],
      ["feature", "Deep interaction: chat with any individual agent in the simulated world, or with the ReportAgent, to interrogate why an outcome emerged."],
      ["mental-model", "Use-tier selector: pick swarm simulation for EMERGENT crowd outcomes/prediction; pick council/jury/panel/debate for a VERDICT from a few experts; pick fishbowl/brainstorm for DIVERGENT perspective surfacing."],
      ["edge-case", "Swarm caveat: high token/compute cost — start with short runs (e.g. <40 rounds) before scaling; simulation fidelity depends on persona and memory quality."],
    ],
  },
];

// Return seeds whose match hits the combined topic+idea text.
export function matchSeeds(text) {
  const hay = text.toLowerCase();
  return KNOWN_SYSTEMS.filter((s) => s.match.some((re) => re.test(hay)));
}

// Turn a seed into candidate rows + pre-decomposed parts.
export function seedToCandidatesAndParts(seed) {
  const candidates = seed.sources.map((src) => ({
    pkg: src.ref,
    installs: null,
    stars: src.stars ?? null,
    query: `seed:${seed.id}`,
    link: src.link,
    shelf: src.kind === "paper" ? "paper" : "seed",
    description: src.title || seed.label,
    trust: "HIGH",
    reason: `curated seed — ${seed.label} (${src.venue || src.kind})`,
    seeded: true,
  }));
  const parts = seed.parts.map(([type, text]) => ({
    source: `${seed.label}`,
    type,
    heading: seed.label,
    text,
    trust: "HIGH",
    seeded: true,
  }));
  return { candidates, parts };
}
