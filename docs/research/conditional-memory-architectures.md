# Conditional-Memory Architectures for Local Harness Inference

Status: `researching`

Date reviewed: 2026-09-14

## Decision summary

Conditional-memory / lookup-heavy architectures are strategically important for local agent stacks because they can increase model capacity without proportionally increasing matrix compute. The current **flagship n-gram systems** (`Qwen3.8-Flash-Next`, `DeepSeek-V4.1-Flash`) remain far outside this project's 28 GB llama.cpp envelope, but the broader lookup-memory idea **is already represented in a practical laptop model family: Google Gemma 4 E2B/E4B uses Per-Layer Embeddings (PLE)**.

This changes the watchlist:

- Do not benchmark Qwen3.8-Flash-Next or DeepSeek-V4.1-Flash locally under current constraints.
- Keep **Gemma 4 E4B** as a conditional efficiency challenger if the primary Qwen distill fails the sustained-operation gate.
- Track research such as Engram, X-GRAM and Memory Grafting for future smaller production checkpoints.

## Why this architecture matters

Classic Transformer/MoE capacity requires repeated matrix computation. Conditional-memory designs add another capacity axis: lookup tables addressed by token/local-context features. Only a small part of the stored lookup capacity is read per token, so parameter capacity can grow without proportionally growing neural FLOPs.

DeepSeek's Engram paper formalizes this as a trade-off between conditional computation and static memory. It reports gains for knowledge, reasoning, code/math and long-context retrieval under matched parameter/FLOP comparisons. X-GRAM and Memory Grafting are subsequent research directions aimed at making lookup memory more parameter-efficient or cheaper to construct.

The important caveat is that **compute efficiency is not the same as resident-memory efficiency**. The lookup table still occupies RAM/storage somewhere.

## Qwen3.8-Flash-Next

`Qwen/Qwen3.8-Flash-Next`, released 2026-08-26, is an open-weight experimental preview of the architecture intended for Qwen4. It is not a small laptop `Flash` model.

Published structure:

- ~125B main-model parameters;
- ~6B activated per token;
- additional ~51B n-gram embedding parameters;
- additional MTP component;
- Gated DeltaNet + Qwen Sparse Attention;
- n-gram lookup memory designed to be offloadable.

The production Qwen Cloud model `Qwen3.8-Flash` is based on this architecture and adds production features. `Flash-Next` is the open architecture preview relevant to local experimentation.

### Why it fails our admission gate

The n-gram table can be offloaded or streamed, which reduces expensive accelerator residency for that component. However, the remaining backbone is still far beyond the project's 28 GB Q5/Q6 envelope. Community llama.cpp experiments involve very large GGUFs and architecture-specific PLE loading/streaming optimizations.

Current llama.cpp support is also recent and still exposes architecture-specific bugs and performance work, including slot/checkpoint behavior and direct-read PLE paths. That is not the stability profile wanted for an always-on Hermes utility service.

**Decision:** architecture watchlist only; no local qualification.

## DeepSeek-V4.1-Flash

`deepseek-ai/DeepSeek-V4.1-Flash`, released 2026-09-10, is the smallest member of DeepSeek's new V4.1 architecture family but is still a datacenter-scale model.

Published structure includes:

- 552B backbone parameters;
- ~8B active parameters during input/prefill and ~16B during output/decode;
- very large Engram conditional-memory tables (two tables with hundreds of millions of entries each);
- compressed KV architecture;
- DSpark speculative generation.

The central efficiency innovation is real: active compute and KV/cache cost are much lower than the stored parameter count suggests. But stored weights and Engram memory remain enormous. Current consumer experimentation depends on very large host memory/NVMe and specialized inference paths.

**Decision:** reject for local deployment; retain as architecture research and an external-provider efficiency signal.

## Gemma 4 E4B: the practical PLE case

Google's official Gemma 4 family includes `gemma-4-E4B-it`, a model explicitly designed for on-device/laptop deployment. Google reports:

- 4.5B **effective** parameters;
- ~8B total parameters including embeddings;
- 42 layers;
- 128K context;
- Per-Layer Embeddings (PLE), where each decoder layer gets a small token embedding lookup;
- native coding/function-calling support.

This is not the same as DeepSeek Engram or Qwen's hashed n-gram table: Gemma's PLE is closer to a **1-gram per-layer lookup capacity**. Architecturally, however, it demonstrates the same useful principle: add cheap lookup capacity that does not require equivalent dense matrix compute.

### Why it is relevant to us

