# Archive — Historical Audit & Inventory Records

These are **point-in-time historical records**, preserved verbatim for the audit
trail. They describe the repository as it stood at the release named in each
section heading and are **not maintained**. For the current state of the project,
see the root reference files (`model-guide.md`, `image-models.md`, `vocab.md`,
`prompt-examples.md`, the `skills/` sub-skills) and `CHANGELOG.md`.

This file consolidates four formerly-separate documents (folded in during the
v3.8.2 docs-hygiene pass):

| Section | Original path (removed) | Release | First committed |
|---------|-------------------------|---------|-----------------|
| v3.0.0 — Release Audit | `docs/archive/v3.0.0/v3-audit-report.md` | v3.0.0 | 2026-04-06 |
| v3.0.0 — Migration Inventory | `docs/archive/v3.0.0/v3-inventory.md` | v3.0.0 | 2026-04-06 |
| v3.4.0 — PDF Integration Audit | `docs/pdf-audit/AUDIT-REPORT.md` | v3.4.0 | 2026-04-18 |
| v3.6.0 — PDF Integration Audit | `docs/pdf-audit/AUDIT-REPORT-v3.6.0.md` | v3.6.0 | 2026-04-25 |

The original per-release rendered PDFs remain recoverable from their git tags
(e.g. `git show v3.6.0:docs/user-guide/USER-GUIDE.pdf`).

---


<!-- ============================================================ -->
# v3.0.0 — Release Audit

> Archived verbatim from `docs/archive/v3.0.0/v3-audit-report.md` (release v3.0.0). Historical — not maintained.

---

# v3.0.0 Audit Report

**Date:** 2026-04-06
**Auditor:** Claude Opus 4.6 (automated)
**Result:** ALL CHECKS PASSED (0 Critical, 0 Warning after fixes)

---

## 5A. File Reference Integrity — PASS

All file paths referenced in sub-skills and dispatcher resolve correctly:
- `../shared/negative-constraints.md` — 14 sub-skills, all valid
- `MODELS-DEEP-REFERENCE.md` — exists
- `templates/` — all 10 templates present
- Root references (`model-guide.md`, `image-models.md`, `vocab.md`, `prompt-examples.md`, `photodump-presets.md`) — all exist
- Cross-skill references — all skill directories exist with SKILL.md

## 5B. Version Consistency — PASS

- `version: 2.0.2` — 0 results (correct)
- `version: 3.0.0` — 21 files (correct: 1 root + 1 dispatcher + 18 sub-skills + 1 MODELS-DEEP-REFERENCE)
- README badge — `version-3.0.0-blue`
- README footer — `v3.0.0 (updated April 2026)`

## 5C. Model Name Accuracy — PASS

- "Cinema Studio 3.0" — 73 occurrences, consistent capitalization
- "Cinema Studio 2.5" — 35 occurrences, consistent
- "Seedance 2.0" — 57 occurrences, consistent
- "SeedDance" / "Seed Dance" / "CINEMA STUDIO" — 0 results
- "(upcoming)" — 0 results in active files (only in CHANGELOG history)

## 5D. Business/Team Plan Flag — PASS

Every sub-skill with Cinema Studio 3.0 content includes the Business/Team plan flag:
- higgsfield-cinema — header + comparison table + callout
- higgsfield-models — table headers + section title
- higgsfield-prompt — inline at section intro
- higgsfield-camera — section header + intro callout (fixed during audit)
- higgsfield-soul — section header + callout
- higgsfield-audio — section header
- higgsfield-troubleshoot — section intro
- higgsfield-motion — inline
- higgsfield-style — inline
- All 10 templates — section headers
- Dispatcher — routing table

## 5E. Content Accuracy — PASS

- All Cinema Studio 2.5 content preserved (verified via diff)
- Resolution specs consistent: 3.0 = 720p video / 2K image; 2.5 = 1080p / 4K
- Duration specs consistent: 3.0 = up to 15s; 2.5 = up to 12s
- No contradictions between sub-skills

## 5F. MCSLA Framework Integrity — PASS

- MCSLA appears as primary framework in higgsfield-prompt (line 17)
- Seedance 2.0 section states "complement the MCSLA formula above. They are not a replacement"
- Director's Formula explicitly mapped TO MCSLA with table

## 5G. Prompt Example Validation — PASS

- Anti-slop words in new sections: only appear in the kill-list table (correct usage)
- Template recipe placeholders: "beautiful" replaced with specific alternatives (fixed during audit)
- All new prompt examples use concrete, observable language

## 5H. README Accuracy — PASS

- File tree matches actual repo structure
- Skill count: 18 sub-skills (correct)
- Template count: 10 (correct)
- Stale "NEW v2.0" / "NEW in v1.3.7" labels removed (fixed during audit)
- Install methods reference correct paths

## 5I. Memory System — PASS

- `db/filter-memory.json` — valid JSON, 4 entries, 0 duplicate IDs
- `db/quality-memory.json` — valid JSON, 5 entries, 0 duplicate IDs
- `validate.py` passes all checks

---

## Fixes Applied During Audit

1. Added "(Business/Team Plan)" to `higgsfield-camera/SKILL.md` section header + intro callout
2. Removed stale "NEW v2.0" / "NEW in v1.3.7" labels from README file tree (3 instances)
3. Replaced anti-slop word "beautiful" in `higgsfield-recipes/SKILL.md` template placeholders (2 instances)

---

## Final Statistics

| Metric | Count |
|--------|-------|
| Files changed (total) | 35 |
| Lines added | ~960 |
| Lines removed | ~85 |
| New sections added | 19 (8 sub-skills + 10 templates + 1 negative constraints) |
| "(upcoming)" removed | 8 instances across 4 files |
| Version bumped | 21 files |
| Validation | ALL CHECKS PASSED |


<!-- ============================================================ -->
# v3.0.0 — Migration Inventory

> Archived verbatim from `docs/archive/v3.0.0/v3-inventory.md` (release v3.0.0). Historical — not maintained.

---

# v3.0.0 Inventory — Cinema Studio 3.0 + Seedance 2.0

Generated: 2026-04-06

---

## File Inventory

### Root Files

| File | Current Version | Needs CS 3.0 | Needs Seedance 2.0 | Notes |
|------|----------------|---------------|---------------------|-------|
| `SKILL.md` | 2.0.2 | ✅ Add to model list | ❌ | Root model selection guide |
| `README.md` | 2.0.2 (badge) | ✅ Version badge, intro, file tree | ❌ | Public-facing |
| `CHANGELOG.md` | — | ✅ v3.0.0 entry | ✅ | Version history |
| `CLAUDE.md` | — | ❌ | ❌ | No model/version refs |
| `CONTRIBUTING.md` | — | ❌ | ❌ | No model/version refs |
| `USER-GUIDE.pdf` | — | ⚠️ PDF — cannot edit directly | ⚠️ | Flag to user |
| `model-guide.md` | — | ✅ Add 3.0 model entry + comparison table | ✅ Remove "(upcoming)" | Root reference |
| `image-models.md` | — | ❌ | ❌ | Image-only models |
| `vocab.md` | — | ❌ | ❌ | Camera vocabulary |
| `prompt-examples.md` | — | ❌ | ❌ | Example prompts |
| `photodump-presets.md` | — | ❌ | ❌ | Photodump presets |
| `validate.py` | — | ❌ | ❌ | Schema checks still valid |
| `higgsfield_memory.py` | — | ❌ | ❌ | No version strings |

### Dispatcher

| File | Current Version | Needs CS 3.0 | Needs Seedance 2.0 | Notes |
|------|----------------|---------------|---------------------|-------|
| `mnt/.../SKILL.md` | 2.0.2 | ✅ Add to routing, "What Is Higgsfield?" | ✅ Remove "(upcoming)" concept | Main dispatcher |

### Core Sub-Skills (Phase 2 targets)

| File | Lines | Current Version | Needs CS 3.0 | Needs Seedance 2.0 | Scope |
|------|-------|----------------|---------------|---------------------|-------|
| `higgsfield-cinema/SKILL.md` | 1,054 | 2.0.2 | ✅ **MAJOR** — Full 3.0 spec section | ❌ | New 3.0 section with specs, comparison table, @ patterns |
| `higgsfield-prompt/SKILL.md` | 250 | 2.0.2 | ❌ | ✅ **MAJOR** — Best practices section | Intent over Precision, Genre Router, I2V Gate, Anti-Slop |
| `higgsfield-camera/SKILL.md` | 184 | 2.0.2 | ✅ Smart Mode docs | ✅ One-Move Rule, genre presets | Camera best practices |
| `higgsfield-motion/SKILL.md` | 208 | 2.0.2 | ❌ | ✅ Intent-first choreography | Motion best practices |
| `higgsfield-style/SKILL.md` | 175 | 2.0.2 | ❌ | ✅ One Style Anchor Rule | Style best practices |
| `higgsfield-audio/SKILL.md` | 239 | 2.0.2 | ✅ **MAJOR** — Native stereo, SCELA | ✅ Remove "(upcoming)", elevate audio | Audio-video joint generation |
| `higgsfield-soul/SKILL.md` | 330 | 2.0.2 | ✅ Soul Cast 3.0 section | ❌ | Character consistency for 3.0 |
| `higgsfield-troubleshoot/SKILL.md` | 160 | 2.0.2 | ❌ | ✅ Diagnostic tree | 6-step troubleshooting for 3.0 engine |

### Other Sub-Skills (unchanged content, version bump only)

| File | Lines | Current Version | Action |
|------|-------|----------------|--------|
| `higgsfield-apps/SKILL.md` | — | 2.0.2 | Version bump only |
| `higgsfield-assist/SKILL.md` | — | 2.0.2 | Version bump only |
| `higgsfield-image-shots/SKILL.md` | — | 2.0.2 | Version bump only |
| `higgsfield-mixed-media/SKILL.md` | — | 2.0.2 | Version bump only |
| `higgsfield-moodboard/SKILL.md` | — | 2.0.2 | Version bump only |
| `higgsfield-pipeline/SKILL.md` | — | 2.0.2 | Version bump only |
| `higgsfield-recall/SKILL.md` | — | 2.0.2 | Version bump only |
| `higgsfield-recipes/SKILL.md` | — | 2.0.2 | Version bump only |
| `higgsfield-vibe-motion/SKILL.md` | — | 2.0.2 | Version bump only |

### Models Sub-Skill

| File | Lines | Current Version | Needs CS 3.0 | Needs Seedance 2.0 | Notes |
|------|-------|----------------|---------------|---------------------|-------|
| `higgsfield-models/SKILL.md` | 197 | 2.0.2 | ✅ Add 3.0 row + flowchart | ✅ Remove "(upcoming)" | Compact model guide |
| `higgsfield-models/MODELS-DEEP-REFERENCE.md` | 14,729+ | 2.0.2 | ✅ Add 3.0 entry | ✅ Remove "(upcoming)" | Full per-model docs; Seedance 2.0 already pre-documented |

### Genre Templates (Phase 3 targets)

