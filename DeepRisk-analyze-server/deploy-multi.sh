#!/bin/bash

# DeepRisk分析服务多实例部署脚本 (适用于WSL)

echo "=============================================="
echo "    DeepRisk分析服务多实例部署脚本 (WSL)"
echo "=============================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null
then
    echo "错误: 未检测到Docker，请先安装Docker"
    exit 1
fi

echo "检测到已运行的依赖服务:"
echo "  Nacos: localhost:8848 (WSL Docker)"
echo "  Redis: localhost:6380 (WSL Docker)"
echo "  RabbitMQ: localhost:5672 (WSL Docker)"
echo "  MySQL: 172.20.0.1:3306 (Windows主机)"
echo ""

echo "开始构建并部署分析服务多实例..."
echo ""

echo "1. 构建分析服务镜像..."
docker build -t deeprisk-analyze:latest .

echo ""
echo "2. 启动分析服务实例1..."
docker run -d \
  --name analyze-service-1 \
  -p 5001:5001 \
  --network host \
  -e NACOS_SERVER_ADDR=localhost:8848 \
  -e REDIS_HOST=localhost \
  -e REDIS_PORT=6380 \
  -e RABBITMQ_HOST=localhost \
  -e DB_HOST=172.20.0.1 \
  -e DB_PORT=3306 \
  -e SERVER_PORT=5001 \
  -e NACOS_SERVICE_NAME=analysis-service-1 \
  deeprisk-analyze:latest

echo ""
echo "3. 启动分析服务实例2..."
docker run -d \
  --name analyze-service-2 \
  -p 5002:5002 \
  --network host \
  -e NACOS_SERVER_ADDR=localhost:8848 \
  -e REDIS_HOST=localhost \
  -e REDIS_PORT=6380 \
  -e RABBITMQ_HOST=localhost \
  -e DB_HOST=172.20.0.1 \
  -e DB_PORT=3306 \
  -e SERVER_PORT=5002 \
  -e NACOS_SERVICE_NAME=analysis-service-2 \
  deeprisk-analyze:latest

echo ""
echo "4. 启动分析服务实例3..."
docker run -d \
  --name analyze-service-3 \
  -p 5003:5003 \
  --network host \
  -e NACOS_SERVER_ADDR=localhost:8848 \
  -e REDIS_HOST=localhost \
  -e REDIS_PORT=6380 \
  -e RABBITMQ_HOST=localhost \
  -e DB_HOST=172.20.0.1 \
  -e DB_PORT=3306 \
  -e SERVER_PORT=5003 \
  -e NACOS_SERVICE_NAME=analysis-service-3 \
  deeprisk-analyze:latest

echo ""
echo "5. 等待服务启动..."
sleep 20

echo ""
echo "部署完成！"
echo ""
echo "服务访问地址:"
echo "  分析服务实例1: http://localhost:5001"
echo "  分析服务实例2: http://localhost:5002"
echo "  分析服务实例3: http://localhost:5003"
echo "  健康检查端点: http://localhost:500X/health (X为实例号)"
echo ""
echo "管理命令:"
echo "  查看所有日志: docker logs -f analyze-service-1 analyze-service-2 analyze-service-3"
echo "  查看单个日志: docker logs -f analyze-service-X (X为实例号)"
echo "  停止所有服务: docker stop analyze-service-1 analyze-service-2 analyze-service-3"
echo "  删除所有容器: docker rm analyze-service-1 analyze-service-2 analyze-service-3"
echo "  删除镜像: docker rmi deeprisk-analyze:latest"
echo ""