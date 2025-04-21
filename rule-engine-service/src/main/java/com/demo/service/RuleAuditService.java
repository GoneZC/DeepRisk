package com.demo.service;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
public class RuleAuditService {

    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    public void auditRuleEffectiveness(String ruleId) {
        // 创建审计查询任务
        Map<String, Object> auditTask = new HashMap<>();
        auditTask.put("queryId", UUID.randomUUID().toString());
        auditTask.put("type", "RULE_AUDIT");
        auditTask.put("ruleId", ruleId);
        
        // 同样发送到查询队列，但使用不同的路由键
        rabbitTemplate.convertAndSend("query-exchange", "data.query.audit", auditTask);
    }
} 