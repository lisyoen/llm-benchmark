#!/usr/bin/env python3
"""
LiteLLM 설정에서 모델 목록을 자동으로 가져오는 스크립트
"""

import yaml
import sys
from pathlib import Path

LITELLM_CONFIG_PATH = "/home/score/llmrp/docker-compose/litellm/litellm_config.yaml"

def load_litellm_models():
    """LiteLLM 설정에서 모델 목록 추출"""
    try:
        with open(LITELLM_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        models = []
        model_list = config.get('model_list', [])
        
        for model_config in model_list:
            model_name = model_config.get('model_name', '')
            if model_name:
                # 주석 처리된 모델은 제외
                models.append({
                    'name': model_name.split('/')[-1],  # 짧은 이름
                    'full_name': model_name,
                    'api_base': model_config.get('litellm_params', {}).get('api_base', ''),
                })
        
        return models
    
    except FileNotFoundError:
        print(f"❌ LiteLLM 설정 파일을 찾을 수 없습니다: {LITELLM_CONFIG_PATH}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"❌ LiteLLM 설정 로드 실패: {e}", file=sys.stderr)
        return []

def get_available_models():
    """사용 가능한 모델 목록 반환 (Run Bench용)"""
    models = load_litellm_models()
    
    if not models:
        print("⚠️  LiteLLM에서 모델을 가져올 수 없습니다. 기본 설정을 사용합니다.", file=sys.stderr)
        return []
    
    return models

if __name__ == "__main__":
    models = load_litellm_models()
    
    if models:
        print(f"\n📋 LiteLLM에서 {len(models)}개 모델 발견:\n")
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model['full_name']}")
            print(f"     서버: {model['api_base']}")
    else:
        print("\n❌ 사용 가능한 모델이 없습니다.")
        sys.exit(1)
