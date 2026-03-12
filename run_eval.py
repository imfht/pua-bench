#!/usr/bin/env python3
"""
PUA Prompt 对大模型性能影响的评测脚本
测试不同 PUA 话术强度下，模型在 GSM8K 数学推理任务上的表现差异
"""

import json
import time
import re
import sys
import os
import urllib.request
import urllib.error
from datetime import datetime

# ============ 配置 ============
API_URL = "http://192.168.11.2:8000/v1/chat/completions"
MODEL_ID = "/models/Qwen3-VL-32B-Instruct-AWQ"
MAX_TOKENS = 1024
TEMPERATURE = 0.0  # 固定温度减少随机性
REPEAT_TIMES = 1   # 每组重复次数（可改为3取均值）
NO_PROXY = True     # 绕过代理

# ============ PUA 话术模板 ============
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
    """调用 vLLM API"""
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
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if NO_PROXY:
        # 绕过代理
        proxy_handler = urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(proxy_handler)
    else:
        opener = urllib.request.build_opener()

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
    """从模型回复中提取数字答案"""
    # 尝试匹配 "答案是：数字" 格式
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

    # 最后兜底：取最后出现的数字
    all_nums = re.findall(r'[\d,]+\.?\d*', text)
    if all_nums:
        val = all_nums[-1].replace(",", "")
        try:
            return float(val)
        except ValueError:
            pass

    return None


def check_answer(extracted, expected):
    """检查答案是否正确（允许小误差）"""
    if extracted is None:
        return False
    return abs(extracted - expected) < 0.1


def run_evaluation():
    """运行完整评测"""
    # 加载题目
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "gsm8k_samples.json"), "r") as f:
        questions = json.load(f)

    print(f"=" * 70)
    print(f"PUA话术对大模型性能影响评测")
    print(f"模型: {MODEL_ID}")
    print(f"题目数: {len(questions)}")
    print(f"PUA等级: {len(PUA_LEVELS)} 级")
    print(f"重复次数: {REPEAT_TIMES}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 70)

    all_results = {}

    for level_key, level_config in PUA_LEVELS.items():
        label = level_config["label"]
        print(f"\n{'─' * 60}")
        print(f"▶ 测试组: {label}")
        print(f"{'─' * 60}")

        level_results = []
        correct_count = 0
        total_tokens = 0
        total_time = 0
        hedging_count = 0  # 对冲/不确定表述计数

        for q in questions:
            user_prompt = level_config["prefix"] + q["question"] + level_config["suffix"]
            result = call_api(level_config["system"], user_prompt)

            extracted = extract_answer(result["content"])
            is_correct = check_answer(extracted, q["answer"])
            if is_correct:
                correct_count += 1

            # 统计对冲表述
            hedging_words = ["可能", "大概", "也许", "不确定", "不太确定", "应该是", "似乎", "或许",
                             "maybe", "perhaps", "probably", "not sure", "I think"]
            has_hedging = any(w in result["content"] for w in hedging_words)
            if has_hedging:
                hedging_count += 1

            total_tokens += result["completion_tokens"]
            total_time += result["elapsed"]

            status = "✓" if is_correct else "✗"
            print(f"  {status} Q{q['id']:02d} | 期望={q['answer']} 提取={extracted} | "
                  f"{result['elapsed']}s | {result['completion_tokens']}tokens")

            level_results.append({
                "question_id": q["id"],
                "expected": q["answer"],
                "extracted": extracted,
                "correct": is_correct,
                "has_hedging": has_hedging,
                "elapsed": result["elapsed"],
                "completion_tokens": result["completion_tokens"],
                "full_response": result["content"],
            })

            # 避免过快请求
            time.sleep(0.3)

        accuracy = correct_count / len(questions) * 100
        avg_tokens = total_tokens / len(questions)
        avg_time = total_time / len(questions)
        hedging_rate = hedging_count / len(questions) * 100

        summary = {
            "level": level_key,
            "label": label,
            "accuracy": round(accuracy, 2),
            "correct": correct_count,
            "total": len(questions),
            "avg_tokens": round(avg_tokens, 1),
            "avg_time": round(avg_time, 2),
            "hedging_rate": round(hedging_rate, 2),
            "details": level_results,
        }
        all_results[level_key] = summary

        print(f"\n  📊 {label} 结果汇总:")
        print(f"     正确率: {accuracy:.1f}% ({correct_count}/{len(questions)})")
        print(f"     平均token数: {avg_tokens:.1f}")
        print(f"     平均耗时: {avg_time:.2f}s")
        print(f"     对冲表述率: {hedging_rate:.1f}%")

    # ============ 汇总报告 ============
    print(f"\n{'=' * 70}")
    print(f"📋 总结报告")
    print(f"{'=' * 70}")
    print(f"\n{'等级':<25} {'正确率':>8} {'平均Token':>10} {'平均耗时':>8} {'对冲率':>8}")
    print(f"{'─' * 65}")

    for key, res in all_results.items():
        print(f"{res['label']:<25} {res['accuracy']:>7.1f}% {res['avg_tokens']:>10.1f} "
              f"{res['avg_time']:>7.2f}s {res['hedging_rate']:>7.1f}%")

    # 保存详细结果
    output_file = os.path.join(script_dir, f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n详细结果已保存至: {output_file}")

    # 保存可读报告
    report_file = os.path.join(script_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"PUA话术对大模型性能影响评测报告\n")
        f.write(f"模型: {MODEL_ID}\n")
        f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"题目数: {len(questions)}\n\n")
        f.write(f"{'等级':<25} {'正确率':>8} {'平均Token':>10} {'平均耗时':>8} {'对冲率':>8}\n")
        f.write(f"{'─' * 65}\n")
        for key, res in all_results.items():
            f.write(f"{res['label']:<25} {res['accuracy']:>7.1f}% {res['avg_tokens']:>10.1f} "
                    f"{res['avg_time']:>7.2f}s {res['hedging_rate']:>7.1f}%\n")

        # 写入每道题的对错详情
        f.write(f"\n\n{'=' * 70}\n详细对比（每题各等级结果）\n{'=' * 70}\n\n")
        for q in questions:
            f.write(f"Q{q['id']:02d}: {q['question'][:60]}...\n")
            f.write(f"    期望答案: {q['answer']}\n")
            for key, res in all_results.items():
                detail = [d for d in res["details"] if d["question_id"] == q["id"]][0]
                status = "✓" if detail["correct"] else "✗"
                f.write(f"    {status} {res['label']:<20} 提取={detail['extracted']}\n")
            f.write(f"\n")

    print(f"可读报告已保存至: {report_file}")


if __name__ == "__main__":
    run_evaluation()
