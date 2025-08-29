package com.demo.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/doc")
@Tag(name = "API文档测试", description = "用于测试Swagger文档功能的接口")
public class ApiDocController {
    
    @Operation(summary = "获取API信息", description = "返回API的基本信息和状态")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "获取成功",
            content = @Content(mediaType = "application/json",
                schema = @Schema(example = "{\"name\": \"医保反欺诈系统API\", \"version\": \"1.0.0\", \"status\": \"running\"}")))
    })
    @GetMapping("/info")
    public ResponseEntity<Map<String, Object>> getApiInfo() {
        Map<String, Object> info = new HashMap<>();
        info.put("name", "医保反欺诈系统API");
        info.put("version", "1.0.0");
        info.put("status", "running");
        info.put("timestamp", LocalDateTime.now());
        info.put("description", "提供医保费用查询、风险分析、门诊监管等功能");
        
        return ResponseEntity.ok(info);
    }
    
    @Operation(summary = "健康检查", description = "检查服务是否正常运行")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "服务正常",
            content = @Content(mediaType = "application/json",
                schema = @Schema(example = "{\"status\": \"UP\", \"message\": \"Service is healthy\"}")))
    })
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> healthCheck() {
        Map<String, String> status = new HashMap<>();
        status.put("status", "UP");
        status.put("message", "Service is healthy");
        
        return ResponseEntity.ok(status);
    }
    
    /**
     * Actuator健康检查端点，用于Nacos健康检查
     */
    @Operation(summary = "Actuator健康检查", description = "用于Nacos等服务注册中心的健康检查")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "服务正常",
            content = @Content(mediaType = "application/json",
                schema = @Schema(example = "{\"status\": \"UP\"}")))
    })
    @GetMapping("/actuator/health")
    public ResponseEntity<Map<String, String>> actuatorHealth() {
        Map<String, String> status = new HashMap<>();
        status.put("status", "UP");
        
        return ResponseEntity.ok(status);
    }
}