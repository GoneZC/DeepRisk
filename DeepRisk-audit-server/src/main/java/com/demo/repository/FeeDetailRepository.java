package com.demo.repository;

import com.demo.model.FeeDetail;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface FeeDetailRepository extends JpaRepository<FeeDetail, String> {
    List<FeeDetail> findByMdtrtId(String mdtrtId);
    
    // 添加排序的查询方法
    List<FeeDetail> findByMdtrtIdOrderByFeeOcurTimeAsc(String mdtrtId);
    
    // 添加支持分页的方法
    Page<FeeDetail> findByMdtrtId(String mdtrtId, Pageable pageable);
    
    // 只需要定义这一个方法，使用fixmedinsCode作为实际字段
    List<FeeDetail> findByMdtrtIdAndFixmedinsCode(String mdtrtId, String fixmedinsCode);
} 