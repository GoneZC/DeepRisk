#!/bin/bash

# DeepRisk分析服务多实例停止脚本

echo "=============================================="
echo "    DeepRisk分析服务多实例停止脚本"
echo "=============================================="
echo ""

echo "正在停止分析服务实例..."
docker stop analyze-service-1 analyze-service-2 analyze-service-3

echo "正在删除分析服务容器..."
docker rm analyze-service-1 analyze-service-2 analyze-service-3

echo ""
echo "分析服务多实例已停止！"
echo ""