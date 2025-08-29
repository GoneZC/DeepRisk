package com.demo.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name = "doctor_monitor_view")
public class DoctorMonitorData {
    
    @Id
    @Column(name = "BILG_DR_CODE")
    private String doctorId;
    
    @Column(name = "FIXMEDINS_CODE")
    private String hospitalCode;
    
    @Column(name = "COM_NAME")
    private String community;
    
    @Column(name = "BILG_DEPT_NAME")
    private String department;
    
    @Column(name = "prescription_count")
    private Integer prescriptionCount;
    
    @Column(name = "total_cost")
    private BigDecimal totalCost;
    
    @Column(name = "prescription_date")
    private LocalDate prescriptionDate;
    
    @Column(name = "COM_DRUG")
    private String communityDrugs;
    
    @Column(name = "FRAUD_RISK")
    private String fraudRisk;
    
    // 构造函数
    public DoctorMonitorData() {
    }
    
    // Getters和Setters
    public String getDoctorId() {
        return doctorId;
    }
    
    public void setDoctorId(String doctorId) {
        this.doctorId = doctorId;
    }
    
    public String getHospitalCode() {
        return hospitalCode;
    }
    
    public void setHospitalCode(String hospitalCode) {
        this.hospitalCode = hospitalCode;
    }
    
    public String getCommunity() {
        return community;
    }
    
    public void setCommunity(String community) {
        this.community = community;
    }
    
    public String getDepartment() {
        return department;
    }
    
    public void setDepartment(String department) {
        this.department = department;
    }
    
    public Integer getPrescriptionCount() {
        return prescriptionCount;
    }
    
    public void setPrescriptionCount(Integer prescriptionCount) {
        this.prescriptionCount = prescriptionCount;
    }
    
    public BigDecimal getTotalCost() {
        return totalCost;
    }
    
    public void setTotalCost(BigDecimal totalCost) {
        this.totalCost = totalCost;
    }
    
    public LocalDate getPrescriptionDate() {
        return prescriptionDate;
    }
    
    public void setPrescriptionDate(LocalDate prescriptionDate) {
        this.prescriptionDate = prescriptionDate;
    }
    
    public String getCommunityDrugs() {
        return communityDrugs;
    }
    
    public void setCommunityDrugs(String communityDrugs) {
        this.communityDrugs = communityDrugs;
    }
    
    public String getFraudRisk() {
        return fraudRisk;
    }
    
    public void setFraudRisk(String fraudRisk) {
        this.fraudRisk = fraudRisk;
    }
}