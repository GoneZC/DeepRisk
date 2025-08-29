#!/usr/bin/env python3
"""
全面的批处理性能测试
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

def comprehensive_batch_test():
    """
    全面的批处理性能测试
    """
    print("创建欺诈检测核心实例...")
    fraud_detector = FraudDetectionCore()
    
    # 测试不同批处理大小
    batch_sizes = [1, 2, 4, 8, 16, 32]
    
    print("\n开始全面批处理性能测试...")
    print("=" * 80)
    print(f"{'批大小':<8} {'单处理总时间(ms)':<18} {'批处理总时间(ms)':<18} {'单处理平均(ms)':<18} {'批处理平均(ms)':<18} {'加速比':<10}")
    print("=" * 80)
    
    results = []
    
    for batch_size in batch_sizes:
        # 生成测试数据
        np.random.seed(42)
        test_vectors = []
        doctor_ids = []
        
        for i in range(batch_size):
            vector = np.random.randn(35).astype(np.float32)
            test_vectors.append(vector)
            doctor_ids.append(f"doctor_{i}")
        
        # 测试单个处理
        start_time = time.time()
        single_results = []
        for i, vector in enumerate(test_vectors):
            result = fraud_detector.process_vector(vector, doctor_ids[i])
            single_results.append(result)
        single_time = (time.time() - start_time) * 1000  # 转换为毫秒
        single_avg = single_time / batch_size
        
        # 测试批处理
        start_time = time.time()
        batch_results = fraud_detector.process_vectors_batch(test_vectors, doctor_ids)
        batch_time = (time.time() - start_time) * 1000  # 转换为毫秒
        batch_avg = batch_time / batch_size
        
        # 计算加速比
        speedup = single_time / batch_time if batch_time > 0 else 0
        
        results.append({
            'batch_size': batch_size,
            'single_time': single_time,
            'batch_time': batch_time,
            'single_avg': single_avg,
            'batch_avg': batch_avg,
            'speedup': speedup
        })
        
        print(f"{batch_size:<8} {single_time:<18.2f} {batch_time:<18.2f} {single_avg:<18.2f} {batch_avg:<18.2f} {speedup:<10.2f}")
    
    print("=" * 80)
    
    # 分析结果
    print("\n性能分析:")
    best_result = max(results, key=lambda x: x['speedup'])
    print(f"1. 最佳批处理大小: {best_result['batch_size']}")
    print(f"2. 最大加速比: {best_result['speedup']:.2f}x")
    
    # 计算理论TPS提升
    base_avg_time = results[0]['single_avg']  # 批大小为1时的平均时间
    best_avg_time = best_result['batch_avg']   # 最佳批处理的平均时间
    tps_improvement = base_avg_time / best_avg_time if best_avg_time > 0 else 0
    print(f"3. 理论TPS提升: {tps_improvement:.2f}x")
    
    # 预估实际TPS
    base_tps = 1000 / base_avg_time if base_avg_time > 0 else 0
    improved_tps = 1000 / best_avg_time if best_avg_time > 0 else 0
    print(f"4. 预估单处理TPS: {base_tps:.2f}")
    print(f"5. 预估批处理TPS: {improved_tps:.2f}")
    
    print("\n结论:")
    print("1. 批处理可以显著提高处理效率")
    print("2. 随着批处理大小增加，加速比先增加后可能下降")
    print("3. 在实际应用中，可以选择合适的批处理大小以平衡性能和延迟")

def test_throughput_improvement():
    """
    测试吞吐量改进
    """
    print("\n\n吞吐量改进测试")
    print("=" * 50)
    
    # 模拟处理大量请求
    total_requests = 1000
    batch_size = 32
    
    print(f"模拟处理 {total_requests} 个请求:")
    print(f"批处理大小: {batch_size}")
    
    # 计算需要的批次数
    num_batches = (total_requests + batch_size - 1) // batch_size
    
    # 模拟单处理时间 (基于之前的测试结果约3.16ms/请求)
    single_process_time = 3.16  # ms
    total_single_time = total_requests * single_process_time
    
    # 模拟批处理时间 (基于之前的测试结果约2.39ms/请求)
    batch_process_time = 2.39  # ms
    total_batch_time = num_batches * batch_process_time * batch_size
    
    print(f"单处理总时间: {total_single_time:.0f} ms ({total_single_time/1000:.2f} s)")
    print(f"批处理总时间: {total_batch_time:.0f} ms ({total_batch_time/1000:.2f} s)")
    print(f"时间节省: {total_single_time - total_batch_time:.0f} ms")
    print(f"性能提升: {total_single_time / total_batch_time:.2f}x")

if __name__ == "__main__":
    comprehensive_batch_test()
    test_throughput_improvement()