package com.demo.controller;

import com.demo.model.StatusUpdate;
import com.demo.service.DataCollectionService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.messaging.simp.SimpMessagingTemplate;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/data-collection")
@CrossOrigin(origins = "*")
@Slf4j
public class DataCollectionController {

    @Autowired
    private DataCollectionService dataCollectionService;
    
    @Autowired
    private SimpMessagingTemplate messagingTemplate;
    
    /**
     * 模拟数据采集
     */
    @PostMapping("/collect")
    public ResponseEntity<Map<String, Object>> simulateDataCollection() {
        log.info("收到模拟数据采集请求");
        try {
            // 记录采集前的计数
            StatusUpdate beforeStatus = dataCollectionService.getCurrentStatus();
            log.info("采集前状态: {}", beforeStatus);
            
            // 执行数据采集
            dataCollectionService.collectData();
            log.info("数据采集请求处理完成");
            
            // 获取采集后的计数
            StatusUpdate afterStatus = dataCollectionService.getCurrentStatus();
            log.info("采集后状态: {}", afterStatus);
            
            // 测试直接发送WebSocket消息
            log.info("直接通过控制器发送WebSocket消息: {}", afterStatus);
            try {
                messagingTemplate.convertAndSend("/topic/collection-status", afterStatus);
                log.info("控制器WebSocket消息发送成功");
            } catch (Exception e) {
                log.error("控制器WebSocket消息发送失败: {}", e.getMessage());
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "数据采集请求已处理");
            response.put("beforeCounts", beforeStatus);
            response.put("counts", afterStatus);
            response.put("changed", afterStatus.getProcessedCount() > beforeStatus.getProcessedCount());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("处理数据采集请求时发生错误: {}", e.getMessage(), e);
            Map<String, Object> response = new HashMap<>();
            response.put("status", "error");
            response.put("message", e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }
    
    /**
     * 获取当前状态
     */
    @GetMapping("/status")
    public ResponseEntity<StatusUpdate> getCurrentStatus() {
        StatusUpdate status = dataCollectionService.getCurrentStatus();
        return ResponseEntity.ok(status);
    }
    
    @GetMapping("/test-websocket")
    public ResponseEntity<String> testWebSocket() {
        StatusUpdate update = new StatusUpdate(999, 888);
        log.info("手动测试WebSocket发送: {}", update);
        messagingTemplate.convertAndSend("/topic/collection-status", update);
        return ResponseEntity.ok("测试消息已发送");
    }
    
    @GetMapping("/force-increment")
    public ResponseEntity<String> forceIncrement() {
        // 获取当前状态
        StatusUpdate currentStatus = dataCollectionService.getCurrentStatus();
        // 强制+1
        StatusUpdate newStatus = new StatusUpdate(
            currentStatus.getProcessedCount() + 1,
            currentStatus.getRuleTriggeredCount() + 1
        );
        
        log.info("强制增加计数: {} -> {}", currentStatus, newStatus);
        
        // 使用try-catch确保WebSocket错误不会阻断正常流程
        try {
            messagingTemplate.convertAndSend("/topic/collection-status", newStatus);
            log.info("WebSocket消息发送成功: /topic/collection-status, 内容: {}", newStatus);
        } catch (Exception e) {
            log.error("WebSocket消息发送失败: {}", e.getMessage(), e);
        }
        
        return ResponseEntity.ok("强制增加计数完成: " + newStatus);
    }
    
    @GetMapping("/set-counters")
    public ResponseEntity<String> setCounters(@RequestParam(defaultValue = "50") int processed, 
                                             @RequestParam(defaultValue = "10") int triggered) {
        StatusUpdate status = dataCollectionService.setCounters(processed, triggered);
        return ResponseEntity.ok("计数器已设置为: " + status);
    }
    
    @GetMapping("/reset-counters")
    public ResponseEntity<String> resetCounters() {
        StatusUpdate status = dataCollectionService.resetCounters();
        return ResponseEntity.ok("计数器已重置: " + status);
    }

    @GetMapping("/direct-send-test")
    public ResponseEntity<Map<String, Object>> directSendTest() {
        StatusUpdate update = new StatusUpdate(
            (int)(Math.random() * 1000), 
            (int)(Math.random() * 100)
        );
        
        log.info("直接发送测试: {}", update);
        
        Map<String, Object> result = new HashMap<>();
        try {
            messagingTemplate.convertAndSend("/topic/collection-status", update);
            log.info("直接发送WebSocket消息成功");
            result.put("success", true);
            result.put("message", "直接发送WebSocket消息成功");
            result.put("data", update);
        } catch (Exception e) {
            log.error("直接发送WebSocket消息失败: {}", e.getMessage(), e);
            result.put("success", false);
            result.put("error", e.getMessage());
        }
        
        return ResponseEntity.ok(result);
    }
} 