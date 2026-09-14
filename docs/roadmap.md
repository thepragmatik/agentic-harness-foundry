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
- [ ] Record llama.cpp and/or MLX runtime versions.
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

**Acceptance:** lower external input-token cost on matched tasks with no statistically/materially meaningful task-success regression.

**Rollback:** configuration-only or isolated adapter disable.

---

## Phase 2 — Local utility model bake-off

**Value:** moves high-volume transformation work off paid providers. **Risk:** low-medium because summaries can omit evidence.

Candidates:

1. `Qwen3.5-9B` MLX 5/6-bit — default champion.
2. `Qwen3.8-27B` MLX 4-bit — burst quality challenger.
3. one small model already available locally (start with `MiniCPM5-2B`) — speed/efficiency baseline.

Benchmark workloads:

- [ ] compiler/test/log distillation;
- [ ] large tool-output -> typed context packet;
- [ ] repository/LSP diagnostic summarisation;
- [ ] durable-memory candidate extraction;
- [ ] structured extraction with JSON-schema validation;
- [ ] query rewrite / retrieval intent extraction;
- [ ] context-summary factual retention and exact-evidence pointer quality.

Measure:

- [ ] cold start and warm first-token latency;
- [ ] prompt processing tok/s;
- [ ] decode tok/s;
- [ ] peak unified memory at 4K/8K/16K/32K input bands;
- [ ] laptop power/thermal throttling over sustained runs;
- [ ] output factuality/retention;
- [ ] schema validity;
- [ ] cloud tokens avoided per accepted task;
- [ ] local milliseconds/joules per cloud token avoided where practical.

**Gate P2:** choose one resident utility model only if it improves total accepted-task economics and fits alongside Hermes + Pi + LSP/build workloads with safe memory headroom.

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
- [ ] Add shadow predictions from one small/local candidate only after telemetry is stable.
- [ ] Measure routing regret/opportunity before training anything.

**Gate P6:** if deterministic/simple routing leaves little recoverable economic regret, STOP. Do not train ModernBERT.

---

## Phase 7 — Learned routing experiment (conditional)

Run only if P6 proves an opportunity.

- [ ] Baseline: rules + linear/logistic classifier over compact features/embeddings.
- [ ] Challenger: nearest-neighbour/semantic routing.
- [ ] Challenger: ModernBERT multi-head classifier.
- [ ] Optional: local generative router.
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

The recommended order for fastest safe value is:

```text
P0 truth
 -> P1 prompt/tool-result diet
 -> P2 local utility benchmark
 -> P3 recoverable local distillation
 -> P4 LCM/Mnemosyne ownership
 -> P5 egress/security
 -> P6 telemetry
 -> P7 learned routing only if justified
 -> P8 Pi/LSP worker
```

This ordering intentionally puts **routing late**. The first dollars/tokens should be saved through deterministic context hygiene and local, recoverable preprocessing rather than through a learned model-selection policy.