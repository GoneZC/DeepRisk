package com.demo.repository;

import com.demo.model.DoctorFraudScore;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

@Repository
public interface DoctorFraudScoreRepository extends JpaRepository<DoctorFraudScore, String> {
    
    /**
     * 插入或更新医生欺诈评分
     * 使用原生SQL实现INSERT ... ON DUPLICATE KEY UPDATE功能
     */
    @Modifying
    @Transactional
    @Query(value = "INSERT INTO doctor_fraud_scores (doctor_id, fraud_score) VALUES (:doctorId, :fraudScore) " +
                   "ON DUPLICATE KEY UPDATE fraud_score = VALUES(fraud_score)", nativeQuery = true)
    void upsertDoctorFraudScore(@Param("doctorId") String doctorId, @Param("fraudScore") String fraudScore);
}