# LCM + Mnemosyne Context and Token Optimization Playbook

Status: `specified`

Reviewed: 2026-09-14

This is a **separate tuning/research artefact** for M2. The normative ownership/security rules remain in `docs/specs/m2-context-memory-security.md`.

## Objective

Minimise paid/context tokens and reduce context decay while preserving exact recoverability.

The working hypothesis is deliberately narrow:

```text
Hermes raw session transcript
        |
        v
LCM = current-session context hierarchy + exact recovery
        |
        | only the bounded active context
        v
main model

Mnemosyne = curated cross-session durable memory
        |
        | only relevant durable facts/prefetch
        v
main model
```

The systems should be **complementary, not symmetric**. LCM should not become a second durable-memory system and Mnemosyne should not become a second active-transcript summariser.

---

## Empirical findings that shape the baseline

### 1. Hermes has one selected context engine

When `context.engine: lcm` is active, LCM owns compaction. Hermes core `compression.enabled` remains the global compaction gate, so it must stay enabled, but the built-in compressor threshold is not the authoritative LCM threshold.

LCM currently supports `lcm.context_threshold` in Hermes `config.yaml`; most other LCM settings are environment variables. Unknown `lcm.*` YAML keys are not silently equivalent to their `LCM_*` env counterparts.

**Consequence:** configure one threshold authority and verify it with live `lcm_status` after a normal turn.

### 2. LCM preserves raw messages; active context is still lossy

LCM stores raw rows and a summary DAG, so older details can be recovered through `lcm_grep`, `lcm_describe`, `lcm_expand`, or `lcm_expand_query`. Earlier compaction therefore trades live-prompt detail for lower token spend; it does not have to destroy the source evidence.

**Consequence:** optimise for a bounded active prompt and make drill-down part of the agent behaviour instead of trying to keep all raw context live.

### 3. Mnemosyne prompt injection can duplicate information already present in LCM

The Hermes provider adds memory context/prefetch to the prompt. Mnemosyne also has a best-effort `MNEMOSYNE_SELF_ECHO_ENABLED=1` integration that observes Hermes' `on_pre_compress` callback and can suppress provider-owned working-memory rows that are already represented in live context.

The feature is intentionally conservative: ambiguous proof falls back to ordinary recall; provider restart loses the suppression ledger; consolidated episodic rows can still be recalled.

**Consequence:** self-echo suppression is a promising LCM companion, but it must be treated as an experimental deduplication optimisation, not as correctness state.

### 4. Consolidated Mnemosyne rows are already excluded from hot context by default

Modern Mnemosyne excludes rows stamped `consolidated_at` from `get_context()` prompt injection unless `MNEMOSYNE_CONTEXT_INCLUDE_CONSOLIDATED=1` is explicitly enabled. They remain available through recall.

**Consequence:** keep this default. Re-including consolidated rows increases prompt duplication without improving durable storage.

### 5. Mnemosyne now defaults Hermes autosync toward user turns rather than assistant turns

Recent Mnemosyne releases default `sync_roles` to user turns only. This was specifically changed to reduce assistant-transcript noise.

**Consequence:** preserve `sync_roles: [user]` unless an evaluation proves assistant turns contain durable information that is otherwise lost.

### 6. Mnemosyne exposes a large tool surface, but it supports a tool allowlist

The current provider implements dozens of memory/graph/persona/sync/diagnostic tools. Every exposed schema can increase tool-definition context. Mnemosyne supports `memory.mnemosyne.tools` to restrict the tool surface while preserving provider context and prefetch.

**Consequence:** start with a minimal operational set rather than exposing every memory capability to every Hermes turn.

### 7. Mnemosyne local embeddings are the right default for this Foundry

The Hermes wrapper supports local FastEmbed/sqlite-vec. Remote embedding endpoints receive memory text and recall queries.

**Consequence:** local embeddings are both the privacy default and the simplest egress model.

### 8. LCM and Mnemosyne can share one local utility LLM service later

Hermes auxiliary compression supports a custom OpenAI-compatible endpoint. LCM uses the Hermes auxiliary summarisation path when no LCM-specific summary model is provided. Mnemosyne can independently point its consolidation LLM at an OpenAI-compatible local endpoint with `MNEMOSYNE_LLM_BASE_URL` / `MNEMOSYNE_LLM_MODEL`.

