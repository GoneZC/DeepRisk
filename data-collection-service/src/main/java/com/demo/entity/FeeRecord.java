package com.demo.entity;

import lombok.Data;

import javax.persistence.*;
import java.math.BigDecimal;
import java.util.Date;

@Data
@Entity
@Table(name = "fee_list_d2409")
public class FeeRecord {
    @Id
    @Column(name = "ID")
    private Long id;
    
    @Column(name = "BKKP_SN")
    private String bkkpSn;
    
    @Column(name = "MDTRT_ID")
    private String mdtrtId;
    
    @Column(name = "PSN_NO")
    private String psnNo;
    
    @Column(name = "DET_ITEM_FEE_SUMAMT")
    private BigDecimal detItemFeeSumamt;
    
    @Column(name = "PRIC")
    private BigDecimal pric;
    
    @Column(name = "PRIC_UPLMT_AMT")
    private BigDecimal pricUplmtAmt;
    
    @Column(name = "SELFPAY_PROP")
    private BigDecimal selfpayProp;
    
    @Column(name = "MED_TYPE")
    private String medType;
    
    @Column(name = "HILIST_CODE")
    private String hilistCode;
    
    @Column(name = "HILIST_NAME")
    private String hilistName;
    
    @Column(name = "MEDINS_LIST_CODG")
    private String medinsListCodg;
    
    @Column(name = "CREATE_TIME")
    @Temporal(TemporalType.TIMESTAMP)
    private Date createTime;
} 