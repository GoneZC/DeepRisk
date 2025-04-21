package com.demo.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.*;
import com.demo.service.SettlementService;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

@RestController
@RequestMapping("/api/cache")
public class CacheController {
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Autowired
    private SettlementService settlementService;

    @GetMapping("/first-page/keys")
    public Set<String> getCacheKeys() {
        return redisTemplate.keys("firstPage*");
    }

    @DeleteMapping("/first-page")
    public String clearCache() {
        redisTemplate.delete(Objects.requireNonNull(redisTemplate.keys("firstPage*")));
        return "缓存已清空";
    }

    @PostMapping("/clear")
    public Map<String, String> clearAllCache() {
        settlementService.clearAllPagesCache();
        Map<String, String> response = new HashMap<>();
        response.put("status", "success");
        response.put("message", "Cache cleared successfully");
        return response;
    }
} 