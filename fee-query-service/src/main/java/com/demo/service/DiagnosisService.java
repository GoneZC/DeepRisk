package com.demo.service;

import com.demo.model.SettlementDiagnosis;
import com.demo.repository.SettlementDiagnosisRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Service
public class DiagnosisService {

    @Autowired
    private SettlementDiagnosisRepository diagnosisRepository;
    
    @Transactional(readOnly = true)
    public List<SettlementDiagnosis> getDiagnosisByMdtrtId(String mdtrtId) {
        return diagnosisRepository.findByMdtrtIdOrderByDiagSrtNoAsc(mdtrtId);
    }
} 