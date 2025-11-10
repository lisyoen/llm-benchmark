#!/bin/bash
# LLM 벤치마크 간편 실행 스크립트

# 스크립트 디렉토리 경로
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🚀 LLM 벤치마크 실행${NC}"
echo -e "${GREEN}========================================${NC}\n"

# 가상환경 존재 확인
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 가상환경이 없습니다.${NC}"
    echo -e "${YELLOW}먼저 설치 스크립트를 실행하세요:${NC}"
    echo -e "  bash install.sh\n"
    exit 1
fi

# 가상환경 활성화
echo -e "${YELLOW}📦 가상환경 활성화 중...${NC}"
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 가상환경 활성화 실패${NC}\n"
    exit 1
fi

echo -e "${GREEN}✅ 가상환경 활성화 완료${NC}\n"

# 인터랙티브 모드 실행
echo -e "${YELLOW}🎯 인터랙티브 모드로 벤치마크 시작...${NC}\n"
python3 scripts/run_bench_interactive.py "$@"

# 종료 코드 저장
EXIT_CODE=$?

# 가상환경 비활성화 (선택사항)
# deactivate

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✨ 벤치마크 완료!${NC}"
    echo -e "${GREEN}========================================${NC}\n"
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}  ❌ 벤치마크 실행 중 오류 발생${NC}"
    echo -e "${RED}========================================${NC}\n"
fi

exit $EXIT_CODE
