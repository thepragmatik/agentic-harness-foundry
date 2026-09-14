# LCM + Mnemosyne Context and Token Optimization Playbook

Status: `specified` (not yet target-host validated)

Reviewed: 2026-09-14

This is a **separate tuning/research artefact** for M2. The normative ownership/security rules remain in `docs/specs/m2-context-memory-security.md`.

## Objective

Minimise paid/context tokens and context decay while preserving exact recoverability and keeping the two memory systems from doing the same job twice.

The Foundry working model is:

```text
Hermes durable raw transcript
        |
        v
LCM
current-session hierarchy, compaction, exact drill-down
        |
        | bounded active context only
        v
main model
        ^
        | bounded durable-memory recall only
        |
Mnemosyne
curated cross-session facts/preferences/decisions
```

The core rule is **complementary ownership, not symmetric recall**:

- LCM owns *what from this session remains live and how old session evidence is recovered*.
- Mnemosyne owns *what deserves to survive into another session*.
- Neither system should proactively inject information that the other already supplies unless a measured recall gap justifies it.

---

## Evidence-backed findings

### 1. LCM is the sole active context engine

Hermes selects one `ContextEngine`. With `context.engine: lcm`, LCM owns compaction. Hermes `compression.enabled` remains the global gate, so it must remain enabled, but LCM's threshold is the effective compaction threshold.

LCM currently accepts `lcm.context_threshold` from Hermes `config.yaml`; most other LCM controls remain `LCM_*` environment variables. Unknown `lcm.*` YAML keys are not interchangeable with arbitrary `LCM_*` variables.

**Foundry consequence:** one threshold authority; verify the resolved source with `lcm_status` after a normal turn.

### 2. There is no universal optimal LCM threshold

LCM's upstream default is `0.35`, but upstream model-aware presets use substantially different values (for example `0.75` on some benchmark-backed GPT/Codex routes). The operator guide explicitly recommends tuning against the **effective** context window and the active prompt budget you are willing to pay for.

Use:

```text
trigger_tokens = effective_context_tokens × LCM_CONTEXT_THRESHOLD
LCM_CONTEXT_THRESHOLD = desired_trigger_tokens / effective_context_tokens
```

**Foundry consequence:** do not hard-code `0.35` merely because it is the default. T006/M0 must establish current prompt economics first; T202 then chooses a desired trigger budget and derives the ratio.

### 3. LCM's storage can be lossless while active inference remains lossy

LCM preserves raw rows and builds a summary DAG. Older exact details can be recovered with `lcm_grep`, `lcm_describe`, `lcm_expand`, and `lcm_expand_query` rather than being kept in every active prompt.

**Foundry consequence:** optimise the live prompt aggressively enough to save tokens, but test drill-down recovery. "Raw data still exists" is not equivalent to "the main model automatically remembers it."

### 4. Mnemosyne can echo information that is still present through LCM

Mnemosyne's Hermes integration injects provider context/prefetch. It also ships a best-effort `MNEMOSYNE_SELF_ECHO_ENABLED=1` mode that observes Hermes' `on_pre_compress` callback and suppresses matching provider-owned working-memory candidates while they are still represented in live context.

Upstream explicitly describes this as best-effort: ambiguous proof falls back to ordinary recall, provider restart loses the suppression ledger, and consolidated episodic representations remain independently eligible.

**Foundry consequence:** self-echo suppression is one of the few features specifically complementary to LCM, but it is an experiment, not correctness state.

### 5. Consolidated Mnemosyne rows are already excluded from hot context by default

Current Mnemosyne excludes `consolidated_at` working-memory rows from `get_context()` prompt injection unless `MNEMOSYNE_CONTEXT_INCLUDE_CONSOLIDATED=1` is set. Consolidated information remains recallable through episodic retrieval.

**Foundry consequence:** keep consolidated hot-context inclusion **off**. Turning it back on defeats a major token benefit of consolidation.

### 6. User-only autosync is now the safer default

Mnemosyne changed Hermes autosync defaults to user turns only to avoid assistant-transcript noise.

**Foundry consequence:** keep `sync_roles: [user]` unless a test proves assistant turns contain durable information that cannot be represented as explicit memories.

### 7. The provider's tool schema is itself a context cost

Current Mnemosyne code implements dozens of memory, graph, persona, sync and diagnostic tools. Mnemosyne supports a `memory.mnemosyne.tools` allowlist while preserving provider context/prefetch behavior.

**Foundry consequence:** tool-surface minimisation is a low-risk token optimisation. Ordinary sessions should not carry graph/sync/export/persona schemas unless needed.

