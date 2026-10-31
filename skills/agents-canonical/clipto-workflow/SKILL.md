---
name: clipto-workflow
description: Run Clipto's evidence-workflow against Vinny's own library. Use when a task needs quoted, timestamped evidence from his recordings/media — interview organizing, pain-point mining, testimonial pulls, b-roll matching, viewpoint comparison, "find where users get stuck" reports, or any "find the moment where…" ask. Carries the complete 16-template Clipto prompt pack (extracted verbatim from the desktop app v0.9.291 — 15 active + 1 disabled in Clipto's own source) and its 4-step retrieval funnel (scope sources → locate files → search content → pull full transcript). Backend is local: Spotlight/find/search over his Mac + Landing Pad (8787) / capture-door (8941) media — no Clipto account, no cloud.
---

# Clipto Workflow — evidence plays on Vinny's own library

Extracted from Clipto (clipto.com) desktop app v0.9.291 via REA (ASAR + gRPC protos + MCP server code).
Full receipts + definitive library: ~/Documents/00_INBOX/clipto-extraction/ (VERIFY-NOTES.md, clipto-prompt-library.md/.json, clipto-prompt-registry-source.txt, evidence-proto/).

## The law of the format (why their prompts work)

Every play returns an **evidence triple**: exact quote · timestamp · source link — plus:
- Missing information gets **separated and flagged**, never inferred.
- Hard guardrails close each prompt ("Don't score the candidate…", "don't invent frequency", "flag uncertain edits").
- One independent evidence target per search query (2–6 content words, not sentences).
- Same factual structure when comparing people/candidates — never rank, never infer protected traits.

Adapt to Vinny's library: "Clipto link" → a real path or markdeep anchor to his file; "timestamp" → media timestamp from the transcript/asset.

## The 4-step funnel (their MCP tool order — steal the order)

1. **Scope** (`select_sources` equivalent): pick the folder(s) he means. Multiple matches → ask, never silently search all.
2. **Locate** (`locate_files`): filename lookup or one-shot folder listing. Never wildcard-guess; call once.
3. **Search** (`search_memory`): content search, ranked candidates, one target per query, multiple folders = one batched call.
4. **Pull** (`get_transcription`): full text/time-aligned content of the chosen file, then run the play's prompt over it.

On this Mac: `mdfind`/`find` for 1–2, then read files directly (text exports) — step 3 collapses to grepping transcripts/notes; media without transcripts gets transcribed first.

## The 16 plays (VERBATIM from the extracted JSON — swap {placeholders} and "my Clipto library" → "Vinny's library")

### Create

1. **Match B-roll to my script** — needs: A script · you get: A complete video with matched B-roll

```text
Create a complete video using this A-roll or voiceover in my Clipto library: {name the recording}. Match B-roll to this script: {paste your script}, following {describe the look you want}. Use the strongest clip for each beat, keep it in sync, and stay on the main track when no good match exists. Export the finished video with source timestamps and Clipto links.
```

2. **Edit a podcast for release** — needs: A full-length recording · you get: A polished audio or video episode

```text
Edit this full podcast recording in my Clipto library: {name the recording}. Shape it around {main topic or goal} and deliver it as {audio or video}. Remove filler, false starts, repetition, long pauses, interruptions, and off-topic sections while preserving meaning and natural pacing. Clean the audio, smooth video cuts when needed, export the complete episode, and flag uncertain edits.
```

3. **Turn a script into a video** — needs: A folder, shoot, or event · you get: a complet video matched to your script

```text
Use Clipto to find matching footage and assemble it into a video.Here’s my script:{paste or replace with your own script}
```

4. **Build a footage log** — needs: A folder of media files · you get: An Excel log of every usable moment (DISABLED in Clipto's app source — kept verbatim; their site still lists it)

```text
Create a footage log for all media currently indexed and analyzed in my Clipto library. Use Clipto only—do not search or scan local folders. Export a .csv with one row per useful segment, including source path, duration, in/out timecodes, description, spoken topic or quote, quality or privacy issues, recommended use, and Clipto link. Mark media with no usable footage or access issues reported by Clipto.
```

### Research

5. **Find the quote I remember** — needs: A half-remembered line · you get: Exact quotes with sources

```text
Search my Clipto library for reliable moments that match this remembered quote or idea: {what you remember}. Return the closest matches with the exact spoken words, source, timestamp, and Clipto link, plus enough surrounding context to understand each one. Rank closer matches first. If nothing is convincing, tell me rather than turning a loose similarity into an exact quote.
```

6. **Compare viewpoints** — needs: A topic or question · you get: Grouped viewpoints with quotes

```text
Compare how people in my Clipto library discuss {topic or question}. Group the main viewpoints, show where they agree or differ, and support each point with a short quote, source, timestamp, and Clipto link. Keep the speaker’s original meaning and note when context is limited. Don’t force the recordings into opposing sides if the evidence is more nuanced.
```

7. **Build a lesson evidence pack** — needs: A lesson topic · you get: An ordered clip pack with notes

```text
Build a lesson evidence pack from my Clipto library for {lesson topic}. Choose a small set of clear, useful moments that explain the key ideas or provide strong examples. For each one, include a short teaching note, the source, timestamp, and Clipto link. Organize them in a sensible learning order and identify important points the library does not cover well.
```

8. **Trace how an idea changed** — needs: An idea or project name · you get: A dated change timeline

```text
Trace how {idea or project} changed across the recordings in my Clipto library. Build a chronological account of the important shifts, decisions, and unresolved questions. Support every step with the source, timestamp, Clipto link, and a short explanation of what changed. Use dates only when the recording or file metadata makes them clear, and flag gaps instead of guessing.
```

### Product

9. **Find customer pain points** — needs: Interviews or customer calls · you get: Grouped pain points with quotes

```text
Find reliable moments in my Clipto library where customers describe problems related to {product or workflow}. Group similar pain points and show what triggered each problem, how it affected the customer, and any workaround they mentioned. Include a short quote, source, timestamp, and Clipto link for every finding. Separate repeated patterns from one-off comments, and don’t invent frequency.
```

10. **Find product UI footage** — needs: A feature or flow name · you get: Screen-recording moments with timestamps

```text
Find screen recordings in my Clipto library that clearly show {feature or user flow}. Return the strongest moments with the source, timestamp, Clipto link, and a short description of what is visible on screen. Prefer clean, reviewable coverage and point out interruptions, outdated UI, or missing steps. If the product state is unclear, flag it rather than assuming.
```

11. **Build testimonial evidence** — needs: A product, benefit, or outcome · you get: Quotable testimonials with context

```text
Find strong testimonial moments in my Clipto library about {product, benefit, or outcome}. Include the exact quote, source, timestamp, Clipto link, and enough surrounding context to preserve what the customer meant. Highlight specific results or before-and-after details when they are actually stated. Exclude vague praise and flag any quote that would be misleading without additional context.
```

12. **Find where users get stuck** — needs: Interviews, support calls, and screen recordings · you get: A friction report with source clips

```text
Find moments in interviews, support calls, and screen recordings where users struggle with {feature or flow}. Group repeated friction points and show what the user tried, what blocked them, and any workaround, with source, timestamp, and Clipto link. Separate product confusion from technical issues or outdated UI, and don’t invent frequency.
```

### HR

13. **Organize interview evidence** — needs: One recorded interview · you get: Answers grouped by topic

```text
Organize the interview evidence in my Clipto library for {candidate or interview}. Group the candidate’s answers by the role-related topics I asked about and include a short quote, source, timestamp, and Clipto link for each point. Separate direct evidence from missing information. Don’t score the candidate, rank them, infer personal traits or protected characteristics, or make the hiring decision.
```

14. **Compare answers to one role question** — needs: One interview question · you get: A same-structure answer comparison

```text
Compare the recorded answers to this role-related question: {paste the interview question}. Summarize the approaches, examples, and stated experience in each answer, with a short quote, source, timestamp, and Clipto link. Use the same factual structure for everyone. Don’t score or rank candidates, infer personal traits or protected characteristics, or treat missing evidence as a weakness.
```

15. **Compare candidates against a rubric** — needs: Candidates and rubric criteria · you get: A side-by-side evidence matrix

```text
Organize recorded interview evidence for {candidates} against this role rubric: {criteria}. Use the same factual structure for everyone. For each criterion, include relevant quotes, sources, timestamps, and Clipto links, and mark missing evidence. Don’t score or rank candidates, infer personal traits or protected characteristics, or make the hiring decision.
```

16. **Find what we told a candidate** — needs: A policy, process, or offer term · you get: A sourced record of policies and commitments

```text
Find recorded moments where our team discussed {policy, process, or offer terms} with {candidate}. Capture the exact wording, speaker, context, source, timestamp, Clipto link, commitments, open questions, and later changes or contradictions. Treat this as a communication record, not current policy or legal guidance, and verify important points against the latest official documents.
```

## Bonus taxonomy (their 18 server summary templates — replicate as prompt recipes)
Brief · Detailed · By-Speaker · Daily Standup · Group Meeting · Brainstorming · Job Interview (candidate/interviewer) · Casual Discussion · 1-on-1 · Meeting Discussion · Journalistic Research Interview · Medical · Lecture · Course (professor/student) · Podcast · Investor Meeting.
Standard pipeline equivalent: record/import → transcribe → correct → post-process → summarize (segment or whole) → file into folders/tags/smart collections.
