---
name: custom-storm-co-storm-brainstorm-council-jury-p
description: Custom Stanford-tuned build synthesized from STORM/Co-STORM parts. A custom Stanford-tuned brainstorm+STORM engine with pluggable deliberation tiers: divergent brainstorm and fishbowl perspective surfacing, council/jury/panel/debate verdicts with a moderator, and swarm simulation for emergent crowd prediction, all feeding perspective-guided question asking, a dynamic mind map, unknown-unknown probes, and a citation-grounded synthesis report
---

# Custom Build: Storm Co-Storm Brainstorm Council Jury Panel Fishbowl Swarm Simulation

Assembled from the corpus (STORM + Co-STORM papers/repo) — not adopted whole.

## Idea
A custom Stanford-tuned brainstorm+STORM engine with pluggable deliberation tiers: divergent brainstorm and fishbowl perspective surfacing, council/jury/panel/debate verdicts with a moderator, and swarm simulation for emergent crowd prediction, all feeding perspective-guided question asking, a dynamic mind map, unknown-unknown probes, and a citation-grounded synthesis report

## Core Model
- Use-tier selector: pick swarm simulation for EMERGENT crowd outcomes/prediction; pick council/jury/panel/debate for a VERDICT from a few experts; pick fishbowl/brainstorm for DIVERGENT perspective surfacing.  
  _(source: Swarm Simulation (MiroFish/OASIS))_
- STORM = Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking; two stages: pre-writing (research+outline) then writing (grounded article with citations).  
  _(source: STORM (Stanford OVAL))_
- Co-STORM = collaborative discourse among several LM agents that the user observes and occasionally steers, surfacing 'unknown unknowns' the user wouldn't think to ask.  
  _(source: Co-STORM (Stanford/Yale))_
- BRAINSTORM is the DIVERGENT front-end to STORM/Co-STORM: open the problem space wide before STORM converges. It outputs exactly what STORM consumes — perspectives + seed questions — so the two stages compose.  
  _(source: Brainstorm Layer (custom))_
- Deliberation structures are pluggable discourse formats that sit where Co-STORM's plain multi-agent conversation runs; pick the format to match the decision (converge vs diverge, judge vs consensus).  
  _(source: Deliberation Structures)_
- FISHBOWL: a small inner circle actively discusses while a larger outer circle observes; an empty chair lets an observer swap in, so perspectives rotate through the conversation.  
  _(source: Deliberation Structures)_
- SWARM SIMULATION is the largest deliberation scale: instead of a few debating agents, run thousands of persona-agents with independent personalities, long-term memory, and behavioral logic that interact and socially evolve to reveal EMERGENT outcomes.  
  _(source: Swarm Simulation (MiroFish/OASIS))_

## Agent Roles & Instructions
- Multi-agent roles: instantiate perspective-A agent, perspective-B agent, and a Moderator that steers and injects complementary information.  
  _(source: Co-STORM (Stanford/Yale))_
- Stanford academic framing: rewrite every surviving idea as a research question and flag its citation needs, so STORM's grounded-writing stage has concrete claims to ground.  
  _(source: Brainstorm Layer (custom))_
- COUNCIL roles: N peer members + 1 chairman; optionally assign adversarial roles to peers to prevent echo chambers.  
  _(source: Deliberation Structures)_
- DEBATE roles: proponent, opponent, and (optional) judge; assign adversarial personas to force genuine opposition and surface the premise left unsaid.  
  _(source: Deliberation Structures)_
