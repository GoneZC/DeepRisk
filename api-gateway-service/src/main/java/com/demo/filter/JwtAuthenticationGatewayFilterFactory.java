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
        return jwtFilter.withPredicate(config.getPredicate());
    }
    
    public static class Config {
        private String predicate;
        
        public String getPredicate() {
            return predicate;
        }
        
        public void setPredicate(String predicate) {
            this.predicate = predicate;
        }
    }
} 