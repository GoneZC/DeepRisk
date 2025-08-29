package com.demo.dto;

import java.math.BigDecimal;
import java.time.LocalDate;

public class OutpatientMonitorDTO {
    private String doctorId;
    private String hospitalCode;
    private String community;
    private String department;
    private Integer prescriptionCount;
    private BigDecimal totalCost;
    private LocalDate prescriptionDate;
    private String fraudRisk;
    private String comDrug;
    
    public OutpatientMonitorDTO() {
    }
    
    public OutpatientMonitorDTO(String doctorId, String hospitalCode, String community, 
                               String department, Integer prescriptionCount, 
                               BigDecimal totalCost, LocalDate prescriptionDate,
                               String comDrug) {
        this.doctorId = doctorId;
        this.hospitalCode = hospitalCode;
        this.community = community;
        this.department = department;
        this.prescriptionCount = prescriptionCount;
        this.totalCost = totalCost;
        this.prescriptionDate = prescriptionDate;
        this.fraudRisk = null; // 默认未评估
        this.comDrug = comDrug;
    }

    // Getters and Setters
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

    public String getFraudRisk() {
        return fraudRisk;
    }

    public void setFraudRisk(String fraudRisk) {
        this.fraudRisk = fraudRisk;
    }

    public String getComDrug() {
        return comDrug;
    }

    public void setComDrug(String comDrug) {
        this.comDrug = comDrug;
    }
} 