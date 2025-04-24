package com.demo.dto;

import java.time.LocalDate;

public class OutpatientQueryDTO {
    private String doctorId;
    private String community;
    private String hospitalCode;
    private String department;
    private LocalDate startDate;
    private LocalDate endDate;
    private Integer page;
    private Integer size;
    
    public OutpatientQueryDTO() {
    }
    
    // Getters and Setters
    public String getDoctorId() {
        return doctorId;
    }

    public void setDoctorId(String doctorId) {
        this.doctorId = doctorId;
    }

    public String getCommunity() {
        return community;
    }

    public void setCommunity(String community) {
        this.community = community;
    }

    public String getHospitalCode() {
        return hospitalCode;
    }

    public void setHospitalCode(String hospitalCode) {
        this.hospitalCode = hospitalCode;
    }

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
    }

    public LocalDate getStartDate() {
        return startDate;
    }

    public void setStartDate(LocalDate startDate) {
        this.startDate = startDate;
    }

    public LocalDate getEndDate() {
        return endDate;
    }

    public void setEndDate(LocalDate endDate) {
        this.endDate = endDate;
    }

    public Integer getPage() {
        return page;
    }

    public void setPage(Integer page) {
        this.page = page;
    }

    public Integer getSize() {
        return size;
    }

    public void setSize(Integer size) {
        this.size = size;
    }

    @Override
    public String toString() {
        return "OutpatientQueryDTO{" +
                "doctorId='" + doctorId + '\'' +
                ", community='" + community + '\'' +
                ", hospitalCode='" + hospitalCode + '\'' +
                ", department='" + department + '\'' +
                ", startDate=" + startDate +
                ", endDate=" + endDate +
                ", page=" + page +
                ", size=" + size +
                '}';
    }
} 