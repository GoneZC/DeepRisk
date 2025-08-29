package com.demo.model;

import jakarta.persistence.*;
import java.math.BigDecimal;

@Entity
@Table(name = "doctor_fraud_scores")
public class DoctorFraudScore {
    
    @Id
    @Column(name = "doctor_id")
    private String doctorId;
    
    @Column(name = "fraud_score", precision = 5, scale = 2)
    private BigDecimal fraudScore;
    
    // 构造函数
    public DoctorFraudScore() {
    }
    
    public DoctorFraudScore(String doctorId, BigDecimal fraudScore) {
        this.doctorId = doctorId;
        this.fraudScore = fraudScore;
    }
    
    // Getters和Setters
    public String getDoctorId() {
        return doctorId;
    }
    
    public void setDoctorId(String doctorId) {
        this.doctorId = doctorId;
    }
    
    public BigDecimal getFraudScore() {
        return fraudScore;
    }
    
    public void setFraudScore(BigDecimal fraudScore) {
        this.fraudScore = fraudScore;
    }
}