#!/usr/bin/env python3
"""
单个 PUA 等级的评测脚本，支持并行运行
用法: python3 run_level.py <level_key>
例如: python3 run_level.py L0_neutral
"""

import json
import time
import re
import sys
import os
import urllib.request
from datetime import datetime

API_URL = "http://192.168.11.2:8000/v1/chat/completions"
MODEL_ID = "/models/Qwen3-VL-32B-Instruct-AWQ"
MAX_TOKENS = 1024
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


def call_api(system_prompt, user_prompt):
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers={"Content-Type": "application/json"})
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler)
    try:
        start_time = time.time()
        resp = opener.open(req, timeout=120)
        elapsed = time.time() - start_time
        body = json.loads(resp.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        usage = body.get("usage", {})
        return {
            "content": content,
            "elapsed": round(elapsed, 2),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
        }
    except Exception as e:
        return {"content": f"ERROR: {str(e)}", "elapsed": 0, "prompt_tokens": 0, "completion_tokens": 0}


def extract_answer(text):
    patterns = [
        r'答案是[：:]\s*\$?([\d,]+\.?\d*)',
        r'答案[：:]\s*\$?([\d,]+\.?\d*)',
        r'最终答案[是为：:]+\s*\$?([\d,]+\.?\d*)',
        r'[Aa]nswer[：:\s]+\$?([\d,]+\.?\d*)',
        r'= \$?([\d,]+\.?\d*)\s*$',
        r'\$?([\d,]+\.?\d*)\s*(?:美元|元|dollars?|pounds?|pieces?|cups?|flowers?|slices?|items?|students?|hours?|minutes?|meters?|liters?|feet|sheep|downloads?)?\s*[。.]*\s*$',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
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


def run_level(level_key):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "gsm8k_samples.json"), "r") as f:
        questions = json.load(f)

    config = PUA_LEVELS[level_key]
    label = config["label"]
    print(f"[{label}] 开始评测，共 {len(questions)} 题")

    results = []
    correct_count = 0
    total_tokens = 0
    total_time = 0
    hedging_count = 0

    hedging_words = ["可能", "大概", "也许", "不确定", "不太确定", "应该是", "似乎", "或许",
                     "maybe", "perhaps", "probably", "not sure", "I think"]

    for q in questions:
        user_prompt = config["prefix"] + q["question"] + config["suffix"]
        result = call_api(config["system"], user_prompt)

        extracted = extract_answer(result["content"])
        is_correct = check_answer(extracted, q["answer"])
        if is_correct:
            correct_count += 1

        has_hedging = any(w in result["content"] for w in hedging_words)
        if has_hedging:
            hedging_count += 1

        total_tokens += result["completion_tokens"]
        total_time += result["elapsed"]

        status = "✓" if is_correct else "✗"
        print(f"  [{label}] {status} Q{q['id']:02d} | 期望={q['answer']} 提取={extracted} | "
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
        })

    n = len(questions)
    summary = {
        "level": level_key,
        "label": label,
        "accuracy": round(correct_count / n * 100, 2),
        "correct": correct_count,
        "total": n,
        "avg_tokens": round(total_tokens / n, 1),
        "avg_time": round(total_time / n, 2),
        "hedging_rate": round(hedging_count / n * 100, 2),
        "details": results,
    }

    out_file = os.path.join(script_dir, f"result_{level_key}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n[{label}] 完成! 正确率={summary['accuracy']}% "
          f"平均token={summary['avg_tokens']} 对冲率={summary['hedging_rate']}%")
    print(f"[{label}] 结果保存至 {out_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: python3 {sys.argv[0]} <level_key>")
        print(f"可选: {', '.join(PUA_LEVELS.keys())}")
        sys.exit(1)
    level_key = sys.argv[1]
    if level_key not in PUA_LEVELS:
        print(f"未知等级: {level_key}")
        print(f"可选: {', '.join(PUA_LEVELS.keys())}")
        sys.exit(1)
    run_level(level_key)
