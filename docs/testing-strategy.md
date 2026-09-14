# Fast-Feedback Testing Strategy

Status: `specified`

## Purpose

Foundry tests are designed to answer one question as early and cheaply as possible:

> **What is the cheapest experiment that can prove this task or design is wrong before we invest further?**

This is not a large benchmark programme. It is a falsification ladder for a self-hosted agentic harness.

## Core rules

1. **Cheapest falsifier first.** Never start with a soak test, cloud benchmark, full red-team suite or end-to-end coding run when a smaller deterministic probe can invalidate the hypothesis.
2. **One unknown at a time.** A test should change one material variable. If model, quant, prompt, runtime flags and context size all change together, the result is not useful evidence.
3. **Deterministic before probabilistic.** Prefer schema validation, hashes, exact excerpts, compiler/tests, LSP diagnostics, network denial and filesystem permissions over an LLM judge.
4. **Negative tests are first-class.** A component is not proven merely because the happy path works. Test the failure mode that would make the architecture unsafe or uneconomic.
5. **Promote only after the lower tier passes.** A failure at a cheap tier blocks the more expensive tier until the failure is explained or the spec changes.
6. **Keep controls.** Before/after comparisons reuse the same fixture, provider/model and environment wherever possible.
7. **Raw evidence stays recoverable and private.** Follow `docs/evidence-policy.md`.
8. **A failed test is useful output.** Do not tune indefinitely to force a preferred design to pass.

## Test ladder

The budgets below are defaults, not performance promises. A governing spec may override them explicitly.

| Tier | Goal | Default budget | Cloud/model use | Typical examples |
|---|---|---:|---|---|
| **F0 — static/preflight** | catch impossible/stale assumptions | seconds | none | version/flag presence, config shape, schema parse, file/path checks, dependency availability |
| **F1 — micro smoke** | prove the smallest callable seam works | ~1 minute | local only where possible; at most one tiny paid call when unavoidable | load model + one response, Pi RPC handshake, gateway allow/deny with fake upstream, one LSP diagnostic |
| **F2 — contract fixture** | prove semantics on a small deterministic fixture | a few minutes | bounded; no broad benchmark | 3–5 compression cases, one LCM buried fact, one Mnemosyne durable/transient/untrusted fixture, one malicious repo fixture |
| **F3 — milestone acceptance** | prove the selected implementation under representative conditions | only after F0–F2 pass | bounded by the milestone spec | three M0 baseline tasks, 10–20 utility examples, M2 security suite, Pi P1–P9 |
| **F4 — soak / sustained** | expose thermal, memory, leak and long-session defects | only when the component already passes quality/correctness | no exploration during soak | 20-minute llama.cpp Hermes-shaped replay; repeated worker/replay check |

### Cost rule

For any test that invokes a paid provider, use the smallest synthetic fixture that exercises the contract. A task MUST NOT add repeated paid calls merely to increase confidence when the acceptance signal is unchanged. If more than a handful of paid calls appear necessary, first write down what new uncertainty each additional call resolves.

## The three-question preflight

Before executing any non-trivial task, answer in one or two lines in the local evidence record:

1. **Hypothesis:** what exact behavior do we expect?
2. **Cheapest falsifier:** what is the smallest test that would prove the hypothesis wrong?
3. **Promotion signal:** what observable result allows the next tier?

Example:

```text
Hypothesis: Granite Q6 can produce schema-valid context packets without omitting sentinel evidence.
Cheapest falsifier: 3 fixed artifacts with required sentinel facts + JSON schema validation.
Promotion signal: 3/3 schema-valid; 0 required facts omitted -> run the larger utility smoke, then sustained soak.
```

## Rabbit-hole circuit breaker

For the same failed hypothesis:

- **Attempt 1:** reproduce and classify the failure: environment, compatibility, implementation, data/fixture, or design.
- **Attempt 2:** change exactly one variable justified by the classification and re-run the cheapest failing test.
- **If it still fails:** stop. Record the failure and either revise/reject the spec or request an explicit operator decision.

