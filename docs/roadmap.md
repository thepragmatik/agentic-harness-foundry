# Staged Roadmap

Status: `specified`

Goal: harvest low-risk savings first, prove each layer, and postpone complex routing/training until simpler controls have exhausted their value.

## Phase 0 — Establish truth before tuning

**Value:** prevents version drift and invalid specs. **Risk:** minimal.

- [ ] Record Apple hardware: chip, unified memory, macOS, thermal/power mode.
- [ ] Record exact Hermes version + commit/package source.
- [ ] Record exact Pi version + package source.
- [ ] Record LCM package/plugin version and active configuration.
- [ ] Record Mnemosyne version, integration path, embedding backend, capture/retrieval settings.
- [ ] Record exact llama.cpp version/commit and Metal build flags.
- [ ] Snapshot current Hermes configuration with secrets removed.
- [ ] Define one reversible baseline task corpus: research, tool-heavy, coding, long-context, memory-recall.
- [ ] Capture baseline: input/output/cache tokens, wall time, retries, task success, provider cost.

**Gate P0:** no implementation spec may target Hermes/Pi until the compatibility matrix exists.

---

## Phase 1 — Low-hanging token diet

**Value:** immediate paid-token reduction without learned routing. **Risk:** low.

- [ ] Identify static/repeated prompt material and deduplicate it.
- [ ] Measure provider prompt-cache reuse; stabilize prefix ordering where practical.
- [ ] Cap and normalize tool-result payloads before they enter the main model context.
- [ ] Blob/hash oversized artifacts and pass compact references plus selective excerpts.
- [ ] Remove redundant tool schemas/instructions from turns where they are unavailable or unnecessary, if Hermes' current extension surface safely supports it.
- [ ] Add per-turn telemetry for `raw_context_bytes -> sent_context_tokens`.

**Acceptance:** lower external input-token cost on matched tasks with no materially meaningful task-success regression.

**Rollback:** configuration-only or isolated adapter disable.

---

## Phase 2 — Local utility model qualification

**Value:** moves high-volume transformation work off paid providers. **Risk:** low-medium because summaries can omit evidence.

Keep the decision surface intentionally small. Follow [`docs/specs/local-model-admission.md`](specs/local-model-admission.md).

Failure-directed order:

1. `empero-ai/Qwen3.8-9B-Distill` Q6_K — primary.
2. Same model Q5_K_M — only if Q6 quality passes but sustained operation is limiting.
3. `google/gemma-4-E4B-it` — only if the Qwen distill fails on efficiency/runtime; its PLE/on-device architecture makes it the targeted efficiency challenger.
4. `Qwen/Qwen3.5-9B` — only if the distill fails on utility quality; this is the conservative quality fallback.

Only **one model path is active at a time**. Runtime is llama.cpp/Metal only.

Qualification workloads are deliberately compact:

- [ ] compiler/test/log distillation;
- [ ] large tool-output -> typed context packet;
- [ ] durable-memory candidate extraction;
- [ ] code/LSP diagnostic summarisation;
- [ ] schema-constrained structured output.

Measure only what changes the decision:

- [ ] load/TTFT;
- [ ] prompt and decode tok/s;
- [ ] total inference memory and swap delta at 16K context;
- [ ] one sustained 20-minute Hermes-shaped replay;
- [ ] critical evidence retention;
- [ ] schema validity.

**Gate P2:** promote the first model+quant configuration that fits the 28 GB inference envelope, remains stable through the sustained replay, and passes the compact utility-quality smoke test. Do not continue benchmarking for marginal gains after the gate is satisfied.

---

## Phase 3 — Recoverable local context distillation

**Value:** likely the highest local-model cost-saving opportunity. **Risk:** medium.

- [ ] Define `context-packet.schema.json` with provenance to original artifacts.
- [ ] Keep raw evidence separately addressable by path/hash; never make the summary the only copy.
- [ ] Add local distillation only for oversized tool/artifact classes with deterministic fallback to raw retrieval.
- [ ] Validate summaries against task-native checks where possible.
- [ ] Measure cloud-token reduction and retrieval-backtracking frequency.

**Gate P3:** promote per artifact class, not globally. A class fails if omitted evidence materially increases retries/errors.

---

## Phase 4 — Context and memory ownership

**Value:** prevents duplicate context work and memory inflation. **Risk:** medium.

