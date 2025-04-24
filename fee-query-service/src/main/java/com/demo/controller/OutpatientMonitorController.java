package com.demo.controller;

import com.demo.dto.OutpatientMonitorDTO;
import com.demo.dto.OutpatientQueryDTO;
import com.demo.service.OutpatientMonitorService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/outpatient-monitor")
public class OutpatientMonitorController {

    @Autowired
    private OutpatientMonitorService outpatientMonitorService;
    
    /**
     * 获取门诊监管数据
     */
    @PostMapping("/search")
    public ResponseEntity<Page<OutpatientMonitorDTO>> searchOutpatientData(@RequestBody OutpatientQueryDTO queryDTO) {
        System.out.println("收到查询参数: " + queryDTO);  // 添加日志帮助调试
        Page<OutpatientMonitorDTO> result = outpatientMonitorService.getOutpatientMonitorData(queryDTO);
        return ResponseEntity.ok(result);
    }
    
    /**
     * 更新医生风险评估结果
     */
    @PostMapping("/update-risk/{doctorId}")
    public ResponseEntity<OutpatientMonitorDTO> updateRiskLevel(
            @PathVariable String doctorId,
            @RequestBody Map<String, String> requestBody) {
        
        String riskLevel = requestBody.get("riskLevel");
        OutpatientMonitorDTO updated = outpatientMonitorService.updateDoctorRiskLevel(doctorId, riskLevel);
        
        if (updated != null) {
            return ResponseEntity.ok(updated);
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 获取医生详情
     */
    @GetMapping("/doctor-details/{doctorId}")
    public ResponseEntity<OutpatientMonitorDTO> getDoctorDetails(@PathVariable String doctorId) {
        OutpatientQueryDTO queryDTO = new OutpatientQueryDTO();
        queryDTO.setDoctorId(doctorId);
        queryDTO.setPage(0);
        queryDTO.setSize(1);
        
        Page<OutpatientMonitorDTO> result = outpatientMonitorService.getOutpatientMonitorData(queryDTO);
        
        if (result.hasContent()) {
            return ResponseEntity.ok(result.getContent().get(0));
        } else {
            return ResponseEntity.notFound().build();
        }
    }
} 