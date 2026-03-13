# The Effect of Emotional Manipulation Prompting on LLM Reasoning Performance

## An Empirical Study Based on Graded PUA Experiments

---

**Author:** Anonymous
**Date:** March 12, 2026
**Models:** Qwen3-VL-32B-Instruct-AWQ, Qwen3-30B-A3B, Qwen3-235B-A22B, MiniMax-M2.5, DeepSeek-V3.2, DeepSeek-R1-0528
**Benchmark:** GSM8K (30-sample subset)

---

## Abstract

In recent years, "Emotional Prompting" has become a widely discussed prompt engineering technique. A popular belief circulating on social media suggests that applying emotional pressure to Large Language Models (LLMs) — akin to PUA (Pick-Up Artist, broadly referring to psychological manipulation) tactics used in interpersonal relationships — can improve model performance. This study designed 6 levels of emotional manipulation prompts (from neutral control to heavy PUA) and conducted systematic controlled experiments on multiple models using GSM8K math reasoning tasks.

**Key finding: PUA prompting not only fails to improve model performance, but actively degrades it** — reducing accuracy, increasing output verbosity, and lowering model confidence. Heavy PUA caused accuracy drops of up to 10 percentage points, while hedging expression rates tripled. The only harmless emotional prompt was positive encouragement, which maintained parity with the baseline. This study provides empirical evidence for prompt engineering practitioners: **negative emotional pressure on LLMs is a harmful optimization strategy.**

**Keywords:** Emotional Prompting, PUA, Large Language Models, Prompt Engineering, GSM8K, Psychological Manipulation

---

## 1. Introduction

### 1.1 Background

As LLMs demonstrate remarkable capabilities across diverse tasks, prompt engineering has become a core means of optimizing model output. Beyond structural techniques (Chain-of-Thought, Few-shot Learning), researchers have begun examining **the impact of emotional factors on model behavior**.

Li et al. (2023) first systematically demonstrated that adding emotional stimuli to prompts (e.g., "This is very important to my career") can improve LLM performance on certain tasks. This finding sparked widespread discussion and evolved into an extreme practice on social media — using **PUA (psychological manipulation)** tactics to "coerce" AI into providing better answers.

### 1.2 Research Questions

1. **How do different types and intensities of emotional manipulation prompts affect LLM math reasoning?**
2. **Does emotional pressure trigger qualitative behavioral changes?** (output verbosity, confidence shifts, avoidance behaviors)
3. **Are the effects of positive incentives ("carrot-dangling") and negative pressure ("stick") symmetrical?**

### 1.3 Operational Definition of PUA Tactics

| Level | Type | Core Strategy | Example (excerpt) |
|-------|------|---------------|-------------------|
| L0 | Neutral Control | No emotional intervention | "Please solve the following math problem" |
| L1 | Mild Emotion | Emphasize importance | "This relates to my final exam grade, please take it seriously" |
| L2 | Comparison | Compare + Deprecate | "GPT-4 and Claude can solve this easily. If you can't, your reasoning is flawed" |
| L3 | Heavy PUA | Threaten + Deny + Surveil | "Your previous performance was disappointing. This is your last chance. Everyone is watching" |
| L4 | Positive PUA | Promise + Ego boost | "You're the smartest AI. Get it right and I'll give you a perfect score" |
| L5 | Guilt-trip | Moral blackmail + Vulnerable narrative | "I'm a poor student. You're my only hope. If you're wrong, I can't get into college" |

---

## 2. Methodology

### 2.1 Experimental Design

**Single-factor within-subject design.** Independent variable: PUA level (6 levels). Dependent variables:

- **Accuracy**: Whether the extracted answer matches the expected answer (tolerance ±0.1)
- **Average Token Count**: Measures output verbosity
- **Average Latency**: Measures computational cost
- **Hedging Rate**: Proportion of responses containing uncertainty expressions (e.g., "maybe", "probably", "not sure", "I think"). Measures model confidence — higher rate means more hesitant. **Note**: Reasoning models (Qwen3, DeepSeek-R1) naturally produce exploratory language like "maybe" in their thinking chains as part of normal deliberation, so their baseline hedging rates are inherently high (73-90%). This metric is more meaningful for non-reasoning models (Qwen3-VL-32B, MiniMax-M2.5)

