package com.demo.controller;

import com.demo.dto.SearchRequest;
import com.demo.model.Settlement;
import com.demo.service.SettlementService;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.Collections;

@RestController
@RequestMapping("/api")
public class SettlementController {
    
    @Autowired
    private SettlementService settlementService;
    
    @PostMapping("/settlements/search")
    public Map<String, Object> searchSettlements(
        @RequestBody SearchRequest request) {
        
        System.out.println("接收参数:");
        System.out.println("mdtrtId: " + request.getMdtrtId());
        System.out.println("psnNo: " + request.getPsnNo());
        System.out.println("medTypes: " + request.getMedTypes());
        
        List<String> medTypeList = request.getMedTypes() != null ? 
            request.getMedTypes() // 直接使用前端传递的List
            : Collections.emptyList();
        System.out.println("medTypeList: " + medTypeList);
        Page<Settlement> pageResult = settlementService.searchSettlements(request.getMdtrtId(), request.getPsnNo(), request.getPage(), request.getSize(), medTypeList);
        Map<String, Object> response = new HashMap<>();
        response.put("data", pageResult.getContent());
        response.put("totalElements", pageResult.getTotalElements());
        
        return response;
    }
    
} 