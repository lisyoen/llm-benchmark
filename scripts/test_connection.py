#!/usr/bin/env python3
"""
서버 연결 테스트 스크립트
벤치마크 실행 전 서버 연결 및 API 동작을 간단히 확인합니다.
"""

import asyncio
import argparse
from pathlib import Path

import httpx
import yaml


async def test_connection(base_url: str, api_key: str, model: str):
    """서버 연결 및 간단한 응답 테스트"""
    print(f"\n{'='*60}")
    print(f"Testing connection to: {base_url}")
    print(f"Model: {model}")
    print(f"{'='*60}\n")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "안녕하세요! 간단히 인사해주세요."}],
        "max_tokens": 50,
        "temperature": 0.7,
        "stream": True
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("📡 Sending test request...")
            
            async with client.stream(
                "POST",
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                print(f"✅ Connection successful! (Status: {response.status_code})")
                
                if response.status_code == 200:
                    print("\n📝 Response preview:")
                    token_count = 0
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data.strip() == "[DONE]":
                                break
                            
                            try:
                                import json
                                chunk = json.loads(data)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        print(content, end='', flush=True)
                                        token_count += 1
                            except:
                                continue
                    
                    print(f"\n\n✅ Test completed successfully!")
                    print(f"   Tokens received: {token_count}")
                else:
                    print(f"❌ Error: HTTP {response.status_code}")
                    print(await response.aread())
                    
    except httpx.ConnectError as e:
        print(f"❌ Connection failed: {e}")
        print("   Check if the server is running and the URL is correct.")
    except httpx.TimeoutException:
        print(f"❌ Request timeout")
        print("   Server is not responding within 30 seconds.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print(f"\n{'='*60}\n")


async def main():
    parser = argparse.ArgumentParser(description="Test LLM server connection")
    parser.add_argument("--target", default="titan-test", help="Target name from targets.yaml")
    parser.add_argument("--model", help="Model name (override)")
    parser.add_argument("--config-dir", type=Path, default=Path("configs"), help="Config directory")
    
    args = parser.parse_args()
    
    # 설정 로드
    targets_path = args.config_dir / "targets.yaml"
    models_path = args.config_dir / "models.yaml"
    
    with open(targets_path, 'r', encoding='utf-8') as f:
        targets_config = yaml.safe_load(f)
    
    with open(models_path, 'r', encoding='utf-8') as f:
        models_config = yaml.safe_load(f)
    
    # 대상 찾기
    target = next((t for t in targets_config['targets'] if t['name'] == args.target), None)
    if not target:
        print(f"❌ Error: Target '{args.target}' not found in {targets_path}")
        print(f"\nAvailable targets:")
        for t in targets_config['targets']:
            print(f"  - {t['name']}: {t['description']}")
        return
    
    # 모델 결정
    if args.model:
        model_name = args.model
    else:
        # 기본 모델 사용
        default_model_name = models_config.get('default_model', models_config['models'][0]['name'])
        model_info = next((m for m in models_config['models'] if m['name'] == default_model_name), None)
        model_name = model_info['full_name'] if model_info else default_model_name
    
    # 연결 테스트
    await test_connection(target['base_url'], target['api_key'], model_name)


if __name__ == "__main__":
    asyncio.run(main())
