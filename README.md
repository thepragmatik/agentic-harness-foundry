# Agentic Harness Foundry

A clean-slate research, architecture, specification, and validation repository for building a safer, cheaper, context-efficient agentic harness around **Hermes**, **Pi**, local inference, and external LLM providers.

> **Status:** research / specification. No production uplift code is trusted or inherited from prior prototypes.

## Mission

Design and validate an agentic harness that:

- reduces paid-token consumption without silently reducing task quality;
- treats context, durable memory, routing, security, and execution as separate ownership boundaries;
- uses local Apple Silicon inference where it has measurable economic or privacy value;
- keeps security-critical policy deterministic and fail-closed;
- integrates Hermes orchestration with a contained Pi coding worker and LSP-assisted edits;
- is reproducible against exact upstream versions/commits;
- is readable by humans and executable/unambiguous for agents.

## Clean-slate rules

1. **No inherited implementation authority.** Earlier repositories may be consulted only as evidence or failed-experiment archives. Their code, metrics, and architectural claims are not accepted without re-validation.
2. **Version-pin before implementation.** Every integration spec MUST name the upstream version/commit it targets and define a compatibility probe.
3. **Measure cost per accepted task.** Token count alone is not the objective; retries, cache effects, latency, local compute, and task success all matter.
4. **Keep raw evidence recoverable.** Local compression may reduce cloud context, but original artifacts remain addressable by stable provenance/hash wherever practical.
5. **Security is not delegated to an LLM.** Local or remote models may provide risk signals; deterministic policy controls authorization, egress, capabilities, and high-risk actions.
6. **Complexity must pay rent.** A learned router, extra memory layer, verifier, or model is promoted only if a simpler baseline fails a predeclared acceptance gate.

## Fixed local-inference constraints

To keep the decision surface small, the current local-model programme is intentionally constrained:

- **Runtime:** `llama.cpp` / Metal only. MLX is out of scope unless a future ADR reopens it.
- **Weight quantization:** `Q6_K` (or a documented Q6-equivalent only if plain Q6_K is unavailable).
- **Host:** Apple Silicon laptop with 128 GB unified memory.
- **Inference allocation:** **28 GB hard planning envelope** for model weights + runtime state + KV/cache required by the local inference service. The remaining system memory is reserved for Hermes, Pi, LSPs, builds/tests, browser/tooling, and macOS.
- **Admission:** a model MUST have credible llama.cpp support and MUST pass a sustained-session probe on the target Mac before integration work begins.

## Current research position

- **Context:** LCM is the leading working-context candidate, subject to recall/cost/cache-stability evaluation.
- **Durable memory:** Mnemosyne is the leading cross-session candidate, subject to a strict authority contract with LCM and local/private embeddings.
- **Local utility model:** the decision has narrowed to the **9B Q6 class**. `empero-ai/Qwen3.8-9B-Distill` is the highest-upside candidate; official `Qwen3.5-9B` is the conservative control. Neither is promoted until the short sustained-session qualification passes on the target Mac.
- **Large conditional-memory models:** Qwen3.8-Flash-Next and DeepSeek-V4.1-Flash are architecture research inputs, **not local deployment candidates** under the 28 GB/Q6/stock-llama.cpp constraint.
- **Routing:** deterministic eligibility first; learned routing is an optional experiment, not a roadmap assumption.
- **Security:** provenance + deterministic policy + least privilege + containment; model-based detectors are advisory.
- **Coding:** Pi is expected to operate as a contained worker behind Hermes, with LSP/compiler/test evidence used for verification.

## Execution order

See [`docs/roadmap.md`](docs/roadmap.md) for the low-risk, early-value checklist and promotion gates.

## Specifications

This project uses a deliberately lightweight Spec-Kit-inspired workflow. We keep durable Markdown artifacts, but do **not** install the full prompt-heavy workflow by default.

For each bounded change:

```text
spec.md  ->  plan.md  ->  tasks.md  ->  evidence  ->  decision
```

Only `spec.md` and `tasks.md` are mandatory for small changes. See [`docs/spec-lite.md`](docs/spec-lite.md).

## Documentation model

Markdown is the source of truth. Human-facing HTML will render the same Markdown and Mermaid diagrams; HTML is a presentation layer, not a second documentation source.

- `README.md` — project entry point
- `AGENTS.md` — agent navigation and authority rules
- `docs/` — architecture, research, specifications, ADRs, runbooks, benchmarks
- `schemas/` — machine-readable contracts
- `evals/` — reproducible evaluations
- `evidence/` — generated validation evidence, never unverifiable claims
- `site/` — pinned local Markdown/Mermaid renderer

## Research notes

- [`docs/research/apple-local-models.md`](docs/research/apple-local-models.md) — local-model candidate decision.
- [`docs/research/conditional-memory-architectures.md`](docs/research/conditional-memory-architectures.md) — Engram/PLE/n-gram architectures and why current flagships are outside the local deployment envelope.
- [`docs/specs/local-model-admission.md`](docs/specs/local-model-admission.md) — hard admission gates for any local model.

## Next gate

Do not modify Hermes or Pi yet. First complete the version/compatibility inventory and run the deliberately small local-model admission check defined in the roadmap.