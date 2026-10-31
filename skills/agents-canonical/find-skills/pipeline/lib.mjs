// pipeline/lib.mjs
// Shared types + small utilities for the find-skills harvest-and-synthesize engine.
//
// Mental model: GitHub/skills.sh is a CORPUS OF PARTS, not a store of packages.
// We harvest parts across the whole corpus, run the user's IDEA through them,
// and emit a CUSTOM BUILD (scaffold), not a repo install.

import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { mkdir, writeFile, readFile, rm } from "node:fs/promises";
import { join } from "node:path";

export const exec = promisify(execFile);

export const PART_TYPES = [
  "feature",       // a capability a repo exposes (we cherry-pick these)
  "prompt",        // reusable system instructions / phrasing
  "workflow",      // ordered steps / decision trees / loops
  "table",         // reference taxonomies / matrices / mappings
  "snippet",       // code / config / template
  "mental-model",  // underlying pattern/idea independent of implementation
  "edge-case",     // failure / ambiguity / limit handling
];

export const TRUST = {
  HIGH: "HIGH",
  MED: "MED",
  LOW: "LOW",
  EXCLUDED: "EXCLUDED",
};

// --- Shelf B: search ALL of GitHub (not just the skills registry) ---
// Any repo is a box of features we can pull parts from.
export async function ghSearchRepos(query, limit = 20) {
  try {
    const { stdout } = await exec("gh", [
      "search", "repos", query,
      "--limit", String(limit),
      "--json", "fullName,stargazerCount,description,updatedAt,pushedAt",
    ], { maxBuffer: 1024 * 1024 * 16 });
    const arr = JSON.parse(stdout);
    return arr.map((r) => ({ ...r, nameWithOwner: r.fullName }));
  } catch (e) {
    return [];
  }
}

// Fetch a repo's README (or SKILL.md) text for decomposition.
export async function fetchReadme(ownerRepo) {
  for (const path of ["SKILL.md", "README.md", "docs/README.md"]) {
    try {
      const { stdout } = await exec("gh", [
        "api", `repos/${ownerRepo}/contents/${path}`,
        "--jq", ".content",
      ], { maxBuffer: 1024 * 1024 * 16 });
      if (stdout && stdout.trim() && stdout.trim() !== "null") {
        // GitHub returns base64; decode safely
        return Buffer.from(stdout.trim().replace(/\s/g, ""), "base64").toString("utf8");
      }
    } catch { /* try next path */ }
  }
  return "";
}

// Run `npx skills find <q>` and return raw stdout. Never throws on non-zero;
// we capture stderr too so a CLI quirk doesn't kill the pipeline.
export async function skillsFind(query) {
  try {
    const { stdout } = await exec("npx", ["-y", "skills", "find", query], {
      maxBuffer: 1024 * 1024 * 16,
    });
    return stdout;
  } catch (e) {
    return e.stdout || "";
  }
}

// Parse `npx skills find` output into candidate rows.
// Lines look like:  owner/repo@skill  12.3K installs
//                   └ https://skills.sh/owner/repo/skill
export function parseFind(raw, query) {
  const out = [];
  const lines = stripAnsi(raw).split("\n");
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^\s*([\w.-]+\/[\w.-]+@[\w.-]+)\s+([\d.]+K?)\s*installs/i);
    if (!m) continue;
    const pkg = m[1];
    const installs = parseCount(m[2]);
    const link = (lines[i + 1] || "").match(/skills\.sh\/(\S+)/)?.[0] || "";
    out.push({ pkg, installs, query, link: `https://${link}` });
  }
  return out;
}

export function parseCount(s) {
  s = s.trim().toLowerCase();
  if (s.endsWith("k")) return Math.round(parseFloat(s) * 1000);
  return parseInt(s, 10) || 0;
}

// Strip ANSI color escape codes (skills CLI colorizes even when piped).
export function stripAnsi(s) {
  return s.replace(/\u001b\[[0-9;]*m/g, "");
}

// Fetch GitHub stars + maintenance for a source repo.
export async function githubMeta(ownerRepo) {
  try {
    const { stdout } = await exec("gh", [
      "repo", "view", ownerRepo,
      "--json", "stargazerCount,pushedAt,updatedAt,description",
    ], { maxBuffer: 1024 * 1024 });
    return JSON.parse(stdout);
  } catch {
    return { stargazerCount: 0, pushedAt: null, updatedAt: null, description: "", missing: true };
  }
}

// Dry-run an install to confirm the skill actually resolves (claim-vs-reality).
export async function dryRun(pkg) {
  try {
    const { stdout } = await exec("npx", ["-y", "skills", "add", pkg, "--dry-run"], {
      maxBuffer: 1024 * 1024 * 16,
    });
    const dead = /No matching skills found/i.test(stripAnsi(stdout));
    return { ok: !dead, stdout };
  } catch (e) {
    return { ok: false, stdout: e.stdout || e.message || "" };
  }
}

export function dedupeCandidates(list) {
  const map = new Map();
  for (const c of list) {
    const prev = map.get(c.pkg);
    if (!prev) { map.set(c.pkg, { ...c, queries: [c.query] }); continue; }
    if (!prev.queries.includes(c.query)) prev.queries.push(c.query);
  }
  return [...map.values()];
}

export function trustFor(installs, stars, missing) {
  if (missing) return TRUST.EXCLUDED;
  if (installs >= 1000 && stars >= 100) return TRUST.HIGH;
  if (installs >= 100 || stars >= 100) return TRUST.MED;
  return TRUST.LOW;
}

export async function ensureDir(p) { await mkdir(p, { recursive: true }); }
export async function write(p, data) {
  await ensureDir(join(p, ".."));
  await writeFile(p, data);
}
export async function read(p) { return readFile(p, "utf8"); }
export async function clean(p) { await rm(p, { recursive: true, force: true }); }

export function nowStamp() {
  return new Date().toISOString().replace("T", " ").slice(0, 19);
}
