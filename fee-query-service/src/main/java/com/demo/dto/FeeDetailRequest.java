package com.demo.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "费用明细查询请求")
public class FeeDetailRequest {
    
    @Schema(description = "就诊ID", example = "3202411010001", required = true)
    private String mdtrtId;
    
    @Schema(description = "页码，从1开始", example = "1", defaultValue = "1")
    private Integer page = 1;
    
    @Schema(description = "每页大小，最大100", example = "10", defaultValue = "10")
    private Integer size = 10;
    
    @Schema(description = "排序字段", example = "feeOcurTime", defaultValue = "feeOcurTime")
    private String sortBy = "feeOcurTime";
    
    @Schema(description = "排序方向", example = "ASC", allowableValues = {"ASC", "DESC"}, defaultValue = "ASC")
    private String sortDirection = "ASC";
} 