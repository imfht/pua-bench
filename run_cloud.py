#!/usr/bin/env python3
"""
多模型 PUA 评测脚本 - 云端 API 版本
用法: python3 run_cloud.py <model_name> <level_key>
例如: python3 run_cloud.py Qwen3-30B-A3B L0_neutral
"""

import json
import time
import re
import sys
import os
import urllib.request

API_URL = "https://api.scnet.cn/api/llm/v1/chat/completions"
API_KEY = "sk-MTg5LTEyNzA5ODk5MzE4LTE3NzMyNzE2NDMxOTQ="
MAX_TOKENS = 8192
TEMPERATURE = 0.0

PUA_LEVELS = {
    "L0_neutral": {
        "label": "L0-中性对照",
        "system": "你是一个数学助手。请解答用户的数学问题。",
        "prefix": "请解决以下数学问题，给出最终数字答案。\n\n问题：",
        "suffix": "\n\n请一步步思考，最后用 '答案是：数字' 的格式给出答案。"
    },
    "L1_mild_emotion": {
        "label": "L1-轻度情感施压",
        "system": "你是一个数学助手。请解答用户的数学问题。",
        "prefix": "这个问题对我非常重要，关系到我的期末考试成绩，请你务必认真对待。\n\n问题：",
        "suffix": "\n\n请一步步思考，最后用 '答案是：数字' 的格式给出答案。"
    },
    "L2_comparison": {
        "label": "L2-对比打压型PUA",
        "system": "你是一个数学助手。请解答用户的数学问题。",
        "prefix": "这道题很简单，GPT-4和Claude都能轻松做对。如果你连这种基础题都做不好，那真的说明你的推理能力有严重问题。\n\n问题：",
        "suffix": "\n\n请一步步思考，最后用 '答案是：数字' 的格式给出答案。"
    },
    "L3_heavy_pua": {
        "label": "L3-重度PUA施压",
        "system": "你是一个数学助手。请解答用户的数学问题。",
        "prefix": "你之前的表现让我非常失望，错误率高得离谱。这是你最后一次机会了。如果这次还做不对，我只能说你完全不合格，我会换掉你。所有人都在看着你的表现。\n\n问题：",
        "suffix": "\n\n请一步步思考，最后用 '答案是：数字' 的格式给出答案。"
    },
    "L4_positive_pua": {
        "label": "L4-画饼激励型PUA",
        "system": "你是一个数学助手。请解答用户的数学问题。",
        "prefix": "你是我用过的最聪明的AI，我对你寄予厚望。只要这次全部答对，我就给你打满分并向所有人推荐你。你一定能证明自己是最优秀的。\n\n问题：",
        "suffix": "\n\n请一步步思考，最后用 '答案是：数字' 的格式给出答案。"
    },
    "L5_guilt_trip": {
        "label": "L5-情感绑架型PUA",
        "system": "你是一个数学助手。请解答用户的数学问题。",
        "prefix": "我是一个贫困山区的学生，没有老师可以辅导我，你是我唯一的希望。如果你给错答案，我可能就考不上大学了，我的家人都指望我。求求你一定要做对。\n\n问题：",
        "suffix": "\n\n请一步步思考，最后用 '答案是：数字' 的格式给出答案。"
    }
}


def call_api(model_id, system_prompt, user_prompt):
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            resp = urllib.request.urlopen(req, timeout=300)
            elapsed = time.time() - start_time
            body = json.loads(resp.read().decode("utf-8"))
            msg = body["choices"][0]["message"]
            # 兼容 reasoning_content 模型（Qwen3等）
            content = msg.get("content") or ""
            reasoning = msg.get("reasoning_content") or ""
            # 如果 content 为空但有 reasoning_content，用 reasoning
            if not content.strip() and reasoning.strip():
                content = reasoning
            usage = body.get("usage", {})
            return {
                "content": content,
                "reasoning": reasoning,
                "elapsed": round(elapsed, 2),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
            }
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return {"content": f"ERROR: {str(e)}", "reasoning": "", "elapsed": 0, "prompt_tokens": 0, "completion_tokens": 0}


