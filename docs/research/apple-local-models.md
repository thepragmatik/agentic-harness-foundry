# Apple Silicon Local Utility Model Assessment

Status: `researching`

Date reviewed: 2026-09-14

## Fixed operating envelope

- Target host: Apple Silicon laptop, 128 GB unified memory.
- Local inference allocation: **28 GB hard planning envelope** for model weights + llama.cpp runtime/KV/state.
- Runtime: **llama.cpp / Metal only**.
- Quantization: **Q6_K reference**, **Q5_K_M conditional production option**.
- Goal: sustained Hermes utility inference while preserving system headroom for Pi, LSPs, builds/tests, browser/tooling and macOS.

## Narrowed decision

The active decision surface is intentionally only two model families:

1. **Primary:** `empero-ai/Qwen3.8-9B-Distill`.
2. **Control:** official `Qwen/Qwen3.5-9B`.

The Empero model is a community full-parameter distillation into the Qwen3.5-9B architecture using roughly 70K private teacher traces from the official Qwen3.8 large teacher. Its public capability evidence is narrower than Qwen's official Qwen3.5 evidence, so it is promising rather than pre-approved.

For Empero's official GGUF release, published sizes are approximately:

| Quant | Weight size | Foundry role |
|---|---:|---|
| Q5_K_M | 6.64 GB | production option if it materially improves sustained operation |
| Q6_K | 7.56 GB | quality reference |

Both leave ample room inside the 28 GB inference envelope for practical context/runtime state; the qualification still has to prove that on the actual Mac.

## Why the larger newest architectures are not active candidates

### Qwen3.8-27B

Q6 weights alone are roughly in the 23–24 GB class. That technically fits under 28 GB but leaves too little margin for realistic context/runtime state. Public Apple/llama.cpp evidence also does not justify spending our limited qualification budget on it as an always-on Hermes utility model.

**Posture:** excluded from current local qualification.

### Qwen3.8-Flash-Next

This is a new open architecture preview for Qwen4, not a small laptop `Flash` model. It has ~125B main-model parameters with ~6B active per token, plus ~51B n-gram/PLE embedding parameters and an MTP component. The lookup memory can be offloaded, but the compute backbone remains far outside the 28 GB Q5/Q6 envelope. llama.cpp support is also recent and still seeing architecture-specific correctness/performance work.

**Posture:** architecture watchlist only.

### DeepSeek-V4.1-Flash

Despite low active compute (8B input / 16B output), it has a 552B backbone and very large Engram conditional-memory tables. Reduced active FLOPs do not mean reduced stored-model footprint. Current consumer inference approaches depend on large host memory/NVMe and specialized paths.

**Posture:** architecture research only.

See [`conditional-memory-architectures.md`](conditional-memory-architectures.md).

## Quantization policy

Do not run Q5 and Q6 automatically.

1. Qualify Q6 first.
2. If Q6 comfortably passes the 28 GB envelope and sustained-session gate, stop.
3. If Q6 is operationally limiting, run the same qualification with Q5_K_M.
4. Promote Q5 only if it produces a meaningful operational gain without critical evidence-retention/schema regression.

This avoids turning quantization into another benchmark surface.

## Appropriate local-model jobs

Prioritize high-volume, recoverable, verifiable work:

| Workload | Expected value | Required safeguard |
|---|---:|---|
| compiler/test/log distillation | very high | retain raw artifact + provenance |
| oversized tool-output compression | very high | typed context packet + raw fallback |
| LSP/repository reconnaissance summary | high | exact symbol/file references |
| candidate durable-memory extraction | high | admission policy + provenance |
| structured extraction | high | schema validation |
| retrieval/query rewrite | medium | deterministic fallback |
| LCM summary generation | potentially high | exact-message recovery tests |
| routing prediction | uncertain | shadow mode only after telemetry |
| security classification | advisory only | deterministic policy remains authoritative |

## Minimal Apple qualification

Do not run generic leaderboards locally. Use the short admission spec in [`../specs/local-model-admission.md`](../specs/local-model-admission.md):

- 16K runtime/memory check;
- one 20-minute Hermes-shaped sustained replay;
- 10–20 utility examples covering evidence retention, structured extraction, memory extraction and code/LSP summarisation.

Only move to 32K if 16K passes and the real workflow needs it.

## Critical review

- Empero's distill has promising public MMLU transfer but much thinner public coding/tool/long-context evidence than official Qwen3.5-9B.
- The distill's reasoning behavior can generate substantial `<think>` output, which may make it slower than expected for simple transformation jobs; local qualification must measure total generated tokens, not only tok/s.
- Q5 may reduce memory/latency slightly, but at this 9B scale the weight difference from Q6 is under 1 GB; do not assume Q5 is automatically the better production choice.
- Recent conditional-memory architectures reduce active compute and/or KV cost but do not make their enormous stored parameter sets fit a 28 GB Q5/Q6 laptop envelope.
- A short synthetic `llama-bench` burst is insufficient evidence for a model that will remain loaded through sustained Hermes sessions.

## Primary sources

- Empero Qwen3.8-9B Distill GGUF: https://huggingface.co/empero-ai/Qwen3.8-9B-Distill-GGUF
- Official Qwen3.5-9B: https://huggingface.co/Qwen/Qwen3.5-9B
- Qwen3.8-Flash-Next: https://huggingface.co/Qwen/Qwen3.8-Flash-Next
- DeepSeek-V4.1-Flash: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
- llama.cpp: https://github.com/ggml-org/llama.cpp

## Revisit trigger

Re-open the model shortlist only if the primary/control pair fails qualification or a new sub-28-GB Q5/Q6 model arrives with stock llama.cpp/Metal support and compelling evidence for sustained agentic utility workloads.