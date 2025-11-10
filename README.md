# Run Bench

GPU 서버에서 LLM 성능을 자동 측정하기 위한 벤치마크 도구입니다.

## 개요

**Run Bench**는 LiteLLM 설정에서 모델 정보를 자동으로 가져와  
**지연시간, 처리량, 안정성**을 측정하고 리포트를 생성하는 도구입니다.

### 주요 특징

- ✅ **LiteLLM 연동**: 설치된 모델을 자동으로 감지
- ✅ TTFT (Time To First Token), 응답시간, 토큰 처리량 측정
- ✅ 워크로드별 성능 비교 리포트 자동 생성
- ✅ 비동기 요청 처리로 대규모 부하 시뮬레이션
- ✅ CSV + Markdown 리포트 자동 생성

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

### 방법 1: 패키지 설치 (권장)

**Run Bench** 배포 패키지를 사용하는 방법:

```bash
# 1. 패키지 압축 해제
tar -xzf run-bench-20251107-001.tar.gz
cd run-bench-20251107-001

# 2. 설치 스크립트 실행
./install.sh
```

설치 스크립트는 자동으로 다음을 수행합니다:
- 시스템 의존성 확인 및 자동 설치 (python3, python3-venv, python3-pip, git)
- Python 버전 확인 (3.11+)
- 가상환경 생성 (`venv/`)
- Python 의존성 패키지 설치
- 디렉토리 구조 생성
- 설정 파일 템플릿 생성

**지원 OS**: Ubuntu, Debian, CentOS, RHEL, Fedora

### 방법 2: 수동 설치

소스 코드가 있는 경우 직접 설치:

```bash
# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 필요한 디렉토리 생성
mkdir -p results/raw results/summary results/reports
```

### 패키지 빌드 (개발자용)

배포 패키지를 직접 생성하려면:

```bash
./build_package.sh
# run-bench-YYYYMMDD-BBB.tar.gz 파일이 생성됩니다
# 예: run-bench-20251107-001.tar.gz
```

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 필요한 디렉토리 생성
mkdir -p results/raw results/summary results/reports
```

### 요구사항

- **Python**: 3.11 이상
- **OS**: Linux (Ubuntu, CentOS 등)
- **의존성 패키지**:
  - httpx >= 0.27.0 (HTTP 클라이언트)
  - pyyaml >= 6.0.1 (설정 파일 파싱)
  - pandas >= 2.2.0 (데이터 분석)

## 사용법

### 빠른 시작 (권장)

**가장 간단한 방법** - 한 줄로 벤치마크 실행:

```bash
# 인터랙티브 모드로 벤치마크 실행
./run_bench.sh
```

이 스크립트는 자동으로:
- ✅ 가상환경 활성화
- ✅ 인터랙티브 모드 실행
- ✅ 결과 자동 생성

---

### 수동 실행 (고급 사용자)

가상환경을 직접 제어하고 싶다면:

```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. 인터랙티브 모드 실행
python3 scripts/run_bench_interactive.py

# 또는 CLI 모드로 직접 실행
python3 scripts/run_bench_interactive.py \
  --target localhost \
  --model "Qwen/Qwen3-Coder-30B-A3B-Instruct" \
  --workload high-load
