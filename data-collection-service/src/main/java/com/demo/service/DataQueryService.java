package com.demo.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import java.util.Map;
import java.util.UUID;
import java.util.HashMap;

@Service
public class DataQueryService {
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    public String submitComplexQuery(Map<String, Object> queryParams) {
        String queryId = UUID.randomUUID().toString();
        
        // 创建查询任务消息
        Map<String, Object> queryTask = new HashMap<>();
        queryTask.put("queryId", queryId);
        queryTask.put("params", queryParams);
        queryTask.put("timestamp", System.currentTimeMillis());
        
        // 发送到查询队列
        rabbitTemplate.convertAndSend("query-exchange", "data.query.complex", queryTask);
        
        return queryId; // 返回查询ID
    }
} 