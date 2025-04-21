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
@Table(name = "setl_d2409", indexes = {
    @Index(name = "idx_query_optimize_mdtrt", 
           columnList = "mdtrt_id, begndate DESC, setl_id"),
    @Index(name = "idx_query_optimize_medtype", 
           columnList = "med_type, begndate DESC")
})
public class Settlement implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @Column(name = "setl_id", length = 20)
    private String setlId;

    @Column(name = "mdtrt_id", length = 20)
    private String mdtrtId;
    
    @Column(name = "psn_no", length = 30)
    private String psnNo;
    
    @Column(name = "gend", length = 1)
    private String gend;
    
    @Column(name = "age")
    private Integer age;
    
    @Column(name = "dise_name", length = 100)
    private String diseName;

    @Column(name = "FIXMEDINS_CODE", length = 20)
    private String fixmedinsCode;
    
    @Column(name = "med_type", length = 6)
    private String medType;
    
    @Column(name = "begndate", columnDefinition = "TIMESTAMP COMMENT '就诊开始时间'")
    private LocalDateTime begndate;
    
    @Column(name = "enddate")
    private LocalDateTime enddate;

    @Column(name = "MEDFEE_SUMAMT", precision = 15, scale = 2)
    private BigDecimal medfeeSumamt;

    @Column(name = "FULAMT_OWNPAY_AMT", precision = 15, scale = 2)
    private BigDecimal fulamtOwnpayAmt;
    
    @Column(name = "HIFP_PAY", precision = 15, scale = 2)
    private BigDecimal hifpPay;

    @Column(name = "SETL_TIME")
    private LocalDateTime setlTime;

    @Column(name = "OVERLMT_SELFPAY", precision = 15, scale = 2)
    private BigDecimal overlmtSelfpay;
} 