# llm-benchmark 프로젝트 목표

## 1. 개요
`llm-benchmark`는 GPU 서버 환경에서 **LLM 성능을 자동 측정**하기 위한 내부용 벤치마크 도구입니다.  
이 도구는 S-CORE의 **LLM Run Package** 구성 요소(vLLM, LiteLLM, Prometheus, Grafana 등)를 대상으로  
지연시간, 처리량, 안정성, 효율성 등을 자동 측정하고 리포트를 생성하는 것을 목표로 합니다.

---

## 2. 주요 목표

### 2.1 자동화된 LLM 워크로드 측정
- OpenAI 호환 API(`/v1/chat/completions`)를 대상으로 실제 사용 패턴 기반 부하를 생성  
- 요청 단위로 **TTFT(첫 토큰 지연시간)**, **응답 완료시간**, **토큰 처리량(tokens/sec)**, **성공률** 등을 기록  
- 워크로드 구성은 `workloads.yaml`로 관리 (RPS, 동시성, 프롬프트 유형 등)

### 2.2 결과 집계 및 리포트 생성
- 벤치 결과(JSONL)를 자동 집계하여 모델·워크로드별 지표를 CSV/Markdown 리포트로 변환  
- 성능 변화 추이를 시각화(향후 Grafana 연동 또는 HTML 보고서로 확장)

### 2.3 GPU 리소스 효율 분석 (확장 목표)
- Prometheus로부터 GPU 메트릭(nvidia-smi exporter 등)을 수집하여  
  전력 소비, 메모리 사용률, SM Util 기반의 **토큰당 효율(Tokens/W)** 계산  
- 성능/전력 효율 비교 리포트 생성

---

## 3. 구성 계획

```
scripts/
 ├─ run_bench.py      # 비동기 부하 테스트 실행
 ├─ parse_metrics.py  # 결과 집계 및 통계 계산
 ├─ gen_report.py     # 리포트 자동 생성
 └─ run_bench.sh      # 전체 실행 파이프라인 스크립트
configs/
 ├─ targets.yaml      # 벤치 대상 엔드포인트 정의
 ├─ models.yaml       # 테스트 모델 목록
 └─ workloads.yaml    # 요청 패턴 설정
results/
 ├─ raw/              # 원시 측정 로그(JSONL)
 ├─ summary/          # 통계 요약(CSV)
 └─ reports/          # 리포트(Markdown/HTML)
```

---

## 4. 기술 스택
- **언어:** Python 3.11+
- **라이브러리:** httpx, asyncio, pyyaml, pandas
- **지원 환경:**  
  - 로컬 실행 (개별 서버)
  - GitHub Actions (Self-hosted GPU Runner)
- **벤치 대상:** vLLM / LiteLLM / OpenAI 호환 API

---

## 5. 산출물
- **정량 지표:** TTFT, 평균 응답시간, 토큰 처리량, 성공률
- **정성 지표:** GPU 리소스 효율, 안정성(에러율), 응답 일관성
- **보고서:** Markdown 기반 성능 리포트 (필요 시 PDF/HTML 변환 가능)

---

## 6. 향후 계획
- Workload Generator 모듈을 별도 패키지화하여 재사용 가능하게 구조화
- Prometheus/Grafana 연동 자동화 스크립트 추가
- 여러 모델 간 비교 리포트 및 시각화 기능 확장
- CI 파이프라인 내 벤치마크 검증 단계 자동화

---

**작성일:** 2025-11-07  
**작성자:** 이창연 (AI사업그룹)
