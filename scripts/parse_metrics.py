#!/usr/bin/env python3
"""
벤치마크 결과 파싱 및 통계 계산 스크립트
JSONL 형식의 원시 데이터를 읽어 통계 지표를 계산하고 CSV로 저장합니다.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List
import statistics

import pandas as pd


class MetricsParser:
    """벤치마크 결과 파싱 및 통계 계산 클래스"""
    
    def __init__(self):
        self.results: List[Dict] = []
        
    def load_results(self, result_file: Path):
        """JSONL 파일에서 결과 로드"""
        with open(result_file, 'r', encoding='utf-8') as f:
            for line in f:
                self.results.append(json.loads(line))
        print(f"Loaded {len(self.results)} results from {result_file}")
    
    def calculate_statistics(self) -> Dict:
        """통계 지표 계산"""
        successful = [r for r in self.results if r['success']]
        
        if not successful:
            return {"error": "No successful requests"}
        
        ttfts = [r['ttft'] for r in successful if r['ttft'] is not None]
        total_times = [r['total_time'] for r in successful]
        tokens_per_sec = [r['tokens_per_sec'] for r in successful]
        
        stats = {
            # 기본 정보
            "total_requests": len(self.results),
            "successful_requests": len(successful),
            "failed_requests": len(self.results) - len(successful),
            "success_rate": len(successful) / len(self.results) * 100,
            
            # TTFT (Time To First Token)
            "ttft_mean": statistics.mean(ttfts) if ttfts else None,
            "ttft_median": statistics.median(ttfts) if ttfts else None,
            "ttft_p95": self._percentile(ttfts, 95) if ttfts else None,
            "ttft_p99": self._percentile(ttfts, 99) if ttfts else None,
            
            # 총 응답 시간
            "total_time_mean": statistics.mean(total_times),
            "total_time_median": statistics.median(total_times),
            "total_time_p95": self._percentile(total_times, 95),
            "total_time_p99": self._percentile(total_times, 99),
            
            # 토큰 처리량
            "tokens_per_sec_mean": statistics.mean(tokens_per_sec),
            "tokens_per_sec_median": statistics.median(tokens_per_sec),
            "tokens_per_sec_p95": self._percentile(tokens_per_sec, 95),
            
            # 총 토큰 수
            "total_tokens_generated": sum(r['tokens_generated'] for r in successful),
        }
        
        # 메타데이터 (첫 번째 결과에서 추출)
        if successful:
            stats['target'] = successful[0].get('target', 'unknown')
            stats['model'] = successful[0].get('model', 'unknown')
            stats['workload'] = successful[0].get('workload', 'unknown')
        
        return stats
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """백분위수 계산"""
        if not data:
            return None
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def save_summary(self, stats: Dict, output_file: Path):
        """통계를 CSV 파일로 저장"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # DataFrame으로 변환
        df = pd.DataFrame([stats])
        
        # CSV 저장
        df.to_csv(output_file, index=False)
        print(f"\n✓ Summary saved to: {output_file}")
        
    def print_summary(self, stats: Dict):
        """통계 요약 출력"""
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60)
        
        if "error" in stats:
            print(f"Error: {stats['error']}")
            return
        
        print(f"\nTarget: {stats.get('target', 'N/A')}")
        print(f"Model: {stats.get('model', 'N/A')}")
        print(f"Workload: {stats.get('workload', 'N/A')}")
        
        print(f"\n--- Request Statistics ---")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Successful: {stats['successful_requests']} ({stats['success_rate']:.1f}%)")
        print(f"Failed: {stats['failed_requests']}")
        
        print(f"\n--- TTFT (Time To First Token) ---")
        print(f"Mean: {stats['ttft_mean']:.3f}s")
        print(f"Median: {stats['ttft_median']:.3f}s")
        print(f"P95: {stats['ttft_p95']:.3f}s")
        print(f"P99: {stats['ttft_p99']:.3f}s")
        
        print(f"\n--- Total Response Time ---")
        print(f"Mean: {stats['total_time_mean']:.3f}s")
        print(f"Median: {stats['total_time_median']:.3f}s")
        print(f"P95: {stats['total_time_p95']:.3f}s")
        print(f"P99: {stats['total_time_p99']:.3f}s")
        
        print(f"\n--- Token Throughput ---")
        print(f"Mean: {stats['tokens_per_sec_mean']:.1f} tokens/s")
        print(f"Median: {stats['tokens_per_sec_median']:.1f} tokens/s")
        print(f"P95: {stats['tokens_per_sec_p95']:.1f} tokens/s")
        print(f"Total Tokens: {stats['total_tokens_generated']}")
        
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Parse benchmark results and calculate statistics")
    parser.add_argument("result_file", type=Path, help="Path to JSONL result file")
    parser.add_argument("--output", type=Path, help="Output CSV file (optional)")
    
    args = parser.parse_args()
    
    # 결과 파싱
    parser_obj = MetricsParser()
    parser_obj.load_results(args.result_file)
    
    # 통계 계산
    stats = parser_obj.calculate_statistics()
    
    # 출력
    parser_obj.print_summary(stats)
    
    # CSV 저장 (옵션)
    if args.output:
        parser_obj.save_summary(stats, args.output)
    else:
        # 기본 출력 경로
        default_output = Path("results/summary") / f"{args.result_file.stem}_summary.csv"
        parser_obj.save_summary(stats, default_output)


if __name__ == "__main__":
    main()
