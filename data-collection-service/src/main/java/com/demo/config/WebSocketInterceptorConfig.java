package com.demo.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.lang.NonNull;
import org.springframework.messaging.Message;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.simp.config.ChannelRegistration;
import org.springframework.messaging.simp.stomp.StompCommand;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.messaging.support.ChannelInterceptor;
import org.springframework.messaging.support.MessageHeaderAccessor;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

@Configuration
@Order(Ordered.HIGHEST_PRECEDENCE + 99)
@Slf4j
public class WebSocketInterceptorConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureClientInboundChannel(@NonNull ChannelRegistration registration) {
        registration.interceptors(new ChannelInterceptor() {
            @Override
            public Message<?> preSend(@NonNull Message<?> message, @NonNull MessageChannel channel) {
                StompHeaderAccessor accessor = MessageHeaderAccessor.getAccessor(message, StompHeaderAccessor.class);
                if (accessor != null && accessor.getCommand() != null) {
                    log.info("WebSocket消息: {} - 目标路径: {} - 会话ID: {}", 
                             accessor.getCommand(), accessor.getDestination(), accessor.getSessionId());
                    
                    if (StompCommand.SEND.equals(accessor.getCommand()) && accessor.getDestination() != null) {
                        if (accessor.getDestination().equals("/app/heartbeat")) {
                            log.info("拦截到心跳消息: {}", message.getPayload());
                        }
                    }
                }
                return message;
            }
        });
    }
} 