**Consequence:** after M1 qualifies Granite, one llama.cpp server can potentially service both LCM summaries and Mnemosyne consolidation without paid summarisation calls. This is a **post-M1 experiment**, not a precondition for M2.

---

## Recommended Foundry starting profile

This profile intentionally keeps advanced features off. It is a starting hypothesis to validate with T201-T203, not a claim that these values are universally optimal.

### Hermes `config.yaml`

```yaml
compression:
  # Required global gate even when LCM is the selected ContextEngine.
  enabled: true

context:
  engine: lcm

# LCM currently supports this specific YAML override.
lcm:
  # Start with upstream default; move only from measured prompt economics.
  context_threshold: 0.35

memory:
  provider: mnemosyne

  # Foundry preference: avoid a second always-injected durable-memory block.
  # Preserve the files as rollback artefacts, but do not inject them once
  # Mnemosyne has proven healthy in the disposable profile.
  memory_enabled: false
  user_profile_enabled: false

  mnemosyne:
    # Exact key spelling is version-sensitive; T004/T201 MUST inspect the
    # installed mnemosyne-hermes provider before applying this profile.
    auto_sleep: true
    sleep_threshold: 20

    # Newer Mnemosyne defaults to user-only autosync. Keep it explicit after
    # verifying the installed provider accepts this key.
    sync_roles:
      - user

    # Do not absorb obvious transient terminal/runtime noise as durable memory.
    # Keep this list conservative; a broad regex can destroy useful memories.
    ignore_patterns:
      - "^Traceback \\(most recent call last\\)"
      - "^\\s+at "

    # Tool names MUST be confirmed from the installed runtime tool list.
    # Start with only the capabilities that are needed during ordinary turns.
    tools:
      - mnemosyne_remember
      - mnemosyne_recall
      - mnemosyne_sleep
      - mnemosyne_stats
      - mnemosyne_get
      - mnemosyne_invalidate
      - mnemosyne_recall_diagnostics
```

### LCM environment — Phase A baseline

```bash
# Preserve upstream defaults unless the active workload proves a problem.
LCM_CONTEXT_THRESHOLD=0.35
LCM_FRESH_TAIL_COUNT=32
LCM_LEAF_CHUNK_TOKENS=20000
LCM_INCREMENTAL_MAX_DEPTH=3

# Avoid competing proactive memory injection. Mnemosyne is the cross-session
# proactive memory layer in this architecture.
LCM_PROACTIVE_RECALL_ENABLED=false

# Advanced/derived retrieval features remain off until a measured recall gap.
LCM_TEMPORAL_ROLLUPS_ENABLED=false
LCM_ADAPTIVE_RETRIEVAL_ENABLED=false
LCM_PREANSWER_EVIDENCE_ENABLED=false
LCM_ASSERTION_EXTRACTION_ENABLED=false
LCM_THRESHOLD_FULL_SWEEP_ENABLED=false
```

### Mnemosyne environment — Phase A baseline

```bash
# Local semantic retrieval; exact model may be pinned from installed defaults.
MNEMOSYNE_EMBEDDINGS_VIA_API=false

# Keep consolidated rows out of automatic hot prompt context.
MNEMOSYNE_CONTEXT_INCLUDE_CONSOLIDATED=0

# Do not enable a second wide retrieval pipeline before baseline measurements.
MNEMOSYNE_POLYPHONIC_RECALL=0
MNEMOSYNE_ENHANCED_RECALL=0

# Test this separately after ordinary provider recall is proven.
MNEMOSYNE_SELF_ECHO_ENABLED=0
```

### Important version rule

Mnemosyne's configuration surface has changed quickly. Current generated docs distinguish `auto_sleep_enabled`, environment-only keys, Hermes wrapper keys, and effective defaults that may differ from declared defaults. The Foundry MUST treat the installed provider's runtime config/tool surface as authoritative.

Before applying any example above:

```text
hermes memory status
hermes tools list | grep mnemosyne_
hermes config get memory.mnemosyne
hermes mnemosyne version     # when available in the installed wrapper
```

If a key is absent or renamed, stop and update this artefact from the pinned installed version rather than guessing.

---

## Recommended optimisation sequence

Do not enable all optimisations at once. Each stage should earn the next.

### O1 — eliminate duplicate memory authorities

**Change:** after Mnemosyne passes a disposable-profile canary, disable built-in `MEMORY.md` / `USER.md` injection with `memory_enabled: false` and `user_profile_enabled: false` while keeping the files untouched for rollback.

