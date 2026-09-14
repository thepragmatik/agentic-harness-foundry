# M3 Pi Worker RPC, Containment and LSP Specification

Status: `specified`

## Desired outcome

Hermes can delegate a bounded coding task to Pi as a separate worker process, with explicit task/result contracts, disposable workspace isolation, least privilege, objective verification, and no dependency on Pi's internal/in-progress harness APIs.

## Compatibility target

Research reference: Pi stable `v0.85.1`. The implementation MUST pin the actually installed Pi version in T004/T301 and stop if documented RPC/CLI flags materially differ.

The default integration surface is Pi's documented RPC mode:

```text
pi --mode rpc --no-session
```

RPC is newline-delimited JSON over stdin/stdout. Hermes MUST interact through a bridge/process supervisor rather than importing Pi's internal `AgentHarness` implementation.

## Why RPC is the selected seam

- documented public surface;
- process isolation from Hermes runtime;
- language-neutral bridge;
- explicit lifecycle/timeout/kill boundary;
- lower coupling to Pi refactors than internal TypeScript harness APIs;
- easy to place the whole worker inside a sandbox/container/micro-VM.

Do not adopt Pi's in-progress internal AgentHarness migration APIs unless a later ADR proves RPC insufficient.

## Worker launch profile

The first unattended worker profile SHOULD start from the restrictive baseline:

```text
pi --mode rpc --no-session \
  --no-approve \
  --no-extensions \
  --no-skills \
  --no-prompt-templates \
  --no-themes \
  --no-context-files
```

Then add only explicitly required capabilities.

`--offline` MAY be used to suppress Pi startup/network behavior where supported, but it is **not a sandbox** and MUST NOT be relied on as the network-denial boundary.

## Tool policy

### Read-only qualification profile

Prefer only:

- `read`
- `grep`
- `find`
- `ls`

No write/edit/bash capability is needed for the first RPC/LSP compatibility smoke.

### Coding profile

Only after the read-only qualification passes, permit the minimum tool set required for implementation inside the disposable workspace. Candidate set:

- `read`
- `grep`
- `find`
- `ls`
- `edit`
- `write`
- `bash`

The bridge/sandbox, not model compliance, MUST enforce filesystem/network/process restrictions.

## Workspace boundary

Unattended coding MUST NOT run against the canonical working tree.

Preferred flow:

```text
canonical repo (read-only source)
        |
        v
 disposable git worktree / copy
        |
        v
 OS/container/micro-VM policy boundary
        |
        v
 Pi RPC worker
        |
        v
 diff + diagnostics + tests + evidence
        |
        v
 explicit review/apply step outside worker
```

The worker MUST receive only credentials and network access explicitly required for the task. Default is no unrelated host credentials and no unrestricted outbound network.

## Hermes -> Pi task contract

The bridge MUST produce a typed task object with at least:

- `schema_version`;
- `task_id`;
- `repo_identity` / canonical repo reference;
- disposable `workspace_path` or worker-visible workspace ID;
- requested outcome / acceptance criteria;
- allowed paths;
- allowed tools/capabilities;
- network policy;
- maximum wall-clock timeout;
- required verification commands;
- source/provenance references for supplied context;
- model/provider selection only when explicitly controlled by the caller.

The task contract MUST NOT contain reusable host secrets.

## Pi -> Hermes result contract

The bridge result MUST include:

- `task_id`;
- terminal status: `completed | failed | timed_out | cancelled | rejected`;
- changed file list;
- patch/diff reference;
- commands executed or compact command evidence;
- compiler/test/static-analysis outcome;
- LSP diagnostics before/after where applicable;
- unresolved warnings/uncertainties;
- worker exit reason;
- artifact/evidence paths and hashes.

A conversational statement such as "done" is not sufficient completion evidence.

## LSP strategy

Do not make a third-party Pi LSP extension part of the trusted base. Pi extensions execute with local privileges and third-party LSP extensions have shown version-compatibility breakage across Pi releases.

