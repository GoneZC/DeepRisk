package com.demo.controller;

import com.demo.dto.OutpatientMonitorDTO;
import com.demo.service.OutpatientMonitorService;
import com.demo.repository.DoctorFraudScoreRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;

/**
 * 异步风险评估控制器
 * 处理来自分析服务的风险评估结果回调
 */
@RestController
@RequestMapping("/async-risk-assessment")
public class AsyncRiskAssessmentController {
    
    private static final Logger logger = Logger.getLogger(AsyncRiskAssessmentController.class.getName());
    
    // 用于存储异步风险评估结果的临时存储
    private static final Map<String, Map<String, Object>> assessmentResults = new ConcurrentHashMap<>();
    
    @Autowired
    private OutpatientMonitorService outpatientMonitorService;
    
    @Autowired
    private DoctorFraudScoreRepository doctorFraudScoreRepository;
    
    /**
     * 接收分析服务发送的风险评估结果
     */
    @PostMapping("/result")
    public ResponseEntity<String> receiveRiskAssessmentResult(@RequestBody Map<String, Object> result) {
        try {
            logger.info("收到风险评估结果: " + result);
            
            String requestId = (String) result.get("requestId");
            String doctorId = (String) result.get("doctorId");
            String status = (String) result.get("status");
            
            if (requestId == null || requestId.isEmpty()) {
                logger.warning("收到的风险评估结果缺少requestId");
                return ResponseEntity.badRequest().body("缺少requestId");
            }
            
            // 存储结果以便后续查询
            assessmentResults.put(requestId, result);
            
            // 如果有医生ID，更新医生的风险等级
            if (doctorId != null && !doctorId.isEmpty() && status != null) {
                String riskLevel = "正常";
                
                // 根据欺诈分数确定风险等级
                Object fraudScoreObj = result.get("fraudScore");
                if (fraudScoreObj != null) {
                    try {
                        double fraudScore = Double.parseDouble(fraudScoreObj.toString());
                        if (fraudScore >= 0.8) {
                            riskLevel = "高风险";
                        } else if (fraudScore >= 0.5) {
                            riskLevel = "中风险";
                        } else if (fraudScore >= 0.2) {
                            riskLevel = "低风险";
                        }
                        
                        // 保存欺诈评分到数据库
                        try {
                            doctorFraudScoreRepository.upsertDoctorFraudScore(doctorId, String.valueOf(fraudScore));
                            logger.info("医生 " + doctorId + " 的欺诈评分已保存到数据库: " + fraudScore);
                        } catch (Exception e) {
                            logger.warning("保存医生 " + doctorId + " 的欺诈评分到数据库时出错: " + e.getMessage());
                        }
                    } catch (NumberFormatException e) {
                        logger.warning("无法解析欺诈分数: " + fraudScoreObj);
                    }
                }
                
                // 更新医生风险等级
                OutpatientMonitorDTO updated = outpatientMonitorService.updateDoctorRiskLevel(doctorId, riskLevel);
                if (updated != null) {
                    logger.info("成功更新医生 " + doctorId + " 的风险等级为 " + riskLevel);
                } else {
                    logger.warning("未能更新医生 " + doctorId + " 的风险等级");
                }
            }
            
            logger.info("风险评估结果处理完成，请求ID: " + requestId);
            return ResponseEntity.ok("结果已接收并处理");
        } catch (Exception e) {
            logger.severe("处理风险评估结果时出错: " + e.getMessage());
            return ResponseEntity.status(500).body("处理结果时出错: " + e.getMessage());
        }
    }
    
    /**
     * 查询异步风险评估结果
     * 客户端可以通过这个端点查询评估结果
     */
    @GetMapping("/{requestId}")
    public ResponseEntity<Map<String, Object>> getRiskAssessmentResult(@PathVariable String requestId) {
        Map<String, Object> result = assessmentResults.get(requestId);
        if (result == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(result);
    }
    
    /**
     * 获取所有存储的结果（用于调试）
     */
    @GetMapping("/all-results")
    public ResponseEntity<Map<String, Map<String, Object>>> getAllResults() {
        return ResponseEntity.ok(assessmentResults);
    }
}