package com.demo.utils;

import com.demo.model.UserInfo;

public class UserContext {
    private static final ThreadLocal<UserInfo> userContext = new ThreadLocal<>();
    
    public static void setCurrentUser(UserInfo userInfo) {
        userContext.set(userInfo);
    }
    
    public static UserInfo getCurrentUser() {
        return userContext.get();
    }
    
    public static void clear() {
        userContext.remove();
    }
} 