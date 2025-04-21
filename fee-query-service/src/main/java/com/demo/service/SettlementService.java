package com.demo.service;

import org.springframework.aop.framework.AopContext;
import org.springframework.stereotype.Service;
import com.demo.repository.SettlementRepository;
import com.demo.model.Settlement;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.jpa.domain.Specification;
import jakarta.persistence.criteria.Predicate;
import java.util.ArrayList;
import java.util.List;
import org.springframework.util.StringUtils;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.CacheEvict;
import com.demo.model.UserInfo;
import com.demo.utils.UserContext;

@Service
public class SettlementService {  
    @Autowired
    private SettlementRepository settlementRepository;
    
    public SettlementService(SettlementRepository settlementRepo) {
        this.settlementRepository = settlementRepo;
    }

    public Page<Settlement> searchSettlements(String mdtrtId, String psnNo, 
                                             int page, int size, List<String> medTypes) {
        System.out.println("服务层接收参数: mdtrtId=" + mdtrtId + ", psnNo=" + psnNo + 
                           ", page=" + page + ", size=" + size + ", medTypes=" + medTypes);
        
        // 使用AopContext获取当前代理对象
        SettlementService proxy = (SettlementService) AopContext.currentProxy();
        
        // 通过代理调用缓存方法
        List<Settlement> pageContent = proxy.getPagedSettlementList(mdtrtId, psnNo, medTypes, page, size);
        long totalElements = proxy.getSettlementCount(mdtrtId, psnNo, medTypes);
        
        // 构建Page对象
        return new PageImpl<>(pageContent, PageRequest.of(page, size), totalElements);
    }

    // 获取结算数据
    @Cacheable(value = "settlementList", 
               key = "{#mdtrtId,#psnNo,#medTypes?.toString(),#page,#size,T(com.demo.utils.UserContext).getCurrentUser()?.getRole(),T(com.demo.utils.UserContext).getCurrentUser()?.getHospitalCode()}")
    public List<Settlement> getPagedSettlementList(String mdtrtId, String psnNo, 
                                                  List<String> medTypes, int page, int size) {
        System.out.println("从数据库获取第" + page + "页结算数据");
        Specification<Settlement> spec = createSpecification(mdtrtId, psnNo, medTypes);
        Page<Settlement> pageResult = settlementRepository.findAll(
            spec, PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "begndate")));
        return pageResult.getContent();
    }

    // 获取结算数据总数
    @Cacheable(value = "settlementCount", 
               key = "{#mdtrtId,#psnNo,#medTypes?.toString(),T(com.demo.utils.UserContext).getCurrentUser()?.getRole(),T(com.demo.utils.UserContext).getCurrentUser()?.getHospitalCode()}")
    public long getSettlementCount(String mdtrtId, String psnNo, List<String> medTypes) {
        System.out.println("从数据库获取结算数据总数");
        Specification<Settlement> spec = createSpecification(mdtrtId, psnNo, medTypes);
        return settlementRepository.count(spec);
    }

    // 清除所有相关缓存
    @CacheEvict(value = {"settlementList", "settlementCount"}, allEntries = true)
    public void clearAllPagesCache() {
        System.out.println("所有结算数据缓存已清除");
    }

    private Specification<Settlement> createSpecification(String mdtrtId, String psnNo, List<String> medTypes) {
        return (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            
            // 添加查询条件
            if (medTypes != null && !medTypes.isEmpty() && !medTypes.contains("")) {
                predicates.add(root.get("medType").in(medTypes));
            }
            if (StringUtils.hasText(mdtrtId)) {
                predicates.add(cb.equal(root.get("mdtrtId"), mdtrtId));
            }
            if (StringUtils.hasText(psnNo)) {
                predicates.add(cb.equal(root.get("psnNo"), psnNo));
            }
            
            // 根据用户角色添加数据权限过滤
            UserInfo userInfo = UserContext.getCurrentUser();
            if (userInfo != null) {
                // 如果不是医保局角色，只能查看自己医院的数据
                if (!"INSURANCE_BUREAU".equals(userInfo.getRole())) {
                    predicates.add(cb.equal(root.get("fixmedinsCode"), userInfo.getHospitalCode()));
                    System.out.println("添加医院限制: " + userInfo.getHospitalCode());
                } else {
                    System.out.println("医保局用户查询，无医院限制");
                }
            } else {
                System.out.println("警告: 无法获取用户信息，默认不显示任何数据");
                // 如果没有用户信息，返回空结果集
                predicates.add(cb.equal(cb.literal(1), 0));
            }
            
            return cb.and(predicates.toArray(new Predicate[0]));
        };
    }
} 