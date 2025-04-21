package com.demo.filter;

import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory;

// @Component  // 注释掉此注解
public class JwtAuthenticationFilterFactory extends AbstractGatewayFilterFactory<Object> {
    
    private final JwtAuthenticationFilter filter;
    
    public JwtAuthenticationFilterFactory(JwtAuthenticationFilter filter) {
        this.filter = filter;
    }
    
    @Override
    public GatewayFilter apply(Object config) {
        return filter;
    }
    
    @Override
    public Class<Object> getConfigClass() {
        return Object.class;
    }
    
    @Override
    public String name() {
        return "JwtAuthentication";
    }
} 