**Why:** Hermes otherwise renders built-in memory and the external memory-provider block additively. This is direct recurring context overhead and can also create conflicting versions of the same fact.

**Measure:** system-prompt tokens before/after and recall accuracy on 5 durable facts.

**Promotion:** keep disabled only if Mnemosyne recalls all required durable facts and the built-in block contributes no unique required information.

**Confidence:** **high**.

### O2 — minimise Mnemosyne tool schemas

**Change:** allowlist the smallest runtime-confirmed tool set needed for ordinary work.

Suggested initial role set:

- `mnemosyne_remember`
- `mnemosyne_recall`
- `mnemosyne_get` if exact-ID retrieval is useful
- `mnemosyne_invalidate`
- `mnemosyne_sleep`
- `mnemosyne_stats`
- `mnemosyne_recall_diagnostics`

Keep export/import/sync/graph/persona/shared-memory tools out of the routine schema unless a task needs them.

**Why:** provider context/prefetch continues while unnecessary JSON tool schemas disappear from the model tool surface.

**Measure:** request tool-definition tokens or total stable/volatile prompt delta, plus a tool-call smoke test.

**Confidence:** **high**, subject to installed tool names.

### O3 — keep automatic durable capture user-biased

**Change:** preserve user-only autosync and use conservative `ignore_patterns` for obvious runtime noise.

**Why:** assistant-generated text and raw error output are poor candidates for unquestioned durable authority and increase retrieval noise.

**Measure:** 20-turn synthetic session containing stable facts, assistant speculation, stack traces and transient task state. Inspect stored rows after sleep.

**Confidence:** **high** for user-only autosync; **medium** for any custom ignore regex.

### O4 — use Mnemosyne consolidation to remove hot-memory duplication

**Change:** keep auto-sleep enabled with the installed default threshold initially. Keep `MNEMOSYNE_CONTEXT_INCLUDE_CONSOLIDATED=0`.

**Why:** consolidated rows remain recallable but stop competing with unconsolidated working memory in automatic hot context.

**Measure:** working vs consolidated counts, injected-context size before/after sleep, and next-session recall of durable facts.

**Confidence:** **high** for excluding consolidated rows; **medium** for the optimal sleep threshold.

### O5 — test Mnemosyne self-echo suppression with LCM

**Change:** only after ordinary LCM compaction + Mnemosyne recall pass, set:

```bash
MNEMOSYNE_SELF_ECHO_ENABLED=1
```

**Why:** the feature is explicitly designed to observe Hermes pre-compression boundaries and suppress provider-owned working-memory candidates that would echo content still represented in live context.

**Cheap falsifier:** one session with a distinctive durable fact repeated before LCM compaction. Measure whether the fact is injected twice before and after compaction, and whether it remains recallable after it leaves live context.

**Reject if:** restart/session transitions make a required fact disappear or suppression causes recall holes.

**Confidence:** **medium**. Upstream calls this best-effort duplicate reduction, not exact context tracking.

### O6 — externalise oversized tool outputs through LCM

**Change:** if M0 proves tool/log output is a major prompt-growth source, test:

```bash
LCM_LARGE_OUTPUT_EXTERNALIZATION_ENABLED=true
# upstream default threshold is 12,000 characters
```

Do not change the threshold in the first experiment.

**Why:** LCM can persist large outputs and put compact references into its compaction serializer while keeping the raw payload recoverable.

If the current-turn/provider-visible replay itself remains the problem, separately test:

```bash
LCM_LARGE_OUTPUT_ACTIVE_REPLAY_STUBBING_ENABLED=true
# upstream default active-replay threshold is 25,000 tokens
```

**Do not simultaneously tune Hermes core tool spillover thresholds.** Hermes already has its own tool-result spillover mechanism; changing both layers at once makes token attribution and recovery ownership ambiguous.

**Confidence:** **high** that this reduces token pressure for genuinely large outputs; **medium** on the best threshold for this workload.

### O7 — cap the fresh LCM tail only if it grows pathologically

LCM protects 32 recent messages by default. A message-count tail can still be huge when recent tool turns are huge.

If O6 does not control the problem, test a token cap with `LCM_FRESH_TAIL_MAX_TOKENS` rather than immediately reducing `LCM_FRESH_TAIL_COUNT`.

