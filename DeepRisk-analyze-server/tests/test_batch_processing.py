#!/usr/bin/env python3
"""
测试批处理功能
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

def test_batch_processing():
    """
    测试批处理功能
    """
    print("创建欺诈检测核心实例...")
    fraud_detector = FraudDetectionCore()
    
    # 生成测试数据
    np.random.seed(42)
    batch_size = 8
    test_vectors = []
    doctor_ids = []
    
    for i in range(batch_size):
        vector = np.random.randn(35).astype(np.float32)
        test_vectors.append(vector)
        doctor_ids.append(f"doctor_{i}")
    
    print(f"生成了 {batch_size} 个测试向量")
    
    # 测试单个处理
    print("\n=== 单个处理测试 ===")
    start_time = time.time()
    single_results = []
    for i, vector in enumerate(test_vectors):
        result = fraud_detector.process_vector(vector, doctor_ids[i])
        single_results.append(result)
    single_time = time.time() - start_time
    print(f"单个处理时间: {single_time*1000:.2f} ms")
    print(f"平均每个向量处理时间: {single_time*1000/batch_size:.2f} ms")
    
    # 测试批处理
    print("\n=== 批处理测试 ===")
    start_time = time.time()
    batch_results = fraud_detector.process_vectors_batch(test_vectors, doctor_ids)
    batch_time = time.time() - start_time
    print(f"批处理时间: {batch_time*1000:.2f} ms")
    print(f"平均每个向量处理时间: {batch_time*1000/batch_size:.2f} ms")
    
    # 计算加速比
    speedup = single_time / batch_time if batch_time > 0 else 0
    print(f"批处理加速比: {speedup:.2f}x")
    
    # 验证结果一致性
    print("\n=== 结果验证 ===")
    consistent = True
    for i, (single_result, batch_result) in enumerate(zip(single_results, batch_results)):
        single_score = single_result.get('fraud_score', 0)
        batch_score = batch_result.get('fraud_score', 0)
        if abs(single_score - batch_score) > 0.01:  # 允许小的浮点数误差
            print(f"结果不一致: 向量{i}, 单处理={single_score}, 批处理={batch_score}")
            consistent = False
    
    if consistent:
        print("✓ 所有结果一致")
    else:
        print("✗ 结果不一致")
    
    # 显示示例结果
    print("\n=== 示例结果 ===")
    for i in range(min(3, len(batch_results))):
        result = batch_results[i]
        print(f"医生 {result.get('doctor_id')}: "
              f"欺诈得分={result.get('fraud_score'):.2f}, "
              f"风险等级={result.get('fraud_level')}")

if __name__ == "__main__":
    test_batch_processing()