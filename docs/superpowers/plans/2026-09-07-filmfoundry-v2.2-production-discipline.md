# FilmFoundry Skills v2.2 Production Discipline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add provider-neutral production facts, an append-only ledger, conditional artifact requirements, scene/look/dependency contracts, and a beginner workflow without changing existing v2.1 behavior or Wucheng canon.

**Architecture:** FilmFoundry remains the contract and validation core. New artifacts are independent strict JSON contracts referenced by requirement evaluation and prompt compilation; provider execution and aesthetic decisions remain external or human-owned. Wucheng adopts the rules in shadow mode.

**Tech Stack:** Python 3.11, JSON Schema documents, Markdown, pytest, SHA-256.

**Spec:** The user-approved plan in the task conversation is authoritative; no separate design file exists.

## Global Constraints

- Preserve the v1.3.3 compatibility baseline (`167 passed`) and existing v2.1 behavior (`211 passed`).
- Keep the FilmFoundry core provider-neutral and reject project-specific fields outside valid extension namespaces.
- Structural failures are `ERROR`; optional creative guidance and unverified practices are `WARNING`.
- Use layered enforcement: foundation artifacts are always required; expensive creative artifacts are required only when policy triggers match.
- Do not call paid providers or claim that grey backgrounds, 3/4 views, one-second previs, FOV values, or physics wording guarantee quality.
- Do not modify Wucheng Canon, existing blockers, media, routed units, or `99_归档`.
- Keep the main `SKILL.md` at or below 300 lines.

---

### Task 1: Production Ledger and Requirement Policy

- [ ] Add strict production-ledger and production-policy schemas.
- [ ] Add immutable event validation, retry-variable validation, and entity references.
- [ ] Add `ArtifactRequirement`, `RequirementReport`, and `evaluate_requirements`.
- [ ] Add `ff requirements`, `ff ledger validate`, and `ff ledger report`.
- [ ] Add failing tests first, then implementation, and commit.

### Task 2: Script Analysis and Emotional Beat Map

- [ ] Add strict schemas and parsers for sourced script facts and beat-level emotion/audio intent.
- [ ] Prevent inferred facts from becoming Canon without confirmation.
- [ ] Treat tension as creator annotation and music as intent, not an automatic output decision.
- [ ] Add requirement triggers for dialogue, music, and multi-beat units.
- [ ] Add failing tests first, then implementation, and commit.

### Task 3: Character Reference Package, Scene Topology, and Coverage

- [ ] Add strict schemas and parsers for view packages, scene topology, floor-plan facts, and location coverage.
- [ ] Require traceable view assets and independent hashes after QC promotion.
- [ ] Validate nodes, adjacency, anchors, movement paths, camera sides, and coverage references.
- [ ] Add conditional triggers for reusable characters and spatially complex scenes.
- [ ] Add templates/references, tests first, implementation, and commit.

### Task 4: Look Bible, Palette/Lighting State, and Asset Dependencies

- [ ] Add strict schemas and parsers for look, palette/lighting states, and asset dependency relations.
- [ ] Preserve reference-source provenance and keep film titles out of compiled visible-trait instructions.
- [ ] Validate dependency endpoints, cycles where ordering is required, scope, and review status.
- [ ] Add tests first, implementation, and commit.

### Task 5: Prompt Compilation and Visual-Control Integration

- [ ] Compile available artifacts in the approved stable order before provider capability data.
- [ ] Add ledger event IDs, visual-control hash, requirement-report hash, and all input hashes to compiled payloads.
- [ ] Add lint for vague adjective stacks, observable-result gaps, state/topology/camera conflicts, and unsupported slots.
- [ ] Prove compilation never modifies Prompt, Canon, Registry, or source artifacts.
- [ ] Add tests first, implementation, and commit.

### Task 6: CLI and Beginner End-to-End Guide

- [ ] Add `ff graph` and `ff report` while keeping every command root-independent and JSON-capable.
- [ ] Add the complete beginner workflow guide and focused progressive references/templates.
- [ ] Update `SKILL.md`, README, support matrix, version, and changelog without exceeding 300 lines.
- [ ] Add CLI/docs contract tests first, implementation, and commit.

### Task 7: Wucheng Shadow-Mode Vertical Slice

- [ ] Extend the Wucheng adapter to report v2.2 requirements for `TEST_H3_06_A` without blocking production.
- [ ] Preserve 75 registry assets, 109 active media files, 21 prompts, 19 routed units, all blockers, and zero real H3 outputs.
- [ ] Do not edit Canon, media, or archive content and do not call a provider.
- [ ] Add adapter tests first, implementation, and commit in the Wucheng repository.

### Task 8: Verification and Release Evidence

- [ ] Run all FilmFoundry tests, compatibility checks, CLI tests, path tests, and `git diff --check`.
- [ ] Run Wucheng adapter tests and verify counts, blockers, media hashes, and archive diff.
- [ ] Generate a v2.2 verification report with support boundaries and external evidence gaps.
- [ ] Perform whole-branch review, fix material findings, rerun verification, and commit release evidence.
