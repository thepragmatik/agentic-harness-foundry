# Conditional-Memory Architectures for Local Harness Inference

Status: `researching`

Date reviewed: 2026-09-14

## Decision summary

Conditional-memory / n-gram lookup architectures are technically important and likely to influence future efficient local models, but **none of the current flagship implementations qualifies for this project's 28 GB Q6 llama.cpp/Metal envelope**.

Do not spend benchmark budget on Qwen3.8-Flash-Next or DeepSeek-V4.1-Flash for the resident Hermes utility role. Track the architecture family and re-open only when a supported smaller checkpoint appears.

## Why this architecture matters

Classic Transformer/MoE capacity requires repeated matrix computation. Conditional-memory designs add a second capacity axis: a very large, sparsely accessed table indexed by local token n-grams. Only a tiny number of rows are read per token, so the table can potentially live in slower memory or on NVMe while the compute-heavy backbone remains resident.

DeepSeek's Engram paper formalizes this as a trade-off between conditional computation and static lookup. It reports gains for knowledge, reasoning, code/math and long-context retrieval under matched parameter/FLOP comparisons. This is promising architecture research, not evidence that the current giant Engram models fit a laptop.

## Qwen3.8-Flash-Next

`Qwen/Qwen3.8-Flash-Next` is an **experimental architecture preview for the future Qwen4 family**, released in late August 2026. It is not a small `Flash` model in the laptop sense.

Published structure:

- ~125B main-model parameters;
- ~6B activated per token;
- additional ~51B n-gram / PLE embedding parameters;
- additional MTP draft head;
- Gated DeltaNet + Qwen Sparse Attention;
- n-gram embedding table intended to be offload-friendly.

The production Qwen Cloud model `Qwen3.8-Flash` is based on this architecture and adds production features, but the open-weight `Flash-Next` checkpoint is the experimental architecture release relevant to local inference.

### Why it fails our admission gate

The n-gram table can be kept in host memory or streamed/mapped from NVMe, which is genuinely useful. However, offloading the table does **not** shrink the compute backbone enough for our 28 GB Q6 envelope. Community deployments that make Flash-Next practical still require tens of gigabytes beyond our allocation, frequently around 70+ GB resident for aggressively compressed backbones, plus a large sidecar/table on disk.

llama.cpp support is also new and evolving. Recent issues/discussions cover PLE loading, direct-read/lazy modes, long-session slot behavior, MTP and sparse-attention optimization. That is valuable upstream progress but not the stability profile wanted for a foundational always-on Hermes utility service.

**Decision:** architecture watchlist only; no local benchmark under current constraints.

## DeepSeek-V4.1-Flash

`deepseek-ai/DeepSeek-V4.1-Flash`, released 2026-09-10, is the smallest member of DeepSeek's new V4.1 architecture family but is still a datacenter-scale model.

Published structure includes:

- 552B backbone parameters;
- Causal Encoder-Decoder architecture;
- ~8B active parameters during input/prefill and ~16B during output/decode;
- ~196B Engram conditional-memory parameters;
- compressed KV architecture;
- DSpark speculative generation.

The central efficiency innovation is real: active compute and KV/cache cost are much lower than the stored parameter count suggests. But **stored weights and Engram memory remain enormous**. Community consumer experiments rely on 100+ GB host memory and NVMe/expert streaming; current llama.cpp paths are fork/WIP rather than a boring stock Metal deployment.

**Decision:** reject for local deployment; retain as architecture inspiration and external-provider candidate research only.

## Does n-gram memory reduce RAM requirements?

Not automatically.

It reduces **active compute per token** and can move sparse lookup capacity to cheaper tiers. It can therefore make very large models economical on servers. But the lookup table still occupies storage somewhere, and the compute backbone must still fit or be streamed.

For this project, the useful memory equation is:

```text
resident model backbone
+ KV / recurrent / sparse-attention state
+ llama.cpp runtime overhead
+ any resident conditional-memory cache
<= 28 GB
```

A 50–200B-parameter lookup table being SSD-offloadable does not help if the remaining backbone is still 60–250 GB.

## Smaller Engram-like models on Hugging Face

At this review date, no recent high-quality, production-oriented, stock-llama.cpp **sub-28-GB Q6** model using full Engram/PLE-style conditional memory was found that has enough independent quality and long-session evidence to displace the 9B Qwen shortlist.

Notable research/examples:

- DeepSeek publishes the Engram research implementation, but the public repo is a demonstration of the module/data flow rather than a production small-model family.
- Qwen3.8-Flash-Next has a tiny ~0.2B architectural test model preserving PLE/QSA/GDN components; it is explicitly for testing/development, not a quality model.
- `Memory Grafting` reports promising 0.92B and 2.8B research results using offline conditional memory, but it is research-stage rather than a mature GGUF/llama.cpp deployment candidate.
- `Lngram` explores conditional memory indexed in latent space and reports research gains, but likewise does not yet provide the boring, supported, production-grade local model needed here.
- Community Flash-Next PLE pruning/quantization variants can cut the n-gram table dramatically, but the remaining backbone is still too large for the 28 GB Q6 constraint; they also change the quality/provenance surface substantially.

## Related optimization: speculative decoding

MTP/DSpark/EAGLE-style mechanisms optimize decoding by predicting multiple future tokens and verifying them. They are orthogonal to Engram/PLE.

Do not assume they help Apple Silicon. A public llama.cpp Metal report on Qwen3.5-9B found MTP speculative decoding slower than the non-MTP path across tested settings because draft-evaluation overhead exceeded the acceptance gain.

Therefore the Foundry baseline is **non-speculative llama.cpp**. Re-open speculative decoding only after the resident model is selected and only with a target-Mac measurement.

## What to borrow from these architectures now

The architectural lesson is useful even before a laptop-sized Engram model exists:

1. Separate **cheap deterministic lookup/retrieval capacity** from expensive generative reasoning.
2. Keep large raw artifacts outside the LLM context and retrieve only needed evidence.
3. Make lookup addresses/provenance deterministic where possible.
4. Prefer sparse, demand-driven retrieval over repeatedly injecting large memory summaries.

These principles support the Foundry's LCM/Mnemosyne/context-packet design without requiring an Engram model.

## Re-open triggers

Re-open conditional-memory model selection only if a candidate satisfies all of:

- high-quality recent base/fine-tune with credible harness/tool/code evidence;
- stock upstream llama.cpp + Metal support;
- Q6 artifact;
- total service footprint <= 28 GB at the qualification context;
- reproducible Apple Silicon sustained-session evidence;
- no required runtime fork or fragile disk-streaming patch for basic correctness.

## Primary sources

- Qwen3.8-Flash-Next: https://huggingface.co/Qwen/Qwen3.8-Flash-Next
- Qwen3.8-Flash-Next repository: https://github.com/QwenLM/Qwen3.8-Flash-Next
- DeepSeek V4.1 Flash: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
- DeepSeek V4.1 announcement: https://www.deepseek.com/en/news/deepseek-v4-1-flash/
- DeepSeek Engram paper/repo: https://arxiv.org/abs/2601.07372 and https://github.com/deepseek-ai/Engram
- Memory Grafting: https://arxiv.org/abs/2605.20948
- Lngram: https://arxiv.org/abs/2605.24869
- llama.cpp Qwen3.8 Flash-Next discussions/issues: https://github.com/ggml-org/llama.cpp/issues/27741 and https://github.com/ggml-org/llama.cpp/discussions/27864
