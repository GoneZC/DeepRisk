#!/bin/bash

# DeepRisk分析服务停止脚本

echo "========================================"
echo "    DeepRisk分析服务停止脚本"
echo "========================================"
echo ""

echo "正在停止分析服务..."
docker stop analyze-service

echo "正在删除分析服务容器..."
docker rm analyze-service

echo ""
echo "分析服务已停止！"
echo ""