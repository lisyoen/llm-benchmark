# Session 011: 코딩 난이도별 프롬프트 재구성

## 세션 정보
**세션 ID:** session-011-20251110-coding-difficulty-prompts  
**제목:** AI Code Agent 테스트를 위한 코딩 난이도별 프롬프트 재구성  
**상태:** 완료  
**시작 일시:** 2025-11-10  
**종료 일시:** 2025-11-10  

---

## 작업 목적

기존 프롬프트 타입을 "길이별"에서 "코딩 난이도별"로 변경:
- **기존 문제**: Short/Medium/Long은 단순 길이 구분 (날씨, 일반 대화 포함)
- **변경 목적**: AI Code Agent로써의 LLM 성능 측정에 집중
- **새로운 구조**: Easy/Medium/Hard (코딩 난이도)

---

## 작업 계획

1. ✅ 세션 파일 생성 및 TODO 리스트 관리
2. ⏳ 프롬프트 타입 재정의 (short/medium/long → easy/medium/hard)
3. ⏳ Easy 난이도 프롬프트 작성 (간단한 함수, 기초 디버깅)
4. ⏳ Medium 난이도 프롬프트 작성 (API 구현, 알고리즘)
5. ⏳ Hard 난이도 프롬프트 작성 (복잡한 아키텍처, 최적화)
6. ⏳ workloads.yaml 업데이트
7. ⏳ README 업데이트 (프롬프트 예시 변경)
8. ⏳ 에러 확인 및 Git 커밋

---

## 프롬프트 난이도 정의

### Easy (기초 코딩 작업)
**목적:** 기본 문법, 간단한 함수 구현, 기초 디버깅
**특징:**
- 10-30줄 이내의 코드
- 명확한 입출력
- 단일 함수/클래스
- 기초 알고리즘

**예시 작업:**
- 간단한 유틸리티 함수 작성
- 기초 데이터 변환
- 간단한 버그 수정
- 기본 테스트 코드

### Medium (실무 개발 작업)
**목적:** 실제 개발 시나리오, API 구현, 알고리즘 문제 해결
**특징:**
- 50-150줄 정도의 코드
- 여러 함수/클래스 조합
- 에러 핸들링 포함
- 실무 패턴 적용

**예시 작업:**
- REST API 엔드포인트 구현
- 중급 알고리즘 문제 (정렬, 탐색)
- 데이터베이스 쿼리 최적화
- 유닛 테스트 작성

### Hard (복잡한 시스템 설계)
**목적:** 아키텍처 설계, 성능 최적화, 전체 시스템 구현
**특징:**
- 200줄 이상의 코드
- 다중 모듈/서비스 설계
- 확장성 고려
- 고급 패턴 적용

**예시 작업:**
- 마이크로서비스 아키텍처 설계
- 분산 시스템 구현
- 성능 병목 분석 및 최적화
- 전체 프로젝트 스캐폴딩

---

## 수행한 작업

### 1. 세션 초기화
- ✅ session-011 파일 생성
- ✅ TODO 리스트 8단계 작성

### 2. workloads.yaml 전면 재구성
#### 2.1 프롬프트 타입 변경
- **변경 전**: prompt_type (short/medium/long)
- **변경 후**: difficulty (easy/medium/hard)
- 모든 워크로드 정의에서 변경 적용

#### 2.2 프롬프트 템플릿 재작성
**Easy 난이도 (5개)**
- 리스트 중복 제거 함수
- 회문 검사 함수 + 테스트
- 버그 수정 (간단한 디버깅)
- JSON 파일 저장/읽기 유틸리티
- 날짜 계산 함수

**Medium 난이도 (4개)**
- FastAPI RESTful API (GET/POST, Pydantic 검증)
- K번째 큰 요소 찾기 (heapq, O(n log k))
- SQLAlchemy User-Post 관계 및 쿼리 최적화
- aiohttp 비동기 웹 스크래핑 (세마포어, 재시도)

**Hard 난이도 (3개)**
- 마이크로서비스 E-commerce (FastAPI, Redis, PostgreSQL, Saga 패턴)
- 대용량 로그 분석 시스템 (초당 100만 건, ClickHouse)
- 분산 캐시 시스템 (Consistent Hashing, LRU, Redis 샤딩)

### 3. 스크립트 코드 업데이트
#### 3.1 run_bench.py
- `prompt_type` → `difficulty` 변경
- 하위 호환성 유지 (fallback 로직)
```python
difficulty = workload.get('difficulty', workload.get('prompt_type', 'medium'))
```

#### 3.2 run_bench_interactive.py
**변경 사항:**
- CLI 인수: `--prompt-type` → `--difficulty` (하위 호환성 유지)
- 커스텀 설정: "프롬프트 길이" → "코딩 난이도"
- 출력 메시지: "프롬프트 타입" → "코딩 난이도"
- 선택지: short/medium/long → easy/medium/hard

### 4. README 업데이트
#### 4.1 테스트 프롬프트 예시 섹션
**변경 전:**
- Short: 날씨, Hello World
- Medium: LLM 설명, 비동기 프로그래밍
- Long: FastAPI 서버, Kubernetes 설계

**변경 후:**
- Easy: 중복 제거, 회문 검사, 버그 수정
- Medium: FastAPI API, K번째 요소, SQLAlchemy 최적화
- Hard: 마이크로서비스, 로그 분석, 분산 캐시

