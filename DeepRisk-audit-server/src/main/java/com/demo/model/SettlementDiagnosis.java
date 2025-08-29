package com.demo.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "setl_diag_list_d_2409", indexes = {
    @Index(name = "idx_mdtrt_diag", columnList = "mdtrt_id, diag_srt_no")
})
public class SettlementDiagnosis {

    @Id
    @Column(name = "diag_info_id")
    private String id;
    
    @Column(name = "mdtrt_id", length = 20)
    private String mdtrtId;
    
    @Column(name = "inout_diag_type")
    private String inoutDiagType;
    
    @Column(name = "diag_type")
    private String diagType;
    
    @Column(name = "maindiag_flag")
    private String maindiagFlag;
    
    @Column(name = "diag_srt_no")
    private Integer diagSrtNo;
    
    @Column(name = "diag_name")
    private String diagName;
    
    @Column(name = "adm_cond")
    private String admCond;
    
    @Column(name = "diag_dept")
    private String diagDept;
    
    @Column(name = "diag_time")
    private LocalDateTime diagTime;
} 