- [ ] Specify LCM ownership: current-session context selection, compaction, recoverable hierarchy.
- [ ] Specify Mnemosyne ownership: curated cross-session durable memory only.
- [ ] Prohibit recursive/duplicate summarisation paths.
- [ ] Use local embeddings for sensitive memory unless an explicit egress policy permits otherwise.
- [ ] Add memory-admission criteria, provenance, expiry/review rules.
- [ ] Cap retrieval budget per turn and measure useful-recall precision.
- [ ] Test exact-detail recovery after multiple compactions.

**Gate P4:** LCM/Mnemosyne must beat a simpler baseline on accepted-task token economics and recall quality; either layer may be rejected independently.

---

## Phase 5 — Deterministic egress and trust boundary

**Value:** privacy/security improvement and safer external-model use. **Risk:** medium-high; must be fail-closed.

- [ ] Define provenance/trust labels for user, repo, web, tool, memory, generated content.
- [ ] Define deterministic provider eligibility and data-egress rules.
- [ ] Detect known secrets using deterministic mechanisms first.
- [ ] Tokenize/redact reversible sensitive values locally where useful.
- [ ] Treat local prompt-injection/PII classifiers as advisory signals only.
- [ ] Require independent authorization for destructive/high-risk tool actions.
- [ ] Red-team memory poisoning, indirect injection, exfiltration, and policy-bypass paths.

**Gate P5:** mandatory controls must fail closed; Hermes middleware alone is not sufficient if its failure semantics are fail-open.

---

## Phase 6 — Routing telemetry before routing intelligence

**Value:** creates evidence without production risk. **Risk:** low.

- [ ] Define privacy-minimized routing-decision record schema.
- [ ] Record deterministic eligibility decisions.
- [ ] Record actual model/provider/task outcomes and economics.
- [ ] Add shadow predictions from the selected local utility model only after telemetry is stable.
- [ ] Measure routing regret/opportunity before training anything.

**Gate P6:** if deterministic/simple routing leaves little recoverable economic regret, STOP. Do not train ModernBERT.

---

## Phase 7 — Learned routing experiment (conditional)

Run only if P6 proves an opportunity.

- [ ] Baseline: rules + linear/logistic classifier over compact features/embeddings.
- [ ] Challenger: nearest-neighbour/semantic routing.
- [ ] Challenger: ModernBERT multi-head classifier.
- [ ] Optional: local generative router only if the discriminative approaches fail the economic objective.
- [ ] Use mission/session/repository/time-separated holdouts.
- [ ] Calibrate abstention/uncertainty.
- [ ] Compare cost per accepted task, not classification accuracy alone.

**Gate P7:** promote only if the learned layer materially beats the simple baseline after its own latency/compute/retry costs.

---

## Phase 8 — Pi coding worker + LSP

**Value:** higher-quality edits with objective verification. **Risk:** high because this crosses execution boundaries.

- [ ] Pin Pi version and supported integration surface.
- [ ] Define Hermes -> Pi typed task contract.
- [ ] Run Pi in a disposable worktree/container/sandbox with least privilege.
- [ ] Deny direct production-repo mutation in unattended mode.
- [ ] Integrate LSP symbol lookup, diagnostics, rename/refactor, and post-edit diagnostics.
- [ ] Run compiler/tests/static checks as objective acceptance signals.
- [ ] Return structured diff + diagnostics + test evidence to Hermes.

**Gate P8:** no unattended promotion until containment, rollback, replay, and malicious-repo tests pass.

---

## Phase 9 — Documentation/site renderer

Can begin early but MUST NOT block optimisation experiments.

- [ ] Markdown remains the only authored prose source of truth.
- [ ] Render Markdown client-side or at build time with pinned dependencies.
- [ ] Render fenced Mermaid blocks using a pinned Mermaid version and strict security mode.
- [ ] Sanitize rendered HTML and enforce a restrictive CSP.
- [ ] Use a semantic, accessible diagram palette with textual labels.
- [ ] Add CI link/diagram/render validation.

---

# Early harvest order

```text
P0 truth
 -> P1 prompt/tool-result diet
 -> P2 one local model qualification
 -> P3 recoverable local distillation
 -> P4 LCM/Mnemosyne ownership
 -> P5 egress/security
 -> P6 telemetry
 -> P7 learned routing only if justified
 -> P8 Pi/LSP worker
```

This ordering intentionally puts **routing late** and keeps the local-model decision cheap. The first dollars/tokens should be saved through deterministic context hygiene and local, recoverable preprocessing.