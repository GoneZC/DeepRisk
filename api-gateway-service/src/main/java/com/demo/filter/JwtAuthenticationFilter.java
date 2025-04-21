package com.demo.filter;

import com.demo.util.JwtUtil;
import io.jsonwebtoken.Claims;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Component
public class JwtAuthenticationFilter implements GatewayFilter {

    private final JwtUtil jwtUtil;
    
    // 配置白名单路径（不需要令牌的路径）
    private final String[] whitelist = {"/api/auth/", "/api/diagnosis-details/", "/api/fee-details/"};

    public JwtAuthenticationFilter(JwtUtil jwtUtil) {
        this.jwtUtil = jwtUtil;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getURI().getPath();
        
        System.out.println("\n=== JWT过滤器开始处理请求 ===");
        System.out.println("请求路径: " + path);
        System.out.println("请求方法: " + request.getMethod());
        System.out.println("请求头部: " + request.getHeaders());
        
        // 检查是否是白名单URL
        for (String whitelistPath : whitelist) {
            if (path.startsWith(whitelistPath)) {
                System.out.println("白名单路径，跳过认证: " + path);
                return chain.filter(exchange);
            }
        }
        
        // 获取Authorization头
        String authHeader = request.getHeaders().getFirst(HttpHeaders.AUTHORIZATION);
        System.out.println("Authorization头: " + authHeader);
        
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            System.out.println("认证失败: Authorization头缺失或格式不正确");
            return onError(exchange, "Authorization header is missing or invalid", HttpStatus.UNAUTHORIZED);
        }
        
        // 提取和验证令牌
        String token = authHeader.substring(7);
        System.out.println("提取到的JWT令牌: " + token.substring(0, Math.min(20, token.length())) + "...");
        
        try {
            if (!jwtUtil.validateToken(token)) {
                System.out.println("认证失败: JWT令牌无效或已过期");
                return onError(exchange, "Invalid or expired JWT token", HttpStatus.UNAUTHORIZED);
            }
            
            System.out.println("JWT令牌验证成功");
            
            // 提取用户信息
            Claims claims = jwtUtil.extractAllClaims(token);
            String userId = claims.getSubject();
            String username = claims.getSubject();
            String role = claims.get("role", String.class);
            String hospitalCode = claims.get("hospitalCode", String.class);
            
            System.out.println("从JWT提取用户信息:");
            System.out.println("  - userId: " + userId);
            System.out.println("  - username: " + username);
            System.out.println("  - role: " + role);
            System.out.println("  - hospitalCode: " + hospitalCode);
            
            // 将用户信息添加到请求头
            ServerHttpRequest mutatedRequest = request.mutate()
                    .header("X-User-Id", userId)
                    .header("X-User-Name", username)
                    .header("X-User-Role", role)
                    .header("X-Hospital-Code", hospitalCode != null ? hospitalCode : "")
                    .build();
            
            System.out.println("已将用户信息添加到请求头，转发请求");
            System.out.println("=== JWT过滤器处理完成 ===\n");
            
            return chain.filter(exchange.mutate().request(mutatedRequest).build());
        } catch (Exception e) {
            System.err.println("JWT处理异常: " + e.getMessage());
            e.printStackTrace();
            return onError(exchange, "JWT processing error: " + e.getMessage(), HttpStatus.UNAUTHORIZED);
        }
    }
    
    private Mono<Void> onError(ServerWebExchange exchange, String message, HttpStatus status) {
        ServerHttpResponse response = exchange.getResponse();
        System.err.println("返回错误: " + status + " - " + message);
        response.setStatusCode(status);
        return response.setComplete();
    }
} 