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

## Current research position

- **Context:** LCM is the leading working-context candidate, subject to recall/cost/cache-stability evaluation.
- **Durable memory:** Mnemosyne is the leading cross-session candidate, subject to a strict authority contract with LCM and local/private embeddings.
- **Local utility model:** `Qwen3.5-9B` is the current always-on Apple Silicon candidate. `Qwen3.8-27B` is a burst/benchmark challenger, not the default resident model.
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

## Research sources currently informing the baseline

- Qwen3.8 official repository: https://github.com/QwenLM/Qwen3.8
- Qwen3.5-9B model card: https://huggingface.co/Qwen/Qwen3.5-9B
- Qwen3.8-27B model card: https://huggingface.co/Qwen/Qwen3.8-27B
- MLX Qwen3.5-9B 5-bit: https://huggingface.co/mlx-community/Qwen3.5-9B-5bit
- MLX Qwen3.8-27B 4-bit: https://huggingface.co/mlx-community/Qwen3.8-27B-4bit
- GitHub Spec Kit: https://github.com/github/spec-kit

## Next gate

Do not modify Hermes or Pi yet. First complete the version/compatibility inventory and local-model benchmark harness defined in the roadmap.