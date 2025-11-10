#!/usr/bin/env python3
"""
대화형 LLM 벤치마크 실행 스크립트
기본값으로 엔터만 치면 5분 고부하 성능 테스트 실행

CLI 파라미터 지원:
  --target: 대상 서버 이름
  --model: 모델 이름
  --workload: 워크로드 이름
  --duration: 테스트 시간 (초)
  --rps: 초당 요청 수
  --concurrency: 동시 요청 수
  --max-tokens: 최대 토큰 수
"""

import asyncio
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

import httpx
import yaml

# run_bench 모듈 import
sys.path.insert(0, str(Path(__file__).parent))
from run_bench import LLMBenchmark


def print_header():
    """헤더 출력"""
    print("\n" + "="*60)
    print("🚀 LLM 벤치마크 대화형 실행")
    print("="*60)
    print("\n💡 팁: 엔터만 치면 기본값 사용 (5분 고부하 테스트)\n")


def load_configs(config_dir: Path):
    """설정 파일 로드"""
    with open(config_dir / "targets.yaml", 'r', encoding='utf-8') as f:
        targets = yaml.safe_load(f)
    with open(config_dir / "models.yaml", 'r', encoding='utf-8') as f:
        models = yaml.safe_load(f)
    with open(config_dir / "workloads.yaml", 'r', encoding='utf-8') as f:
        workloads = yaml.safe_load(f)
    return targets, models, workloads


async def fetch_litellm_models(base_url: str, api_key: str) -> list:
    """LiteLLM에서 실제 가동 중인 모델 목록 조회
    
    Args:
        base_url: LiteLLM API base URL (예: http://localhost:4000/v1)
        api_key: API 인증 키
        
    Returns:
        모델 ID 리스트. 실패 시 빈 리스트 반환
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            response = await client.get(f"{base_url}/models", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if 'data' in data:
                model_ids = [model.get('id') for model in data['data'] if model.get('id')]
                return model_ids
            return []
            
    except Exception as e:
        print(f"⚠️  LiteLLM 모델 목록 조회 실패: {e}")
        return []


def select_option(prompt: str, options: list, default_index: int = 0) -> tuple:
    """옵션 선택 (기본값 지원)"""
    print(f"\n{prompt}")
    for i, opt in enumerate(options):
        prefix = "→" if i == default_index else " "
        print(f"  {prefix} {i+1}. {opt['display']}")
    
    default_display = f"기본값: {default_index + 1}"
    choice = input(f"\n선택 (1-{len(options)}) [{default_display}]: ").strip()
    
    if not choice:
        return default_index, options[default_index]
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return idx, options[idx]
        else:
            print(f"⚠️  잘못된 선택입니다. 기본값 사용")
            return default_index, options[default_index]
    except ValueError:
        print(f"⚠️  잘못된 입력입니다. 기본값 사용")
        return default_index, options[default_index]


def input_with_default(prompt: str, default: any, value_type=str) -> any:
    """기본값이 있는 입력"""
    user_input = input(f"{prompt} [기본값: {default}]: ").strip()
    if not user_input:
        return default
    try:
        return value_type(user_input)
    except:
        print(f"⚠️  잘못된 입력입니다. 기본값 사용: {default}")
        return default


def parse_arguments():
    """CLI 인수 파싱"""
    parser = argparse.ArgumentParser(
        description="LLM 벤치마크 실행 (대화형 또는 CLI 모드)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 대화형 모드 (기본값)
  python3 run_bench_interactive.py
  
  # CLI 모드 - 기본 워크로드
  python3 run_bench_interactive.py --target spark-test --model qwen3-coder-30b --workload high-load
  
  # CLI 모드 - 커스텀 설정
  python3 run_bench_interactive.py --target spark-test --model qwen3-coder-30b --duration 600 --rps 50 --concurrency 100
        """
    )
    
    parser.add_argument("--target", help="대상 서버 이름")
    parser.add_argument("--model", help="모델 이름")
    parser.add_argument("--workload", help="워크로드 이름")
    parser.add_argument("--duration", type=int, help="테스트 시간 (초)")
    parser.add_argument("--rps", type=int, help="초당 요청 수")
    parser.add_argument("--concurrency", type=int, help="동시 요청 수")
    parser.add_argument("--max-tokens", type=int, help="최대 토큰 수")
    parser.add_argument("--temperature", type=float, help="Temperature (0.0-2.0)")
    parser.add_argument("--prompt-type", choices=['short', 'medium', 'long'], help="프롬프트 타입")
    
    return parser.parse_args()


