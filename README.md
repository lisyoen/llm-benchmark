# llm-benchmark

GPU 서버 환경에서 LLM 성능을 자동 측정하기 위한 내부용 벤치마크 도구입니다.

## 개요

`llm-benchmark`는 S-CORE의 LLM Run Package 구성 요소(vLLM, LiteLLM 등)를 대상으로  
**지연시간, 처리량, 안정성, 효율성**을 자동 측정하고 리포트를 생성하는 도구입니다.

### 주요 기능

- ✅ OpenAI 호환 API 대상 부하 테스트 (`/v1/chat/completions`)
- ✅ TTFT (Time To First Token), 응답시간, 토큰 처리량 측정
- ✅ 워크로드별/모델별 성능 비교 리포트 자동 생성
- ✅ 비동기 요청 처리로 대규모 부하 시뮬레이션
- 🔄 GPU 리소스 효율 분석 (확장 예정)

## 프로젝트 구조

```
llm-benchmark/
├── scripts/              # 실행 스크립트
│   ├── run_bench.py      # 벤치마크 실행
│   ├── parse_metrics.py  # 결과 파싱 및 통계 계산
│   ├── gen_report.py     # 리포트 생성
│   └── run_bench.sh      # 전체 파이프라인 스크립트
├── configs/              # 설정 파일
│   ├── targets.yaml      # 벤치마크 대상 엔드포인트
│   ├── models.yaml       # 테스트 모델 목록
│   └── workloads.yaml    # 워크로드 패턴 정의
├── results/              # 결과 저장
│   ├── raw/              # 원시 측정 로그 (JSONL)
│   ├── summary/          # 통계 요약 (CSV)
│   └── reports/          # 최종 리포트 (Markdown)
└── .github/              # 프로젝트 문서
```

## 설치

### 요구사항

- Python 3.11+
- pip

### 의존성 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 1. 설정 파일 편집

**대상 서버 설정** (`configs/targets.yaml`):
```yaml
targets:
  - name: vllm-local
    base_url: http://localhost:8000/v1
    api_key: "EMPTY"
```

**테스트 모델 설정** (`configs/models.yaml`):
```yaml
models:
  - name: llama-3.1-8b-instruct
    full_name: meta-llama/Meta-Llama-3.1-8B-Instruct
```

**워크로드 설정** (`configs/workloads.yaml`):
```yaml
workloads:
  - name: medium-load
    duration: 300  # 초
    rps: 5         # Requests Per Second
    concurrency: 10
```

### 2. 벤치마크 실행

#### 🚀 대화형 실행 (추천!)

```bash
# 가상환경 활성화
source venv/bin/activate

# 대화형 벤치마크 실행
python3 scripts/run_bench_interactive.py
```

**특징:**
- 💡 엔터만 치면 기본값 사용 (5분 고부하 테스트)
- 서버, 모델, 워크로드 선택 가능
- 커스텀 설정 지원 (시간, RPS, 토큰 수 등)

#### 개별 스크립트 실행

```bash
# 벤치마크 실행
python3 scripts/run_bench.py --target vllm-local --model llama-3.1-8b-instruct --workload medium-load

# 결과 파싱
python3 scripts/parse_metrics.py results/raw/bench_*.jsonl

# 리포트 생성
python3 scripts/gen_report.py
```

#### 전체 파이프라인 실행

```bash
# 기본 설정으로 실행
./scripts/run_bench.sh

# 파라미터 지정
./scripts/run_bench.sh vllm-local llama-3.1-8b-instruct high-load
```

### 3. 결과 확인

- **원시 데이터**: `results/raw/*.jsonl`
- **통계 요약**: `results/summary/*.csv`
- **리포트**: `results/reports/benchmark_report.md`

## 측정 지표

### 1. TTFT (Time To First Token)
첫 번째 토큰이 생성될 때까지의 지연시간

- Mean, Median, P95, P99

### 2. 총 응답 시간
요청부터 응답 완료까지의 총 시간

- Mean, Median, P95, P99

### 3. 토큰 처리량
초당 생성되는 토큰 수 (tokens/sec)

- Mean, Median, P95

### 4. 성공률
전체 요청 중 성공한 요청의 비율 (%)

## 워크로드 시나리오

| 시나리오 | RPS | 동시성 | 설명 |
|---------|-----|--------|------|
| `low-load` | 1 | 1 | 개별 사용자 탐색 |
| `medium-load` | 5 | 10 | 일반적인 프로덕션 |
| `high-load` | 20 | 50 | 피크 타임 트래픽 |
| `stress-test` | 50 | 100 | 시스템 한계 측정 |

## 확장 계획

- [ ] Prometheus/Grafana 연동으로 GPU 메트릭 수집
- [ ] 토큰당 전력 효율(Tokens/W) 계산
- [ ] 여러 모델 간 비교 시각화
- [ ] CI 파이프라인 자동화 (GitHub Actions)
- [ ] HTML/PDF 리포트 생성

## 개발자 정보

**작성자:** 이창연 (AI사업그룹)  
**작성일:** 2025-11-07  
**라이선스:** MIT

## 기여

이슈 및 풀 리퀘스트 환영합니다!

---

**Note:** 이 도구는 S-CORE 내부 사용을 위해 개발되었습니다.
