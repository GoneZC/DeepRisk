package com.demo.controller;

import com.demo.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private JwtUtil jwtUtil;

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, String> loginRequest) {
        String username = loginRequest.get("username");
        String password = loginRequest.get("password");
        
        System.out.println("用户是: " + username);
        // 简化认证逻辑，实际应用中应该查询数据库
        if ("admin".equals(username) && "123".equals(password)) {
            // 医保局管理员
            String token = jwtUtil.generateToken("1", username, "INSURANCE_BUREAU", null);
            Map<String, Object> response = new HashMap<>();
            response.put("token", token);
            response.put("role", "INSURANCE_BUREAU");
            return ResponseEntity.ok(response);
        } else if ("hospital1".equals(username) && "123".equals(password)) {
            // 医院用户
            String token = jwtUtil.generateToken("2", username, "HOSPITAL", "AAZGJONNU");
            Map<String, Object> response = new HashMap<>();
            response.put("token", token);
            response.put("role", "HOSPITAL");
            response.put("hospitalCode", "AAZGJONNU");
            return ResponseEntity.ok(response);
        } else if ("hospital2".equals(username) && "123".equals(password)) {
            // 另一个医院用户
            String token = jwtUtil.generateToken("3", username, "HOSPITAL", "AAZNJHLHC");
            Map<String, Object> response = new HashMap<>();
            response.put("token", token);
            response.put("role", "HOSPITAL");
            response.put("hospitalCode", "AAZNJHLHC");
            return ResponseEntity.ok(response);
        }
        
        return ResponseEntity.status(401).body(Map.of("error", "Invalid credentials"));
    }
} 