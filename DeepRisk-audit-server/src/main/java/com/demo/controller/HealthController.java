package com.demo.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@Tag(name = "健康检查", description = "服务健康状态检查接口")
public class HealthController {
    
    @GetMapping("/simple-health")
    @Operation(summary = "简单健康检查", description = "基本的服务运行状态检查")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "服务正常",
            content = @Content(mediaType = "application/json",
                schema = @Schema(example = "{\"status\": \"healthy\", \"service\": \"audit-service\"}")))
    })
    public Map<String, String> health() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("service", "audit-service");
        return response;
    }
    
    /**
     * Actuator健康检查端点，用于Nacos健康检查
     */
    @GetMapping("/actuator/health")
    public ResponseEntity<Map<String, String>> actuatorHealth() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "UP");
        response.put("service", "audit-service");
        return ResponseEntity.ok(response);
    }
}