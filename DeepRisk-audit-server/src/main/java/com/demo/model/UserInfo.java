package com.demo.model;

import java.io.Serializable;

public class UserInfo implements Serializable {
    
    private String userId;
    private String username;
    private String role;
    private String hospitalCode; // 医院编码
    
    // 构造函数
    public UserInfo() {
    }
    
    public UserInfo(String userId, String username, String role, String hospitalCode) {
        this.userId = userId;
        this.username = username;
        this.role = role;
        this.hospitalCode = hospitalCode;
    }
    
    public UserInfo(String userId, String role, String hospitalCode) {
        this.userId = userId;
        this.role = role;
        this.hospitalCode = hospitalCode;
    }
    
    // Getters and Setters
    public String getUserId() {
        return userId;
    }
    
    public void setUserId(String userId) {
        this.userId = userId;
    }
    
    public String getUsername() {
        return username;
    }
    
    public void setUsername(String username) {
        this.username = username;
    }
    
    public String getRole() {
        return role;
    }
    
    public void setRole(String role) {
        this.role = role;
    }
    
    public String getHospitalCode() {
        return hospitalCode;
    }
    
    public void setHospitalCode(String hospitalCode) {
        this.hospitalCode = hospitalCode;
    }
    
    @Override
    public String toString() {
        return "UserInfo{" +
                "userId='" + userId + '\'' +
                ", username='" + username + '\'' +
                ", role='" + role + '\'' +
                ", hospitalCode='" + hospitalCode + '\'' +
                '}';
    }
} 