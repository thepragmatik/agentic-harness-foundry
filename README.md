# Agentic Harness Foundry

A clean-slate research, architecture, specification, and validation repository for building a safer, cheaper, context-efficient agentic harness around **Hermes**, **Pi**, local inference, and external LLM providers.

> **Status:** specification-hardened and ready to begin M0 evidence capture. No production uplift is considered validated until the declared tests run on the target machine.

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
7. **Use stable public seams.** Execution agents stop rather than bind to undocumented/upstream-internal APIs.
8. **Cheapest falsifier first.** Expensive/long tests are earned by passing cheaper deterministic probes.

## Start the build with Hermes

When Hermes is building Foundry for itself, use the repository bootstrap prompt:

**[`prompts/hermes-bootstrap.md`](prompts/hermes-bootstrap.md)**

It tells the agent to execute the existing architecture rather than redesign it, start from the first unchecked task, use the fast-feedback ladder, keep evidence private, and protect the running Hermes instance from self-hosting failures.

## Fast feedback before deep work

The definitive testing policy is [`docs/testing-strategy.md`](docs/testing-strategy.md).

Its central rule is:

```text
static/preflight
    -> micro smoke
    -> small contract fixture
    -> milestone acceptance
    -> sustained/soak only after correctness passes
```

A repeated failure gets one classified retry with one justified variable changed; if it still fails, stop/revise rather than entering a tuning rabbit hole.

The explicitly prioritized low-hanging fruit is in [`docs/early-wins.md`](docs/early-wins.md).

## Current readiness

Evidence-weighted pre-execution scores are maintained in [`docs/build-readiness.md`](docs/build-readiness.md):

- **required-stack specification readiness (M0–M3): 97/100**;
- **required-stack operational confidence before local execution: 79/100**.

The operational score is intentionally capped by missing evidence from the actual Mac/installed stack. Completing T001 onward is how it rises; more broad research is no longer the default way to increase confidence.

## Fixed local-inference constraints

- **Runtime:** `llama.cpp` / Metal only.
- **Quantization:** `Q6_K` first; `Q5_K_M` only if Q6 quality passes but sustained operation benefits materially from Q5.
- **Host:** Apple Silicon laptop with 128 GB unified memory.
- **Inference envelope:** **28 GB total** for local-model weights + inference/runtime/KV/state. The rest is reserved for Hermes, Pi, LSPs, builds/tests, browser/tooling, and macOS.
- **Admission:** model support must be boring enough for stock upstream llama.cpp and survive a sustained Hermes-shaped replay on the target Mac.

## Current architecture posture

- **Context:** one Hermes `ContextEngine`; LCM is the planned current-session compaction/recovery authority.
- **Durable memory:** one external Hermes `MemoryProvider`; Mnemosyne provider mode is the planned cross-session authority. The same bank is not exposed through provider + MCP by default.
- **Resident local utility model:** qualify official `ibm-granite/granite-4.2-8b-GGUF` Q6_K first. Stop model selection if it passes the compact admission gate.
- **Q5:** try only if Granite Q6 quality passes but sustained operation needs more throughput/headroom.
- **One challenger:** `empero-ai/Qwen3.8-9B-Distill` Q6_K is tested only if Granite fails admission.
- **Original 2–4B fleet:** retained as a **candidate specialist shelf**, not discarded and not benchmarked in parallel.
- **Stacking:** prefer `local attempt -> deterministic verify -> cloud escalation`; avoid always-on multi-model voting/fusion.
- **Mandatory external egress:** policy-controlled external inference goes through a **localhost OpenAI-compatible gateway** selected via Hermes' supported custom-provider surface; mandatory-deny policy is independent of fail-open hooks/middleware.
- **Pi integration:** use Pi's documented **RPC mode over stdin/stdout**, not evolving internal AgentHarness APIs. Project-local resources are disabled by default and the worker runs behind a real containment boundary.
- **LSP:** start read-only (diagnostics/definition/references/symbols) through a minimal trusted adapter; no arbitrary third-party Pi LSP extension in the critical path.
- **Routing:** optional. Collect telemetry first; learned routing exists only if economic regret is proven.

## Low-hanging fruit

M0 is deliberately optimization-before-architecture. The first targets are:

1. duplicate context/memory injection;
2. oversized tool/log payloads that can be retained as raw artifacts and represented compactly;
3. repeated static prompt/tool-schema material;
4. avoidable prompt-prefix churn that harms provider cache reuse;
5. overlapping LCM/Mnemosyne work;
6. only after those are measured, one local-model context-packet pilot for the single noisiest artifact class.

Do these one at a time so the savings are attributable.

## Minimal roadmap

Only one milestone is active at a time:

```text
M0  baseline + deterministic token diet
 -> M1  Granite-first local utility + recoverable context packets
 -> M2  LCM/Mnemosyne ownership + fail-closed localhost egress gateway
 -> M3  contained Pi RPC worker + read-only-first LSP
 -> M4  routing only if telemetry proves value
```

See [`docs/roadmap.md`](docs/roadmap.md). The single executable checklist is root [`TASKS.md`](TASKS.md).

## Normative specifications

- [`docs/specs/local-model-admission.md`](docs/specs/local-model-admission.md) — one-path local-model qualification.
- [`docs/specs/m2-context-memory-security.md`](docs/specs/m2-context-memory-security.md) — context/memory ownership, provenance and fail-closed egress.
- [`docs/specs/m3-pi-worker-rpc.md`](docs/specs/m3-pi-worker-rpc.md) — Pi RPC process boundary, sandbox and staged LSP.
- [`docs/testing-strategy.md`](docs/testing-strategy.md) — fast-feedback ladder, circuit breaker and self-hosting test discipline.

Research notes support decisions but do not override these specifications.

## Lightweight specifications

The project uses a reduced Spec-Kit-inspired workflow. Small bounded work normally needs only:

```text
normative spec -> TASKS.md item -> evidence -> decision
```

Create another `plan.md` only for genuinely dependent migrations/architectural choices. See [`docs/spec-lite.md`](docs/spec-lite.md).

## Documentation model

Markdown is the authored source of truth. Human-facing HTML will render that same Markdown and fenced Mermaid diagrams; it is a presentation layer, not duplicated documentation. Site work is non-blocking until the execution architecture is proven.

- `AGENTS.md` — agent authority, reading discipline and stable integration choices
- `TASKS.md` — single executable task ledger
- `prompts/hermes-bootstrap.md` — self-build execution prompt
- `docs/testing-strategy.md` — cheap-to-expensive test ladder
- `docs/early-wins.md` — first optimization harvests
- `docs/build-readiness.md` — evidence-weighted readiness model
- `docs/roadmap.md` — milestone boundaries and stop rules
- `docs/specs/` — normative bounded specifications
- `docs/research/` — decision-support research only
- future `schemas/`, `evals/`, `evidence/` — created by execution tasks as needed rather than as empty ceremony

## Next gate

Execute **T001–T009 in `TASKS.md`** first. Do not download/qualify Granite or modify M2/M3 components until M0 passes and the installed stack has been pinned.
