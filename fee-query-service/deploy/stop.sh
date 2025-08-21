#!/bin/bash

APP_NAME="fee-query-service"
PID_FILE="/var/run/${APP_NAME}.pid"

# 检查PID文件是否存在
if [ ! -f ${PID_FILE} ]; then
    echo "${APP_NAME} is not running"
    exit 0
fi

# 读取PID
PID=$(cat ${PID_FILE})

# 检查进程是否存在
if ! ps -p ${PID} > /dev/null 2>&1; then
    echo "${APP_NAME} is not running (stale PID file)"
    rm -f ${PID_FILE}
    exit 0
fi

# 优雅停止
echo "Stopping ${APP_NAME} (PID: ${PID})..."
kill ${PID}

# 等待进程停止
for i in {1..30}; do
    if ! ps -p ${PID} > /dev/null 2>&1; then
        echo "${APP_NAME} stopped successfully"
        rm -f ${PID_FILE}
        exit 0
    fi
    sleep 1
done

# 强制停止
echo "Force stopping ${APP_NAME}..."
kill -9 ${PID}
rm -f ${PID_FILE}
echo "${APP_NAME} force stopped" 