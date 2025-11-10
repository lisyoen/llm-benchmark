# 세션 009: 실시간 GPU 모니터링 통합

## 세션 정보
- **세션 ID:** session-009-20251110-gpu-monitoring
- **날짜:** 2025-11-10
- **상태:** 진행 중
- **담당자:** GitHub Copilot

---

## 작업 목적
벤치마크 실행 중 실시간 GPU 사용률 모니터링 기능 추가:
- 벤치마크 진행 중 GPU 메트릭 실시간 표시
- GPU 사용률, 메모리, 전력, 온도 등 주요 지표 출력
- 최종 보고서에 GPU 통계 포함

---

## 작업 계획

### 1단계: 구현 방안 결정
- [x] 방안 검토 (watch, Python 내장, TUI 대시보드)
- [ ] 최종 방안 선택 및 설계

### 2단계: GPU 모니터링 모듈 구현
- [ ] `pynvml` 라이브러리 추가
- [ ] GPU 정보 수집 함수 작성
- [ ] 별도 스레드에서 주기적 모니터링

### 3단계: 벤치마크 통합
- [ ] `run_bench.py`에 GPU 모니터링 통합
- [ ] 실시간 출력 포맷 개선
- [ ] GPU 메트릭 로그 저장

### 4단계: 보고서 개선
- [ ] GPU 사용률 그래프/통계 추가
- [ ] 성능-전력 효율 분석

### 5단계: 문서 및 테스트
- [ ] README.md 업데이트
- [ ] requirements.txt에 pynvml 추가
- [ ] 실제 GPU 환경에서 테스트
- [ ] Git 커밋 및 푸시

---

## 구현 방안 비교

### 방안 1: `watch nvidia-smi` 사용
**장점:**
- 구현 불필요 (이미 존재하는 도구)
- 익숙한 인터페이스

**단점:**
- 별도 터미널 필요 (tmux/screen 사용)
- 벤치마크와 분리된 화면
- 로그 저장 어려움

### 방안 2: Python 내장 모니터링 (추천!)
**장점:**
- 한 화면에서 모든 정보 확인
- GPU 메트릭을 로그에 저장 가능
- 최종 보고서에 통계 포함 가능
- 추가 터미널 불필요

**단점:**
- `pynvml` 패키지 추가 필요
- 코드 수정 필요

**구현 예시:**
```python
import pynvml
import threading
import time

class GPUMonitor:
    def __init__(self):
        pynvml.nvmlInit()
        self.device_count = pynvml.nvmlDeviceGetCount()
        self.running = False
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
    def _monitor_loop(self):
        while self.running:
            for i in range(self.device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                
                print(f"\r🎮 GPU {i}: {util.gpu}% | "
                      f"Mem: {mem.used/1024**3:.1f}/{mem.total/1024**3:.1f}GB | "
                      f"{power:.0f}W | {temp}°C", end="")
            
            time.sleep(1)
    
    def stop(self):
        self.running = False
```

### 방안 3: Rich TUI 대시보드
**장점:**
- 매우 보기 좋은 인터페이스
- 진행률 바, 테이블, 실시간 차트 등

**단점:**
- `rich` 라이브러리 추가 필요
- 복잡한 구현
- SSH 환경에서 렌더링 이슈 가능

---

## 최종 구현 모습 (방안 2)

```
============================================================
🚀 LLM 벤치마크 대화형 실행
============================================================

📡 대상 서버: localhost - 로컬 LiteLLM 서버
🤖 모델: Qwen/Qwen3-Coder-30B-A3B-Instruct
⚙️  워크로드: high-load (180초, RPS:20)

🚀 벤치마크 시작!

┌─────────────────────────────────────────────────────────┐
│ 🎮 GPU 모니터링                                         │
│ GPU 0 (H200): 87% | 메모리: 45.2/141GB | 420W | 65°C   │
│ GPU 1 (H200): 82% | 메모리: 42.8/141GB | 405W | 63°C   │
└─────────────────────────────────────────────────────────┘

⏱️  진행: 45s / 180s (25.0%)
📊 요청: 900 / 3600 | 성공: 850 (94.4%) | 실패: 50
📈 TTFT: 0.23s (평균) | 처리량: 125 tokens/s

[진행 중...]
```

