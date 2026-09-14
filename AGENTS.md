# Agent Guide

This repository is designed for both human maintainers and agentic execution. Agents MUST treat this file as navigation guidance, not as a substitute for governing specifications and evidence.

## Authority order

When artifacts conflict, use this precedence:

1. accepted ADRs in `docs/adr/`;
2. active normative specifications in `docs/specs/`;
3. root `TASKS.md` for execution order and evidence paths;
4. `docs/testing-strategy.md` for test ordering/circuit-breakers;
5. `docs/roadmap.md` for milestone boundaries;
6. `docs/architecture.md` for visual/explanatory orientation;
7. research notes in `docs/research/`;
8. README prose.

Generated evidence does not silently override a specification; it triggers a decision/spec update.

## Non-negotiable rules

- Do not inherit implementation assumptions from prior Hermes/Pi prototype repositories.
- Do not modify Hermes, Pi, LCM, Mnemosyne, llama.cpp, provider settings, model artifacts or host security controls unless the active task/spec explicitly authorizes the change.
- Every implementation touching an upstream project MUST pin the installed/tested release/commit/package and record a compatibility probe.
- **Prefer documented public/stable surfaces over upstream internals.** If a task would require an undocumented/private API, stop and revise the spec.
- **Cheapest falsifier first.** Follow `docs/testing-strategy.md`; do not jump to a soak/full benchmark/end-to-end mission while a smaller deterministic test can still disprove the design.
- Change one material variable at a time. After two failed attempts on the same hypothesis, stop/revise rather than tuning indefinitely.
- Security-critical authorization and egress decisions MUST NOT depend solely on probabilistic model output or a documented fail-open callback path.
- Context compression MUST retain recoverable provenance to original evidence where practical.
- A new model/component MUST have a simpler baseline and a measurable promotion gate.
- Never mark a task validated without its declared evidence.
- **Runtime evidence is local/untracked and sensitive by default.** Follow `docs/evidence-policy.md`; do not commit raw configs/logs/databases/prompts/secrets to this public repo.
- Prefer reversible, isolated experiments before host-level changes.
- A task reaching its `Stop if` condition MUST stop. Do not invent a new architecture during execution to get around the gate.

## Stable integration choices already made

Unless a pinned compatibility probe proves them unavailable:

- Hermes current-session context uses one selected `ContextEngine`; LCM is the planned engine.
- Hermes cross-session durable memory uses one selected external `MemoryProvider`; Mnemosyne provider mode is planned. Do not expose the same memory bank through provider + MCP by default.
- Hermes hooks/middleware may provide telemetry/transformation/risk signals, but fail-open callback paths are not sole mandatory-security enforcement points.
- Policy-controlled external inference goes through a **localhost OpenAI-compatible gateway** selected through Hermes' supported custom-provider surface. Direct provider fallback is not allowed for requests/classes that require the gateway.
- Hermes→Pi uses Pi's documented **RPC mode over stdin/stdout**. Do not couple the bridge to Pi's internal/in-progress `AgentHarness` APIs.
- Unattended Pi defaults to **whole-process OCI-container containment** with a disposable workspace, no canonical-repo write authority, no external-provider credentials and no unrestricted internet. If no suitable OCI runtime exists, stop for an operator decision rather than silently switching sandbox architecture.
- Pi model calls use a custom OpenAI-compatible provider pointed at the policy gateway when external inference is required.
- Pi project extensions/skills/templates/themes/context files are disabled for the base worker and added back only through an explicit spec/task.
- The trusted LSP base does not depend on an arbitrary third-party Pi extension. Start read-only with diagnostics/definition/references/symbols; mutation/refactor support is a later promotion.
- Local model runtime is llama.cpp/Metal. Granite 4.2-8B Q6_K is the first admission candidate; Q5_K_M is triggered only by a concrete operational limitation; Empero Qwen3.8-9B-Distill is the single challenger if Granite fails.

## Lightweight specification workflow

For small bounded work, use the existing normative spec plus root `TASKS.md`; do not create another recap/task document.

Create a new normative spec only when a genuinely new bounded workstream introduces an interface, trust/security boundary, compatibility dependency or promotion gate. It MUST contain:

- desired outcome and non-goals;
- invariants/selected integration surface;
- compatibility target;
- measurable acceptance criteria;
- rollback/disable path;
- only the primary references needed to justify the design.

Create `plan.md` only when multiple dependent migration paths remain after the spec. ADRs are only for durable system/security/source-of-truth/dependency decisions.

See `docs/spec-lite.md`.

## Agent reading discipline

To limit token consumption:

1. Read this file.
2. Read the current item in root `TASKS.md`.
3. Read only the governing spec named by that milestone/task.
4. Read `docs/testing-strategy.md` before executing non-trivial tests.
5. Read `docs/evidence-policy.md` before producing/publishing runtime evidence.
6. Read `docs/build-readiness.md` only when a compatibility/readiness decision is relevant.
7. Use `docs/architecture.md` when a visual boundary map is useful.
8. Load research notes only when the active task explicitly needs their evidence.
9. Never load the entire evidence or research tree into context pre-emptively.
10. Persist findings to files; chat/session memory is not project state.

## Evidence discipline

Each completed task points to its declared local path under `evidence/`, `evals/`, `schemas/` or tests. Suitable evidence includes:

- deterministic test output;
- compact benchmark result;
- compatibility probe;
- schema validation;
- security negative test;
- reproducible command transcript;
- manual approval only when no machine-verifiable check exists.

`evidence/` is gitignored. A completed task does not imply its raw evidence should be committed. Publish only a manually reviewed/sanitized summary when useful.

Keep bulky raw logs out of routine agent prompts. Store them as files/artifacts and reference by path/hash.

## Status vocabulary

Use only:

- `proposed`
- `researching`
- `specified`
- `experimental`
- `validated`
- `rejected`
- `superseded`

`specified` means implementation intent is unambiguous enough to execute the declared next task. `validated` means the declared acceptance criteria were actually run against the pinned environment.

## Build-readiness rule

`docs/build-readiness.md` contains evidence-weighted readiness scores. Those scores are advisory and MUST NOT be confused with validation. Target-machine evidence is required to lift operational confidence above the pre-execution cap.

## Self-build bootstrap

When Hermes is used to build Foundry for itself, use `prompts/hermes-bootstrap.md`. The bootstrap prompt delegates task execution while preserving the architecture, fast-feedback and self-hosting safety rules in this repository.

## Current execution boundary

The repository is ready to begin **M0 only**. Execute root `TASKS.md` from T001. Do not perform M1–M3 changes before their predecessor milestone passes.
