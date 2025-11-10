# 세션 005: LiteLLM 가동 모델 표시 기능

## 세션 정보
**세션 ID:** session-005-20251110-model-list  
**시작 일시:** 2025-11-10  
**상태:** 완료  
**작성자:** GitHub Copilot

---

## 작업 목적
인터랙티브 모드에서 **LiteLLM이 실제로 가동 중인 모델**을 선택할 수 있도록 개선:
- 기존: `configs/models.yaml`에 설정된 모델만 표시
- 개선: LiteLLM의 `/v1/models` API를 통해 실시간으로 가동 중인 모델 목록 조회
- `run_bench_interactive.py`에서 모델 선택 시 실제 가동 모델만 표시

---

## 작업 계획

### 1. LiteLLM API 조사
- `/v1/models` 엔드포인트의 응답 형식 확인
- 모델 ID 추출 방법 파악

### 2. 모델 목록 조회 함수 작성
- `scripts/run_bench_interactive.py`에 LiteLLM API 호출 함수 추가
- 에러 처리 (LiteLLM 서버가 응답하지 않을 경우 fallback)

### 3. 인터랙티브 모드 수정
- 모델 선택 로직을 LiteLLM API 기반으로 변경
- API 호출 실패 시 기존 `models.yaml` 사용하도록 fallback

### 4. 테스트 및 문서화
- 실제 LiteLLM 서버에 대해 테스트
- 변경사항 문서화

---

## 진행 상황 체크리스트

- [x] 새 세션 파일 생성
- [x] LiteLLM `/v1/models` API 테스트
- [x] 모델 목록 조회 함수 작성
- [x] `run_bench_interactive.py` 수정
- [x] 기능 테스트
- [x] Git 동기화

---

## 생성/수정된 파일
- `.github/sessions/session-005-20251110-model-list.md` (신규)
- `.github/current-session.md` (업데이트)
- `.github/session-manager.md` (업데이트)
- `scripts/run_bench_interactive.py` (수정)
  - httpx import 추가
  - `fetch_litellm_models()` 함수 추가
  - 모델 선택 로직을 LiteLLM API 기반으로 변경

---

## 작업 결과

### 구현 내용
1. **LiteLLM 모델 목록 조회 함수 추가** (`fetch_litellm_models()`)
   - LiteLLM의 `/v1/models` API를 호출하여 실제 가동 중인 모델 조회
   - API 인증 헤더 포함
   - 에러 처리 및 빈 리스트 반환

2. **인터랙티브 모드 수정**
   - 서버 선택 후 LiteLLM API를 통해 실시간으로 가동 중인 모델 조회
   - API 조회 성공 시: LiteLLM 모델 목록 표시
   - API 조회 실패 시: 기존 `configs/models.yaml` 사용 (fallback)
   - 모델 ID를 파일명에 사용할 수 있도록 변환 (예: `/` → `-`)

3. **테스트 결과**
   - spark-test 서버에 대해 테스트 성공
   - `Qwen/Qwen3-Coder-30B-A3B-Instruct` 모델이 올바르게 표시됨
   - 사용자는 실제로 가동 중인 모델만 선택할 수 있음

### 주요 개선 사항
- ✅ 기존: `configs/models.yaml`에 정의된 모델만 선택 가능 (실제 가동 여부와 무관)
- ✅ 개선: LiteLLM이 실제로 가동 중인 모델만 표시되어 실수 방지
- ✅ Fallback: API 조회 실패 시 기존 방식으로 동작하여 안정성 확보

---

## 학습한 내용 및 결정 사항

1. **LiteLLM API 구조**
   - `/v1/models` 엔드포인트는 OpenAI API와 호환
   - 인증 헤더(`Authorization: Bearer {api_key}`) 필요
   - 응답 형식: `{"data": [{"id": "model_id", ...}, ...]}`

2. **모델 ID 변환**
   - LiteLLM의 모델 ID는 `Qwen/Qwen3-Coder-30B-A3B-Instruct` 같은 형식
   - 파일명으로 사용하기 위해 `/`를 `-`로 변환
   - 전체 ID는 `full_name`으로 유지하여 API 호출 시 사용

3. **에러 처리 전략**
   - API 조회 실패 시 사용자에게 경고 메시지 표시
   - 자동으로 `configs/models.yaml`로 fallback
   - 기존 기능이 중단되지 않도록 보장