- official Google checkpoint, Apache-2.0;
- stock llama.cpp has a dedicated Gemma 4 implementation including per-layer token embeddings;
- official/third-party GGUF ecosystem exists;
- Q5_K_M/Q6_K artifacts are roughly in the ~6 GB class, easily inside the 28 GB envelope;
- Google positions E4B for edge/laptop deployment and reports 52.0 on LiveCodeBench v6 and 42.2 on Tau2.

### Why it is not promoted immediately

The public agent/coding results are materially below the stronger published Qwen3.5-9B results, and llama.cpp/Metal has had Gemma-4-specific performance regressions/issues. PLE can also be memory-bandwidth sensitive, so lower effective parameter count does **not** guarantee higher Apple-Silicon token/s.

**Decision:** do not create a three-way benchmark. Keep Gemma 4 E4B as a **triggered challenger** only if the primary 9B Qwen distill fails due to sustained throughput/latency/headroom rather than quality.

## Does n-gram/lookup memory reduce RAM requirements?

Not automatically.

It primarily reduces **compute required to access model capacity**. Some architectures can additionally place lookup tables in host memory/NVMe. But total stored capacity remains real.

For this project, the admission equation is:

```text
resident model/lookup weights
+ KV / recurrent / attention state
+ llama.cpp runtime overhead
<= 28 GB
```

The useful local model is one where both the stored footprint and sustained memory bandwidth fit the laptop envelope.

## Smaller research directions

At this review date:

- DeepSeek publishes an Engram demonstration implementation, but not a mature small production GGUF family.
- Qwen3.8-Flash-Next has a ~0.2B architectural test fixture preserving PLE/QSA/GDN; it is explicitly for development/testing, not capability use.
- `Memory Grafting` reports promising 0.92B and 2.8B experiments using offline conditional memory, but is research-stage.
- `X-GRAM` reports gains at 0.73B and 1.15B scales with more memory-efficient token lookup, but is also research-stage.
- `Lngram` explores conditional memory indexed in latent space; likewise not yet a boring llama.cpp production option.
- Gemma 4 E2B/E4B are currently the strongest evidence that lookup-augmented capacity can ship in a practical small open model, although their PLE mechanism is simpler than n-gram Engram.

## Related optimization: speculative decoding

MTP/DSpark/EAGLE-style mechanisms optimize decoding by predicting multiple future tokens and verifying them. They are orthogonal to lookup memory.

Do not assume they help Apple Silicon. A public llama.cpp Metal report on Qwen3.5-9B found MTP speculative decoding slower than the non-MTP path across tested settings because draft-evaluation overhead exceeded the acceptance gain.

Therefore the Foundry baseline remains **non-speculative llama.cpp**. Re-open speculative decoding only after the resident model is selected and only with a target-Mac measurement.

## What to borrow from these architectures now

1. Separate cheap lookup/retrieval capacity from expensive generative reasoning.
2. Keep large raw artifacts outside the prompt and retrieve only needed evidence.
3. Make lookup/provenance deterministic where possible.
4. Prefer sparse demand-driven retrieval over repeated large memory injection.
5. Treat lower active-parameter count as a **throughput hypothesis**, not proof; memory bandwidth and runtime kernels still determine Apple-Silicon performance.

These principles support the Foundry's LCM/Mnemosyne/context-packet design even without an Engram model.

## Re-open triggers for new conditional-memory models

A new candidate enters qualification only if it has:

- credible capability evidence for our utility/tool/code workloads;
- stock upstream llama.cpp + Metal support;
- Q5_K_M or Q6_K artifact;
- total service footprint <= 28 GB at the qualification context;
- credible sustained Apple-Silicon evidence or a sufficiently compelling architecture to justify one short local qualification;
- no required runtime fork or fragile disk-streaming patch for basic correctness.

## Primary sources

- Qwen official Flash-Next announcement: https://qwen.ai/blog?id=qwen3.8-flash-next
- Qwen3.8-Flash-Next: https://huggingface.co/Qwen/Qwen3.8-Flash-Next
- DeepSeek V4.1 Flash: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
- DeepSeek Engram: https://arxiv.org/abs/2601.07372 and https://github.com/deepseek-ai/Engram
- Google Gemma 4 model card: https://ai.google.dev/gemma/docs/core/model_card_4
- Gemma 4 E4B: https://huggingface.co/google/gemma-4-E4B-it
- llama.cpp Gemma 4 implementation: https://github.com/ggml-org/llama.cpp/blob/master/src/models/gemma4.cpp
- X-GRAM: https://arxiv.org/abs/2604.21724
- Memory Grafting: https://arxiv.org/abs/2605.20948