| File | Lines | CS Mentions | Seedance Mentions | Action |
|------|-------|-------------|-------------------|--------|
| `01-cinematic-action-chase.md` | 56 | ❌ | ❌ | Add 3.0 genre mapping + prompt length |
| `02-product-ugc-showcase.md` | 57 | ✅ Grid Gen | ❌ | Add 3.0 genre mapping + prompt length |
| `03-horror-atmosphere.md` | 71 | ❌ | ❌ | Add 3.0 genre mapping + prompt length |
| `04-fashion-editorial.md` | 68 | ✅ Creative Tilt | ❌ | Add 3.0 genre mapping + prompt length |
| `05-sci-fi-vfx.md` | 68 | ❌ | ❌ | Add 3.0 genre mapping + prompt length |
| `06-portrait-character-intro.md` | 71 | ✅ Clinical Sharp | ❌ | Add 3.0 genre mapping + prompt length |
| `07-landscape-establishing-shot.md` | 54 | ❌ | ❌ | Add 3.0 genre mapping + prompt length |
| `08-comedy-social-media.md` | 67 | ❌ | ✅ Seedance Pro | Add 3.0 genre mapping + prompt length |
| `09-romantic-intimate.md` | 75 | ❌ | ❌ | Add 3.0 genre mapping + prompt length |
| `10-dance-music-performance.md` | 70 | ❌ | ❌ | Add 3.0 genre mapping + prompt length |

### Shared Resources

| File | Lines | Action |
|------|-------|--------|
| `shared/negative-constraints.md` | 111 | Add no-negative-prompt note for 3.0 + positive alternatives |

### Memory System

| File | Lines | Action |
|------|-------|--------|
| `db/filter-memory.json` | 61 | Model-agnostic — no changes needed |
| `db/quality-memory.json` | 113 | Consider adding Cinema Studio 3.0 quality entry |
| `db/memory-summary.md` | 97 | Regenerate after any JSON changes |
| `higgsfield_memory.py` | 385 | No version strings — unchanged |

### Config / Rules (unchanged)

| File | Action |
|------|--------|
| `.claude/settings.json` | ❌ Unchanged |
| `.claude/settings.local.json` | ❌ Unchanged |
| `.claude/rules/*.md` (5 files) | ❌ Unchanged — thin pointers |
| `.claude/commands/*.md` (2 files) | ❌ Unchanged |

---

## Pre-Existing Issues Found

1. **Seedance 2.0 labeled "(upcoming)"** — appears in: `higgsfield-models/SKILL.md` (lines 40, 94), `MODELS-DEEP-REFERENCE.md` (line 262), `model-guide.md` (lines 19, 104), `higgsfield-audio/SKILL.md` (lines 24, 185–191). All need "(upcoming)" removed.
2. **Seedance 2.0 in negative-constraints.md** — line 67 references lip-sync constraints but does NOT have "(upcoming)" label — already consistent.
3. **Seedance 2.0 in filter-memory.json** — entry F-004 references face upload blocking — content-accurate, no change needed.
4. **USER-GUIDE.pdf** — binary PDF, cannot be edited. User will need to regenerate from source after v3.0.0 changes.

---

## Summary

| Category | Files | Need Content Changes | Version Bump Only | Unchanged |
|----------|-------|---------------------|-------------------|-----------|
| Root docs | 13 | 4 (README, CHANGELOG, SKILL.md, model-guide.md) | 0 | 9 |
| Dispatcher | 1 | 1 | 0 | 0 |
| Core sub-skills | 8 | 8 | 0 | 0 |
| Other sub-skills | 9 | 0 | 9 | 0 |
| Models sub-skill | 2 | 2 | 0 | 0 |
| Genre templates | 10 | 10 | 0 | 0 |
| Shared resources | 1 | 1 | 0 | 0 |
| Memory system | 4 | 1 (quality-memory.json) | 0 | 3 |
| Config/rules | 8 | 0 | 0 | 8 |
| **Total** | **56** | **27** | **9** | **20** |


<!-- ============================================================ -->
# v3.4.0 — PDF Integration Audit

> Archived verbatim from `docs/pdf-audit/AUDIT-REPORT.md` (release v3.4.0). Historical — not maintained.

---

# PDF Integration Audit — v3.4.0 candidate

Date: 2026-04-18
Source material: 7 official Higgsfield handbooks (reviewed externally, not stored in repo)

This report is an analytical summary of what the seven PDFs cover, compared to the current state of the higgsfield-ai-prompt-skill. All PDF content is described in paraphrase; no verbatim tables, prompts, or long quotes from the source material appear in this report. Three of the seven PDFs (Ai Promting Guide, Cinema Studio 3.0 HandBook, CS3 Doc) are slide-based or text-based presentations of the same Cinema Studio 3.0 material; overlap across those three is collapsed in the Cross-PDF overlaps section.

---

## Summary table

| PDF | Total items | DUPLICATE | REINFORCE | GAP | PHILOSOPHICAL |
|-----|-------------|-----------|-----------|-----|---------------|
| AI_prompting_handbook_image_video_models_en | 14 | 11 | 2 | 1 | 0 |
| Ai Promting Guide (CS slide deck variant) | 9 | 8 | 1 | 0 | 0 |
| Cinema Studio 3.0 HandBook (slide deck) | 8 | 7 | 0 | 0 | 1 |
| CS3 Doc (text Cinema Studio 3.0) | 12 | 9 | 1 | 1 | 1 |
| Seedance 2.0 Handbook | 18 | 14 | 1 | 2 | 1 |
| HiggsfieldTools Guide | 9 | 4 | 1 | 3 | 1 |
| Kling Motion Control | 10 | 7 | 0 | 3 | 0 |
| **TOTAL** | **80** | **60** | **6** | **10** | **4** |

---

## Per-PDF findings

### AI_prompting_handbook_image_video_models_en

A cross-ecosystem prompting handbook covering nine model families (OpenAI/Sora, Midjourney, Runway, Veo, FLUX, Firefly, Stability, Kling, Luma). It frames Higgsfield as a workflow layer rather than a model family and teaches universal prompt skeletons, reusable building blocks, image-to-video best practices, consistency rules, camera language, and common failures.

**Content items:**

1. **Scope framing — Higgsfield as platform/workflow, not a model family** — classification: PHILOSOPHICAL (handled in item 7 below; not counted here as a gap)
2. **Universal image prompt skeleton (subject/scene/composition/lighting/style/constraints)** — classification: DUPLICATE
   - Concept: seven-slot image prompt scaffold with a compact one-liner form.
   - Where it exists: `skills/higgsfield-image-shots/SKILL.md` + `prompt-examples.md` (shot size + angle + movement + subject + pose + environment + lighting + style formula).
   - Priority: N/A
3. **Universal video prompt skeleton (subject/action/camera/change-over-time/environment/look)** — classification: DUPLICATE
   - Concept: nine-slot video scaffold with a compact one-liner.
   - Where it exists: MCSLA five-layer formula in `skills/higgsfield-prompt/SKILL.md:14-26`; same five axes with different labels.
   - Priority: N/A
4. **Reusable prompt blocks (subject / composition / camera / lighting / motion / constraint)** — classification: DUPLICATE
   - Concept: modular blocks you can mix into any prompt.
   - Where it exists: equivalent block thinking in `higgsfield-prompt` (MCSLA), `higgsfield-camera`, `higgsfield-style`, and the Identity/Motion separation rule.
   - Priority: N/A
5. **Image-to-video rule: do not re-describe the static image, only describe motion** — classification: DUPLICATE
   - Concept: the prompt's job in I2V is the motion layer, not scene re-description.
   - Where it exists: `skills/higgsfield-prompt/SKILL.md:74-78` (explicit I2V rule), Cinema Studio 3.0 Soul Cast section in `higgsfield-soul`.
   - Priority: N/A
6. **Consistency rules + character bible template** — classification: REINFORCE
   - Concept: keep identical face/body/wardrobe descriptors across shots, and maintain a short "character bible" paragraph that gets pasted verbatim into every prompt in a sequence.
   - Where it exists: Identity/Motion separation rule in `higgsfield-prompt/SKILL.md:172-213` and `higgsfield-soul/SKILL.md:72-173` — but neither skill teaches the "one short paragraph, pasted unchanged every time" bible pattern outside Soul ID. There's no explicit template for users who are NOT using Soul ID and need manual identity locking (e.g., Popcorn-only workflows, non-Higgsfield models).
   - Target: small addition to `higgsfield-soul` or `higgsfield-pipeline` — a "manual character bible" pattern for when Soul ID is not in use.
   - REINFORCE justification: the current skill assumes Soul ID is the primary lock mechanism. The PDF's template is cleaner for manual-only workflows.
   - Priority: MEDIUM
7. **Higgsfield-as-workflow-layer framing** — classification: PHILOSOPHICAL
   - Concept: treat Higgsfield as a platform that orchestrates third-party model engines, rather than as a single generator. (See Philosophical shifts section.)
   - Priority: See Philosophical shifts.
8. **Camera language cheat sheet (locked-off, push-in, pull-back, pan, tilt, tracking, crane, orbit, POV, OTS)** — classification: DUPLICATE
   - Where it exists: `vocab.md`, `skills/higgsfield-camera/SKILL.md`, with richer naming (Higgsfield-specific presets like Action Run, FPV Drone, Snorricam, Robo Arm).
   - Priority: N/A
9. **Model-specific notes — OpenAI/Sora, Midjourney, Runway, Veo, FLUX, Firefly, Stability, Kling, Luma** — classification: DUPLICATE (partial)
   - Concept: per-model prompt preferences.
   - Where it exists: `skills/higgsfield-models/SKILL.md` + `MODELS-DEEP-REFERENCE.md` cover all Higgsfield-integrated engines in deeper detail. The PDF also covers OpenAI DALL-E, Midjourney, FLUX, Firefly, Stability, Luma — but these are NOT Higgsfield-integrated engines, so they are outside the skill's scope by design.
   - Priority: N/A (out of scope)
10. **Common failure patterns (three-prompts-glued-together, conflicting camera+composition, underspecified motion, static request with motion words, inconsistent identity, abstract-style-no-subject)** — classification: DUPLICATE
    - Where it exists: `skills/higgsfield-prompt/SKILL.md:217-230` (Common Prompt Mistakes table), `skills/higgsfield-troubleshoot/SKILL.md`.
    - Priority: N/A
11. **Quick templates (portrait / product / environment / subtle I2V / dynamic action / static shot)** — classification: DUPLICATE
    - Where it exists: `templates/` (10 annotated genre templates), `skills/higgsfield-recipes/SKILL.md`.
    - Priority: N/A
12. **Fast workflow recommendation — iterate one variable at a time** — classification: GAP
    - Concept: when iterating, change only one variable (subject, composition, motion, or style) per regeneration so you can identify what changed the result.
    - Where it exists: absent. Closest thing is the general "iterate" advice in `higgsfield-troubleshoot` and the Hero Frame workflow in `higgsfield-cinema`, but neither teaches the explicit one-variable-per-iteration loop as a named methodology. The HiggsfieldTools Guide PDF reinforces this same rule (see that section).
    - Target: small addition to `higgsfield-prompt` as a named pattern ("Iteration rule: one variable per regeneration") OR a new short section in `higgsfield-troubleshoot`.
    - Priority: MEDIUM
13. **Prompt weighting / negative prompts guidance (Stability-specific)** — classification: DUPLICATE
    - Where it exists: `skills/shared/negative-constraints.md` handles negative constraints for Higgsfield. Stability weighting syntax is out of scope for the Higgsfield skill.
    - Priority: N/A (out of scope)
14. **REINFORCE — camera language tied to emotional effect (push-in = tension/intimacy, pull-back = isolation, low-angle = power, handheld = urgency)** — classification: REINFORCE
    - Concept: a compact "camera term → typical effect" lookup tied to emotional intent.
    - Where it exists: `higgsfield-camera/SKILL.md` has "Best for" columns per movement, and the CS3 Business/Team section has genre-based camera presets. The emotional-intent angle exists but is scattered across multiple movement tables rather than consolidated as a standalone cheat sheet.
    - Target: minor reorganization — could add a single "camera-intent cheat sheet" table at the top of `higgsfield-camera` pulling the Best-for columns together.
    - Priority: LOW

---

### Ai Promting Guide (Cinema Studio 3.0 slide deck)

