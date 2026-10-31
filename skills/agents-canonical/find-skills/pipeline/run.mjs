// pipeline/run.mjs
// Orchestrates the 7-stage find-skills harvest-and-synthesize pipeline.
//
//   node pipeline/run.mjs --topic "video editor" \
//     --idea "I need trim, caption-burn, frame-export, audio-extract, batch"
//
// Stages: EXPLODE -> HARVEST(multi-shelf) -> VERIFY -> DECOMPOSE -> SYNTHESIZE
//         -> RENDER -> SCAFFOLD

import { argv } from "node:process";
import {
  skillsFind, parseFind, ghSearchRepos, fetchReadme, githubMeta, dryRun,
  dedupeCandidates, trustFor, ensureDir, write, clean, TRUST,
} from "./lib.mjs";
import { explode } from "./explode.mjs";
import { decompose } from "./decompose.mjs";
import { synthesize } from "./synthesize.mjs";
import { renderHTML } from "./render.mjs";
import { emitScaffold } from "./scaffold.mjs";
import { matchSeeds, seedToCandidatesAndParts } from "./seeds.mjs";

function getArg(name) {
  const i = argv.indexOf(name);
  return i >= 0 ? argv[i + 1] : null;
}

async function main() {
  const topic = getArg("--topic") || "rewind session history";
  const idea = getArg("--idea") || getArg("--idea-file")
    ? (getArg("--idea") || (await (await import("node:fs/promises")).readFile(getArg("--idea-file"), "utf8")))
    : "rewind an agent session by snapshotting its state, with a cross-session diff view";
  const outDir = "out";

  console.log(`\n=== find-skills pipeline: "${topic}" ===\n`);

  // STAGE 1 — EXPLODE
  const queries = explode(topic);
  const maxQ = parseInt(getArg("--max-queries") || "12", 10);
  const runQueries = queries.slice(0, maxQ);
  console.log(`[1/7] EXPLODE: ${queries.length} queries (running ${runQueries.length})`);
  runQueries.forEach((q) => console.log("   -", q));

  // STAGE 1.5 — SEED (named systems inject curated repos/papers + real parts)
  const seeds = matchSeeds(`${topic} ${idea}`);
  const seedParts = [];
  const seedCandidates = [];
  for (const s of seeds) {
    const { candidates, parts } = seedToCandidatesAndParts(s);
    seedCandidates.push(...candidates);
    seedParts.push(...parts);
    console.log(`   SEED: ${s.label} -> ${candidates.length} sources, ${parts.length} curated parts`);
  }

  // STAGE 2 — HARVEST (multi-shelf)
  const seedsOnly = argv.includes("--seeds-only");
  console.log(`\n[2/7] HARVEST: ${seedsOnly ? "seeds only (network skipped)" : "skills registry + all GitHub"}`);
  let candidates = [...seedCandidates];
  if (!seedsOnly) for (const q of runQueries) {
    const raw = await skillsFind(q);
    for (const c of parseFind(raw, q)) candidates.push({ ...c, shelf: "skills" });
    const repos = await ghSearchRepos(q, 8);
    for (const r of repos) {
      candidates.push({
        pkg: r.nameWithOwner,
        installs: null,
        stars: r.stargazerCount,
        query: q,
        link: `https://github.com/${r.nameWithOwner}`,
        shelf: "github",
        description: r.description,
        pushedAt: r.pushedAt,
      });
    }
  }
  candidates = dedupeCandidates(candidates);
  console.log(`   pulled ${candidates.length} candidate repos`);

  // STAGE 3 — VERIFY (caveat pass)
  console.log(`\n[3/7] VERIFY: caveat pass on every source`);
  for (const c of candidates) {
    if (c.seeded) continue; // curated seeds are pre-trusted (repo/paper provenance)
    const ownerRepo = c.pkg.split("@")[0];
    const meta = await githubMeta(ownerRepo);
    c.stars = c.stars ?? meta.stargazerCount ?? 0;
    c.pushedAt = c.pushedAt ?? meta.pushedAt ?? null;
    c.missing = !!meta.missing;
    if (c.shelf === "skills") {
      const dr = await dryRun(c.pkg);
      c.claimOk = dr.ok;
      c.notes = dr.stdout.slice(0, 200);
    }
    // Exclude logic
    let reason = "";
    if (c.missing) { c.trust = TRUST.EXCLUDED; reason = "repo 404 — dead"; }
    else if (c.shelf === "skills" && c.claimOk === false) { c.trust = TRUST.EXCLUDED; reason = "claim mismatch (dry-run found no such skill) — clickbait"; }
    else c.trust = trustFor(c.installs ?? 0, c.stars, false);
    c.reason = reason;
    if (c.trust === TRUST.EXCLUDED) console.log(`   EXCLUDE ${c.pkg}: ${reason}`);
  }
  const alive = candidates.filter((c) => c.trust !== TRUST.EXCLUDED);
  console.log(`   ${alive.length} survived (${seedCandidates.length} seeded)`);

  // STAGE 4 — DECOMPOSE (parts bin) — start with curated seed parts
  console.log(`\n[4/7] DECOMPOSE: pulling parts out of every surviving repo`);
  let parts = [...seedParts];
  for (const c of alive) {
    if (c.seeded) continue; // seed parts already curated; papers have no gh README
    const text = await fetchReadme(c.pkg.split("@")[0]);
    const ps = decompose(c.pkg, text).map((p) => ({ ...p, trust: c.trust }));
    parts.push(...ps);
  }
  console.log(`   extracted ${parts.length} parts (${seedParts.length} curated)`);

  // STAGE 5 — SYNTHESIZE (idea vs whole parts set)
  console.log(`\n[5/7] SYNTHESIZE: running idea against ${parts.length} parts`);
  const synth = synthesize(idea, parts);
  console.log(`   idea wants ${synth.wanted.length} parts; ${synth.recipe.invent.length} gap(s) to invent`);

  // STAGE 6 — RENDER
  console.log(`\n[6/7] RENDER: writing out/report.html`);
  await ensureDir(outDir);
  const branches = {};
  for (const c of candidates) (branches[c.query] ||= []).push(c);
  const html = renderHTML({ topic, idea, queries: runQueries, candidates, parts, synth, branches });
  await write(`${outDir}/report.html`, html);

  // STAGE 7 — SCAFFOLD
  console.log(`\n[7/7] SCAFFOLD: emitting custom build`);
  const scaffoldDir = await emitScaffold(outDir, { topic, idea, synth });
  console.log(`   wrote ${scaffoldDir}`);

  console.log(`\n=== DONE ===\n  report:  out/report.html\n  build:   ${scaffoldDir}\n`);
}

main().catch((e) => { console.error(e); process.exit(1); });
