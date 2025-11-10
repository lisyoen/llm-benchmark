#!/usr/bin/env python3
"""
LLM 벤치마크 실행 스크립트
OpenAI 호환 API를 대상으로 비동기 부하 테스트를 수행합니다.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import sys

import httpx
import yaml

# GPU 모니터링 import (선택적)
sys.path.insert(0, str(Path(__file__).parent))
try:
    from gpu_monitor import GPUMonitor
    GPU_MONITORING_AVAILABLE = True
except ImportError:
    GPU_MONITORING_AVAILABLE = False


class LLMBenchmark:
    """LLM 벤치마크 실행 클래스"""
    
    def __init__(self, config_dir: Path, output_dir: Path, enable_gpu_monitoring: bool = True):
        self.config_dir = config_dir
        self.output_dir = output_dir
        self.results: List[Dict] = []
        self.gpu_monitor: Optional[GPUMonitor] = None
        self.enable_gpu_monitoring = enable_gpu_monitoring and GPU_MONITORING_AVAILABLE
        
        # GPU 모니터링 초기화
        if self.enable_gpu_monitoring:
            self.gpu_monitor = GPUMonitor(interval=1.0)
        
    def load_config(self, config_name: str) -> Dict:
        """설정 파일 로드"""
        config_path = self.config_dir / f"{config_name}.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    async def send_request(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        api_key: str,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict:
        """단일 요청 전송 및 지표 수집"""
        request_id = f"{int(time.time() * 1000000)}"
        start_time = time.time()
        ttft = None
        tokens_generated = 0
        
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True
            }
            
            async with client.stream(
                "POST",
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=300.0
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data.strip() == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            if ttft is None:
                                ttft = time.time() - start_time
                            
                            # 토큰 카운트 (실제로는 chunk에서 추출)
                            tokens_generated += 1
                            
                        except json.JSONDecodeError:
                            continue
            
            end_time = time.time()
            total_time = end_time - start_time
            
            return {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "ttft": ttft,
                "total_time": total_time,
                "tokens_generated": tokens_generated,
                "tokens_per_sec": tokens_generated / total_time if total_time > 0 else 0,
                "prompt_length": len(prompt),
                "error": None
            }
            
        except Exception as e:
            return {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "ttft": None,
                "total_time": time.time() - start_time,
                "tokens_generated": 0,
                "tokens_per_sec": 0,
                "prompt_length": len(prompt),
                "error": str(e)
            }
    
    async def run_workload(
        self,
        target: Dict,
        model: str,
        workload: Dict,
        prompts: List[str]
    ):
        """워크로드 실행 (동시성 지원, 진행 상황 표시 개선, GPU 모니터링)"""
        print(f"\n=== Starting workload: {workload['name']} ===")
        print(f"Target: {target['name']}, Model: {model}")
        print(f"Duration: {workload['duration']}s, RPS: {workload['rps']}, Concurrency: {workload['concurrency']}")
        
        total_requests = workload['duration'] * workload['rps']
        print(f"Expected total requests: {total_requests}")
        
        # GPU 모니터링 시작
        if self.gpu_monitor:
            self.gpu_monitor.start()
        
        print(f"\n{'='*70}")
        
        try:
            async with httpx.AsyncClient() as client:
                start_time = time.time()
                request_interval = 1.0 / workload['rps']
                tasks = []
                request_count = 0
                last_print_time = start_time
                
                # 요청 생성 루프
                while time.time() - start_time < workload['duration']:
                    # 프롬프트 선택 (라운드 로빈)
                    prompt = prompts[request_count % len(prompts)]
                    
                    # 비동기 요청 태스크 생성
                    task = asyncio.create_task(
                        self._send_and_record(
                            client,
                            target,
                            model,
                            prompt,
                            workload
                        )
                    )
                    tasks.append(task)
                    request_count += 1
                    
                    # 진행 상황 출력 (1초마다)
                    current_time = time.time()
                    if current_time - last_print_time >= 1.0:
                        elapsed = current_time - start_time
                        remaining = workload['duration'] - elapsed
                        progress = (elapsed / workload['duration']) * 100
                        
                        # GPU 상태 출력
                        if self.gpu_monitor:
                            self.gpu_monitor.print_current_status()
                            print()  # 줄바꿈
                        
                        print(f"\r⏱️  진행: {int(elapsed)}s / {workload['duration']}s "
                              f"({progress:.1f}%) | "
                              f"요청: {request_count:,} / {total_requests:,} | "
                              f"남은 시간: {int(remaining)}s ({int(remaining/60)}분 {int(remaining%60)}초)", 
                              end='', flush=True)
                        last_print_time = current_time
                    
                    # RPS 유지를 위한 대기
                    await asyncio.sleep(request_interval)
                
                # 최종 진행 상황
                print(f"\r⏱️  요청 생성 완료: {request_count:,}개 (100%)                                    ")
                
                # 모든 요청 완료 대기
                print(f"\n{'='*70}")
                print(f"⏳ 모든 요청 응답 대기 중... ({len(tasks):,}개)")
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 결과 수집
                for result in results:
                    if isinstance(result, dict):
                        self.results.append(result)
                
                # 최종 통계
                success_count = sum(1 for r in self.results if r['success'])
                print(f"✅ 완료: {len(self.results):,}개, 성공: {success_count:,}개 ({success_count/len(self.results)*100:.1f}%)")
                print(f"{'='*70}\n")
                
        finally:
            # GPU 모니터링 종료
            if self.gpu_monitor:
                self.gpu_monitor.stop()
    
    async def _send_and_record(
        self,
        client: httpx.AsyncClient,
        target: Dict,
        model: str,
        prompt: str,
        workload: Dict
    ) -> Dict:
        """요청 전송 및 결과 기록"""
        result = await self.send_request(
            client,
            target['base_url'],
            target['api_key'],
            model,
            prompt,
            workload['max_tokens'],
            workload['temperature']
        )
        
        result['workload'] = workload['name']
        result['model'] = model
        result['target'] = target['name']
        
        return result
    
    def save_results(self, output_file: Path):
        """결과를 JSONL과 CSV 형식으로 저장 (GPU 통계 포함)"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # JSONL 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in self.results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        print(f"\n✓ Results saved to: {output_file}")
        print(f"  Total requests: {len(self.results)}")
        success_count = sum(1 for r in self.results if r['success'])
        print(f"  Successful: {success_count} ({success_count/len(self.results)*100:.1f}%)")
        
        # CSV 저장
        csv_file = output_file.with_suffix('.csv')
        try:
            import pandas as pd
            df = pd.DataFrame(self.results)
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"✓ CSV saved to: {csv_file}")
        except Exception as e:
            print(f"⚠️  CSV 저장 실패: {e}")
        
        # GPU 통계 저장
        if self.gpu_monitor and self.gpu_monitor.snapshots:
            gpu_stats = self.gpu_monitor.get_statistics()
            if gpu_stats:
                gpu_file = output_file.parent / f"{output_file.stem}_gpu_stats.json"
                with open(gpu_file, 'w', encoding='utf-8') as f:
                    json.dump(gpu_stats, f, indent=2, ensure_ascii=False)
                print(f"✓ GPU stats saved to: {gpu_file}")
                
                # GPU 통계 요약 출력
                print(f"\n🎮 GPU 사용률 요약:")
                for gpu_key, stats in gpu_stats.items():
                    print(f"  {gpu_key.upper()}: "
                          f"평균 {stats['avg_utilization']:.1f}% | "
                          f"메모리 {stats['avg_memory_used']:.1f}GB | "
                          f"전력 {stats['avg_power']:.0f}W | "
                          f"온도 {stats['max_temperature']}°C")


