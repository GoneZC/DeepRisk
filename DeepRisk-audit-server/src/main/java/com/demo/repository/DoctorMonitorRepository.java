package com.demo.repository;

import com.demo.model.DoctorMonitorData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface DoctorMonitorRepository extends JpaRepository<DoctorMonitorData, String>, JpaSpecificationExecutor<DoctorMonitorData> {
    
    /**
     * 根据条件查询医生监控数据
     */
    @Query("SELECT d FROM DoctorMonitorData d WHERE " +
           "(:doctorId IS NULL OR d.doctorId LIKE %:doctorId%) AND " +
           "(:community IS NULL OR d.community LIKE %:community%) AND " +
           "(:hospitalCode IS NULL OR d.hospitalCode = :hospitalCode) AND " +
           "(:department IS NULL OR d.department LIKE %:department%) AND " +
           "(:startDate IS NULL OR d.prescriptionDate >= :startDate) AND " +
           "(:endDate IS NULL OR d.prescriptionDate <= :endDate)")
    List<DoctorMonitorData> findByDynamicConditions(
            @Param("doctorId") String doctorId,
            @Param("community") String community,
            @Param("hospitalCode") String hospitalCode,
            @Param("department") String department,
            @Param("startDate") LocalDate startDate,
            @Param("endDate") LocalDate endDate);
    
    /**
     * 计算符合条件的记录总数
     */
    @Query("SELECT COUNT(d) FROM DoctorMonitorData d WHERE " +
           "(:doctorId IS NULL OR d.doctorId LIKE %:doctorId%) AND " +
           "(:community IS NULL OR d.community LIKE %:community%) AND " +
           "(:hospitalCode IS NULL OR d.hospitalCode = :hospitalCode) AND " +
           "(:department IS NULL OR d.department LIKE %:department%) AND " +
           "(:startDate IS NULL OR d.prescriptionDate >= :startDate) AND " +
           "(:endDate IS NULL OR d.prescriptionDate <= :endDate)")
    long countByDynamicConditions(
            @Param("doctorId") String doctorId,
            @Param("community") String community,
            @Param("hospitalCode") String hospitalCode,
            @Param("department") String department,
            @Param("startDate") LocalDate startDate,
            @Param("endDate") LocalDate endDate);
}