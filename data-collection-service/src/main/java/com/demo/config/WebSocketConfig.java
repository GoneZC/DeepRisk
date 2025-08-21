package com.demo.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.lang.NonNull;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketTransportRegistration;
import org.springframework.web.socket.server.standard.ServletServerContainerFactoryBean;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureMessageBroker(@NonNull MessageBrokerRegistry registry) {
        // 客户端订阅路径前缀
        registry.enableSimpleBroker("/topic")
                .setHeartbeatValue(new long[]{10000, 10000})  // 设置心跳间隔
                .setTaskScheduler(heartbeatScheduler());
        // 客户端发送消息路径前缀 - 客户端向此前缀发送消息，Spring会自动截取前缀后查找@MessageMapping
        registry.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(@NonNull StompEndpointRegistry registry) {
        // 注册STOMP端点
        registry.addEndpoint("/ws-data-collection")
                .setAllowedOriginPatterns("*")
                .withSockJS()
                .setDisconnectDelay(30000)  // 30秒断开延迟
                .setHeartbeatTime(25000);   // 25秒心跳
    }
    
    @Override
    public void configureWebSocketTransport(@NonNull WebSocketTransportRegistration registry) {
        registry.setMessageSizeLimit(128 * 1024)     // 消息大小限制
                .setSendBufferSizeLimit(512 * 1024)  // 发送缓冲区大小
                .setSendTimeLimit(20000);            // 发送超时时间
    }
    
    @Bean
    public ServletServerContainerFactoryBean createWebSocketContainer() {
        ServletServerContainerFactoryBean container = new ServletServerContainerFactoryBean();
        container.setMaxTextMessageBufferSize(8192);
        container.setMaxBinaryMessageBufferSize(8192);
        container.setMaxSessionIdleTimeout(60000L);  // 60秒会话超时
        return container;
    }
    
    @Bean
    public org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler heartbeatScheduler() {
        org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler scheduler = 
            new org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler();
        scheduler.setPoolSize(1);
        scheduler.setThreadNamePrefix("ws-heartbeat-");
        return scheduler;
    }
} 