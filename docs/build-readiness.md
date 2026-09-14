# Build Readiness

Status: `specified`

This document answers one question: **is the repository ready to move from research/specification into implementation?**

It separates **specification confidence** from **operational confidence**. A design can be well specified before it has been proven on the target Mac; those are different claims.

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
2. **Hermes durable memory:** one selected external `MemoryProvider`; Mnemosyne provider plugin is preferred over exposing the same bank through MCP.
3. **Hermes telemetry:** observer hooks may collect data; exceptions are fail-open, so they are not security boundaries.
4. **Hermes mutation/routing:** middleware may shape requests, but middleware failures are fail-open and MUST NOT be the only enforcement point for mandatory security policy.
5. **Mandatory external egress:** Hermes uses its documented custom OpenAI-compatible provider seam to target a localhost policy gateway. External provider credentials required by that route are held outside the policy-controlled Hermes process/profile wherever practical. Gateway/policy failure is a deny, never direct-provider fall-through.
6. **Pi integration:** `pi --mode rpc` JSON protocol over stdin/stdout is the default Hermes→Pi boundary. Do not bind to Pi's internal/in-progress `AgentHarness` APIs.
7. **Pi isolation:** the Pi process or all execution tools MUST run inside a real OS/container/micro-VM boundary for unattended work. Pi project trust is not a sandbox.
8. **Pi project resources:** worker launch defaults to `--no-approve --no-extensions --no-skills --no-prompt-templates --no-themes --no-context-files`; resources are added back explicitly only when required.
9. **LSP:** no third-party Pi LSP extension is part of the trusted base. Start with an in-repo minimal adapter/read-only LSP surface and add rename/refactor only after diagnostics/references are proven.

Normative details live in:

- `docs/specs/local-model-admission.md`
- `docs/specs/m2-context-memory-security.md`
- `docs/specs/m3-pi-worker-rpc.md`
- root `TASKS.md`

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

## Current scores after specification hardening

| Milestone | Spec confidence | Operational confidence | Main residual uncertainty |
|---|---:|---:|---|
| M0 baseline/token diet | **98** | **80 (cap)** | actual installed versions/config and provider telemetry |
| M1 Granite/local context packets | **95** | **78** | target-Mac sustained llama.cpp throughput and utility retention |
| M2 context/memory/security | **97** | **79** | exact installed LCM/Mnemosyne versions and localhost gateway implementation/negative test |
| M3 Pi RPC + containment + LSP | **97** | **79** | target sandbox choice, language-server set and end-to-end worker replay |
| M4 optional routing | **85** | **45** | whether an economic routing problem exists at all |

**Required-stack specification readiness (M0–M3): 97/100.**

**Required-stack operational confidence before execution: 79/100.** This is deliberately constrained by the absence of measurements from the actual Mac and installed stack.

M4 is optional and is not included in required-stack readiness. A low M4 operational score is acceptable because `routing not worth building` is a valid successful outcome.

## Why the scores increased

The previous largest ambiguities have been removed:

- M2 now has a single context engine/single memory-provider contract, explicit memory-admission rules, deterministic red-team cases and a concrete fail-closed egress seam using Hermes' supported custom-provider capability.
- M3 now uses Pi's documented RPC protocol rather than evolving internal harness APIs, disables project-local resources by default, specifies process supervision, requires a real containment boundary, and stages LSP read-only before mutation.
- `TASKS.md` now maps M0–M3 work to exact evidence paths and `Stop if` conditions, so an execution agent should not need to invent architecture while working.
- `AGENTS.md` now makes stable-public-surface and stop-condition behavior normative for agents.

## What raises operational confidence fastest

Do **not** add more broad research. Execute these evidence gates:

1. **T001–T004:** pin the real host and installed component versions. Expected effect: removes version/interface uncertainty from every milestone.
2. **T005–T009:** establish three replayable tasks and before/after economics. Expected effect: turns token-optimization hypotheses into local evidence.
3. **T102–T104:** one Granite Q6 admission run. Expected effect: resolves most M1 operational uncertainty in a single experiment.
4. **T201–T203:** prove exactly one context engine/provider path plus LCM recovery and Mnemosyne precision on fixtures.
5. **T204–T205:** stand up the localhost gateway and run fail-closed negative/bypass tests, including deliberate advisory-hook failure.
6. **T301–T303:** Pi RPC smoke plus real sandbox/network/credential containment.
7. **T305–T307:** read-only LSP, one bounded edit, replay/rollback/malicious-repo suite.

After T001–T009 pass, M0 operational confidence can exceed the pre-execution cap. After the relevant acceptance suites pass, M1–M3 can move into the 90s independently.

## Definition of `ready-to-build`

The repository is **ready to begin M0 implementation now** because:

- M0 task definitions are executable with no unanswered design choice;
- later component-changing tasks point to normative specs and rollback/stop conditions;
- mandatory security denies have a selected enforcement architecture independent of fail-open callbacks;
- the Pi integration uses documented RPC/CLI behavior and requires a real sandbox boundary;
- model selection is a one-path admission decision, not an open-ended benchmark programme;
- no current task requires an agent to invent an architecture choice while executing it.

It is **not yet validated for production uplift**. T001 onward must produce the declared evidence before `validated` may be used.

## Primary references

- Hermes releases: https://github.com/NousResearch/hermes-agent/releases
- Hermes context engine contract: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/context-engine-plugin.md
- Hermes memory provider contract: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/memory-provider-plugin.md
- Hermes middleware contract: https://github.com/NousResearch/hermes-agent/blob/main/docs/middleware/README.md
- Hermes hook semantics: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/hooks.md
- Hermes providers/custom endpoints: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/integrations/providers.md
- Hermes provider runtime: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/provider-runtime.md
- hermes-lcm: https://github.com/stephenschoettler/hermes-lcm
- Mnemosyne Hermes integration: https://github.com/mnemosyne-oss/mnemosyne/blob/main/docs/hermes-integration.md
- Pi releases: https://github.com/earendil-works/pi/releases
- Pi RPC: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md
- Pi security/containerization: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/security.md
- Granite 4.2-8B GGUF: https://huggingface.co/ibm-granite/granite-4.2-8b-GGUF
