package com.demo.utils;

import com.demo.model.UserInfo;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import jakarta.servlet.http.HttpServletRequest;

public class UserContext {
    
    private static final String USER_ATTRIBUTE = "currentUser";
    
    // 存储当前线程的用户信息
    private static final ThreadLocal<UserInfo> userHolder = new ThreadLocal<>();
    
    // 从请求或线程本地变量获取当前用户信息
    public static UserInfo getCurrentUser() {
        // 优先从线程本地变量获取
        UserInfo user = userHolder.get();
        if (user != null) {
            return user;
        }
        
        // 尝试从请求属性中获取
        try {
            ServletRequestAttributes attributes = 
                (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
            if (attributes != null) {
                HttpServletRequest request = attributes.getRequest();
                user = (UserInfo) request.getAttribute(USER_ATTRIBUTE);
                if (user != null) {
                    // 存入线程本地变量
                    setCurrentUser(user);
                }
            }
        } catch (Exception e) {
            System.err.println("获取当前用户信息失败: " + e.getMessage());
        }
        
        return user;
    }
    
    // 设置当前用户信息到线程本地变量
    public static void setCurrentUser(UserInfo user) {
        userHolder.set(user);
    }
    
    // 清除线程本地变量
    public static void clear() {
        userHolder.remove();
    }
} 