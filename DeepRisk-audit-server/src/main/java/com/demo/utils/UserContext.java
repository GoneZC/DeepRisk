package com.demo.utils;

import com.demo.model.UserInfo;

public class UserContext {
    // 存储当前线程的用户信息
    private static final ThreadLocal<UserInfo> userHolder = new ThreadLocal<>();
    
    // 从线程本地变量获取当前用户信息
    public static UserInfo getCurrentUser() {
        return userHolder.get();
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