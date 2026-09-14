# Spec-Lite Workflow

Status: `specified`

## Why this exists

GitHub Spec Kit is useful and comprehensive, but repeatedly generating/reading specification, clarification, plan, checklist and task artifacts can consume substantial context for a small infrastructure project.

Foundry keeps the durable-artifact discipline while using **one execution ledger and a small set of normative specs**.

Reference: https://github.github.com/spec-kit/

## Core lifecycle

```text
research evidence
      |
      v
normative spec (only when needed)
      |
      v
root TASKS.md item
      |
      v
experiment / implementation
      |
      v
compact evidence
      |
      v
promote / reject / revise spec
```

## Source-of-truth contract

### `TASKS.md` — single execution ledger

There is only one active task ledger: root `TASKS.md`.

Tasks MUST be:

- atomic and ordered;
- bound to a governing spec when they change architecture/security/integration behavior;
- explicit about evidence path;
- explicit about `Stop if` conditions;
- small enough to execute without loading the whole repository.

Do **not** create another `tasks.md`, checklist or status recap for routine execution.

### `docs/specs/*.md` — normative contracts

Create or update a normative spec only when work needs an explicit interface, security/trust boundary, data contract, compatibility target or measurable promotion gate.

A spec SHOULD contain only:

1. **Status**
2. **Desired outcome**
3. **Scope / non-goals**
4. **Compatibility target**
5. **Invariants / selected integration surface**
6. **Acceptance tests / promotion criteria**
7. **Rollback / disable path**
8. **Primary references**

Target size: normally a few pages, not a research report.

Current normative specs:

- `docs/specs/local-model-admission.md`
- `docs/specs/m2-context-memory-security.md`
- `docs/specs/m3-pi-worker-rpc.md`

### `plan.md` — exceptional

Do not create a plan by default. Add one only when a single spec still contains multiple dependent migration sequences that cannot be expressed clearly in `TASKS.md`.

If created, it MUST NOT restate the full spec.

### ADR — only for durable architectural decisions

An ADR is required only when a decision changes a long-lived system/security boundary, source-of-truth rule or mandatory dependency and the rationale needs to survive after the implementation spec is superseded.

Do not create ADRs for routine implementation choices.

## Token-budget rules for agents

- Start from `AGENTS.md` + the current root `TASKS.md` item.
- Read only the governing spec named by that task.
- Read research notes only when the task needs the evidence behind a decision.
- Do not load all specs, research or evidence pre-emptively.
- Keep bulky logs out of prompts; reference files by path/hash.
- Update an existing authoritative artifact rather than generating a parallel recap.
- Stop when a task gate is reached; do not spend context inventing alternatives during execution.

## Relationship to GitHub Spec Kit

We retain:

- intent before implementation;
- durable Markdown source of truth;
- explicit acceptance criteria;
- agent-independent specifications;
- convergence against evidence.

We intentionally omit by default:

- Spec Kit CLI initialization;
- generated constitution prompts;
- mandatory clarify/analyze/checklist phases;
- per-feature task documents when root `TASKS.md` already carries execution state;
- extension/preset/workflow catalogs;
- repeated restatement of requirements across artifacts.

Full Spec Kit may be tested later only if a workstream becomes large enough to justify it and the correctness benefit is measured against its token/context overhead.

## Promotion gate

Spec-Lite remains the project process unless a concrete failure demonstrates that the reduced artifact set is insufficient. Process complexity is subject to the same **complexity must pay rent** rule as runtime architecture.