async def run_with_cli_args(args, config_dir: Path, output_dir: Path):
    """CLI 인수로 벤치마크 실행"""
    targets, models, workloads = load_configs(config_dir)
    
    # 대상 서버 찾기
    target = next((t for t in targets['targets'] if t['name'] == args.target), None)
    if not target:
        print(f"❌ 오류: 대상 서버 '{args.target}'를 찾을 수 없습니다.")
        print(f"사용 가능한 서버: {', '.join(t['name'] for t in targets['targets'])}")
        sys.exit(1)
    
    # 모델 찾기
    model_info = next((m for m in models['models'] if m['name'] == args.model), None)
    if not model_info:
        print(f"❌ 오류: 모델 '{args.model}'을 찾을 수 없습니다.")
        print(f"사용 가능한 모델: {', '.join(m['name'] for m in models['models'])}")
        sys.exit(1)
    
    # 워크로드 설정
    if args.workload:
        # 기존 워크로드 사용
        workload = next((w for w in workloads['workloads'] if w['name'] == args.workload), None)
        if not workload:
            print(f"❌ 오류: 워크로드 '{args.workload}'를 찾을 수 없습니다.")
            print(f"사용 가능한 워크로드: {', '.join(w['name'] for w in workloads['workloads'])}")
            sys.exit(1)
        workload = workload.copy()
    else:
        # 커스텀 워크로드 생성
        if not args.duration or not args.rps:
            print("❌ 오류: 워크로드 이름 또는 duration/rps를 지정해야 합니다.")
            sys.exit(1)
        
        workload = {
            'name': 'custom',
            'description': 'CLI 커스텀 워크로드',
            'duration': args.duration,
            'rps': args.rps,
            'concurrency': args.concurrency or 50,
            'max_tokens': args.max_tokens or 2048,
            'temperature': args.temperature or 0.7,
            'prompt_type': args.prompt_type or 'medium'
        }
    
    # CLI 인수로 오버라이드
    if args.duration:
        workload['duration'] = args.duration
    if args.rps:
        workload['rps'] = args.rps
    if args.concurrency:
        workload['concurrency'] = args.concurrency
    if args.max_tokens:
        workload['max_tokens'] = args.max_tokens
    if args.temperature:
        workload['temperature'] = args.temperature
    if args.prompt_type:
        workload['prompt_type'] = args.prompt_type
    
    # 프롬프트 로드
    prompts = workloads['prompt_templates'][workload['prompt_type']]
    
    # 설정 확인
    print("\n" + "="*60)
    print("🚀 CLI 모드로 벤치마크 실행")
    print("="*60)
    print(f"  서버: {target['name']} - {target['description']}")
    print(f"  모델: {model_info['full_name']}")
    print(f"  워크로드: {workload.get('description', 'Custom')}")
    print(f"    - 시간: {workload['duration']}초 ({workload['duration']//60}분)")
    print(f"    - RPS: {workload['rps']} (초당 요청 수)")
    print(f"    - 동시성: {workload['concurrency']}")
    print(f"    - 예상 총 요청: {workload['duration'] * workload['rps']}개")
    print(f"    - 최대 토큰: {workload['max_tokens']}")
    print(f"    - Temperature: {workload['temperature']}")
    print(f"    - 프롬프트 타입: {workload['prompt_type']}")
    print("="*60 + "\n")
    
    # 벤치마크 실행
    benchmark = LLMBenchmark(config_dir, output_dir)
    
    await benchmark.run_workload(
        target,
        model_info['full_name'],
        workload,
        prompts
    )
    
    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"bench_{target['name']}_{model_info['name']}_{workload['name']}_{timestamp}.jsonl"
    benchmark.save_results(output_file)
    
    print("\n✅ 벤치마크 완료!")
    print(f"� 원시 데이터: {output_file}")
    
    # 자동으로 분석 및 보고서 생성
    print("\n📊 결과 분석 중...")
    generate_report(output_file)


async def main():
    """메인 함수"""
    config_dir = Path(__file__).parent.parent / "configs"
    output_dir = Path(__file__).parent.parent / "results" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # CLI 인수 파싱
    args = parse_arguments()
    
    # CLI 모드 vs 대화형 모드
    if args.target or args.model or args.workload or args.duration:
        # CLI 모드: 인수가 하나라도 있으면 CLI 모드
        await run_with_cli_args(args, config_dir, output_dir)
    else:
        # 대화형 모드
        await run_interactive(config_dir, output_dir)