```

**VSCode 터미널**은 자동으로 가상환경을 활성화하지만, **일반 SSH 터미널**에서는 수동 활성화가 필요합니다.

---

## 테스트 동작 원리

### 🎯 무엇을 테스트하나요?

**Run Bench**는 AI Code Agent로써 LLM의 코딩 능력을 평가합니다.

#### 테스트 프롬프트 예시 (코딩 난이도별)

**Easy (기초 코딩 작업)**
- "Python으로 리스트의 중복을 제거하고 정렬된 결과를 반환하는 함수를 작성해주세요."
- "주어진 문자열이 회문(palindrome)인지 확인하는 함수를 작성하고, 테스트 케이스 3개를 포함해주세요."
- "다음 코드의 버그를 찾아 수정해주세요: (간단한 디버깅)"

**Medium (실무 개발 작업)**
- "FastAPI를 사용하여 RESTful API를 구현해주세요 (GET/POST /users, Pydantic 검증, 에러 핸들링 포함)"
- "정렬되지 않은 배열에서 K번째로 큰 요소를 찾는 효율적인 알고리즘 구현 (O(n log k), heapq 사용)"
- "SQLAlchemy User-Post 일대다 관계 구현 및 쿼리 최적화 (N+1 문제 방지)"

**Hard (복잡한 시스템 설계)**
- "마이크로서비스 E-commerce 주문 시스템 설계 (FastAPI, Redis, PostgreSQL, Saga 패턴, Circuit Breaker)"
- "대용량 로그 분석 시스템 구현 (초당 100만 건 처리, 실시간 대시보드, ClickHouse)"
- "분산 캐시 시스템 구현 (Consistent Hashing, LRU, Redis 샤딩, 장애 감지)"

> 💡 **프롬프트는 `configs/workloads.yaml`에서 수정 가능합니다.**

---

### ⚙️ 어떻게 부하를 생성하나요?

#### 핵심 파라미터

| 파라미터 | 설명 | 예시 |
|---------|------|------|
| **RPS** | 초당 요청 수 (Requests Per Second) | `20` = 초당 20개 요청 생성 |
| **Concurrency** | 동시 처리 요청 수 | `50` = 최대 50개 요청이 동시 실행 |
| **Duration** | 테스트 지속 시간 (초) | `300` = 5분간 테스트 |
| **Max Tokens** | 최대 생성 토큰 수 | `2048` = 최대 2048 토큰까지 생성 |

#### 워크로드 프리셋

```yaml
# configs/workloads.yaml

low-load:      # 저부하 - 기초 코딩 작업 (Easy)
  rps: 1       # 초당 1개 요청
  concurrency: 1
  duration: 60초
  difficulty: easy

medium-load:   # 중간부하 - 일반 개발 작업 (Medium, 기본값)
  rps: 5
  concurrency: 10
  duration: 300초 (5분)
  difficulty: medium

high-load:     # 고부하 - 복잡한 시스템 설계 (Hard)
  rps: 20
  concurrency: 50
  duration: 180초 (3분)

stress-test:   # 스트레스 - 시스템 한계 측정
  rps: 50
  concurrency: 100
  duration: 600초 (10분)
```

---

### 🔧 비동기 부하 생성 방식

#### 1. RPS 제어 (일정한 요청 생성)

```python
# 0.05초(50ms)마다 1개씩 요청 생성 → RPS=20
interval = 1.0 / rps  # 1.0 / 20 = 0.05초

while 테스트_진행중:
    새_요청_생성()
    await asyncio.sleep(interval)  # 50ms 대기
```

**동작 방식:**
- RPS=20 설정 시, **50ms마다** 새 요청을 생성합니다
- 요청 생성과 처리가 **분리**되어 일정한 속도 유지
- 5분(300초) 동안 총 **6,000개 요청** 생성

#### 2. Concurrency 제어 (동시 처리 제한)

```python
# 최대 50개까지만 동시 실행
semaphore = asyncio.Semaphore(50)

async def 요청_실행():
    async with semaphore:  # 50개 슬롯 중 하나 사용
        await API_호출()   # 실제 요청 처리
    # 완료되면 슬롯 반환 (다음 요청이 실행 가능)
