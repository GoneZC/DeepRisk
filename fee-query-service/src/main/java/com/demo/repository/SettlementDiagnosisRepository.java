package com.demo.repository;

import com.demo.model.SettlementDiagnosis;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface SettlementDiagnosisRepository extends JpaRepository<SettlementDiagnosis, String> {
    List<SettlementDiagnosis> findByMdtrtIdOrderByDiagSrtNoAsc(String mdtrtId);
} 