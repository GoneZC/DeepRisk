package com.demo.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@Tag(name = "用户认证", description = "用户登录认证相关接口")
public class AuthController {

    @PostMapping("/login")
    @Operation(summary = "用户登录", description = "用户登录获取JWT令牌")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, String> loginRequest) {
        String username = loginRequest.get("username");
        String password = loginRequest.get("password");
        
        // 简单的用户验证逻辑
        Map<String, Object> response = new HashMap<>();
        
        if ("admin".equals(username) && "demo123".equals(password)) {
            // 生成简单的token（实际项目中应该使用JWT）
            String token = "admin_token_" + System.currentTimeMillis();
            
            response.put("token", token);
            response.put("username", "admin");
            response.put("role", "ADMIN");
            response.put("hospitalCode", null); // 管理员没有医院编码
            response.put("message", "登录成功");
            
            return ResponseEntity.ok(response);
        } else if ("hospital2".equals(username) && "demo123".equals(password)) {
            // 医院用户
            String token = "hospital2_token_" + System.currentTimeMillis();
            
            response.put("token", token);
            response.put("username", "hospital2");
            response.put("role", "HOSPITAL");
            response.put("hospitalCode", "H002");
            response.put("message", "登录成功");
            
            return ResponseEntity.ok(response);
        } else {
            response.put("message", "用户名或密码错误");
            return ResponseEntity.badRequest().body(response);
        }
    }
}