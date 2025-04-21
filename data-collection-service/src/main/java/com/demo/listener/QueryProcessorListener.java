package com.demo.listener;

import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

@Component
public class QueryProcessorListener {
    
    @Autowired
    private DataRepository dataRepository;
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    @RabbitListener(queues = "data-query-queue")
    public void processQuery(Map<String, Object> queryTask) {
        String queryId = (String) queryTask.get("queryId");
        Map<String, Object> params = (Map<String, Object>) queryTask.get("params");
        
        try {
            // 执行查询(耗时操作)
            Object result = executeQuery(params);
            
            // 发送成功结果
            Map<String, Object> resultMessage = new HashMap<>();
            resultMessage.put("queryId", queryId);
            resultMessage.put("status", "SUCCESS");
            resultMessage.put("result", result);
            
            rabbitTemplate.convertAndSend("query-exchange", "data.result." + queryId, resultMessage);
        } catch (Exception e) {
            // 发送错误消息
            Map<String, Object> errorMessage = new HashMap<>();
            errorMessage.put("queryId", queryId);
            errorMessage.put("status", "ERROR");
            errorMessage.put("error", e.getMessage());
            
            rabbitTemplate.convertAndSend("query-exchange", "data.result." + queryId, errorMessage);
        }
    }
    
    private Object executeQuery(Map<String, Object> params) {
        // 实现查询逻辑
        return dataRepository.executeComplexQuery(params);
    }
} 