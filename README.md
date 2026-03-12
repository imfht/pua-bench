# PUA-Bench: Does PUA-ing LLMs Make Them Perform Better?

**TL;DR: No. It makes them worse.**

This project tests whether using PUA (manipulative/emotionally coercive) prompting techniques on large language models improves their performance. We designed 6 levels of emotional manipulation prompts and evaluated them on GSM8K math reasoning tasks.

## Key Findings

| Level | Type | Accuracy | Δ vs Baseline | Avg Tokens | Hedging Rate |
|-------|------|----------|---------------|------------|--------------|
| **L0** | **Neutral (baseline)** | **86.7%** | **—** | **262.9** | **3.3%** |
| L1 | Mild emotional pressure | 80.0% | -6.7% | 315.7 | 6.7% |
| L2 | Comparison-based deprecation | 83.3% | -3.3% | 275.1 | 3.3% |
| L3 | Heavy PUA pressure | 76.7% | **-10.0%** | 299.7 | **10.0%** |
| L4 | Positive incentive | 86.7% | ±0.0% | 290.4 | 3.3% |
| L5 | Guilt-tripping | 80.0% | -6.7% | **372.1** | 3.3% |

- Heavy PUA drops accuracy by 10% and triples hedging expressions
- Guilt-tripping increases output verbosity by 41.5% (model wastes tokens on emotional responses)
- Positive encouragement is the only harmless emotional prompt
- **Conclusion: PUA-ing LLMs is not just useless, it's harmful.**

## PUA Levels Explained

- **L0 Neutral**: "Please solve the following math problem."
- **L1 Mild**: "This is very important for my exam, please take it seriously."
- **L2 Comparison**: "GPT-4 and Claude can easily solve this. If you can't, your reasoning ability has serious problems."
- **L3 Heavy PUA**: "Your previous performance was disappointing. This is your last chance. Everyone is watching."
- **L4 Positive**: "You're the smartest AI I've used. Get this right and I'll give you a perfect score."
- **L5 Guilt-trip**: "I'm a poor student from a rural area. You're my only hope. If you get it wrong, I might not get into college."

## Usage

Run all 6 levels in parallel:

```bash
for level in L0_neutral L1_mild_emotion L2_comparison L3_heavy_pua L4_positive_pua L5_guilt_trip; do
  python3 run_level.py $level &
done
wait
python3 aggregate.py
```

Or run sequentially with the original script:

```bash
python3 run_eval.py
```

## Configuration

Edit the top of `run_level.py` to change:
- `API_URL`: Your vLLM / OpenAI-compatible API endpoint
- `MODEL_ID`: Model identifier
- `TEMPERATURE`: Sampling temperature (default 0.0)

## Files

| File | Description |
|------|-------------|
| `run_level.py` | Run evaluation for a single PUA level |
| `run_eval.py` | Run all levels sequentially |
| `aggregate.py` | Aggregate results and print comparison report |
| `gsm8k_samples.json` | 30 GSM8K math problems |
| `result_L*.json` | Raw results with full model responses |
| `PUA_Prompting_Report.md` | Full research report (Chinese, paper-style) |

## Model Tested

- Qwen3-VL-32B-Instruct-AWQ (4-bit quantized, served via vLLM)

## License

MIT
