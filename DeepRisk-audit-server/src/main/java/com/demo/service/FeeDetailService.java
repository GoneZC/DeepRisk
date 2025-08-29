package com.demo.service;

import com.demo.model.FeeDetail;
import com.demo.repository.FeeDetailRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import javax.servlet.http.HttpServletRequest;

@Service
public class FeeDetailService {
    private static final Logger logger = LoggerFactory.getLogger(FeeDetailService.class);

    @Autowired
    private FeeDetailRepository feeDetailRepo;

    @Transactional(readOnly = true)
    public List<FeeDetail> getFeeDetails(String mdtrtId) {
        logger.debug("查询所有费用记录, 就诊ID: {}", mdtrtId);
        return feeDetailRepo.findByMdtrtIdOrderByFeeOcurTimeAsc(mdtrtId);
    }
    
    @Transactional(readOnly = true)
    public Page<FeeDetail> getFeeDetailsPaged(String mdtrtId, int page, int size) {
        logger.debug("分页查询费用记录, 就诊ID: {}, 页码: {}, 每页条数: {}", mdtrtId, page, size);
        Pageable pageable = PageRequest.of(page, size, Sort.by("feeOcurTime").ascending());
        return feeDetailRepo.findByMdtrtId(mdtrtId, pageable);
    }

    @Transactional(readOnly = true)
    public List<FeeDetail> getHospitalFeeDetails(String mdtrtId, HttpServletRequest request) {
        // 从请求头获取医院ID和用户角色
        String hospitalId = request.getHeader("X-Hospital-Id");
        String userRole = request.getHeader("X-User-Role");
        if ("MEDICAL_INSURANCE_BUREAU".equals(userRole)) {
            return feeDetailRepo.findByMdtrtIdOrderByFeeOcurTimeAsc(mdtrtId);
        }
        return feeDetailRepo.findByMdtrtIdAndFixmedinsCode(mdtrtId, hospitalId);
    }
}