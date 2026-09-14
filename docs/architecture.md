# Architecture Overview

Status: `specified`

This page is a compact human/agent map. Normative behavior lives in `docs/specs/` and execution order lives in root `TASKS.md`.

## System boundary

```mermaid
flowchart LR
    U[Human / task source]

    subgraph H[Hermes control plane]
      HP[Prompt / task orchestration]
      CE[LCM\ncurrent-session ContextEngine]
      MP[Mnemosyne\ncross-session MemoryProvider]
      LI[Local utility inference\nllama.cpp / Granite 4.2-8B]
    end

    subgraph SEC[Deterministic trust + egress boundary]
      PG[Local OpenAI-compatible\npolicy gateway]
      POL[Provenance / sensitivity /\nprovider policy]
    end

    subgraph EXT[External providers]
      ELLM[Approved external LLM]
    end

    subgraph W[Contained Pi coding worker]
      RPC[Pi RPC process]
      LSP[Allowlisted LSP / build tools]
      WS[Disposable workspace]
    end

    U --> HP
    HP <--> CE
    HP <--> MP
    HP <--> LI
    HP --> PG
    PG --> POL
    POL --> ELLM
    ELLM --> PG
    PG --> HP

    HP -->|typed task| RPC
    RPC <--> LSP
    RPC <--> WS
    RPC -->|model API only| PG
    RPC -->|typed result + diff + evidence| HP

    classDef control fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:2px;
    classDef memory fill:#ede9fe,stroke:#7c3aed,color:#0f172a,stroke-width:2px;
    classDef local fill:#dcfce7,stroke:#16a34a,color:#0f172a,stroke-width:2px;
    classDef security fill:#fee2e2,stroke:#dc2626,color:#0f172a,stroke-width:2px;
    classDef external fill:#fef3c7,stroke:#d97706,color:#0f172a,stroke-width:2px;
    classDef evidence fill:#f1f5f9,stroke:#64748b,color:#0f172a,stroke-width:2px;

    class HP control;
    class CE,MP memory;
    class LI,RPC,LSP,WS local;
    class PG,POL security;
    class ELLM external;
    class U evidence;
```

Color is redundant with text labels:

- **Blue — control:** Hermes orchestration.
- **Purple — context/memory:** LCM and Mnemosyne, with separate authority.
- **Green — contained/local execution:** local inference and Pi worker resources.
- **Red — enforcement boundary:** deterministic egress/provider policy.
- **Amber — external:** provider outside the local trust boundary.
- **Grey — human/evidence edge:** task/review source.

## Invariants

1. **One current-session context authority.** LCM may compact/select/recover current-session evidence; Mnemosyne does not create a competing transcript hierarchy.
2. **One durable-memory authority.** Mnemosyne holds curated cross-session memories; the same bank is not injected through multiple Hermes integration paths by default.
3. **Raw evidence remains recoverable.** Local compression/context packets carry provenance and retrieval pointers.
4. **Mandatory egress policy is fail closed.** Hermes fail-open hooks/middleware can contribute signals but cannot be the only deny boundary.
5. **External provider credentials do not belong in the contained Pi worker.** Worker model calls go through the policy gateway.
6. **Pi does not edit the canonical repository directly.** It operates on a disposable workspace and returns a diff/evidence package.
7. **Objective verification beats model judging where available.** Schema validation, compiler/tests and LSP diagnostics are preferred acceptance signals.
8. **Routing is optional.** The system works without a learned router; routing is built only if accumulated telemetry proves recoverable economic regret.

## Data-flow classification

| Flow | Default trust/sensitivity posture | Enforcement |
|---|---|---|
| Human → Hermes | trusted input but may contain sensitive data | provenance + egress classification |
| Repo/web/tool → Hermes | bounded/untrusted | never authorizes privileged action by itself |
| LCM/Mnemosyne → Hermes | persisted local evidence with provenance | budgeted injection; no automatic authority escalation |
| Hermes → local utility model | local/private | no external egress required |
| Hermes/Pi → policy gateway | policy-controlled | deterministic checks before provider connection |
| Gateway → external LLM | outside local trust boundary | minimized/approved payload only |
| Hermes → Pi | typed bounded task | sandbox, path/tool/network allowlist |
| Pi → Hermes | untrusted generated result until verified | diff/tests/LSP/schema evidence |

## Build sequence

```mermaid
flowchart LR
    M0[M0\nBaseline + token diet]
    M1[M1\nGranite + context packet]
    M2[M2\nMemory + fail-closed gateway]
    M3[M3\nPi RPC + OCI + LSP]
    M4{Routing regret\nmaterial?}
    R[Build simple router]
    S[Stop: no router needed]

    M0 --> M1 --> M2 --> M3 --> M4
    M4 -->|yes| R
    M4 -->|no| S

    classDef required fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:2px;
    classDef decision fill:#fef3c7,stroke:#d97706,color:#0f172a,stroke-width:2px;
    classDef stop fill:#dcfce7,stroke:#16a34a,color:#0f172a,stroke-width:2px;

    class M0,M1,M2,M3 required;
    class M4 decision;
    class R,S stop;
```

Each milestone can stop/reject a component without invalidating the entire architecture. `Routing not needed`, `Mnemosyne not paying for itself`, or `Q5 not needed` are valid outcomes rather than failures of the project.

## Normative references

- `docs/specs/local-model-admission.md`
- `docs/specs/m2-context-memory-security.md`
- `docs/specs/m3-pi-worker-rpc.md`
- `docs/build-readiness.md`
- root `TASKS.md`
