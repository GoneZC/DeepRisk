package com.demo.repository;

import org.springframework.stereotype.Repository;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.beans.factory.annotation.Autowired;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Repository
public class DataRepository {

    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    /**
     * 获取单个医生基本信息
     */
    public Map<String, Object> getDoctorBasicInfo(String doctorId) {
        String sql = "SELECT * FROM doctors WHERE id = ?";
        List<Map<String, Object>> results = jdbcTemplate.queryForList(sql, doctorId);
        return results.isEmpty() ? new HashMap<>() : results.get(0);
    }
    
    /**
     * 获取多个医生基本信息
     */
    public Map<String, Object> getDoctorsBasicInfo(List<String> doctorIds) {
        String placeholders = String.join(",", doctorIds.stream().map(id -> "?").collect(Collectors.toList()));
        String sql = "SELECT * FROM doctors WHERE id IN (" + placeholders + ")";
        
        List<Map<String, Object>> results = jdbcTemplate.queryForList(sql, doctorIds.toArray());
        
        Map<String, Object> doctorsMap = new HashMap<>();
        for (Map<String, Object> doctorInfo : results) {
            doctorsMap.put(doctorInfo.get("id").toString(), doctorInfo);
        }
        
        return doctorsMap;
    }
    
    /**
     * 获取单个医生的费用数据
     */
    public List<Map<String, Object>> getDoctorFees(String doctorId, LocalDate startDate, LocalDate endDate) {
        String sql = "SELECT * FROM doctor_fees WHERE doctor_id = ? AND service_date BETWEEN ? AND ? ORDER BY service_date DESC";
        return jdbcTemplate.queryForList(sql, doctorId, startDate, endDate);
    }
    
    /**
     * 获取多个医生的费用数据
     */
    public Map<String, List<Map<String, Object>>> getDoctorsFees(List<String> doctorIds, LocalDate startDate, LocalDate endDate) {
        String placeholders = String.join(",", doctorIds.stream().map(id -> "?").collect(Collectors.toList()));
        
        String sql = "SELECT * FROM doctor_fees WHERE doctor_id IN (" + placeholders + ") " +
                    "AND service_date BETWEEN ? AND ? ORDER BY doctor_id, service_date DESC";
        
        Object[] params = new Object[doctorIds.size() + 2];
        System.arraycopy(doctorIds.toArray(), 0, params, 0, doctorIds.size());
        params[doctorIds.size()] = startDate;
        params[doctorIds.size() + 1] = endDate;
        
        List<Map<String, Object>> results = jdbcTemplate.queryForList(sql, params);
        
        // 按医生ID分组
        Map<String, List<Map<String, Object>>> groupedFees = new HashMap<>();
        for (String doctorId : doctorIds) {
            groupedFees.put(doctorId, results.stream()
                .filter(fee -> doctorId.equals(fee.get("doctor_id").toString()))
                .collect(Collectors.toList()));
        }
        
        return groupedFees;
    }
    
    /**
     * 获取单个医生统计数据
     */
    public Map<String, Object> getDoctorStatistics(String doctorId, LocalDate startDate, LocalDate endDate) {
        Map<String, Object> statistics = new HashMap<>();
        
        // 计算总费用
        String totalFeeSql = "SELECT SUM(fee_amount) FROM doctor_fees WHERE doctor_id = ? AND service_date BETWEEN ? AND ?";
        Double totalFee = jdbcTemplate.queryForObject(totalFeeSql, Double.class, doctorId, startDate, endDate);
        statistics.put("totalFee", totalFee != null ? totalFee : 0);
        
        // 计算平均费用
        String avgFeeSql = "SELECT AVG(fee_amount) FROM doctor_fees WHERE doctor_id = ? AND service_date BETWEEN ? AND ?";
        Double avgFee = jdbcTemplate.queryForObject(avgFeeSql, Double.class, doctorId, startDate, endDate);
        statistics.put("averageFee", avgFee != null ? avgFee : 0);
        
        // 计算服务数量
        String countSql = "SELECT COUNT(*) FROM doctor_fees WHERE doctor_id = ? AND service_date BETWEEN ? AND ?";
        Integer serviceCount = jdbcTemplate.queryForObject(countSql, Integer.class, doctorId, startDate, endDate);
        statistics.put("serviceCount", serviceCount != null ? serviceCount : 0);
        
        // 其他统计...
        
        return statistics;
    }
    
