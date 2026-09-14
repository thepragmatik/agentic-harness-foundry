# Execution Roadmap

Status: `specified`

Goal: harvest measurable value early, keep the number of active decisions small, and stop adding architecture once the operating requirement is met.

## Operating rules

- Only **one milestone is active** at a time.
- Only **one local-model path is qualified** at a time.
- Prefer configuration/adapters over Hermes/Pi core changes.
- Every lossy transformation keeps recoverable provenance to raw evidence.
- Security-critical policy is deterministic and fail-closed.
- Routing/training is optional and starts only if telemetry proves an economic gap.

---

## M0 — Baseline + deterministic token diet

**Outcome:** know the exact stack and remove obvious paid-token waste before adding another model or subsystem.

- [ ] Record Apple chip, 128 GB unified memory, macOS/power mode and the **28 GB local-inference envelope**.
- [ ] Pin Hermes, Pi, LCM, Mnemosyne and llama.cpp versions/commits.
- [ ] Snapshot active Hermes configuration with secrets removed.
- [ ] Capture a very small representative baseline: one tool-heavy task, one long-context/memory task and one coding task.
- [ ] Record external input/output/cache tokens, wall time, retries and success.
- [ ] Remove repeated/static prompt material where safe.
- [ ] Cap/normalize oversized tool output and retain large raw artifacts by path/hash.
- [ ] Stabilize reusable prompt prefixes where practical for provider cache reuse.

**Done when:** baseline is reproducible and at least the obvious deterministic context waste has been removed or explicitly found negligible.

**Stop rule:** do not build local-model preprocessing until the baseline exists; otherwise savings cannot be attributed.

---

## M1 — One resident local utility path + recoverable context packets

**Outcome:** move high-volume, recoverable transformations off paid providers with the smallest possible model-selection exercise.

Follow [`docs/specs/local-model-admission.md`](specs/local-model-admission.md).

Decision tree:

1. `empero-ai/Qwen3.8-9B-Distill` Q6_K.
2. Same model Q5_K_M only if Q6 quality passes but sustained operation is limiting.
3. Gemma 4 E4B only if Empero fails mainly on efficiency/runtime.
4. Official Qwen3.5-9B only if Empero fails mainly on utility quality.

The original 2–4B model fleet remains a **candidate shelf**, not an active benchmark pool. See [`docs/research/stacked-local-models.md`](research/stacked-local-models.md). A tiny specialist is admitted later only if production telemetry exposes a concrete recurring job where it materially beats the resident model end-to-end.

Qualification is limited to:

- [ ] memory/runtime/throughput at 16K context in llama.cpp/Metal;
- [ ] one 20-minute sustained Hermes-shaped replay;
- [ ] 10–20 utility examples: tool/log compression, structured extraction, memory-candidate extraction and code/LSP summary.

Once a model passes, **stop model selection** and implement one `context-packet` contract:

- [ ] typed compact result;
- [ ] source path/hash/provenance;
- [ ] selected exact excerpts where needed;
- [ ] deterministic fallback to raw evidence;
- [ ] per-artifact promotion, not global summarization.

**Done when:** one local configuration is operationally stable and at least one real artifact class shows material external-token reduction without material task-quality regression.

---

## M2 — Context/memory ownership + trust/egress controls

**Outcome:** eliminate duplicate context work and establish the security boundary before deeper autonomy.

Treat these as one architecture milestone because the same provenance/trust metadata feeds both context selection and egress policy.

### Context and memory

- [ ] LCM owns current-session context selection/compaction/recovery.
- [ ] Mnemosyne owns curated cross-session durable memory only.
- [ ] Prohibit recursive/duplicate summarisation paths.
- [ ] Use local/private embeddings for sensitive memory unless policy explicitly permits egress.
- [ ] Define memory admission, provenance, expiry/review and per-turn retrieval budget.
- [ ] Test exact-detail recovery after compaction.

### Trust and egress

- [ ] Label provenance/trust for user, repo, web, tool, memory and generated content.
- [ ] Define deterministic provider/data eligibility rules.
- [ ] Detect known secrets deterministically first; reversible local substitution where useful.
- [ ] Treat model-based injection/PII/security scores as advisory only.
- [ ] Independently authorize destructive/high-risk actions.
- [ ] Test prompt injection, memory poisoning and exfiltration paths.

**Done when:** context/memory authorities are unambiguous, required controls fail closed, and the simplified stack beats or matches the pre-M2 baseline on accepted-task economics and recall.

**Simplification rule:** if either LCM or Mnemosyne fails to add measurable value under this ownership contract, remove that layer rather than tuning indefinitely.

---

## M3 — Hermes -> contained Pi + LSP execution

**Outcome:** add coding capability only after context and trust boundaries are stable.

- [ ] Pin Pi version/integration surface.
- [ ] Define one typed Hermes -> Pi task/result contract.
- [ ] Run Pi in a disposable worktree plus OS/container sandbox with least privilege.
- [ ] Prevent unattended direct mutation of the canonical repo.
- [ ] Add only high-value LSP operations: symbol lookup, references, diagnostics, rename/refactor where supported.
- [ ] Verify edits with compiler/tests/static checks and post-edit LSP diagnostics.
- [ ] Return structured diff + diagnostics + test evidence to Hermes.

**Done when:** containment, rollback, replay and malicious-repo tests pass and a coding task can execute end-to-end without widening Hermes' authority unnecessarily.

---

## M4 — Optional routing intelligence

**Outcome:** do nothing unless real telemetry proves that model-selection mistakes are costing enough to matter.

Always collect lightweight decision telemetry during M0–M3:

- eligible model/provider set;
- chosen path;
- task/workflow stage;
- tokens/cache/latency/cost;
- retry/escalation;
- objective acceptance outcome where available.

Only if analysis shows material recoverable routing regret:

1. try deterministic rules/simple scores first;
2. then a linear/embedding baseline;
3. only then consider ModernBERT or a learned harness-native router.

A local generative router or multi-model committee is not a default milestone.

**Done when:** either telemetry shows routing is not worth pursuing (**valid success state**) or a simple router materially improves cost per accepted task.

---

## Documentation and HTML rendering — continuous, non-blocking

Markdown remains the only authored source of truth. Add the HTML/Mermaid renderer incrementally when useful, but it MUST NOT gate M0–M3.

Required properties when implemented:

- pinned local Markdown/Mermaid/sanitizer dependencies;
- strict Mermaid security mode and restrictive CSP;
- accessible semantic diagram palette;
- no duplicated prose between Markdown and HTML.

---

# Minimal execution order

```text
M0 baseline + token diet
  -> M1 one local model + context packets
  -> M2 context/memory + security
  -> M3 Pi/LSP
  -> M4 routing only if telemetry proves value
```

This is the complete default roadmap. New phases/components require an explicit reason that cannot be satisfied inside one of these milestones.