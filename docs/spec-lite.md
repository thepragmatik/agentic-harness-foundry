# Spec-Lite Workflow

Status: `specified`

## Why this exists

GitHub Spec Kit is useful, mature, and intentionally comprehensive. Its default flow is `Specify -> Plan -> Tasks -> Implement -> Converge`, with optional clarification, analysis, presets, extensions, workflows, and agent integrations.

For this project, the full workflow is deliberately **not** the default because repeated prompt/template expansion can consume substantial agent context for small infrastructure changes. We retain the durable-artifact discipline while reducing mandatory artifacts and re-reading.

Reference: https://github.github.com/spec-kit/

## Core lifecycle

```text
research evidence
      |
      v
   spec.md
      |
      +---- plan.md   (only when non-trivial)
      |
      v
  tasks.md
      |
      v
experiment / implementation
      |
      v
 evidence
      |
      v
promotion / rejection ADR
```

## Artifact contract

### `spec.md` — mandatory

Keep it concise. It MUST contain:

1. **Status**
2. **Problem / desired outcome**
3. **Scope and non-goals**
4. **Invariants** — what must never be violated
5. **Acceptance criteria** — measurable pass/fail conditions
6. **Compatibility target** — exact upstream version/commit where applicable
7. **Rollback / disable path**
8. **References** — only sources directly needed to justify the design

Target size: normally 1–3 pages, not a research report.

### `plan.md` — conditional

Create only if at least one is true:

- multiple viable implementation approaches exist;
- data/schema migration is required;
- the change crosses trust/security boundaries;
- multiple upstream components interact;
- rollback is non-trivial;
- staged rollout is required.

It SHOULD contain architecture choices, rejected alternatives, dependency order, and rollback mechanics. Do not restate the full spec.

### `tasks.md` — mandatory

Tasks MUST be atomic, ordered, checkable, and small enough for an agent to execute without loading the entire repository.

Each task uses this compact form:

```markdown
- [ ] T012 Add context-packet schema
  - Input: `docs/specs/context-packet.md`
  - Touch: `schemas/context-packet.schema.json`
  - Verify: `python -m pytest evals/context/test_schema.py`
  - Evidence: `evidence/context/T012-schema.txt`
  - Stop if: schema cannot represent provenance without raw secret material
```

### ADR — only for durable architectural decisions

An ADR is required when a decision changes a system boundary, security invariant, source-of-truth rule, or major dependency. Do not create ADRs for routine implementation details.

## Token-budget rules for agents

- Do not load all specs or research notes pre-emptively.
- `tasks.md` points to the exact spec/ADR sections needed for each task.
- Research is summarized into decision tables; raw source dumps are not included in routine execution context.
- Evidence files should contain machine-readable summaries plus links/paths to bulky raw logs.
- Update existing artifacts rather than generating parallel recap documents.
- A spec SHOULD state a maximum context bundle for its implementation agent when relevant.

## Relationship to GitHub Spec Kit

We borrow these ideas:

- intent before implementation;
- durable Markdown artifacts;
- explicit specification, plan, and task phases;
- convergence against acceptance criteria;
- agent-independent source-of-truth files.

We intentionally omit by default:

- full CLI initialization;
- generated constitution prompts;
- mandatory clarification/analyze/checklist phases;
- extension/preset/workflow catalogs;
- repeated multi-document restatement of the same requirements.

If a future workstream becomes large enough to justify full Spec Kit, adopt it only through a bounded experiment and compare token/latency overhead against this workflow.

## Promotion gate

Spec-Lite remains the project default unless full Spec Kit demonstrates a measurable improvement in implementation correctness or review quality that justifies its additional context and process cost.