```

**동작 방식:**
- Concurrency=50 설정 시, **최대 50개 요청이 동시 실행**
- 51번째 요청은 앞의 요청이 완료될 때까지 **대기**
- 서버 과부하 방지하면서 실제 부하 시뮬레이션

#### 3. 비동기 vs 멀티스레드

| 구분 | 멀티스레드 | 비동기 (Run Bench) |
|------|-----------|-------------------|
| 동시성 메커니즘 | OS 스레드 (커널 레벨) | 이벤트 루프 (유저 레벨) |
| 메모리 사용 | 스레드당 ~1MB | 태스크당 ~KB |
| 최대 동시성 | ~수백 개 | ~수만 개 |
| 적합한 작업 | CPU 집약적 | I/O 집약적 ✅ |

**왜 비동기를 사용하나요?**
- LLM API 호출은 **네트워크 대기 시간**이 긴 I/O 작업
- 응답을 기다리는 동안 다른 요청을 처리할 수 있음
- 단일 프로세스로 **수천 개의 동시 연결** 효율적 처리

---

### 📊 측정 지표

#### TTFT (Time To First Token)
- 요청 전송 후 **첫 토큰이 도착할 때까지 시간**
- 사용자가 체감하는 **반응 속도**
- 예: 0.2초 → 사용자가 즉시 응답 시작을 확인

#### Total Response Time
- 요청 전송부터 **응답 완료까지 전체 시간**
- 스트리밍의 경우 마지막 토큰까지 시간
- 예: 5.3초 → 전체 답변 생성 완료

#### Token Throughput (처리량)
- **초당 생성하는 토큰 수**
- 모델의 생성 속도 지표
- 예: 125 tokens/s → 1초에 125개 토큰 생성

#### GPU Utilization (사용률) 🆕
- GPU 사용률, 메모리, 전력, 온도 실시간 모니터링
- 성능-전력 효율 분석 가능
- 예: 평균 87% 사용률, 420W 전력

---

### 🚀 실행 흐름 예시

**5분 고부하 테스트 (high-load)**

```
설정:
- Duration: 300초 (5분)
- RPS: 20
- Concurrency: 50
- 총 요청: 6,000개

타임라인:
00:00 → 테스트 시작, GPU 모니터링 시작
00:00 → 요청 #1 생성
00:05 → 요청 #2 생성 (50ms 후)
00:10 → 요청 #3 생성
...
01:00 → 60초 경과, 1,200개 요청 생성, 850개 완료
        GPU: 87% 사용률, 420W
03:00 → 3분 경과, 3,600개 요청 생성, 3,200개 완료
        GPU: 91% 사용률, 450W
05:00 → 테스트 완료, 6,000개 요청 생성
05:30 → 모든 응답 수신 완료, GPU 모니터링 종료
        
결과:
- 성공률: 99.2%
- 평균 TTFT: 0.23초
- 평균 응답시간: 5.8초
- 처리량: 125 tokens/s
- GPU 평균 사용률: 87%
```

---

### 실제 측정 데이터 예시

**5분 고부하 테스트 결과 (RPS=20, Concurrency=50):**

| 지표 | Mean | Median | P95 | P99 |
|------|------|--------|-----|-----|
| TTFT (ms) | 325 | 310 | 450 | 580 |
| Total Time (s) | 2.15 | 2.08 | 3.12 | 3.85 |
| Tokens/sec | 245 | 248 | 198 | 165 |
| Success Rate | 99.67% | - | - | - |

### GPU 사용률 확인

테스트 실행 중 다른 터미널에서 GPU 사용률을 모니터링할 수 있습니다:

```bash
# 1초마다 GPU 상태 갱신
watch -n 1 nvidia-smi
```

**예상 결과:**
- GPU 사용률: 0% → 95% (부하 테스트 시작 후)
- GPU 온도: 45°C → 65°C (부하 증가)
- 전력 소비: 50W → 400W (추론 작업 수행)

---

### 대화형 인터페이스 예시

```bash
$ python3 scripts/run_bench_interactive.py

============================================================
🚀 Run Bench - 대화형 벤치마크 실행
============================================================

💡 팁: 엔터만 치면 기본값 사용 (5분 고부하 테스트)


📡 벤치마크 대상 서버 선택:
  → 1. spark-test: Spark GPU 서버 (DGX 테스트용)
    2. titan-test: Titan GPU 서버 (A100x8)
    3. score-main: S-Core 메인 서버 (H200x8)

선택 (1-3) [기본값: 1]: ↵

