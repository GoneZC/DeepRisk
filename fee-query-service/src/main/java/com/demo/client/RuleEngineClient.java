package com.demo.client;

import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

@Component
public class RuleEngineClient {
    
    private final RestTemplate restTemplate = new RestTemplate();
    private final String ruleEngineUrl = "http://localhost:8083/api/rules";
    
    public boolean checkAbnormalFee(String mdtrtId, BigDecimal amount) {
        Map<String, Object> request = new HashMap<>();
        request.put("mdtrtId", mdtrtId);
        request.put("amount", amount);
        
        Boolean result = restTemplate.postForObject(
            ruleEngineUrl + "/check-abnormal-fee", 
            request, 
            Boolean.class
        );
        
        return result != null && result;
    }
} 