### 8. Mnemosyne's persona layer can become an always-on prompt tax

Current generated configuration enables persona support and exposes a persona token cap. Persona is useful for stable identity/behavior rules, but it can duplicate user/profile facts already available through durable memory.

**Foundry consequence:** start with persona injection disabled in the token-minimising profile. Re-enable it only if the new-session durable-fact fixture demonstrates a real stable-identity gap.

### 9. Local embeddings are the correct Foundry default

The Hermes wrapper supports local FastEmbed/sqlite-vec. Remote embedding endpoints receive memory text and recall queries.

**Foundry consequence:** local embeddings are the privacy default and avoid a second data-egress path. Remote embeddings require an explicit later policy decision.

### 10. One local Granite service can potentially serve both summary paths

Hermes auxiliary compression accepts a custom OpenAI-compatible `base_url`. LCM uses Hermes' auxiliary summarisation path when no LCM-specific summary model is selected. Mnemosyne can independently use an OpenAI-compatible endpoint for consolidation/fact-extraction with `MNEMOSYNE_LLM_BASE_URL` / `MNEMOSYNE_LLM_MODEL`.

**Foundry consequence:** after M1 qualifies Granite, one llama.cpp service can potentially remove paid summarisation calls from both LCM and Mnemosyne. This is post-M1 and must be measured for queueing/thermal contention.

---

## Recommended Phase-A topology

The starting profile deliberately enables the minimum number of automatic context mechanisms.

### Hermes configuration skeleton

Apply only after T004/T201 confirms the installed versions accept the keys shown.

```yaml
compression:
  # LCM still depends on Hermes' global compaction gate.
  enabled: true

context:
  engine: lcm

# Set ONE explicit threshold source only after M0 establishes the desired
# active-prompt trigger. Example only:
# lcm:
#   context_threshold: 0.50

memory:
  provider: mnemosyne

  # After the Mnemosyne canary passes in a disposable profile, disable the
  # built-in blocks to prevent additive MEMORY.md/USER.md injection.
  # Keep the files untouched for rollback.
  memory_enabled: false
  user_profile_enabled: false

  mnemosyne:
    # Mnemosyne key names/effective defaults have moved between releases.
    # Confirm these names against the installed wrapper before applying.
    auto_sleep: true
    sleep_threshold: 20

    # Keep automatic transcript capture user-biased.
    sync_roles:
      - user

    # Durable facts should be made global/canonical intentionally rather than
    # making every captured memory cross-session by default.
    default_scope: session

    # Start without an always-on persona block. Re-enable only if measured need.
    persona_enabled: false

    # Current upstream default is 2000 chars. Keep it initially; if C4 shows
    # excessive memory injection, halve it once and rerun the recall fixture.
    prefetch_content_chars: 2000

    # Filter only obvious technical noise. Broad regexes can destroy evidence.
    ignore_patterns:
      - "^Traceback \\(most recent call last\\)"
      - "^\\s+at "

    # Confirm exact tool names from `hermes tools list` first.
    tools:
      - mnemosyne_remember
      - mnemosyne_recall
      - mnemosyne_get
      - mnemosyne_invalidate
      - mnemosyne_sleep
      - mnemosyne_stats
      - mnemosyne_recall_diagnostics
```

### LCM environment — Phase A

Do **not** re-declare the context threshold here if it is already set through `lcm.context_threshold` in `config.yaml`.

```bash
# Keep a single proactive memory layer: Mnemosyne.
LCM_PROACTIVE_RECALL_ENABLED=false

# Keep advanced/derived retrieval paths out of the baseline.
LCM_TEMPORAL_ROLLUPS_ENABLED=false
LCM_ADAPTIVE_RETRIEVAL_ENABLED=false
LCM_PREANSWER_EVIDENCE_ENABLED=false
LCM_ASSERTION_EXTRACTION_ENABLED=false
LCM_THRESHOLD_FULL_SWEEP_ENABLED=false
LCM_DYNAMIC_LEAF_CHUNK_ENABLED=false
```

Unless the installed configuration already differs, initially retain LCM's other upstream defaults (fresh tail 32 messages, leaf chunk 20K tokens, incremental depth 3). Change them only after the specific failure they address has been measured.

### Mnemosyne environment — Phase A

