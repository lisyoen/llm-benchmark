#!/bin/bash

# Run Bench 배포 패키지 생성 스크립트

set -e

# 버전: YYYYMMDD-BUILD
VERSION="$(date +%Y%m%d)-001"
PACKAGE_NAME="run-bench-${VERSION}"
BUILD_DIR="build_package"

echo "Run Bench 배포 패키지 생성 중..."

# 이전 빌드 디렉토리 제거
rm -rf ${BUILD_DIR}
mkdir -p ${BUILD_DIR}/${PACKAGE_NAME}

# 필요한 파일 복사
echo "파일 복사 중..."
cp -r scripts ${BUILD_DIR}/${PACKAGE_NAME}/
cp -r configs ${BUILD_DIR}/${PACKAGE_NAME}/
cp install.sh ${BUILD_DIR}/${PACKAGE_NAME}/
cp requirements.txt ${BUILD_DIR}/${PACKAGE_NAME}/
cp README.md ${BUILD_DIR}/${PACKAGE_NAME}/
cp LICENSE ${BUILD_DIR}/${PACKAGE_NAME}/

# 결과 디렉토리 구조만 생성
mkdir -p ${BUILD_DIR}/${PACKAGE_NAME}/results/{raw,summary,reports}

# .gitkeep 파일 생성 (빈 디렉토리 유지용)
touch ${BUILD_DIR}/${PACKAGE_NAME}/results/raw/.gitkeep
touch ${BUILD_DIR}/${PACKAGE_NAME}/results/summary/.gitkeep
touch ${BUILD_DIR}/${PACKAGE_NAME}/results/reports/.gitkeep

# tar.gz 생성
echo "압축 중..."
cd ${BUILD_DIR}
tar -czf ../${PACKAGE_NAME}.tar.gz ${PACKAGE_NAME}/
cd ..

# 빌드 디렉토리 제거
rm -rf ${BUILD_DIR}

echo "완료! ${PACKAGE_NAME}.tar.gz 생성됨"
echo ""
echo "배포 방법:"
echo "1. tar.gz 파일을 대상 서버로 전송"
echo "2. tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "3. cd ${PACKAGE_NAME}"
echo "4. ./install.sh"
