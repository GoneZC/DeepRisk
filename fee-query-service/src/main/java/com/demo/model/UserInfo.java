package com.demo.model;

public class UserInfo {
    private String userId;
    private String role;
    private String hospitalCode;
    
    public UserInfo(String userId, String role, String hospitalCode) {
        this.userId = userId;
        this.role = role;
        this.hospitalCode = hospitalCode;
    }
    
    // Getters
    public String getRole() { return role; }
    public String getHospitalCode() { return hospitalCode; }
} 