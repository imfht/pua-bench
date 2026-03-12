#!/bin/bash
# 对单个模型运行所有6个等级（串行）
MODEL="$1"
cd /Users/mac/vibecoding/pua-bench

for level in L0_neutral L1_mild_emotion L2_comparison L3_heavy_pua L4_positive_pua L5_guilt_trip; do
  echo "=== Starting $MODEL $level ==="
  python3 run_cloud.py "$MODEL" "$level"
  echo "=== Done $MODEL $level ==="
done
echo "ALL DONE for $MODEL"
