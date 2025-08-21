#!/bin/bash

# 应用配置
APP_NAME="fee-query-service"
APP_VERSION="1.0.0"
JAR_FILE="/opt/${APP_NAME}/${APP_NAME}-${APP_VERSION}.jar"
PID_FILE="/var/run/${APP_NAME}.pid"
LOG_DIR="/var/log/${APP_NAME}"

# JVM参数
JAVA_OPTS="-Xms1g -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:+PrintGCDetails -XX:+PrintGCTimeStamps -Xloggc:${LOG_DIR}/gc.log"

# 环境变量
export SPRING_PROFILES_ACTIVE=prod
export DB_USERNAME=${DB_USERNAME:-app_user}
export DB_PASSWORD=${DB_PASSWORD:-your_secure_password}
export REDIS_HOST=${REDIS_HOST:-localhost}
export REDIS_PORT=${REDIS_PORT:-6379}
export REDIS_PASSWORD=${REDIS_PASSWORD:-}
export SERVER_PORT=${SERVER_PORT:-8081}
export EUREKA_URL=${EUREKA_URL:-http://localhost:8761/eureka/}

# 创建日志目录
sudo mkdir -p ${LOG_DIR}
sudo chown $(whoami):$(whoami) ${LOG_DIR}

# 检查应用是否已运行
if [ -f ${PID_FILE} ]; then
    PID=$(cat ${PID_FILE})
    if ps -p ${PID} > /dev/null 2>&1; then
        echo "${APP_NAME} is already running with PID ${PID}"
        exit 1
    else
        rm -f ${PID_FILE}
    fi
fi

# 启动应用
echo "Starting ${APP_NAME}..."
nohup java ${JAVA_OPTS} -jar ${JAR_FILE} > ${LOG_DIR}/startup.log 2>&1 &
PID=$!

# 保存PID
echo ${PID} > ${PID_FILE}
echo "${APP_NAME} started with PID ${PID}"

# 等待应用启动
sleep 10
if ps -p ${PID} > /dev/null 2>&1; then
    echo "${APP_NAME} started successfully"
    echo "Health check: curl http://localhost:${SERVER_PORT}/actuator/health"
else
    echo "${APP_NAME} failed to start"
    exit 1
fi 