**최종 보고서에 추가될 내용:**
```markdown
## GPU 사용률

| 메트릭 | GPU 0 | GPU 1 | 평균 |
|--------|-------|-------|------|
| 사용률 | 85.3% | 81.7% | 83.5% |
| 메모리 | 45.2GB | 42.8GB | 44.0GB |
| 평균 전력 | 418W | 402W | 410W |
| 최대 온도 | 68°C | 66°C | 67°C |

**전력 효율:** 0.305 tokens/W (125 tokens/s ÷ 410W)
```

---

## 진행 상황
- [x] 세션 파일 생성
- [x] 구현 방안 검토
- [x] 방안 선택 및 구현
- [x] 벤치마크 통합
- [x] 테스트
- [ ] Git 동기화

---

## 작업 결과

### ✅ 완료된 작업

#### 1. nvidia-ml-py3 패키지 추가
**파일:** `requirements.txt`
- `nvidia-ml-py3>=7.352.0` 추가

#### 2. GPU 모니터링 클래스 구현
**파일:** `scripts/gpu_monitor.py`

**주요 기능:**
- `GPUMonitor` 클래스: 실시간 GPU 메트릭 수집
- 별도 스레드에서 주기적 모니터링 (1초 간격)
- GPU 사용률, 메모리, 전력, 온도 추적
- 지원되지 않는 메트릭에 대한 graceful fallback
- 통계 계산 기능 (평균, 최대값 등)

**모니터링 정보:**
- GPU 사용률 (%)
- 메모리 사용량 (GB) 및 사용률 (%)
- 전력 사용량 (W)
- 온도 (°C)

#### 3. run_bench.py 통합
**변경사항:**
- `LLMBenchmark` 클래스에 GPU 모니터링 통합
- 벤치마크 시작 시 자동으로 GPU 모니터링 시작
- 벤치마크 종료 시 자동으로 GPU 모니터링 종료
- 실시간 GPU 상태를 진행 상황과 함께 출력
- GPU 통계를 JSON 파일로 저장

#### 4. 실행 결과 (테스트 성공!)
```
GPU0 (GB10): 93% │ 0.0/0GB │ 27W │ 48°C
⏱️  진행: 5s / 10s (50%) | 요청: 100 / 200 | 남은 시간: 5s (0분 5초)
```

**GPU 통계 저장:**
```
✓ GPU stats saved to: bench_..._gpu_stats.json

🎮 GPU 사용률 요약:
  GPU_0: 평균 92.8% | 메모리 0.0GB | 전력 28W | 온도 58°C
```

### 주요 개선 사항
- ✅ **실시간 모니터링**: 벤치마크 진행 중 GPU 상태 즉시 확인
- ✅ **자동 저장**: GPU 통계가 JSON 파일로 자동 저장
- ✅ **Graceful Degradation**: GPU가 없거나 메트릭이 지원되지 않아도 벤치마크 계속 진행
- ✅ **통합 인터페이스**: 별도 터미널 불필요, 한 화면에서 모든 정보 확인

### 변경된 파일 목록
1. `requirements.txt` - nvidia-ml-py3 추가
2. `scripts/gpu_monitor.py` - GPU 모니터링 모듈 신규 생성
3. `scripts/run_bench.py` - GPU 모니터링 통합

### 생성된 파일 형식
**GPU 통계 JSON 예시:**
```json
{
  "gpu_0": {
    "name": "NVIDIA GB10",
    "avg_utilization": 92.8,
    "max_utilization": 96,
    "avg_memory_used": 0.0,
    "max_memory_used": 0.0,
    "memory_total": 0,
    "avg_power": 28.2,
    "max_power": 30.0,
    "power_limit": 0,
    "avg_temperature": 48.5,
    "max_temperature": 58,
    "sample_count": 129
  }
}
```

---

## 학습한 내용 및 결정 사항

1. **NVML API의 제한사항**
   - 일부 GPU 메트릭은 드라이버나 하드웨어에 따라 지원되지 않을 수 있음
   - 에러 처리로 지원되지 않는 메트릭은 0으로 설정

2. **bytes vs string**
   - `pynvml.nvmlDeviceGetName()` 반환값이 bytes일 수 있음
   - UTF-8 디코딩으로 문자열 변환 필요

3. **스레드 기반 모니터링**
   - 비동기 벤치마크와 분리된 스레드에서 GPU 모니터링 수행
   - Daemon 스레드로 설정하여 메인 프로그램 종료 시 자동 종료

4. **사용자 경험**
   - 실시간 GPU 정보가 한 줄로 표시되어 깔끔함
   - 진행률과 GPU 상태를 동시에 확인 가능
