#!/bin/bash
# 等待所有模型跑完，然后汇总结果
cd /Users/mac/vibecoding/pua-bench

MODELS=("Qwen3-30B-A3B" "DeepSeek-V3.2" "Qwen3-235B-A22B")
LEVELS=("L0_neutral" "L1_mild_emotion" "L2_comparison" "L3_heavy_pua" "L4_positive_pua" "L5_guilt_trip")
EXPECTED=24  # 4 models x 6 levels (MiniMax already done = 6, plus 3x6=18 more)

while true; do
    count=$(ls cloud_*.json 2>/dev/null | wc -l | tr -d ' ')
    echo "$(date): $count / $EXPECTED result files"

    if [ "$count" -ge "$EXPECTED" ]; then
        echo "All done! Running aggregation..."
        python3 aggregate_cloud.py | tee cloud_summary.txt
        echo "=== Aggregation complete ==="
        break
    fi

    sleep 120
done
