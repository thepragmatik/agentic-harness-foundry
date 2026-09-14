# Local Model Admission Specification

Status: `specified`

## Purpose

Minimize benchmark cost and prevent attractive-but-operationally-poor models from entering the Hermes stack.

## Fixed constraints

A candidate MUST satisfy all of the following before any workload-quality evaluation is run:

1. Runs through current `llama.cpp` with the Metal backend; no runtime fork is accepted for the default path.
2. Has a reproducible `Q6_K` GGUF (or documented Q6-equivalent only when plain Q6_K is technically unavailable).
3. Fits inside a **28 GB total local-inference envelope**, including weights plus the runtime/KV/state needed by the qualification context.
4. Runs on the target 128 GB Apple Silicon laptop without swap pressure attributable to the local inference service.
5. Has no known long-session correctness defect relevant to Hermes-style chat/tool use in the pinned llama.cpp build.
6. Sustains useful throughput during a 20-minute mixed prefill/decode session rather than only a short `llama-bench` burst.

Failure of any hard constraint rejects the candidate without further benchmarking.

## Minimal qualification profile

The project intentionally avoids a broad benchmark suite. Run only:

### Q1 — Runtime and memory

- load the Q6 model in pinned llama.cpp/Metal;
- allocate a realistic Hermes context target (start at 16K; 32K only after 16K passes);
- record model-file size, process resident/wired memory, total inference allocation, swap delta, TTFT, prompt tok/s and decode tok/s.

**Pass:** model + required inference state stay below 28 GB and do not induce sustained swap growth.

### Q2 — Sustained Hermes-shaped session

Run one 20-minute replay containing:

- repeated chat turns;
- one oversized tool/log input;
- structured JSON output;
- one code/LSP-style analysis request;
- context reuse / prompt-cache behavior where supported.

Record throughput by interval and the slowest 5-minute window.

**Pass:** no correctness degeneration, server stall, runaway memory growth, or material thermal collapse. Exact throughput threshold is recorded after the target Mac baseline is known; until then compare candidates on the same replay.

### Q3 — Utility-quality smoke test

Use a compact fixed set of 10–20 examples covering only the intended local jobs:

- evidence-preserving log/tool-output distillation;
- schema-constrained extraction;
- memory-candidate extraction with provenance;
- code/LSP diagnostic summarisation.

**Pass:** no critical evidence omissions in the safety-critical examples and schema-valid structured output at the declared threshold.

## Candidate policy

To minimize decision surface, at most **two full candidates plus one incumbent/control** may be active at a time.

Current shortlist:

1. `empero-ai/Qwen3.8-9B-Distill` Q6_K — primary challenger.
2. `Qwen/Qwen3.5-9B` Q6_K — conservative control.

Do not add another model unless one of the current candidates is rejected or an architecture/model release supplies compelling new evidence against this shortlist.

## Explicit exclusions at this gate

- `Qwen3.8-27B` Q6: weights alone consume roughly 23–24 GB, leaving inadequate margin inside the 28 GB service envelope for sustained-context operation; public M4 Max evidence also shows modest single-stream decode in at least one laptop configuration.
- `Qwen3.8-Flash-Next`: far above the envelope even with n-gram/PLE disk offload; stock llama.cpp support remains young and the resident compute weights remain much too large.
- `DeepSeek-V4.1-Flash`: hundreds of billions of stored parameters plus large Engram tables; current consumer inference relies on substantial host/NVMe streaming and non-stock implementations.
- MLX-only variants: out of scope by decision.
- Q4/Q5/IQ quants: out of scope by decision.
- uncensored/abliterated variants: no demonstrated benefit for the intended utility role and add avoidable provenance/safety variability.

## Speculative decoding

MTP/DSpark/EAGLE-style acceleration is NOT part of initial admission. Establish the non-speculative baseline first. Enable a speculative mechanism only under a separate measured experiment; public llama.cpp Metal evidence has shown MTP can reduce rather than improve throughput on Apple Silicon.

## Promotion rule

The promoted utility model is the **simplest candidate that passes Q1–Q3**. Do not spend additional benchmark budget looking for marginal gains after a candidate meets the operational and quality requirements unless observed production telemetry later exposes a concrete deficiency.

## Evidence output

Store one compact JSON/Markdown result under `evidence/local-model/` containing:

- machine identifier without secrets;
- macOS + llama.cpp commit/build;
- model repo/revision + GGUF SHA256;
- exact server arguments;
- memory/context settings;
- Q1–Q3 measurements;
- pass/reject decision and reason.
