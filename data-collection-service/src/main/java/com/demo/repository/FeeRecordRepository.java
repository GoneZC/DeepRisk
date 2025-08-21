package com.demo.repository;

import com.demo.entity.FeeRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface FeeRecordRepository extends JpaRepository<FeeRecord, Long> {
    
    @Query(value = "SELECT * FROM fee_list_d2409 LIMIT 1", nativeQuery = true)
    FeeRecord findRandomRecord();
    
    // 备用方法，返回所有记录
    @Query(value = "SELECT * FROM fee_list_d2409 LIMIT 10", nativeQuery = true)
    List<FeeRecord> findSampleRecords();
    
    // 通过ID查询一条记录
    @Query(value = "SELECT * FROM fee_list_d2409 WHERE id = ?1", nativeQuery = true)
    FeeRecord findRecordById(Long id);
} 