# Execution Roadmap

Status: `specified`

Goal: harvest measurable value early, keep active decisions small, and stop adding architecture once the operating requirement is met.

## Operating rules

- Only **one milestone is active** at a time.
- Only **one local-model path is qualified** at a time.
- Prefer documented configuration/public integration surfaces over Hermes/Pi core changes.
- Every lossy transformation keeps recoverable provenance to raw evidence.
- Security-critical policy is deterministic and fail-closed.
- Routing/training is optional and starts only if telemetry proves an economic gap.
- `TASKS.md` is the execution ledger; this roadmap defines milestone boundaries only.
- `docs/testing-strategy.md` governs test ordering: cheapest falsifier first; soak/full acceptance only after cheaper probes pass.
- `docs/early-wins.md` defines the first optimization harvests.
- `docs/build-readiness.md` tracks specification vs operational confidence; documentation alone cannot lift operational confidence above the pre-execution cap.

---

## M0 — Baseline + deterministic token diet

**Outcome:** know the exact stack and remove obvious paid-token waste before adding another model or subsystem.

This is the primary low-hanging-fruit milestone:

- pin hardware/software/configuration truth;
- capture three representative baseline tasks;
- record token/cache/latency/retry/success metrics;
- detect duplicate context/memory injection;
- remove obvious repeated prompt/tool-result/tool-schema waste one change at a time;
- preserve raw oversized artifacts by path/hash while keeping only needed prompt material;
- stabilize reusable prompt prefixes where practical;
- identify LCM/Mnemosyne overlap before tuning either layer.

**Done when:** the baseline is reproducible and obvious deterministic context waste has been removed or explicitly found negligible.

**Stop rule:** do not build local-model preprocessing until the baseline exists.

---

## M1 — One resident local utility path + recoverable context packets

**Outcome:** move high-volume, recoverable transformations off paid providers with the smallest possible model-selection exercise.

Follow `docs/specs/local-model-admission.md`.

Decision tree:

1. `ibm-granite/granite-4.2-8b-GGUF` Q6_K.
2. Same model Q5_K_M only if Q6 quality passes but sustained operation is limiting.
3. `empero-ai/Qwen3.8-9B-Distill` Q6_K only if Granite fails the admission gate.
4. Stop model selection after a passing configuration; if both fail, revisit requirements instead of opening a broad bake-off.

The original 2–4B fleet remains a **candidate specialist shelf**, not an active benchmark pool. A second local model is admitted later only if real telemetry exposes a recurring job where it materially beats the resident model end-to-end.

Qualification order is deliberately cheap-to-expensive:

1. runtime/memory + one tiny structured response at 16K;
2. exactly four synthetic utility falsifiers with sentinel/schema checks;
3. only then one 20-minute sustained Hermes-shaped replay.

Once a model qualifies, implement one recoverable `context-packet` contract and prove it on exactly one high-volume artifact class first. Passing model admission does not by itself prove production value.

**Done when:** one local configuration is operationally stable and one real artifact class shows material external-token reduction without material task-quality regression.

---

## M2 — Context/memory ownership + fail-closed egress

**Outcome:** eliminate duplicate context work and establish the mandatory external-data boundary before deeper autonomy.

Follow `docs/specs/m2-context-memory-security.md`.

Selected architecture:

- LCM is the single current-session `ContextEngine` authority;
- Mnemosyne is the single external cross-session `MemoryProvider` authority;
- duplicate Mnemosyne provider+MCP injection is prohibited by default;
- sensitive memory embeddings remain local unless explicitly allowed;
- provenance/trust/sensitivity metadata is shared by context and egress decisions;
- policy-controlled external inference targets a **localhost OpenAI-compatible gateway** through Hermes' documented custom-provider seam;
- external provider credentials required by that route stay outside the policy-controlled Hermes process/profile wherever practical;
- hook/middleware/model risk signals are advisory, never the sole mandatory deny boundary.

Testing starts with ownership checks and single synthetic LCM/Mnemosyne fixtures. Gateway allow/deny/timeout/malformed-policy behavior is proven against a fake local upstream before any real provider path is exercised.

**Done when:** ownership/recovery/memory-budget tests and all fail-closed/injection/poisoning/gateway-bypass tests pass, and rollback is exercised in a disposable profile.

**Simplification rule:** if LCM or Mnemosyne fails to add distinct measured value, remove the non-paying layer rather than tuning indefinitely.

---

## M3 — Hermes → contained Pi RPC worker + LSP

**Outcome:** add coding execution through a stable process boundary without widening Hermes or host authority unnecessarily.

Follow `docs/specs/m3-pi-worker-rpc.md`.

Selected architecture:

- Hermes delegates through Pi's documented `--mode rpc` stdin/stdout protocol, not internal AgentHarness APIs;
- project-local extensions/skills/templates/themes/context files are disabled by default;
- the unattended baseline uses **whole-process OCI-container containment** with a disposable workspace and no canonical-repo write authority;
- the Pi worker has no external-provider credentials and no unrestricted internet; model traffic reaches only the policy gateway;
- the trusted LSP path is minimal/read-only first: diagnostics, definition, references and symbols;
- write/refactor capability is promoted only after read-only LSP and containment pass;
- compiler/tests/static checks/post-edit diagnostics provide objective evidence.

Testing starts with RPC/process framing, resource-disable behavior and write/network denial. One bounded coding task is attempted only after those cheap probes and read-only LSP pass.

**Done when:** RPC compatibility, project-resource isolation, canonical-repo protection, gateway-only model access, credential/network containment, timeout/crash behavior, read-only LSP, one bounded edit and replay/rollback all pass.

---

## M4 — Optional routing intelligence

**Outcome:** do nothing unless real telemetry proves model-selection mistakes are costing enough to matter.

Collect lightweight decision telemetry during M0–M3: eligible model/provider set, chosen path, task/workflow stage, tokens/cache/latency/cost, retry/escalation and objective acceptance outcome where available.

Only if analysis shows material recoverable routing regret:

1. deterministic rules/simple scores;
2. linear/embedding baseline;
3. ModernBERT or another learned harness-native router only if the simple baseline leaves material value.

A local generative router or multi-model committee is not a default milestone.

**Done when:** either telemetry shows routing is not worth pursuing (**valid success state**) or a simple router materially improves cost per accepted task.

---

## Documentation and HTML rendering — continuous, non-blocking

Markdown remains the authored source of truth. `docs/architecture.md` contains the Mermaid system/trust diagram. HTML rendering is presentation-only and MUST NOT gate M0–M3.

When implemented, the renderer uses pinned local Markdown/Mermaid/sanitizer dependencies, strict Mermaid security mode, restrictive CSP, accessible labels and no duplicated prose.

---

# Minimal execution order

```text
M0 baseline + token diet
  -> M1 Granite-first local utility + context packets
  -> M2 LCM/Mnemosyne + localhost policy gateway
  -> M3 Pi RPC + OCI containment + read-only-first LSP
  -> M4 routing only if telemetry proves value
```

This is the complete default roadmap. Detailed executable items live in root `TASKS.md`. New phases/components require an explicit reason that cannot be satisfied inside one of these milestones.
