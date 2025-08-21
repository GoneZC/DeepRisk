package com.demo.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.io.Serializable;
import io.swagger.v3.oas.annotations.media.Schema;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "fee_list_d2409", indexes = {
    @Index(name = "idx_mdtrt_id", columnList = "MDTRT_ID")
})
@Schema(description = "医保费用明细")
public class FeeDetail implements Serializable {
    private static final long serialVersionUID = 2L;
    
    @Schema(description = "就诊ID", example = "3202411010001")
    @Column(name = "MDTRT_ID")
    private String mdtrtId;
    
    @Schema(description = "医疗类别", example = "11")
    @Column(name = "MED_TYPE", length = 3)
    private String medType;
    
    @Schema(description = "数量", example = "1.00")
    @Column(name = "CNT", precision = 10, scale = 2)
    private BigDecimal cnt;
    
    @Schema(description = "单价", example = "15.50")
    @Column(name = "PRIC", precision = 10, scale = 2)
    private BigDecimal pric;
    
    @Schema(description = "费用发生时间")
    @Column(name = "FEE_OCUR_TIME")
    private LocalDateTime feeOcurTime;
    
    @Schema(description = "记账流水号", example = "20241101001")
    @Id
    @Column(name = "BKKP_SN", length = 30)
    private String bkkpSn;
    
    @Schema(description = "医保目录名称", example = "阿莫西林胶囊")
    @Column(name = "HILIST_NAME", length = 100)
    private String hilistName;
    
    @Column(name = "DET_ITEM_FEE_SUMAMT", precision = 12, scale = 2)
    private BigDecimal detItemFeeSumamt;
    
    @Column(name = "PRIC_UPLMT_AMT", precision = 12, scale = 2)
    private BigDecimal pricUplmtAmt;
    
    @Column(name = "SELFPAY_PROP", precision = 5, scale = 2)
    private BigDecimal selfpayProp;
    
    @Column(name = "FULAMT_OWNPAY_AMT", precision = 12, scale = 2)
    private BigDecimal fulamtOwnpayAmt;
    
    @Column(name = "OVERLMT_SELFPAY", precision = 12, scale = 2)
    private BigDecimal overlmtSelfpay;
    
    @Column(name = "PRESELFPAY_AMT", precision = 12, scale = 2)
    private BigDecimal preselfpayAmt;
    
    @Column(name = "INSCP_AMT", precision = 12, scale = 2)
    private BigDecimal inscpAmt;
    
    @Column(name = "REIM_PROP", precision = 5, scale = 2)
    private BigDecimal reimProp;
    
    @Column(name = "FIXMEDINS_CODE", length = 30)
    private String fixmedinsCode;
    
    public String getHospitalId() {
        return this.fixmedinsCode;
    }
    
    public void setHospitalId(String hospitalId) {
        this.fixmedinsCode = hospitalId;
    }
} 