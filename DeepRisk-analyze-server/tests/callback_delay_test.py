#!/usr/bin/env python3
"""
测试回调延迟对系统性能的影响
"""

import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np

def simulate_callback_with_delay(delay_ms):
    """
    模拟带有延迟的回调
    """
    time.sleep(delay_ms / 1000.0)  # 模拟网络延迟
    return True

def test_synchronous_processing(num_requests, processing_time_ms, callback_delay_ms):
    """
    测试同步处理方式的性能
    """
    print(f"测试同步处理: {num_requests}个请求, 处理时间{processing_time_ms}ms, 回调延迟{callback_delay_ms}ms")
    
    start_time = time.time()
    
    for i in range(num_requests):
        # 模拟消息处理
        time.sleep(processing_time_ms / 1000.0)
        
        # 同步发送回调（阻塞）
        simulate_callback_with_delay(callback_delay_ms)
        
        # 模拟消息确认
        pass
    
    total_time = time.time() - start_time
    tps = num_requests / total_time
    
    print(f"  总耗时: {total_time:.2f}秒")
    print(f"  TPS: {tps:.2f}")
    print(f"  平均每个请求时间: {(total_time*1000/num_requests):.2f}ms")
    return tps

def test_asynchronous_processing(num_requests, processing_time_ms, callback_delay_ms):
    """
    测试异步处理方式的性能
    """
    print(f"测试异步处理: {num_requests}个请求, 处理时间{processing_time_ms}ms, 回调延迟{callback_delay_ms}ms")
    
    # 创建线程池处理回调
    callback_executor = ThreadPoolExecutor(max_workers=20)
    
    start_time = time.time()
    
    callback_futures = []
    
    for i in range(num_requests):
        # 模拟消息处理
        time.sleep(processing_time_ms / 1000.0)
        
        # 异步发送回调（非阻塞）
        future = callback_executor.submit(simulate_callback_with_delay, callback_delay_ms)
        callback_futures.append(future)
        
        # 立即确认消息
        pass
    
    # 等待所有回调完成（仅用于测试）
    for future in callback_futures:
        future.result()
    
    total_time = time.time() - start_time
    tps = num_requests / total_time
    
    callback_executor.shutdown(wait=True)
    
    print(f"  总耗时: {total_time:.2f}秒")
    print(f"  TPS: {tps:.2f}")
    print(f"  平均每个请求时间: {(total_time*1000/num_requests):.2f}ms")
    return tps

def test_performance_comparison():
    """
    性能对比测试
    """
    print("回调延迟对系统性能的影响测试")
    print("=" * 50)
    
    # 测试参数
    num_requests = 100
    processing_time_ms = 1  # 消息处理时间1ms
    callback_delay_ms = 10   # 回调延迟10ms
    
    print(f"测试配置:")
    print(f"  消息数量: {num_requests}")
    print(f"  消息处理时间: {processing_time_ms}ms")
    print(f"  回调延迟: {callback_delay_ms}ms")
    print()
    
    # 测试同步处理
    sync_tps = test_synchronous_processing(num_requests, processing_time_ms, callback_delay_ms)
    print()
    
    # 测试异步处理
    async_tps = test_asynchronous_processing(num_requests, processing_time_ms, callback_delay_ms)
    print()
    
    # 性能对比
    improvement = async_tps / sync_tps
    print(f"性能提升: {improvement:.2f}倍")
    
    print("\n结论:")
    print(f"1. 同步处理TPS: {sync_tps:.2f}")
    print(f"2. 异步处理TPS: {async_tps:.2f}")
    print(f"3. 性能提升: {improvement:.2f}倍")
    print("4. 回调延迟严重影响同步处理的性能")
    print("5. 异步处理可以显著提高系统吞吐量")

def test_different_callback_delays():
    """
    测试不同回调延迟的影响
    """
    print("\n\n不同回调延迟对性能的影响")
    print("=" * 50)
    
    num_requests = 100
    processing_time_ms = 1
    
    delays = [1, 5, 10, 20, 50]  # 不同的回调延迟（ms）
    
    print(f"{'回调延迟(ms)':<12} {'同步TPS':<10} {'异步TPS':<10} {'提升倍数':<10}")
    print("-" * 45)
    
    for delay in delays:
        # 测试同步处理
        sync_tps = test_synchronous_processing(num_requests, processing_time_ms, delay)
        
        # 测试异步处理
        async_tps = test_asynchronous_processing(num_requests, processing_time_ms, delay)
        
        improvement = async_tps / sync_tps
        print(f"{delay:<12} {sync_tps:<10.2f} {async_tps:<10.2f} {improvement:<10.2f}")
        
        # 重置时间以避免累积影响
        time.sleep(0.1)

if __name__ == "__main__":
    test_performance_comparison()
    test_different_callback_delays()