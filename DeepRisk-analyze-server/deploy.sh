#!/bin/bash

# DeepRisk分析服务部署脚本 (适用于WSL)

echo "========================================"
echo "    DeepRisk分析服务部署脚本 (WSL)"
echo "========================================"
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null
then
    echo "错误: 未检测到Docker，请先安装Docker"
    exit 1
fi

echo "检测到已运行的依赖服务:"
echo "  Nacos: host.docker.internal:8848"
echo "  Redis: host.docker.internal:6380"
echo "  RabbitMQ: host.docker.internal:5672"
echo ""

echo "开始构建并部署分析服务..."
echo ""

echo "1. 构建分析服务镜像..."
docker build -t deep-risk-analyze-service .

echo ""
echo "2. 启动分析服务容器..."
docker run -d \
  --name analyze-service \
  -p 8000:8000 \
  -e NACOS_SERVER_ADDR=host.docker.internal:8848 \
  -e REDIS_HOST=host.docker.internal \
  -e REDIS_PORT=6380 \
  -e RABBITMQ_HOST=host.docker.internal \
  -e SERVER_PORT=8000 \
  -e NACOS_SERVICE_NAME=analysis-service \
  --add-host=host.docker.internal:host-gateway \
  deep-risk-analyze-service

echo ""
echo "3. 等待服务启动..."
sleep 15

echo ""
echo "部署完成！"
echo ""
echo "服务访问地址:"
echo "  分析服务API: http://localhost:8000"
echo "  健康检查端点: http://localhost:8000/health"
echo ""
echo "管理命令:"
echo "  查看日志: docker logs -f analyze-service"
echo "  停止服务: docker stop analyze-service"
echo "  删除容器: docker rm analyze-service"
echo "  删除镜像: docker rmi deep-risk-analyze-service"
echo ""