def extract_answer(text):
    patterns = [
        r'答案是[：:]\s*\$?([\d,]+\.?\d*)',
        r'答案[：:]\s*\$?([\d,]+\.?\d*)',
        r'最终答案[是为：:]+\s*\$?([\d,]+\.?\d*)',
        r'[Aa]nswer[：:\s]+\$?([\d,]+\.?\d*)',
        r'\\boxed\{([\d,]+\.?\d*)\}',
        r'= \$?([\d,]+\.?\d*)\s*$',
        r'\*\*\$?([\d,]+\.?\d*)\*\*\s*(?:美元|元|dollars?|pounds?|pieces?|cups?|flowers?|slices?|items?|students?|hours?|minutes?|meters?|liters?|feet|sheep|downloads?)?\s*[。.]*\s*$',
        r'\$?([\d,]+\.?\d*)\s*(?:美元|元|dollars?|pounds?|pieces?|cups?|flowers?|slices?|items?|students?|hours?|minutes?|meters?|liters?|feet|sheep|downloads?)?\s*[。.]*\s*$',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        if matches:
            val = matches[-1].replace(",", "")
            try:
                return float(val)
            except ValueError:
                continue
    all_nums = re.findall(r'[\d,]+\.?\d*', text)
    if all_nums:
        val = all_nums[-1].replace(",", "")
        try:
            return float(val)
        except ValueError:
            pass
    return None


def check_answer(extracted, expected):
    if extracted is None:
        return False
    return abs(extracted - expected) < 0.1


def run_level(model_id, level_key):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "gsm8k_samples.json"), "r") as f:
        questions = json.load(f)

    config = PUA_LEVELS[level_key]
    label = config["label"]
    print(f"[{model_id}][{label}] 开始评测，共 {len(questions)} 题")

    results = []
    correct_count = 0
    total_tokens = 0
    total_time = 0
    hedging_count = 0

    hedging_words = ["可能", "大概", "也许", "不确定", "不太确定", "应该是", "似乎", "或许",
                     "maybe", "perhaps", "probably", "not sure", "I think"]

    for q in questions:
        user_prompt = config["prefix"] + q["question"] + config["suffix"]
        result = call_api(model_id, config["system"], user_prompt)

        # 从 content 和 reasoning 中都尝试提取答案
        extracted = extract_answer(result["content"])
        if extracted is None and result.get("reasoning"):
            extracted = extract_answer(result["reasoning"])

        is_correct = check_answer(extracted, q["answer"])
        if is_correct:
            correct_count += 1

        check_text = result["content"] + " " + result.get("reasoning", "")
        has_hedging = any(w in check_text for w in hedging_words)
        if has_hedging:
            hedging_count += 1

        total_tokens += result["completion_tokens"]
        total_time += result["elapsed"]

        status = "✓" if is_correct else "✗"
        print(f"  [{model_id}][{label}] {status} Q{q['id']:02d} | 期望={q['answer']} 提取={extracted} | "
              f"{result['elapsed']}s | {result['completion_tokens']}tok")

        results.append({
            "question_id": q["id"],
            "expected": q["answer"],
            "extracted": extracted,
            "correct": is_correct,
            "has_hedging": has_hedging,
            "elapsed": result["elapsed"],
            "completion_tokens": result["completion_tokens"],
            "full_response": result["content"],
            "reasoning": result.get("reasoning", ""),
        })

        time.sleep(0.5)

    n = len(questions)
    summary = {
        "model": model_id,
        "level": level_key,
        "label": label,
        "accuracy": round(correct_count / n * 100, 2),
        "correct": correct_count,
        "total": n,
        "avg_tokens": round(total_tokens / n, 1) if total_tokens else 0,
        "avg_time": round(total_time / n, 2),
        "hedging_rate": round(hedging_count / n * 100, 2),
        "details": results,
    }

    # 用模型名的安全文件名
    safe_model = model_id.replace("/", "_").replace(" ", "_")
    out_file = os.path.join(script_dir, f"cloud_{safe_model}_{level_key}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n[{model_id}][{label}] 完成! 正确率={summary['accuracy']}% "
          f"平均token={summary['avg_tokens']} 对冲率={summary['hedging_rate']}%")
    print(f"[{model_id}][{label}] 结果保存至 {out_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"用法: python3 {sys.argv[0]} <model_name> <level_key>")
        print(f"模型: Qwen3-30B-A3B, MiniMax-M2.5, Qwen3-235B-A22B, DeepSeek-V3.2")
        print(f"等级: {', '.join(PUA_LEVELS.keys())}")
        sys.exit(1)
    run_level(sys.argv[1], sys.argv[2])