A visual slide-based version of the Cinema Studio 3.0 material. Covers the practical formula (subject + action + camera + lighting + vibe), core principles, image vs. video prompt structure, reusable blocks, character bible, camera language, and common failures. OCR quality was mixed on this deck; several slides rendered fragmented.

**Content items:**

1. **Prompt-as-blueprint, not essay** — classification: DUPLICATE
   - Where it exists: `higgsfield-prompt/SKILL.md` intent-over-precision section (lines 242-244), anti-slop vocabulary.
   - Priority: N/A
2. **Image vs video prompt contrast (spatial vs temporal logic)** — classification: DUPLICATE
   - Where it exists: `higgsfield-prompt` T2V vs I2V sections, `higgsfield-image-shots` for stills.
   - Priority: N/A
3. **Compact practical formula "Subject + Action + Camera + Lighting + Vibe"** — classification: DUPLICATE
   - Where it exists: MCSLA in `higgsfield-prompt`. "Vibe" maps to Look; the slide formula is a rephrasing.
   - Priority: N/A
4. **Failure patterns preview (prompt bleed, motion conflict, detail overload)** — classification: DUPLICATE
   - Where it exists: `higgsfield-prompt/SKILL.md` Common Prompt Mistakes, `higgsfield-troubleshoot`.
   - Priority: N/A
5. **Universal image skeleton (Subject + Environment + Lighting + Camera/Angle + Style/Render)** — classification: DUPLICATE
   - Where it exists: `higgsfield-image-shots/SKILL.md`.
   - Priority: N/A
