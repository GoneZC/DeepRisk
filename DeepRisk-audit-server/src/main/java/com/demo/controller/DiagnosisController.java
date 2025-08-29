package com.demo.controller;

import com.demo.model.SettlementDiagnosis;
import com.demo.service.DiagnosisService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api")
public class DiagnosisController {
    
    @Autowired
    private DiagnosisService diagnosisService;
    
    // 查询诊断详情
    @GetMapping("/diagnosis-details/{mdtrtId}")
    public ResponseEntity<?> getDiagnosisDetails(@PathVariable String mdtrtId) {
        try {
            List<SettlementDiagnosis> details = diagnosisService.getDiagnosisByMdtrtId(mdtrtId);
            return ResponseEntity.ok(details);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body("查询失败");
        }
    }
} 