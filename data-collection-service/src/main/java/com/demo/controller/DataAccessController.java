package com.demo.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.demo.service.DataAccessService;
import com.demo.service.DataQueryService;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.Optional;

@RestController
@RequestMapping("/access")
public class DataAccessController {

    @Autowired
    private DataAccessService dataAccessService;
    
    @Autowired
    private DataQueryService dataQueryService;
    
    // 获取医生数据
    @GetMapping("/doctors/{doctorId}")
    public ResponseEntity<Map<String, Object>> getDoctorData(
            @PathVariable String doctorId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        
        if (startDate == null) startDate = LocalDate.now().minusMonths(3);
        if (endDate == null) endDate = LocalDate.now();
        
        return ResponseEntity.ok(dataAccessService.getDoctorData(doctorId, startDate, endDate));
    }
    
    // 批量获取医生数据
    @GetMapping("/doctors/batch")
    public ResponseEntity<Map<String, Map<String, Object>>> getDoctorsBatchData(
            @RequestParam List<String> ids,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        
        if (startDate == null) startDate = LocalDate.now().minusMonths(3);
        if (endDate == null) endDate = LocalDate.now();
        
        return ResponseEntity.ok(dataAccessService.getDoctorsBatchData(ids, startDate, endDate));
    }
    
    // 获取医疗机构数据
    @GetMapping("/providers/{providerId}")
    public ResponseEntity<Map<String, Object>> getProviderData(
            @PathVariable String providerId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        
        if (startDate == null) startDate = LocalDate.now().minusMonths(3);
        if (endDate == null) endDate = LocalDate.now();
        
        return ResponseEntity.ok(dataAccessService.getProviderData(providerId, startDate, endDate));
    }
    
    // 获取费用数据
    @GetMapping("/fees")
    public ResponseEntity<List<Map<String, Object>>> getFeeData(
            @RequestParam(required = false) String hospitalId,
            @RequestParam(required = false) String patientId,
            @RequestParam(required = false) LocalDate startDate,
            @RequestParam(required = false) LocalDate endDate,
            @RequestParam(required = false) Double minAmount) {
        
        // 调用服务处理数据请求
        List<Map<String, Object>> results = dataAccessService.getFeeData(
                hospitalId, patientId, startDate, endDate, minAmount);
        
        return ResponseEntity.ok(results);
    }
    
    // 获取统计数据
    @GetMapping("/statistics/{entityType}")
    public ResponseEntity<Map<String, Object>> getStatistics(
            @PathVariable String entityType,
            @RequestParam String id,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        
        if (startDate == null) startDate = LocalDate.now().minusMonths(6);
        if (endDate == null) endDate = LocalDate.now();
        
        return ResponseEntity.ok(dataAccessService.getStatistics(entityType, id, startDate, endDate));
    }
    
    // 异步查询API
    @PostMapping("/fees/async")
    public ResponseEntity<Map<String, String>> submitFeeQuery(
            @RequestBody Map<String, Object> queryParams) {
        
        String queryId = dataQueryService.submitComplexQuery(queryParams);
        
        Map<String, String> response = new HashMap<>();
        response.put("queryId", queryId);
        response.put("status", "SUBMITTED");
        
        return ResponseEntity.accepted().body(response);
    }
    
    // 查询结果获取接口
    @GetMapping("/query-results/{queryId}")
    public ResponseEntity<?> getQueryResult(@PathVariable String queryId) {
        Optional<Object> result = dataQueryService.getQueryResult(queryId);
        
        if (result.isPresent()) {
            return ResponseEntity.ok(result.get());
        } else {
            Map<String, String> response = new HashMap<>();
            response.put("queryId", queryId);
            response.put("status", "PROCESSING");
            return ResponseEntity.ok(response);
        }
    }
} 