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

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
public class OutpatientMonitorService {

    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    @Autowired
    private DoctorCommunityRepository doctorCommunityRepository;
    
    /**
     * 查询门诊监管数据 - 修改缓存方式，避免缓存Page对象
     */
    public Page<OutpatientMonitorDTO> getOutpatientMonitorData(OutpatientQueryDTO queryDTO) {
        int page = queryDTO.getPage() != null ? queryDTO.getPage() : 0;
        int size = queryDTO.getSize() != null ? queryDTO.getSize() : 10;
        
        // 获取缓存数据
        List<OutpatientMonitorDTO> resultList = getOutpatientMonitorList(queryDTO);
        Integer totalCount = getOutpatientMonitorCount(queryDTO);
        
        // 重新构建Page对象
        return new PageImpl<>(resultList, PageRequest.of(page, size), totalCount != null ? totalCount : 0);
    }
    
    /**
     * 缓存查询结果列表
     */
    @Cacheable(value = "outpatientMonitorList", key = "#queryDTO.toString()")
    private List<OutpatientMonitorDTO> getOutpatientMonitorList(OutpatientQueryDTO queryDTO) {
        int page = queryDTO.getPage() != null ? queryDTO.getPage() : 0;
        int size = queryDTO.getSize() != null ? queryDTO.getSize() : 10;
        List<OutpatientMonitorDTO> resultList = new ArrayList<>();
        
        try {
            // 1. 先分页查询医生基本信息
            StringBuilder doctorSql = new StringBuilder();
            doctorSql.append("SELECT BILG_DR_CODE as doctorId, COM_NAME as community ");
            doctorSql.append("FROM doctor_community WHERE 1=1 ");
            
            List<Object> params = new ArrayList<>();
            
            // 添加条件 - 支持模糊查询
            if (queryDTO.getDoctorId() != null && !queryDTO.getDoctorId().isEmpty()) {
                doctorSql.append("AND BILG_DR_CODE LIKE ? ");
                params.add("%" + queryDTO.getDoctorId() + "%");
            }
            
            if (queryDTO.getCommunity() != null && !queryDTO.getCommunity().isEmpty()) {
                doctorSql.append("AND COM_NAME LIKE ? ");
                params.add("%" + queryDTO.getCommunity() + "%");
            }
            
            // 添加医院和科室查询
            if (queryDTO.getHospitalCode() != null && !queryDTO.getHospitalCode().isEmpty()) {
                doctorSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE FIXMEDINS_CODE = ? AND MED_TYPE = '14') ");
                params.add(queryDTO.getHospitalCode());
            }
            
            if (queryDTO.getDepartment() != null && !queryDTO.getDepartment().isEmpty()) {
                doctorSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE BILG_DEPT_NAME LIKE ? AND MED_TYPE = '14') ");
                params.add("%" + queryDTO.getDepartment() + "%");
            }
            
