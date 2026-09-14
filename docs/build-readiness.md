# Build Readiness

Status: `specified`

This document answers one question: **is the repository ready to move from research/specification into implementation?**

It separates **specification confidence** from **operational confidence**. A design can be well specified before it has been proven on the target Mac; those are different claims.

## Current upstream reference points

These are research anchors, not substitutes for T001–T004 local version capture.

| Component | Current upstream reference | Build posture |
|---|---|---|
| Hermes | stable `v0.21.2` / `v2026.9.11` | supported reference; local install MUST be pinned before implementation |
| Pi | stable `v0.85.1` | use documented RPC/CLI/custom-provider surface, not internal `AgentHarness` migration APIs |
| hermes-lcm | latest published GitHub stable release `v0.20.0`; current source tree also documents a `v1.0.0-rc.1` line | do not infer the installed line from GitHub `latest`; pin exact installed version/commit and back up `lcm.db` before any change |
| Mnemosyne | latest GitHub Hermes-integration release observed as `v0.7.0`; core package and Hermes wrapper versioning are separate | T004 MUST record installed `mnemosyne-memory` and `mnemosyne-hermes` metadata independently; do not use the repo tag as a core-version proxy |
| Granite 4.2-8B GGUF | official IBM GGUF | Q6_K is ~7.22 GB; first local qualification candidate |

Freshness check performed 2026-09-14 before build handoff: Hermes and Pi stable release references above remain current. Upstream references may move after handoff; installed local versions remain the implementation authority for this build.

## Stable seams selected now

The project MUST prefer these integration surfaces unless a compatibility probe proves they are unavailable:

1. **Hermes context:** one selected `ContextEngine` via `context.engine`; LCM owns current-session compaction/recovery.
2. **Hermes durable memory:** one selected external `MemoryProvider`; Mnemosyne provider plugin is preferred over exposing the same bank through MCP.
3. **Hermes telemetry:** observer hooks may collect data; exceptions are fail-open, so they are not security boundaries.
4. **Hermes mutation/routing:** middleware may shape requests, but middleware failures are fail-open and MUST NOT be the only enforcement point for mandatory security policy.
5. **Mandatory external egress:** Hermes uses its documented custom OpenAI-compatible provider seam to target a localhost policy gateway. External provider credentials required by that route are held outside the policy-controlled Hermes process/profile wherever practical. Gateway/policy failure is a deny, never direct-provider fall-through.
6. **Pi integration:** `pi --mode rpc` JSON protocol over stdin/stdout is the default Hermes→Pi boundary. Do not bind to Pi's internal/in-progress `AgentHarness` APIs.
7. **Pi containment:** unattended baseline is whole-process OCI-container containment with disposable workspace, no canonical-repo write authority, no external-provider credentials and no unrestricted internet. If no suitable OCI runtime exists, execution stops for an operator decision rather than silently changing sandbox architecture.
8. **Pi provider path:** custom OpenAI-compatible provider configuration points the worker at the policy gateway; direct external-provider fallback is prohibited for the contained profile.
9. **Pi project resources:** worker launch defaults to `--no-approve --no-extensions --no-skills --no-prompt-templates --no-themes --no-context-files`; resources are added back explicitly only when required.
10. **LSP:** no third-party Pi LSP extension is part of the trusted base. Start with an in-repo minimal adapter/read-only LSP surface and add rename/refactor only after diagnostics/references are proven.

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
| M2 context/memory/security | **98** | **79** | installed LCM/Mnemosyne behavior and localhost gateway negative tests |
| M3 Pi RPC + OCI + LSP | **98** | **79** | available OCI runtime/toolchain image, gateway-only network proof and end-to-end replay |
| M4 optional routing | **85** | **45** | whether an economic routing problem exists at all |

**Required-stack specification readiness (M0–M3): 97/100** (rounded; raw mean 97.25).

**Required-stack operational confidence before execution: 79/100.** This is deliberately constrained by the absence of measurements from the actual Mac and installed stack.

M4 is optional and is not included in required-stack readiness. A low M4 operational score is acceptable because `routing not worth building` is a valid successful outcome.

