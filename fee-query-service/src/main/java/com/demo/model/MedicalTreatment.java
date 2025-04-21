package com.demo.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.io.Serializable;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "mdtrt_d2409")
public class MedicalTreatment implements Serializable {
    private static final long serialVersionUID = 3L;

    @Id
    @Column(name = "MDTRT_ID", length = 20)
    private String mdtrtId;

    @Column(name = "MEDINS_SETL_ID", length = 20)
    private String medinsSetlId;

    @Column(name = "PSN_NO", length = 20)
    private String psnNo;

    @Column(name = "PSN_INSU_RLTS_ID", length = 20)
    private String psnInsuRltsId;

    @Column(name = "PSN_CERT_TYPE", length = 3)
    private String psnCertType;

    @Column(name = "GEND", length = 1)
    private String gend;

    @Column(name = "NATY", length = 3)
    private String naty;

    @Column(name = "BRDY")
    private LocalDateTime brdy;


} 