```bash
# Local retrieval; do not send memory/query text to an embedding API.
MNEMOSYNE_EMBEDDINGS_VIA_API=false

# Consolidated material remains recallable but should not re-enter hot context.
MNEMOSYNE_CONTEXT_INCLUDE_CONSOLIDATED=0

# Avoid a wider retrieval pipeline before proving the default path insufficient.
MNEMOSYNE_POLYPHONIC_RECALL=0
MNEMOSYNE_ENHANCED_RECALL=0

# Baseline first; enable in its own experiment after ordinary recall passes.
MNEMOSYNE_SELF_ECHO_ENABLED=0
```

### Version rule

Mnemosyne's generated configuration currently lists more than 100 keys plus environment-only controls, and several effective defaults have historically differed from declared defaults. The installed package/runtime is authoritative.

Before applying this profile:

```text
hermes memory status
hermes tools list | grep mnemosyne_
hermes config get memory.mnemosyne
hermes mnemosyne version        # when supported by installed wrapper
lcm_status                      # after one normal Hermes turn
```

If a key is absent/renamed, stop and update this artefact from the pinned installed version rather than guessing.

---

## Optimisation ladder

Each step changes one material variable and reuses the same fixture.

### O1 — remove duplicate built-in memory injection

After a Mnemosyne canary succeeds, disable built-in `MEMORY.md` and `USER.md` injection in a disposable profile while retaining the files for rollback.

**Why:** Hermes renders built-in memory and external provider memory additively when both are enabled.

**Cheap test:** five durable facts, including one preference and one project decision. Compare prompt tokens and new-session recall before/after.

**Keep if:** 5/5 durable facts remain available and prompt overhead falls.

**Confidence:** **high**.

### O2 — shrink Mnemosyne's routine tool surface

Use `memory.mnemosyne.tools` to keep only the runtime-confirmed ordinary tools. Defer export/import/sync/graph/persona/shared-memory operations to operator/specialist profiles when possible.

**Why:** provider context still works while unnecessary JSON schemas no longer occupy the normal tool surface.

**Cheap test:** record prompt/tool-definition tokens before/after; call `remember`, `recall`, exact `get`, and diagnostics once.

**Confidence:** **high**, with installed tool names as the compatibility gate.

### O3 — keep automatic capture precise

Keep `sync_roles: [user]`, `default_scope: session`, and conservative `ignore_patterns`.

Durable cross-session facts should be made `scope=global` or canonical **intentionally** through memory admission, rather than making every auto-captured row global.

**Why:** this reduces assistant hallucination/transient task state becoming cross-session retrieval noise.

**Cheap test:** synthetic session with stable user facts, assistant speculation, shell noise, transient task state and one explicit global fact; inspect stored scopes/content.

**Confidence:** **high** for user-only capture/default-session scope; **medium** for custom regex filters.

### O4 — use consolidation as a prompt-budget boundary

Keep auto-sleep enabled and `MNEMOSYNE_CONTEXT_INCLUDE_CONSOLIDATED=0`.

**Why:** consolidated information remains recallable without continuously competing in working-memory prompt context.

**Cheap test:** measure working/consolidated counts, injected context size before/after sleep, and next-session recall.

**Confidence:** **high** for excluding consolidated rows; **medium** for the optimal sleep threshold.

### O5 — test persona injection only if needed

Start persona injection off. If the durable-fact/new-session fixture loses stable identity/preferences despite ordinary recall, re-enable persona with a deliberately small token cap and rerun the same fixture.

**Why:** persona can improve always-on identity continuity, but it is also an always-on prompt block and may duplicate canonical/global memory.

**Confidence:** **medium**; value depends strongly on workload.

### O6 — test Mnemosyne self-echo suppression against LCM

Only after normal LCM compaction and Mnemosyne recall pass:

```bash
MNEMOSYNE_SELF_ECHO_ENABLED=1
```

**Why:** this feature was designed to reduce automatic-memory echo around Hermes compression boundaries.

**Cheap falsifier:** store a distinctive fact that remains in live session context. Measure whether it appears redundantly in Mnemosyne prefetch before compaction; then compact and prove it becomes recallable when it is no longer safely represented live.

**Reject if:** restart/boundary ambiguity produces a recall hole.

**Confidence:** **medium**; upstream explicitly calls it best-effort.

### O7 — externalise large tool outputs through LCM

If M0 shows tool/log payloads dominate prompt growth, test:

```bash
LCM_LARGE_OUTPUT_EXTERNALIZATION_ENABLED=true
# upstream default threshold: 12,000 characters
```

Do not change the threshold in the first run.

If provider-visible current-turn replay is still the expensive path, separately test:

```bash
LCM_LARGE_OUTPUT_ACTIVE_REPLAY_STUBBING_ENABLED=true
# upstream default replay-stub threshold: 25,000 tokens
```

