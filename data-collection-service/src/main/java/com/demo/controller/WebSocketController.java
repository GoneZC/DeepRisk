package com.demo.controller;

import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;

import java.util.HashMap;
import java.util.Map;

@Controller
@Slf4j
public class WebSocketController {

    /**
     * 处理心跳消息
     * 客户端应该发送到/app/heartbeat，但由于在WebSocketConfig中已配置前缀，
     * 这里只需要配置/heartbeat
     */
    @MessageMapping("/heartbeat")
    @SendTo("/topic/heartbeat")
    public Map<String, Object> handleHeartbeat(Map<String, Object> message) {
        log.debug("收到心跳消息: {}", message);
        Map<String, Object> response = new HashMap<>();
        response.put("timestamp", System.currentTimeMillis());
        response.put("status", "ok");
        return response;
    }
} 