async def main():
    parser = argparse.ArgumentParser(description="LLM Benchmark Runner")
    parser.add_argument("--target", default="localhost", help="Target name from targets.yaml")
    parser.add_argument("--model", required=True, help="Model name (LiteLLM에서 가동 중인 모델)")
    parser.add_argument("--workload", default="medium-load", help="Workload name from workloads.yaml")
    parser.add_argument("--config-dir", type=Path, default=Path("configs"), help="Config directory")
    parser.add_argument("--output-dir", type=Path, default=Path("results/raw"), help="Output directory")
    
    args = parser.parse_args()
    
    # 벤치마크 실행
    benchmark = LLMBenchmark(args.config_dir, args.output_dir)
    
    # 설정 로드
    targets_config = benchmark.load_config("targets")
    models_config = benchmark.load_config("models")
    workloads_config = benchmark.load_config("workloads")
    
    # 대상 찾기
    target = next((t for t in targets_config['targets'] if t['name'] == args.target), None)
    if not target:
        print(f"Error: Target '{args.target}' not found")
        return
    
    # 모델 찾기
    model_info = next((m for m in models_config['models'] if m['name'] == args.model), None)
    if not model_info:
        print(f"Error: Model '{args.model}' not found")
        return
    
    # 워크로드 찾기
    workload = next((w for w in workloads_config['workloads'] if w['name'] == args.workload), None)
    if not workload:
        print(f"Error: Workload '{args.workload}' not found")
        return
    
    # 프롬프트 가져오기 (difficulty 기반)
    difficulty = workload.get('difficulty', workload.get('prompt_type', 'medium'))
    prompts = workloads_config['prompt_templates'][difficulty]
    
    # 워크로드 실행
    await benchmark.run_workload(target, model_info['full_name'], workload, prompts)
    
    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = args.output_dir / f"bench_{args.target}_{args.model}_{args.workload}_{timestamp}.jsonl"
    benchmark.save_results(output_file)


if __name__ == "__main__":
    asyncio.run(main())
