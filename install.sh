#!/bin/bash

set -e  # 에러 발생 시 즉시 종료

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 헤더 출력
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Run Bench 설치 스크립트${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 설치 위치 확인 및 이동
REQUIRED_PATH="$HOME/llmrp/llm-benchmark"

if [ "$PWD" != "$REQUIRED_PATH" ]; then
    echo -e "${YELLOW}Run Bench는 ~/llmrp/llm-benchmark에 설치되어야 합니다.${NC}"
    echo -e "${BLUE}현재 위치: $PWD${NC}"
    echo -e "${BLUE}필요 위치: $REQUIRED_PATH${NC}"
    echo ""
    
    # ~/llmrp 디렉토리가 없으면 생성
    if [ ! -d "$HOME/llmrp" ]; then
        echo -e "${YELLOW}~/llmrp 디렉토리를 생성합니다...${NC}"
        mkdir -p "$HOME/llmrp"
    fi
    
    # 대상 디렉토리가 이미 존재하는지 확인
    if [ -d "$REQUIRED_PATH" ]; then
        echo -e "${RED}오류: $REQUIRED_PATH가 이미 존재합니다.${NC}"
        echo "기존 설치를 삭제하거나 다른 위치에서 실행하세요."
        exit 1
    fi
    
    # 현재 디렉토리를 올바른 위치로 이동
    echo -e "${YELLOW}현재 디렉토리를 $REQUIRED_PATH로 이동합니다...${NC}"
    mv "$PWD" "$REQUIRED_PATH"
    cd "$REQUIRED_PATH"
    echo -e "${GREEN}✓ 이동 완료${NC}"
    echo ""
fi

echo -e "${GREEN}✓ 설치 위치 확인: $PWD${NC}"
echo ""

# sudo 권한 확인 함수
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        echo -e "${YELLOW}일부 패키지 설치를 위해 sudo 권한이 필요할 수 있습니다.${NC}"
        return 1
    fi
    return 0
}

# 시스템 의존성 확인 및 설치
echo -e "${YELLOW}[1/9] 시스템 의존성 확인...${NC}"

# OS 확인
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo -e "${RED}오류: 지원하지 않는 운영체제입니다.${NC}"
    exit 1
fi

# 필수 패키지 확인 및 설치
MISSING_PACKAGES=()

# Python 3.11+ 확인
if ! command -v python3 &> /dev/null; then
    MISSING_PACKAGES+=("python3")
fi

# python3-venv 확인
if ! python3 -m venv --help &> /dev/null 2>&1; then
    MISSING_PACKAGES+=("python3-venv")
fi

# pip 확인
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null 2>&1; then
    MISSING_PACKAGES+=("python3-pip")
fi

# git 확인
if ! command -v git &> /dev/null; then
    MISSING_PACKAGES+=("git")
fi

# 누락된 패키지 설치
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}누락된 패키지: ${MISSING_PACKAGES[*]}${NC}"
    echo -e "${BLUE}필수 패키지를 설치하시겠습니까? (y/N)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        case $OS in
            ubuntu|debian)
                echo -e "${YELLOW}apt를 사용하여 패키지 설치 중...${NC}"
                sudo apt update
                sudo apt install -y "${MISSING_PACKAGES[@]}"
                ;;
            centos|rhel|fedora)
                echo -e "${YELLOW}yum/dnf를 사용하여 패키지 설치 중...${NC}"
                if command -v dnf &> /dev/null; then
                    sudo dnf install -y "${MISSING_PACKAGES[@]}"
                else
                    sudo yum install -y "${MISSING_PACKAGES[@]}"
                fi
                ;;
            *)
                echo -e "${RED}오류: 자동 설치를 지원하지 않는 OS입니다.${NC}"
                echo "다음 패키지를 수동으로 설치해주세요: ${MISSING_PACKAGES[*]}"
                exit 1
                ;;
        esac
        echo -e "${GREEN}✓ 시스템 패키지 설치 완료${NC}"
    else
        echo -e "${RED}필수 패키지가 설치되지 않았습니다. 설치를 중단합니다.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ 모든 시스템 의존성이 설치되어 있습니다${NC}"
fi
echo ""

# Python 버전 확인
echo -e "${YELLOW}[2/9] Python 버전 확인...${NC}"
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}오류: Python 3.11 이상이 필요합니다. (현재: $PYTHON_VERSION)${NC}"
    echo ""
    echo "Python 3.11 이상을 설치하는 방법:"
    echo "  Ubuntu/Debian: sudo apt install python3.11"
    echo "  CentOS/RHEL: sudo yum install python3.11"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION 확인됨${NC}"
