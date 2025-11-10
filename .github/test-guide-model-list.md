# 테스트 가이드: LiteLLM 모델 목록 조회 기능

## 개요
이 기능은 인터랙티브 모드에서 모델을 선택할 때 LiteLLM이 실제로 가동 중인 모델 목록을 표시합니다.

---

## 테스트 환경
- LiteLLM 서버가 가동 중이어야 함
- 최소 1개 이상의 모델이 로드되어 있어야 함

---

## 테스트 절차

### 1. 인터랙티브 모드 실행
```bash
cd /home/score/llmrp/llm-benchmark
source venv/bin/activate
python3 scripts/run_bench_interactive.py
```

### 2. 서버 선택
- 테스트할 LiteLLM 서버 선택 (예: spark-test)
- 엔터 키를 눌러 기본값 사용 가능

### 3. 모델 목록 확인
**예상 결과:**
```
🔍 LiteLLM에서 가동 중인 모델 조회 중...
✅ 1개의 모델이 가동 중입니다.

🤖 테스트 모델 선택:
  → 1. Qwen3-Coder-30B-A3B-Instruct (Qwen/Qwen3-Coder-30B-A3B-Instruct)
```

**확인 포인트:**
- ✅ "LiteLLM에서 가동 중인 모델 조회 중..." 메시지 표시
- ✅ 실제 가동 중인 모델 개수 표시
- ✅ 모델 ID가 LiteLLM에서 실제로 로드된 모델과 일치
- ✅ 표시 이름이 읽기 쉬운 형식으로 나타남

### 4. Fallback 동작 테스트 (선택 사항)
LiteLLM 서버를 중지하고 다시 실행:

**예상 결과:**
```
🔍 LiteLLM에서 가동 중인 모델 조회 중...
⚠️  LiteLLM 모델 목록을 가져올 수 없습니다. configs/models.yaml 사용

🤖 테스트 모델 선택:
  → 1. qwen3-coder-30b: Qwen3 Coder 30B
    2. qwen2-72b: Qwen2 72B Instruct
    ...
```

**확인 포인트:**
- ✅ 경고 메시지 표시
- ✅ `configs/models.yaml`의 모델 목록으로 fallback
- ✅ 기존 기능이 정상적으로 동작

---

## 성공/실패 판단 기준

### 성공
1. LiteLLM API 조회가 성공하고 실제 모델 목록이 표시됨
2. 모델을 선택하고 벤치마크를 실행할 수 있음
3. API 조회 실패 시 자동으로 fallback 동작

### 실패
1. 모델 목록이 비어있거나 잘못된 모델이 표시됨
2. API 오류 발생 시 프로그램이 중단됨
3. Fallback이 동작하지 않음

---

## 문제 발생 시 확인사항

1. **LiteLLM 서버가 응답하는가?**
   ```bash
   curl -H "Authorization: Bearer sk--VGcWKuO_nquce9dMMc5IA" \
        http://172.21.113.31:4000/v1/models
   ```

2. **API 키가 올바른가?**
   - `configs/targets.yaml`에서 `api_key` 확인

3. **모델이 실제로 로드되었는가?**
   - LiteLLM 로그 확인
   - `/v1/models` API 응답 확인

---

## 추가 테스트 시나리오

### 여러 모델이 가동 중인 경우
- 모든 모델이 목록에 표시되는지 확인
- 모델 선택이 올바르게 동작하는지 확인

### 서로 다른 서버 테스트
- score-main, spark-test, titan-test 등 다양한 서버에서 테스트
- 각 서버에 맞는 모델이 표시되는지 확인

---

**작성일:** 2025-11-10  
**작성자:** GitHub Copilot
