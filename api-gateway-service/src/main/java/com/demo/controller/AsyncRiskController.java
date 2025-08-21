package com.demo.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.UUID;
import reactor.core.scheduler.Schedulers;
import com.demo.config.RabbitMQConfig;
import org.springframework.amqp.rabbit.core.RabbitTemplate;

@RestController
@RequestMapping("/async-risk-assessment")
public class AsyncRiskController {

    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    @Autowired
    private RedisTemplate<String, String> redisTemplate;
    
    private ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 提交风险评估请求
     */
    @PostMapping("/assess")
    public Mono<ResponseEntity<String>> asyncAssessment(@RequestBody Map<String, Object> data) {
        return Mono.fromCallable(() -> {
            String requestId = UUID.randomUUID().toString();
            data.put("requestId", requestId);
            try {
                rabbitTemplate.convertAndSend(
                    RabbitMQConfig.RISK_EXCHANGE,
                    RabbitMQConfig.RISK_ROUTING_KEY,
                    data
                );
                return ResponseEntity.ok("风险评估请求已提交，ID: " + requestId);
            } catch (Exception e) {
                return ResponseEntity.status(500).body("处理失败: " + e.getMessage());
            }
        }).subscribeOn(Schedulers.boundedElastic());
    }
    
    /**
     * 获取风险评估结果
     */
    @GetMapping("/{requestId}")
    public ResponseEntity<?> getResult(@PathVariable String requestId) {
        String result = redisTemplate.opsForValue().get("risk:result:" + requestId);
        if (result == null) {
            return ResponseEntity.status(404).body("结果尚未准备好或不存在");
        }
        return ResponseEntity.ok(result);
    }
    
    /**
     * 接收风险评估结果回调
     */
    @PostMapping("/result")
    public ResponseEntity<?> resultCallback(@RequestBody Map<String, Object> result) {
        try {
            String requestId = (String) result.get("requestId");
            redisTemplate.opsForValue().set(
                "risk:result:" + requestId,
                objectMapper.writeValueAsString(result),
                30, TimeUnit.MINUTES
            );
            return ResponseEntity.ok("结果已保存");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("处理回调时出错: " + e.getMessage());
        }
    }

    @GetMapping("/test")
    public Mono<String> test() {
        return Mono.just("异步风险评估服务正常运行");
    }
}