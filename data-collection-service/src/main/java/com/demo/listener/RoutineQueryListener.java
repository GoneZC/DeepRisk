package com.demo.listener;

import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class RoutineQueryListener {
    
    @RabbitListener(queues = "routine-query-queue", concurrency = "2-5")
    public void processRoutineQuery(Map<String, Object> queryTask) {
        // 常规查询处理逻辑
        // 1. 完整数据处理
        // 2. 结果缓存
        // 3. 详细日志记录
    }
} 