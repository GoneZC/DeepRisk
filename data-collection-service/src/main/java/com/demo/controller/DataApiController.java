package com.demo.controller;

import com.demo.service.DataCollectionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/data")
public class DataApiController {
    
    @Autowired
    private DataCollectionService dataService;
    
    @Autowired
    private AsyncTaskService asyncTaskService;
    
    @GetMapping("/treatments/{mdtrtId}")
    public Map<String, Object> getTreatmentData(@PathVariable String mdtrtId) {
        return dataService.getMedicalTreatment(mdtrtId);
    }
    
    @GetMapping("/patients/{patientId}/records")
    public List<Map<String, Object>> getPatientRecords(@PathVariable String patientId) {
        return dataService.getMedicalRecords(patientId);
    }
    
    @PostMapping("/treatments/fee-details/batch")
    public Map<String, Object> receiveDailyFeeDetails(@RequestBody List<Map<String, Object>> feeDetails) {
        // 保存费用明细到数据库
        int processedRecords = dataService.saveFeeDetails(feeDetails);
        
        // 异步触发规则引擎检查
        asyncTaskService.triggerRuleEngineCheck(feeDetails);
        
        return createResponse("success", feeDetails.size(), processedRecords);
    }
    
    private Map<String, Object> createResponse(String status, int totalRecords, int processedRecords) {
        Map<String, Object> response = new HashMap<>();
        response.put("status", status);
        response.put("totalRecords", totalRecords);
        response.put("processedRecords", processedRecords);
        return response;
    }
} 