#!/usr/bin/env python3
"""
벤치마크 리포트 생성 스크립트
CSV 통계 파일을 읽어 Markdown 리포트를 생성합니다.
"""

import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

import pandas as pd


class ReportGenerator:
    """벤치마크 리포트 생성 클래스"""
    
    def __init__(self):
        self.summaries: List[pd.DataFrame] = []
        
    def load_summaries(self, summary_dir: Path):
        """요약 CSV 파일들을 로드"""
        csv_files = list(summary_dir.glob("*.csv"))
        
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            self.summaries.append(df)
        
        print(f"Loaded {len(self.summaries)} summary files")
    
    def generate_markdown_report(self, output_file: Path):
        """Markdown 리포트 생성"""
        if not self.summaries:
            print("No summaries to generate report")
            return
        
        # 모든 요약 통합
        combined_df = pd.concat(self.summaries, ignore_index=True)
        
        # Markdown 생성
        markdown = self._create_markdown_header()
        markdown += self._create_overview_section(combined_df)
        markdown += self._create_performance_section(combined_df)
        markdown += self._create_comparison_section(combined_df)
        markdown += self._create_recommendations_section(combined_df)
        
        # 파일 저장
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"\n✓ Report generated: {output_file}")
    
    def _create_markdown_header(self) -> str:
        """리포트 헤더 생성"""
        return f"""# LLM 벤치마크 리포트

**생성 일시:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

"""
    
    def _create_overview_section(self, df: pd.DataFrame) -> str:
        """개요 섹션 생성"""
        section = "## 1. 개요\n\n"
        
        section += f"- **총 테스트 수:** {len(df)}\n"
        section += f"- **테스트 대상:** {', '.join(df['target'].unique())}\n"
        section += f"- **테스트 모델:** {', '.join(df['model'].unique())}\n"
        section += f"- **워크로드:** {', '.join(df['workload'].unique())}\n\n"
        
        section += "---\n\n"
        return section
    
    def _create_performance_section(self, df: pd.DataFrame) -> str:
        """성능 지표 섹션 생성"""
        section = "## 2. 성능 지표\n\n"
        
        section += "### 2.1 TTFT (Time To First Token)\n\n"
        section += "| Target | Model | Workload | Mean (s) | Median (s) | P95 (s) | P99 (s) |\n"
        section += "|--------|-------|----------|----------|------------|---------|----------|\n"
        
        for _, row in df.iterrows():
            section += f"| {row['target']} | {row['model'][:30]}... | {row['workload']} | "
            section += f"{row['ttft_mean']:.3f} | {row['ttft_median']:.3f} | "
            section += f"{row['ttft_p95']:.3f} | {row['ttft_p99']:.3f} |\n"
        
        section += "\n### 2.2 총 응답 시간\n\n"
        section += "| Target | Model | Workload | Mean (s) | Median (s) | P95 (s) | P99 (s) |\n"
        section += "|--------|-------|----------|----------|------------|---------|----------|\n"
        
        for _, row in df.iterrows():
            section += f"| {row['target']} | {row['model'][:30]}... | {row['workload']} | "
            section += f"{row['total_time_mean']:.3f} | {row['total_time_median']:.3f} | "
            section += f"{row['total_time_p95']:.3f} | {row['total_time_p99']:.3f} |\n"
        
        section += "\n### 2.3 토큰 처리량\n\n"
        section += "| Target | Model | Workload | Mean (tokens/s) | Median (tokens/s) | P95 (tokens/s) |\n"
        section += "|--------|-------|----------|-----------------|-------------------|----------------|\n"
        
        for _, row in df.iterrows():
            section += f"| {row['target']} | {row['model'][:30]}... | {row['workload']} | "
            section += f"{row['tokens_per_sec_mean']:.1f} | {row['tokens_per_sec_median']:.1f} | "
            section += f"{row['tokens_per_sec_p95']:.1f} |\n"
        
        section += "\n### 2.4 성공률\n\n"
        section += "| Target | Model | Workload | Total | Success | Failed | Success Rate |\n"
        section += "|--------|-------|----------|-------|---------|--------|-------------|\n"
        
        for _, row in df.iterrows():
            section += f"| {row['target']} | {row['model'][:30]}... | {row['workload']} | "
            section += f"{int(row['total_requests'])} | {int(row['successful_requests'])} | "
            section += f"{int(row['failed_requests'])} | {row['success_rate']:.1f}% |\n"
        
        section += "\n---\n\n"
        return section
    
    def _create_comparison_section(self, df: pd.DataFrame) -> str:
        """비교 분석 섹션 생성"""
        section = "## 3. 비교 분석\n\n"
        
        # 가장 빠른 TTFT
        best_ttft = df.loc[df['ttft_mean'].idxmin()]
        section += f"### 3.1 최고 TTFT 성능\n\n"
        section += f"- **Target:** {best_ttft['target']}\n"
        section += f"- **Model:** {best_ttft['model']}\n"
        section += f"- **Workload:** {best_ttft['workload']}\n"
        section += f"- **Mean TTFT:** {best_ttft['ttft_mean']:.3f}s\n\n"
        
        # 가장 높은 처리량
        best_throughput = df.loc[df['tokens_per_sec_mean'].idxmax()]
        section += f"### 3.2 최고 처리량\n\n"
        section += f"- **Target:** {best_throughput['target']}\n"
        section += f"- **Model:** {best_throughput['model']}\n"
        section += f"- **Workload:** {best_throughput['workload']}\n"
        section += f"- **Mean Throughput:** {best_throughput['tokens_per_sec_mean']:.1f} tokens/s\n\n"
        
        section += "---\n\n"
        return section
    
    def _create_recommendations_section(self, df: pd.DataFrame) -> str:
        """권장사항 섹션 생성"""
        section = "## 4. 권장사항\n\n"
        
        # 낮은 성공률 경고
        low_success = df[df['success_rate'] < 95]
        if not low_success.empty:
            section += "### ⚠️ 낮은 성공률 경고\n\n"
            for _, row in low_success.iterrows():
                section += f"- **{row['target']} / {row['model']} / {row['workload']}**: "
                section += f"성공률 {row['success_rate']:.1f}% (목표: 95% 이상)\n"
            section += "\n"
        
        # 높은 지연시간 경고
        high_latency = df[df['ttft_p99'] > 2.0]
        if not high_latency.empty:
            section += "### ⚠️ 높은 지연시간 경고\n\n"
            for _, row in high_latency.iterrows():
                section += f"- **{row['target']} / {row['model']} / {row['workload']}**: "
                section += f"P99 TTFT {row['ttft_p99']:.3f}s (목표: 2s 이하)\n"
            section += "\n"
        
        section += "---\n\n"
        section += "*이 리포트는 자동 생성되었습니다.*\n"
        
        return section


def main():
    parser = argparse.ArgumentParser(description="Generate benchmark report")
    parser.add_argument("--summary-dir", type=Path, default=Path("results/summary"),
                       help="Directory containing summary CSV files")
    parser.add_argument("--output", type=Path, default=Path("results/reports/benchmark_report.md"),
                       help="Output Markdown file")
    
    args = parser.parse_args()
    
    # 리포트 생성
    generator = ReportGenerator()
    generator.load_summaries(args.summary_dir)
    generator.generate_markdown_report(args.output)


if __name__ == "__main__":
    main()
