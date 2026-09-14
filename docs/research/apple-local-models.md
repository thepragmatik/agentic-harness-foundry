# Apple Silicon Local Utility Model Assessment

Status: `researching`

Date reviewed: 2026-09-14

## Decision summary

There is **no official Qwen3.8-9B release** at this review date. The official Qwen3.8 repository lists Qwen3.8-27B and the very large Qwen3.8-2.4T-A95B; the 9B open model remains Qwen3.5-9B.

Current recommendation for an Apple Silicon laptop:

- **Resident utility-model champion:** `Qwen3.5-9B`, initially test MLX 5-bit and 6-bit.
- **Burst quality challenger:** `Qwen3.8-27B`, MLX 4-bit only, loaded on demand.
- **Small efficiency baseline:** `MiniCPM5-2B` from the already-downloaded fleet.

No model is promoted until local measurements on the target Mac prove memory headroom, sustained throughput, quality, and accepted-task economics.

## Why Qwen3.8-27B is not the resident default

Official Qwen3.8 currently exposes a 27B dense model as its laptop-relevant open checkpoint, not a 9B model. Qwen3.8-27B has strong vendor-reported agentic/coding results, including 73.0 on Terminal Bench 2.1 and 61.7 on SWE-bench Pro, making it attractive as a quality challenger.

However, the MLX Community 4-bit conversion is roughly **16.1 GB** of model files. The 8-bit conversion is roughly **29.5 GB**, before runtime/KV-cache/application overhead. On a laptop that must concurrently run macOS, Hermes, Pi, LSP servers, builds/tests, browser/tool processes, and the inference server, the 4-bit model can be feasible but materially constrains headroom.

Therefore Qwen3.8-27B should initially be treated as a **load-on-demand local medium tier**, not an always-resident utility service.

## Why Qwen3.5-9B remains the leading resident candidate

The MLX Community 5-bit conversion is roughly **7.07 GB**, leaving substantially more unified-memory headroom. The official Qwen3.5-9B model card reports strong instruction-following, long-context, reasoning/coding and tool-use results for its size, including IFEval 91.5, LongBench v2 55.2, LiveCodeBench v6 65.6 and BFCL-v4 66.1.

Those are vendor-reported benchmark values and MUST NOT substitute for Foundry workload evaluation, but they justify including the model as the first champion.

Qwen3.5-9B also has MLX conversions available and is supported by Apple-Silicon-oriented MLX tooling.

## Appropriate local-model jobs

Prioritize workloads that are high-volume, recoverable, and cheap to verify:

| Workload | Expected value | Required safeguard |
|---|---:|---|
| compiler/test/log distillation | very high | retain raw artifact + provenance |
| oversized tool-output compression | very high | typed context packet + raw fallback |
| LSP/repository reconnaissance summary | high | read-only + exact symbol/file references |
| candidate durable-memory extraction | high | admission policy + source provenance |
| structured extraction | high | schema validation |
| retrieval/query rewrite | medium | deterministic fallback |
| LCM summary generation | potentially high | exact-message recovery tests |
| easy local task completion | task-dependent | compiler/test/schema verifier |
| routing prediction | uncertain | shadow mode first |
| security classification | advisory only | deterministic policy remains authoritative |

## Anti-patterns

Do NOT make the utility model:

- the sole prompt-injection firewall;
- the sole secret/PII detector;
- the authorization engine for tools;
- the only copy of compressed evidence;
- a mandatory reasoning pass over every request regardless of size;
- the production router before routing regret has been measured;
- a speculative-decoding draft model for unrelated external-provider models.

## Apple Silicon benchmark protocol

Benchmark on the actual laptop, not public GPU numbers.

### Runtime arms

1. MLX/MLX-LM or MLX-VLM where the model architecture requires it.
2. llama.cpp only when it provides a clear interoperability/serving advantage and quality-equivalent quantization.

Do not benchmark multiple runtimes merely for completeness; start with MLX because Apple Silicon is the target and expand only if needed.

### Quantization arms

For Qwen3.5-9B:

- 5-bit champion;
- 6-bit quality challenger;
- 4-bit only if memory/throughput materially improves without unacceptable retention loss.

For Qwen3.8-27B:

- 4-bit only in the initial bake-off.

For MiniCPM5-2B:

- use the existing local quantization as the speed baseline, recording its exact artifact/hash.

### Context bands

Test realistic input bands rather than advertised maximum context:

- 4K
- 8K
- 16K
- 32K

Only test larger contexts after these pass memory/latency gates. Large advertised context windows are not a reason to pay their KV/prefill cost.

### Metrics

Record:

- model artifact + checksum;
- runtime + version/commit;
- quantization;
- cold load time;
- time to first token;
- prompt processing tokens/sec;
- generation tokens/sec;
- peak unified memory;
- swap occurrence;
- sustained 10–20 minute throughput and thermal degradation;
- energy impact where available;
- exact output-token count;
- schema-valid rate;
- factual retention / omission score;
- source-pointer correctness;
- external tokens avoided;
- end-to-end cost per accepted task.

### Promotion criteria

The resident utility model MUST:

1. fit with safe memory headroom while representative Hermes/Pi/LSP/build workloads are active;
2. avoid system swap in the normal operating profile;
3. maintain acceptable sustained laptop throughput rather than only burst throughput;
4. pass factual-retention/context-packet tests;
5. reduce total external-token cost enough to offset added local latency/complexity;
6. degrade safely to raw evidence or external processing when uncertain/failing.

## Critical review / uncertainties

- Qwen benchmark tables are produced by the model vendor; they establish plausibility, not Foundry fitness.
- Public throughput results from discrete GPUs, Mac Studios, or different memory bandwidths are not valid performance predictions for the target laptop.
- Qwen3.8-27B may outperform Qwen3.5-9B enough on some compression/reasoning tasks to justify burst use even if its steady-state economics are worse.
- A smaller model may beat both for structured extraction or simple summaries; therefore MiniCPM5-2B remains an important baseline.
- Quantization quality can affect subtle evidence retention more than generic benchmark scores reveal.
- Laptop thermals can invert a short-run throughput ranking during sustained agent operation.

## Sources

- Official Qwen3.8 repository: https://github.com/QwenLM/Qwen3.8
- Qwen3.8-27B model card: https://huggingface.co/Qwen/Qwen3.8-27B
- Qwen3.5-9B model card: https://huggingface.co/Qwen/Qwen3.5-9B
- MLX Qwen3.5-9B 5-bit: https://huggingface.co/mlx-community/Qwen3.5-9B-5bit
- MLX Qwen3.5-9B 6-bit: https://huggingface.co/mlx-community/Qwen3.5-9B-6bit
- MLX Qwen3.8-27B 4-bit: https://huggingface.co/mlx-community/Qwen3.8-27B-4bit

## Revisit trigger

Re-open this decision immediately if an official `Qwen3.8-9B` or similar sub-10B Qwen3.8 checkpoint is released with supported MLX/llama.cpp inference. It would become a natural direct challenger to Qwen3.5-9B.