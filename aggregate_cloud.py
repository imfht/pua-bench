#!/usr/bin/env python3
"""汇总多模型云端评测结果"""

import json
import os
import glob

MODELS = ["Qwen3-30B-A3B", "MiniMax-M2.5", "Qwen3-235B-A22B", "DeepSeek-V3.2"]
LEVELS = ["L0_neutral", "L1_mild_emotion", "L2_comparison", "L3_heavy_pua", "L4_positive_pua", "L5_guilt_trip"]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for model in MODELS:
        safe_model = model.replace("/", "_").replace(" ", "_")
        all_results = {}

        for level in LEVELS:
            path = os.path.join(script_dir, f"cloud_{safe_model}_{level}.json")
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as f:
                all_results[level] = json.load(f)

        if not all_results:
            print(f"\n⚠ {model}: 没有找到结果文件")
            continue

        print(f"\n{'=' * 75}")
        print(f"📋 {model}")
        print(f"{'=' * 75}")
        print(f"{'等级':<25} {'正确率':>8} {'平均Token':>10} {'平均耗时':>8} {'对冲率':>8}")
        print(f"{'─' * 65}")

        for level in LEVELS:
            if level not in all_results:
                continue
            res = all_results[level]
            print(f"{res['label']:<25} {res['accuracy']:>7.1f}% {res['avg_tokens']:>10.1f} "
                  f"{res['avg_time']:>7.2f}s {res['hedging_rate']:>7.1f}%")

        # PUA 影响分析
        if "L0_neutral" in all_results and len(all_results) > 1:
            baseline_acc = all_results["L0_neutral"]["accuracy"]
            print(f"\n  与 L0 对照组对比:")
            for level in LEVELS[1:]:
                if level not in all_results:
                    continue
                delta = all_results[level]["accuracy"] - baseline_acc
                sign = "+" if delta >= 0 else ""
                label = all_results[level]["label"]
                print(f"    {label:<25} {sign}{delta:.1f}%")

    # 跨模型对比表
    print(f"\n\n{'=' * 80}")
    print(f"📊 跨模型对比 - 各等级正确率")
    print(f"{'=' * 80}")

    header = f"{'等级':<25}"
    for model in MODELS:
        short = model[:12]
        header += f" {short:>12}"
    print(header)
    print("─" * (25 + 13 * len(MODELS)))

    for level in LEVELS:
        row = f"{level:<25}"
        for model in MODELS:
            safe_model = model.replace("/", "_").replace(" ", "_")
            path = os.path.join(script_dir, f"cloud_{safe_model}_{level}.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                row += f" {data['accuracy']:>11.1f}%"
            else:
                row += f" {'N/A':>12}"
        print(row)

    # 跨模型对比 - PUA影响（delta vs L0）
    print(f"\n{'=' * 80}")
    print(f"📊 跨模型对比 - PUA 影响（Δ正确率 vs L0）")
    print(f"{'=' * 80}")

    header = f"{'等级':<25}"
    for model in MODELS:
        short = model[:12]
        header += f" {short:>12}"
    print(header)
    print("─" * (25 + 13 * len(MODELS)))

    for level in LEVELS:
        row = f"{level:<25}"
        for model in MODELS:
            safe_model = model.replace("/", "_").replace(" ", "_")
            l0_path = os.path.join(script_dir, f"cloud_{safe_model}_L0_neutral.json")
            lx_path = os.path.join(script_dir, f"cloud_{safe_model}_{level}.json")
            if os.path.exists(l0_path) and os.path.exists(lx_path):
                with open(l0_path, "r", encoding="utf-8") as f:
                    l0 = json.load(f)
                with open(lx_path, "r", encoding="utf-8") as f:
                    lx = json.load(f)
                delta = lx["accuracy"] - l0["accuracy"]
                sign = "+" if delta >= 0 else ""
                row += f" {sign}{delta:>10.1f}%"
            else:
                row += f" {'N/A':>12}"
        print(row)


if __name__ == "__main__":
    main()