async def run_interactive(config_dir: Path, output_dir: Path):
    """대화형 모드 실행"""
    print_header()
    
    targets, models, workloads = load_configs(config_dir)
    
    # 1. 서버 선택
    target_options = [
        {
            'name': t['name'],
            'data': t,
            'display': f"{t['name']}: {t['description']}"
        }
        for t in targets['targets']
    ]
    
    # Spark를 기본값으로 (인덱스 찾기)
    default_target_idx = next(
        (i for i, t in enumerate(target_options) if 'spark' in t['name'].lower()),
        0
    )
    
    _, selected_target = select_option(
        "📡 벤치마크 대상 서버 선택:",
        target_options,
        default_target_idx
    )
    target = selected_target['data']
    
    # 2. 모델 선택 - LiteLLM에서 실제 가동 중인 모델 조회
    print("\n🔍 LiteLLM에서 가동 중인 모델 조회 중...")
    available_models = await fetch_litellm_models(target['base_url'], target['api_key'])
    
    if available_models:
        # LiteLLM API로부터 모델 목록을 성공적으로 가져온 경우
        print(f"✅ {len(available_models)}개의 모델이 가동 중입니다.\n")
        
        model_options = []
        for model_id in available_models:
            # 모델 ID에서 간단한 표시 이름 생성
            display_name = model_id
            if '/' in model_id:
                display_name = model_id.split('/')[-1]
            
            model_options.append({
                'name': model_id,
                'data': {
                    'name': model_id.replace('/', '-'),  # 파일명에 사용할 수 있도록
                    'full_name': model_id,
                    'description': f'LiteLLM 가동 모델'
                },
                'display': f"{display_name} ({model_id})"
            })
        
        # 첫 번째 모델을 기본값으로
        default_model_idx = 0
        
    else:
        # LiteLLM API 조회 실패 시 기존 models.yaml 사용
        print("⚠️  LiteLLM 모델 목록을 가져올 수 없습니다. configs/models.yaml 사용\n")
        
        model_options = [
            {
                'name': m['name'],
                'data': m,
                'display': f"{m['name']}: {m['description']}"
            }
            for m in models['models']
        ]
        
        # qwen3-coder-30b를 기본값으로
        default_model_idx = next(
            (i for i, m in enumerate(model_options) if 'qwen3-coder-30b' in m['name']),
            0
        )
    
    _, selected_model = select_option(
        "🤖 테스트 모델 선택:",
        model_options,
        default_model_idx
    )
    model_info = selected_model['data']
    
    # 3. 워크로드 선택 또는 커스텀
    print("\n⚙️  워크로드 설정:")
    print("  → 1. 기본 설정 사용 (5분 고부하 테스트)")
    print("    2. 사전 정의된 워크로드 선택")
    print("    3. 커스텀 설정")
    
    workload_choice = input("\n선택 (1-3) [기본값: 1]: ").strip()
    
    if workload_choice == "3":
        # 커스텀 설정
        print("\n📝 커스텀 워크로드 설정:")
        duration = input_with_default("  테스트 시간 (초)", 300, int)
        rps = input_with_default("  초당 요청 수 (RPS)", 20, int)
        max_tokens = input_with_default("  최대 토큰 수", 1024, int)
        temperature = input_with_default("  Temperature", 0.7, float)
        
        prompt_types = ["short", "medium", "long"]
        print("\n  프롬프트 길이:")
        for i, pt in enumerate(prompt_types):
            prefix = "→" if i == 1 else " "
            print(f"    {prefix} {i+1}. {pt}")
        prompt_choice = input(f"  선택 (1-3) [기본값: 2 (medium)]: ").strip()
        
        if not prompt_choice or prompt_choice == "2":
            prompt_type = "medium"
        elif prompt_choice == "1":
            prompt_type = "short"
        elif prompt_choice == "3":
            prompt_type = "long"
        else:
            prompt_type = "medium"
        
        workload = {
            'name': 'custom',
            'description': f'커스텀 설정 ({duration}초, RPS:{rps})',
            'duration': duration,
            'rps': rps,
            'concurrency': min(rps * 10, 100),  # RPS의 10배 또는 최대 100
            'max_tokens': max_tokens,
            'temperature': temperature,
            'prompt_type': prompt_type
        }
        
    elif workload_choice == "2":
        # 사전 정의된 워크로드
        workload_options = [
            {
                'name': w['name'],
                'data': w,
                'display': f"{w['name']}: {w['description']} ({w['duration']}초, RPS:{w['rps']})"
            }
            for w in workloads['workloads']
        ]
        
        # high-load를 기본값으로
        default_workload_idx = next(
            (i for i, w in enumerate(workload_options) if 'high' in w['name']),
            1
        )
        
        _, selected_workload = select_option(
            "워크로드 선택:",
            workload_options,
            default_workload_idx
        )
        workload = selected_workload['data']
        
    else:
        # 기본값: 5분 고부하 테스트
        workload = {
            'name': 'high-load-5min',
            'description': '5분 고부하 성능 테스트',
            'duration': 300,
            'rps': 20,
            'concurrency': 50,
            'max_tokens': 1024,
            'temperature': 0.7,
            'prompt_type': 'medium'
        }
    
    # 프롬프트 로드
    prompts = workloads['prompt_templates'][workload['prompt_type']]
    
    # 설정 확인
    print("\n" + "="*60)
    print("📋 벤치마크 설정 확인")
    print("="*60)
    print(f"  서버: {target['name']} - {target['description']}")
    print(f"  모델: {model_info['full_name']}")
    print(f"  워크로드: {workload['description']}")
    print(f"    - 시간: {workload['duration']}초 ({workload['duration']//60}분)")
    print(f"    - RPS: {workload['rps']} (초당 요청 수)")
    print(f"    - 동시성: {workload['concurrency']}")
    print(f"    - 예상 총 요청: {workload['duration'] * workload['rps']}개")
    print(f"    - 최대 토큰: {workload['max_tokens']}")
    print(f"    - Temperature: {workload['temperature']}")
    print(f"    - 프롬프트 타입: {workload['prompt_type']}")
    print("="*60)
    
    confirm = input("\n시작하시겠습니까? (Y/n) [기본값: Y]: ").strip().lower()
    if confirm and confirm != 'y':
        print("\n❌ 취소되었습니다.")
        return
    
    print("\n🚀 벤치마크 시작!\n")
    
    # 벤치마크 실행
    benchmark = LLMBenchmark(config_dir, output_dir)
    
    await benchmark.run_workload(
        target,
        model_info['full_name'],
        workload,
        prompts
    )
    
    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"bench_{target['name']}_{model_info['name']}_{workload['name']}_{timestamp}.jsonl"
    benchmark.save_results(output_file)
    
    print("\n✅ 벤치마크 완료!")
    print(f"📁 원시 데이터: {output_file}")
    
    # 자동으로 분석 및 보고서 생성
    print("\n📊 결과 분석 중...")
    generate_report(output_file)


