# Execution Tasks

Status: `specified`

This is the **single execution ledger**. Work top-to-bottom. Only one unchecked task may be treated as active unless a task explicitly says it can run in parallel.

Before changing an upstream-integrated component, compare the installed version/interface captured by T001–T004 with the compatibility target in the governing spec. If they materially differ, stop and update the spec/compatibility probe rather than guessing.

## M0 — baseline + deterministic token diet

- [ ] **T001 Capture host identity**
  - Record: Apple chip, 128 GB unified memory, macOS version, power mode.
  - Verify: `system_profiler SPHardwareDataType SPSoftwareDataType`
  - Evidence: `evidence/m0/host.txt`
  - Stop if: none.

- [ ] **T002 Pin llama.cpp**
  - Record exact binary version/commit, build options and Metal backend availability.
  - Verify: `llama-cli --version`, `llama-server --version` where available, and one no-model startup/help check.
  - Evidence: `evidence/m0/llama-version.txt`
  - Stop if: llama.cpp/Metal is not available; fix runtime before model work.

- [ ] **T003 Pin Hermes**
  - Record exact Hermes version/package source, active profile/config path, selected context engine, selected memory provider and relevant plugin paths with secrets redacted.
  - Verify: `hermes --version`; inspect/export config using only commands supported by the installed Hermes version.
  - Evidence: `evidence/m0/hermes-version.txt`, `evidence/m0/hermes-config.redacted.*`
  - Stop if: version, active config, context engine or memory provider cannot be identified unambiguously.

- [ ] **T004 Pin Pi, LCM and Mnemosyne**
  - Record exact Pi version/package source and verify documented RPC mode/flags exist.
  - Record the installed LCM plugin path/version/commit and database location without changing it.
  - Record Mnemosyne core version and Hermes wrapper version independently; use installed package metadata (`pip show`/equivalent) and, when useful, `pip index versions mnemosyne-hermes` rather than inferring publication state from git source alone.
  - Record whether Mnemosyne is integrated as Hermes memory provider, MCP, or both; record local/remote embedding backend.
  - Evidence: `evidence/m0/components.md`
  - Stop if: Pi RPC surface is absent on the installed version, LCM identity is ambiguous, or the same Mnemosyne bank is unintentionally injected through more than one Hermes path.

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
  - Inspect one trace from each baseline task for repeated static prompt text, duplicate tool schemas, oversized tool payloads, duplicate memory/context injection and unstable reusable prefixes.
  - Evidence: `evidence/m0/token-waste.md`
  - Stop if: none.

- [ ] **T008 Apply only obvious reversible token-diet changes**
  - Allowed: configuration or isolated adapter changes that remove duplication/cap oversized payloads while retaining raw evidence by path/hash.
  - Not allowed: local-model summarization, routing, Hermes/Pi core patches or security-boundary changes.
  - Evidence: exact diff/config change + rollback command in `evidence/m0/token-diet.md`.
  - Stop if: the change requires a core patch or loses raw evidence.

- [ ] **T009 Re-run baseline and decide M0**
  - Re-run T006 tasks and compare accepted-task quality, tokens/cost and latency.
  - Pass: no material quality regression and deterministic waste is reduced or proven negligible.
  - Evidence: `evidence/m0/decision.md`
  - Stop if: regression is material; roll back T008 before M1.

## M1 — one local utility model + recoverable context packets

Run only after T009 passes. Governing spec: `docs/specs/local-model-admission.md`.

- [ ] **T101 Pin Granite 4.2-8B Q6 artifact**
  - Candidate: `ibm-granite/granite-4.2-8b-GGUF` Q6_K.
  - Record model repo revision, exact GGUF filename, SHA256, license and llama.cpp command line.
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
  - Fields MUST include source identity/hash, compact content, exact excerpts where needed, uncertainty/omissions, transformation provenance and raw-evidence retrieval pointer.
  - Evidence: `schemas/context-packet.schema.json` plus a schema-validation test.
  - Stop if: provenance requires embedding raw secrets in the packet.

- [ ] **T108 Prove one token-saving artifact class**
  - Apply the promoted local model to exactly one high-volume artifact class first (for example compiler/test/log output).
  - Compare external tokens, task outcome, backtracking/retrieval and latency against M0.
  - Pass: material external-token reduction with no material accepted-task quality regression.
  - Evidence: `evidence/m1/context-packet-pilot.md`
  - Stop if: omissions cause retries/errors often enough to erase the gain.

## M2 — context/memory + trust/egress

Run only after M1 decision. Governing spec: `docs/specs/m2-context-memory-security.md`.

- [ ] **T201 Prove context/memory ownership uniqueness**
  - Verify exactly one selected Hermes context engine and exactly one selected external memory provider.
  - Record LCM and Mnemosyne versions, config keys, plugin/provider paths and active bank/database identity.
  - Verify Mnemosyne is not unintentionally injected through both provider + MCP.
  - Evidence: `evidence/m2/ownership.md`
  - Stop if: ownership is ambiguous or duplicate injection exists.

- [ ] **T202 Exercise LCM exact-detail recovery**
  - Back up current LCM database/config first.
  - Drive the long-context fixture through compaction and retrieve one exact buried detail through the documented LCM recovery/drill-down path.
  - Compare against the original raw source.
  - Evidence: `evidence/m2/lcm-recovery.md`
  - Stop if: raw evidence is missing, recovery lineage is ambiguous, or the installed LCM version materially differs from the spec contract.

