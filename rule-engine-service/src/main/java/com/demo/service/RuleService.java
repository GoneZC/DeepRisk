package com.demo.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class RuleService {
    
    @Autowired
    private CustomRuleEngine ruleEngine;
    
    public List<Map<String, Object>> executeRules(List<Map<String, Object>> feeDetails) {
        // 对每条费用记录执行规则检查
        return feeDetails.stream()
            .map(fee -> {
                Map<String, Object> result = new HashMap<>(fee);
                
                // 执行各类规则
                executeFeeLimitRules(result);
                executeDiagnosisMatchRules(result);
                executeFrequencyRules(result);
                
                return result;
            })
            .collect(Collectors.toList());
    }
} 