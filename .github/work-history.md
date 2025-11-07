# 작업 히스토리

이 파일은 완료된 세션들의 아카이브입니다.

---

## Session 001: 프로젝트 초기 구성
**세션 ID:** session-001-20251107-init  
**일시:** 2025-11-07  
**상태:** 완료

### 작업 내용
프로젝트 기본 구조 및 파일 생성

### 생성된 파일
- `.github/session-manager.md` - 세션 관리 문서
- `.github/current-session.md` - 현재 세션 상태
- `.github/project-context.md` - 프로젝트 컨텍스트
- `.github/work-history.md` - 작업 히스토리
- `scripts/run_bench.py` - 벤치마크 실행 스크립트
- `scripts/parse_metrics.py` - 결과 파싱 스크립트
- `scripts/gen_report.py` - 리포트 생성 스크립트
- `scripts/run_bench.sh` - 전체 파이프라인 스크립트
- `configs/targets.yaml` - 대상 엔드포인트 설정
- `configs/models.yaml` - 모델 목록 설정
- `configs/workloads.yaml` - 워크로드 패턴 설정
- `README.md` - 프로젝트 문서
- `requirements.txt` - Python 의존성

### 디렉토리 구조
```
scripts/
├── run_bench.py
├── parse_metrics.py
├── gen_report.py
└── run_bench.sh
configs/
├── targets.yaml
├── models.yaml
└── workloads.yaml
results/
├── raw/
├── summary/
└── reports/
```

### 주요 결정사항
1. Python 3.11+ 기반 비동기 부하 테스트 구조
2. YAML 기반 설정 관리
3. JSONL → CSV → Markdown 리포트 파이프라인
4. httpx를 사용한 비동기 HTTP 요청
5. 세션 기반 작업 추적 시스템 도입

### 다음 단계
- [ ] Python 의존성 설치 테스트
- [ ] vLLM 또는 LiteLLM 서버 설정
- [ ] 실제 벤치마크 실행 및 검증
- [ ] GPU 메트릭 수집 기능 추가 (Phase 2)

---

**히스토리 시작일:** 2025-11-07
