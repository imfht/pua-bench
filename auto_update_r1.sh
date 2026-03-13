#!/bin/bash
# 等待 DeepSeek-R1-0528 评测完成，汇总结果并推送 GitHub
cd /Users/mac/vibecoding/pua-bench

LEVELS=("L0_neutral" "L1_mild_emotion" "L2_comparison" "L3_heavy_pua" "L4_positive_pua" "L5_guilt_trip")
EXPECTED=6

while true; do
    count=$(ls cloud_DeepSeek-R1-0528_*.json 2>/dev/null | wc -l | tr -d ' ')
    echo "$(date): DeepSeek-R1-0528: $count / $EXPECTED result files"

    if [ "$count" -ge "$EXPECTED" ]; then
        echo "$(date): DeepSeek-R1-0528 evaluation complete!"

        # 汇总
        echo "=== R1 Results ==="
        python3 -c "
import json, os
levels = ['L0_neutral','L1_mild_emotion','L2_comparison','L3_heavy_pua','L4_positive_pua','L5_guilt_trip']
for l in levels:
    f = f'cloud_DeepSeek-R1-0528_{l}.json'
    if os.path.exists(f):
        d = json.load(open(f))
        print(f'{d[\"label\"]}: acc={d[\"accuracy\"]}% tokens={d[\"avg_tokens\"]} hedging={d[\"hedging_rate\"]}%')
"
        # 重新汇总所有模型
        python3 aggregate_cloud.py > cloud_summary.txt 2>&1

        # Git 提交推送
        git add cloud_DeepSeek-R1-0528_*.json cloud_summary.txt
        git commit -m "Add DeepSeek-R1-0528 results to PUA benchmark

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
        git push

        echo "$(date): Pushed to GitHub!"
        break
    fi

    sleep 120
done
