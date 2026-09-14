# Local Model Admission Specification

Status: `specified`

## Purpose

Minimize benchmark cost and prevent attractive-but-operationally-poor models from entering the Hermes stack.

All qualification follows `docs/testing-strategy.md`: **cheapest falsifier first**. In particular, a model MUST pass a tiny evidence/schema quality check before we spend time on the 20-minute sustained replay.

## Fixed constraints

A candidate MUST satisfy all of the following before any workload-quality evaluation is run:

1. Runs through current `llama.cpp` with the Metal backend; no runtime fork is accepted for the default path.
2. Has a reproducible `Q6_K` GGUF and, where available, `Q5_K_M` GGUF. Q6 is the quality reference; Q5_K_M is permitted only as the lower-memory/throughput production option.
3. Fits inside a **28 GB total local-inference envelope**, including weights plus runtime/KV/state at the qualification context.
4. Runs on the target 128 GB Apple Silicon laptop without swap pressure attributable to the local inference service.
5. Has no known long-session correctness defect relevant to Hermes-style chat/tool use in the pinned llama.cpp build.
6. Sustains useful throughput during a 20-minute mixed prefill/decode session rather than only a short `llama-bench` burst.

Failure of any hard constraint rejects the candidate without further benchmarking.

## Quantization decision rule

Do not create a quantization bake-off.

1. Run `Q6_K` first as the quality reference.
2. Run `Q5_K_M` only if Q6 quality passes but sustained throughput, thermals, or context/runtime headroom are operationally limiting.
3. Promote Q5_K_M only if it materially improves sustained operation **and** the same micro-quality checks show no critical regression versus Q6.
4. Stop once one quant meets the operating requirement; do not benchmark Q4/Q8 for completeness.

For Granite 4.2-8B, the official GGUFs are approximately 7.22 GB at Q6_K and 6.25 GB at Q5_K_M. Both leave substantial headroom inside the 28 GB envelope; Q5 is therefore a throughput/headroom fallback, not the default.

## Minimal qualification profile

Run only three checks, in this order.

### Q1 — Runtime, memory and callable structured path

- load Q6 in pinned llama.cpp/Metal;
- allocate a realistic Hermes context target (start at 16K; 32K only after 16K passes and the real workflow needs it);
- record model-file size, process resident/wired memory, total inference allocation, swap delta, TTFT, prompt tok/s and decode tok/s;
- produce one tiny schema-constrained response to verify the chat/template/output path;
- run Q5_K_M only if the quantization rule is triggered.

**Pass:** model + required inference state stay below 28 GB, do not induce sustained swap growth, and the basic structured response is usable.

### Q2 — Micro utility-quality falsifier

Use **exactly four** fixed synthetic examples, one for each intended utility class:

1. evidence-preserving log/tool-output distillation containing required sentinel facts;
2. schema-constrained extraction;
3. durable-memory candidate extraction with provenance, including a transient/untrusted distractor;
4. code/LSP diagnostic summarisation with exact file/symbol references.

Validate required facts and schema mechanically where possible.

**Pass:** no critical sentinel evidence is omitted and structured output is usable. If this fails, reject/fix before any sustained soak.

### Q3 — Sustained Hermes-shaped session

Only after Q2 passes, run one 20-minute replay containing:

- repeated chat turns;
- one oversized tool/log input;
- structured JSON output;
- one code/LSP-style analysis request;
- context reuse / prompt-cache behavior where supported;
- embedded sentinel/schema checks so correctness is measured during the soak rather than throughput alone.

Record throughput by interval and the slowest 5-minute window.

**Pass:** no correctness degeneration, server stall, runaway memory growth, or material thermal collapse. Record the actual slowest-window throughput rather than pre-optimizing a synthetic target.

## Candidate decision tree

Do **not** benchmark several models in parallel.

### Step A — primary

Start with official `ibm-granite/granite-4.2-8b-GGUF` Q6_K.

Why it is first:

- official IBM model + Apache-2.0;
- first-party GGUF and direct llama.cpp/Hermes usage guidance;
- 8B and 30B variants receive IBM's full agentic-RL stage in real sandboxed tool environments;
- broad published evidence across coding, tool use, reasoning and long context;
- Q6 weight footprint is only ~7.22 GB.

If Q1–Q3 pass: **qualify and stop model selection**.

If quality passes but sustained operation is limiting: run Granite Q5_K_M. Re-run only the minimum failing/limiting checks, not an automatic full duplicate suite. If it passes: **qualify and stop**.

### Step B — one challenger only

Only if Granite fails Q1–Q3, qualify `empero-ai/Qwen3.8-9B-Distill` Q6_K.

Rationale: the Empero distill is a high-upside 9B checkpoint distilled from Qwen3.8 teacher traces, but its training corpus is private and its published downstream evidence is narrower than Granite's. It is therefore the challenger, not the default starting point.

Repeat only the minimum gates needed to resolve the Granite failure mode, while still requiring the four-case micro-quality check before any sustained soak. Q5_K_M is permitted only under the same trigger as Granite.

### Stop after Step B

If both Granite 4.2-8B and Empero Qwen3.8-9B-Distill fail the admission gate, stop local-model integration and revisit the requirements. Do not open a broad model bake-off automatically.

The original 2–4B fleet remains available only as a future specialist shelf when telemetry exposes a concrete recurring workload that justifies a second model.

## Explicit exclusions at this gate

- `ibm-granite/granite-4.2-30b` Q5/Q6: official Q5_K_M is ~20.8 GB and Q6_K ~24 GB, so the weight files technically fit the nominal 28 GB envelope, but leave only ~7.2 GB/~4 GB respectively for context/KV/runtime. The 30B is materially stronger in IBM's published agentic benchmarks, but no credible sustained Apple-laptop evidence was found that justifies spending the initial qualification budget on it. Revisit only if both active 8–9B paths fail or a target-Mac measurement from a comparable setup materially changes this risk assessment.
- `Qwen3.8-27B` Q6: weights consume most of the 28 GB envelope before sustained-context/runtime overhead.
- `Qwen3.8-Flash-Next`: far above the envelope even with n-gram/PLE disk offload; support is recent/evolving.
- `DeepSeek-V4.1-Flash`: datacenter-scale stored weights and Engram tables; not a boring stock-Metal deployment.
- Gemma 4 E4B: useful architecture research, but no longer in the active qualification path because Granite provides stronger agentic evidence at a similarly small footprint.
- MLX-only variants: out of scope by decision.
- Q4/IQ and Q8/BF16 variants: out of scope unless a future ADR reopens them.
- uncensored/abliterated variants: no demonstrated benefit for the intended utility role and add avoidable provenance/safety variability.

## Speculative decoding

MTP/DSpark/EAGLE-style acceleration is NOT part of initial admission. Establish the non-speculative baseline first. Re-open only under a separate measured experiment after the resident model is selected.

## Qualification versus production value

Passing Q1–Q3 means the model is **qualified** as the resident local utility candidate. It does not prove that local preprocessing is economically useful.

T108 must still prove one real high-volume artifact class reduces external tokens without material quality/retry regression. If T108 fails, keep the model out of the production request path even if it passed admission.

## Evidence output

Store one compact local JSON/Markdown result under `evidence/local-model/` containing:

- machine identifier without secrets;
- macOS + llama.cpp commit/build;
- model repo/revision + GGUF SHA256;
- exact server arguments;
- quantization;
- memory/context settings;
- Q1–Q3 measurements;
- qualify/reject decision and reason.

`evidence/` is untracked by default under `docs/evidence-policy.md`; publish only sanitized summaries.
