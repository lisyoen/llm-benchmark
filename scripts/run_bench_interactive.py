#!/usr/bin/env python3
"""
대화형 LLM 벤치마크 실행 스크립트
기본값으로 엔터만 치면 5분 고부하 성능 테스트 실행
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

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


async def main():
    print_header()
    
    config_dir = Path("configs")
    output_dir = Path("results/raw")
    
    # 설정 로드
    targets_config, models_config, workloads_config = load_configs(config_dir)
    
    # 1. 서버 선택
    target_options = [
        {
            'name': t['name'],
            'data': t,
            'display': f"{t['name']}: {t['description']}"
        }
        for t in targets_config['targets']
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
    
    # 2. 모델 선택
    model_options = [
        {
            'name': m['name'],
            'data': m,
            'display': f"{m['name']}: {m['description']}"
        }
        for m in models_config['models']
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
            for w in workloads_config['workloads']
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
    prompts = workloads_config['prompt_templates'][workload['prompt_type']]
    
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
    print(f"\n📊 다음 명령으로 결과를 분석하세요:")
    print(f"  python3 scripts/parse_metrics.py {output_file}")
    print(f"  python3 scripts/gen_report.py")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
