package com.demo.model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Column;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "doctor_community")
@Data                   
@NoArgsConstructor      
@AllArgsConstructor     
public class DoctorCommunity {
    
    @Id
    @Column(name = "BILG_DR_CODE")
    private String bilgDrCode;
    
    @Column(name = "COM_ID")
    private String comId;
    
    @Column(name = "COM_NAME")
    private String comName;
    
    @Column(name = "COM_DRUG")
    private String comDrug;
} 