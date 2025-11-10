#!/usr/bin/env python3
"""
GPU 모니터링 모듈
NVIDIA GPU의 실시간 사용률, 메모리, 전력, 온도를 추적합니다.
"""

import threading
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False


@dataclass
class GPUSnapshot:
    """GPU 상태 스냅샷"""
    timestamp: float
    gpu_id: int
    gpu_name: str
    utilization: int  # GPU 사용률 (%)
    memory_used: float  # 사용 중인 메모리 (GB)
    memory_total: float  # 전체 메모리 (GB)
    memory_percent: float  # 메모리 사용률 (%)
    power_usage: float  # 현재 전력 사용량 (W)
    power_limit: float  # 전력 제한 (W)
    temperature: int  # 온도 (°C)


class GPUMonitor:
    """GPU 실시간 모니터링 클래스"""
    
    def __init__(self, interval: float = 1.0):
        """
        Args:
            interval: 모니터링 간격 (초)
        """
        self.interval = interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.snapshots: List[GPUSnapshot] = []
        self.device_count = 0
        self.devices = []
        
        if not NVML_AVAILABLE:
            print("⚠️  경고: pynvml 패키지가 설치되지 않았습니다. GPU 모니터링이 비활성화됩니다.")
            print("   설치: pip install nvidia-ml-py3")
            return
        
        try:
            pynvml.nvmlInit()
            self.device_count = pynvml.nvmlDeviceGetCount()
            
            # 각 GPU의 핸들과 이름 저장
            for i in range(self.device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                # bytes인 경우 문자열로 변환
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                self.devices.append({
                    'id': i,
                    'handle': handle,
                    'name': name
                })
                
            print(f"✅ GPU 모니터링 초기화 완료: {self.device_count}개 GPU 감지")
            
        except Exception as e:
            print(f"⚠️  GPU 모니터링 초기화 실패: {e}")
            self.device_count = 0
    
    def start(self):
        """모니터링 시작"""
        if self.device_count == 0:
            return
        
        if self.running:
            print("⚠️  GPU 모니터링이 이미 실행 중입니다.")
            return
        
        self.running = True
        self.snapshots.clear()
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("🎮 GPU 모니터링 시작...")
    
    def stop(self):
        """모니터링 종료"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print(f"\n✅ GPU 모니터링 종료 (총 {len(self.snapshots)}개 스냅샷 수집)")
    
    def _monitor_loop(self):
        """모니터링 루프 (별도 스레드에서 실행)"""
        while self.running:
            try:
                for device in self.devices:
                    snapshot = self._get_gpu_snapshot(device['handle'], device['id'], device['name'])
                    if snapshot:
                        self.snapshots.append(snapshot)
                
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"\n⚠️  GPU 모니터링 오류: {e}")
                break
    
    def _get_gpu_snapshot(self, handle, gpu_id: int, gpu_name: str) -> Optional[GPUSnapshot]:
        """현재 GPU 상태를 가져옵니다"""
        try:
            # GPU 사용률 (지원되지 않는 경우 0으로 설정)
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                utilization = util.gpu
            except pynvml.NVMLError:
                utilization = 0
            
            # 메모리 정보
            try:
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                memory_used_gb = mem.used / (1024 ** 3)
                memory_total_gb = mem.total / (1024 ** 3)
                memory_percent = (mem.used / mem.total) * 100
            except pynvml.NVMLError:
                memory_used_gb = 0
                memory_total_gb = 0
                memory_percent = 0
            
            # 전력 사용량 (지원되지 않는 경우 0으로 설정)
            try:
                power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000  # mW -> W
            except pynvml.NVMLError:
                power_usage = 0
            
            try:
                power_limit = pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000
            except pynvml.NVMLError:
                power_limit = 0
            
            # 온도 (지원되지 않는 경우 0으로 설정)
            try:
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            except pynvml.NVMLError:
                temperature = 0
            
            return GPUSnapshot(
                timestamp=time.time(),
                gpu_id=gpu_id,
                gpu_name=gpu_name,
                utilization=utilization,
                memory_used=memory_used_gb,
                memory_total=memory_total_gb,
                memory_percent=memory_percent,
                power_usage=power_usage,
                power_limit=power_limit,
                temperature=temperature
            )
            
        except Exception as e:
            print(f"\n⚠️  GPU {gpu_id} 정보 수집 실패: {e}")
            return None
    
    def get_latest_snapshots(self) -> List[GPUSnapshot]:
        """각 GPU의 최신 스냅샷 반환"""
        if not self.snapshots:
            return []
        
        latest = {}
        for snapshot in reversed(self.snapshots):
            if snapshot.gpu_id not in latest:
                latest[snapshot.gpu_id] = snapshot
            
            if len(latest) == self.device_count:
                break
        
        return list(latest.values())
    
    def get_statistics(self) -> Dict:
        """수집된 스냅샷의 통계 계산"""
        if not self.snapshots:
            return {}
        
        stats = {}
        
        for gpu_id in range(self.device_count):
            gpu_snapshots = [s for s in self.snapshots if s.gpu_id == gpu_id]
            
            if not gpu_snapshots:
                continue
            
            stats[f"gpu_{gpu_id}"] = {
                "name": gpu_snapshots[0].gpu_name,
                "avg_utilization": sum(s.utilization for s in gpu_snapshots) / len(gpu_snapshots),
                "max_utilization": max(s.utilization for s in gpu_snapshots),
                "avg_memory_used": sum(s.memory_used for s in gpu_snapshots) / len(gpu_snapshots),
                "max_memory_used": max(s.memory_used for s in gpu_snapshots),
                "memory_total": gpu_snapshots[0].memory_total,
                "avg_power": sum(s.power_usage for s in gpu_snapshots) / len(gpu_snapshots),
                "max_power": max(s.power_usage for s in gpu_snapshots),
                "power_limit": gpu_snapshots[0].power_limit,
                "avg_temperature": sum(s.temperature for s in gpu_snapshots) / len(gpu_snapshots),
                "max_temperature": max(s.temperature for s in gpu_snapshots),
                "sample_count": len(gpu_snapshots)
            }
        
        return stats
    
    def print_current_status(self):
        """현재 GPU 상태를 출력 (한 줄)"""
        latest = self.get_latest_snapshots()
        if not latest:
            return
        
        # 한 줄로 모든 GPU 정보 출력
        status_parts = []
        for snapshot in sorted(latest, key=lambda s: s.gpu_id):
            # GPU 이름 간략화 (예: NVIDIA H200 -> H200)
            short_name = snapshot.gpu_name.replace("NVIDIA ", "").replace("Tesla ", "")
            
            status = (
                f"GPU{snapshot.gpu_id} ({short_name}): "
                f"{snapshot.utilization}% │ "
                f"{snapshot.memory_used:.1f}/{snapshot.memory_total:.0f}GB │ "
                f"{snapshot.power_usage:.0f}W │ "
                f"{snapshot.temperature}°C"
            )
            status_parts.append(status)
        
        # 줄바꿈으로 구분하여 출력
        print("\r" + " | ".join(status_parts), end="", flush=True)
    
    def __del__(self):
        """소멸자: NVML 종료"""
        if NVML_AVAILABLE and self.device_count > 0:
            try:
                pynvml.nvmlShutdown()
            except:
                pass


if __name__ == "__main__":
    """테스트 코드"""
    print("GPU 모니터링 테스트 시작...")
    
    monitor = GPUMonitor(interval=1.0)
    
    if monitor.device_count == 0:
        print("GPU를 찾을 수 없습니다.")
        exit(1)
    
    monitor.start()
    
    try:
        # 10초간 모니터링
        for i in range(10):
            time.sleep(1)
            monitor.print_current_status()
        
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    
    finally:
        monitor.stop()
        
        # 통계 출력
        stats = monitor.get_statistics()
        print("\n\n=== GPU 통계 ===")
        for gpu_key, gpu_stats in stats.items():
            print(f"\n{gpu_key.upper()} ({gpu_stats['name']}):")
            print(f"  평균 사용률: {gpu_stats['avg_utilization']:.1f}%")
            print(f"  최대 사용률: {gpu_stats['max_utilization']}%")
            print(f"  평균 메모리: {gpu_stats['avg_memory_used']:.1f}GB / {gpu_stats['memory_total']:.0f}GB")
            print(f"  평균 전력: {gpu_stats['avg_power']:.0f}W")
            print(f"  최대 온도: {gpu_stats['max_temperature']}°C")
