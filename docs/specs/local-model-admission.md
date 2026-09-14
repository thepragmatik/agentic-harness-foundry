# Local Model Admission Specification

Status: `specified`

## Purpose

Minimize benchmark cost and prevent attractive-but-operationally-poor models from entering the Hermes stack.

## Fixed constraints

A candidate MUST satisfy all of the following before any workload-quality evaluation is run:

1. Runs through current `llama.cpp` with the Metal backend; no runtime fork is accepted for the default path.
2. Has a reproducible `Q6_K` GGUF and, where available, `Q5_K_M` GGUF. Q6 is the quality reference; Q5_K_M is permitted only as the lower-memory/throughput production option.
3. Fits inside a **28 GB total local-inference envelope**, including weights plus the runtime/KV/state needed by the qualification context.
4. Runs on the target 128 GB Apple Silicon laptop without swap pressure attributable to the local inference service.
5. Has no known long-session correctness defect relevant to Hermes-style chat/tool use in the pinned llama.cpp build.
6. Sustains useful throughput during a 20-minute mixed prefill/decode session rather than only a short `llama-bench` burst.

Failure of any hard constraint rejects the candidate without further benchmarking.

## Quantization decision rule

Do not create a quantization bake-off.

For each admitted model:

1. Run `Q6_K` first as the quality reference.
2. Run `Q5_K_M` only if Q6 leaves materially less context/runtime headroom than desired or its sustained throughput is operationally limiting.
3. Promote Q5_K_M only if it materially improves sustained operation **and** the compact utility-quality smoke test shows no critical regression versus Q6.
4. Stop once one quant meets the operating requirement; do not benchmark Q4/Q8 for completeness.

For the current Empero distill, published GGUF sizes are approximately 7.56 GB for Q6_K and 6.64 GB for Q5_K_M, so the weight saving alone is modest; the reason to test Q5 is sustained throughput/headroom, not mere disk size.

## Minimal qualification profile

The project intentionally avoids a broad benchmark suite. Run only:

### Q1 — Runtime and memory

- load Q6 in pinned llama.cpp/Metal;
- allocate a realistic Hermes context target (start at 16K; 32K only after 16K passes);
- record model-file size, process resident/wired memory, total inference allocation, swap delta, TTFT, prompt tok/s and decode tok/s;
- run Q5_K_M only if the quantization decision rule above is triggered.

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

## Candidate decision tree

Do **not** benchmark three models in parallel.

### Step A — primary

Start with `empero-ai/Qwen3.8-9B-Distill` Q6_K.

- If Q1–Q3 pass comfortably: **promote and stop model selection**.
- If quality passes but sustained throughput/headroom is limiting: run the same candidate at Q5_K_M.
- If Q5 passes: **promote and stop**.

### Step B — triggered efficiency challenger

Only if the Empero candidate fails primarily on sustained throughput/latency/runtime behavior, qualify `google/gemma-4-E4B-it`.

Rationale: Gemma 4 E4B is an official on-device model with ~8B stored parameters but ~4.5B effective compute and Per-Layer Embeddings (PLE), plus stock llama.cpp Gemma 4 support. It is a useful architecture challenger specifically for efficiency. Run Q6 first and Q5_K_M only under the same quantization trigger.

### Step C — quality fallback

Only if Empero fails the utility-quality gate rather than the efficiency gate, qualify official `Qwen/Qwen3.5-9B` Q6_K as the conservative fallback because it has broader published coding/tool/long-context evidence than the community distill.

This failure-directed decision tree keeps the active benchmark surface to **one model at a time**.

## Explicit exclusions at this gate

- `Qwen3.8-27B` Q6: weights alone consume roughly 23–24 GB, leaving inadequate margin inside the 28 GB service envelope for sustained-context operation.
- `Qwen3.8-Flash-Next`: far above the envelope even with n-gram/PLE disk offload; llama.cpp support is recent/evolving and the resident compute weights remain much too large.
- `DeepSeek-V4.1-Flash`: hundreds of billions of stored parameters plus large Engram tables; current consumer inference relies on substantial host/NVMe streaming and specialized implementations.
- MLX-only variants: out of scope by decision.
- Q4/IQ and Q8/BF16 variants: out of scope unless a future ADR reopens them.
- uncensored/abliterated variants: no demonstrated benefit for the intended utility role and add avoidable provenance/safety variability.

## Speculative decoding

MTP/DSpark/EAGLE-style acceleration is NOT part of initial admission. Establish the non-speculative baseline first. Enable a speculative mechanism only under a separate measured experiment; public llama.cpp Metal evidence has shown MTP can reduce rather than improve throughput on Apple Silicon.

## Promotion rule

The promoted utility configuration is the **first model + quant in the decision tree that passes Q1–Q3**. Do not continue benchmark exploration after the operating requirement is met unless production telemetry later exposes a concrete deficiency.

## Evidence output

Store one compact JSON/Markdown result under `evidence/local-model/` containing:

- machine identifier without secrets;
- macOS + llama.cpp commit/build;
- model repo/revision + GGUF SHA256;
- exact server arguments;
- quantization;
- memory/context settings;
- Q1–Q3 measurements;
- pass/reject decision and reason.