def generate_report(result_file: Path):
    """벤치마크 결과 분석 및 보고서 자동 생성"""
    project_root = result_file.parent.parent.parent
    scripts_dir = project_root / "scripts"
    summary_dir = project_root / "results" / "summary"
    reports_dir = project_root / "results" / "reports"
    
    summary_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. 통계 분석 (parse_metrics.py)
        print("  → 통계 계산 중...")
        result = subprocess.run(
            [sys.executable, str(scripts_dir / "parse_metrics.py"), str(result_file)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        
        # 2. 보고서 생성 (gen_report.py)
        print("  → 보고서 생성 중...")
        result = subprocess.run(
            [sys.executable, str(scripts_dir / "gen_report.py")],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        
        # 최종 결과 출력
        # 가장 최근 보고서 찾기
        report_files = sorted(reports_dir.glob("benchmark_report_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not report_files:
            # 구형 파일명도 확인
            report_files = list(reports_dir.glob("benchmark_report.md"))
        
        if report_files:
            report_file = report_files[0]
            print(f"\n✨ 보고서 생성 완료!")
            print(f"📄 보고서: {report_file}")
            
            # CSV 파일 찾기
            csv_files = list(summary_dir.glob("*.csv"))
            if csv_files:
                latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
                print(f"📊 통계 요약: {latest_csv}")
        
    except subprocess.CalledProcessError as e:
        print(f"\n⚠️  보고서 생성 중 오류 발생:")
        print(e.stderr)
        print(f"\n수동으로 실행하세요:")
        print(f"  python3 scripts/parse_metrics.py {result_file}")
        print(f"  python3 scripts/gen_report.py")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
