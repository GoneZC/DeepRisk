package com.demo.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.io.Serializable;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "fee_list_d2409", indexes = {
    @Index(name = "idx_mdtrt_id", columnList = "MDTRT_ID")
})
public class FeeDetail implements Serializable {
    private static final long serialVersionUID = 2L;
    
    @Column(name = "MDTRT_ID")
    private String mdtrtId;
    
    @Column(name = "MED_TYPE", length = 3)
    private String medType;
    
    @Column(name = "CNT", precision = 10, scale = 2)
    private BigDecimal cnt;
    
    @Column(name = "PRIC", precision = 10, scale = 2)
    private BigDecimal pric;
    
    @Column(name = "FEE_OCUR_TIME")
    private LocalDateTime feeOcurTime;
    
    @Id
    @Column(name = "BKKP_SN", length = 30)
    private String bkkpSn;
    
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