            // 日期范围查询
            if (queryDTO.getStartDate() != null) {
                doctorSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE DATE(FEE_OCUR_TIME) >= ? AND MED_TYPE = '14') ");
                params.add(queryDTO.getStartDate());
            }
            
            if (queryDTO.getEndDate() != null) {
                doctorSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE DATE(FEE_OCUR_TIME) <= ? AND MED_TYPE = '14') ");
                params.add(queryDTO.getEndDate());
            }
            
            // 添加分页
            doctorSql.append("LIMIT ? OFFSET ?");
            params.add(size);
            params.add(page * size);
            
            List<Map<String, Object>> doctors = jdbcTemplate.queryForList(
                doctorSql.toString(), params.toArray(new Object[0]));
            
            // 2. 批量查询处方信息
            for (Map<String, Object> doctor : doctors) {
                String doctorId = (String) doctor.get("doctorId");
                String community = (String) doctor.get("community");
                
                // 查询社区药品信息
                String comDrug = getCommunityDrugs(community);
                
                // 构建处方查询SQL
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
                    
                    OutpatientMonitorDTO dto = new OutpatientMonitorDTO(
                        doctorId,
                        (String) fee.get("hospitalCode"),
                        community,
                        (String) fee.get("department"),
                        ((Number) fee.get("prescriptionCount")).intValue(),
                        (BigDecimal) fee.get("totalCost"),
                        ((java.sql.Date) fee.get("prescriptionDate")).toLocalDate(),
                        comDrug
                    );
                    
                    resultList.add(dto);
                }
            }
            
            return resultList;
        } catch (Exception e) {
            System.err.println("查询出错: " + e.getMessage());
            return new ArrayList<>();
        }
    }
    
    /**
     * 缓存总记录数
     */
    @Cacheable(value = "outpatientMonitorCount", key = "#queryDTO.toString()")
    private Integer getOutpatientMonitorCount(OutpatientQueryDTO queryDTO) {
        try {
            StringBuilder countSql = new StringBuilder();
            countSql.append("SELECT COUNT(*) FROM doctor_community WHERE 1=1 ");
            
            List<Object> params = new ArrayList<>();
            
            // 添加条件 - 支持模糊查询
            if (queryDTO.getDoctorId() != null && !queryDTO.getDoctorId().isEmpty()) {
                countSql.append("AND BILG_DR_CODE LIKE ? ");
                params.add("%" + queryDTO.getDoctorId() + "%");
            }
            
            if (queryDTO.getCommunity() != null && !queryDTO.getCommunity().isEmpty()) {
                countSql.append("AND COM_NAME LIKE ? ");
                params.add("%" + queryDTO.getCommunity() + "%");
            }
            
            // 添加医院和科室查询
            if (queryDTO.getHospitalCode() != null && !queryDTO.getHospitalCode().isEmpty()) {
                countSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE FIXMEDINS_CODE = ? AND MED_TYPE = '14') ");
                params.add(queryDTO.getHospitalCode());
            }
            
            if (queryDTO.getDepartment() != null && !queryDTO.getDepartment().isEmpty()) {
                countSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE BILG_DEPT_NAME LIKE ? AND MED_TYPE = '14') ");
                params.add("%" + queryDTO.getDepartment() + "%");
            }
            
            // 日期范围查询
            if (queryDTO.getStartDate() != null) {
                countSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE DATE(FEE_OCUR_TIME) >= ? AND MED_TYPE = '14') ");
                params.add(queryDTO.getStartDate());
            }
            
            if (queryDTO.getEndDate() != null) {
                countSql.append("AND BILG_DR_CODE IN (SELECT DISTINCT BILG_DR_CODE FROM fee_list_d2409 WHERE DATE(FEE_OCUR_TIME) <= ? AND MED_TYPE = '14') ");
                params.add(queryDTO.getEndDate());
            }
            
            return jdbcTemplate.queryForObject(countSql.toString(), Integer.class, params.toArray(new Object[0]));
        } catch (Exception e) {
            System.err.println("查询总数出错: " + e.getMessage());
            return 0;
        }
    }
    
    /**
     * 更新医生风险评估结果
     */
    public OutpatientMonitorDTO updateDoctorRiskLevel(String doctorId, String riskLevel) {
        if (doctorId == null || riskLevel == null) {
            return null;
        }
        
        // 查询医生信息
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
        
        OutpatientMonitorDTO dto = new OutpatientMonitorDTO(
                doctorId, hospitalCode, community, department,
                prescriptionCount, totalCost, lastPrescriptionDate,
                getCommunityDrugs(community)
        );
        
        // 设置风险评估结果
        dto.setFraudRisk(riskLevel);
        
        return dto;
    }

    // 根据社区名称获取药品列表
    private String getCommunityDrugs(String community) {
        try {
            if (community == null || community.isEmpty()) {
                return "";
            }
            
            // 使用DISTINCT关键字获取唯一药品列表
            String sql = "SELECT DISTINCT COM_DRUG FROM doctor_community WHERE COM_NAME = ? LIMIT 1";
            
            String result = jdbcTemplate.queryForObject(sql, String.class, community);
            return result != null ? result : "";
        } catch (Exception e) {
            System.err.println("查询社区药品出错: " + e.getMessage());
            return "";
        }
    }
} 