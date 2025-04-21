package com.demo.listener;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import java.util.Map;

@Component
public class CacheUpdateListener {
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    @RabbitListener(queues = "cache-update-queue")
    public void processCacheUpdate(Map<String, Object> message) {
        String cacheKey = (String) message.get("cacheKey");
        Object data = message.get("data");
        
        // 更新缓存
        redisTemplate.opsForValue().set(cacheKey, data);
    }
} 