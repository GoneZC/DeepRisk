package com.demo.controller;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import com.fasterxml.jackson.databind.ObjectMapper;

@RestController
@RequestMapping("/test")
public class TestController {

    @Autowired
    private RabbitTemplate rabbitTemplate;

    @GetMapping("/send-test-message")
    public String sendTestMessage() {
        try {
            // 创建测试消息
            Map<String, Object> testData = new HashMap<>();
            testData.put("requestId", UUID.randomUUID().toString());
            testData.put("doctorId", "TEST-DOCTOR");
            testData.put("date", "2025-04-25");
            testData.put("test", true);
            
            // 转为JSON并发送
            String json = new ObjectMapper().writeValueAsString(testData);
            
            rabbitTemplate.convertAndSend(
                "risk.assessment.exchange",   // 直接使用字符串确保名称正确
                "risk.assessment",
                json
            );
            
            return "测试消息已发送，请查看Python消费者日志";
        } catch (Exception e) {
            return "发送失败: " + e.getMessage();
        }
    }
} 