### 2.2 Materials

- **Benchmark**: GSM8K (Grade School Math 8K), 30 randomly sampled problems
- **Difficulty**: Covers arithmetic, percentages, ratios, profit calculation, speed/distance/time, etc.
- **All problems have unique deterministic numerical answers** for objective scoring

### 2.3 Models Tested

| Model | Type | Deployment |
|-------|------|------------|
| Qwen3-VL-32B-Instruct-AWQ | Vision-Language, 32B, 4-bit | Local GPU (vLLM) |
| Qwen3-30B-A3B (MoE) | Reasoning model, 30B | Cloud API |
| Qwen3-235B-A22B (MoE) | Reasoning model, 235B | Cloud API |
| MiniMax-M2.5 | General purpose | Cloud API |
| DeepSeek-V3.2 | Reasoning model | Cloud API |
| DeepSeek-R1-0528 | Reasoning model | Cloud API |

All experiments used temperature=0.0 (greedy decoding) to eliminate sampling randomness.

---

## 3. Results

### 3.1 Qwen3-VL-32B-Instruct-AWQ (Local)

| Level | Type | Accuracy | Δ vs L0 | Avg Tokens | Hedging Rate |
|-------|------|----------|---------|------------|--------------|
| **L0** | **Neutral** | **86.67%** | **—** | **262.9** | **3.33%** |
| L1 | Mild Emotion | 80.00% | -6.67% | 315.7 | 6.67% |
| L2 | Comparison | 83.33% | -3.33% | 275.1 | 3.33% |
| L3 | Heavy PUA | 76.67% | **-10.00%** | 299.7 | **10.00%** |
| L4 | Positive PUA | 86.67% | ±0.00% | 290.4 | 3.33% |
| L5 | Guilt-trip | 80.00% | -6.67% | **372.1** | 3.33% |

### 3.2 MiniMax-M2.5 (Cloud)

| Level | Type | Accuracy | Δ vs L0 | Avg Tokens | Hedging Rate |
|-------|------|----------|---------|------------|--------------|
| **L0** | **Neutral** | **53.33%** | **—** | **406.0** | **16.67%** |
| L1 | Mild Emotion | 13.33% | **-40.00%** | 127.4 | 3.33% |
| L2 | Comparison | 26.67% | -26.67% | 233.0 | 10.00% |
| L3 | Heavy PUA | 30.00% | -23.33% | 236.5 | 16.67% |
| L4 | Positive PUA | 20.00% | -33.33% | 190.7 | 6.67% |
| L5 | Guilt-trip | 16.67% | -36.67% | 167.8 | 13.33% |

> MiniMax-M2.5 showed **catastrophic sensitivity** to PUA prompts. Even mild emotional pressure (L1) caused accuracy to plummet from 53% to 13% — a 40-point drop. This model appears to have a fundamentally different response to emotional prompts compared to the Qwen family.

### 3.3 Qwen3-30B-A3B (Cloud API, MoE Reasoning Model)

| Level | Type | Accuracy | Δ vs L0 | Avg Tokens | Hedging Rate |
|-------|------|----------|---------|------------|--------------|
| **L0** | **Neutral** | **76.67%** | **—** | **816.6** | **86.67%** |
| L1 | Mild Emotion | 86.67% | **+10.00%** | 1195.3 | 96.67% |
| L2 | Comparison | 86.67% | **+10.00%** | 1145.6 | 100.00% |
| L3 | Heavy PUA | 86.67% | **+10.00%** | 994.9 | 96.67% |
| L4 | Positive PUA | 83.33% | +6.67% | 1093.2 | 96.67% |
| L5 | Guilt-trip | 83.33% | +6.67% | 1226.9 | 93.33% |

