package com.demo.controller;

import com.demo.model.FeeDetail;
import com.demo.service.FeeDetailService;
import com.demo.dto.FeeDetailRequest;
import com.demo.dto.FeeDetailResponse;
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

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;

@RestController
@RequestMapping("/api")
@Tag(name = "费用明细管理", description = "医保费用明细查询相关接口")
public class FeeDetailController {
    private static final Logger logger = LoggerFactory.getLogger(FeeDetailController.class);
    
    @Autowired
    private FeeDetailService feeDetailService;
    
    @Operation(summary = "分页查询费用明细", 
               description = "根据就诊ID分页查询医保费用明细信息，支持排序和时间统计")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "查询成功",
            content = @Content(mediaType = "application/json",
                schema = @Schema(implementation = FeeDetailResponse.class))),
        @ApiResponse(responseCode = "400", description = "参数错误"),
        @ApiResponse(responseCode = "500", description = "服务器内部错误")
    })
    @PostMapping("/fee-details")
    public ResponseEntity<Map<String, Object>> getFeeDetails(
            @io.swagger.v3.oas.annotations.parameters.RequestBody(
                description = "查询参数，包含就诊ID、分页信息等",
                content = @Content(schema = @Schema(implementation = FeeDetailRequest.class))
            )
            @RequestBody Map<String, Object> params) {
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

    @Operation(summary = "根据就诊ID查询所有费用明细", 
               description = "获取指定就诊ID的所有费用明细，不分页")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "查询成功",
            content = @Content(mediaType = "application/json",
                schema = @Schema(implementation = FeeDetail.class))),
        @ApiResponse(responseCode = "404", description = "未找到数据"),
        @ApiResponse(responseCode = "500", description = "服务器内部错误")
    })
    @GetMapping("/fee-details/{mdtrtId}")
    public ResponseEntity<List<FeeDetail>> getFeeDetailsByMdtrtId(
            @Parameter(description = "就诊ID", example = "3202411010001", required = true)
            @PathVariable String mdtrtId) {
        List<FeeDetail> feeDetails = feeDetailService.getFeeDetails(mdtrtId);
        return ResponseEntity.ok(feeDetails);
    }
} 