#### 4.2 워크로드 프리셋 설명
- "개별 사용자 탐색" → "기초 코딩 작업 (Easy)"
- "일반 서비스" → "일반 개발 작업 (Medium)"
- "피크 타임" → "복잡한 시스템 설계 (Hard)"

---

## 주요 결정사항

### 1. 난이도 기준 정의
**Easy (10-30줄)**
- 단일 함수/클래스
- 명확한 입출력
- 기본 문법 및 알고리즘

**Medium (50-150줄)**
- 여러 컴포넌트 조합
- 에러 핸들링
- 실무 패턴

**Hard (200줄 이상)**
- 다중 모듈/서비스
- 확장성 및 성능
- 고급 아키텍처

### 2. 하위 호환성 유지
- `prompt_type` 필드가 있는 기존 설정도 동작
- `--prompt-type` CLI 인수도 지원 (difficulty로 매핑)
- 코드 내부에서 fallback 처리

### 3. AI Code Agent 중심
- 날씨, 일반 대화 등 비코딩 프롬프트 제거
- 모든 프롬프트를 실제 개발 작업으로 변경
- 난이도별로 요구되는 기술 스택 명시

---

## 생성/수정된 파일

1. **configs/workloads.yaml**
   - 워크로드 정의: prompt_type → difficulty
   - 프롬프트 템플릿 전면 재작성 (12개)
   - AI Code Agent 시나리오로 전환

2. **scripts/run_bench.py**
   - difficulty 필드 우선 사용
   - prompt_type fallback 지원

3. **scripts/run_bench_interactive.py**
   - CLI 인수 업데이트
   - 커스텀 설정 UI 변경
   - 출력 메시지 변경

4. **README.md**
   - 프롬프트 예시를 코딩 난이도별로 재작성
   - 워크로드 설명 업데이트

---

## 학습한 내용

### 1. AI Code Agent 벤치마크 설계
- **길이보다 복잡도**: 코드 길이가 아닌 요구되는 기술 수준이 중요
- **실제 작업 중심**: 실무에서 마주할 법한 작업으로 구성
- **점진적 난이도**: Easy → Medium → Hard로 명확한 단계

### 2. 프롬프트 품질
- **구체적 요구사항**: 추상적 설명보다 구체적 스펙 제공
- **컨텍스트 포함**: 기술 스택, 성능 목표 명시
- **검증 가능**: 성공/실패를 명확히 판단 가능한 기준

### 3. 하위 호환성
- 필드명 변경 시 fallback 로직 필수
- 기존 설정 파일도 동작하도록 보장
- CLI 인수는 dest로 매핑 가능

---

## 테스트 방법 ✅

### 1. 인터랙티브 모드 테스트
```bash
./run_bench.sh
# 또는
python3 scripts/run_bench_interactive.py
```

**확인 사항:**
- 커스텀 설정 시 "코딩 난이도" 선택지 표시 (easy/medium/hard)
- 설정 확인 화면에 "코딩 난이도: medium" 표시
- 실제 코딩 프롬프트가 전송되는지 확인

### 2. CLI 모드 테스트
```bash
python3 scripts/run_bench_interactive.py \
    --target localhost \
    --model "Qwen/Qwen3-Coder-30B-A3B-Instruct" \
    --workload high-load \
    --difficulty hard
```

**확인 사항:**
- `--difficulty` 인수가 정상 작동
- 설정에 "코딩 난이도: hard" 표시
- Hard 난이도 프롬프트 사용

### 3. 하위 호환성 테스트
```bash
# 기존 --prompt-type도 동작해야 함
python3 scripts/run_bench_interactive.py \
    --target localhost \
    --model "..." \
    --prompt-type medium
```

**기대 결과:**
- 에러 없이 실행
- difficulty=medium으로 변환되어 동작

### 4. 예상 출력 예시
```
📋 벤치마크 설정 확인
============================================================
  서버: localhost - Local LiteLLM Server
  모델: Qwen/Qwen3-Coder-30B-A3B-Instruct
  워크로드: 고부하 시나리오 - 복잡한 아키텍처 설계 (Hard)
    - 시간: 180초 (3분)
    - RPS: 20 (초당 요청 수)
    - 동시성: 50
    - 예상 총 요청: 3,600개
    - 최대 토큰: 2048
    - Temperature: 0.7
    - 코딩 난이도: hard  ← 이 부분 확인!
============================================================
```

---

## 다음 세션에서 고려할 사항

1. **프롬프트 검증**
   - 실제 LLM으로 각 난이도 프롬프트 테스트
   - 생성된 코드 품질 평가
   - 난이도가 적절한지 확인

2. **추가 메트릭**
   - 코드 정확도 (문법 오류, 실행 가능 여부)
   - 요구사항 충족도
   - 코드 품질 점수

3. **프롬프트 확장**
   - 각 난이도별 더 다양한 시나리오 추가
   - 다른 프로그래밍 언어 (JavaScript, Go 등)
   - 특정 도메인 (DevOps, Data Science 등)

---

## 참고 자료

- `configs/workloads.yaml`: 새로운 난이도별 프롬프트
- 실무 개발 시나리오 기반 프롬프트 설계
- AI Code Agent 벤치마크 모범 사례
