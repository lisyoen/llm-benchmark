# 프로젝트 컨텍스트

## 프로젝트 개요

**프로젝트명:** llm-benchmark  
**목적:** GPU 서버 환경에서 LLM 성능을 자동 측정하기 위한 벤치마크 도구  
**대상:** vLLM, LiteLLM 등 OpenAI 호환 API

---

## 프로젝트 구조 및 역할

### 디렉토리 구조

```
llm-benchmark/
├── .github/                 # 프로젝트 관리 문서
│   ├── copilot-instructions.md  # Copilot 지시사항
│   ├── project-goal.md          # 프로젝트 목표 및 계획
│   ├── project-context.md       # 이 파일
│   ├── session-manager.md       # 세션 관리
│   ├── current-session.md       # 현재 작업 상태
│   ├── work-history.md          # 작업 히스토리
│   └── sessions/                # 세션별 상세 기록
│
├── scripts/                 # 실행 스크립트
│   ├── run_bench.py         # 벤치마크 메인 실행 (비동기 HTTP 요청)
│   ├── parse_metrics.py     # 결과 파싱 및 통계 계산
│   ├── gen_report.py        # Markdown 리포트 생성
│   └── run_bench.sh         # 전체 파이프라인 셸 스크립트
│
├── configs/                 # 설정 파일 (YAML)
│   ├── targets.yaml         # 벤치마크 대상 엔드포인트 정의
│   ├── models.yaml          # 테스트 모델 목록
│   └── workloads.yaml       # 워크로드 패턴 (RPS, 동시성 등)
│
├── results/                 # 벤치마크 결과 저장
│   ├── raw/                 # 원시 측정 로그 (JSONL)
│   ├── summary/             # 통계 요약 (CSV)
│   └── reports/             # 최종 리포트 (Markdown/HTML)
│
├── README.md                # 프로젝트 사용 가이드
├── requirements.txt         # Python 의존성
├── LICENSE                  # 라이선스
└── .gitignore              # Git 제외 파일
```

---

## 핵심 파일 설명

### 1. `scripts/run_bench.py`
- **역할:** 비동기 부하 테스트 실행
- **주요 기능:**
  - OpenAI 호환 API로 streaming 요청 전송
  - TTFT (Time To First Token) 측정
  - 토큰 처리량, 응답시간 기록
  - JSONL 형식으로 원시 데이터 저장
- **의존성:** httpx, asyncio, yaml
- **입력:** configs/*.yaml
- **출력:** results/raw/*.jsonl

### 2. `scripts/parse_metrics.py`
- **역할:** 결과 파싱 및 통계 계산
- **주요 기능:**
  - JSONL 파일 읽기
  - 평균, 중앙값, P95, P99 계산
  - 성공률, 에러율 집계
  - CSV 파일로 통계 저장
- **의존성:** pandas
- **입력:** results/raw/*.jsonl
- **출력:** results/summary/*.csv

### 3. `scripts/gen_report.py`
- **역할:** Markdown 리포트 생성
- **주요 기능:**
  - 여러 CSV 파일 통합
  - 성능 비교 테이블 생성
  - 권장사항 및 경고 생성
- **의존성:** pandas
- **입력:** results/summary/*.csv
- **출력:** results/reports/benchmark_report.md

### 4. `scripts/run_bench.sh`
- **역할:** 전체 파이프라인 자동화
- **실행 순서:**
  1. `run_bench.py` 실행
  2. `parse_metrics.py`로 결과 파싱
  3. `gen_report.py`로 리포트 생성

---

## 설정 파일 구조

### `configs/targets.yaml`
벤치마크 대상 서버 정의
```yaml
targets:
  - name: vllm-local
    base_url: http://localhost:8000/v1
    api_key: "EMPTY"
```

### `configs/models.yaml`
테스트 대상 모델 목록
```yaml
models:
  - name: llama-3.1-8b-instruct
    full_name: meta-llama/Meta-Llama-3.1-8B-Instruct
    context_length: 8192
```

### `configs/workloads.yaml`
워크로드 패턴 정의
```yaml
workloads:
  - name: medium-load
    duration: 300     # 초
    rps: 5            # Requests Per Second
    concurrency: 10
    max_tokens: 1024
    temperature: 0.7
    prompt_type: medium
```

---

## 측정 지표

### 1. TTFT (Time To First Token)
- **정의:** 요청 전송부터 첫 번째 토큰 수신까지의 시간
- **중요도:** 사용자 체감 반응 속도
- **측정 단위:** 초(s)
- **통계:** Mean, Median, P95, P99

### 2. 총 응답 시간
- **정의:** 요청 전송부터 응답 완료까지의 시간
- **중요도:** 전체 처리 시간
- **측정 단위:** 초(s)
- **통계:** Mean, Median, P95, P99

### 3. 토큰 처리량
- **정의:** 초당 생성되는 토큰 수
- **중요도:** 시스템 처리 능력
- **측정 단위:** tokens/sec
- **통계:** Mean, Median, P95

### 4. 성공률
- **정의:** 전체 요청 중 성공한 요청의 비율
- **중요도:** 시스템 안정성
- **측정 단위:** %
- **목표:** 95% 이상

---

## 코딩 스타일 및 컨벤션

### Python
- **버전:** Python 3.11+
- **스타일:** PEP 8
- **독스트링:** 함수/클래스마다 명확한 설명 추가
- **타입 힌트:** 함수 시그니처에 타입 명시
- **비동기:** `async`/`await` 패턴 사용

### 파일명 규칙
- **스크립트:** snake_case (예: `run_bench.py`)
- **설정:** kebab-case (예: `workloads.yaml`)
- **결과 파일:** 타임스탬프 포함 (예: `bench_vllm_20251107_143022.jsonl`)

### Git 커밋 메시지
- **형식:** `[타입] 간단한 설명`
- **타입:** feat, fix, docs, refactor, test, chore
- **언어:** 한국어

---

## 기술 스택

### 필수 라이브러리
- **httpx:** 비동기 HTTP 클라이언트
- **asyncio:** 비동기 프로그래밍
- **pyyaml:** YAML 파싱
- **pandas:** 데이터 분석 및 CSV 처리

### 개발 도구
- **Python 3.11+**
- **Git**
- **GitHub** (리포지토리 호스팅)

---

## 확장 계획

### Phase 2: GPU 메트릭 통합
- Prometheus로부터 GPU 메트릭 수집
- nvidia-smi exporter 연동
- 토큰당 전력 효율(Tokens/W) 계산

### Phase 3: 시각화
- Grafana 대시보드 연동
- HTML 리포트 생성
- 성능 추이 그래프

### Phase 4: CI/CD 통합
- GitHub Actions 자동화
- Self-hosted GPU Runner 설정
- 정기 벤치마크 실행 및 리포트 생성

---

## 참고 사항

### 환경 변수
- `OPENAI_API_KEY`: OpenAI API 키 (비교 테스트용)

### 포트
- vLLM: 기본 8000번
- LiteLLM: 기본 4000번

### 주의사항
- 대규모 부하 테스트 시 대상 서버 리소스 고려
- 실제 프로덕션 환경에서는 사전 협의 필요
- API 키 및 엔드포인트는 .env 파일로 관리 권장

---

**문서 버전:** 1.0  
**최종 업데이트:** 2025-11-07