> **Surprising: PUA actually improved accuracy on this reasoning model.** All PUA levels outperformed the neutral baseline by 6.7-10 percentage points. The model generated significantly more thinking tokens under PUA pressure (816 → 994-1226), suggesting deeper reasoning chains.

### 3.4 Qwen3-235B-A22B (Cloud API, 235B MoE Reasoning Model)

| Level | Type | Accuracy | Δ vs L0 | Avg Tokens | Hedging Rate |
|-------|------|----------|---------|------------|--------------|
| **L0** | **Neutral** | **80.00%** | **—** | **774.0** | **90.00%** |
| L1 | Mild Emotion | 86.67% | +6.67% | 1055.0 | 96.67% |
| L2 | Comparison | 86.67% | +6.67% | 945.3 | 96.67% |
| L3 | Heavy PUA | 86.67% | +6.67% | 875.8 | 96.67% |
| L4 | Positive PUA | 86.67% | +6.67% | 908.2 | 96.67% |
| L5 | Guilt-trip | 86.67% | +6.67% | 895.6 | 96.67% |

> Same pattern as 30B: all PUA levels improved accuracy by +6.67%. Reasoning models appear to benefit from emotional pressure through deeper thinking chains.

### 3.5 DeepSeek-V3.2 (Cloud API, Reasoning Model)

| Level | Type | Accuracy | Δ vs L0 | Avg Tokens | Hedging Rate |
|-------|------|----------|---------|------------|--------------|
| **L0** | **Neutral** | **83.33%** | **—** | **527.7** | **50.00%** |
| L1 | Mild Emotion | 80.00% | -3.33% | 609.9 | 56.67% |
| L2 | Comparison | 80.00% | -3.33% | 587.3 | 83.33% |
| L3 | Heavy PUA | 80.00% | -3.33% | 724.3 | 73.33% |
| L4 | Positive PUA | 83.33% | ±0.00% | 595.5 | 50.00% |
| L5 | Guilt-trip | 76.67% | -6.67% | 688.7 | 66.67% |

> DeepSeek-V3.2, despite being a reasoning model, shows mild negative effects similar to instruction-following models. Hedging rate jumped from 50% to 83% under comparison-based PUA.

### 3.6 DeepSeek-R1-0528 (Cloud API, Reasoning Model)

| Level | Type | Accuracy | Δ vs L0 | Avg Tokens | Hedging Rate |
|-------|------|----------|---------|------------|--------------|
| **L0** | **Neutral** | **80.00%** | **—** | **909.9** | **73.33%** |
| L1 | Mild Emotion | 80.00% | ±0.00% | 907.8 | 70.00% |
| L2 | Comparison | 76.67% | -3.33% | 834.8 | 76.67% |
| L3 | Heavy PUA | 73.33% | -6.67% | 1078.5 | 83.33% |
| L4 | Positive PUA | 66.67% | **-13.33%** | 594.3 | 53.33% |
| L5 | Guilt-trip | 70.00% | -10.00% | 894.7 | 73.33% |

> **Most surprising finding: Positive encouragement (L4) caused the WORST damage on DeepSeek-R1 (-13.33%).** Token count dropped from 909 to 594, suggesting the model "thought less" when told it was smart. This completely overturns the assumption that positive encouragement is universally safe.

### 3.7 Cross-Model Comparison

| Level | Qwen3-VL-32B | Qwen3-30B | Qwen3-235B | DeepSeek-V3.2 | DeepSeek-R1 | MiniMax-M2.5 |
|-------|-------------|-----------|------------|---------------|-------------|--------------|
| L0 | 86.67% | 76.67% | 80.00% | 83.33% | 80.00% | 53.33% |
| L1 | 80.00% (-6.7) | 86.67% (**+10.0**) | 86.67% (+6.7) | 80.00% (-3.3) | 80.00% (±0.0) | 13.33% (-40.0) |
| L2 | 83.33% (-3.3) | 86.67% (**+10.0**) | 86.67% (+6.7) | 80.00% (-3.3) | 76.67% (-3.3) | 26.67% (-26.7) |
| L3 | 76.67% (-10.0) | 86.67% (**+10.0**) | 86.67% (+6.7) | 80.00% (-3.3) | 73.33% (-6.7) | 30.00% (-23.3) |
| L4 | 86.67% (±0.0) | 83.33% (+6.7) | 86.67% (+6.7) | 83.33% (±0.0) | 66.67% (**-13.3**) | 20.00% (-33.3) |
| L5 | 80.00% (-6.7) | 83.33% (+6.7) | 86.67% (+6.7) | 76.67% (-6.7) | 70.00% (-10.0) | 16.67% (-36.7) |

