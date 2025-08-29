package com.demo.service;

import com.demo.dto.OutpatientMonitorDTO;
import com.demo.dto.OutpatientQueryDTO;
import com.demo.model.DoctorCommunity;
import com.demo.repository.DoctorCommunityRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.context.annotation.Lazy;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * 门诊监管服务
 */
@Service
public class OutpatientMonitorService {

    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    @Autowired
    private DoctorCommunityRepository doctorCommunityRepository;
    
    // 注入自身代理，解决AOP缓存问题
    @Autowired
    @Lazy
    private OutpatientMonitorService self;
    
    /**
     * 查询门诊监管数据 - 修改缓存方式，避免缓存Page对象
     */
    @Transactional(readOnly = true)
    public Page<OutpatientMonitorDTO> getOutpatientMonitorData(OutpatientQueryDTO queryDTO) {
        int page = queryDTO.getPage() != null ? queryDTO.getPage() : 0;
        int size = queryDTO.getSize() != null ? queryDTO.getSize() : 10;
        
        // 修改为使用代理对象调用，确保AOP缓存生效
        List<OutpatientMonitorDTO> resultList = self.getOutpatientMonitorList(queryDTO);
        Integer totalCount = self.getOutpatientMonitorCount(queryDTO);
        
        // 重新构建Page对象
        return new PageImpl<>(resultList, PageRequest.of(page, size), totalCount != null ? totalCount : 0);
    }
    
    /**
     * 缓存查询结果列表
     */
    @Cacheable(value = "outpatientMonitorList", key = "#queryDTO.toString()")
    @Transactional(readOnly = true)
    public List<OutpatientMonitorDTO> getOutpatientMonitorList(OutpatientQueryDTO queryDTO) {
        System.out.println("执行数据库查询方法(缓存未命中)");
        
        try {
            return findDoctorsWithPrescriptionInfo(queryDTO);
        } catch (Exception e) {
            System.err.println("查询出错: " + e.getMessage());
            return new ArrayList<>();
        }
    }
    
    /**
     * 缓存总记录数
     */
    @Cacheable(value = "outpatientMonitorCount", key = "#queryDTO.toString()")
    @Transactional(readOnly = true)
    public Integer getOutpatientMonitorCount(OutpatientQueryDTO queryDTO) {
        System.out.println("执行数据库总数查询(缓存未命中)");
        
        try {
            return countDoctorsByConditions(queryDTO);
        } catch (Exception e) {
            System.err.println("查询总数出错: " + e.getMessage());
            return 0;
        }
    }
    
    /**
     * 更新医生风险评估结果
     */
    @Transactional
    public OutpatientMonitorDTO updateDoctorRiskLevel(String doctorId, String riskLevel) {
        if (doctorId == null || riskLevel == null) {
            return null;
        }
        
        try {
            // 查询医生信息
            OutpatientMonitorDTO doctorInfo = findDoctorById(doctorId);
            if (doctorInfo != null) {
                doctorInfo.setFraudRisk(riskLevel);
            }
            return doctorInfo;
        } catch (Exception e) {
            System.err.println("更新风险等级失败: " + e.getMessage());
            return null;
        }
    }

    /**
     * 查询符合条件的医生及其处方信息
     */
    private List<OutpatientMonitorDTO> findDoctorsWithPrescriptionInfo(OutpatientQueryDTO queryDTO) {
        int page = queryDTO.getPage() != null ? queryDTO.getPage() : 0;
        int size = queryDTO.getSize() != null ? queryDTO.getSize() : 10;
        List<OutpatientMonitorDTO> resultList = new ArrayList<>();
        
        // 1. 构建查询医生基本信息的SQL
        String doctorSql = buildDoctorQuery(queryDTO);
        List<Object> params = buildDoctorQueryParams(queryDTO);
        
        // 添加分页
        params.add(size);
        params.add(page * size);
        
        // 2. 查询医生基本信息
        List<Map<String, Object>> doctors = jdbcTemplate.queryForList(
            doctorSql, params.toArray(new Object[0]));
        
        // 3. 批量查询处方信息
        for (Map<String, Object> doctor : doctors) {
            String doctorId = (String) doctor.get("doctorId");
            String community = (String) doctor.get("community");
            
            // 查询社区药品信息
            String comDrug = getCommunityDrugs(community);
            
            // 查询处方信息
            OutpatientMonitorDTO prescriptionInfo = findPrescriptionInfo(doctorId, community, comDrug, queryDTO);
            if (prescriptionInfo != null) {
                resultList.add(prescriptionInfo);
            }
        }
        
        return resultList;
    }
    
