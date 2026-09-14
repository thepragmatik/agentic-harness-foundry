# Agent Guide

This repository is designed for both human maintainers and agentic execution. Agents MUST treat this file as navigation guidance, not as a substitute for the governing specifications.

## Authority order

When artifacts conflict, use this precedence:

1. accepted ADRs in `docs/adr/`;
2. active specifications in `docs/specs/`;
3. active bounded-work artifacts under `specs/`;
4. `docs/roadmap.md`;
5. research notes in `docs/research/`;
6. README prose.

Generated evidence never overrides an accepted specification by itself; it triggers a decision/update.

## Non-negotiable rules

- Do not inherit implementation assumptions from prior Hermes/Pi prototype repositories.
- Do not modify Hermes, Pi, LCM, Mnemosyne, llama.cpp, MLX, provider settings, or host security controls unless an active spec explicitly authorizes the change.
- Every implementation touching an upstream project MUST pin the tested release/commit and record a compatibility probe.
- Security-critical authorization and egress decisions MUST NOT depend solely on probabilistic model output.
- Context compression MUST retain recoverable provenance to the original evidence where practical.
- A new component MUST have a simpler baseline and a measurable promotion gate.
- Never mark a task validated without reproducible evidence.
- Prefer reversible, isolated experiments before host-level changes.

## Lightweight specification workflow

For a bounded change, create `specs/<nnn>-<slug>/`.

Minimum small-change artifact set:

- `spec.md` — outcome, invariants, acceptance criteria, non-goals;
- `tasks.md` — atomic checklist with verification commands/evidence.

Add `plan.md` only when architecture, migration, dependency, or rollback choices are non-trivial.

Do not create clarification/analyze/checklist documents automatically. Add them only when the work genuinely needs them.

## Agent reading discipline

To limit token consumption:

1. Read this file and the active `tasks.md`.
2. Read the active `spec.md`.
3. Read only referenced architecture/ADR sections needed for the current task.
4. Avoid loading whole research directories or historical evidence into context.
5. Persist findings to files; do not rely on chat/session memory as project state.

## Evidence discipline

Each completed implementation task SHOULD point to one of:

- deterministic test output;
- benchmark result;
- compatibility probe;
- schema validation;
- security test;
- reproducible command transcript;
- manual approval when no machine-verifiable check exists.

Keep bulky raw logs out of agent prompts. Store them under `evidence/` or an external artifact store and reference them by path/hash.

## Status vocabulary

Use only:

- `proposed`
- `researching`
- `specified`
- `experimental`
- `validated`
- `rejected`
- `superseded`

`validated` means the declared acceptance criteria were actually run against the pinned environment.

## Current execution boundary

The repository is in research/specification mode. Do not perform production harness uplift work until the roadmap's compatibility and baseline gates are complete.