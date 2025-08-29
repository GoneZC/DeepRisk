#!/usr/bin/env python3
"""
性能分析脚本 - 测量各阶段时间消耗
"""

import sys
import os
import time
import numpy as np

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 强制加载模型
from app.models.model_loader import load_models
load_models()

from app.models.fraud_detection import FraudDetectionCore

def performance_analysis():
    """
    性能分析
    """
    print("创建欺诈检测核心实例...")
    fraud_detector = FraudDetectionCore()
    
    # 生成测试向量
    np.random.seed(42)
    test_vector = np.random.randn(35).astype(np.float32)
    
    print("\n开始性能分析...")
    
    # 多次运行以获得平均时间
    num_runs = 10
    times = {
        'encode_vector': [],
        'find_similar': [],
        'calculate_score': [],
        'total_process': []
    }
    
    for i in range(num_runs):
        print(f"\n第 {i+1} 次运行:")
        
        # 测量总处理时间
        start_total = time.time()
        
        # 测量向量编码时间
        start_encode = time.time()
        vector_128d = fraud_detector._encode_vector(test_vector)
        end_encode = time.time()
        encode_time = (end_encode - start_encode) * 1000  # 转换为毫秒
        times['encode_vector'].append(encode_time)
        print(f"  向量编码时间: {encode_time:.2f} ms")
        
        if vector_128d is not None:
            # 测量相似医生查找时间
            start_find = time.time()
            similar_doctors = fraud_detector._find_similar_doctors(vector_128d, k=10)
            end_find = time.time()
            find_time = (end_find - start_find) * 1000  # 转换为毫秒
            times['find_similar'].append(find_time)
            print(f"  相似医生查找时间: {find_time:.2f} ms")
            print(f"  找到相似医生数量: {len(similar_doctors)}")
            
            # 测量评分计算时间
            start_score = time.time()
            fraud_score = fraud_detector._calculate_fraud_score(similar_doctors)
            end_score = time.time()
            score_time = (end_score - start_score) * 1000  # 转换为毫秒
            times['calculate_score'].append(score_time)
            print(f"  评分计算时间: {score_time:.4f} ms")
            print(f"  欺诈得分: {fraud_score:.2f}")
        else:
            print("  向量编码失败")
            # 添加默认值以保持数组长度一致
            times['find_similar'].append(0)
            times['calculate_score'].append(0)
        
        end_total = time.time()
        total_time = (end_total - start_total) * 1000  # 转换为毫秒
        times['total_process'].append(total_time)
        print(f"  总处理时间: {total_time:.2f} ms")
    
    # 计算平均时间
    print("\n=== 性能分析结果 (平均时间) ===")
    for key, value in times.items():
        if value:
            avg_time = np.mean(value)
            print(f"{key}: {avg_time:.2f} ms")
    
    # 计算TPS
    avg_total_time = np.mean(times['total_process'])
    tps = 1000 / avg_total_time if avg_total_time > 0 else 0
    print(f"\n估算TPS: {tps:.2f} 请求/秒")
    
    print("\n=== 性能分析完成 ===")

if __name__ == "__main__":
    performance_analysis()