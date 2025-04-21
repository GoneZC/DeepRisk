package com.demo.service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class RuleEvaluationService {
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    @Autowired
    private EventPublisher eventPublisher;
    
    @Autowired
    private FeeDetailRepository feeDetailRepository;
    
    @Autowired
    private ViolationRepository violationRepository;
    
    @Autowired
    private FeeAuditRepository feeAuditRepository;
    
    public boolean detectAbnormalFee(String mdtrtId, double amount) {
        // 获取治疗相关数据
        Map<String, Object> treatmentData = fetchTreatmentData(mdtrtId);
        
        // 规则引擎逻辑...
        String treatmentType = (String) treatmentData.get("medType");
        double avgAmount = (double) treatmentData.get("avgAmount");
        
        // 简单规则：费用超过平均值的150%视为异常
        return amount > (avgAmount * 1.5);
    }
    
    public Map<String, Object> evaluateTreatmentRules(Map<String, Object> treatmentData) {
        // 执行各种规则检查...
        Map<String, Object> result = new HashMap<>();
        result.put("rulesPassed", true);
        result.put("warningFlags", new String[]{});
        return result;
    }
    
    private Map<String, Object> fetchTreatmentData(String mdtrtId) {
        // 从数据采集服务获取数据
        return restTemplate.getForObject(
            "http://localhost:8084/api/data/treatments/" + mdtrtId,
            Map.class
        );
    }
    
    public Map<String, Object> batchEvaluate(List<Map<String, Object>> feeDetails, String checkType) {
        List<Map<String, Object>> abnormalItems = new ArrayList<>();
        Map<String, List<Map<String, Object>>> doctorFeeMap = new HashMap<>();
        
        // 对每个费用条目应用规则
        for (Map<String, Object> feeDetail : feeDetails) {
            // 应用各种规则检查
            List<String> violations = applyRules(feeDetail);
            boolean isAbnormal = !violations.isEmpty();
            
            if (isAbnormal) {
                feeDetail.put("violations", violations);
                abnormalItems.add(feeDetail);
            }
            
            // 按医生分组，为后续深度分析准备
            String doctorId = (String) feeDetail.get("doctorId");
            doctorFeeMap.computeIfAbsent(doctorId, k -> new ArrayList<>()).add(feeDetail);
        }
        
        // 保存审核结果到单独的表(而不是更新原始表)
        for (Map<String, Object> abnormalItem : abnormalItems) {
            String feeDetailId = (String) abnormalItem.get("feeDetailId");
            List<String> violations = (List<String>) abnormalItem.get("violations");
            
            // 记录审核结果
            feeAuditRepository.saveAuditResult(
                feeDetailId, 
                true, // isAbnormal
                violations.size()
            );
            
            // 记录详细违规信息
            for (String violation : violations) {
                violationRepository.saveViolation(
                    feeDetailId, 
                    violation, 
                    getViolationDescription(violation)
                );
            }
        }
        
        // 对于正常条目，也记录审核结果（可选）
        for (Map<String, Object> feeDetail : feeDetails) {
            String feeDetailId = (String) feeDetail.get("feeDetailId");
            if (!feeDetail.containsKey("violations")) {
                feeAuditRepository.saveAuditResult(feeDetailId, false, 0);
            }
        }
        
        // 生成结果
        Map<String, Object> checkResult = createCheckResult(feeDetails, abnormalItems, doctorFeeMap);
        
        // 发布事件通知其他服务
        eventPublisher.publishEvent("RULE_CHECKING_COMPLETED", checkResult);
        
        return checkResult;
    }
    
    private String getViolationDescription(String violation) {
        // Implementation of getViolationDescription method
        return "Description of the violation";
    }
    
    private Map<String, Object> createCheckResult(List<Map<String, Object>> feeDetails, List<Map<String, Object>> abnormalItems, Map<String, List<Map<String, Object>>> doctorFeeMap) {
        // Implementation of createCheckResult method
        return new HashMap<>();
    }
} 