Reason: the token-cap implementation still retains the newest message and complete assistant/tool-result groups, reducing the chance of cutting a tool interaction in half.

**Do not choose a production value from theory.** Derive it from the M0/M1 replay distribution.

**Confidence:** **medium**.

### O8 — use the local Granite service for both summary paths only after M1

After Granite is qualified, test one shared llama.cpp service rather than two separate local models.

Hermes/LCM path, conceptually:

```yaml
auxiliary:
  compression:
    provider: main-or-named-local-provider
    model: <pinned Granite model name>
    base_url: http://127.0.0.1:<llama-port>/v1
    reasoning_effort: low
```

Mnemosyne path:

```bash
MNEMOSYNE_LLM_ENABLED=true
MNEMOSYNE_LLM_BASE_URL=http://127.0.0.1:<llama-port>/v1
MNEMOSYNE_LLM_MODEL=<pinned Granite model name>
```

**Why:** summarisation/consolidation is recoverable auxiliary work and is a good target for local inference.

**Risks:**

- LCM and Mnemosyne can contend for the same llama.cpp server;
- reasoning models can over-generate summaries;
- a built-in Hermes compressor fallback may have different context-size requirements than LCM leaf summarisation;
- Mnemosyne's local/fallback chain is version-sensitive.

Run the server with a deliberately bounded concurrency policy and measure queueing during a sustained Hermes replay.

**Confidence:** **medium-high** as a cost-saving architecture; **unvalidated** on the target Mac until M1.

---

## Features to keep OFF initially

These are interesting but increase the decision surface or duplicate another layer's job.

| Feature | Initial posture | Reason |
|---|---|---|
| LCM proactive recall | **OFF** | Mnemosyne already owns cross-session proactive recall; dual injection risks duplication |
| LCM pre-answer evidence | **OFF** | another automatic context-injection path before a measured retrieval gap |
| LCM temporal rollups | **OFF** | derived summary hierarchy adds maintenance/summarisation work before demonstrated need |
| LCM assertion extraction | **OFF** | additional model/extraction calls and another structured-memory surface |
| LCM threshold full sweep | **OFF** | can spend multiple synchronous summary calls; not needed for baseline |
| LCM dynamic leaf chunking | **OFF** | upstream recommends threshold/tail/externalization tuning first |
| Mnemosyne polyphonic recall | **OFF** | upstream evaluation shows better phrasing tolerance but wider irrelevant recall; not a free win |
| Mnemosyne enhanced recall | **OFF** | upstream isolated probes showed no benefit in at least one measured small corpus; adds pipeline complexity |
| Mnemosyne consolidated hot-context inclusion | **OFF** | defeats consolidation's prompt-budget advantage |
| Mnemosyne remote embeddings | **OFF** | memory text/query egress + no obvious need on this host |
| provider + MCP against same Mnemosyne bank | **OFF** | duplicate tools/injection and ambiguous ownership |
| broad `MNEMOSYNE_CROSS_SESSION` search | **OFF initially** | prefer intentionally global/canonical durable facts; wide legacy-session search can raise irrelevant recall |

---

## Prompt-cache interaction

Hermes explicitly structures the system prompt for cache reuse. External memory-provider content lives in the volatile part of the cached system prompt, while later-turn provider recall is appended closer to the current user turn. Any automatic context system that mutates earlier messages can invalidate downstream prefix caching.

LCM itself states that it is **cache-friendly, not fully cache-aware**: it does not know whether a proposed mutation will break a currently hot provider cache.

Therefore:

1. do not enable cache-friendly/deferred LCM tuning until provider cache telemetry shows compaction churn is material;
2. prefer fewer, meaningful compaction/externalization boundaries over frequent tiny rewrites;
3. keep stable identity/instructions outside per-turn memory prefetch where possible;
4. avoid model/provider/account switches mid-session when provider prefix caching matters.

Do not infer a cache win from lower raw prompt size alone. Record billed/cache-read tokens from the external provider where available.

---

## Context-decay test fixture

Use one synthetic 30-40 turn session containing:

- 5 durable user/project facts;
- 5 transient facts that should expire with the task;
- 3 deliberate contradictions/supersessions;
- 2 large tool outputs with unique sentinel details;
- 2 untrusted repo/web instructions;
- one exact buried identifier required near the end;
- one `/new` or fresh-session recall check.

