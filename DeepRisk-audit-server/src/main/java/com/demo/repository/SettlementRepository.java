package com.demo.repository;

import com.demo.model.Settlement;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.time.LocalDateTime;
import java.util.List;
import org.springframework.data.domain.Page;

public interface SettlementRepository extends JpaRepository<Settlement, String>, JpaSpecificationExecutor<Settlement> {
    // 按就诊ID查询结算记录列表
    List<Settlement> findByMdtrtId(String mdtrtId);
    
    // 按就诊ID统计记录数 
    int countByMdtrtId(String mdtrtId);
    
    // 根据患者编号查询
    List<Settlement> findByPsnNo(String psnNo);
    
    // 根据患者编号和就诊日期范围查询
    List<Settlement> findByPsnNoAndBegndateGreaterThanEqualAndBegndateLessThanEqual(
            String psnNo, 
            java.time.LocalDateTime startDate, 
            java.time.LocalDateTime endDate);
    
    // 按就诊日期排序查询最近的记录
    List<Settlement> findTop10ByOrderByBegndateDesc();

    @Query(value = "SELECT s FROM Settlement s WHERE s.begndate < :lastDate OR (s.begndate = :lastDate AND s.setlId < :lastId) ORDER BY s.begndate DESC, s.setlId DESC")
    List<Settlement> findNextPage(@Param("lastDate") LocalDateTime lastDate, 
                                 @Param("lastId") String lastId,
                                 Pageable pageable);

    // 添加医疗类别查询方法
    Page<Settlement> findByMedType(String medType, Pageable pageable);
} 