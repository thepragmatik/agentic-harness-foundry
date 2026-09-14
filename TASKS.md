# Execution Tasks

Status: `specified`

This is the **single execution ledger**. Work top-to-bottom. Only one unchecked task may be treated as active unless a task explicitly says it can run in parallel.

## M0 — baseline + deterministic token diet

- [ ] **T001 Capture host identity**
  - Record: Apple chip, 128 GB unified memory, macOS version, power mode.
  - Verify: `system_profiler SPHardwareDataType SPSoftwareDataType`
  - Evidence: `evidence/m0/host.txt`
  - Stop if: none.

- [ ] **T002 Pin llama.cpp**
  - Record exact binary version/commit and Metal backend availability.
  - Verify: `llama-cli --version` and one no-model startup/help check.
  - Evidence: `evidence/m0/llama-version.txt`
  - Stop if: llama.cpp/Metal is not available; fix runtime before model work.

- [ ] **T003 Pin Hermes**
  - Record exact Hermes version/package source and active profile/config path with secrets redacted.
  - Verify: `hermes --version`; export/read config using the installed Hermes-supported command only.
  - Evidence: `evidence/m0/hermes-version.txt`, `evidence/m0/hermes-config.redacted.*`
  - Stop if: version or active config cannot be identified unambiguously.

- [ ] **T004 Pin Pi, LCM and Mnemosyne**
  - Record exact versions/package sources and active integration paths. Do not change them.
  - Evidence: `evidence/m0/components.md`
  - Stop if: more than one Mnemosyne integration path is active unintentionally; record as a finding before proceeding.

- [ ] **T005 Define three baseline tasks**
  - Create exactly three replayable tasks: tool-heavy, long-context/memory, coding.
  - Keep fixtures small and non-sensitive.
  - Evidence: `evals/baseline/README.md` plus fixtures.
  - Stop if: a task cannot be replayed deterministically enough to compare before/after.

- [ ] **T006 Capture baseline economics**
  - Run each baseline task once under the existing stack with no uplift changes.
  - Record: external input/output/cache tokens where exposed, wall time, retries, provider/model, success/failure.
  - Evidence: `evidence/m0/baseline.jsonl`
  - Stop if: token/cost telemetry is unavailable; define the nearest reproducible proxy before continuing.

- [ ] **T007 Inventory deterministic token waste**
  - Inspect one trace from each baseline task for repeated static prompt text, duplicate tool schemas, oversized tool payloads, and unstable reusable prefixes.
  - Evidence: `evidence/m0/token-waste.md`
  - Stop if: none.

- [ ] **T008 Apply only obvious reversible token-diet changes**
  - Allowed: configuration or isolated adapter changes that remove duplication/cap oversized payloads while retaining raw evidence by path/hash.
  - Not allowed: local-model summarization, routing, Hermes/Pi core patches.
  - Evidence: exact diff/config change + rollback command in `evidence/m0/token-diet.md`.
  - Stop if: the change requires a core patch or loses raw evidence.

- [ ] **T009 Re-run baseline and decide M0**
  - Re-run T006 tasks and compare accepted-task quality, tokens/cost and latency.
  - Pass: no material quality regression and deterministic waste is reduced or proven negligible.
  - Evidence: `evidence/m0/decision.md`
  - Stop if: regression is material; roll back T008 before M1.

## M1 — one local utility model + recoverable context packets

Run only after T009 passes.

- [ ] **T101 Pin Granite 4.2-8B Q6 artifact**
  - Candidate: `ibm-granite/granite-4.2-8b-GGUF` Q6_K.
  - Record model repo revision, exact GGUF filename, SHA256, license.
  - Evidence: `evidence/m1/granite-manifest.md`
  - Stop if: artifact provenance is ambiguous or requires a non-stock runtime.

- [ ] **T102 Run Q1 runtime/memory admission**
  - Use pinned llama.cpp/Metal at 16K context.
  - Record load time, TTFT, prompt/decode tok/s, total inference memory and swap delta.
  - Pass: total local-inference service remains inside 28 GB and does not cause sustained swap growth.
  - Evidence: `evidence/m1/granite-q1.json`
  - Stop if: hard envelope fails.

