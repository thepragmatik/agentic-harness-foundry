# Stacked Local Models in an Agentic Harness

Status: `researching`

Date reviewed: 2026-09-14

## Decision summary

Do **not** run a committee of local models by default. Current evidence supports multi-model systems when models have distinct roles or when a reliable quality/acceptance signal controls escalation. Heterogeneous answer ensembles can improve quality, but they multiply inference work and recent research shows that mixing weaker models can underperform repeated sampling from one stronger model.

For Foundry, the default architecture is:

```text
one resident utility model
        |
        +--> bounded local utility jobs
        |
        +--> deterministic verifier / schema / tests
        |
        +--> external frontier escalation when needed
```

A second local model is admitted only for a **specific specialist role** with measured end-to-end benefit. No model is loaded merely because it is already downloaded.

## What the literature says

### Cascades are credible when acceptance is credible

FrugalGPT demonstrated that cheaper models can be queried first and expensive models used only when needed. Later work on unified routing/cascading formalizes this and identifies the **quality estimator** as the critical component: cascades are valuable when the system can estimate whether the cheaper answer is good enough.

For Foundry, this favors tasks with machine-checkable acceptance: JSON/schema extraction, compiler/test results, exact provenance checks, deterministic tool constraints, and bounded compression-retention tests.

### Ensembles can help, but heterogeneous mixtures are not free quality

LLM-Blender and Mixture-of-Agents show gains from combining outputs from multiple models. However, these methods deliberately spend multiple inference calls and usually add ranking/fusion passes.

A 2025 reassessment of Mixture-of-Agents found that repeated sampling from one high-quality model (`Self-MoA`) often outperformed mixtures of different models. The lesson for a laptop harness is important: **diversity only helps when added models contribute sufficiently high-quality complementary outputs**.

### Agentic routing increasingly belongs at the harness step, not only at session start

Recent harness-native routing research treats model choice as a per-step decision using task state, observations, verification and execution phase. This is strategically relevant, but it does not imply that several local models must be resident. The same approach can route between one local utility model and external provider tiers.

## Re-assessment of the original local fleet

The models below were never rejected for being poor models. They were deprioritized when the project changed from broad model exploration to a narrow requirement: one model that can cover most local utility workloads reliably during sustained Hermes sessions.

| Model | Strength relevant to Foundry | Why it is not a separate resident candidate today | Possible future specialist role |
|---|---|---|---|
| `openbmb/MiniCPM5-2B` | Current on-device model; official GGUF/llama.cpp path; long-context and tool-calling positioning; Apache-2.0 | Lower likely ceiling for evidence-preserving compression/code analysis; adding it beside an already-capable 8B model creates switching complexity | Ultra-cheap extraction/classification or draft model **only if** a measured high-volume job justifies it |
| `Qwen/Qwen3.5-2B` | Same Qwen family; Apache-2.0; modern compact architecture | A separate 2B service must beat the resident model on end-to-end latency/energy enough to justify switching | Fast narrow schema/extraction path if production telemetry exposes the need |
| `LiquidAI/LFM2.5-2.6B` | Explicitly designed for on-device/agentic workloads; hybrid conv+GQA architecture can be efficient | Custom `lfm1.0` license and another architecture/runtime path; no current measured gap justifies it | Efficiency specialist if real telemetry proves the resident model is wasteful on a bounded job |
| `HuggingFaceTB/SmolLM3-3B` | Fully open Apache-2.0, compact, GGUF ecosystem, reasoning/tool-use positioning | Older generation and no obvious unique job versus newer candidates | Simple extraction/summarization only if startup/throughput economics are exceptional |
| `microsoft/Phi-4-mini-instruct` | MIT license, strong compact reasoning/code pedigree | Different prompt/tool conventions and no current unique workload | Difficult compact reasoning challenger if a specific gap is observed |
| `ibm-granite/granite-4.2-8b` | Official IBM model; Apache-2.0; native tool calling; low/full thinking modes; full agentic RL; broad code/tool/long-context evals; first-party GGUF/Hermes guidance | **No longer treated as a specialist shelf model: it is the primary resident qualification candidate** | Resident utility model; a second tiny model is considered only later if telemetry proves value |

## Why Granite 4.2-8B replaces the 3B idea

IBM's 8B receives the additional agentic-RL stage that the 3B does not. Published results include stronger coding, general-agent, reasoning and long-context performance while the Q6 GGUF remains only about 7.2–7.5 GB. Under a 28 GB service envelope there is little reason to prefer the 3B merely to save a few gigabytes if the 8B is intended to be the main utility model.

The 3B remains interesting only in a future scenario where telemetry proves that a very cheap second model provides meaningful end-to-end savings. Until that gap exists, it adds orchestration without enough upside.

## If we ever stack models, prefer these patterns

### Pattern A — local utility -> deterministic verify -> cloud escalation

**Recommended.** One local model attempts bounded work. A schema, tests, provenance check, compiler, LSP diagnostic or other objective mechanism accepts/rejects it. Failure escalates externally.

### Pattern B — tiny specialist -> resident utility model -> cloud

**Conditionally recommended.** A 2–3B model handles one very frequent cheap task, the resident 8B handles harder local utility tasks, and cloud remains the final escalation path. Promote only if the specialist reduces end-to-end latency/energy or materially frees the resident service.

### Pattern C — several local models vote/fuse every answer

**Not recommended.** It multiplies prompt prefill/decode work, adds orchestration and memory pressure, and has no obvious cost advantage for this laptop deployment.

### Pattern D — different models per agent role

**Not initially recommended.** Planner/model-A + executor/model-B + verifier/model-C compounds per-step error and context transfer. Prefer deterministic tools/verifiers for execution and validation; split model roles only after telemetry identifies a stable specialization.

## The one-specialist rule

A second local model may enter the production stack only when all are true:

1. A recurring workload class is already measured in real Hermes telemetry.
2. The primary resident model is demonstrably wasteful or deficient on that workload.
3. The proposed specialist can be evaluated with objective or compact acceptance tests.
4. Model load/switching cost and extra memory are included in the comparison.
5. The specialist materially improves **end-to-end accepted-task latency, energy, or external-token savings**.
6. The architecture remains operable if the specialist is disabled.

Until then, the original small models remain a **candidate shelf**, not an active model pool.

## References

- FrugalGPT: https://arxiv.org/abs/2305.05176
- Unified Routing and Cascading (ICML 2025): https://proceedings.mlr.press/v267/dekoninck25a.html
- LLM-Blender: https://aclanthology.org/2023.acl-long.792/
- Mixture-of-Agents: https://arxiv.org/abs/2406.04692
- Rethinking Mixture-of-Agents / Self-MoA: https://arxiv.org/abs/2502.00674
- Agentic Routing: https://arxiv.org/abs/2607.11399
- MiniCPM5-2B: https://huggingface.co/openbmb/MiniCPM5-2B
- Qwen3.5-2B: https://huggingface.co/Qwen/Qwen3.5-2B
- LFM2.5-2.6B: https://huggingface.co/LiquidAI/LFM2.5-2.6B
- SmolLM3-3B: https://huggingface.co/HuggingFaceTB/SmolLM3-3B
- Phi-4-mini-instruct: https://huggingface.co/microsoft/Phi-4-mini-instruct
- Granite-4.2-8B: https://huggingface.co/ibm-granite/granite-4.2-8b
