# Agentic Harness Foundry

A clean-slate research, architecture, specification, and validation repository for building a safer, cheaper, context-efficient agentic harness around **Hermes**, **Pi**, local inference, and external LLM providers.

> **Status:** research / specification. No production uplift code is trusted or inherited from prior prototypes.

## Mission

Design and validate an agentic harness that:

- reduces paid-token consumption without silently reducing task quality;
- treats context, durable memory, security, routing, and execution as separate ownership boundaries;
- uses local Apple Silicon inference only where it has measurable economic, latency, or privacy value;
- keeps security-critical policy deterministic and fail-closed;
- integrates Hermes orchestration with a contained Pi coding worker and LSP-assisted edits;
- is reproducible against exact upstream versions/commits;
- is readable by humans and unambiguous for agents.

## Clean-slate rules

1. **No inherited implementation authority.** Earlier repositories are evidence/failed-experiment archives only.
2. **Version-pin before implementation.** Every upstream integration declares the tested version/commit and a compatibility probe.
3. **Measure cost per accepted task.** Tokens, cache effects, retries, latency, local compute, and task success all count.
4. **Keep raw evidence recoverable.** Compression never becomes the only copy of important evidence.
5. **Security is not delegated to an LLM.** Models may provide signals; deterministic policy controls authorization/egress.
6. **Complexity must pay rent.** A second model, memory layer, router, or verifier is added only after a measured gap exists.

## Fixed local-inference constraints

- **Runtime:** `llama.cpp` / Metal only.
- **Quantization:** `Q6_K` first; `Q5_K_M` only if Q6 quality passes but sustained operation benefits materially from Q5.
- **Host:** Apple Silicon laptop with 128 GB unified memory.
- **Inference envelope:** **28 GB total** for local-model weights + inference/runtime/KV/state. The rest is reserved for Hermes, Pi, LSPs, builds/tests, browser/tooling, and macOS.
- **Admission:** model support must be boring enough for stock upstream llama.cpp and survive a sustained Hermes-shaped replay on the target Mac.

## Current architecture posture

- **Context:** LCM is the leading current-session context/compaction candidate, subject to measured recall/cache/token benefit.
- **Durable memory:** Mnemosyne is the leading cross-session candidate, with an explicit non-overlap contract with LCM.
- **Resident local utility model:** qualify official `ibm-granite/granite-4.2-8b-GGUF` Q6_K first. Stop model selection if it passes the compact admission gate.
- **Q5:** try only if Granite Q6 quality passes but sustained operation needs more throughput/headroom.
- **One challenger:** `empero-ai/Qwen3.8-9B-Distill` Q6_K is tested only if Granite fails admission.
- **Original 2–4B fleet:** retained as a **candidate specialist shelf**, not discarded and not benchmarked in parallel. A second model enters only for a measured recurring workload where it materially improves end-to-end operation.
- **Stacking:** prefer `local attempt -> deterministic verify -> cloud escalation`; avoid always-on multi-model voting/fusion.
- **Routing:** optional. Collect telemetry first; learned routing exists only if economic regret is proven.
- **Security:** provenance + deterministic policy + least privilege + containment; model detectors are advisory.
- **Coding:** Pi is intended to become a contained worker behind Hermes with LSP/compiler/test evidence.

## Minimal roadmap

Only one milestone is active at a time:

```text
M0  baseline + deterministic token diet
 -> M1  Granite-first local utility + recoverable context packets
 -> M2  context/memory ownership + deterministic trust/egress
 -> M3  contained Pi + LSP
 -> M4  routing only if telemetry proves value
```

See [`docs/roadmap.md`](docs/roadmap.md). The executable checklist is root [`TASKS.md`](TASKS.md).

## Lightweight specifications

The project uses a deliberately reduced Spec-Kit-inspired workflow. Small bounded work normally needs only:

```text
spec.md -> tasks.md -> evidence -> decision
```

Add `plan.md` only for genuinely non-trivial architecture/migration/security work. See [`docs/spec-lite.md`](docs/spec-lite.md).

## Documentation model

Markdown is the authored source of truth. Human-facing HTML will render that same Markdown and fenced Mermaid diagrams; it is a presentation layer, not duplicated documentation.

- `README.md` — project entry point
- `AGENTS.md` — agent navigation/authority rules
- `TASKS.md` — single executable task ledger
- `docs/roadmap.md` — milestone boundaries and stop rules
- `docs/specs/` — normative bounded specifications
- `docs/research/` — decision-support research, not implementation authority
- `schemas/` — machine-readable contracts when actually needed
- `evals/` / `evidence/` — compact reproducible validation artifacts
- `site/` — optional pinned Markdown/Mermaid renderer, non-blocking

## Research notes

- [`docs/research/stacked-local-models.md`](docs/research/stacked-local-models.md) — original local fleet, model stacking/cascades, and the one-specialist rule.
- [`docs/research/apple-local-models.md`](docs/research/apple-local-models.md) — Apple Silicon candidate assessment.
- [`docs/research/conditional-memory-architectures.md`](docs/research/conditional-memory-architectures.md) — Engram/PLE/n-gram architectures and practical local implications.
- [`docs/specs/local-model-admission.md`](docs/specs/local-model-admission.md) — hard local-model decision gate.

## Next gate

Do not modify Hermes or Pi yet. Execute **T001–T009 in `TASKS.md`** first. Only after M0 passes should Granite 4.2-8B qualification begin.
