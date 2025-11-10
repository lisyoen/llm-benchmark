# 현재 작업 세션

## 현재 세션 정보
**세션 ID:** session-011-20251110-coding-difficulty-prompts  
**제목:** AI Code Agent 테스트를 위한 코딩 난이도별 프롬프트 재구성  
**상태:** 완료  
**시작 일시:** 2025-11-10

---

## 작업 요약
프롬프트를 "길이별" → "코딩 난이도별"로 재구성하여 AI Code Agent 성능 평가에 최적화

**주요 변경사항:**
1. workloads.yaml: prompt_type → difficulty (easy/medium/hard)
2. 프롬프트 템플릿 전면 재작성 (12개)
   - Easy: 간단한 함수, 기초 디버깅 (5개)
   - Medium: API 구현, 알고리즘 문제 (4개)
   - Hard: 복잡한 시스템 설계 (3개)
3. 스크립트 코드 업데이트 (run_bench.py, run_bench_interactive.py)
4. README 프롬프트 예시 변경
5. 하위 호환성 유지 (prompt_type → difficulty fallback)

---

## 다음에 해야 할 작업
- 없음 (작업 완료)

---

## 동기화 상태
**마지막 동기화:** 대기 중  
**상태:** 동기화 완료
