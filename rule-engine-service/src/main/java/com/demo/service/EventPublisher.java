package com.demo.service;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class EventPublisher {
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    public void publishEvent(String type, Object payload) {
        Event event = new Event(type, payload);
        rabbitTemplate.convertAndSend("medical-audit-exchange", "rule.completed", event);
    }
} 