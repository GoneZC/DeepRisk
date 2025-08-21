package com.demo.entity;

import lombok.Data;
import javax.persistence.*;
import java.math.BigDecimal;
import java.util.Date;

@Data
@Entity
@Table(name = "medical_data")
public class MedicalData {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "patient_id")
    private String patientId;
    
    @Column(name = "hospital_code")
    private String hospitalCode;
    
    @Column(name = "total_fee")
    private BigDecimal totalFee;
    
    @Column(name = "self_pay_ratio")
    private Double selfPayRatio;
    
    @Column(name = "create_time")
    @Temporal(TemporalType.TIMESTAMP)
    private Date createTime;
} 