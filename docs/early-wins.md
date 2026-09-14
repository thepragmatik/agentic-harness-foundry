# Early Wins

Status: `specified`

The first implementation goal is **not** to add a local model, router, gateway or Pi worker. It is to harvest cheap, reversible savings and observability from the existing stack.

## Priority order

| Priority | Early win | Why it is cheap | Expected value | Promotion signal |
|---|---|---|---|---|
| **E1** | Pin versions/config and capture three reproducible baseline tasks | read-only | Very high leverage: every later claim becomes attributable | T001–T006 complete |
| **E2** | Remove duplicate context/memory injection | configuration/trace inspection first | Potentially high token saving every turn | Same task quality, fewer billed/prompt tokens |
| **E3** | Spill oversized tool/log output to raw artifact + compact pointer/excerpt | deterministic; no LLM required initially | High on tool-heavy/coding sessions | Lower external tokens with exact raw fallback |
| **E4** | Remove repeated static prompt/tool-schema material where safe | deterministic prompt hygiene | Medium–high recurring saving | Stable behavior + reduced repeated prefix |
| **E5** | Stabilize reusable prompt prefix ordering for provider cache reuse | mostly ordering/config discipline | Medium recurring cost/latency improvement where provider cache applies | Better cache-read/reuse metrics without quality change |
| **E6** | Detect LCM/Mnemosyne overlap before tuning either | one trace + config inspection | Avoids paying twice for summarization/retrieval | One clear authority per context/memory responsibility |
| **E7** | One local context-packet pilot for the noisiest artifact class | one model, one artifact class only | Potentially high cloud-token reduction | Material token reduction, no material retries/quality loss |

## What is deliberately *not* an early win

These may be valuable later, but they are not allowed to distract M0/M1:

- learned routing / ModernBERT;
- multi-model committees;
- speculative decoding;
- global summarization of every tool result;
- refactoring Pi via LSP before read-only LSP works;
- broad prompt-injection classifier training;
- replacing LCM/Mnemosyne before measuring them;
- benchmarking many local models because they are available.

## Why these wins come first

The first six wins share three properties:

1. they are cheap to test;
2. they are reversible;
3. they reduce waste or uncertainty **before** adding another probabilistic component.

This keeps the build honest. If deterministic hygiene already removes most avoidable token cost, later local-model/routing complexity may not be needed.

## Immediate harvesting sequence

```text
observe current stack
      |
      v
find duplication / oversized payloads
      |
      v
change one thing
      |
      v
replay same fixture
      |
      +--> no measurable benefit -> revert / record
      |
      +--> benefit, no regression -> keep
      |
      v
next cheapest waste source
```

Do not batch E2–E6 into one change. The purpose is to learn which optimization actually pays.

## Expected first useful outcomes

By the end of M0 we should know, with evidence:

- whether context/memory is being injected more than once;
- which tool/artifact types dominate prompt growth;
- how much repeated static material is present;
- whether provider cache reuse is being harmed by avoidable prefix churn;
- the before/after token and latency effect of each retained deterministic change.

By the first half of M1 we should know whether Granite can cheaply turn the single worst high-volume artifact class into a recoverable context packet. Only then does broader local preprocessing become eligible.
