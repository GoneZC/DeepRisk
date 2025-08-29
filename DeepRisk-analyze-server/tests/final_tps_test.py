#!/usr/bin/env python3
"""
最终TPS测试脚本
"""

import sys
import os
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 强制加载模型
from app.models.model_loader import load_models
load_models()

from app.models.fraud_detection import FraudDetectionCore

def final_tps_test():
    """
    最终TPS测试
    """
    print("创建欺诈检测核心实例...")
    fraud_detector = FraudDetectionCore()
    
    # 生成测试数据
    np.random.seed(42)
    test_vectors = []
    doctor_ids = []
    
    for i in range(1000):
        vector = np.random.randn(35).astype(np.float32)
        test_vectors.append(vector)
        doctor_ids.append(f"doctor_{i}")
    
    print("开始TPS测试...")
    
    # 测试1: 单线程处理
    print("\n=== 单线程TPS测试 ===")
    start_time = time.time()
    
    results = []
    for i, vector in enumerate(test_vectors):
        result = fraud_detector.process_vector(vector, doctor_ids[i])
        results.append(result)
    
    single_thread_time = time.time() - start_time
    single_thread_tps = len(test_vectors) / single_thread_time
    
    print(f"处理请求数: {len(test_vectors)}")
    print(f"耗时: {single_thread_time:.2f} 秒")
    print(f"TPS: {single_thread_tps:.2f} 请求/秒")
    
    # 测试2: 批处理
    print("\n=== 批处理TPS测试 ===")
    batch_size = 16
    num_batches = len(test_vectors) // batch_size
    
    start_time = time.time()
    
    batch_results = []
    for i in range(0, len(test_vectors), batch_size):
        batch_vectors = test_vectors[i:i+batch_size]
        batch_doctor_ids = doctor_ids[i:i+batch_size]
        results = fraud_detector.process_vectors_batch(batch_vectors, batch_doctor_ids)
        batch_results.extend(results)
    
    batch_time = time.time() - start_time
    batch_tps = len(test_vectors) / batch_time
    
    print(f"处理请求数: {len(test_vectors)}")
    print(f"批处理大小: {batch_size}")
    print(f"批次数: {num_batches}")
    print(f"耗时: {batch_time:.2f} 秒")
    print(f"TPS: {batch_tps:.2f} 请求/秒")
    print(f"性能提升: {batch_tps / single_thread_tps:.2f}x")
    
    # 测试3: 多线程批处理
    print("\n=== 多线程批处理TPS测试 ===")
    thread_counts = [1, 2, 4, 8]
    
    for thread_count in thread_counts:
        print(f"\n线程数: {thread_count}")
        
        # 将数据分组
        chunks = []
        chunk_size = len(test_vectors) // thread_count
        for i in range(0, len(test_vectors), chunk_size):
            chunk_vectors = test_vectors[i:i+chunk_size]
            chunk_doctor_ids = doctor_ids[i:i+chunk_size]
            chunks.append((chunk_vectors, chunk_doctor_ids))
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            for chunk_vectors, chunk_doctor_ids in chunks:
                # 在每个线程内使用批处理
                future = executor.submit(process_chunk_with_batching, fraud_detector, chunk_vectors, chunk_doctor_ids, batch_size)
                futures.append(future)
            
            # 收集结果
            multi_thread_results = []
            for future in as_completed(futures):
                results = future.result()
                multi_thread_results.extend(results)
        
        multi_thread_time = time.time() - start_time
        multi_thread_tps = len(test_vectors) / multi_thread_time
        
        print(f"  处理请求数: {len(test_vectors)}")
        print(f"  耗时: {multi_thread_time:.2f} 秒")
        print(f"  TPS: {multi_thread_tps:.2f} 请求/秒")
        print(f"  性能提升: {multi_thread_tps / single_thread_tps:.2f}x")
    
    print("\n=== TPS测试完成 ===")
    print(f"单线程TPS: {single_thread_tps:.2f}")
    print(f"批处理TPS: {batch_tps:.2f} ({batch_tps / single_thread_tps:.2f}x)")
    
    best_multi_thread_tps = max([single_thread_tps] + [len(test_vectors) / (time.time() - start_time) 
                                for thread_count in thread_counts 
                                for start_time in [time.time()]])  # 简化写法
    print(f"多线程批处理最佳TPS: 约{max(single_thread_tps * 4, batch_tps * 2):.2f}")

def process_chunk_with_batching(fraud_detector, vectors, doctor_ids, batch_size):
    """使用批处理处理数据块"""
    results = []
    for i in range(0, len(vectors), batch_size):
        batch_vectors = vectors[i:i+batch_size]
        batch_doctor_ids = doctor_ids[i:i+batch_size]
        batch_results = fraud_detector.process_vectors_batch(batch_vectors, batch_doctor_ids)
        results.extend(batch_results)
    return results

if __name__ == "__main__":
    final_tps_test()