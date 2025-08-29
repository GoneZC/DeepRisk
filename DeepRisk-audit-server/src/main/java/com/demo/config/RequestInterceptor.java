package com.demo.config;

import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.lang.NonNull;
import org.springframework.lang.Nullable;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import com.demo.utils.UserContext;
import com.demo.model.UserInfo;

@Component
public class RequestInterceptor implements HandlerInterceptor {
    
    @Override
    public boolean preHandle(@NonNull HttpServletRequest request, 
                            @NonNull HttpServletResponse response, 
                            @NonNull Object handler) {
        // 跳过登录接口的拦截
        if (request.getRequestURI().contains("/api/auth/login")) {
            return true;
        }
        
        // 优先从请求头获取用户信息（API网关设置的）
        String userId = request.getHeader("X-User-Id");
        String username = request.getHeader("X-User-Name");
        String role = request.getHeader("X-User-Role");
        String hospitalCode = request.getHeader("X-Hospital-Code");
        
        // 如果没有用户信息，尝试从Authorization头解析token
        if (userId == null || username == null) {
            String authHeader = request.getHeader("Authorization");
            if (authHeader != null && authHeader.startsWith("Bearer ")) {
                String token = authHeader.substring(7);
                
                // 简单的token解析逻辑
                if (token.startsWith("admin_token_")) {
                    userId = "1";
                    username = "admin";
                    role = "ADMIN";
                    hospitalCode = null; // 管理员没有医院编码
                } else if (token.startsWith("hospital2_token_")) {
                    userId = "2";
                    username = "hospital2";
                    role = "HOSPITAL";
                    hospitalCode = "H002";
                }
            }
        }
        
        // 为当前线程设置用户上下文
        if (userId != null && username != null) {
            UserContext.setCurrentUser(new UserInfo(userId, username, role, hospitalCode));
        } else {
            System.out.println("警告: 无法获取用户信息，请求URI: " + request.getRequestURI());
        }
        
        return true;
    }
    
    @Override
    public void afterCompletion(@NonNull HttpServletRequest request, 
                               @NonNull HttpServletResponse response, 
                               @NonNull Object handler, 
                               @Nullable Exception ex) {
        // 清除用户上下文
        UserContext.clear();
    }
}