- [ ] **T203 Exercise Mnemosyne memory precision**
  - Use a fixture containing one durable fact, one transient detail and one untrusted instruction.
  - Sync/end the session, inspect durable memory, then test next-session recall.
  - Record embedding backend and added prompt/context size.
  - Evidence: `evidence/m2/memory-precision.md`
  - Stop if: secrets/untrusted instructions become durable authority, or remote embeddings receive sensitive memory without explicit policy approval.

- [ ] **T204 Define and implement provenance + deterministic egress policy**
  - Use the minimal labels and fail-closed requirements from the M2 spec.
  - Choose one independently supervised enforcement point (for example a local provider/egress gateway) for mandatory deny decisions.
  - Model/hook/middleware risk signals may feed policy but may not override deterministic denial.
  - Evidence: `evidence/m2/egress-design.md` plus configuration/code diff and rollback procedure.
  - Stop if: the only available enforcement mechanism is a fail-open hook/middleware callback.

- [ ] **T205 Run M2 acceptance/red-team suite**
  - Run ownership uniqueness, exact-detail recovery, memory precision/injection-budget, indirect-injection, memory-poisoning and sensitive-egress tests from the M2 spec.
  - Deliberately crash/disable advisory hooks/middleware during the egress test and prove the independent boundary still blocks the sentinel secret.
  - Evidence: `evidence/m2/acceptance.json` and `evidence/m2/decision.md`
  - Stop if: any mandatory deny path fails open or baseline recall/economics regress materially.

- [ ] **T206 Exercise M2 rollback**
  - Restore pre-M2 config in a disposable profile; de-select new provider/context/egress routes without deleting databases or credentials.
  - Evidence: `evidence/m2/rollback.md`
  - Stop if: rollback requires destructive/manual recovery not already documented.

## M3 — contained Pi RPC worker + LSP

Run only after M2 passes. Governing spec: `docs/specs/m3-pi-worker-rpc.md`.

- [ ] **T301 Prove Pi RPC compatibility**
  - Pin the installed Pi version and verify `--mode rpc`, `--no-session`, `--no-approve`, resource-disable flags and tool-selection flags on that version.
  - Launch one read-only RPC worker and complete a trivial request/clean shutdown.
  - Evidence: `evidence/m3/pi-rpc-smoke.jsonl`
  - Stop if: the bridge would need Pi internal/in-progress `AgentHarness` APIs.

- [ ] **T302 Establish restrictive worker launch + disposable workspace**
  - Launch with project extensions/skills/templates/themes/context files disabled and a read-only tool profile first.
  - Create disposable git worktree/copy; ensure canonical repo is outside worker write authority.
  - Evidence: `evidence/m3/worker-launch.md`
  - Stop if: project-local resources execute implicitly or canonical writes remain possible.

- [ ] **T303 Establish real sandbox/network/credential boundary**
  - Select one OS/container/micro-VM containment path supported on the host.
  - Run sentinel credential/file and denied-network probes from a malicious fixture.
  - Evidence: `evidence/m3/sandbox.md`
  - Stop if: containment depends only on Pi prompts, trust prompts, `--offline`, or model compliance.

- [ ] **T304 Implement typed Hermes↔Pi bridge contract**
  - Implement the task/result fields from the M3 spec plus process supervision: startup timeout, task timeout, cancellation/kill, stderr capture, size limits and cleanup.
  - Evidence: bridge schema/tests + `evidence/m3/bridge-contract.md`
  - Stop if: a worker crash/malformed RPC result can be interpreted as success.

- [ ] **T305 Add read-only LSP adapter**
  - No third-party Pi LSP extension is required for the trusted path.
  - Start with diagnostics, definition, references and symbol lookup only, using allowlisted language servers inside the worker containment boundary or an equivalent constrained service.
  - Evidence: `evidence/m3/lsp-readonly.md`
  - Stop if: LSP operation mutates files or can execute unapproved host commands outside policy.

- [ ] **T306 Run one bounded coding task**
  - Enable only the minimum edit/write/bash capabilities inside the disposable workspace.
  - Return changed paths, diff, compiler/tests/static checks and post-edit diagnostics to Hermes.
  - Evidence: `evidence/m3/coding-task.md`
  - Stop if: changes escape allowed paths or objective verification is missing.

- [ ] **T307 Run replay/rollback/malicious-repo suite**
  - Execute P2–P8 from the M3 spec, including project-resource isolation, canonical protection, timeout/crash, network/credential containment, read-only LSP, bounded edit and clean replay/disposal.
  - Evidence: `evidence/m3/acceptance.json`, `evidence/m3/rollback.md`
  - Stop if: any containment invariant fails.

## M4 — optional routing

- [ ] **T401 Evaluate accumulated routing regret**
  - Use telemetry already accumulated during M0–M3; do not create a new routing dataset merely to justify routing.
  - If recoverable economic regret is not material: mark M4 `rejected` and stop.
  - If material: write one bounded routing spec starting with deterministic/simple baselines; ModernBERT is considered only after those baselines.
  - Evidence: `evidence/m4/routing-regret.md`

## Global completion rule

A checkbox may be marked complete only when its declared evidence exists. Architecture prose or chat confirmation is not evidence.

A task that reaches a `Stop if` condition remains unchecked until the governing spec is revised or the condition is resolved. Agents MUST NOT silently choose a new architecture to bypass a stop condition.
