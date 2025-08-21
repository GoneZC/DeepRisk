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
import com.demo.model.UserInfo;
import com.demo.utils.UserContext;


@RestController
@RequestMapping("/api")
public class SettlementController {
    
    @Autowired
    private SettlementService settlementService;
    
    @PostMapping("/settlements/search")
    public Map<String, Object> searchSettlements(
        @RequestBody SearchRequest request) {

        // 获取当前用户信息
        UserInfo currentUser = UserContext.getCurrentUser();
        System.out.println("当前用户信息：" + currentUser);
        
        List<String> medTypeList = request.getMedTypes() != null ? 
            request.getMedTypes() 
            : Collections.emptyList();
        Page<Settlement> pageResult = settlementService.searchSettlements(request.getMdtrtId(), request.getPsnNo(), request.getPage(), request.getSize(), medTypeList);
        Map<String, Object> response = new HashMap<>();
        response.put("data", pageResult.getContent());
        response.put("totalElements", pageResult.getTotalElements());

        return response;
    }
    
} 