echo ""

# 가상환경 생성
echo -e "${YELLOW}[3/9] 가상환경 생성 중...${NC}"
if [ -d "venv" ]; then
    echo "기존 venv 디렉토리가 존재합니다. 삭제 후 재생성하시겠습니까? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓ 가상환경 재생성 완료${NC}"
    else
        echo "기존 가상환경을 사용합니다."
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓ 가상환경 생성 완료${NC}"
fi
echo ""

# 가상환경 활성화
echo -e "${YELLOW}[4/9] 가상환경 활성화...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ 가상환경 활성화 완료${NC}"
echo ""

# pip 업그레이드
echo -e "${YELLOW}[5/9] pip 업그레이드 중...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip 업그레이드 완료${NC}"
echo ""

# 의존성 설치
echo -e "${YELLOW}[6/9] 의존성 패키지 설치 중...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ 의존성 설치 완료${NC}"
else
    echo -e "${YELLOW}requirements.txt가 없습니다. 직접 설치...${NC}"
    pip install httpx>=0.27.0 pyyaml>=6.0.1 pandas>=2.2.0
    echo -e "${GREEN}✓ 기본 의존성 설치 완료${NC}"
fi
echo ""

# 디렉토리 구조 생성
echo -e "${YELLOW}[7/8] 디렉토리 구조 생성 중...${NC}"
mkdir -p results/raw
mkdir -p results/summary
mkdir -p results/reports
mkdir -p configs
mkdir -p scripts

echo -e "${GREEN}✓ 디렉토리 구조 생성 완료${NC}"
echo ""

# 설정 파일 확인
echo -e "${YELLOW}[8/8] 설정 파일 확인...${NC}"
if [ ! -f "configs/targets.yaml" ]; then
    echo -e "${YELLOW}⚠ configs/targets.yaml이 없습니다. 템플릿을 생성합니다.${NC}"
    cat > configs/targets.yaml << 'EOF'
# 벤치마크 대상 서버 설정
# 새 서버를 추가하려면 아래 형식으로 추가하세요

spark-test:
  url: "http://172.21.113.31:4000/v1/chat/completions"
  api_key: "sk--VGcWKuO_nquce9dMMc5IA"
  description: "Spark Test Server"

# 추가 서버 예시:
# my-server:
#   url: "http://your-server:port/v1/chat/completions"
#   api_key: "your-api-key-here"
#   description: "My Server Description"
EOF
fi

if [ ! -f "configs/workloads.yaml" ]; then
    echo -e "${YELLOW}⚠ configs/workloads.yaml이 없습니다. 템플릿을 생성합니다.${NC}"
    cat > configs/workloads.yaml << 'EOF'
# 워크로드 설정
# duration: 총 실행 시간 (초)
# rps: 초당 요청 수

low-load:
  duration: 60
  rps: 1
  description: "저부하 테스트 (1 RPS, 1분)"

medium-load:
  duration: 300
  rps: 5
  description: "중간부하 테스트 (5 RPS, 5분)"

high-load:
  duration: 300
  rps: 20
  description: "고부하 테스트 (20 RPS, 5분)"

stress-test:
  duration: 600
  rps: 50
  description: "스트레스 테스트 (50 RPS, 10분)"
EOF
fi

echo -e "${GREEN}✓ 설정 파일 확인 완료${NC}"
echo ""

# 완료 메시지
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  설치가 완료되었습니다!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}다음 단계:${NC}"
echo "1. 설정 파일을 수정하세요:"
echo "   - configs/targets.yaml (서버 설정)"
echo "   - configs/models.yaml (모델 설정)"
echo "   - configs/workloads.yaml (워크로드 설정)"
echo ""
echo "2. 가상환경을 활성화하세요:"
echo -e "   ${GREEN}source venv/bin/activate${NC}"
echo ""
echo "3. 벤치마크를 실행하세요:"
echo -e "   ${GREEN}python3 scripts/run_bench_interactive.py${NC}"
echo "   또는"
echo -e "   ${GREEN}python3 scripts/run_bench.py --target <target> --model <model> --workload <workload>${NC}"
echo ""
echo -e "${YELLOW}자세한 사용법은 README.md를 참고하세요.${NC}"
echo ""
