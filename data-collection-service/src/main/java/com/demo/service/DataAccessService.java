package com.demo.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import com.demo.repository.DataRepository;
import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class DataAccessService {

    @Autowired
    private DataRepository dataRepository;
    
    /**
     * 获取单个医生的数据
     */
    @Cacheable(value = "doctorData", key = "#doctorId + #startDate + #endDate")
    public Map<String, Object> getDoctorData(String doctorId, LocalDate startDate, LocalDate endDate) {
        Map<String, Object> result = new HashMap<>();
        
        // 获取医生基本信息
        result.put("basicInfo", dataRepository.getDoctorBasicInfo(doctorId));
        
        // 获取医生费用数据
        result.put("fees", dataRepository.getDoctorFees(doctorId, startDate, endDate));
        
        // 获取医生统计信息
        result.put("statistics", dataRepository.getDoctorStatistics(doctorId, startDate, endDate));
        
        return result;
    }
    
    /**
     * 批量获取医生数据
     */
    public Map<String, Map<String, Object>> getDoctorsBatchData(List<String> doctorIds, LocalDate startDate, LocalDate endDate) {
        Map<String, Map<String, Object>> result = new HashMap<>();
        
        // 获取所有医生基本信息
        Map<String, Object> allDoctorsInfo = dataRepository.getDoctorsBasicInfo(doctorIds);
        
        // 获取所有医生费用数据
        Map<String, List<Map<String, Object>>> allDoctorsFees = dataRepository.getDoctorsFees(doctorIds, startDate, endDate);
        
        // 获取所有医生统计信息
        Map<String, Map<String, Object>> allDoctorsStatistics = dataRepository.getDoctorsStatistics(doctorIds, startDate, endDate);
        
        // 组装每个医生的完整数据
        for (String doctorId : doctorIds) {
            Map<String, Object> doctorData = new HashMap<>();
            doctorData.put("basicInfo", allDoctorsInfo.get(doctorId));
            doctorData.put("fees", allDoctorsFees.get(doctorId));
            doctorData.put("statistics", allDoctorsStatistics.get(doctorId));
            
            result.put(doctorId, doctorData);
        }
        
        return result;
    }
    
    /**
     * 获取医疗机构数据
     */
    @Cacheable(value = "providerData", key = "#providerId + #startDate + #endDate")
    public Map<String, Object> getProviderData(String providerId, LocalDate startDate, LocalDate endDate) {
        Map<String, Object> result = new HashMap<>();
        
        // 获取机构基本信息
        result.put("basicInfo", dataRepository.getProviderBasicInfo(providerId));
        
        // 获取机构医生列表
        result.put("doctors", dataRepository.getProviderDoctors(providerId));
        
        // 获取机构费用数据
        result.put("fees", dataRepository.getProviderFees(providerId, startDate, endDate));
        
        // 获取机构统计信息
        result.put("statistics", dataRepository.getProviderStatistics(providerId, startDate, endDate));
        
        return result;
    }
    
    /**
     * 获取费用数据
     */
    public List<Map<String, Object>> getFeeData(String doctorId, String providerId, LocalDate startDate, LocalDate endDate, int limit) {
        return dataRepository.getFeeData(doctorId, providerId, startDate, endDate, limit);
    }
    
    /**
     * 获取统计数据
     */
    @Cacheable(value = "statistics", key = "#entityType + #id + #startDate + #endDate")
    public Map<String, Object> getStatistics(String entityType, String id, LocalDate startDate, LocalDate endDate) {
        switch (entityType.toLowerCase()) {
            case "doctor":
                return dataRepository.getDoctorStatistics(id, startDate, endDate);
            case "provider":
                return dataRepository.getProviderStatistics(id, startDate, endDate);
            default:
                throw new IllegalArgumentException("不支持的实体类型: " + entityType);
        }
    }
} 