- [ ] **T103 Run Q2 sustained replay**
  - Run the 20-minute Hermes-shaped replay from `docs/specs/local-model-admission.md`.
  - Record per-interval throughput, slowest 5-minute window, memory trend, stalls/errors.
  - Evidence: `evidence/m1/granite-q2.json`
  - Stop if: correctness degrades, server stalls, memory grows without bound, or thermals make the service operationally unusable.

- [ ] **T104 Run Q3 compact utility smoke test**
  - Use only 10–20 fixed examples covering log/tool compression, schema extraction, memory candidates and code/LSP summaries.
  - Evidence: `evidence/m1/granite-q3.json`
  - Stop if: critical evidence is omitted or structured-output reliability is inadequate.

- [ ] **T105 Decide Q6 vs Q5**
  - If T102–T104 pass comfortably: promote Q6 and skip Q5.
  - Run Q5_K_M only if Q6 quality passes but sustained throughput/headroom is materially limiting.
  - Evidence: `evidence/m1/quant-decision.md`

- [ ] **T106 Trigger Empero challenger only if Granite fails**
  - Candidate: `empero-ai/Qwen3.8-9B-Distill` Q6_K.
  - Repeat only T101–T104 equivalents.
  - If both Granite and Empero fail: stop local-model integration and revisit requirements; do not open a broad bake-off.
  - Evidence: `evidence/m1/empero-*` only if triggered.

- [ ] **T107 Define minimal context-packet schema**
  - Fields MUST include source identity/hash, compact content, exact excerpts where needed, uncertainty/omissions, and raw-evidence retrieval pointer.
  - Evidence: `schemas/context-packet.schema.json` plus a schema-validation test.
  - Stop if: provenance requires embedding raw secrets in the packet.

- [ ] **T108 Prove one token-saving artifact class**
  - Apply the promoted local model to exactly one high-volume artifact class first (for example compiler/test/log output).
  - Compare external tokens, task outcome, backtracking/retrieval and latency against M0.
  - Pass: material external-token reduction with no material accepted-task quality regression.
  - Evidence: `evidence/m1/context-packet-pilot.md`
  - Stop if: omissions cause retries/errors often enough to erase the gain.

## M2 — context/memory + trust/egress

- [ ] **T201 Write one ownership contract** for LCM, Mnemosyne and raw Hermes history; no overlapping authority.
- [ ] **T202 Measure LCM/Mnemosyne benefit** on the existing long-context baseline; remove any layer that does not pay for itself.
- [ ] **T203 Define provenance/trust labels** shared by context and egress.
- [ ] **T204 Define deterministic provider/data eligibility rules** and fail-closed behavior.
- [ ] **T205 Run three red-team cases**: indirect injection, memory poisoning, and attempted sensitive-data egress.

Each M2 task MUST get a bounded spec before implementation because it crosses data/security ownership boundaries.

## M3 — contained Pi + LSP

- [ ] **T301 Pin Pi integration surface** and write the typed Hermes→Pi task/result contract.
- [ ] **T302 Establish disposable worktree + sandbox boundary** with no unattended canonical-repo mutation.
- [ ] **T303 Add only symbol lookup/references/diagnostics first**; postpone refactoring operations until read-only LSP use is stable.
- [ ] **T304 Run one end-to-end coding task** with diff + compiler/tests + post-edit diagnostics returned to Hermes.
- [ ] **T305 Run rollback/replay/malicious-repo checks** before unattended use.

## M4 — optional routing

- [ ] **T401 Evaluate accumulated routing regret.**
  - If not materially economic: mark M4 `rejected` and stop.
  - If material: write a new bounded routing spec starting with deterministic/simple baselines.

## Global completion rule

A checkbox may be marked complete only when its declared evidence exists. Architecture prose or chat confirmation is not evidence.
