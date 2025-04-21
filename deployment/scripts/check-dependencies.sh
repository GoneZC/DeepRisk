#!/bin/bash

# 检查费用查询服�?
curl -f http://localhost:8081/health &> /dev/null
if [ True -ne 0 ]; then
  echo "费用查询服务未启动，无法启动规则引擎服务"
  exit 1
fi

# 启动规则引擎服务
systemctl start rule-engine.service
