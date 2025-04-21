#!/bin/bash
# 1. 启动基础服务
systemctl start fee-query.service
systemctl start auth-service.service

# 2. 等待基础服务启动
sleep 10

# 3. 启动依赖基础服务的服�?
systemctl start rule-engine.service
systemctl start deep-analysis.service

# 4. 最后启动API网关
systemctl start api-gateway.service
