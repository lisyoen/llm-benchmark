# LLM 벤치마크 리포트

**생성 일시:** 2025-11-10 08:11:05

---

## 1. 개요

- **총 테스트 수:** 8
- **테스트 대상:** spark-test, localhost
- **테스트 모델:** Qwen/Qwen3-Coder-30B-A3B-Instruct
- **워크로드:** low-load, custom, high-load-5min

---

## 2. 성능 지표

### 2.1 TTFT (Time To First Token)

| Target | Model | Workload | Mean (s) | Median (s) | P95 (s) | P99 (s) |
|--------|-------|----------|----------|------------|---------|----------|
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 0.091 | 0.084 | 0.156 | 0.156 |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 0.228 | 0.221 | 0.356 | 0.356 |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 282.886 | 331.608 | 509.506 | 576.726 |
| localhost | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 0.225 | 0.215 | 0.316 | 0.334 |
| N/A | N/A | N/A | nan | nan | nan | nan |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 36.490 | 37.639 | 78.249 | 82.223 |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | high-load-5min | 283.006 | 285.004 | 550.936 | 586.436 |
| localhost | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 39.697 | 39.825 | 85.044 | 87.558 |

### 2.2 총 응답 시간

| Target | Model | Workload | Mean (s) | Median (s) | P95 (s) | P99 (s) |
|--------|-------|----------|----------|------------|---------|----------|
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 5.061 | 2.972 | 14.454 | 14.454 |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 116.266 | 119.002 | 136.879 | 136.879 |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 415.052 | 455.991 | 647.182 | 696.204 |
| localhost | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 17.284 | 11.108 | 38.466 | 40.992 |
| N/A | N/A | N/A | nan | nan | nan | nan |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 53.330 | 52.211 | 101.876 | 110.753 |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | high-load-5min | 419.114 | 450.877 | 677.260 | 738.701 |
| localhost | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 57.879 | 58.108 | 109.867 | 118.652 |

### 2.3 토큰 처리량

| Target | Model | Workload | Mean (tokens/s) | Median (tokens/s) | P95 (tokens/s) |
|--------|-------|----------|-----------------|-------------------|----------------|
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 25.3 | 25.6 | 26.3 |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 6.8 | 6.7 | 7.7 |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 2.5 | 1.8 | 6.4 |
| localhost | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 8.2 | 7.6 | 12.1 |
| N/A | N/A | N/A | nan | nan | nan |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 3.2 | 2.4 | 7.7 |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | high-load-5min | 2.6 | 1.7 | 6.4 |
| localhost | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 3.2 | 2.4 | 7.7 |

### 2.4 성공률

| Target | Model | Workload | Total | Success | Failed | Success Rate |
|--------|-------|----------|-------|---------|--------|-------------|
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 12 | 12 | 0 | 100.0% |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 20 | 20 | 0 | 100.0% |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 6517 | 245 | 6272 | 3.8% |
| localhost | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 60 | 60 | 0 | 100.0% |
| N/A | N/A | N/A | 0 | 0 | 0 | 0.0% |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 196 | 196 | 0 | 100.0% |
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | high-load-5min | 4902 | 180 | 4722 | 3.7% |
| localhost | Qwen/Qwen3-Coder-30B-A3B-Instr... | custom | 196 | 196 | 0 | 100.0% |

---

## 3. 비교 분석

### 3.1 최고 TTFT 성능

- **Target:** spark-test
- **Model:** Qwen/Qwen3-Coder-30B-A3B-Instruct
- **Workload:** low-load
- **Mean TTFT:** 0.091s

### 3.2 최고 처리량

- **Target:** spark-test
- **Model:** Qwen/Qwen3-Coder-30B-A3B-Instruct
- **Workload:** low-load
- **Mean Throughput:** 25.3 tokens/s

---

## 4. 권장사항

### ⚠️ 낮은 성공률 경고

- **spark-test / Qwen/Qwen3-Coder-30B-A3B-Instruct / custom**: 성공률 3.8% (목표: 95% 이상)
- **spark-test / Qwen/Qwen3-Coder-30B-A3B-Instruct / high-load-5min**: 성공률 3.7% (목표: 95% 이상)

### ⚠️ 높은 지연시간 경고

- **spark-test / Qwen/Qwen3-Coder-30B-A3B-Instruct / custom**: P99 TTFT 576.726s (목표: 2s 이하)
- **spark-test / Qwen/Qwen3-Coder-30B-A3B-Instruct / custom**: P99 TTFT 82.223s (목표: 2s 이하)
- **spark-test / Qwen/Qwen3-Coder-30B-A3B-Instruct / high-load-5min**: P99 TTFT 586.436s (목표: 2s 이하)
- **localhost / Qwen/Qwen3-Coder-30B-A3B-Instruct / custom**: P99 TTFT 87.558s (목표: 2s 이하)

---

*이 리포트는 자동 생성되었습니다.*