    /**
     * 构建医生查询SQL
     */
    private String buildDoctorQuery(OutpatientQueryDTO queryDTO) {
        StringBuilder doctorSql = new StringBuilder();
        doctorSql.append("SELECT BILG_DR_CODE as doctorId, COM_NAME as community ");
        doctorSql.append("FROM doctor_community WHERE 1=1 ");
        
        if (queryDTO.getDoctorId() != null && !queryDTO.getDoctorId().isEmpty()) {
            doctorSql.append("AND BILG_DR_CODE LIKE ? ");
        }
        
        if (queryDTO.getCommunity() != null && !queryDTO.getCommunity().isEmpty()) {
            doctorSql.append("AND COM_NAME LIKE ? ");
        }
        
        if (queryDTO.getHospitalCode() != null && !queryDTO.getHospitalCode().isEmpty()) {
            doctorSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE FIXMEDINS_CODE = ? AND MED_TYPE = '14') ");
        }
        
        if (queryDTO.getDepartment() != null && !queryDTO.getDepartment().isEmpty()) {
            doctorSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE BILG_DEPT_NAME LIKE ? AND MED_TYPE = '14') ");
        }
        
        if (queryDTO.getStartDate() != null) {
            doctorSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE DATE(FEE_OCUR_TIME) >= ? AND MED_TYPE = '14') ");
        }
        
        if (queryDTO.getEndDate() != null) {
            doctorSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE DATE(FEE_OCUR_TIME) <= ? AND MED_TYPE = '14') ");
        }
        
        doctorSql.append("LIMIT ? OFFSET ?");
        return doctorSql.toString();
    }
    
    /**
     * 构建医生查询参数
     */
    private List<Object> buildDoctorQueryParams(OutpatientQueryDTO queryDTO) {
        List<Object> params = new ArrayList<>();
        
        if (queryDTO.getDoctorId() != null && !queryDTO.getDoctorId().isEmpty()) {
            params.add("%" + queryDTO.getDoctorId() + "%");
        }
        
        if (queryDTO.getCommunity() != null && !queryDTO.getCommunity().isEmpty()) {
            params.add("%" + queryDTO.getCommunity() + "%");
        }
        
        if (queryDTO.getHospitalCode() != null && !queryDTO.getHospitalCode().isEmpty()) {
            params.add(queryDTO.getHospitalCode());
        }
        
        if (queryDTO.getDepartment() != null && !queryDTO.getDepartment().isEmpty()) {
            params.add("%" + queryDTO.getDepartment() + "%");
        }
        
        if (queryDTO.getStartDate() != null) {
            params.add(queryDTO.getStartDate());
        }
        
        if (queryDTO.getEndDate() != null) {
            params.add(queryDTO.getEndDate());
        }
        
        return params;
    }
    
    /**
     * 查询处方信息
     */
    private OutpatientMonitorDTO findPrescriptionInfo(String doctorId, String community, String comDrug, OutpatientQueryDTO queryDTO) {
        StringBuilder feeSql = new StringBuilder();
        feeSql.append("SELECT FIXMEDINS_CODE as hospitalCode, BILG_DEPT_NAME as department, ");
        feeSql.append("COUNT(DISTINCT MDTRT_ID) as prescriptionCount, ");
        feeSql.append("SUM(DET_ITEM_FEE_SUMAMT) as totalCost, DATE(FEE_OCUR_TIME) as prescriptionDate ");
        feeSql.append("FROM fee_list_d2409 WHERE BILG_DR_CODE = ? AND MED_TYPE = '14' ");
        
        List<Object> feeParams = new ArrayList<>();
        feeParams.add(doctorId);
        
        // 添加日期条件
        if (queryDTO.getStartDate() != null) {
            feeSql.append("AND DATE(FEE_OCUR_TIME) >= ? ");
            feeParams.add(queryDTO.getStartDate());
        }
        
        if (queryDTO.getEndDate() != null) {
            feeSql.append("AND DATE(FEE_OCUR_TIME) <= ? ");
            feeParams.add(queryDTO.getEndDate());
        }
        
        // 添加医院和科室过滤
        if (queryDTO.getHospitalCode() != null && !queryDTO.getHospitalCode().isEmpty()) {
            feeSql.append("AND FIXMEDINS_CODE = ? ");
            feeParams.add(queryDTO.getHospitalCode());
        }
        
        if (queryDTO.getDepartment() != null && !queryDTO.getDepartment().isEmpty()) {
            feeSql.append("AND BILG_DEPT_NAME LIKE ? ");
            feeParams.add("%" + queryDTO.getDepartment() + "%");
        }
        
        feeSql.append("GROUP BY DATE(FEE_OCUR_TIME), FIXMEDINS_CODE, BILG_DEPT_NAME ");
        feeSql.append("ORDER BY prescriptionDate DESC LIMIT 1");
        
        List<Map<String, Object>> feeInfo = jdbcTemplate.queryForList(
            feeSql.toString(), feeParams.toArray(new Object[0]));
        
        if (!feeInfo.isEmpty()) {
            Map<String, Object> fee = feeInfo.get(0);
            
            return new OutpatientMonitorDTO(
                doctorId,
                (String) fee.get("hospitalCode"),
                community,
                (String) fee.get("department"),
                ((Number) fee.get("prescriptionCount")).intValue(),
                (BigDecimal) fee.get("totalCost"),
                ((java.sql.Date) fee.get("prescriptionDate")).toLocalDate(),
                comDrug
            );
        }
        
        return null;
    }
    
    /**
     * 查询符合条件的记录总数
     */
    private Integer countDoctorsByConditions(OutpatientQueryDTO queryDTO) {
        StringBuilder countSql = new StringBuilder();
        countSql.append("SELECT COUNT(*) FROM doctor_community WHERE 1=1 ");
        
        List<Object> params = new ArrayList<>();
        
        if (queryDTO.getDoctorId() != null && !queryDTO.getDoctorId().isEmpty()) {
            countSql.append("AND BILG_DR_CODE LIKE ? ");
            params.add("%" + queryDTO.getDoctorId() + "%");
        }
        
        if (queryDTO.getCommunity() != null && !queryDTO.getCommunity().isEmpty()) {
            countSql.append("AND COM_NAME LIKE ? ");
            params.add("%" + queryDTO.getCommunity() + "%");
        }
        
        if (queryDTO.getHospitalCode() != null && !queryDTO.getHospitalCode().isEmpty()) {
            countSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE FIXMEDINS_CODE = ? AND MED_TYPE = '14') ");
            params.add(queryDTO.getHospitalCode());
        }
        
        if (queryDTO.getDepartment() != null && !queryDTO.getDepartment().isEmpty()) {
            countSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE BILG_DEPT_NAME LIKE ? AND MED_TYPE = '14') ");
            params.add("%" + queryDTO.getDepartment() + "%");
        }
        
        if (queryDTO.getStartDate() != null) {
            countSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE DATE(FEE_OCUR_TIME) >= ? AND MED_TYPE = '14') ");
            params.add(queryDTO.getStartDate());
        }
        
        if (queryDTO.getEndDate() != null) {
            countSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE DATE(FEE_OCUR_TIME) <= ? AND MED_TYPE = '14') ");
            params.add(queryDTO.getEndDate());
        }
        
        return jdbcTemplate.queryForObject(countSql.toString(), Integer.class, params.toArray(new Object[0]));
    }
    
    /**
     * 根据ID查询医生信息
     */
    private OutpatientMonitorDTO findDoctorById(String doctorId) {
        String sql = "SELECT fl.BILG_DR_CODE as doctorId, fl.FIXMEDINS_CODE as hospitalCode, " +
                "fl.BILG_DEPT_NAME as department, COUNT(DISTINCT fl.MDTRT_ID) as prescriptionCount, " +
                "SUM(fl.DET_ITEM_FEE_SUMAMT) as totalCost, DATE(MAX(fl.FEE_OCUR_TIME)) as lastPrescriptionDate " +
                "FROM fee_list_d2409 fl " +
                "WHERE fl.BILG_DR_CODE = ? AND fl.MED_TYPE = '14' " +
                "GROUP BY fl.BILG_DR_CODE, fl.FIXMEDINS_CODE, fl.BILG_DEPT_NAME";

        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql, doctorId);
        
        if (rows.isEmpty()) {
            return null;
        }
        
        Map<String, Object> row = rows.get(0);
        String hospitalCode = (String) row.get("hospitalCode");
        String department = (String) row.get("department");
        Integer prescriptionCount = ((Number) row.get("prescriptionCount")).intValue();
        BigDecimal totalCost = (BigDecimal) row.get("totalCost");
        
        // 日期转换
        java.sql.Date sqlDate = (java.sql.Date) row.get("lastPrescriptionDate");
        LocalDate lastPrescriptionDate = sqlDate != null ? sqlDate.toLocalDate() : null;
        
        // 获取医生所属社区
        DoctorCommunity doctorCommunity = doctorCommunityRepository.findByBilgDrCode(doctorId);
        String community = doctorCommunity != null ? doctorCommunity.getComName() : null;
        
        return new OutpatientMonitorDTO(
                doctorId, hospitalCode, community, department,
                prescriptionCount, totalCost, lastPrescriptionDate,
                getCommunityDrugs(community)
        );
    }

    /**
     * 根据社区名称获取药品列表
     */
    private String getCommunityDrugs(String community) {
        try {
            if (community == null || community.isEmpty()) {
                return "";
            }
            
            String sql = "SELECT DISTINCT COM_DRUG FROM doctor_community WHERE COM_NAME = ? LIMIT 1";
            
            String result = jdbcTemplate.queryForObject(sql, String.class, community);
            return result != null ? result : "";
        } catch (Exception e) {
            System.err.println("查询社区药品出错: " + e.getMessage());
            return "";
        }
    }
}