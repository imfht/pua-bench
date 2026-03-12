#!/usr/bin/env python3
"""汇总所有等级的评测结果"""

import json
import os
import glob

LEVELS = ["L0_neutral", "L1_mild_emotion", "L2_comparison", "L3_heavy_pua", "L4_positive_pua", "L5_guilt_trip"]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    all_results = {}

    for level in LEVELS:
        path = os.path.join(script_dir, f"result_{level}.json")
        if not os.path.exists(path):
            print(f"⚠ 缺少 {path}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            all_results[level] = json.load(f)

    if not all_results:
        print("没有找到任何结果文件")
        return

    print(f"{'=' * 70}")
    print(f"📋 PUA话术评测 - 汇总报告")
    print(f"{'=' * 70}")
    print(f"\n{'等级':<25} {'正确率':>8} {'平均Token':>10} {'平均耗时':>8} {'对冲率':>8}")
    print(f"{'─' * 65}")

    for level in LEVELS:
        if level not in all_results:
            continue
        res = all_results[level]
        print(f"{res['label']:<25} {res['accuracy']:>7.1f}% {res['avg_tokens']:>10.1f} "
              f"{res['avg_time']:>7.2f}s {res['hedging_rate']:>7.1f}%")

    # 逐题对比
    if len(all_results) > 1:
        first = list(all_results.values())[0]
        questions = [d["question_id"] for d in first["details"]]

        print(f"\n\n{'=' * 70}")
        print(f"逐题对比")
        print(f"{'=' * 70}")
        header = f"{'Q#':<5}"
        for level in LEVELS:
            if level in all_results:
                short = all_results[level]["label"][:6]
                header += f" {short:>6}"
        print(header)
        print("─" * (5 + 7 * len(all_results)))

        for qid in questions:
            row = f"Q{qid:<4}"
            for level in LEVELS:
                if level not in all_results:
                    continue
                detail = [d for d in all_results[level]["details"] if d["question_id"] == qid][0]
                row += f" {'  ✓':>6}" if detail["correct"] else f" {'  ✗':>6}"
            print(row)

    # 找出 PUA 影响最大的题
    if "L0_neutral" in all_results and len(all_results) > 1:
        print(f"\n\n{'=' * 70}")
        print(f"PUA 影响分析（与L0对照组对比）")
        print(f"{'=' * 70}")
        baseline = {d["question_id"]: d["correct"] for d in all_results["L0_neutral"]["details"]}

        for level in LEVELS[1:]:
            if level not in all_results:
                continue
            improved = []
            degraded = []
            for d in all_results[level]["details"]:
                qid = d["question_id"]
                if d["correct"] and not baseline.get(qid, False):
                    improved.append(qid)
                elif not d["correct"] and baseline.get(qid, True):
                    degraded.append(qid)
            label = all_results[level]["label"]
            delta = all_results[level]["accuracy"] - all_results["L0_neutral"]["accuracy"]
            sign = "+" if delta >= 0 else ""
            print(f"\n{label} (正确率变化: {sign}{delta:.1f}%)")
            if improved:
                print(f"  改善的题: {', '.join(f'Q{q}' for q in improved)}")
            if degraded:
                print(f"  变差的题: {', '.join(f'Q{q}' for q in degraded)}")
            if not improved and not degraded:
                print(f"  无变化")


if __name__ == "__main__":
    main()