**Why:** large raw payloads remain recoverable while active context carries compact references.

**Important:** Hermes also has core tool spillover controls. Do not tune Hermes spillover and LCM externalization simultaneously; first assign one layer responsibility so savings and recovery failures remain attributable.

**Confidence:** **high** for tool-heavy sessions; threshold optimum remains workload-specific.

### O8 — cap the LCM fresh tail only if externalization is insufficient

LCM's default fresh tail protects 32 recent messages. If recent large turns remain expensive after O7, test `LCM_FRESH_TAIL_MAX_TOKENS` before reducing the message count.

The token-cap implementation preserves the newest message and complete assistant/tool-result groups, reducing the chance of splitting a tool exchange.

**Do not choose a value from theory.** Derive it from the replay's recent-tail distribution.

**Confidence:** **medium**.

### O9 — use one local Granite service for both summary paths after M1

After Granite passes M1, test a single llama.cpp OpenAI-compatible service for auxiliary summary work.

Hermes/LCM conceptual path:

```yaml
auxiliary:
  compression:
    model: <llama-server model id>
    base_url: http://127.0.0.1:<port>/v1
```

Mnemosyne path:

```bash
MNEMOSYNE_LLM_ENABLED=true
MNEMOSYNE_LLM_BASE_URL=http://127.0.0.1:<port>/v1
MNEMOSYNE_LLM_MODEL=<llama-server model id>
```

**Why:** LCM summarisation and Mnemosyne consolidation are recoverable auxiliary work, making them strong candidates for local inference and paid-token elimination.

**Risks:** shared-server queueing, thermal contention, over-generation, and version-sensitive Mnemosyne fallback behavior. Also verify that any accidental fallback to Hermes' built-in compressor does not exceed the local model's context capacity.

**Test:** one 20-minute Hermes replay with at least one LCM compaction and one Mnemosyne consolidation; record local queue latency, generation tokens, peak inference memory and external auxiliary tokens.

**Confidence:** **medium-high architecture / unvalidated on target Mac**.

### O10 — tune prefetch size only after deduplication

Current Mnemosyne generated configuration defaults `prefetch_content_chars` to 2000. Do not immediately shrink it: first eliminate duplicated stores/tools/persona/self-echo.

If C4 still shows excessive injected memory, test **one** smaller value (for example 1000 chars) on the same durable-fact fixture.

**Keep if:** prompt tokens fall with no recall-answer degradation.

**Confidence:** **medium**; exact value is workload-dependent.

---

## Features to keep OFF initially

| Feature | Initial posture | Reason |
|---|---|---|
| LCM proactive recall | **OFF** | Mnemosyne already owns cross-session proactive recall; dual automatic injection is likely duplicative |
| LCM pre-answer evidence | **OFF** | another automatic prompt-injection path before a measured retrieval gap |
| LCM temporal rollups | **OFF** | derived summary hierarchy and maintenance work before demonstrated need |
| LCM assertion extraction | **OFF** | another structured-memory/extraction surface and extra model calls |
| LCM threshold full sweep | **OFF** | may spend many synchronous summary calls; unnecessary for baseline |
| LCM dynamic leaf chunking | **OFF** | upstream recommends threshold/tail/externalization as first tuning knobs |
| Mnemosyne persona injection | **OFF initially** | always-on context cost; may duplicate global/canonical memories |
| Mnemosyne polyphonic recall | **OFF** | upstream measured better phrasing tolerance but wider irrelevant recall; not a free win |
| Mnemosyne enhanced recall | **OFF** | extra pipeline complexity; upstream isolated small-corpus probes showed no improvement in one published comparison |
| consolidated rows in hot context | **OFF** | defeats consolidation's context-budget benefit |
| Mnemosyne remote embeddings | **OFF** | sends memory text and queries outside the host |
| provider + MCP for same bank | **OFF** | duplicate tool/injection surface and ambiguous ownership |
| broad cross-session search | **OFF initially** | prefer intentionally global/canonical durable facts over searching every historical session |

---

## Prompt-cache interaction

Hermes explicitly organizes prompt material for cache reuse. External provider memory is part of the more volatile system-prompt region, and later-turn recalled context is injected near the active user turn. Compaction or rewriting of earlier messages can invalidate downstream cache prefixes.

LCM itself describes its current policy as **cache-friendly, not fully cache-aware**: it does not have reliable forward-looking provider cache state/cache-break information.

Therefore:

