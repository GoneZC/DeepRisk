package com.demo.config;

import org.springframework.context.annotation.Configuration;
import reactor.core.publisher.Hooks;

import jakarta.annotation.PostConstruct;

@Configuration
public class ReactorConfig {

    @PostConstruct
    public void init() {
        // 禁用上下文传播深度检查，避免栈溢出
        Hooks.onOperatorDebug();
        System.setProperty("reactor.trace.cancel", "true");
        // 增加最大上下文深度
        System.setProperty("reactor.contextstackoverflow.maxsize", "256");
    }
} 