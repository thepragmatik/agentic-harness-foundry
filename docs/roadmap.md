# Execution Roadmap

Status: `specified`

Goal: harvest measurable value early, keep active decisions small, and stop adding architecture once the operating requirement is met.

## Operating rules

- Only **one milestone is active** at a time.
- Only **one local-model path is qualified** at a time.
- Prefer configuration/adapters over Hermes/Pi core changes.
- Every lossy transformation keeps recoverable provenance to raw evidence.
- Security-critical policy is deterministic and fail-closed.
- Routing/training is optional and starts only if telemetry proves an economic gap.
- `TASKS.md` is the execution ledger; this roadmap defines milestone boundaries only.

---

## M0 — Baseline + deterministic token diet

**Outcome:** know the exact stack and remove obvious paid-token waste before adding another model or subsystem.

- pin hardware/software/configuration truth;
- capture three representative baseline tasks;
- record token/cache/latency/retry/success metrics;
- remove obvious repeated prompt/tool-result waste;
- preserve raw oversized artifacts by path/hash;
- stabilize reusable prompt prefixes where practical.

**Done when:** the baseline is reproducible and obvious deterministic context waste has been removed or explicitly found negligible.

**Stop rule:** do not build local-model preprocessing until the baseline exists.

---

## M1 — One resident local utility path + recoverable context packets

**Outcome:** move high-volume, recoverable transformations off paid providers with the smallest possible model-selection exercise.

Follow [`docs/specs/local-model-admission.md`](specs/local-model-admission.md).

Decision tree:

1. `ibm-granite/granite-4.2-8b-GGUF` Q6_K.
2. Same model Q5_K_M only if Q6 quality passes but sustained operation is limiting.
3. `empero-ai/Qwen3.8-9B-Distill` Q6_K only if Granite fails the admission gate.
4. Stop model selection after a passing configuration; if both fail, revisit requirements instead of opening a broad bake-off.

The original 2–4B fleet remains a **candidate specialist shelf**, not an active benchmark pool. A second local model is admitted later only if real telemetry exposes a recurring job where it materially beats the resident model end-to-end.

Qualification is limited to:

- memory/runtime/throughput at 16K context in llama.cpp/Metal;
- one 20-minute sustained Hermes-shaped replay;
- 10–20 utility examples: tool/log compression, structured extraction, memory-candidate extraction and code/LSP summary.

Once a model passes, implement one `context-packet` contract with typed result, source path/hash/provenance, selected exact excerpts where needed, deterministic fallback to raw evidence, and per-artifact promotion rather than global summarization.

**Done when:** one local configuration is operationally stable and at least one real artifact class shows material external-token reduction without material task-quality regression.

---

## M2 — Context/memory ownership + trust/egress controls

**Outcome:** eliminate duplicate context work and establish the security boundary before deeper autonomy.

### Context and memory

- LCM owns current-session context selection/compaction/recovery.
- Mnemosyne owns curated cross-session durable memory only.
- Recursive/duplicate summarisation paths are prohibited.
- Sensitive memory uses local/private embeddings unless policy explicitly permits egress.
- Memory admission, provenance, expiry/review and per-turn retrieval budget are explicit.
- Exact-detail recovery after compaction is tested.

### Trust and egress

- provenance/trust labels exist for user, repo, web, tool, memory and generated content;
- provider/data eligibility rules are deterministic;
- known secrets are detected deterministically first, with reversible local substitution where useful;
- model-based injection/PII/security scores remain advisory;
- destructive/high-risk actions require independent authorization;
- prompt injection, memory poisoning and exfiltration paths are tested.

**Done when:** context/memory authorities are unambiguous, required controls fail closed, and the simplified stack beats or matches the pre-M2 baseline on accepted-task economics and recall.

**Simplification rule:** if either LCM or Mnemosyne fails to add measurable value under this ownership contract, remove that layer rather than tuning indefinitely.

---

## M3 — Hermes -> contained Pi + LSP execution

**Outcome:** add coding capability only after context and trust boundaries are stable.

- pin Pi version/integration surface;
- define one typed Hermes -> Pi task/result contract;
- run Pi in a disposable worktree plus OS/container sandbox with least privilege;
- prevent unattended direct mutation of the canonical repo;
- add only high-value LSP operations: symbol lookup, references, diagnostics, rename/refactor where supported;
- verify edits with compiler/tests/static checks and post-edit LSP diagnostics;
- return structured diff + diagnostics + test evidence to Hermes.

**Done when:** containment, rollback, replay and malicious-repo tests pass and a coding task can execute end-to-end without widening Hermes' authority unnecessarily.

---

## M4 — Optional routing intelligence

**Outcome:** do nothing unless real telemetry proves model-selection mistakes are costing enough to matter.

Collect lightweight decision telemetry during M0–M3: eligible model/provider set, chosen path, task/workflow stage, tokens/cache/latency/cost, retry/escalation, and objective acceptance outcome where available.

Only if analysis shows material recoverable routing regret:

1. deterministic rules/simple scores;
2. linear/embedding baseline;
3. ModernBERT or learned harness-native router only if the simple baseline leaves material value.

A local generative router or multi-model committee is not a default milestone.

**Done when:** either telemetry shows routing is not worth pursuing (**valid success state**) or a simple router materially improves cost per accepted task.

---

## Documentation and HTML rendering — continuous, non-blocking

Markdown remains the authored source of truth. HTML/Mermaid rendering is presentation-only and MUST NOT gate M0–M3.

Required properties when implemented: pinned local dependencies, strict Mermaid security mode, restrictive CSP, accessible semantic palette, and no duplicated prose.

---

# Minimal execution order

```text
M0 baseline + token diet
  -> M1 Granite-first local utility + context packets
  -> M2 context/memory + security
  -> M3 Pi/LSP
  -> M4 routing only if telemetry proves value
```

This is the complete default roadmap. Detailed executable items live in root [`TASKS.md`](../TASKS.md). New phases/components require an explicit reason that cannot be satisfied inside one of these milestones.