- FISHBOWL fit: it lives in the DIVERGENT phase (Kaner's Diamond) — surface many perspectives before converging; pairs naturally with the Brainstorm Layer's perspective explosion.  
  _(source: Deliberation Structures)_

## Workflow Steps
- Perspective discovery: survey existing articles on similar topics to enumerate diverse viewpoints before asking questions.  
  _(source: STORM (Stanford OVAL))_
- Perspective-guided question asking: each discovered persona asks questions from its own angle (beats naive 'ask 30 questions').  
  _(source: STORM (Stanford OVAL))_
- Simulated conversation: a writer-persona converses with a topic-expert grounded on trusted internet sources, updating understanding and asking follow-ups.  
  _(source: STORM (Stanford OVAL))_
- Curation to outline: synthesize the collected Q&A into a structured outline (the core pre-writing artifact).  
  _(source: STORM (Stanford OVAL))_
- Grounded writing stage: expand the outline into a full article with inline citations to the retrieved references.  
  _(source: STORM (Stanford OVAL))_
- Collaborative discourse protocol: a turn-management policy decides which agent speaks next to keep the multi-agent conversation productive.  
  _(source: Co-STORM (Stanford/Yale))_
- Human-in-the-loop steering: agents ask questions on the user's behalf; the user mostly observes and can inject direction at any turn.  
  _(source: Co-STORM (Stanford/Yale))_
- Problem reframing: restate the prompt 5 ways before ideating — invert it, generalize it, tightly constrain it, analogize it to another domain, and reduce it to first principles.  
  _(source: Brainstorm Layer (custom))_
- Perspective explosion: generate wildly diverse personas beyond Co-STORM's expert A/B — adversary, novice, historian, futurist, contrarian, cross-domain outsider. These feed STORM's perspective-discovery step.  
  _(source: Brainstorm Layer (custom))_
- Divergent idea storm: run SCAMPER + random-stimulus + 'worst possible idea' passes to force quantity and novelty. No filtering yet — quantity first.  
  _(source: Brainstorm Layer (custom))_
- Unknown-unknown probes: invert Co-STORM's mind map — explicitly ask 'what would we NOT think to ask?' to seed the multi-agent discourse with blind spots.  
  _(source: Brainstorm Layer (custom))_
- Convergence gate: cluster and dedupe ideas, then score each by novelty × feasibility × fit; only survivors pass to STORM as perspectives + seed questions.  
  _(source: Brainstorm Layer (custom))_
- COUNCIL (3-stage): each agent answers the prompt independently, then anonymously ranks the other answers, then a chairman synthesizes one final response from the ranked set.  
  _(source: Deliberation Structures)_
- JURY/PANEL: 3+ judge agents independently evaluate, surface disagreement, run deliberation rounds toward consensus; compare jury accuracy vs a single judge.  
  _(source: Deliberation Structures)_
- DEBATE (MAD): 2+ debaters take positions and argue over N rounds with access to debate history; resolve via an LLM judge or self-consistency majority vote.  
  _(source: Deliberation Structures)_
- FISHBOWL turn policy: seed the inner circle with a few agents, keep 1-2 empty chairs; an outer-circle agent may take an empty chair (an inner agent then rotates out), continuously refreshing viewpoints.  
  _(source: Deliberation Structures)_
- Seed -> digital world: extract seed information (news, policy drafts, financial signals, or a story) and auto-construct a high-fidelity parallel world to run the crowd inside.  
  _(source: Swarm Simulation (MiroFish/OASIS))_
- Graph building: build a GraphRAG knowledge graph with individual + collective memory injection, then dynamic temporal memory updates as the simulation runs.  
  _(source: Swarm Simulation (MiroFish/OASIS))_
- Environment setup: extract entity relationships from the seed, auto-generate agent personas, and inject per-agent configuration before simulating.  
  _(source: Swarm Simulation (MiroFish/OASIS))_

## Capabilities
- Dynamic mind map: organize uncovered information into a live, growing mind map as the discourse proceeds.  
  _(source: Co-STORM (Stanford/Yale))_
- Report-as-takeaways: generate a comprehensive final report synthesized from the mind map.  
  _(source: Co-STORM (Stanford/Yale))_
- FISHBOWL variants: open (any observer joins anytime), closed (fixed inner group, rotate on a timer), tap-out (observer taps an inner agent to swap), silent (outer circle only observes and annotates).  
  _(source: Deliberation Structures)_
- God's-eye variable injection: dynamically inject variables mid-simulation to deduce alternative future trajectories ('what-if' rehearsal at zero real-world risk).  
  _(source: Swarm Simulation (MiroFish/OASIS))_
- ReportAgent: a post-simulation agent with a rich toolset that deeply interacts with the settled world to produce a prediction report (parallels Co-STORM's report-as-takeaways).  
  _(source: Swarm Simulation (MiroFish/OASIS))_
- Deep interaction: chat with any individual agent in the simulated world, or with the ReportAgent, to interrogate why an outcome emerged.  
  _(source: Swarm Simulation (MiroFish/OASIS))_

## Evaluation & Metrics
- Eval via FreshWiki dataset + rubric metrics: ROUGE, entity recall, heading entity recall, outline quality.  
  _(source: STORM (Stanford OVAL))_
- Eval via WildSeek dataset (real info-seeking goals); 70% of participants prefer Co-STORM over a search engine, 78% over a RAG chatbot.  
  _(source: Co-STORM (Stanford/Yale))_
- JURY voting rules: majority (ties default to reject/low-confidence), unanimous (accept only if all concur), or reliability-weighted aggregation (weight each juror by an estimated reliability score).  
  _(source: Deliberation Structures)_

## Failure Modes & Guards
- Known failure modes: source bias transfer and over-association of unrelated facts; guard against both when curating.  
  _(source: STORM (Stanford OVAL))_
- Limitations: higher latency (utterance-intent decision + mind-map update), weak tailoring to user prior knowledge, English-centric.  
  _(source: Co-STORM (Stanford/Yale))_
- Handoff contract: BRAINSTORM diverges -> convergence gate filters -> STORM/Co-STORM grounds & writes. Never let divergent noise reach the writing stage unfiltered (avoids over-association of unrelated facts).  
  _(source: Brainstorm Layer (custom))_
- JURY caveat: correlate panel disagreement with question difficulty; use adaptive stopping (e.g., stability detection) so deliberation ends when consensus dynamics stabilize instead of running fixed rounds.  
  _(source: Deliberation Structures)_
- DEBATE caveat: LLMs anchor to initial positions ('hung jury' effect) and heavy RLHF alignment makes them rigid; explicitly prompt open-mindedness and prefer flexible models for mind-changing.  
  _(source: Deliberation Structures)_
- Swarm caveat: high token/compute cost — start with short runs (e.g. <40 rounds) before scaling; simulation fidelity depends on persona and memory quality.  
  _(source: Swarm Simulation (MiroFish/OASIS))_

## Invent (gaps not covered by any source)
- INVENT: no existing part covers "tiers" — design custom.
- INVENT: no existing part covers "verdicts" — design custom.
- INVENT: no existing part covers "feeding" — design custom.

## Provenance
Every part above was pulled off the GitHub/paper shelf, decomposed, and matched
to this idea. See ../report.html for the full Parts Catalog and Ideas-vs-Parts
analysis, and RECIPE.md for lift/adapt/invent classification.
