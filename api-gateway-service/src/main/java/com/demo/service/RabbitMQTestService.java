package com.demo.service;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class RabbitMQTestService implements CommandLineRunner {
    
    @Autowired(required = false)
    private RabbitTemplate rabbitTemplate;
    
    @Override
    public void run(String... args) {
        System.out.println("=== RabbitMQ测试 ===");
        System.out.println("RabbitTemplate: " + (rabbitTemplate != null ? "已注入" : "未注入"));
    }
} 