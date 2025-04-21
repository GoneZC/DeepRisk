package com.demo.controller;

import com.demo.model.FeeDetail;
import com.demo.service.FeeDetailService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class FeeDetailController {
    private static final Logger logger = LoggerFactory.getLogger(FeeDetailController.class);
    
    @Autowired
    private FeeDetailService feeDetailService;
    
    @PostMapping("/fee-details")
    public ResponseEntity<Map<String, Object>> getFeeDetails(@RequestBody Map<String, Object> params) {
        String mdtrtId = params.get("mdtrtId").toString();
        
        // 获取分页参数，默认第1页，每页10条
        int page = 0; // JPA页码从0开始
        int size = 10;
        
        try {
            if (params.containsKey("page")) {
                if (params.get("page") instanceof Number) {
                    page = ((Number) params.get("page")).intValue() - 1; // 前端从1开始，转为从0开始
                } else {
                    page = Integer.parseInt(params.get("page").toString()) - 1;
                }
            }
            if (params.containsKey("size")) {
                if (params.get("size") instanceof Number) {
                    size = ((Number) params.get("size")).intValue();
                } else {
                    size = Integer.parseInt(params.get("size").toString());
                }
            }
        } catch (Exception e) {
            logger.warn("解析分页参数出错，使用默认值", e);
        }
        
        logger.info("查询费用明细，就诊ID: {}, 页码: {}, 每页条数: {}", mdtrtId, page + 1, size);
        
        // 先获取所有数据，用于统计和信息获取
        List<FeeDetail> allFeeDetails = feeDetailService.getFeeDetails(mdtrtId);
        
        // 再获取分页数据
        Page<FeeDetail> feeDetailsPage = feeDetailService.getFeeDetailsPaged(mdtrtId, page, size);
        
        Map<String, Object> response = new HashMap<>();
        
        // 设置分页数据
        response.put("data", feeDetailsPage.getContent());
        response.put("totalElements", feeDetailsPage.getTotalElements());
        response.put("totalPages", feeDetailsPage.getTotalPages());
        response.put("currentPage", feeDetailsPage.getNumber() + 1); // 转回前端从1开始的页码
        response.put("pageSize", feeDetailsPage.getSize());
        
        // 计算时间跨度
        if (!allFeeDetails.isEmpty()) {
            // 查找最早和最晚时间
            LocalDateTime earliestTime = allFeeDetails.stream()
                .filter(detail -> detail.getFeeOcurTime() != null)
                .min(Comparator.comparing(FeeDetail::getFeeOcurTime))
                .map(FeeDetail::getFeeOcurTime)
                .orElse(null);
                
            LocalDateTime latestTime = allFeeDetails.stream()
                .filter(detail -> detail.getFeeOcurTime() != null)
                .max(Comparator.comparing(FeeDetail::getFeeOcurTime))
                .map(FeeDetail::getFeeOcurTime)
                .orElse(null);
            
            if (earliestTime != null && latestTime != null) {
                long days = ChronoUnit.DAYS.between(earliestTime, latestTime);
                long hours = ChronoUnit.HOURS.between(earliestTime, latestTime) % 24;
                
                response.put("earliestTime", earliestTime);
                response.put("latestTime", latestTime);
                response.put("timeSpan", String.format("%d天%d小时", days, hours));
            }
            
            // 提取医疗类别（假设所有记录有相同的医疗类别）
            String medType = allFeeDetails.stream()
                .filter(detail -> detail.getMedType() != null && !detail.getMedType().isEmpty())
                .map(FeeDetail::getMedType)
                .findFirst()
                .orElse("");
                
            response.put("medType", medType);
        }
        
        return ResponseEntity.ok(response);
    }

    @GetMapping("/fee-details/{mdtrtId}")
    public ResponseEntity<List<FeeDetail>> getFeeDetailsByMdtrtId(@PathVariable String mdtrtId) {
        List<FeeDetail> feeDetails = feeDetailService.getFeeDetails(mdtrtId);
        return ResponseEntity.ok(feeDetails);
    }
} 