#!/usr/bin/env python3
"""
批处理性能测试脚本
"""

import sys
import os
import time
import numpy as np
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 强制加载模型
from app.models.model_loader import load_models, get_encoder

def test_batch_performance():
    """
    测试批处理性能
    """
    print("加载模型...")
    load_models()
    
    # 获取编码器和标准化器
    encoder, scaler = get_encoder()
    if encoder is None or scaler is None:
        print("模型加载失败")
        return
    
    print("模型加载成功")
    
    # 生成测试数据
    np.random.seed(42)
    batch_sizes = [1, 2, 4, 8, 16, 32, 64]
    
    print("\n开始批处理性能测试...")
    print("=" * 80)
    print(f"{'批大小':<8} {'总时间(ms)':<12} {'平均时间(ms)':<15} {'单样本时间(ms)':<15} {'吞吐量(req/s)':<15} {'加速比':<10}")
    print("=" * 80)
    
    results = []
    base_throughput = None
    
    for batch_size in batch_sizes:
        # 生成批处理数据
        test_vectors = []
        for _ in range(batch_size):
            vector = np.random.randn(35).astype(np.float32)
            test_vectors.append(vector)
        
        test_vectors = np.array(test_vectors)
        
        # 多次运行取平均值
        num_runs = 5
        total_times = []
        
        for _ in range(num_runs):
            # 测量批处理时间
            start_time = time.time()
            
            # 标准化批处理数据
            scaled_vectors = scaler.transform(test_vectors)
            
            # 转换为PyTorch张量
            tensor_vectors = torch.FloatTensor(scaled_vectors)
            
            # 批处理推理
            with torch.no_grad():
                encoded_vectors = encoder(tensor_vectors)
            
            end_time = time.time()
            total_times.append((end_time - start_time) * 1000)  # 转换为毫秒
        
        # 计算平均时间
        avg_total_time = np.mean(total_times)
        avg_time_per_sample = avg_total_time / batch_size
        throughput = 1000 / avg_time_per_sample if avg_time_per_sample > 0 else 0
        
        results.append({
            'batch_size': batch_size,
            'total_time': avg_total_time,
            'avg_time': avg_time_per_sample,
            'throughput': throughput
        })
        
        # 计算相对于单样本的加速比
        if batch_size == 1:
            base_throughput = throughput
            speedup = 1.0
        else:
            speedup = throughput / base_throughput if base_throughput and base_throughput > 0 else 0
        
        print(f"{batch_size:<8} {avg_total_time:<12.2f} {avg_time_per_sample:<15.4f} {avg_time_per_sample:<15.4f} {throughput:<15.2f} {speedup:<10.2f}")
    
    print("=" * 80)
    
    # 分析结果
    print("\n性能分析:")
    best_result = max(results, key=lambda x: x['throughput'])
    print(f"1. 最佳批处理大小: {best_result['batch_size']}")
    print(f"2. 最大吞吐量: {best_result['throughput']:.2f} 请求/秒")
    print(f"3. 相比单样本提升: {best_result['throughput'] / results[0]['throughput']:.2f}x")
    
    # 批处理效率分析
    print("\n批处理效率分析:")
    for i, result in enumerate(results):
        efficiency = (result['batch_size'] * results[0]['avg_time']) / result['total_time'] if result['total_time'] > 0 else 0
        print(f"批大小 {result['batch_size']:2d}: 效率 {efficiency:.2f}x, 吞吐量 {result['throughput']:.2f} req/s")
    
    print("\n结论:")
    print("1. 批处理可以显著提高深度学习模型的推理效率")
    print("2. 随着批处理大小增加，吞吐量先增加后可能下降（受内存和计算资源限制）")
    print("3. 在实际应用中，应根据系统资源选择合适的批处理大小")

def test_concurrent_batch_processing():
    """
    测试并发批处理性能
    """
    print("\n\n开始并发批处理性能测试...")
    print("=" * 50)
    
    # 模拟并发处理多个小批次
    batch_size = 8
    num_concurrent_batches = 4
    
    # 生成测试数据
    np.random.seed(42)
    test_batches = []
    for i in range(num_concurrent_batches):
        batch = []
        for j in range(batch_size):
            vector = np.random.randn(35).astype(np.float32)
            batch.append(vector)
        test_batches.append(np.array(batch))
    
    print(f"测试配置: 批大小={batch_size}, 并发批数量={num_concurrent_batches}")
    
    # 加载模型
    load_models()
    encoder, scaler = get_encoder()
    
    if encoder is None or scaler is None:
        print("模型加载失败")
        return
    
    # 串行处理
    start_time = time.time()
    serial_results = []
    for batch in test_batches:
        scaled_vectors = scaler.transform(batch)
        tensor_vectors = torch.FloatTensor(scaled_vectors)
        with torch.no_grad():
            encoded_vectors = encoder(tensor_vectors)
        serial_results.append(encoded_vectors)
    serial_time = time.time() - start_time
    
    # 并行处理
    start_time = time.time()
    parallel_results = []
    
    def process_batch(batch):
        scaled_vectors = scaler.transform(batch)
        tensor_vectors = torch.FloatTensor(scaled_vectors)
        with torch.no_grad():
            encoded_vectors = encoder(tensor_vectors)
        return encoded_vectors
    
    with ThreadPoolExecutor(max_workers=num_concurrent_batches) as executor:
        futures = [executor.submit(process_batch, batch) for batch in test_batches]
        for future in as_completed(futures):
            result = future.result()
            parallel_results.append(result)
    
    parallel_time = time.time() - start_time
    
    print(f"串行处理时间: {serial_time*1000:.2f} ms")
    print(f"并行处理时间: {parallel_time*1000:.2f} ms")
    print(f"并行加速比: {serial_time/parallel_time:.2f}x")
    print(f"总处理样本数: {batch_size * num_concurrent_batches}")
    print(f"串行吞吐量: {batch_size * num_concurrent_batches / serial_time:.2f} req/s")
    print(f"并行吞吐量: {batch_size * num_concurrent_batches / parallel_time:.2f} req/s")

if __name__ == "__main__":
    test_batch_performance()
    test_concurrent_batch_processing()