## Why the scores are not higher before execution

The remaining uncertainty is operational, not architectural:

- installed Hermes/LCM/Mnemosyne/Pi versions may differ from current research anchors;
- Granite's sustained Metal behavior must be measured on the target Mac;
- LCM/Mnemosyne ownership and recall behavior must be proven in the installed configuration;
- the gateway must survive negative/bypass tests;
- OCI containment, Pi RPC, LSP and replay must work end-to-end on the host.

More broad research does not resolve those uncertainties as efficiently as the existing local evidence gates.

## Hardening added before build handoff

- M2 has a single context-engine/single memory-provider contract, explicit memory-admission rules, deterministic red-team cases and a concrete fail-closed egress seam using Hermes' supported custom-provider capability.
- M3 uses Pi's documented RPC/custom-provider surfaces rather than evolving internal harness APIs, disables project-local resources by default, specifies whole-process OCI containment and gateway-only model access, requires process supervision, and stages LSP read-only before mutation.
- `TASKS.md` maps M0–M3 work to exact evidence paths and `Stop if` conditions, so an execution agent should not need to invent architecture while working.
- `docs/testing-strategy.md` enforces cheapest-falsifier-first testing and a bounded retry/circuit-breaker rule.
- `scripts/check_repo.py` statically checks required source-of-truth files, local Markdown links, task-ID uniqueness and accidental tracking of evidence/model/credential artifacts.
- `AGENTS.md` and `prompts/hermes-bootstrap.md` require a recorded baseline commit plus a dedicated build branch/worktree; self-build work does not go directly to `main`.
- `docs/evidence-policy.md` keeps raw runtime evidence local/untracked in this public repository.

## What raises operational confidence fastest

Do **not** add more broad research. Execute these evidence gates:

1. **Build-start gate:** `python3 scripts/check_repo.py`, read-only preflight, clean checkout, recorded baseline commit, dedicated build branch/worktree.
2. **T001–T004:** pin the real host and installed component versions. This removes version/interface uncertainty from every milestone.
3. **T005–T009:** establish three replayable tasks and before/after economics. This turns token-optimization hypotheses into local evidence.
4. **T102–T104:** Granite runtime preflight, four-case quality falsifier, then the sustained replay. This resolves most M1 uncertainty with the cheap tests first.
5. **T201–T203:** prove exactly one context engine/provider path plus LCM recovery and Mnemosyne precision on fixtures.
6. **T204–T205:** stand up the localhost gateway and run fail-closed negative/bypass tests, including deliberate advisory-hook failure.
7. **T301–T303:** Pi RPC/custom-provider smoke plus OCI network/credential/canonical-workspace containment.
8. **T305–T307:** read-only LSP, one bounded edit, replay/rollback/malicious-repo suite.

After T001–T009 pass, M0 operational confidence can exceed the pre-execution cap. After the relevant acceptance suites pass, M1–M3 can move into the 90s independently.

## Definition of `ready-to-build`

The repository is **ready to begin M0 implementation now** because:

- a static repository consistency gate exists before T001;
- M0 task definitions are executable with no unanswered design choice;
- later component-changing tasks point to normative specs and rollback/stop conditions;
- mandatory security denies have a selected enforcement architecture independent of fail-open callbacks;
- the Pi integration uses documented RPC/custom-provider behavior and a selected real containment topology;
- model selection is a one-path admission decision, not an open-ended benchmark programme;
- source-control isolation prevents the self-build experiment from treating `main` as its scratch surface;
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
- hermes-lcm releases/source: https://github.com/stephenschoettler/hermes-lcm
- Mnemosyne releases/integration: https://github.com/mnemosyne-oss/mnemosyne/releases and https://github.com/mnemosyne-oss/mnemosyne/blob/main/docs/hermes-integration.md
- Pi releases: https://github.com/earendil-works/pi/releases
- Pi RPC: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md
- Pi custom providers/models: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md
- Pi security/containerization: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/security.md
- Granite 4.2-8B GGUF: https://huggingface.co/ibm-granite/granite-4.2-8b-GGUF
