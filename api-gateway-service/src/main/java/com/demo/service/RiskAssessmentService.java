package com.demo.service;

import com.demo.config.RabbitMQConfig;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.UUID;

@Service
public class RiskAssessmentService {

    private static final Logger log = LoggerFactory.getLogger(RiskAssessmentService.class);

    @Autowired
    private RabbitTemplate rabbitTemplate;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    private static final String REDIS_KEY_PREFIX = "risk_assessment_status:";
    private static final Duration REDIS_EXPIRATION = Duration.ofHours(1);

    @PostConstruct
    public void checkRabbitTemplateInjection() {
        String versionMarker = "VERSION_CHECK_" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        log.info("<<<<<<<<<< {} >>>>>>>>>>", versionMarker);

        if (this.rabbitTemplate != null) {
            MessageConverter converter = this.rabbitTemplate.getMessageConverter();
            log.info("==============================================================");
            log.info("[DEBUG] Injected RabbitTemplate Check ({}):", versionMarker);
            log.info("  - RabbitTemplate Instance: {}", System.identityHashCode(this.rabbitTemplate));
            log.info("  - Configured MessageConverter: {}", (converter != null ? converter.getClass().getName() : "NULL"));
            log.info("==============================================================");
            if (converter == null || !converter.getClass().getName().contains("Jackson2JsonMessageConverter")) {
                 log.error("[ERROR] Injected RabbitTemplate does NOT have Jackson2JsonMessageConverter configured! ({})", versionMarker);
            }
        } else {
            log.error("[ERROR] RabbitTemplate was not injected into RiskAssessmentService! ({})", versionMarker);
        }
    }

    public Mono<String> submitRiskAssessment(Map<String, Object> data) {
        log.info("Entering submitRiskAssessment method...");
        return Mono.fromCallable(() -> {
            String requestId = UUID.randomUUID().toString();
            data.put("requestId", requestId);

            log.info("Setting Redis key {} to PENDING", REDIS_KEY_PREFIX + requestId);
            redisTemplate.opsForValue().set(
                REDIS_KEY_PREFIX + requestId,
                "PENDING",
                REDIS_EXPIRATION
            );
            log.info("Redis key {} set successfully", REDIS_KEY_PREFIX + requestId);

            log.info(">>> [BEFORE SEND] Sending to RabbitMQ - Type: {}, Data: {}", data.getClass().getName(), data);

            rabbitTemplate.convertAndSend(
                RabbitMQConfig.RISK_EXCHANGE,
                RabbitMQConfig.RISK_ROUTING_KEY,
                data
            );

            log.info("<<< [AFTER SEND] 风险评估请求已发送到队列，ID: {}, Data: {}", requestId, data);

            return "风险评估请求已提交，ID: " + requestId;
        }).publishOn(Schedulers.boundedElastic())
          .doOnSubscribe(subscription -> log.info("Mono subscribed for requestId generation and sending"))
          .doOnSuccess(result -> log.info("Mono completed successfully with result: {}", result))
          .doOnError(error -> log.error("Mono failed with error", error));
    }

    public Mono<String> getAssessmentStatus(String requestId) {
        return Mono.fromCallable(() -> {
                    Object status = redisTemplate.opsForValue().get(REDIS_KEY_PREFIX + requestId);
                    return status != null ? status.toString() : "UNKNOWN";
                })
                .publishOn(Schedulers.boundedElastic());
    }

    public Mono<Void> handleAssessmentResult(Map<String, Object> result) {
        return Mono.fromRunnable(() -> {
            String requestId = (String) result.get("requestId");
            if (requestId != null) {
                log.info("收到风险评估结果回调，ID: {}, Result: {}", requestId, result);
                redisTemplate.opsForValue().set(
                    REDIS_KEY_PREFIX + requestId,
                    result,
                    REDIS_EXPIRATION
                );
            } else {
                log.error("收到的回调结果缺少 requestId: {}", result);
            }
        }).subscribeOn(Schedulers.boundedElastic()).then();
    }
}