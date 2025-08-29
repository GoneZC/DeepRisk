package com.demo.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import com.demo.model.FeeDetail;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "费用明细查询响应")
public class FeeDetailResponse {
    
    @Schema(description = "费用明细列表")
    private List<FeeDetail> data;
    
    @Schema(description = "总记录数", example = "1250")
    private Long totalElements;
    
    @Schema(description = "总页数", example = "125")
    private Integer totalPages;
    
    @Schema(description = "当前页码", example = "1")
    private Integer currentPage;
    
    @Schema(description = "每页大小", example = "10")
    private Integer pageSize;
    
    @Schema(description = "最早费用发生时间")
    private LocalDateTime earliestTime;
    
    @Schema(description = "最晚费用发生时间")
    private LocalDateTime latestTime;
    
    @Schema(description = "时间跨度描述", example = "30天5小时")
    private String timeSpan;
    
    @Schema(description = "医疗类别", example = "11")
    private String medType;
} 