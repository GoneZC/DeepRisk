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
        // 从请求头获取用户信息
        String userId = request.getHeader("X-User-Id");
        String role = request.getHeader("X-User-Role");
        String hospitalCode = request.getHeader("X-Hospital-Code");
        
        // 将用户信息存入当前线程上下文
        UserContext.setCurrentUser(new UserInfo(userId, role, hospitalCode));
        return true;
    }
    
    @Override
    public void afterCompletion(@NonNull HttpServletRequest request, 
                               @NonNull HttpServletResponse response, 
                               @NonNull Object handler, 
                               @Nullable Exception ex) {
        // 清理线程上下文
        UserContext.clear();
    }
} 