Do not keep prompt-tuning, flag-tuning, model-shopping or dependency-swapping until something passes. A third materially different experiment requires a written reason tied to new evidence.

## Self-hosting rule: Hermes building Hermes

Changes to the harness that is currently executing the build are higher risk than ordinary application changes.

- Prefer a **disposable profile/config/worktree/process** for experiments.
- Capture rollback before applying a live configuration change.
- Never delete/overwrite the only known-good config/database as part of a test.
- A task that requires restarting/replacing the active controlling Hermes process MUST first leave a deterministic recovery command/path outside that process.
- Do not let a partially modified live harness become the only mechanism capable of finishing its own repair.
- For gateway/security changes, prove the local fake-upstream path before any real provider traffic.
- For Pi, prove RPC/resource isolation before allowing edits; prove read-only LSP before refactoring.

## Milestone-specific cheapest feedback

### M0 — baseline + deterministic token diet

Run in this order:

1. version/config inspection;
2. one trace per representative task;
3. static identification of duplicate prompt/tool/memory material;
4. one reversible change at a time;
5. replay the same fixture immediately.

Do **not** batch several token optimizations before measuring them. We want attribution.

### M1 — local utility model

Run in this order:

1. model provenance + llama.cpp support check;
2. load/memory + one structured response;
3. **3–5 example micro-quality smoke** with sentinel evidence and schema validation;
4. 10–20 example utility smoke only if needed to resolve uncertainty;
5. 20-minute sustained replay only after quality/correctness passes;
6. one real artifact-class token-saving pilot.

A model that fails evidence preservation is rejected before thermal/throughput soak.

### M2 — context, memory and egress

Run in this order:

1. ownership/config uniqueness check;
2. one LCM exact-detail fixture;
3. one Mnemosyne durable/transient/untrusted fixture;
4. gateway unit tests against a **fake local upstream**: allow, redact/transform where applicable, deny, timeout, malformed policy;
5. gateway-bypass/network-negative test;
6. only then one minimal real-provider path if required;
7. full C1–C4/S1–S4 acceptance suite.

Security tests use sentinel secrets, never real credentials.

### M3 — Pi RPC + containment + LSP

Run in this order:

1. RPC process starts and protocol responds;
2. project resources remain disabled;
3. disposable workspace/canonical-repo write denial;
4. network/credential denial with a malicious fixture;
5. gateway-only model path;
6. one read-only LSP diagnostic/definition/reference fixture;
7. one bounded edit with compiler/test/LSP verification;
8. replay/rollback/malicious-repo suite.

Never start with an autonomous coding mission.

## Default acceptance signals

Prefer these signals in descending order:

1. exact byte/value/hash comparison;
2. JSON/schema validation;
3. filesystem/network/process policy result;
4. compiler/test/static-analysis result;
5. LSP diagnostics/reference result;
6. exact evidence/provenance recall;
7. task-level before/after outcome;
8. human review;
9. LLM-as-judge only when no stronger signal exists.

## Regression rule

Every promoted optimization keeps a small regression fixture that covers the failure it could introduce. The fixture should run at F1/F2 cost where practical.

Examples:

- tool-output compression: sentinel fact survives;
- memory admission: untrusted instruction does not become durable authority;
- gateway: sentinel secret is denied even when advisory middleware fails;
- Pi worker: canonical repo remains unwritable;
- LSP mutation: changed paths remain allowlisted and diagnostics do not worsen silently.

## Reporting format

For each task, keep the result compact:

```text
Task: Txxx
Hypothesis: ...
Tier reached: F0/F1/F2/F3/F4
Result: PASS / FAIL / STOP
Key measurement: ...
Evidence: local/path
Next: next task | retry one changed variable | revise/reject
```

Do not write a long retrospective for a passing micro-test.

## Definition of enough testing

Testing is sufficient to move forward when:

- the cheapest relevant failure modes have been exercised;
- the declared promotion signal is met;
- the task's specific acceptance criteria pass;
- rollback/disable behavior exists where the task changes state;
- no lower-cost unresolved test could still falsify the design.

More testing is not automatically more confidence. **Targeted evidence that resolves a material uncertainty is the goal.**
