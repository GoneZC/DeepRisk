package com.demo.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

@Service
public class AsyncTaskService {
    
    private static final Logger logger = LoggerFactory.getLogger(AsyncTaskService.class);
    
    @Autowired
    private RestTemplate restTemplate;
    
    /**
     * 异步触发规则引擎检查
     */
    @Async
    public void triggerRuleEngineCheck(List<Map<String, Object>> feeDetails) {
        try {
            logger.info("开始异步触发规则引擎检查，数据记录数: {}", feeDetails.size());
            
            // // 调用规则引擎服务的API
            // String ruleEngineUrl = "http://rule-engine-service/rules/check";
            
            // 通过API网关访问
            String gatewayUrl = "http://api-gateway/api/rules/check";
            
            // 发送数据到API网关
            Map<String, Object> response = restTemplate.postForObject(
                gatewayUrl, 
                feeDetails, 
                Map.class
            );
            
            logger.info("规则引擎检查触发成功，响应: {}", response);
        } catch (Exception e) {
            logger.error("触发规则引擎检查失败", e);
            // 可以实现重试逻辑或将失败任务存入队列
        }
    }

    @Async("taskExecutor")
    public CompletableFuture<List<Map<String, Object>>> processDataAsync(
            Map<String, Object> parameters) {
        // 执行耗时处理
        return CompletableFuture.completedFuture(results);
    }
} 