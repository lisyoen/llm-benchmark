# 세션 관리자

## 현재 활성 세션
**세션 ID:** session-009-20251110-gpu-monitoring
**상태:** 완료
**일시:** 2025-11-10 (실시간 GPU 모니터링 통합)

---

## 전체 세션 목록

| 세션 ID | 제목 | 상태 | 일시 |
|---------|------|------|------|
| session-001-20251107-init | 프로젝트 초기 구성 | 완료 | 2025-11-07 |
| session-002-20251107-cli-params | CLI 파라미터 지원 추가 | 완료 | 2025-11-07 |
| session-003-20251107-auto-report | 자동 보고서 생성 기능 추가 | 완료 | 2025-11-07 |
| session-004-20251107-packaging | 패키징 및 설치 스크립트 추가 | 완료 | 2025-11-07 |
| session-005-20251110-model-list | LiteLLM 가동 모델 표시 기능 | 완료 | 2025-11-10 |
| session-006-20251110-remove-server-select | 서버 선택 단계 제거 | 완료 | 2025-11-10 |
| session-007-20251110-remove-models-yaml | models.yaml 파일 제거 | 완료 | 2025-11-10 |
| session-008-20251110-run-script | 간편 실행 스크립트 추가 | 완료 | 2025-11-10 |
| session-009-20251110-gpu-monitoring | 실시간 GPU 모니터링 통합 | 완료 | 2025-11-10 |

---

## 새 세션 생성 규칙

- 세션 ID 형식: `session-XXX-YYYYMMDD-description`
- XXX: 3자리 일련번호 (001부터 시작)
- YYYYMMDD: 날짜
- description: 작업 내용 간략 설명 (영문 소문자, 하이픈 구분)
- 각 세션은 `.github/sessions/` 디렉토리에 별도 파일로 관리
