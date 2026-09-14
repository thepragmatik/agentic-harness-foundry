# Conditional-Memory Architectures for Local Harness Inference

Status: `researching`

Date reviewed: 2026-09-14

Normative local-model admission lives in `docs/specs/local-model-admission.md`. This note tracks architecture ideas that may matter later.

## Decision summary

Conditional-memory / lookup-heavy architectures are strategically important because they can increase model capacity without proportionally increasing matrix compute. The current flagship n-gram systems (`Qwen3.8-Flash-Next`, `DeepSeek-V4.1-Flash`) remain far outside this project's 28 GB llama.cpp envelope.

Google Gemma 4 E2B/E4B is a practical example of lookup-augmented capacity via Per-Layer Embeddings (PLE), but **Gemma is no longer in the active Foundry qualification path**. Granite 4.2-8B currently provides stronger agentic evidence at a similarly small footprint, so adding Gemma would widen the benchmark surface without a measured gap.

Current posture:

- qualify Granite 4.2-8B first;
- Empero Qwen3.8-9B-Distill is the single challenger only if Granite fails;
- keep Gemma 4 E4B, Engram, X-GRAM, Memory Grafting and related work as architecture/watchlist evidence;
- do not benchmark Qwen3.8-Flash-Next or DeepSeek-V4.1-Flash locally under current constraints.

## Why this architecture matters

Classic Transformer/MoE capacity requires repeated matrix computation. Conditional-memory designs add another capacity axis: lookup tables addressed by token/local-context features. Only a small part of stored lookup capacity is read per token, so parameter capacity can grow without proportionally growing neural FLOPs.

DeepSeek's Engram paper formalizes a trade-off between conditional computation and static memory. X-GRAM and Memory Grafting explore more parameter-efficient or cheaper-to-construct lookup memory.

The key caveat for laptops is that **compute efficiency is not the same as resident-memory efficiency**. Lookup tables still occupy RAM/storage and still consume memory bandwidth.

## Qwen3.8-Flash-Next

`Qwen/Qwen3.8-Flash-Next`, released 2026-08-26, is an open-weight experimental preview of architecture intended for Qwen4. It is not a small laptop `Flash` model.

Published structure:

- ~125B main-model parameters;
- ~6B activated per token;
- additional ~51B n-gram embedding parameters;
- additional MTP component;
- Gated DeltaNet + Qwen Sparse Attention;
- n-gram lookup memory designed to be offloadable.

Offloading the n-gram table does not make the remaining backbone fit the 28 GB Q5/Q6 service envelope, and llama.cpp support is still relatively new/architecture-specific.

**Decision:** architecture watchlist only.

## DeepSeek-V4.1-Flash

`deepseek-ai/DeepSeek-V4.1-Flash`, released 2026-09-10, combines a 552B backbone, low active compute (roughly 8B input / 16B output), very large Engram conditional-memory tables, compressed KV architecture and DSpark speculative generation.

The efficiency innovation is real, but stored weights/memory remain datacenter scale. Current consumer experimentation relies on very large host memory/NVMe and specialized inference paths.

**Decision:** architecture research only; not a local candidate.

## Gemma 4 E4B: practical PLE evidence, not an active candidate

Google's `gemma-4-E4B-it` demonstrates a smaller related idea:

- ~8B total parameters including embeddings;
- ~4.5B effective compute;
- 42 layers;
- 128K context;
- Per-Layer Embeddings (PLE);
- coding/function-calling support;
- stock llama.cpp implementation and GGUF ecosystem.

This is not DeepSeek Engram or Qwen's contextual n-gram table. It is closer to per-layer token lookup capacity.

Gemma remains important evidence that lookup-heavy designs can be practical on laptops. But its public agent/coding results are not strong enough relative to Granite 4.2-8B to justify another active qualification arm before telemetry exposes a concrete efficiency problem.

**Decision:** watchlist, not benchmark.

## Does n-gram/lookup memory reduce RAM requirements?

Not automatically.

For Foundry, the admission equation remains:

```text
resident model/lookup weights
+ KV / recurrent / attention state
+ llama.cpp runtime overhead
<= 28 GB
```

A design with low active FLOPs can still be a poor laptop choice if total stored capacity or memory traffic is high.

## Smaller research directions

At this review date:

- DeepSeek publishes an Engram demonstration implementation, but not a mature small production GGUF family.
- Qwen3.8-Flash-Next has a tiny architectural test fixture; it is for development/testing, not capability use.
- `Memory Grafting` reports promising 0.92B and 2.8B experiments using offline conditional memory, but remains research-stage.
- `X-GRAM` reports gains at sub-2B scales with more memory-efficient lookup, also research-stage.
- `Lngram` explores latent-space conditional memory; likewise not a boring stock-llama.cpp production option.
- Gemma 4 is the clearest current proof that lookup-augmented capacity can ship in a practical small model, but it does not currently beat the Foundry's evidence-first Granite choice.

## Related optimization: speculative decoding

MTP/DSpark/EAGLE-style mechanisms predict multiple future tokens and verify them; they are orthogonal to lookup memory.

Do not assume they help Apple Silicon. Public llama.cpp Metal evidence has shown cases where draft overhead outweighs acceptance gains. The Foundry baseline remains **non-speculative llama.cpp**; reopen speculative decoding only after the resident model is selected and only with target-Mac evidence.

## What to borrow now

1. Separate cheap lookup/retrieval capacity from expensive generative reasoning.
2. Keep large raw artifacts outside the prompt and retrieve only needed evidence.
3. Make lookup/provenance deterministic where possible.
4. Prefer sparse demand-driven retrieval over repeated large memory injection.
5. Treat lower active-parameter count as a throughput hypothesis, not proof.

These principles reinforce the Foundry's context-packet, LCM/Mnemosyne and deterministic retrieval design without requiring an Engram model.

## Re-open triggers

A conditional-memory candidate enters qualification only if all are true:

- the current admitted model exposes a measured recurring deficiency;
- credible capability evidence exists for our utility/tool/code workloads;
- stock upstream llama.cpp + Metal support exists;
- Q5_K_M or Q6_K artifact exists;
- total service footprint <= 28 GB at qualification context;
- credible sustained Apple-Silicon evidence or enough architectural upside to justify one short qualification;
- no runtime fork or fragile disk-streaming patch is required for basic correctness.

## Primary sources

- Qwen official Flash-Next announcement: https://qwen.ai/blog?id=qwen3.8-flash-next
- Qwen3.8-Flash-Next: https://huggingface.co/Qwen/Qwen3.8-Flash-Next
- DeepSeek V4.1 Flash: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
- DeepSeek Engram: https://arxiv.org/abs/2601.07372 and https://github.com/deepseek-ai/Engram
- Google Gemma 4 model card: https://ai.google.dev/gemma/docs/core/model_card_4
- Gemma 4 E4B: https://huggingface.co/google/gemma-4-E4B-it
- X-GRAM: https://arxiv.org/abs/2604.21724
- Memory Grafting: https://arxiv.org/abs/2605.20948