6. **Universal video skeleton (OCR rendered fragmented; appears to mirror the handbook's scaffold)** — classification: DUPLICATE
   - Where it exists: MCSLA.
   - Priority: N/A
7. **Character bible example (one-sentence identity template)** — classification: REINFORCE (already covered in item 6 of the AI Prompting Handbook)
   - Priority: MEDIUM (consolidated with item 6 of handbook)
8. **Camera language cheat sheet (term → effect → best used for)** — classification: DUPLICATE
   - Where it exists: `higgsfield-camera/SKILL.md`.
   - Priority: N/A
9. **Model-specific notes — cross-model (OpenAI DALL-E, Midjourney, Runway, Veo, FLUX, Firefly, Stability, Kling, Luma)** — classification: DUPLICATE (partial, same out-of-scope caveat as handbook)
   - Priority: N/A

---

### Cinema Studio 3.0 HandBook (slide deck)

A second Cinema Studio 3.0 slide deck. Short, promotional-feeling deck emphasizing: scene-building tool mental model, character+environment asset creation, the practical formula, genre/pacing as behavior modifiers, camera techniques, common mistakes, three starter templates, and a "think like a filmmaker" closing.

**Content items:**

1. **Core six-step workflow (ideation → character → environment → scene prompt → audio → export)** — classification: DUPLICATE
   - Where it exists: `higgsfield-cinema/SKILL.md:75-91` (the 10-step Cinema Studio 2.5 workflow); 3.0 workflow steps overlap tightly.
   - Priority: N/A
2. **Asset creation — stable characters and environments via reference sheets** — classification: DUPLICATE
   - Where it exists: `higgsfield-soul/SKILL.md:194-224` (character sheet creation) + `higgsfield-cinema` Reference Anchor.
   - Priority: N/A
3. **Practical formula "Subject + Action + Camera + Lighting + Vibe"** — classification: DUPLICATE (same as Ai Promting Guide item 3)
   - Priority: N/A
4. **Genre & pacing — rhythm follows genre** — classification: DUPLICATE
   - Where it exists: `higgsfield-cinema/SKILL.md` Speed Ramp tables + Genre tables per-version.
   - Priority: N/A
5. **Camera techniques — close-up = emotion, establishing = context, tracking = movement** — classification: DUPLICATE
   - Where it exists: `higgsfield-camera/SKILL.md` shot size table, genre-based camera presets section.
   - Priority: N/A
6. **Common mistakes (conflicting keywords, ignored lighting, missing seeds, inconsistent ratios)** — classification: DUPLICATE
   - Where it exists: `higgsfield-troubleshoot/SKILL.md` + `higgsfield-prompt/SKILL.md`.
   - Priority: N/A
7. **Three starter templates (hero intro, dialogue scene, action sequence)** — classification: DUPLICATE
   - Where it exists: `templates/` provides 10 genre-specific templates including character intro, action chase, and several dialogue-capable recipes.
   - Priority: N/A
8. **"Think like a filmmaker" — tools don't make the movie, directors do** — classification: PHILOSOPHICAL
   - Concept: director's mindset over prompt-writer mindset. See Philosophical shifts.

---

### CS3 Doc (Cinema Studio 3.0 text-heavy version)

The fullest text version of the Cinema Studio 3.0 material. Ten numbered sections covering: CS3.0 as a scene-building tool, six-step workflow, building characters properly, building locations, prompt-writing mindset, story-first prompting, genre/pacing, camera thinking, common mistakes, simple starter templates.

**Content items:**

1. **CS3.0 as scene-building tool, not clip generator** — classification: PHILOSOPHICAL
   - See Philosophical shifts.
2. **Six-step core workflow (character → location → upload references → describe scene → choose genre/pace/camera → generate and iterate)** — classification: DUPLICATE
   - Where it exists: `higgsfield-cinema/SKILL.md:75-91`.
   - Priority: N/A
3. **Character-first principle: build character asset BEFORE scene** — classification: DUPLICATE
   - Where it exists: `higgsfield-soul/SKILL.md` (Soul ID/Soul Cast flows), `higgsfield-cinema` Reference Anchor + Elements system.
   - Priority: N/A
4. **Character reference sheet structure (front/left profile/right profile/back/close-up portraits)** — classification: REINFORCE
   - Concept: a specific five-view character sheet layout — the PDF names the exact angles.
   - Where it exists: `higgsfield-soul/SKILL.md:208-214` mentions front / 3-4 / side profile / back (4 views). The PDF's list is subtly different (adds close-up portraits as a named variant, drops 3/4).
   - Target: minor edit to `higgsfield-soul` character sheet angle list — either align the angle set to the PDF's five-view pattern or note both variants.
   - Priority: LOW
5. **Location sheet structure (straight-on wide / left-angle / right-angle / reverse / close-up environmental details)** — classification: GAP
   - Concept: a parallel location reference-sheet pattern with five prescribed angles — separate from character reference sheets.
   - Where it exists: absent. `higgsfield-cinema` mentions `@Locations` and Reference Anchors for characters, but there is NO structured "location sheet" pattern. The skill currently conflates location handling with character handling or pushes it into generic Element description.
   - Target: new subsection in `higgsfield-cinema` (Elements section) OR new subsection in `higgsfield-soul` — "Location reference sheets" with five-view angle spec.
   - Priority: HIGH — this is a concrete missing asset class.
6. **Location-as-asset principle (treat environments like characters: establish once, reuse, keep architecture/light/color treatment stable)** — classification: DUPLICATE (principle) / GAP (named workflow)
   - Where it exists as principle: `higgsfield-cinema` Elements system, `higgsfield-pipeline` Popcorn stage.
   - Where it's a gap: the explicit "build the location as an asset first, before scene generation" workflow is only implicit. The PDF frames this as a named methodology parallel to character-first.
   - Priority: covered by item 5 above.
7. **Weak prompt vs strong prompt diagnostic (keyword soup vs scene direction)** — classification: DUPLICATE
   - Where it exists: `higgsfield-prompt` anti-slop vocabulary, `higgsfield-seedance` filmmaker-not-friend pass, prompt-examples before/after section.
   - Priority: N/A
8. **Seven-slot prompt formula ([shot type] + [subject] + [action] + [environment] + [lighting] + [camera behavior] + [tone])** — classification: DUPLICATE
   - Where it exists: MCSLA (five-layer), Seedance six-slot formula.
   - Priority: N/A
9. **Story-first prompting — prompt answers "what's happening, what's the character feeling, what changes, what should the audience feel"** — classification: DUPLICATE
   - Where it exists: `higgsfield-prompt` Intent-over-Precision, `higgsfield-seedance` physics-not-emotion (the CS3 approach lands between these two — emotion as dramatic intent without the physics-only rewrite).
   - Priority: N/A
10. **Genre as performance tool (noir doesn't move like action; horror doesn't pace like comedy)** — classification: DUPLICATE
    - Where it exists: `higgsfield-cinema` Genre table, `higgsfield-camera` genre-based camera presets.
    - Priority: N/A
11. **Camera supports emotion (close-up = intimacy/fear/realization, wide = isolation/scale, handheld = instability/urgency, push-in = tension, static = restraint/dread)** — classification: REINFORCE
    - See item 14 in AI_prompting_handbook — already flagged as a low-priority consolidation opportunity.
    - Priority: LOW
12. **Five common mistakes (scenes before locked characters, disposable locations, keyword soup, over-controlling, ignoring emotional intention)** — classification: DUPLICATE
    - Where it exists: `higgsfield-prompt` + `higgsfield-troubleshoot`.
    - Priority: N/A

---

### Seedance 2.0 Handbook

Seedance's own handbook. Covers the mental model, beginner mistakes, seven core operating principles, the prompt modes, single-shot and multi-shot structures, reference-role rules, continuation formula, reference-sheet types (environment / outfit / motion-camera / palette-mood), beat-based timing, nine-slot prompt structure, anti-patterns, troubleshooting-by-symptom, and reference vocabulary for camera/lighting/sound/constraints.

**Content items:**

1. **Mental model — "controlled directing system, not poetic toy"** — classification: PHILOSOPHICAL
   - See Philosophical shifts (compatible with current framing).
2. **Six biggest beginner mistakes (prompt overload, role-less references, too many actions, too many camera ideas, too many style words, no hierarchy)** — classification: DUPLICATE
   - Where it exists: `higgsfield-seedance/SKILL.md` filter playbook, `higgsfield-prompt` one-action-per-scene rule, anti-patterns list in existing Seedance skill.
   - Priority: N/A
3. **Principle 1 — one shot = one dominant readable action** — classification: DUPLICATE
   - Where it exists: `higgsfield-prompt/SKILL.md:155-168` (One Action Per Scene rule).
   - Priority: N/A
4. **Principle 2 — camera is not decoration, it serves story** — classification: DUPLICATE
   - Where it exists: `higgsfield-camera` genre-based camera presets + `higgsfield-seedance` voice-rewrite pass ("name the camera move").
   - Priority: N/A
5. **Principle 3 — action must be physical (visible behavior, not dialogue/exposition)** — classification: DUPLICATE
   - Where it exists: `higgsfield-seedance/SKILL.md` voice rewrite + engine constraints ("describe physics, not emotion").
   - Priority: N/A
6. **Principle 4 — environment is active, not wallpaper** — classification: REINFORCE
   - Concept: the environment should participate in the scene (weather responds, ambient motion carries mood), not just sit as a static backdrop.
   - Where it exists: `templates/` use environmental motion as secondary action; `higgsfield-prompt` lists environmental motion in the Motion Block. But there's no named principle "environment = active participant" framed as a Seedance operating rule.
   - Target: small addition to `higgsfield-seedance` as a named operating principle.
   - Priority: LOW
7. **Principle 5 — references need assigned roles (identity / motion / audio / palette)** — classification: DUPLICATE
   - Where it exists: `higgsfield-seedance/SKILL.md` rule of 12, `higgsfield-cinema/SKILL.md` @ Reference Patterns section (character identity, environment, motion reference, audio reference, multi-image spatial mapping).
   - Priority: N/A
8. **Principle 6 — continuity is not just linking (flow vs sequence)** — classification: DUPLICATE
   - Where it exists: `higgsfield-pipeline` master chain, Cinema Studio multi-shot workflow.
   - Priority: N/A
9. **Principle 7 — structure beats length** — classification: DUPLICATE
   - Where it exists: `higgsfield-prompt` keep-under-200-words rule, Seedance short-prompt preference.
   - Priority: N/A
10. **Six prompt modes — Single-Shot, Multi-Shot, Reference-Based, Continuation, Expand Shot (canvas extension), Edit Shot** — classification: GAP
    - Concept: Seedance supports six named generation modes. The handbook names them as first-class mode labels with specific use cases: Reference-Based uses a source image to guide generation; Continuation extends a prior output; Edit Shot modifies specific elements in an existing image; Expand Shot extends the canvas/scene.
    - Where it exists: `higgsfield-seedance/SKILL.md` covers single-shot / multi-shot style implicitly, but does NOT name or distinguish Reference-Based, Continuation, Expand Shot, or Edit Shot as distinct modes with distinct prompt patterns. `higgsfield-cinema` covers @ Reference Patterns but conflates them with Cinema Studio-specific behavior rather than Seedance modes.
    - Target: new subsection in `higgsfield-seedance` — "Seedance 2.0 prompt modes" with one paragraph per mode and a minimal example pattern.
    - Priority: HIGH — this is directly applicable to Seedance users and not currently documented.
11. **Reference roles: image = identity/wardrobe/palette/composition; video = motion rhythm/camera behavior/blocking; audio = timing/speech/ambience** — classification: DUPLICATE
    - Where it exists: `higgsfield-cinema/SKILL.md` @ Reference Patterns section distinguishes these uses by input type.
    - Priority: N/A
12. **Continuation formula: last-frame anchor + identity anchor + previous clip as secondary memory; start immediately after final frame; never repeat previous action; preserve character/outfit/environment/emotional carryover** — classification: GAP
    - Concept: a specific five-rule formula for writing continuation prompts so the model doesn't repeat actions, loses state, or drifts identity.
    - Where it exists: absent as a named pattern. `higgsfield-pipeline` discusses chaining shots but not the continuation-specific rules. `higgsfield-cinema` has frame extraction loop (2.5) but doesn't document continuation prompt rules. Veo 3.1 video extension is covered in `higgsfield-models/MODELS-DEEP-REFERENCE.md:710-711` at the model level only, not at the prompt-construction level.
    - Target: new subsection in `higgsfield-seedance` OR `higgsfield-pipeline` — "Continuation prompt formula" with the five rules.
    - Priority: HIGH — continuation is a recurring failure mode and this is a clean, portable ruleset.
13. **Reference-sheet types (environment / outfit-material / motion-camera / palette-mood)** — classification: REINFORCE
    - Concept: four parallel reference-sheet categories, each reducing one specific kind of ambiguity. The motion-camera sheet and palette-mood sheet are under-documented in the current skill.
    - Where it exists: `higgsfield-soul` covers character sheets; `higgsfield-moodboard` covers palette/mood via Soul Hex and curated moodboards. But motion-camera sheets (a short reference clip of the camera behavior you want repeated) and outfit-material sheets (dedicated wardrobe reference) are not documented as dedicated artifacts.
    - Target: small addition to `higgsfield-soul` or `higgsfield-cinema` — name the four reference-sheet types and which artifact they correspond to in Higgsfield's UI.
    - Priority: MEDIUM
14. **Beats-and-timing framework (beat = meaningful unit of progression; use seconds when timing matters, shot numbers when storyboard logic matters; three-beat structure establish/develop/payoff)** — classification: DUPLICATE
    - Where it exists: `higgsfield-prompt` three-act rhythm for action (charge-up / burst / aftermath), Cinema Studio Multi-Shot Manual scene structure, timestamped prompt format.
    - Priority: N/A
15. **Nine-slot prompt structure (format-goal / asset-roles / scene / action / camera / lighting-color / sound / timeline-shot-structure / constraints / continuity)** — classification: DUPLICATE
    - Where it exists: MCSLA + the `higgsfield-seedance` six-slot formula + Cinema Studio UI settings. Nine slots is a more granular repackaging of material already covered.
    - Priority: N/A
16. **Seedance anti-patterns (adjective soup, too many camera moves, unassigned reference stacks, controlling everything equally, continuation without start lock, contradictory identity, literary emotion vs visible behavior, changing too many variables at once)** — classification: DUPLICATE
    - Where it exists: `higgsfield-seedance` voice rewrite + existing anti-patterns section; `higgsfield-prompt` common mistakes.
    - Priority: N/A
17. **Troubleshooting-by-symptom matrix (chaotic result / style ignored / character drift / camera resets / previous beat replays / motion feels fake / clip feels unstable)** — classification: DUPLICATE
    - Where it exists: `higgsfield-troubleshoot/SKILL.md` symptom-based organization.
    - Priority: N/A
18. **Vocabulary tables (camera / lighting / sound / constraint language)** — classification: DUPLICATE
    - Where it exists: `vocab.md`, `higgsfield-camera`, `higgsfield-audio`, `skills/shared/negative-constraints.md`.
    - Priority: N/A

---

### HiggsfieldTools Guide

A concise guide to the Higgsfield platform's workspaces — Cinema Studio, Lipsync Studio, Draw-to-Video/Sketch-to-Video, Sora 2 Trends, Click to Ad, Higgsfield Audio — with an emphasis on "choose the workspace by task, not the model." Six-step project workflow. A decision matrix mapping production problems to workspaces. OCR had occasional slide-layout confusion but the core structure was readable.

**Content items:**

1. **Platform is organized around tools/workspaces, not a single generator** — classification: PHILOSOPHICAL
   - See Philosophical shifts. Not currently a primary framing in the skill.
2. **Workspace-first decision framework — "What are you trying to make?" precedes "Which model?"** — classification: GAP
   - Concept: the user should start by identifying the production problem (cinematic scene / speaking character / rough idea / trend-led short / product ad / narration), pick the matching workspace, THEN select the model inside it.
   - Where it exists: partially in `higgsfield-models/SKILL.md` decision flowchart (model-first) and in `higgsfield-apps/SKILL.md` (by-use-case tables). But the root `SKILL.md` routes by SUB-SKILL based on what the user mentions — there's no workspace-first decision layer. The Fast Path table in root `SKILL.md:74-79` jumps straight to default models.
   - Target: either a new subsection at the top of root `SKILL.md` ("Workspace-first decision — choose the workspace by task, then the model by result") OR a new sub-skill `higgsfield-workspaces` acting as the entry-point router.
   - Priority: HIGH — this is a meaningful philosophical layer plus a concrete routing matrix, and the skill currently has no equivalent.
3. **Cinema Studio workspace description (cinematic scenes with deliberate camera direction)** — classification: DUPLICATE
   - Where it exists: `higgsfield-cinema/SKILL.md`.
   - Priority: N/A
4. **Lipsync Studio workspace (speaking characters, dubbing, avatars)** — classification: DUPLICATE (but sparsely)
   - Where it exists: `higgsfield-audio/SKILL.md` mentions Lipsync Studio; `higgsfield-apps/SKILL.md:90` lists it as an app. The skill does NOT have a dedicated Lipsync Studio workspace write-up.
   - Priority: covered by item 2 above (workspace-first framework would surface this)
5. **Draw to Video / Sketch to Video workspace (early ideation, storyboard blocking)** — classification: GAP
   - Concept: dedicated workspace for turning a rough sketch or blocking drawing into a generated video — fundamentally different workflow from text-to-video.
   - Where it exists: `higgsfield-apps/SKILL.md:81` has a one-liner ("Sketch-to-Real — turn sketch into realistic image/video"). CHANGELOG notes mention Draw-to-Video was on the backlog but not implemented. There is no documented sketch-to-video prompt pattern, example, or decision point.
   - Target: either a new sub-skill `higgsfield-sketch` OR a dedicated section in `higgsfield-apps` with prompt patterns.
   - Priority: MEDIUM — not huge, but this is a concrete missing workflow.
6. **Sora 2 Trends workspace (fast trend-led short-form content)** — classification: GAP
   - Concept: dedicated workspace for trend/viral short-form. Different from Sora 2 the model — a templated workflow on top.
   - Where it exists: absent. `higgsfield-models` covers Sora 2 as a model but doesn't describe a Trends workspace or workflow.
   - Target: dedicated section in `higgsfield-apps` OR in a new `higgsfield-workspaces` sub-skill.
   - Priority: MEDIUM
7. **Click to Ad workspace (product-focused ad generation from URL or image)** — classification: DUPLICATE
   - Where it exists: `higgsfield-apps/SKILL.md:36-47` covers Click to Ad and the product-ad family.
   - Priority: N/A
8. **Higgsfield Audio workspace (voiceovers, voice swaps, translation)** — classification: REINFORCE
   - Concept: a workspace dedicated to generative voice — distinct from Lipsync Studio.
   - Where it exists: `higgsfield-audio/SKILL.md` is primarily about audio IN video generations. A dedicated Higgsfield Audio workspace for voiceover/voice swap/translation is not separately documented.
   - Target: new subsection in `higgsfield-audio` — "Higgsfield Audio workspace (standalone voice tools)".
   - Priority: MEDIUM
9. **Six-step project logic (open workspace → choose feature → select model → prepare input → add prompt/controls → generate and iterate)** — classification: DUPLICATE (partial)
   - Where it exists: `higgsfield-cinema` 10-step workflow covers much of this; `higgsfield-pipeline` covers cross-workspace chaining. The PDF's six-step version is a simpler, more generic rendering for any workspace. No flat cross-workspace "open → feature → model → input → prompt → iterate" six-step recipe is written down.
   - Priority: covered by item 2 above.

---

### Kling Motion Control

A focused handbook on Kling 3.0 Motion Control and the Higgsfield workflow for using it. Covers when to choose Motion Control, what it does (character image + motion reference video = motion transfer), the one-screen Higgsfield workflow (8 clickable steps), input-quality best practices, face/orientation modes (Image Orientation vs Video Orientation + Element Binding), scene-source selection, prompt role (shape the world, not the base motion), and recommended reference-clip duration (3-30s).

**Content items:**

1. **When to choose Motion Control — directed repeatable motion, dance/sports/acting beats, motion-across-characters transfer, scene prototyping, ad/social/creator repeatability** — classification: REINFORCE
   - Concept: a specific decision shortlist for when Motion Control beats standard generation.
   - Where it exists: `skills/higgsfield-models/MODELS-DEEP-REFERENCE.md:102-127` covers Motion Control at the model level with "best for" list (reference-video motion transfer, full-body choreography, complex dance/action, talking head with precise gestures). The model reference has most of the content; the PDF adds "ad/social repeatability" as a use case which is absent.
   - Priority: LOW
2. **Motion Control core definition: character image + motion reference video = gesture/body-motion/facial-performance/timing transfer** — classification: DUPLICATE
   - Where it exists: `skills/higgsfield-models/MODELS-DEEP-REFERENCE.md:102-126` covers this in detail.
   - Priority: N/A
3. **Image Orientation vs Video Orientation mode (camera movements + static body vs complex full-body motion)** — classification: DUPLICATE
   - Where it exists: `MODELS-DEEP-REFERENCE.md:108-110`.
   - Priority: N/A
4. **Element Binding — connects facial identity to motion data for face stability during movement** — classification: DUPLICATE
   - Where it exists: `MODELS-DEEP-REFERENCE.md:112`.
   - Priority: N/A
5. **Motion reference input best practices (one clear subject, head+body visible, real human motion, avoid cuts/fast transitions, avoid very fast actions, 3-30s range)** — classification: GAP
   - Concept: a structured "input quality checklist" for the motion reference clip itself — what makes a clip a good motion source.
   - Where it exists: `MODELS-DEEP-REFERENCE.md` mentions 3-30s duration and motion transfer capability, but does NOT give a structured "what makes a good motion reference clip" checklist (clean subject, readable face/body, avoid cuts, avoid fast actions). The whole "input quality determines output quality" pre-flight check is absent.
   - Target: new subsection in `higgsfield-motion` or as an addition to the Kling 3.0 Motion Control section in `MODELS-DEEP-REFERENCE.md` — "Motion reference input checklist".
   - Priority: HIGH — this is a concrete, teachable pre-flight check that prevents wasted credits.
6. **Face binding + orientation preflight (close-up face input required, what to do if output suddenly cuts/snaps to different source clip = motion source too fast)** — classification: GAP
   - Concept: a specific diagnostic pattern for common Motion Control failures — if the output jumps between motions, your motion source has cuts or is too fast.
   - Where it exists: absent from the skill entirely.
   - Target: new troubleshooting entry in `higgsfield-troubleshoot/SKILL.md` AND in the motion-control section of `MODELS-DEEP-REFERENCE.md`.
   - Priority: MEDIUM
7. **Kling Motion Control one-screen workflow (8 steps: Video tab → Kling Motion Control 3.0 → upload motion reference → upload character image with readable face+body → pick resolution → set Scene source → describe environment/lighting in Advanced Settings → Generate)** — classification: GAP
   - Concept: a named, step-by-step workflow for running Motion Control specifically on Higgsfield (not generic Kling). The PDF walks through the actual Higgsfield UI flow.
   - Where it exists: `MODELS-DEEP-REFERENCE.md` describes what Motion Control does but does NOT walk through the Higgsfield UI workflow for invoking it. No step-by-step exists.
   - Target: new subsection in `higgsfield-motion` OR in the Kling Motion Control section of `MODELS-DEEP-REFERENCE.md` — "Running Kling Motion Control 3.0 in Higgsfield".
   - Priority: HIGH — this is a concrete missing workflow walkthrough.
8. **Scene source options (pull environment from the motion video vs from the character image)** — classification: GAP (subset of item 7)
   - Priority: covered by item 7.
9. **Prompt role in Motion Control — prompt shapes the world around the motion, not the base motion itself** — classification: DUPLICATE
   - Where it exists: `MODELS-DEEP-REFERENCE.md:118` ("Describe camera direction + scene context; don't describe the motion itself").
   - Priority: N/A
10. **Pre-flight checklist (clean reference with no cuts / readable face+body / correct scene source / correct orientation mode / prompt describes world not motion)** — classification: GAP (overlaps items 5, 7)
    - Priority: covered by items 5 and 7.

---

## New sub-skill candidates

### 1. `higgsfield-workspaces` (PROPOSED)

**What it would cover:** The workspace-first decision layer. Before a user picks a model, they identify which Higgsfield workspace fits their production problem: Cinema Studio (deliberate cinematic direction), Lipsync Studio (speaking characters), Draw-to-Video / Sketch-to-Video (ideation from rough sketches), Sora 2 Trends (trend-led shorts), Click to Ad (product ads), Higgsfield Audio (standalone voice work). Each workspace gets a short "when to use this" paragraph, the model(s) available inside, and the entry-point to the existing sub-skill that covers its prompt patterns.

**Which PDF items feed into it:**
- HiggsfieldTools Guide items 1, 2, 4, 5, 6, 8, 9 (workspace-first framework, workspace descriptions, Lipsync / Draw-to-Video / Sora Trends / Higgsfield Audio workspace entries, six-step project logic)
- Philosophical framing from item 1 (platform as workspaces, not a generator)

**Why it can't live in an existing sub-skill:** The root `SKILL.md` is already a dispatcher routed by sub-skill name. `higgsfield-apps` is a flat list of one-click workflows, not a decision layer. `higgsfield-models` is model-first, not task-first. The workspace-first decision layer is an orthogonal axis to both. It would be the user's first stop after the root dispatcher, then the existing sub-skills handle the prompt-level work.

**Alternative:** Could live as a new top section in the root `SKILL.md` rather than a sub-skill — but the root is already dense. A dedicated sub-skill is cleaner.

### 2. `higgsfield-motion-control` OR expansion of `higgsfield-motion` (EXPANSION PREFERRED)

**What it would cover:** Running Kling 3.0 Motion Control in Higgsfield specifically. Motion-reference input quality checklist (what makes a clip a good motion source). Face binding + orientation preflight. Step-by-step Higgsfield UI workflow. Scene source selection. Common failure diagnostics (output jumps = source too fast, etc.).

**Which PDF items feed into it:** Kling Motion Control items 1, 5, 6, 7, 8, 10.

**Why it might not need a new sub-skill:** `higgsfield-motion` currently covers named motion PRESETS (VFX library), not motion CONTROL (reference-video motion transfer). The two share the word "motion" but are different systems. Options:
- Add a new top section "Kling Motion Control 3.0 workflow" inside `higgsfield-motion` — cleanest, no new file.
- Create `higgsfield-motion-control` as its own sub-skill — cleaner separation but adds routing complexity.

**Recommendation:** expand `higgsfield-motion` first; promote to standalone only if content grows beyond a single section.

---

## Philosophical shifts

### A. Higgsfield as workflow-layer, not a model family

**The shift:** The external AI Prompting Handbook treats Higgsfield as a platform/workflow layer that sits on top of third-party model engines (Kling, Sora, Veo, Wan, etc.). The user's primary question is "which workspace fits my production problem" rather than "which model should I use."

**How it would change the skill:** The root `SKILL.md` currently opens with a mandatory workflow (route to sub-skill → apply MCSLA → use named vocabulary → append negative constraints). It treats Higgsfield as a coherent prompting platform with MCSLA as the core formula. Adding the workspace-first layer would slot IN FRONT of MCSLA: the user first picks a workspace (Cinema Studio / Lipsync / Sketch-to-Video / Sora Trends / Click to Ad / Higgsfield Audio), and only then applies MCSLA for the prompt inside that workspace.

**Compatible with MCSLA?** Yes. MCSLA is the prompt-construction formula; workspace-first is a routing layer one level above it. They compose cleanly. The risk is redundancy: the current root `SKILL.md` already has a "Route to the Right Skill" table routed by user intent, and parts of that are already workspace-ish. Adding a formal workspace layer means reconciling the two routing tables.

### B. Director-first / story-first mindset (Cinema Studio 3.0 and Seedance handbook)

**The shift:** CS3 Doc and the Seedance handbook both emphasize thinking like a director — who is the scene about, what changes, what should the audience feel — rather than like a prompt-writer assembling keywords. Seedance frames it as "controlled directing system, not poetic toy."

**How it would change the skill:** The current `higgsfield-prompt/SKILL.md` has "Intent over Precision" and "Story-first" is implicit in the Three-Act Rhythm for Action. `higgsfield-seedance` has the "filmmaker not friend" voice rewrite. The PDF framing is a slightly different cut: it puts "dramatic purpose of the shot" as question #1 before any prompt construction.

**Compatible with current approach?** Fully compatible. This is not a competing framework — it's the same mindset phrased as an upfront question. Minor edit opportunity to lead `higgsfield-prompt` with "before writing, answer: who is the scene about, what changes, what should the audience feel."

**Priority:** LOW — stylistic reinforcement, not a real gap.

### C. Character and location as ASSETS to be built first (CS3 Doc, Seedance handbook)

**The shift:** Treat characters AND locations as reusable assets with dedicated reference sheets, generated BEFORE any scene work. The skill covers this for characters (Soul ID, character sheets) but treats locations as a subset of the Elements system in Cinema Studio. The PDFs frame locations as equal to characters: you should have a location sheet with five prescribed views and lock its architecture/light/color treatment before generating scenes.

**How it would change the skill:** Small reframing in `higgsfield-soul` and `higgsfield-cinema` — add a "Location Reference Sheet" pattern with five-view structure. Possibly promote locations from "one of three Element types" to "first-class asset with its own workflow."

**Compatible with current approach?** Fully compatible. Additive.

**Priority:** MEDIUM (and also captured as a GAP — CS3 Doc item 5).

### D. Seedance mental model — "controlled directing system"

**The shift:** The Seedance handbook frames Seedance as a system you direct, not a tool you describe to. The current `higgsfield-seedance` has this in spirit via the voice-rewrite and engine-constraints sections, but doesn't name the mental model upfront.

**Compatible?** Fully compatible — it's the current skill's implicit framing, made explicit.

**Priority:** LOW — one-line addition to `higgsfield-seedance` opener.

---

## Cross-PDF overlaps

Content that appears in multiple PDFs (integrate once, not repeatedly):

1. **Universal image prompt skeleton** — AI_prompting_handbook + Ai Promting Guide. Duplicate in both; integrate once (already duplicate in skill).
2. **Universal video prompt skeleton / practical formula** — AI_prompting_handbook + Ai Promting Guide + Cinema Studio 3.0 HandBook + CS3 Doc. Four overlapping formulations. All map to MCSLA.
3. **Character bible / character reference sheet** — AI_prompting_handbook + CS3 Doc + Cinema Studio 3.0 HandBook + Seedance handbook. Four sources, one concept. Target: single REINFORCE edit in `higgsfield-soul`.
4. **Camera language cheat sheet (term → effect)** — AI_prompting_handbook + Ai Promting Guide + CS3 Doc + Seedance handbook. All four reference the same ~10-term list. Single source of truth: `higgsfield-camera`.
5. **"Do not re-describe the image in I2V — describe motion only"** — AI_prompting_handbook + Seedance handbook. Already in `higgsfield-prompt`.
6. **Six-step workflow (ideation → character → location → scene → generate → iterate)** — Cinema Studio 3.0 HandBook + CS3 Doc + HiggsfieldTools Guide. Three sources, same workflow.
7. **Common failure patterns (keyword soup, conflicting movements, underspecified motion, inconsistent identity, prompt bleed)** — AI_prompting_handbook + Ai Promting Guide + Cinema Studio 3.0 HandBook + CS3 Doc + Seedance handbook. Heavily duplicated across all PDFs. Target: keep `higgsfield-troubleshoot` + `higgsfield-prompt` common-mistakes tables as-is — they already subsume these.
8. **Genre/pacing as behavior modifier, not decoration** — Cinema Studio 3.0 HandBook + CS3 Doc + Seedance handbook.
9. **One action per shot** — Seedance handbook + `higgsfield-prompt` already has this rule. Heavily duplicated upstream.
10. **"Think like a filmmaker / director"** — Cinema Studio 3.0 HandBook + CS3 Doc + Seedance handbook. Philosophical shift item B.
11. **Iterate one variable at a time** — AI_prompting_handbook + HiggsfieldTools Guide. Two sources, and currently absent from the skill (GAP item).
12. **Workspace/tool-first mindset** — HiggsfieldTools Guide + AI_prompting_handbook (latter in the form of "Higgsfield is a platform, not a model"). Philosophical shift item A.

---

## Overall recommendation

**How much new content actually exists:** Rough estimate — 60 of 80 items (75%) are DUPLICATE, 6 (7.5%) are REINFORCE, 10 (12.5%) are GAP, and 4 (5%) are PHILOSOPHICAL. The skill already covers the dominant majority of this material, often in more depth than the PDFs. The PDFs are a useful external calibration check — they confirm the skill is complete on MCSLA, camera language, character consistency, I2V rules, and common failures. Where they add value is in a small number of concrete workflow gaps (location sheets, continuation formula, motion-control workflow, workspace-first decision, sketch-to-video, Sora Trends) and one philosophical layer (workspace-first routing).

**The five additions that would deliver the most value:**

1. **Location reference-sheet workflow** (CS3 Doc item 5) — target `higgsfield-cinema` or `higgsfield-soul`. Concrete, actionable, fills a real asymmetry in how the skill treats characters vs locations. HIGH.
2. **Seedance prompt modes — Reference-Based, Continuation, Expand Shot, Edit Shot** (Seedance handbook item 10) — target `higgsfield-seedance`. Core Seedance capability currently absent. HIGH.
3. **Seedance continuation formula** (Seedance handbook item 12) — target `higgsfield-seedance` or `higgsfield-pipeline`. Named five-rule pattern for continuation prompts; prevents recurring failures. HIGH.
4. **Kling Motion Control workflow + reference-input checklist** (Kling PDF items 5, 7) — target `higgsfield-motion` (expanded) + `MODELS-DEEP-REFERENCE.md`. Concrete pre-flight checks for a credit-expensive feature. HIGH.
5. **Workspace-first decision layer** (HiggsfieldTools Guide item 2 + philosophical shift A) — target either new top section in root `SKILL.md` or new `higgsfield-workspaces` sub-skill. Routing layer above MCSLA; surfaces Draw-to-Video / Sora Trends / Lipsync / Higgsfield Audio workspaces that currently get thin coverage. HIGH.

**v3.4.0 scope decision:** All five HIGH-priority gaps are small, additive, and independent. None require rewriting existing sub-skills. They can ship together as a single v3.4.0 release titled something like "v3.4.0 — PDF-sourced gap fills: location sheets, Seedance modes + continuation, Motion Control workflow, workspace-first routing." MEDIUM-priority items (Sora 2 Trends section, Sketch-to-Video section, Higgsfield Audio workspace, environment-as-active principle, motion-camera/outfit/palette reference sheets, active-environment principle, character-bible template for non-Soul-ID workflows, motion-control failure diagnostic) could roll into v3.4.0 or a v3.4.1 cleanup release depending on appetite.

**Integration risks:**

- **Workspace-first layer (GAP #5)** is the one item that touches the root `SKILL.md` routing. The current routing table is dense and well-tuned. Adding a workspace-first layer means reconciling it with the existing "Route to the Right Skill" table — not a rewrite, but a careful insert. If this is too invasive, a standalone `higgsfield-workspaces` sub-skill with a pointer from the root is a safer option.
- **"Director-first" philosophical framing (shift B)** is already implicit in the skill. Making it explicit risks tone drift if overdone. One-line additions only.
- **Location-as-asset reframing (shift C)** is purely additive to Elements system — low risk.
- **All other HIGH items** are additive subsections inside existing sub-skills — no rewrites, no risk.

Nothing in the PDFs requires rewriting existing skill files. The current skill is in strong shape; v3.4.0 would be a focused gap-fill release on top of a solid foundation.


<!-- ============================================================ -->
# v3.6.0 — PDF Integration Audit

> Archived verbatim from `docs/pdf-audit/AUDIT-REPORT-v3.6.0.md` (release v3.6.0). Historical — not maintained.

---

# PDF Integration Audit — v3.6.0 candidate

Date: 2026-04-25
Source material: 8 community/creator PDFs (reviewed externally, not stored in repo) plus hands-on UI verification of Cinema Studio 3.5 conducted on 2026-04-25.

This report is an analytical summary of what the eight PDFs cover, compared to the current state of the higgsfield-ai-prompt-skill, and how that material lines up with what was verified directly in the Cinema Studio 3.5 UI on 2026-04-25. All PDF content is described in paraphrase; no verbatim tables, prompts, or long quotes from the source material appear in this report. Three of the eight PDFs are sibling pairs (a slide-deck and a long-form/prose version of the same body of work), and the overlap is collapsed in the Cross-PDF overlaps section. The Cinema Studio 3.5 platform changes themselves came out of live UI verification, not from any single PDF — the CinemaStudioRecap PDF served as a visual confirmation pass against what the UI surfaces.

---

## Summary table

| PDF | Total items | DUPLICATE | REINFORCE | GAP | PHILOSOPHICAL |
|-----|-------------|-----------|-----------|-----|---------------|
| Building a Cinematic Universe — Mr. Core slide deck | 8 | 8 | 0 | 0 | 0 |
| Building a Cinematic Universe — Mr. Core long-form | 12 | 6 | 2 | 4 | 0 |
| CinemaStudioRecap (Cinema Studio 3.5 visual guide) | 14 | 0 | 0 | 14 | 0 |
| ONESHOT (creator workflow memoir) | 6 | 0 | 0 | 0 | 6 |
| Seedance 2 — Serious Examples Supplement | 9 | 7 | 1 | 1 | 0 |
| Seedance 2.0 Prompt Modes & Prompt Building Framework (slide deck) | 8 | 7 | 0 | 1 | 0 |
| Seedance Promt modes (prose handbook) | 8 | 8 | 0 | 0 | 0 |
| UNDERNEATH THE CHAOS (creator workflow memoir) | 5 | 0 | 0 | 0 | 5 |
| **TOTAL** | **70** | **36** | **3** | **20** | **11** |

---

## Per-PDF findings

### Building a Cinematic Universe — Mr. Core slide deck

A short slide-deck condensation of the Mr. Core long-form workflow document. Functions as a TL;DR of the long-form companion PDF (next entry). Every item in the deck appears in fuller form in the long-form document, so every item is classified DUPLICATE relative to the long-form treatment.

**Content items:**

1. **Pre-production discipline as cost lever** — DUPLICATE of long-form item 1.
2. **AI as collaborator, not vending machine** — DUPLICATE of long-form item 2.
3. **Studio character vs cinematic character distinction** — DUPLICATE of long-form item 3.
4. **Action choreography around AI strengths** — DUPLICATE of long-form item 4.
5. **Location selection rules for AI-friendly spaces** — DUPLICATE of long-form item 5.
6. **Single-generation-per-shot strategy** — DUPLICATE of long-form item 6.
7. **Smooth-cut / morph-cut breathing room** — DUPLICATE of long-form item 7.
8. **Wardrobe-as-generation-cost (piano test)** — DUPLICATE of long-form item 8.

All items: see corresponding entries in the long-form PDF below.

---

### Building a Cinematic Universe — Mr. Core long-form

A creator-author long-form workflow document covering pre-production discipline, location selection, action design around model limits, single-generation strategy, the cost of wardrobe complexity, and the studio-vs-cinematic character distinction. Four GAP candidates surface here. None are in scope for v3.6.0 — all four are deferred to v3.6.1+ planning.

**Content items:**

1. **Pre-production discipline as cost lever** — DUPLICATE
   - Concept: front-load script, shot list, and reference assets before generation.
   - Where it exists: Pre-Prompt Checklist in `skills/higgsfield-prompt/SKILL.md`; Hero Frame and Reference Sheet workflow in `skills/higgsfield-cinema/SKILL.md`.

2. **AI as collaborator, not vending machine** — DUPLICATE
   - Concept: iterative direction beats one-shot prompting.
   - Where it exists: Iteration Rule shipped in v3.4.1 (`skills/higgsfield-prompt/SKILL.md`).

3. **Studio character vs cinematic character — studio output is intermediate** — GAP
   - Concept: when a model returns a character that reads as "studio plastic" (clean, evenly-lit, glossy), treat that as an intermediate frame, not a final — feed it through a Soul Cinema re-pass or a downstream restyle to land on a cinematic-feeling result. The studio look is a stop on the path, not the destination.
   - Where it would go: a new "Intermediate vs final character" section under `skills/higgsfield-soul/SKILL.md` or in the Cinema Studio Hero Frame workflow.
   - Status: deferred to v3.6.1+ backlog. Not in scope for v3.6.0.

4. **Action choreography around AI strengths** — GAP
   - Concept: design action around what the model renders well — circular arenas (the camera can hide most of the choreography), vague ruins (no continuity to break), repeating textures (less drift). Avoid choreography the model fails on (precise hand-to-hand, prop combat, multi-character grappling). Plan one transformation per shot, not a chain of beats.
   - Where it would go: extension of the Fight Scene Rules section in `skills/higgsfield-cinema/SKILL.md`, or a new "Action design discipline" subsection in `skills/higgsfield-prompt/SKILL.md`.
   - Status: deferred to v3.6.1+ backlog. Not in scope for v3.6.0.

5. **Location selection rules for AI-friendly spaces** — GAP
   - Concept: select locations whose geometry forgives drift — circular arenas, repeating textures, vague ruins, fog/dust environments. Avoid locations whose continuity the audience can audit (familiar landmarks, geometric architecture with sight lines).
   - Where it would go: new section in `skills/higgsfield-cinema/SKILL.md` near Location Reference Sheets, or a section in `skills/higgsfield-pipeline/SKILL.md`.
   - Status: deferred to v3.6.1+ backlog. Not in scope for v3.6.0.

6. **Single-generation-per-shot strategy** — GAP
   - Concept: rather than generate-and-pick from many candidates, plan the shot well enough that the first generation lands. Treat each generation as the work, not as exploration.
   - Where it would go: extension of the Iteration Rule in `skills/higgsfield-prompt/SKILL.md`, or a new "Generation budgeting" section.
   - Status: deferred to v3.6.1+ backlog. Not in scope for v3.6.0.

7. **Smooth-cut / morph-cut breathing room — 2-second prompted gaps** — GAP
   - Concept: prompt explicit 2-second still-or-near-still moments at the start AND end of every shot, so editors have material to land morph cuts and smooth cuts on. Without this, every cut has to happen mid-action, which the model renders poorly.
   - Where it would go: addition to the Multi-Shot Manual workflow in `skills/higgsfield-cinema/SKILL.md`, or a new "Cut-friendly shot construction" section in `skills/higgsfield-pipeline/SKILL.md`.
   - Status: deferred to v3.6.1+ backlog. Not in scope for v3.6.0.

8. **Wardrobe-as-generation-cost (piano test)** — REINFORCE
   - Concept: each piece of wardrobe complexity (buttons, ties, jewelry, scarves) is a generation cost; the "piano test" is the rule that if a costume element is as visually demanding as a piano in the frame, the model will spend its budget rendering it instead of the action. Strip wardrobe to the simplest silhouette that still reads as the character.
   - Where it would go: extension of the Outfit / Material Sheet section in `skills/higgsfield-cinema/SKILL.md`, or addition to `skills/higgsfield-soul/SKILL.md`.
   - Status: deferred to v3.6.1+ backlog. Reinforces existing Outfit Sheet pattern; not in scope for v3.6.0.

9. **Reference photography matters more than prompt language** — DUPLICATE
   - Concept: a strong reference image carries the work that prompt prose cannot.
   - Where it exists: Reference-Based Prompt Mode in `skills/higgsfield-seedance/SKILL.md`; @ Element rules in `skills/higgsfield-cinema/SKILL.md`.

10. **Color palette discipline across a project** — DUPLICATE
    - Concept: lock palette early, treat it as a project-wide constraint.
    - Where it exists: Palette / Mood Sheet in `skills/higgsfield-cinema/SKILL.md` (added v3.4.1); Soul Hex color in `skills/higgsfield-moodboard/SKILL.md`.

11. **Lighting language as scene description** — DUPLICATE
    - Concept: describe light as observable behavior (direction, color temperature, source), not as adjectives.
    - Where it exists: Style/Director-Language Prompt Mode in `skills/higgsfield-seedance/SKILL.md`; Anti-Slop Rules in same file.

12. **One transformation per shot** — REINFORCE
    - Concept: limit each shot to a single state change.
    - Where it exists: Beat Density rules in `skills/higgsfield-seedance/SKILL.md` (1 primary change per 4–6s); the existing rule is well-articulated. PDF reframes as "transformation per shot" rather than "beats per duration" — same idea, different surface. No action needed.

---

### CinemaStudioRecap (Cinema Studio 3.5 visual guide)

Primary source material for the v3.6.0 release. A visual recap of the Cinema Studio 3.5 UI surface, used to confirm what was visible during the 2026-04-25 hands-on UI verification. Most items classified as GAP because Cinema Studio 3.5 was previously undocumented in the skill — it sits alongside 2.5 and 3.0 in the model selector but had no skill-side coverage prior to this release.

**Content items:**

1. **Three-pill main UI surface (Genre / Style / Camera)** — GAP
   - Concept: 3.5 collapses creative control into three pills on the main UI; each defaults to Auto and can be overridden manually.
   - Where it would go: new `## Cinema Studio 3.5` section in `skills/higgsfield-cinema/SKILL.md`.
   - Status: IN SCOPE for v3.6.0 (Step 3).

2. **Style Settings — three-axis preset stacking** — GAP
   - Concept: Style pill operates in three modes — Auto, preset stacking (Color Palette / Lighting / Camera Moveset Style), and Manual Style free-form mode.
   - Where it would go: new section per above.
   - Status: IN SCOPE for v3.6.0 (Step 3D).

3. **8 Color Palette presets (Naturalistic Clean, Bleached Warm, Hyper Neon, Teal Orange Epic, Sodium Decay, Cold Steel, Bleach Bypass, Classic B&W)** — GAP
   - Where it would go: Style Settings subsection per above.
   - Status: IN SCOPE for v3.6.0.

4. **6 Lighting presets (Soft Cross, Contre Jour, Overhead Fall, Window, Practicals, Silhouette)** — GAP
   - Status: IN SCOPE for v3.6.0.

5. **9 Camera Moveset Style presets (Classic Static, Silent Machine, One Take, Epic Scale, Intimate Observer, Impossible Camera, Documentary Snap, Raw Chaos, Dreamy Flow)** — GAP
   - Status: IN SCOPE for v3.6.0.

6. **Manual Style free-form mode** — GAP
   - Concept: Manual Style toggle replaces the three-axis preset panel with a free-form Prompt input — this is prompt territory, requires Style/Director-Language Prompt Mode discipline.
   - Where it would go: cross-link to `skills/higgsfield-seedance/SKILL.md` Style/Director-Language Prompt Mode section.
   - Status: IN SCOPE for v3.6.0.

7. **Camera Settings — four-axis panel (Camera Body / Lens / Focal Length / Aperture)** — GAP
   - Concept: restored optical physics surface, with a simpler 3-body abstraction (Clean Digital, Fine Film, Raw 16mm) instead of 2.5's six camera bodies. Different vocabulary from 2.5.
   - Where it would go: new section per above.
   - Status: IN SCOPE for v3.6.0 (Step 3E).

8. **5 Lens characters (Vintage Haze, Warm Halation, Anamorphic, Extreme Macro, Clinical Sharp)** — GAP
   - Status: IN SCOPE for v3.6.0.

9. **Focal length set including new 75mm** — GAP
   - Concept: 5 focal lengths in 3.5 (8mm, 14mm, 35mm, 50mm, 75mm) — 75mm is new vs 2.5's 8/14/35/50mm set.
   - Status: IN SCOPE for v3.6.0.

10. **Genre catalog (General, Action, Horror, Comedy, Noir, Drama, Epic + others scrollable)** — GAP
    - Concept: 7 confirmed genres from the UI, with scroll arrows visible suggesting additional unconfirmed genres exist.
    - Status: IN SCOPE for v3.6.0; documented as the seven confirmed plus a pointer to the live UI for additional genres.

11. **Output controls — Aspect Ratio (7 options including 21:9), Quality (480p / 720p / 1080p), Sound (On/Off), Batch Size, Duration (4s–15s)** — GAP
    - Concept: 480p draft tier is new; 1080p restored vs 3.0's 720p cap.
    - Status: IN SCOPE for v3.6.0 (Step 3G).

12. **AI director toggle (function unverified)** — GAP
    - Concept: toggle visible in the bottom toolbar; function and behavior not yet verified.
    - Where it would go: brief acknowledgment in the new section, with explicit "function deferred to a future release" note.
    - Status: IN SCOPE for v3.6.0 (Step 3H) — acknowledgment only, no behavioral documentation.

13. **Five recommended Style + Camera stacks (Intimate Drama, Gritty Realism, Cold Thriller, Epic Landscape, Impact Close-up)** — GAP
    - Concept: not built-in UI presets — recommended manual combinations across Style Settings and Camera Settings panels.
    - Status: IN SCOPE for v3.6.0 (Step 3F).

14. **Element library surface — source tabs (Uploads, Image Generations, Video Generations, Elements, Liked) and element categories (All, Pinned, Shared, Characters, Locations, Props)** — GAP
    - Concept: the full two-dimensional library structure (5 source tabs × 6 element categories) and cross-shot continuity workflow are not currently documented in the skill. The existing Elements System section at lines 95–154 of `skills/higgsfield-cinema/SKILL.md` covers only Character / Location / Prop element types and @-tag rules — it does not document the source tabs or the Pinned / Shared / Liked categories.
    - Where it would go: new `### Element Library Surface — Source Tabs and Categories` subsection appended to the existing Elements System section in `skills/higgsfield-cinema/SKILL.md`.
    - Status: IN SCOPE for v3.6.0 (Step 4).

---

### ONESHOT (creator workflow memoir)

A creator-voice memoir of a one-shot generation workflow. Reads as personal philosophy and process narration rather than enumerable techniques. Classification PHILOSOPHICAL throughout — no GAPs.

**Content items:**

1. **Authorial process narration** — PHILOSOPHICAL.
2. **Personal taste as creative anchor** — PHILOSOPHICAL.
3. **The role of accident in creative work** — PHILOSOPHICAL.
4. **AI as material, not as oracle** — PHILOSOPHICAL.
5. **Patience as a craft** — PHILOSOPHICAL.
6. **Authorship in the AI era** — PHILOSOPHICAL.

No actionable items extractable. Companion to UNDERNEATH THE CHAOS (sibling memoir).

---

### Seedance 2 — Serious Examples Supplement

A worked-prompt examples supplement to the Seedance 2.0 documentation. Most examples are illustrations of patterns already documented in `skills/higgsfield-seedance/SKILL.md` and `MODELS-DEEP-REFERENCE.md`. One mode (Transformation) flagged for possible example-library expansion in a later release.

**Content items:**

1. **Reference-Based Prompt Mode worked examples** — DUPLICATE of `higgsfield-seedance` Reference-Based section.
2. **Continuation Prompt Formula worked examples** — DUPLICATE of v3.4.0 Continuation Prompt Formula.
3. **Expand Shot worked examples** — DUPLICATE of v3.4.0 Expand Shot section.
4. **Edit Shot worked examples** — DUPLICATE of v3.4.0 Edit Shot section.
5. **Style/Director-Language worked examples** — DUPLICATE of existing Style/Director-Language section.
6. **Five-Layer Stack worked examples** — DUPLICATE of `MODELS-DEEP-REFERENCE.md` Seedance 2.0 Prompt System.
7. **Audio prompting worked examples** — DUPLICATE of `MODELS-DEEP-REFERENCE.md` Audio rules.
8. **Beat Density worked examples** — DUPLICATE of `MODELS-DEEP-REFERENCE.md` Beat Density table.
9. **Transformation prompt mode worked examples** — GAP (deferred)
   - Concept: a possible new mode where the prompt explicitly describes a state change (object → object, character → character, environment → environment) within the duration of a single shot. Distinct from Continuation (which extends an existing clip) and Edit Shot (which modifies a generated clip).
   - Where it would go: new mode in the Seedance 2.0 Prompt Modes section of `skills/higgsfield-seedance/SKILL.md`.
   - Status: deferred to v3.6.1+ backlog as part of an example-library expansion. Not in scope for v3.6.0.

REINFORCE candidate: the worked examples themselves could be added to a dedicated example library, but the underlying patterns are all documented. Status: REINFORCE-only, no action.

---

### Seedance 2.0 Prompt Modes & Prompt Building Framework (slide deck)

A slide-deck presentation of the Seedance 2.0 prompt modes and building framework. Mostly DUPLICATE of v3.4.0 audit material that was already integrated. One candidate gap surfaces: a 6-Pass Testing Protocol — a sequenced testing pass list that may or may not duplicate the Iteration Rule shipped in v3.4.1.

**Content items:**

1. **Reference-Based / Continuation / Expand Shot / Edit Shot mode taxonomy** — DUPLICATE of v3.4.0.
2. **Five-Layer Stack (Subject / Action / Camera / Style / Sound)** — DUPLICATE of `MODELS-DEEP-REFERENCE.md`.
3. **6-Part Field Formula** — DUPLICATE of `MODELS-DEEP-REFERENCE.md`.
4. **Delegation levels (1–4 by complexity)** — DUPLICATE.
5. **Anti-Slop Rules** — DUPLICATE.
6. **Camera Control four-parameter pattern** — DUPLICATE.
7. **One-Take and Nine-Grid storyboard techniques** — DUPLICATE.
8. **6-Pass Testing Protocol — sequenced testing pass list** — GAP (PENDING-CHECK)
   - Concept: a six-pass testing sequence applied when refining a prompt — each pass isolates one variable (subject, action, camera, style, audio, output) and tests in order.
   - Status: needs comparison against the Iteration Rule shipped in v3.4.1 in `skills/higgsfield-prompt/SKILL.md`. The Iteration Rule already enforces single-variable iteration; the 6-Pass Protocol may be a more prescriptive sequencing of which variables to test in which order, OR it may be a full duplicate framed differently.
   - Where it would go: extension of the Iteration Rule in `skills/higgsfield-prompt/SKILL.md`, or a new section if the sequencing turns out to add genuinely new structure.
   - Status: deferred to v3.6.1+ backlog pending the gap-check pass. Not in scope for v3.6.0.

---

### Seedance Promt modes (prose handbook)

The prose / long-form companion to the Seedance 2.0 Prompt Modes slide deck above. Same eight items in fuller paragraph form. Full DUPLICATE of the slide deck — no items unique to the prose version. The 6-Pass Testing Protocol gap-check from item 8 of the slide deck applies here as well; not double-counted.

**Content items:** Identical taxonomy and coverage as the slide deck. All items DUPLICATE.

---

### UNDERNEATH THE CHAOS (creator workflow memoir)

Sibling memoir to ONESHOT — same author voice, same workflow philosophy, same classification. PHILOSOPHICAL throughout, no GAPs.

**Content items:**

1. **Workflow as lived process** — PHILOSOPHICAL.
2. **Embracing failure as input** — PHILOSOPHICAL.
3. **Constraint as creative driver** — PHILOSOPHICAL.
4. **The myth of the finished prompt** — PHILOSOPHICAL.
5. **Authorship and the long game** — PHILOSOPHICAL.

No actionable items extractable. See ONESHOT for sibling treatment.

---

## Cross-PDF overlaps

Three sibling pairs collapse the audit surface:

- **Mr. Core slide deck and Mr. Core long-form** — the slide deck is a strict subset of the long-form document. Every slide-deck item is DUPLICATE relative to the long-form. The four GAPs all surface from the long-form PDF.
- **Seedance 2.0 Prompt Modes slide deck and Seedance Promt modes prose handbook** — slide and prose presentation of the same eight items. The 6-Pass Testing Protocol GAP (PENDING-CHECK) appears in both and is counted once.
- **ONESHOT and UNDERNEATH THE CHAOS** — sibling creator memoirs, same author voice, both PHILOSOPHICAL throughout. No actionable extraction from either.

The CinemaStudioRecap PDF stands alone as the primary source for the v3.6.0 release, alongside the 2026-04-25 hands-on UI verification.

The Seedance 2 Serious Examples Supplement is a worked-examples companion to `MODELS-DEEP-REFERENCE.md`'s existing Seedance 2.0 documentation; it surfaces one new candidate mode (Transformation) and otherwise reinforces existing material.

---

## v3.6.0 release decisions

**IN scope:**

- **Cinema Studio 3.5 platform documentation** — new section in `skills/higgsfield-cinema/SKILL.md` covering the three-pill main UI, Style Settings (three-axis preset stacking + Manual Style free-form mode), Camera Settings (four-axis panel including new 75mm focal length), five recommended stacks, output controls, and AI director toggle acknowledgment. Source: CinemaStudioRecap PDF + 2026-04-25 hands-on UI verification.
- **Elements System extension** — new `### Element Library Surface — Source Tabs and Categories` subsection inside the existing Elements System section in `skills/higgsfield-cinema/SKILL.md`, documenting the five source tabs (Uploads / Image Generations / Video Generations / Elements / Liked) and six element categories (All / Pinned / Shared / Characters / Locations / Props), with library-first workflow guidance and cross-shot continuity tip.
- **Physics Rendering — Resolution Decision Matrix** — cross-model section in `skills/higgsfield-cinema/SKILL.md` applying to Seedance 2.0 and Cinema Studio 3.x: routing rule for fast/chaotic motion (720p), fine-detail physics (1080p), grounded weight (1080p), and draft/exploration (480p).
- **Cinema Studio 3.5 entry** in `skills/higgsfield-models/MODELS-DEEP-REFERENCE.md` mirroring the existing 2.5 / 3.0 structure, with cross-link to the new Cinema Studio 3.5 section in `higgsfield-cinema`.
- **Kling 3.0 quality range refinement** — refine the Kling 3.0 resolution line in `MODELS-DEEP-REFERENCE.md` to "720p / 1080p / 4K HDR" reflecting the current quality dropdown (4K was already documented; 720p added).
- **Cinema Studio version comparison table extension** — fourth column added for Cinema Studio 3.5 in the existing comparison table in `skills/higgsfield-cinema/SKILL.md` (existing 2.5 and 3.0 columns unchanged).
- **Routing entries and sub-skill triggers** — root `SKILL.md` updated to surface Cinema Studio 3.5 in the routing table, in the "What Is Higgsfield?" paragraph, and in the sub-skills triggers row.
- **Frontmatter version bumps** — root `SKILL.md` to 3.6.0 / 2026-04-25; `skills/higgsfield-cinema/SKILL.md` to 3.1.0 / 2026-04-25.

**OUT of scope (deferred to v3.6.1+ backlog):**

- Mr. Core methodology integration — piano test (wardrobe-as-generation-cost), Morph Cut / Smooth Cut breathing room (2-second prompted gaps at start and end of every shot), action choreography around AI strengths (location selection rules, single-generation strategy), studio character vs cinematic character distinction (Soul Cinema re-pass).
- 6-Pass Testing Protocol gap-check against the existing Iteration Rule shipped in v3.4.1.
- Transformation prompt mode addition to the Seedance 2.0 prompt modes catalog.
- Seedance 2.0 worked-example library expansion based on the Serious Examples Supplement.
- AI director toggle behavioral documentation — function not yet verified; toggle acknowledged in v3.6.0 with function deferred.

---

## Backlog — v3.7.0+ planning

| Item | Source | Target location | Priority |
|------|--------|-----------------|----------|
| ~~Wardrobe simplification rule (piano test)~~ | ~~Mr. Core long-form item 8~~ | ~~`higgsfield-cinema` Outfit / Material Sheet section, or `higgsfield-soul`~~ | ~~MEDIUM~~ — closed in v3.6.4 (`higgsfield-cinema` Outfit / Material Sheet → piano test) |
| ~~Morph Cut / Smooth Cut breathing room (2-second prompted gaps)~~ | ~~Mr. Core long-form item 7~~ | ~~`higgsfield-cinema` Multi-Shot Manual workflow, or `higgsfield-pipeline`~~ | ~~MEDIUM~~ — closed in v3.6.4 (`higgsfield-cinema` Multi-Shot Manual → breathing room; cross-linked from `higgsfield-pipeline` Stage 8) |
| ~~Action choreography around AI strengths (location rules, single-gen strategy, action-transforming-space cadence)~~ | ~~Mr. Core long-form items 4–6~~ | ~~`higgsfield-cinema` Fight Scene Rules extension, or `higgsfield-prompt` Action design discipline~~ | ~~MEDIUM~~ — closed in v3.6.4 (`higgsfield-cinema` Fight Scene & Action Design Rules → Action Design Around AI Strengths) |
| ~~Studio character vs cinematic character (intermediate-vs-final, Soul Cinema re-pass)~~ | ~~Mr. Core long-form item 3~~ | ~~`higgsfield-soul` or `higgsfield-cinema` Hero Frame workflow~~ | ~~MEDIUM~~ — closed in v3.6.4 (`higgsfield-soul` Soul Cinema as the CS 3.0/3.5 Default Image Model → Studio Look vs. Cinematic Look) |
| ~~6-Pass Testing Protocol (gap-check against Iteration Rule)~~ | ~~Seedance Prompt Modes slide deck item 8 / prose handbook~~ | ~~`higgsfield-prompt` Iteration Rule extension~~ | ~~LOW (PENDING-CHECK)~~ — closed in v3.6.4 (`higgsfield-prompt` Iteration Rule → 6-Pass Diagnostic Sequence; PARTIAL GAP verdict — 6-Pass ships as subordinate diagnostic tool) |
| ~~Transformation prompt mode~~ | ~~Seedance 2 Serious Examples Supplement item 9~~ | ~~`higgsfield-seedance` Prompt Modes section~~ | ~~LOW~~ — closed in v3.6.4 (`higgsfield-seedance` Prompt Modes → Transformation) |
| ~~Seedance 2.0 worked-example library expansion~~ | ~~Seedance 2 Serious Examples Supplement~~ | ~~`higgsfield-seedance` example library (new)~~ | ~~LOW~~ — closed in v3.6.4 as 5 Seedance 2.0 examples in `prompt-examples.md` (Action, Drama, Sci-Fi, Product/Commercial, Transformation genres) instead of a new file |
| AI director toggle behavioral documentation | CinemaStudioRecap PDF item 12 + future UI verification | `higgsfield-cinema` Cinema Studio 3.5 section | BLOCKED (function unverified) |
| ~~Per-Cinematic-model deep workflow guidance (image and video) — when to pick each Cinematic model for which intent, prompting patterns specific to each, video-mode picker structure~~ | ~~2026-04-25 UI verification (additional screenshots)~~ | ~~`higgsfield-cinema` — extend Cinema Studio 3.5 Image Mode subsection + add video-mode picker subsection~~ | ~~HIGH~~ — closed in v3.6.3 (`higgsfield-cinema` § Per-Cinematic-model selection guide); stale row carried over from v3.6.2 re-label, struck in v3.6.4 cleanup |
| ~~Strip product-marketing language from skill content — file-wide pass on `MODELS-DEEP-REFERENCE.md` (e.g., ⭐ EXCLUSIVE, Current Top Model, similar superlatives)~~ | ~~2026-04-25 review during v3.6.0 integration~~ | ~~`skills/higgsfield-models/MODELS-DEEP-REFERENCE.md` — file-wide style normalization pass~~ | ~~LOW~~ — closed in v3.6.5 (9 surgical edits in `MODELS-DEEP-REFERENCE.md` + 1 cross-file edit in `skills/higgsfield-apps/SKILL.md`; strip rule sharpened to preserve "Strongest at X" capability claims and workflow-vocabulary uses of "premium" in pipeline / assist contexts) |
| ~~Path B — Refactor `generate_user_guide.py` to parse `SKILL.md` files dynamically. Eliminates manual sync burden — by v3.6.1 the PDF was 6 releases stale. Substantial release on its own (~3–4 hours of refactor + validation), should not mix with content writing.~~ | ~~2026-04-25 USER-GUIDE staleness scoping during v3.6.2 planning~~ | ~~`generate_user_guide.py` — full refactor to read `SKILL.md` + `skills/*/SKILL.md` + `CHANGELOG.md` and generate sections dynamically~~ | ~~MEDIUM (v3.7.x+)~~ — closed in v3.7.0 (Option D scope: metadata parameterization via `read_root_metadata()` + sub-skill list discovery via `discover_sub_skills()` + build-time staleness invariant check; full SKILL.md content parsing scoped out as Option B at ~10-15h cost vs Option D's ~2h, with content drift deferred to v3.7.1+ per the USER-GUIDE expansion row below) |
| USER-GUIDE.pdf comprehensive expansion — full Cinema Studio 3.5 / Image Mode / Elements / Physics Matrix / Motion Control / workspace-first / Reference Sheet Types sections. **Drift catalog from v3.7.0 scoping (D3-D8):** Cinema Studio 3.5 per-Cinematic-model selection guide unreflected; Seedance 5 prompt modes (incl. v3.6.4 Transformation) unreflected in Section 10; v3.6.3 Soul Cinema + v3.6.4 Studio Look re-pass unreflected in Section 11; v3.6.4 Iteration Rule + 6-Pass Diagnostic Sequence unreflected in Section 18; v3.6.0 Reference Sheet Types + v3.6.4 piano test / Action Design / Morph-Cut breathing room unreflected in Section 21; sub-skill row descriptions unreflected for v3.6.4 additions in Section 22. After v3.7.0's Option D refactor, hardcoded sections written for these expansions would be cheap to maintain — Path B's full SKILL.md parsing was scoped out as too costly for the value, so manual content edits remain the path forward. | 2026-04-25 USER-GUIDE staleness scoping + 2026-05-04 v3.7.0 Path B scoping | `generate_user_guide.py` content sections (manual hardcoded edits per drift catalog) | LOW (v3.7.1+) |
| ~~Audio-block diversity pass for Seedance worked examples in `prompt-examples.md` — all five v3.6.4 examples use the same audio-block compositional pattern (primary action + environmental texture + distant element + low/no music indicator). Future pass to vary across foreground-heavy, ambient-heavy, music-foregrounded, dialog-anchored, and sound-design-anchored shapes.~~ | ~~2026-05-03 v3.6.4 review~~ | ~~`prompt-examples.md` § Action / Drama / Sci-Fi / Product / Transformation Seedance examples~~ | ~~LOW~~ — closed in v3.6.5 (one-to-one shape mapping across the 5 examples: B1 foreground-heavy / B2 music-foregrounded / B3 sound-design-anchored / B4 ambient-heavy / B5 dialog-anchored as wordless vocal performance; B2 wordless preserved) |

---

## Methodology notes

- Source material PDFs are external (not committed to this repo); analysis preserved here in paraphrase only. No verbatim tables, prompts, or long quotes from any source PDF appear in this report.
- Cinema Studio 3.5 platform changes were verified against the live Higgsfield UI on 2026-04-25; the CinemaStudioRecap PDF served as a confirmation pass against what the UI surfaced. Where the UI showed scroll arrows or other indicators of additional unconfirmed content (e.g., the Genre catalog), this report and the v3.6.0 release content document only what was visually confirmed.
- The v3.4.0 audit report at `docs/pdf-audit/AUDIT-REPORT.md` remains the methodology template; this report mirrors its structure, classification system (DUPLICATE / REINFORCE / GAP / PHILOSOPHICAL), and per-PDF analytical pattern.
