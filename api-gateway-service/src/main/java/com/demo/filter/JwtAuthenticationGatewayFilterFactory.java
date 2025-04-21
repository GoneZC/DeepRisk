package com.demo.filter;

import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory;
import org.springframework.stereotype.Component;

@Component
public class JwtAuthenticationGatewayFilterFactory extends AbstractGatewayFilterFactory<JwtAuthenticationGatewayFilterFactory.Config> {
    
    private final JwtAuthenticationFilter jwtFilter;
    
    public JwtAuthenticationGatewayFilterFactory(JwtAuthenticationFilter jwtFilter) {
        super(Config.class);
        this.jwtFilter = jwtFilter;
    }
    
    @Override
    public GatewayFilter apply(Config config) {
        return jwtFilter;
    }
    
    public static class Config {
        // 配置属性（如果需要）
    }
} 