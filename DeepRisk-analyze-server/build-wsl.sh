#!/bin/bash

# DeepRisk分析服务WSL快速构建脚本

echo "========================================"
echo "    WSL环境快速构建脚本"
echo "========================================"
echo ""

echo "构建环境: WSL Docker"
echo "服务类型: Python FastAPI"
echo ""

echo "1. 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

echo "✓ Python环境检查完成"
echo ""
echo "2. 检查依赖文件..."
if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到requirements.txt"
    exit 1
fi

echo "✓ 依赖文件检查完成"
echo ""
echo "3. 构建Docker镜像..."
docker build -t deep-risk-analyze-service:wsl . -q
if [ $? -ne 0 ]; then
    echo "错误: Docker构建失败"
    exit 1
fi

echo "✓ 镜像构建完成"
echo ""
echo "========================================"
echo "构建成功！"
echo "========================================"
echo ""
echo "构建信息:"
echo "  环境: WSL"
echo "  服务类型: Python FastAPI"
echo "  Docker镜像: deep-risk-analyze-service:wsl"
echo "  基础镜像: python:3.9-slim"
echo ""
echo "下一步:"
echo "  运行单实例: ./deploy.sh"
echo "  运行多实例: ./deploy-multi.sh"
echo ""