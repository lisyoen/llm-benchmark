# LLM 벤치마크 리포트

**생성 일시:** 2025-11-07 08:00:12

---

## 1. 개요

- **총 테스트 수:** 1
- **테스트 대상:** spark-test
- **테스트 모델:** Qwen/Qwen3-Coder-30B-A3B-Instruct
- **워크로드:** low-load

---

## 2. 성능 지표

### 2.1 TTFT (Time To First Token)

| Target | Model | Workload | Mean (s) | Median (s) | P95 (s) | P99 (s) |
|--------|-------|----------|----------|------------|---------|----------|
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 0.091 | 0.084 | 0.156 | 0.156 |

### 2.2 총 응답 시간

| Target | Model | Workload | Mean (s) | Median (s) | P95 (s) | P99 (s) |
|--------|-------|----------|----------|------------|---------|----------|
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 5.061 | 2.972 | 14.454 | 14.454 |

### 2.3 토큰 처리량

| Target | Model | Workload | Mean (tokens/s) | Median (tokens/s) | P95 (tokens/s) |
|--------|-------|----------|-----------------|-------------------|----------------|
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 25.3 | 25.6 | 26.3 |

### 2.4 성공률

| Target | Model | Workload | Total | Success | Failed | Success Rate |
|--------|-------|----------|-------|---------|--------|-------------|
| spark-test | Qwen/Qwen3-Coder-30B-A3B-Instr... | low-load | 12 | 12 | 0 | 100.0% |

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

---

*이 리포트는 자동 생성되었습니다.*
