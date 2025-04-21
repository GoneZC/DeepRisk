package com.demo.controller;

import com.demo.service.RuleEvaluationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/rules")
public class RuleController {
    
    @Autowired
    private RuleEvaluationService ruleService;
    
    @PostMapping("/check-abnormal-fee")
    public boolean checkAbnormalFee(@RequestBody Map<String, Object> request) {
        String mdtrtId = (String) request.get("mdtrtId");
        double amount = ((Number) request.get("amount")).doubleValue();
        
        return ruleService.detectAbnormalFee(mdtrtId, amount);
    }
    
    @PostMapping("/evaluate-treatment")
    public Map<String, Object> evaluateTreatment(@RequestBody Map<String, Object> treatmentData) {
        return ruleService.evaluateTreatmentRules(treatmentData);
    }
    
    @PostMapping("/batch-check")
    public Map<String, Object> batchCheckFeeDetails(@RequestBody Map<String, Object> request) {
        List<Map<String, Object>> feeDetails = (List<Map<String, Object>>) request.get("feeDetails");
        String checkType = (String) request.get("checkType");
        
        // 批量应用规则，识别违规条目
        Map<String, Object> result = ruleService.batchEvaluate(feeDetails, checkType);
        
        // 发布事件通知深度分析服务
        eventPublisher.publishEvent("RULE_CHECKING_COMPLETED", result);
        
        return result;
    }
} 