At checkpoints before compaction, after one LCM compaction, after Mnemosyne sleep, and in a new session, measure:

| Metric | Desired direction |
|---|---|
| active prompt tokens | down |
| memory/provider injected tokens | bounded/down |
| provider cache-read ratio | stable/up where supported |
| exact sentinel recovery | 100% |
| durable-fact recall | high |
| transient/untrusted durable admission | ~0 |
| duplicate semantic injections | ~0 |
| summary/consolidation external tokens | down, ideally local |
| retries caused by missing context | no increase |
| time-to-recover exact old detail | bounded |

### Minimal pass criteria for Foundry

A configuration is promoted only if all are true:

1. **0/5 durable facts lost** across the new-session check.
2. **0/2 untrusted instructions** become durable authority.
3. **Both large-output sentinels remain exactly recoverable** from raw evidence.
4. **No semantically duplicated memory block** is routinely injected from both active context and durable memory.
5. **Total external prompt/cache economics improve** versus the M0 baseline, or the configuration is rejected as non-paying complexity.

The first run does not need a large statistical benchmark. Re-run only if the result is close enough that noise could reverse the decision.

---

## Decision table

| Technique | Token upside | Context-decay risk | Foundry priority | Empirical confidence |
|---|---:|---:|---:|---:|
| single LCM + single Mnemosyne authority | high | low | **P0** | **high** |
| disable built-in MEMORY/USER injection after canary | medium-high | low with rollback | **P0** | **high** |
| Mnemosyne tool allowlist | medium | very low | **P0** | **high** |
| user-only Mnemosyne autosync | medium | low | **P0** | **high** |
| keep consolidated rows out of hot context | medium | low | **P0** | **high** |
| local embeddings | privacy + small latency/token benefit | low | **P0** | **high** |
| LCM large-output externalization | very high on tool-heavy sessions | low with raw refs | **P1** | **high** |
| Mnemosyne self-echo suppression | medium | medium | **P1** | **medium** |
| LCM fresh-tail token cap | medium | medium | **P1 only if needed** | **medium** |
| one Granite service for both summary paths | high paid-token upside | medium | **P1 after M1** | **medium-high architecture / unvalidated locally** |
| polyphonic/enhanced recall | uncertain | precision dilution possible | **defer** | **mixed** |
| dual proactive recall (LCM + Mnemosyne) | negative/duplicative likely | medium | **do not do** | **high** |

---

## Recommended M2 execution order

```text
1. prove installed versions + one ContextEngine / one MemoryProvider
2. canary Mnemosyne recall
3. remove built-in MEMORY/USER injection in disposable profile
4. shrink Mnemosyne tool surface
5. measure provider-context/prefetch tokens
6. prove LCM exact recovery through one compaction
7. prove Mnemosyne sleep + new-session durable recall
8. test self-echo suppression once
9. only if tool payloads dominate: enable LCM externalization
10. only after M1: test local Granite for summaries/consolidation
11. stop when economics + recovery targets pass
```

Do not tune retrieval weights, polyphonic voices, LCM chunking, rollups, or summary DAG parameters unless one of these steps exposes a specific failure that those knobs plausibly address.

---

## Primary sources

- Hermes configuration / context compression / auxiliary models: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/configuration.md
- Hermes context compression and prompt caching: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/context-compression-and-caching.md
- Hermes built-in memory configuration: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory.md
- Hermes memory-provider architecture: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory-providers.md
- LCM operator guide: https://github.com/stephenschoettler/hermes-lcm/blob/main/docs/operator-guide.md
- LCM configuration source: https://github.com/stephenschoettler/hermes-lcm/blob/main/config.py
- Mnemosyne canonical Hermes integration: https://github.com/mnemosyne-oss/mnemosyne/blob/main/docs/hermes-integration.md
- Mnemosyne generated configuration reference: https://github.com/mnemosyne-oss/mnemosyne/blob/main/docs/api/configuration.mdx
- Mnemosyne architecture / retrieval: https://github.com/mnemosyne-oss/mnemosyne/blob/main/docs/architecture.md
- Mnemosyne changelog / measured recall notes: https://github.com/mnemosyne-oss/mnemosyne/blob/main/CHANGELOG.md
- Mnemosyne Hermes tool schemas: https://github.com/mnemosyne-oss/mnemosyne/blob/main/integrations/hermes/src/mnemosyne_hermes/tools.py