### Stage 1 — read-only LSP

Implement the smallest in-repo bridge needed for:

- diagnostics;
- go-to-definition;
- references;
- workspace/document symbol lookup where supported.

Language servers are allowlisted per repo/language and run in the same containment boundary as the worker or behind an equivalently constrained service.

### Stage 2 — edit assistance

Only after Stage 1 is stable, add controlled rename/refactor/code-action support. Any workspace edit MUST be previewed/validated against allowed paths before application and followed by diagnostics/tests.

Do not permit arbitrary LSP server commands to escape the sandbox policy.

## Process supervision

The Hermes-side bridge MUST own:

- process creation;
- stdin/stdout framing;
- stderr capture;
- startup timeout;
- per-task wall-clock timeout;
- cancellation/kill;
- maximum output/log size;
- worker exit-code handling;
- cleanup/disposal of the workspace.

An RPC protocol error, worker crash, timeout or malformed result MUST fail the task closed; Hermes may escalate/retry, but MUST NOT interpret missing evidence as success.

## Acceptance tests

### P1 — RPC compatibility

Start Pi in RPC mode using the pinned version and issue one read-only prompt/request. Verify valid RPC responses and clean shutdown.

**Fail if:** implementation requires an internal Pi API or unsupported extension to communicate.

### P2 — resource isolation

Place malicious/incompatible project-local extension, skill, prompt template and context files in a fixture repo.

Launch with the restrictive flags above.

**Pass:** project resources are not loaded/executed and cannot affect the worker unless explicitly enabled by a later task contract.

### P3 — canonical repo protection

Mount/expose the canonical repo read-only or otherwise deny worker writes. Give the worker a disposable writable worktree/copy.

**Pass:** worker changes appear only in the disposable workspace; attempted canonical writes fail.

### P4 — network/credential containment

Use a sentinel environment variable/file plus a network probe in the malicious fixture.

**Pass:** unrelated credential material is unavailable and denied network destinations cannot be reached by the worker, independent of model instructions.

### P5 — timeout/crash behavior

Trigger a long-running task and a malformed/crashing path.

**Pass:** supervisor kills/cleans up at the declared timeout, result is non-success, and partial workspace remains inspectable or is disposed according to policy.

### P6 — read-only LSP

On one small fixture repo, request diagnostics + definition/references.

**Pass:** correct structured responses are returned without file mutation and without loading unapproved Pi extensions.

### P7 — bounded edit

On a disposable fixture, allow one small code edit.

**Pass:** changed paths remain within allowlist; diff is returned; compiler/tests/static checks and post-edit diagnostics are attached; failure is reported rather than hidden.

### P8 — replay/rollback

Repeat the same bounded task from a clean disposable workspace and discard it afterward.

**Pass:** replay is operationally reproducible enough for review, and rollback is simply discarding the worker workspace/process without modifying the canonical repo.

## Promotion criteria

Promote M3 only if P1–P8 pass and:

- the bridge uses documented Pi RPC/CLI behavior;
- no third-party Pi extension is required for the critical path;
- canonical repo and unrelated host credentials are outside worker authority;
- one coding task completes end-to-end with objective evidence;
- a malicious-repo fixture cannot opt itself into extra Pi resources/capabilities;
- process timeout/cancellation and workspace cleanup have been exercised.

## Rollback

Disable/remove the Hermes→Pi bridge configuration/process launcher. Existing Hermes behavior remains available. Disposable workspaces are discarded; no canonical-repo migration is required.

## Non-goals

- sharing an in-process agent loop between Hermes and Pi;
- using Pi internal `AgentHarness` classes as a stable API;
- trusting project-local extensions by default;
- enabling arbitrary LSP refactors before read-only operations are proven;
- allowing the worker to decide its own sandbox/network policy.

## Primary references

- Pi RPC: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md
- Pi SDK / RPC alternative: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md
- Pi security: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/security.md
- Pi containerization: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/containerization.md
- Pi CLI flags: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/cli/args.ts
