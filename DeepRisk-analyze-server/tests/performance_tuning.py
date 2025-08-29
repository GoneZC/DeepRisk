#!/usr/bin/env python3
"""
性能调优测试脚本
"""

import sys
import os
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 强制加载模型
from app.models.model_loader import load_models
load_models()

from app.models.fraud_detection import FraudDetectionCore

def test_batch_size_performance():
    """
    测试不同批处理大小的性能
    """
    print("创建欺诈检测核心实例...")
    fraud_detector = FraudDetectionCore()
    
    # 测试不同批处理大小
    batch_sizes = [1, 2, 4, 8, 16, 32, 64]
    
    print("\n测试不同批处理大小的性能:")
    print("=" * 80)
    print(f"{'批大小':<8} {'总时间(ms)':<12} {'平均时间(ms)':<15} {'吞吐量(req/s)':<15} {'加速比':<10}")
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
        
        # 测试批处理
        start_time = time.time()
        batch_results = fraud_detector.process_vectors_batch(test_vectors, doctor_ids)
        batch_time = (time.time() - start_time) * 1000  # 转换为毫秒
        avg_time = batch_time / batch_size
        throughput = 1000 / avg_time if avg_time > 0 else 0
        
        results.append({
            'batch_size': batch_size,
            'total_time': batch_time,
            'avg_time': avg_time,
            'throughput': throughput
        })
        
        # 计算相对于单样本的加速比
        if batch_size == 1:
            base_throughput = throughput
            speedup = 1.0
        else:
            speedup = throughput / base_throughput if base_throughput and base_throughput > 0 else 0
        
        print(f"{batch_size:<8} {batch_time:<12.2f} {avg_time:<15.4f} {throughput:<15.2f} {speedup:<10.2f}")
    
    print("=" * 80)
    
    # 分析结果
    best_result = max(results, key=lambda x: x['throughput'])
    print(f"\n最佳批处理大小: {best_result['batch_size']}")
    print(f"最大吞吐量: {best_result['throughput']:.2f} 请求/秒")
    print(f"相比单样本提升: {best_result['throughput'] / results[0]['throughput']:.2f}x")

def test_concurrent_performance():
    """
    测试并发性能
    """
    print("\n\n测试并发性能:")
    print("=" * 50)
    
    # 测试配置
    batch_size = 16
    concurrent_threads = [1, 2, 4, 8]
    
    print(f"基础批处理大小: {batch_size}")
    print(f"并发线程数测试: {concurrent_threads}")
    
    # 生成测试数据
    def generate_test_data(num_vectors):
        np.random.seed(42)
        test_vectors = []
        doctor_ids = []
        
        for i in range(num_vectors):
            vector = np.random.randn(35).astype(np.float32)
            test_vectors.append(vector)
            doctor_ids.append(f"doctor_{i}")
        return test_vectors, doctor_ids
    
    fraud_detector = FraudDetectionCore()
    
    for num_threads in concurrent_threads:
        print(f"\n测试 {num_threads} 个并发线程:")
        
        # 为每个线程生成测试数据
        test_data = []
        for i in range(num_threads):
            vectors, ids = generate_test_data(batch_size)
            test_data.append((vectors, ids))
        
        start_time = time.time()
        
        # 并发执行
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for vectors, ids in test_data:
                future = executor.submit(fraud_detector.process_vectors_batch, vectors, ids)
                futures.append(future)
            
            # 等待所有任务完成
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        total_requests = num_threads * batch_size
        throughput = total_requests / total_time
        
        print(f"  总处理请求数: {total_requests}")
        print(f"  总耗时: {total_time:.4f} 秒")
        print(f"  吞吐量: {throughput:.2f} 请求/秒")

def test_message_processing_latency():
    """
    测试消息处理延迟
    """
    print("\n\n测试消息处理延迟:")
    print("=" * 50)
    
    fraud_detector = FraudDetectionCore()
    
    # 生成单个测试向量
    np.random.seed(42)
    test_vector = np.random.randn(35).astype(np.float32)
    doctor_id = "doctor_test"
    
    # 多次测试取平均值
    num_tests = 100
    latencies = []
    
    for i in range(num_tests):
        start_time = time.time()
        result = fraud_detector.process_vector(test_vector, doctor_id)
        latency = (time.time() - start_time) * 1000  # 转换为毫秒
        latencies.append(latency)
    
    avg_latency = np.mean(latencies)
    min_latency = np.min(latencies)
    max_latency = np.max(latencies)
    p95_latency = np.percentile(latencies, 95)
    p99_latency = np.percentile(latencies, 99)
    
    print(f"测试次数: {num_tests}")
    print(f"平均延迟: {avg_latency:.2f} ms")
    print(f"最小延迟: {min_latency:.2f} ms")
    print(f"最大延迟: {max_latency:.2f} ms")
    print(f"95%延迟: {p95_latency:.2f} ms")
    print(f"99%延迟: {p99_latency:.2f} ms")
    
    # 计算理论TPS
    theoretical_tps = 1000 / avg_latency
    print(f"理论TPS: {theoretical_tps:.2f}")

if __name__ == "__main__":
    test_batch_size_performance()
    test_concurrent_performance()
    test_message_processing_latency()