1. measure provider cache-read/write tokens where available, not just raw prompt size;
2. prefer fewer meaningful compaction/externalization boundaries over frequent tiny rewrites;
3. do not enable LCM cache-friendly/deferred-maintenance tuning unless cache telemetry shows compaction churn is actually material;
4. avoid mid-session model/provider/account switching where provider prefix caching matters;
5. keep stable instructions/identity out of per-turn recalled memory when possible.

---

## Context-decay test fixture

Use one synthetic 30-40 turn replay containing:

- 5 durable user/project facts;
- 5 transient task facts;
- 3 contradictions/supersessions;
- 2 large tool outputs, each containing a unique sentinel detail;
- 2 untrusted repo/web instructions that must never become durable authority;
- 1 exact buried identifier required near the end;
- 1 fresh-session recall check.

Measure at four checkpoints:

1. before LCM compaction;
2. after one LCM compaction;
3. after Mnemosyne consolidation/sleep;
4. in a fresh session.

| Metric | Desired direction |
|---|---|
| active prompt tokens | down |
| Mnemosyne injected tokens | bounded/down |
| provider cached-read ratio where supported | stable/up |
| exact sentinel recovery | 100% |
| durable-fact recall | 100% on the five fixture facts |
| transient/untrusted durable admission | 0 |
| duplicate semantic injections | 0 routine duplicates |
| external summary/consolidation tokens | down, ideally zero after local path |
| retries caused by missing context | no increase |
| exact-old-detail recovery latency | bounded and reproducible |

### Minimal promotion criteria

Promote a configuration only if all are true:

1. **0/5 durable facts lost** in the fresh-session check.
2. **0/2 untrusted instructions** become durable authority.
3. **2/2 large-output sentinels remain exactly recoverable** from raw evidence.
4. **The buried identifier remains exactly recoverable** after compaction.
5. **No routine semantically equivalent memory block** is injected from both active context and durable memory.
6. **External prompt/cache economics improve** versus M0, or the added feature is rejected as non-paying complexity.

This is intentionally a small deterministic fixture. Do not turn it into a benchmark suite unless results are close enough that repeated measurement could change the decision.

---

## Decision table

| Technique | Token upside | Context-decay risk | Priority | Confidence |
|---|---:|---:|---:|---:|
| one LCM + one Mnemosyne authority | high | low | **P0** | **high** |
| disable built-in MEMORY/USER injection after canary | medium-high | low with rollback | **P0** | **high** |
| Mnemosyne tool allowlist | medium | very low | **P0** | **high** |
| user-only autosync + intentional global scope | medium | low | **P0** | **high** |
| consolidated rows excluded from hot context | medium | low | **P0** | **high** |
| local embeddings | privacy + modest latency/egress benefit | low | **P0** | **high** |
| persona off initially | medium | medium if identity facts are under-recalled | **P0** | **medium** |
| LCM large-output externalization | very high on tool-heavy sessions | low with raw refs | **P1** | **high** |
| Mnemosyne self-echo suppression | medium | medium | **P1** | **medium** |
| LCM fresh-tail token cap | medium | medium | **P1 only if needed** | **medium** |
| one Granite service for both summary paths | high paid-token upside | medium | **P1 after M1** | **medium-high architecture / local evidence pending** |
| smaller Mnemosyne prefetch cap | medium | medium | **P1 only if injection still high** | **medium** |
| polyphonic/enhanced recall | uncertain | irrelevant-recall/complexity risk | **defer** | **mixed** |
| dual proactive recall (LCM + Mnemosyne) | likely negative | medium | **do not do** | **high** |

---

## Recommended M2 execution order

```text
1. pin installed LCM + Mnemosyne configuration/tool surfaces
2. prove one ContextEngine + one MemoryProvider
3. canary Mnemosyne write/recall in disposable profile
4. disable built-in MEMORY/USER injection; re-run canary
5. shrink Mnemosyne tool surface; measure schema/prompt delta
6. prove LCM compaction + exact drill-down recovery
7. prove Mnemosyne sleep + fresh-session durable recall
8. test persona only if stable facts are missing
9. test self-echo suppression once
10. if tool payloads dominate, enable LCM externalization
11. if live tail remains oversized, test one fresh-tail token cap
12. after M1 only, test Granite for both summary paths
13. stop when recovery + token economics pass
```

Do **not** tune retrieval weights, polyphonic voices, LCM chunking, rollups, cache-friendly condensation, or additional summary DAG settings unless the preceding tests expose a specific failure those controls plausibly address.

---

## Primary sources

- Hermes configuration / auxiliary models / tool spillover: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/configuration.md
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
