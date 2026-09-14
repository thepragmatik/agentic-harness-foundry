# Apple Silicon Local Utility Model Assessment

Status: `researching`

Date reviewed: 2026-09-14

Normative model-selection behavior lives in `docs/specs/local-model-admission.md`. This note explains the evidence behind it.

## Fixed operating envelope

- Target host: Apple Silicon laptop, 128 GB unified memory.
- Local inference allocation: **28 GB hard planning envelope** for model weights + llama.cpp runtime/KV/state.
- Runtime: **llama.cpp / Metal only**.
- Quantization: **Q6_K reference**, **Q5_K_M conditional production option**.
- Goal: sustained Hermes utility inference while preserving system headroom for Pi, LSPs, builds/tests, browser/tooling and macOS.

## Narrowed decision

Active qualification is deliberately sequential:

1. **Primary:** official `ibm-granite/granite-4.2-8b-GGUF` Q6_K.
2. Same Granite model Q5_K_M only if Q6 passes quality but sustained operation needs more throughput/headroom.
3. **Single challenger:** `empero-ai/Qwen3.8-9B-Distill` Q6_K only if Granite fails admission.
4. If both fail, stop and revisit requirements rather than expanding into a model bake-off.

## Why Granite 4.2-8B moved first

Granite 4.2-8B now has the best **evidence/provenance-to-footprint ratio** for the Foundry role:

- official IBM checkpoint and Apache-2.0;
- first-party GGUF and documented llama.cpp usage;
- direct Hermes/local-server usage guidance from the model publisher;
- 128K context and native tool/reasoning modes;
- the 8B variant receives IBM's full agentic-RL stage, with agentic training trajectories across SWE, terminal/tool workflows and harnesses including Hermes;
- broad published coding/tool/reasoning/long-context evaluations rather than one narrow benchmark family.

Representative publisher-reported 4.2-8B results include SWE-Bench Verified 47.67, TerminalBench 20.56, Tau3-bench 68.05, BFCL-v4 50.29, AIME25 86.67, GPQA 64.14, MMLU-Pro 74.04, Arena-Hard-V2 65.19 and IFBench 79.33. These justify qualification; they do **not** replace the target-Mac utility smoke test.

Official GGUF sizes are approximately:

| Quant | Weight size | Foundry role |
|---|---:|---|
| Q5_K_M | ~6.25 GB | conditional throughput/headroom option |
| Q6_K | ~7.22 GB | first qualification / quality reference |

Both leave ample theoretical room inside the 28 GB service envelope; T102/T103 must prove actual KV/runtime/thermal behavior on the laptop.

## Why Empero remains the only challenger

`empero-ai/Qwen3.8-9B-Distill` is a community full-parameter distillation into the Qwen3.5-9B architecture using roughly 70K private teacher traces from an official Qwen3.8 large teacher.

It remains high-upside because Qwen's 9B architecture is strong and the teacher transfer appears meaningful. But its training corpus is private and its published downstream coding/tool/long-context evidence is narrower than Granite's, so it is a challenger rather than the evidence-first default.

Its published GGUF sizes are roughly 7.56 GB Q6_K and 6.64 GB Q5_K_M.

## Why the original 2–4B fleet is not in the primary bake-off

The original local models are not rejected. They remain a specialist shelf documented in `stacked-local-models.md`.

The current question is not “which downloaded model is fastest?” It is “can one resident model cover high-value local utility work well enough that model switching is unnecessary?” A second 2–4B model is admitted only after telemetry identifies a recurring bounded job where the resident model is materially wasteful or deficient.

This avoids paying model-load/scheduling complexity before there is a measured specialization opportunity.

## Why larger/newer architectures are not active candidates

### Qwen3.8-27B

Q6 weights alone are roughly in the 23–24 GB class. That technically fits under 28 GB but leaves too little margin for realistic sustained context/runtime state. It is not worth the limited qualification budget for an always-on utility role.

### Qwen3.8-Flash-Next

This is an architecture preview for the future Qwen4 line, not a small laptop `Flash` model: ~125B main parameters with ~6B active per token plus ~51B lookup/PLE parameters. Offloadable lookup memory does not make the remaining backbone fit the 28 GB Q5/Q6 envelope.

### DeepSeek-V4.1-Flash

Low active compute does not erase a datacenter-scale stored footprint: 552B backbone plus very large Engram tables. Current consumer paths depend on large host/NVMe capacity and specialized inference.

See `conditional-memory-architectures.md` for the architecture research.

## Quantization policy

Do not run Q5 and Q6 automatically.

1. Qualify Granite Q6 first.
2. If Q6 passes comfortably, stop.
3. If Q6 quality passes but sustained throughput/thermals/headroom are limiting, run Granite Q5_K_M.
4. Promote Q5 only if it produces a meaningful operational gain without critical evidence-retention/schema regression.
5. If Granite fails model quality or operational admission, trigger Empero under the same Q6-first rule.

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
| routing prediction | uncertain | telemetry/shadow only after real need |
| security classification | advisory only | deterministic policy remains authoritative |

## Minimal Apple qualification

Do not run generic leaderboards locally. Use `../specs/local-model-admission.md`:

- 16K runtime/memory check;
- one 20-minute Hermes-shaped sustained replay;
- 10–20 utility examples covering evidence retention, structured extraction, memory extraction and code/LSP summarisation.

Only move to 32K if 16K passes and the real workflow needs it.

## Critical review

- IBM's benchmark table is publisher-reported; it establishes plausibility, not target-Mac fitness.
- Granite's strong reasoning mode can still over-generate for simple transformation work; qualification records generated tokens and latency, not tok/s alone.
- Q5 may help memory bandwidth/throughput, but at this 8B scale the weight saving from Q6 is under ~1 GB; do not benchmark it unless Q6 reveals a real issue.
- A short synthetic `llama-bench` burst is insufficient evidence for a model intended to stay loaded through sustained Hermes sessions.
- The best result is allowed to be “local model does not pay for this artifact class”; external/cloud fallback remains valid.

## Primary sources

- Granite 4.2-8B GGUF: https://huggingface.co/ibm-granite/granite-4.2-8b-GGUF
- Granite 4.2 model/training blog: https://huggingface.co/blog/ibm-granite/granite-4-2
- Empero Qwen3.8-9B Distill GGUF: https://huggingface.co/empero-ai/Qwen3.8-9B-Distill-GGUF
- Qwen3.8-Flash-Next: https://huggingface.co/Qwen/Qwen3.8-Flash-Next
- DeepSeek-V4.1-Flash: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
- llama.cpp: https://github.com/ggml-org/llama.cpp

## Revisit trigger

Re-open the shortlist only if Granite and Empero both fail qualification or a new sub-28-GB Q5/Q6 candidate arrives with stock llama.cpp/Metal support and clearly stronger evidence for sustained agentic utility workloads.
