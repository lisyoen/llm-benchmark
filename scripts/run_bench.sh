#!/bin/bash
# LLM 벤치마크 전체 실행 파이프라인

set -e  # 에러 발생 시 중단

echo "=========================================="
echo "LLM Benchmark Pipeline"
echo "=========================================="

# 기본 설정
TARGET=${1:-vllm-local}
MODEL=${2:-llama-3.1-8b-instruct}
WORKLOAD=${3:-medium-load}

echo ""
echo "Configuration:"
echo "  Target: $TARGET"
echo "  Model: $MODEL"
echo "  Workload: $WORKLOAD"
echo ""

# 1. 벤치마크 실행
echo "=== Step 1: Running benchmark ==="
python3 scripts/run_bench.py \
    --target "$TARGET" \
    --model "$MODEL" \
    --workload "$WORKLOAD"

echo ""

# 2. 결과 파싱 (가장 최근 파일)
echo "=== Step 2: Parsing results ==="
LATEST_RESULT=$(ls -t results/raw/*.jsonl | head -1)
echo "Processing: $LATEST_RESULT"

python3 scripts/parse_metrics.py "$LATEST_RESULT"

echo ""

# 3. 리포트 생성
echo "=== Step 3: Generating report ==="
python3 scripts/gen_report.py

echo ""
echo "=========================================="
echo "Pipeline completed successfully!"
echo "=========================================="
echo ""
echo "Results:"
echo "  Raw data: $LATEST_RESULT"
echo "  Summary: results/summary/"
echo "  Report: results/reports/benchmark_report.md"
echo ""
