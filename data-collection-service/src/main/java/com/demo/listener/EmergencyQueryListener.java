package com.demo.listener;

import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class EmergencyQueryListener {
    
    @RabbitListener(queues = "emergency-query-queue", concurrency = "5-10")
    public void processEmergencyQuery(Map<String, Object> queryTask) {
        // 紧急查询的特殊处理逻辑
        // 1. 更高优先级处理
        // 2. 简化的结果集
        // 3. 更短的超时设置
    }
} 