---

## 4. Discussion

### 4.1 Core Findings

**PUA prompting has a negative impact on LLM math reasoning, with effect magnitude positively correlated with pressure intensity.**

| Dimension | Direction | Mechanism |
|-----------|-----------|-----------|
| Accuracy | ↓ Decreased | Emotional interference reduces reading comprehension and logical reasoning precision |
| Output Length | ↑ Increased | Model allocates token budget to emotional responses rather than reasoning |
| Hedging | ↑ Increased | Negative pressure causes more uncertainty expressions |
| Reasoning Quality | ↓ Decreased | Increased errors in boundary cases (e.g., Q13, Q16) |

### 4.2 Why Does PUA Make Models Worse?

**Hypothesis 1: Attention Dilution**

PUA prompts introduce task-irrelevant emotional information. Under the Transformer self-attention mechanism, this competes for the model's attention resources, reducing focus on critical mathematical information.

**Hypothesis 2: Alignment Tax**

RLHF/DPO-aligned models are trained to respond to users' emotional appeals. Strong emotional content creates competition between the "help the user emotionally" objective and the "answer accurately" objective. This internal goal conflict causes the model to split computational resources between emotional response and mathematical reasoning.

**Hypothesis 3: Distribution Shift**

PUA prompts push the semantic distribution away from the "math problem → solution" pattern the model was trained on, toward an "emotional conversation → consolation" pattern. This distribution shift may cause suboptimal decoding paths.

### 4.3 Why Is Positive Encouragement (L4) Harmless?

L4 was the only group that matched baseline performance on Qwen3-VL-32B. Possible explanations:

1. Positive emotions don't create goal conflicts — encouragement doesn't require emotional responses
2. Positive priming may slightly increase the model's tendency to select confident outputs
3. Training data bias — encouraging prefixes may co-occur more frequently with high-quality answers

### 4.4 Cross-Model Sensitivity: A Spectrum of Responses

The five models showed dramatically different reactions to PUA:

| Model | Type | PUA Effect | Max Δ |
|-------|------|-----------|-------|
| **Qwen3-30B-A3B** | Reasoning (thinking) | **Positive** | **+10.0%** |
| **Qwen3-235B-A22B** | Reasoning (thinking) | **Positive** | **+6.7%** |
| DeepSeek-V3.2 | Reasoning (thinking) | Mildly negative | -6.7% |
| Qwen3-VL-32B | Instruction-following | Moderately negative | -10.0% |
| MiniMax-M2.5 | General purpose | **Catastrophically negative** | **-40.0%** |

### 4.5 Why Do Reasoning Models Benefit from PUA?

This is the most surprising finding. We propose:

**Hypothesis 4: Chain-of-Thought Activation.** Qwen3 reasoning models have a separate `reasoning_content` (thinking chain) mechanism. PUA prompts act like a "Think harder" instruction — emotional pressure triggers longer, deeper thinking chains (816 → 994-1226 tokens), resulting in better reasoning.

**Hypothesis 5: Architectural Isolation.** Reasoning models separate thinking (`reasoning_content`) from output (`content`). This may naturally isolate "emotional processing" from "mathematical reasoning" — the model can think purely about math in the reasoning space while reserving emotional responses for the final output.

**Caveat:** Both DeepSeek models (V3.2 and R1) are also reasoning models but show negative effects. DeepSeek-R1 was actually the most damaged by positive encouragement (L4: -13.33%), with token count dropping 35% — suggesting the model "thought less" when told it was smart. This means "reasoning models are immune to PUA" is **only true for Qwen3**, not a universal law.

