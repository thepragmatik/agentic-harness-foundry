# Build Readiness

Status: `specified`

This document answers one question: **is the repository ready to move from research/specification into implementation?**

It deliberately separates **specification confidence** from **operational confidence**. A design can be well specified before it has been proven on the target Mac; those are different claims.

## Current upstream reference points

These are research anchors, not substitutes for T001–T004 local version capture.

| Component | Current upstream reference | Build posture |
|---|---|---|
| Hermes | stable `v0.21.2` / `v2026.9.11` | supported reference; local install MUST be pinned before implementation |
| Pi | stable `v0.85.1` | use documented RPC/CLI surface, not internal `AgentHarness` migration APIs |
| hermes-lcm | `v1.0.0-rc.1` line documented upstream | pre-release: pin exact commit + back up `lcm.db` before any change |
| Mnemosyne core | latest published core line observed as `3.15.1` | pin installed core and wrapper independently |
| Mnemosyne Hermes wrapper | source manifest currently reports `0.6.0` | publication/version MUST be verified locally; do not infer from git alone |
| Granite 4.2-8B GGUF | official IBM GGUF | Q6_K is ~7.22 GB; first local qualification candidate |

## Stable seams selected now

The project MUST prefer these integration surfaces unless a compatibility probe proves they are unavailable:

1. **Hermes context:** one selected `ContextEngine` via `context.engine`; LCM owns current-session compaction/recovery.
2. **Hermes durable memory:** one selected external `MemoryProvider`; Mnemosyne provider plugin is preferred over exposing the same bank to Hermes through MCP.
3. **Hermes telemetry:** observer hooks may collect data; exceptions are fail-open, so they are not security boundaries.
4. **Hermes mutation/routing:** middleware may shape requests, but middleware failures are fail-open and MUST NOT be the only enforcement point for mandatory security policy.
5. **Pi integration:** `pi --mode rpc` JSON protocol over stdin/stdout is the default Hermes→Pi boundary. Do not bind to Pi's internal/in-progress `AgentHarness` APIs.
6. **Pi isolation:** the Pi process or all of its execution tools MUST run inside a real OS/container/micro-VM boundary for unattended work. Pi project trust is not a sandbox.
7. **Pi project resources:** worker launch defaults to `--no-approve --no-extensions --no-skills --no-prompt-templates --no-themes --no-context-files`; resources are added back explicitly only when the worker contract requires them.
8. **LSP:** no third-party Pi LSP extension is part of the trusted base. Start with an in-repo minimal adapter/read-only LSP surface and add rename/refactor only after diagnostics/references are proven.

## Evidence-weighted confidence method

Each milestone has two scores.

### Specification confidence (0–100)

Weighted by:

- 25% primary upstream contract/source evidence;
- 20% integration boundary is explicit;
- 20% acceptance tests are deterministic/measurable;
- 15% rollback/disable path is explicit;
- 20% implementation ambiguity has been removed.

### Operational confidence (0–100)

Weighted by:

- 25% upstream maturity and stable public surface;
- 25% target-machine/environment evidence;
- 20% end-to-end testability;
- 15% failure containment/rollback;
- 15% known-issue exposure.

**Until target-machine evidence exists, operational confidence is capped at 80.** This prevents research quality from being mistaken for execution proof.

## Current scores before local execution

| Milestone | Spec confidence | Operational confidence | Main residual uncertainty |
|---|---:|---:|---|
| M0 baseline/token diet | **96** | **80 (cap)** | actual installed versions/config and provider telemetry |
| M1 Granite/local context packets | **93** | **78** | target-Mac sustained llama.cpp throughput and utility retention |
| M2 context/memory/security | **91** | **76** | exact installed LCM/Mnemosyne versions and fail-closed egress implementation path |
| M3 Pi RPC + containment + LSP | **92** | **77** | target sandbox choice, language-server set, end-to-end worker replay |
| M4 optional routing | **84** | **45** | whether an economic routing problem exists at all |

Overall **repository build-readiness: 91/100 specification readiness**. Overall **full-stack operational confidence: 77/100**, deliberately capped by missing target-machine evidence.

## What raises the operational scores fastest

Do not add more broad research. Execute these evidence gates:

1. **T001–T004:** pin the real host and installed component versions. This removes version ambiguity across every later milestone.
2. **T005–T009:** establish three replayable tasks and before/after economics. This converts token-optimization claims into local measurements.
3. **T102–T104:** one Granite Q6 admission run. This is the highest-value uncertainty reduction for M1.
4. **M2 compatibility probes:** prove exactly one context engine and one external memory provider are active; prove Mnemosyne provider mode rather than duplicate MCP injection; run LCM/Mnemosyne doctor/status checks.
5. **Fail-closed negative test:** deliberately crash/disable any advisory hook/middleware and prove sensitive egress remains denied by the independent enforcement point.
6. **Pi RPC smoke:** launch an ephemeral worker with project resources disabled, send one RPC prompt, enforce timeout/kill, and prove only the disposable workspace can change.
7. **Read-only LSP smoke:** diagnostics + definition/references only. Refactoring remains out until read-only behavior is stable.

## Definition of `ready-to-build`

The repository is ready for implementation work when all are true:

- M0 task definitions are executable with no unanswered design choice;
- current component versions are captured in `evidence/m0/`;
- every component-changing task points to one normative spec and one rollback path;
- security-critical deny behavior has an enforcement point that does not depend on fail-open Hermes plugin callbacks;
- the Pi integration uses documented RPC/CLI behavior and a real sandbox boundary;
- model selection is a one-path admission decision, not an open-ended benchmark programme;
- no task requires an agent to invent an architecture choice while executing it.

The repository does **not** require every future milestone to be locally validated before M0 implementation begins. It requires the next active milestone to be fully specified, and later milestones to have stable integration boundaries plus explicit gates.

## Primary references

- Hermes releases: https://github.com/NousResearch/hermes-agent/releases
- Hermes context engine contract: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/context-engine-plugin.md
- Hermes memory provider contract: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/memory-provider-plugin.md
- Hermes middleware contract: https://github.com/NousResearch/hermes-agent/blob/main/docs/middleware/README.md
- Hermes hook semantics: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/hooks.md
- hermes-lcm: https://github.com/stephenschoettler/hermes-lcm
- Mnemosyne Hermes integration: https://github.com/mnemosyne-oss/mnemosyne/blob/main/docs/hermes-integration.md
- Pi releases: https://github.com/earendil-works/pi/releases
- Pi RPC: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md
- Pi security/containerization: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/security.md
- Granite 4.2-8B GGUF: https://huggingface.co/ibm-granite/granite-4.2-8b-GGUF