🤖 테스트 모델 선택:
  → 1. qwen3-coder-30b: Qwen3 Coder 30B (코드 생성 특화)
    2. qwen3-4b: Qwen3 4B (경량 모델)
    3. llama-3.1-70b-fp8: Llama 3.1 70B FP8 (대용량)

선택 (1-3) [기본값: 1]: ↵

⚙️  워크로드 설정:
  → 1. 기본 설정 사용 (5분 고부하 테스트)
    2. 사전 정의된 워크로드 선택
    3. 커스텀 설정

선택 (1-3) [기본값: 1]: ↵

============================================================
📋 벤치마크 설정 확인
============================================================
  서버: spark-test - Spark GPU 서버
  모델: Qwen/Qwen3-Coder-30B-A3B-Instruct
  워크로드: 5분 고부하 성능 테스트
    - 시간: 300초 (5분)
    - RPS: 20 (초당 요청 수)
    - 동시성: 50
    - 예상 총 요청: 6,000개
    - 최대 토큰: 1024
    - Temperature: 0.7
    - 프롬프트 타입: medium
============================================================

시작하시겠습니까? (Y/n) [기본값: Y]: ↵

🚀 벤치마크 시작!

=== Starting workload: high-load-5min ===
Target: spark-test, Model: Qwen/Qwen3-Coder-30B-A3B-Instruct
Duration: 300s, RPS: 20, Concurrency: 50
Expected total requests: 6000

======================================================================
⏱️  진행: 120s / 300s (40.0%) | 요청: 2,400 / 6,000 | 남은 시간: 180s (3분 0초)
```

### CLI 모드 예시

```bash
# 10분 스트레스 테스트
$ python3 scripts/run_bench_interactive.py \
    --target spark-test \
    --model qwen3-coder-30b \
    --workload stress-test

============================================================
🚀 CLI 모드로 벤치마크 실행
============================================================
  서버: spark-test - Spark GPU 서버
  모델: Qwen/Qwen3-Coder-30B-A3B-Instruct
  워크로드: 스트레스 테스트 (10분)
    - 시간: 600초 (10분)
    - RPS: 50 (초당 요청 수)
    - 동시성: 100
    - 예상 총 요청: 30,000개

⏱️  진행: 480s / 600s (80.0%) | 요청: 24,000 / 30,000 | 남은 시간: 120s (2분 0초)

✅ 완료: 29,543개, 성공: 29,234개 (98.9%)

📊 다음 명령으로 결과를 분석하세요:
  python3 scripts/parse_metrics.py results/raw/bench_spark-test_qwen3-coder-30b_stress-test_20251107_143022.jsonl
```

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

#### 🖥️ CLI 모드 실행 (자동화/스크립트용)

```bash
# 가상환경 활성화
source venv/bin/activate

# 사전 정의된 워크로드 사용
python3 scripts/run_bench_interactive.py --target spark-test --model qwen3-coder-30b --workload high-load

# 커스텀 설정으로 실행
python3 scripts/run_bench_interactive.py --target spark-test --model qwen3-coder-30b --duration 600 --rps 50 --concurrency 100

# 도움말 보기
python3 scripts/run_bench_interactive.py --help
```

**파라미터:**
- `--target`: 대상 서버 이름 (spark-test, titan-test, score-main 등)
- `--model`: 모델 이름 (qwen3-coder-30b, llama-3.1-70b-fp8 등)
- `--workload`: 워크로드 이름 (low-load, medium-load, high-load, stress-test)
- `--duration`: 테스트 시간 (초)
- `--rps`: 초당 요청 수
- `--concurrency`: 동시 요청 수
- `--max-tokens`, `--temperature`, `--prompt-type`: 추가 옵션

#### 개별 스크립트 실행 (저수준 제어)

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

**프로젝트명:** Run Bench  
**작성자:** 이창연 (DevOps AI사업TF)  
**작성일:** 2025-11-07  
**라이선스:** MIT

## 기여

이슈 및 풀 리퀘스트 환영합니다!

---

**Note:** Run Bench는 S-CORE 내부 사용을 위해 개발되었습니다.