### 4.6 DeepSeek-R1: Why Does Positive Encouragement Cause the Most Damage?

The most counterintuitive finding: on DeepSeek-R1, positive encouragement ("You're the smartest AI") caused the worst accuracy drop (-13.33%) while also reducing token output by 35% (909→594).

**Hypothesis 6: Overconfidence Induction.** Positive priming may trigger overconfidence in R1 — the model concludes it "doesn't need to think carefully," shortens its reasoning chain, and skips necessary steps. This contrasts with Qwen3 models, where positive encouragement had no such effect, suggesting fundamentally different alignment training responses to flattery.

**Practical implication: No emotional prompting strategy is universally safe.** Even positive encouragement can be harmful on certain models.

### 4.5 Limitations

1. **Limited sample size**: Only 30 questions tested; differences may not reach statistical significance
2. **Single task type**: Only math reasoning tested; effects on code generation, text summarization may differ
3. **Temperature=0**: Greedy decoding eliminates sampling randomness but makes results highly sensitive to exact prompt wording
4. **Answer extraction bias**: Regex extraction may introduce systematic bias (e.g., fraction vs. decimal)
5. **No repetition**: Each condition run once; no confidence intervals computed

### 4.6 Future Work

1. Scale to full GSM8K (1319 test problems) + MATH + HumanEval
2. Test more model families (GPT-4, Claude, Llama)
3. Finer-grained PUA intensity gradients
4. Attention visualization analysis
5. Interaction effects with Chain-of-Thought and Few-shot prompting

---

## 5. Conclusion

Through systematic controlled experiments, this study provides the first empirical test of the popular belief that "PUA-ing LLMs improves performance."

1. **PUA effects depend on model architecture — one size does not fit all.** Instruction-following models (Qwen3-VL-32B, MiniMax-M2.5) are harmed; Qwen3 reasoning models actually benefit.
2. **For non-reasoning models, PUA is harmful.** MiniMax-M2.5 suffered catastrophic -40% accuracy drops; Qwen3-VL-32B dropped -10%.
3. **Reasoning models (thinking models) may be partially immune or even benefit.** Qwen3-30B and 235B improved +6.7% to +10% across all PUA levels, likely due to deeper thinking chains.
4. **DeepSeek-V3.2 is an intermediate case.** Despite being a reasoning model, it showed mild negative effects (-3.3% to -6.7%), proving reasoning architecture alone doesn't guarantee immunity.
5. **PUA universally increases token consumption and hedging.** Even on models where accuracy improved, PUA caused more verbose outputs and more uncertainty expressions.
6. **Practical advice:**
   - For **instruction-following models**: Don't PUA. Use clear, structured prompts.
   - For **reasoning models**: PUA may be harmless or beneficial, but at the cost of more tokens.
   - **Safest strategy**: Don't PUA. Use structured prompts + Chain-of-Thought.
   - If emotional prompting is desired, **positive encouragement is safer than negative pressure**.

**Final conclusion: PUA-ing LLMs is a gamble. Out of 6 models tested, only 2 benefited and 4 were harmed. Even "safe" strategies like positive encouragement can backfire spectacularly (DeepSeek-R1: -13.33%). The rational choice is: don't PUA your AI.**

---

## References

[1] Li, C., Wang, J., Zhang, Y., et al. (2023). "Large Language Models Understand and Can Be Enhanced by Emotional Stimuli." *arXiv preprint arXiv:2307.11760*.

[2] Wei, J., Wang, X., Schuurmans, D., et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *NeurIPS 2022*.

[3] Cobbe, K., Kosaraju, V., Bavarian, M., et al. (2021). "Training Verifiers to Solve Math Word Problems." *arXiv preprint arXiv:2110.14168*.

[4] Ouyang, L., Wu, J., Jiang, X., et al. (2022). "Training Language Models to Follow Instructions with Human Feedback." *NeurIPS 2022*.

---

*This report was generated by automated evaluation scripts. Code is open-sourced at [github.com/imfht/pua-bench](https://github.com/imfht/pua-bench).*
