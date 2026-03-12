#!/bin/bash
# 等待所有云端模型评测完成，然后自动汇总并推送到 GitHub
cd /Users/mac/vibecoding/pua-bench

EXPECTED=24  # 4 models x 6 levels

echo "$(date): Waiting for all $EXPECTED result files..."

while true; do
    count=$(ls cloud_*.json 2>/dev/null | wc -l | tr -d ' ')
    echo "$(date): $count / $EXPECTED result files completed"

    if [ "$count" -ge "$EXPECTED" ]; then
        echo "$(date): All evaluations complete!"

        # 汇总结果
        echo "Running aggregation..."
        python3 aggregate_cloud.py | tee cloud_summary.txt

        # Git add, commit, push
        echo "Pushing to GitHub..."
        git add cloud_*.json cloud_summary.txt
        git commit -m "Add Qwen3-30B-A3B, Qwen3-235B-A22B, DeepSeek-V3.2 results

All 5 models evaluated. Full cross-model comparison available.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
        git push

        echo "$(date): Done! All results pushed to GitHub."
        break
    fi

    sleep 120
done
