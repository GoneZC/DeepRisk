package com.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/fallback")
public class FallbackController {

    @GetMapping("/async-risk")
    public Mono<String> asyncRiskFallback() {
        return Mono.just("风险评估服务暂时不可用，请稍后再试");
    }
} 