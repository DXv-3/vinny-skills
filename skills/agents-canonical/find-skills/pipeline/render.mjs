// pipeline/render.mjs
// Stage 6: build the exhaustive website report (out/report.html).
// Sections: coverage header, sitemap, branches, parts catalog, ideas-vs-parts,
// comparison tables, creative picks, custom-build recipe, gaps, top picks.

import { PART_TYPES, TRUST, nowStamp } from "./lib.mjs";

function esc(s) {
  return String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

export function renderHTML({ topic, idea, queries, candidates, parts, synth, branches }) {
  const cov = `
  <section class="coverage">
    <h2>Coverage</h2>
    <ul>
      <li>Topic: <b>${esc(topic)}</b></li>
      <li>Idea: <b>${esc(idea)}</b></li>
      <li>Queries run (explode tree): <b>${queries.length}</b></li>
      <li>Candidate repos pulled: <b>${candidates.length}</b></li>
      <li>Parts extracted from corpus: <b>${parts.length}</b></li>
      <li>Parts the idea wants: <b>${synth.wanted.length}</b></li>
      <li>Generated: ${esc(nowStamp())}</li>
    </ul>
  </section>`;

  const sitemap = `
  <section class="sitemap">
    <h2>Sitemap</h2>
    <ol>
      <li><a href="#coverage">Coverage</a></li>
      <li><a href="#branches">Branches (candidate repos)</a></li>
      <li><a href="#parts">Parts Catalog (${parts.length})</a></li>
      <li><a href="#ideas">Ideas vs Parts</a></li>
      <li><a href="#compare">Comparison Tables</a></li>
      <li><a href="#creative">Creative Picks</a></li>
      <li><a href="#recipe">Custom Build Recipe</a></li>
      <li><a href="#gaps">Gaps</a></li>
    </ol>
  </section>`;

  const branchSec = `
  <section id="branches">
    <h2>Branches (candidate repos pulled off the shelf)</h2>
    ${candidates.map((c) => `
      <div class="card ${c.trust === "EXCLUDED" ? "excluded" : ""}">
        <h3>${esc(c.pkg)} ${c.trust === "EXCLUDED" ? "— EXCLUDED" : ""}</h3>
        <p>installs: ${esc(c.installs ?? "?")} · stars: ${esc(c.stars ?? "?")} ·
           trust: <b>${esc(c.trust)}</b> · shelf: ${esc(c.shelf)}</p>
        <p>${esc(c.reason || "survived caveat pass")}</p>
        ${c.link ? `<a href="${esc(c.link)}">${esc(c.link)}</a>` : ""}
      </div>`).join("")}
  </section>`;

  const partsByType = {};
  for (const t of PART_TYPES) partsByType[t] = parts.filter((p) => p.type === t);
  const partsSec = `
  <section id="parts">
    <h2>Parts Catalog (${parts.length})</h2>
    ${PART_TYPES.map((t) => `
      <h3>${t} (${partsByType[t].length})</h3>
      <ul>
        ${partsByType[t].map((p) => `
          <li><b>[${esc(p.source)}]</b> ${esc(p.text)}
            <span class="tag ${esc(p.trust)}">${esc(p.trust)}</span></li>`).join("")}
      </ul>`).join("")}
  </section>`;

  const ideasSec = `
  <section id="ideas">
    <h2>Ideas vs Parts</h2>
    <p>Our idea run against the whole Parts Index. Relationship per part:</p>
    <ul>
      ${synth.scored.filter((p) => p.rel !== "CONFIRM").slice(0, 60).map((p) => `
        <li><span class="rel ${esc(p.rel)}">${esc(p.rel)}</span>
          <b>[${esc(p.source)}]</b> ${esc(p.text)}
          <span class="score">score ${p.score.toFixed(2)}</span></li>`).join("")}
    </ul>
    ${synth.contradicted.length ? `
      <h3>Contradictions (reconcile before building)</h3>
      <ul>${synth.contradicted.map((p) => `<li><b>[${esc(p.source)}]</b> ${esc(p.text)}</li>`).join("")}</ul>` : ""}
  </section>`;

  const compareSec = `
  <section id="compare">
    <h2>Comparison Table (top wanted parts)</h2>
    <table>
      <tr><th>Source</th><th>Type</th><th>Part</th><th>Trust</th><th>Score</th><th>Rel</th></tr>
      ${synth.wanted.slice(0, 30).map((p) => `
        <tr><td>${esc(p.source)}</td><td>${esc(p.type)}</td><td>${esc(p.text.slice(0, 80))}</td>
          <td>${esc(p.trust)}</td><td>${p.score.toFixed(2)}</td><td>${esc(p.rel)}</td></tr>`).join("")}
    </table>
  </section>`;

  const creativeSec = `
  <section id="creative">
    <h2>Creative / Unconventional Picks</h2>
    <ul>${synth.wanted.filter((p) => p.trust === "LOW").slice(0, 15)
      .map((p) => `<li><b>[${esc(p.source)}]</b> ${esc(p.text)} — novel angle, low install base.</li>`).join("")}</ul>
  </section>`;

  const recipeSec = `
  <section id="recipe">
    <h2>Custom Build Recipe</h2>
    <h3>LIFT (take as-is)</h3>
    <ul>${synth.recipe.lift.map((p) => `<li><b>[${esc(p.source)}]</b> ${esc(p.text)}</li>`).join("")}</ul>
    <h3>ADAPT (take + modify)</h3>
    <ul>${synth.recipe.adapt.map((p) => `<li><b>[${esc(p.source)}]</b> ${esc(p.text)}</li>`).join("")}</ul>
    <h3>INVENT (build custom — gaps in corpus)</h3>
    <ul>${synth.recipe.invent.map((g) => `<li>${esc(g)}</li>`).join("")}</ul>
  </section>`;

  const gapsSec = `
  <section id="gaps">
    <h2>Gaps</h2>
    <p>Idea concepts with no covering part across the entire corpus:</p>
    <ul>${synth.recipe.invent.map((g) => `<li>${esc(g)}</li>`).join("")}</ul>
    <p>To fill a gap: <code>npx skills init my-custom-part</code></p>
  </section>`;

  return `<!doctype html><html><head><meta charset="utf-8">
  <title>Find-Skills Exhaustive Report — ${esc(topic)}</title>
  <style>
    body{font:14px/1.5 system-ui,sans-serif;max-width:1000px;margin:auto;padding:2rem;color:#111}
    h2{border-bottom:2px solid #222;margin-top:2rem}
    .card{border:1px solid #ccc;border-radius:8px;padding:.75rem;margin:.5rem 0}
    .excluded{opacity:.6;border-style:dashed}
    .tag{padding:1px 6px;border-radius:4px;font-size:11px}
    .HIGH{background:#cfe9cf}.MED{background:#fff3c4}.LOW{background:#ffd9c4}.EXCLUDED{background:#eee}
    .rel{padding:1px 6px;border-radius:4px;font-size:11px;margin-right:6px}
    .EXTEND{background:#cfe9cf}.COMBINE{background:#d9e4ff}.CONFIRM{background:#eee}.CONTRADICT{background:#ffc4c4}
    .score{color:#666;font-size:11px;margin-left:6px}
    table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:4px 8px;text-align:left}
    code{background:#f4f4f4;padding:1px 4px;border-radius:3px}
    a{color:#0a58ca}
  </style></head><body>
    <h1>Find-Skills — Exhaustive Parts-Bin Report</h1>
    ${cov}${sitemap}${branchSec}${partsSec}${ideasSec}${compareSec}${creativeSec}${recipeSec}${gapsSec}
  </body></html>`;
}
