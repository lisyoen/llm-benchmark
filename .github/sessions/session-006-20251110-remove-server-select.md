# 세션 006: 인터랙티브 모드 서버 선택 단계 제거

## 세션 정보
- **세션 ID:** session-006-20251110-remove-server-select
- **날짜:** 2025-11-10
- **상태:** 완료
- **담당자:** GitHub Copilot

---

## 작업 목적
인터랙티브 모드에서 서버 선택 단계를 제거하여 사용자 경험 개선:
- 현재: 서버 선택 → 모델 선택 → 워크로드 선택 (5단계)
- 개선: 모델 선택 → 워크로드 선택 (4단계)
- `configs/targets.yaml`의 `default_target` 값을 자동으로 사용
- 빠른 테스트 시작 가능

---

## 작업 계획

### 1단계: 코드 분석 ✅
- `run_bench_interactive.py` 서버 선택 로직 파악
- 265-283줄: 서버 선택 인터랙션 부분
- `default_target` 설정 확인 (현재: `score-main`)

### 2단계: 코드 수정
- 서버 선택 단계 제거
- `default_target`으로 자동 선택 로직 추가
- 사용자에게 선택된 서버 안내 메시지 추가

### 3단계: 테스트
- 대화형 모드 실행 테스트
- 모델 선택부터 바로 시작되는지 확인
- CLI 모드 영향 없음 확인

### 4단계: 문서화 및 동기화
- 세션 파일 완료 처리
- Git 커밋 및 푸시

---

## 현재 문제점
- 인터랙티브 모드에서 매번 서버를 선택해야 함
- 대부분의 경우 같은 서버(default_target)를 사용
- 불필요한 단계가 사용자 경험을 저하시킴

---

## 개선 방향
- `default_target` 자동 사용으로 단계 축소
- 서버 변경이 필요한 경우:
  - Option 1: `configs/targets.yaml`의 `default_target` 수정
  - Option 2: CLI 모드에서 `--target` 옵션 사용

---

## 진행 상황
- [x] 세션 파일 생성
- [x] 코드 수정
- [x] 테스트
- [x] Git 동기화

---

## 작업 결과

### ✅ 완료된 작업

#### 1. 코드 수정
**파일:** `scripts/run_bench_interactive.py`

**변경 내용:**
- 265-283줄의 서버 선택 인터랙션 로직 제거
- `default_target` 자동 선택 로직으로 대체
- 사용자에게 선택된 서버 안내 메시지 추가

**수정 후 코드:**
```python
# 1. 서버 자동 선택 (default_target 사용)
default_target_name = targets.get('default_target', targets['targets'][0]['name'])
target = next(
    (t for t in targets['targets'] if t['name'] == default_target_name),
    targets['targets'][0]  # 폴백: 첫 번째 서버
)

print(f"\n📡 대상 서버: {target['name']} - {target['description']}")
print(f"💡 팁: 서버를 변경하려면 configs/targets.yaml의 default_target을 수정하세요.\n")
```

#### 2. 테스트 결과
✅ **성공적으로 작동 확인**
- 서버 선택 단계 없이 바로 모델 선택으로 진행
- `default_target` (score-main) 자동 선택됨
- 10개 모델이 정상적으로 조회됨
- 전체 워크플로우 정상 작동

**테스트 출력:**
```
📡 대상 서버: score-main - S-Core 주력 LLM 서버 (H200 GPU 8장)
💡 팁: 서버를 변경하려면 configs/targets.yaml의 default_target을 수정하세요.

🔍 LiteLLM에서 가동 중인 모델 조회 중...
✅ 10개의 모델이 가동 중입니다.

🤖 테스트 모델 선택:
  → 1. Meta-Llama-3.1-70B-Instruct-FP8
  ...
```

#### 3. 개선 효과
- **Before:** 5단계 (서버 선택 → 모델 선택 → 워크로드 선택 → 확인 → 실행)
- **After:** 4단계 (모델 선택 → 워크로드 선택 → 확인 → 실행)
- **시간 절약:** 약 5-10초 (서버 선택 단계 제거)
- **사용자 경험:** 더 직관적이고 빠른 시작

### 📝 변경 파일
- `scripts/run_bench_interactive.py` (265-283줄 수정)

### 🔄 영향받는 기능
- **대화형 모드만 영향** (✅ 의도된 동작)
- **CLI 모드는 영향 없음** (✅ `--target` 옵션 여전히 사용 가능)

---

## 테스트 가이드

### 대화형 모드 테스트
```bash
cd /home/score/llmrp/llm-benchmark
source venv/bin/activate
python3 scripts/run_bench_interactive.py
```

**확인 사항:**
1. ✅ 서버 선택 단계 없이 바로 시작
2. ✅ `score-main` 서버가 자동 선택됨
3. ✅ 안내 메시지 표시: "💡 팁: 서버를 변경하려면..."
4. ✅ 모델 선택부터 정상 진행

### CLI 모드 테스트 (선택 사항)
```bash
# CLI 모드는 여전히 --target 옵션 사용 가능
python3 scripts/run_bench_interactive.py \
  --target spark-test \
  --model qwen3-coder-30b \
  --workload high-load
```

**확인 사항:**
1. ✅ CLI 모드는 기존과 동일하게 작동
2. ✅ `--target` 옵션으로 서버 지정 가능

### 서버 변경 방법
**Option 1: 설정 파일 수정 (권장)**
```yaml
# configs/targets.yaml
default_target: spark-test  # score-main에서 변경
```

**Option 2: CLI 모드 사용**
```bash
python3 scripts/run_bench_interactive.py --target spark-test ...
```

---

## 학습 내용
1. **사용자 경험 개선:** 불필요한 단계 제거로 빠른 시작 가능
2. **설정 기반 동작:** `default_target` 설정으로 유연한 관리
3. **점진적 개선:** CLI 모드는 그대로 유지하면서 대화형 모드만 개선
