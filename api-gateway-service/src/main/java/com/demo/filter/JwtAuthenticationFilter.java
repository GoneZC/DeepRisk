package com.demo.filter;

import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import org.springframework.http.MediaType;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.core.io.buffer.DataBuffer;
import com.demo.config.JwtConfig;

@Component
public class JwtAuthenticationFilter implements GatewayFilter {
    
    private final JwtConfig jwtConfig;
    
    public JwtAuthenticationFilter(JwtConfig jwtConfig) {
        this.jwtConfig = jwtConfig;
    }
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // 1. 获取请求头中的token
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        
        // 2. 验证token
        if (token != null && token.startsWith("Bearer ")) {
            String jwtToken = token.substring(7);
            
            // 3. 验证JWT并提取用户信息
            Claims claims = validateAndExtractClaims(jwtToken);
            if (claims != null) {
                // 4. 将用户信息添加到请求头，传递给下游服务
                ServerHttpRequest mutatedRequest = exchange.getRequest().mutate()
                    .header("X-User-Id", claims.getSubject())
                    .header("X-User-Role", claims.get("role", String.class))
                    .header("X-Hospital-Code", claims.get("hospitalCode", String.class))
                    .build();
                    
                return chain.filter(exchange.mutate().request(mutatedRequest).build());
            }
        }
        
        // 认证失败，返回401
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(HttpStatus.FORBIDDEN);
        response.getHeaders().setContentType(MediaType.APPLICATION_JSON);
        byte[] bytes = "{\"message\":\"无效的令牌或令牌已过期\"}".getBytes(StandardCharsets.UTF_8);
        DataBuffer buffer = response.bufferFactory().wrap(bytes);
        return response.writeWith(Mono.just(buffer));
    }

    private Claims validateAndExtractClaims(String jwtToken) {
        try {
            System.out.println("尝试验证令牌: " + jwtToken.substring(0, 20) + "...");
            System.out.println("使用密钥: " + jwtConfig.getSecret());
            
            Claims claims = Jwts.parserBuilder()
                .setSigningKey(Keys.hmacShaKeyFor(jwtConfig.getSecret().getBytes(StandardCharsets.UTF_8)))
                .build()
                .parseClaimsJws(jwtToken)
                .getBody();
                
            System.out.println("令牌验证成功，用户: " + claims.getSubject());
            return claims;
        } catch (Exception e) {
            System.out.println("JWT验证失败，详细错误: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }
} 