    /**
     * 获取多个医生统计数据
     */
    public Map<String, Map<String, Object>> getDoctorsStatistics(List<String> doctorIds, LocalDate startDate, LocalDate endDate) {
        Map<String, Map<String, Object>> allStatistics = new HashMap<>();
        
        // 为简化实现，这里循环调用单个医生的统计方法
        // 实际生产环境中应考虑批量SQL查询提高效率
        for (String doctorId : doctorIds) {
            allStatistics.put(doctorId, getDoctorStatistics(doctorId, startDate, endDate));
        }
        
        return allStatistics;
    }
    
    /**
     * 获取医疗机构基本信息
     */
    public Map<String, Object> getProviderBasicInfo(String providerId) {
        String sql = "SELECT * FROM providers WHERE id = ?";
        List<Map<String, Object>> results = jdbcTemplate.queryForList(sql, providerId);
        return results.isEmpty() ? new HashMap<>() : results.get(0);
    }
    
    /**
     * 获取医疗机构的医生列表
     */
    public List<Map<String, Object>> getProviderDoctors(String providerId) {
        String sql = "SELECT * FROM doctors WHERE provider_id = ?";
        return jdbcTemplate.queryForList(sql, providerId);
    }
    
    /**
     * 获取医疗机构的费用数据
     */
    public List<Map<String, Object>> getProviderFees(String providerId, LocalDate startDate, LocalDate endDate) {
        String sql = "SELECT df.* FROM doctor_fees df " +
                    "JOIN doctors d ON df.doctor_id = d.id " +
                    "WHERE d.provider_id = ? AND df.service_date BETWEEN ? AND ? " +
                    "ORDER BY df.service_date DESC";
        return jdbcTemplate.queryForList(sql, providerId, startDate, endDate);
    }
    
    /**
     * 获取医疗机构统计数据
     */
    public Map<String, Object> getProviderStatistics(String providerId, LocalDate startDate, LocalDate endDate) {
        Map<String, Object> statistics = new HashMap<>();
        
        // 计算总费用
        String totalFeeSql = "SELECT SUM(df.fee_amount) FROM doctor_fees df " +
                           "JOIN doctors d ON df.doctor_id = d.id " +
                           "WHERE d.provider_id = ? AND df.service_date BETWEEN ? AND ?";
        Double totalFee = jdbcTemplate.queryForObject(totalFeeSql, Double.class, providerId, startDate, endDate);
        statistics.put("totalFee", totalFee != null ? totalFee : 0);
        
        // 医生数量
        String doctorCountSql = "SELECT COUNT(*) FROM doctors WHERE provider_id = ?";
        Integer doctorCount = jdbcTemplate.queryForObject(doctorCountSql, Integer.class, providerId);
        statistics.put("doctorCount", doctorCount != null ? doctorCount : 0);
        
        // 其他统计...
        
        return statistics;
    }
    
    /**
     * 获取费用数据
     */
    public List<Map<String, Object>> getFeeData(String doctorId, String providerId, LocalDate startDate, LocalDate endDate, int limit) {
        StringBuilder sqlBuilder = new StringBuilder();
        sqlBuilder.append("SELECT df.* FROM doctor_fees df ");
        
        if (providerId != null) {
            sqlBuilder.append("JOIN doctors d ON df.doctor_id = d.id ");
        }
        
        sqlBuilder.append("WHERE df.service_date BETWEEN ? AND ? ");
        
        if (doctorId != null) {
            sqlBuilder.append("AND df.doctor_id = ? ");
        }
        
        if (providerId != null) {
            sqlBuilder.append("AND d.provider_id = ? ");
        }
        
        sqlBuilder.append("ORDER BY df.service_date DESC LIMIT ?");
        
        String sql = sqlBuilder.toString();
        
        // 准备参数
        List<Object> params = new java.util.ArrayList<>();
        params.add(startDate);
        params.add(endDate);
        
        if (doctorId != null) {
            params.add(doctorId);
        }
        
        if (providerId != null) {
            params.add(providerId);
        }
        
        params.add(limit);
        
        return jdbcTemplate.queryForList(sql, params.toArray());
    }
} 