#!/usr/bin/env python3
"""
吞吐量比较测试脚本
对比异步风险评估API和同步风险评估API的吞吐量差异
"""

import requests
import json
import time
import random
import concurrent.futures
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import numpy as np
import argparse
from threading import Lock

# 配置matplotlib显示中文
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'sans-serif'

# 测试配置
DEFAULT_CONCURRENT_USERS = 1000    # 默认并发用户数
DEFAULT_TEST_DURATION = 60       # 默认测试持续时间(秒)
DEFAULT_REPORT_INTERVAL = 2      # 默认报告间隔(秒)
ASYNC_BASE_URL = "http://localhost:8080"
SYNC_BASE_URL = "http://localhost:5000"
ASYNC_SUBMIT_ENDPOINT = f"{ASYNC_BASE_URL}/api/async-risk-assessment/assess"
ASYNC_RESULT_TEMPLATE = f"{ASYNC_BASE_URL}/api/async-risk-assessment/{{}}"
SYNC_ENDPOINT = f"{SYNC_BASE_URL}/api/risk-assessment"
REQUEST_TIMEOUT = 10             # 请求超时时间(秒)
POLL_INTERVAL = 0.5              # 轮询间隔(秒)
MAX_POLL_COUNT = 10              # 最大轮询次数

# 测试数据
payload = {
    "doctorId": "D440305034671",
    "date": "2024-08-31"
}

# 全局计数器
class Counter:
    def __init__(self):
        self.lock = Lock()
        self.reset()
    
    def reset(self):
        with self.lock:
            self.async_requests = 0
            self.async_success = 0
            self.async_failures = 0
            self.sync_requests = 0
            self.sync_success = 0
            self.sync_failures = 0
            self.async_response_times = []
            self.sync_response_times = []

    def add_async_request(self, success, response_time=None):
        with self.lock:
            self.async_requests += 1
            if success:
                self.async_success += 1
                if response_time is not None:
                    self.async_response_times.append(response_time)
            else:
                self.async_failures += 1
    
    def add_sync_request(self, success, response_time=None):
        with self.lock:
            self.sync_requests += 1
            if success:
                self.sync_success += 1
                if response_time is not None:
                    self.sync_response_times.append(response_time)
            else:
                self.sync_failures += 1
    
    def get_stats(self):
        with self.lock:
            return {
                "async_requests": self.async_requests,
                "async_success": self.async_success,
                "async_failures": self.async_failures,
                "sync_requests": self.sync_requests,
                "sync_success": self.sync_success,
                "sync_failures": self.sync_failures,
                "async_response_times": self.async_response_times.copy() if self.async_response_times else [],
                "sync_response_times": self.sync_response_times.copy() if self.sync_response_times else []
            }

# 全局计数器实例
counter = Counter()

def extract_request_id(response_text):
    """从异步响应中提取请求ID"""
    try:
        return response_text.split('ID: ')[1]
    except (IndexError, AttributeError):
        return None

def poll_result(request_id, max_attempts=MAX_POLL_COUNT, interval=POLL_INTERVAL):
    """轮询异步请求结果"""
    result_url = ASYNC_RESULT_TEMPLATE.format(request_id)
    attempts = 0
    
    while attempts < max_attempts:
        try:
            response = requests.get(
                result_url,
                timeout=REQUEST_TIMEOUT
            )
            
            # 如果请求成功(200)，表示结果已就绪
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json(),
                    "attempts": attempts + 1
                }
                
            # 如果是404，说明结果尚未就绪，继续轮询
            elif response.status_code == 404:
                attempts += 1
                time.sleep(interval)
                continue
                
            # 其他错误
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "attempts": attempts + 1
                }
                
        except Exception as e:
            attempts += 1
            time.sleep(interval)
    
    # 超过最大尝试次数
    return {
        "status": "timeout",
        "error": f"超过最大轮询次数 {max_attempts}",
        "attempts": attempts
    }

def make_async_request():
    """发送异步请求并等待结果"""
    start_time = time.time()
    success = False
    
    try:
        # 步骤1: 提交异步请求
        submit_response = requests.post(
            ASYNC_SUBMIT_ENDPOINT, 
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )
        
        if submit_response.status_code == 200:
            # 提取请求ID
            request_id = extract_request_id(submit_response.text)
            if request_id:
                # 步骤2: 轮询获取结果
                poll_result_data = poll_result(request_id)
                
                if poll_result_data["status"] == "success":
                    success = True
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # 毫秒
        counter.add_async_request(success, response_time)
        
    except Exception as e:
        counter.add_async_request(False)

def make_sync_request():
    """发送同步请求"""
    start_time = time.time()
    success = False
    
    try:
        response = requests.post(
            SYNC_ENDPOINT, 
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            success = True
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # 毫秒
        counter.add_sync_request(success, response_time)
        
    except Exception as e:
        counter.add_sync_request(False)

def async_worker(stop_time):
    """异步请求工作线程"""
    while time.time() < stop_time:
        make_async_request()
        # 随机短暂休息，模拟真实用户行为
        time.sleep(random.uniform(0.01, 0.05))

def sync_worker(stop_time):
    """同步请求工作线程"""
    while time.time() < stop_time:
        make_sync_request()
        # 随机短暂休息，模拟真实用户行为
        time.sleep(random.uniform(0.01, 0.05))

def run_throughput_test(concurrent_users, test_duration, report_interval):
    """运行吞吐量对比测试"""
    # 初始化计数器
    counter.reset()
    
    # 测试时间点
    start_time = time.time()
    stop_time = start_time + test_duration
    
    # 保存周期性报告数据
    timestamps = []
    async_tps_values = []
    sync_tps_values = []
    
    print(f"开始吞吐量对比测试 - {concurrent_users}个并发用户，持续{test_duration}秒")
    print(f"异步API端点: {ASYNC_SUBMIT_ENDPOINT}")
    print(f"同步API端点: {SYNC_ENDPOINT}")
    print("=" * 50)
    
    # 创建并启动工作线程
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users*2) as executor:
        # 启动异步工作线程
        for _ in range(concurrent_users):
            futures.append(executor.submit(async_worker, stop_time))
        
        # 启动同步工作线程
        for _ in range(concurrent_users):
            futures.append(executor.submit(sync_worker, stop_time))
        
        # 周期性报告
        last_report_time = time.time()
        last_async_requests = 0
        last_sync_requests = 0
        
        while time.time() < stop_time:
            time.sleep(0.1)  # 避免CPU过载
            
            current_time = time.time()
            if current_time - last_report_time >= report_interval:
                stats = counter.get_stats()
                
                # 计算这个周期的TPS
                time_diff = current_time - last_report_time
                async_tps = (stats["async_requests"] - last_async_requests) / time_diff
                sync_tps = (stats["sync_requests"] - last_sync_requests) / time_diff
                
                # 更新上次报告的值
                last_report_time = current_time
                last_async_requests = stats["async_requests"]
                last_sync_requests = stats["sync_requests"]
                
                # 保存数据用于图表
                timestamps.append(current_time - start_time)
                async_tps_values.append(async_tps)
                sync_tps_values.append(sync_tps)
                
                # 打印报告
                elapsed = current_time - start_time
                print(f"\n时间点: {elapsed:.1f}秒")
                print(f"异步API - TPS: {async_tps:.2f}/秒, 成功: {stats['async_success']}, 失败: {stats['async_failures']}")
                print(f"同步API - TPS: {sync_tps:.2f}/秒, 成功: {stats['sync_success']}, 失败: {stats['sync_failures']}")
    
    # 测试结束，获取最终统计
    final_stats = counter.get_stats()
    test_duration = time.time() - start_time
    
    # 计算吞吐量
    async_tps = final_stats["async_success"] / test_duration if test_duration > 0 else 0
    sync_tps = final_stats["sync_success"] / test_duration if test_duration > 0 else 0
    
    print("\n" + "=" * 80)
    print("吞吐量对比测试结果:")
    print(f"总测试时间: {test_duration:.2f}秒")
    print("-" * 40)
    print(f"异步API - 总请求: {final_stats['async_requests']}, 成功: {final_stats['async_success']}, 失败: {final_stats['async_failures']}")
    print(f"异步API - 平均吞吐量: {async_tps:.2f} 请求/秒")
    
    if final_stats["async_response_times"]:
        avg_time = sum(final_stats["async_response_times"]) / len(final_stats["async_response_times"])
        print(f"异步API - 平均响应时间: {avg_time:.2f}ms")
    
    print("-" * 40)
    print(f"同步API - 总请求: {final_stats['sync_requests']}, 成功: {final_stats['sync_success']}, 失败: {final_stats['sync_failures']}")
    print(f"同步API - 平均吞吐量: {sync_tps:.2f} 请求/秒")
    
    if final_stats["sync_response_times"]:
        avg_time = sum(final_stats["sync_response_times"]) / len(final_stats["sync_response_times"])
        print(f"同步API - 平均响应时间: {avg_time:.2f}ms")
    
    print("=" * 80)
    
    # 绘制图表并保存结果
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_dir = "test_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # 创建结果数据框
    result_data = {
        "async_requests": final_stats["async_requests"],
        "async_success": final_stats["async_success"],
        "async_failures": final_stats["async_failures"],
        "async_tps": async_tps,
        "sync_requests": final_stats["sync_requests"],
        "sync_success": final_stats["sync_success"],
        "sync_failures": final_stats["sync_failures"],
        "sync_tps": sync_tps,
        "test_duration": test_duration,
        "concurrent_users": concurrent_users,
    }
    
    # 保存结果到CSV
    result_df = pd.DataFrame([result_data])
    csv_filename = os.path.join(results_dir, f"throughput_test_c{concurrent_users}_{timestamp}.csv")
    result_df.to_csv(csv_filename, index=False)
    print(f"结果已保存至: {csv_filename}")
    
    # 保存时间序列数据
    if timestamps:
        time_series_data = {
            "timestamp": timestamps,
            "async_tps": async_tps_values,
            "sync_tps": sync_tps_values
        }
        time_series_df = pd.DataFrame(time_series_data)
        time_series_csv = os.path.join(results_dir, f"throughput_series_c{concurrent_users}_{timestamp}.csv")
        time_series_df.to_csv(time_series_csv, index=False)
        
        # 绘制TPS随时间变化的图表
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, async_tps_values, 'b-', label='异步API')
        plt.plot(timestamps, sync_tps_values, 'r-', label='同步API')
        plt.title(f'并发用户数: {concurrent_users} - 吞吐量随时间变化')
        plt.xlabel('时间 (秒)')
        plt.ylabel('吞吐量 (请求/秒)')
        plt.legend()
        plt.grid(True)
        
        tps_chart_filename = os.path.join(results_dir, f"throughput_chart_c{concurrent_users}_{timestamp}.png")
        plt.savefig(tps_chart_filename)
        print(f"吞吐量图表已保存至: {tps_chart_filename}")
    
    # 绘制响应时间分布图
    try:
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        if final_stats["async_response_times"]:
            plt.hist(final_stats["async_response_times"], bins=20, alpha=0.7, color='blue')
            plt.axvline(np.mean(final_stats["async_response_times"]), color='r', linestyle='dashed', 
                       label=f'平均: {np.mean(final_stats["async_response_times"]):.2f}ms')
            plt.title('异步API响应时间分布')
            plt.xlabel('响应时间 (ms)')
            plt.ylabel('请求数')
            plt.legend()
        else:
            plt.text(0.5, 0.5, "无数据", ha='center', va='center')
            plt.title('异步API响应时间分布')
        
        plt.subplot(1, 2, 2)
        if final_stats["sync_response_times"]:
            plt.hist(final_stats["sync_response_times"], bins=20, alpha=0.7, color='red')
            plt.axvline(np.mean(final_stats["sync_response_times"]), color='b', linestyle='dashed',
                       label=f'平均: {np.mean(final_stats["sync_response_times"]):.2f}ms')
            plt.title('同步API响应时间分布')
            plt.xlabel('响应时间 (ms)')
            plt.ylabel('请求数')
            plt.legend()
        else:
            plt.text(0.5, 0.5, "无数据", ha='center', va='center')
            plt.title('同步API响应时间分布')
        
        plt.tight_layout()
        rt_chart_filename = os.path.join(results_dir, f"response_time_c{concurrent_users}_{timestamp}.png")
        plt.savefig(rt_chart_filename)
        print(f"响应时间分布图已保存至: {rt_chart_filename}")
        
    except Exception as e:
        print(f"图表生成失败: {str(e)}")
    
    return result_data

def compare_results(all_results, timestamp):
    """比较不同并发用户数下的测试结果"""
    print("\n" + "=" * 80)
    print("不同并发用户数的吞吐量比较")
    print("=" * 80)
    
    if not all_results:
        print("没有可比较的结果")
        return
    
    # 准备比较数据
    compare_data = []
    for user_count, result in all_results.items():
        compare_data.append({
            '并发用户数': user_count,
            '异步API吞吐量': result["async_tps"],
            '同步API吞吐量': result["sync_tps"],
            '异步API成功率': result["async_success"] / result["async_requests"] * 100 if result["async_requests"] > 0 else 0,
            '同步API成功率': result["sync_success"] / result["sync_requests"] * 100 if result["sync_requests"] > 0 else 0,
        })
    
    # 转换为DataFrame并打印
    compare_df = pd.DataFrame(compare_data)
    compare_df = compare_df.set_index('并发用户数')
    print("\n吞吐量比较表:")
    print(compare_df.to_string(float_format=lambda x: f"{x:.2f}"))
    
    # 保存比较结果
    results_dir = "test_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # 保存到CSV
    csv_filename = os.path.join(results_dir, f"throughput_compare_{timestamp}.csv")
    compare_df.to_csv(csv_filename)
    print(f"\n比较结果已保存至: {csv_filename}")
    
    try:
        # 绘制比较图表
        plt.figure(figsize=(14, 8))
        
        # 吞吐量比较
        plt.subplot(2, 1, 1)
        x = list(compare_df.index)
        width = 0.35
        plt.bar([i - width/2 for i in range(len(x))], compare_df['异步API吞吐量'], width=width, label='异步API', color='blue', alpha=0.7)
        plt.bar([i + width/2 for i in range(len(x))], compare_df['同步API吞吐量'], width=width, label='同步API', color='red', alpha=0.7)
        plt.xticks(range(len(x)), x)
        plt.title('吞吐量比较 (TPS)')
        plt.xlabel('并发用户数')
        plt.ylabel('吞吐量 (请求/秒)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 成功率比较
        plt.subplot(2, 1, 2)
        plt.bar([i - width/2 for i in range(len(x))], compare_df['异步API成功率'], width=width, label='异步API', color='blue', alpha=0.7)
        plt.bar([i + width/2 for i in range(len(x))], compare_df['同步API成功率'], width=width, label='同步API', color='red', alpha=0.7)
        plt.xticks(range(len(x)), x)
        plt.title('成功率比较')
        plt.xlabel('并发用户数')
        plt.ylabel('成功率 (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        chart_filename = os.path.join(results_dir, f"throughput_compare_{timestamp}.png")
        plt.savefig(chart_filename)
        print(f"比较图表已保存至: {chart_filename}")
    
    except Exception as e:
        print(f"比较图表生成失败: {str(e)}")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='吞吐量比较测试工具')
    parser.add_argument('-c', '--concurrency', type=str, default=str(DEFAULT_CONCURRENT_USERS),
                        help=f'并发用户数，可以是单个数值或逗号分隔的多个数值，例如 "50,100,200" (默认: {DEFAULT_CONCURRENT_USERS})')
    parser.add_argument('-d', '--duration', type=int, default=DEFAULT_TEST_DURATION,
                        help=f'每轮测试持续时间(秒) (默认: {DEFAULT_TEST_DURATION})')
    parser.add_argument('-i', '--interval', type=int, default=DEFAULT_REPORT_INTERVAL,
                        help=f'报告间隔(秒) (默认: {DEFAULT_REPORT_INTERVAL})')
    parser.add_argument('-a', '--async-url', type=str, default=None,
                        help=f'异步API基础URL (默认: {ASYNC_BASE_URL})')
    parser.add_argument('-s', '--sync-url', type=str, default=None,
                        help=f'同步API基础URL (默认: {SYNC_BASE_URL})')
    return parser.parse_args()

if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置基础URL
    if args.async_url:
        ASYNC_BASE_URL = args.async_url
        ASYNC_SUBMIT_ENDPOINT = f"{ASYNC_BASE_URL}/api/async-risk-assessment/assess"
        ASYNC_RESULT_TEMPLATE = f"{ASYNC_BASE_URL}/api/async-risk-assessment/{{}}"
        print(f"使用自定义异步API URL: {ASYNC_BASE_URL}")
    
    if args.sync_url:
        SYNC_BASE_URL = args.sync_url
        SYNC_ENDPOINT = f"{SYNC_BASE_URL}/api/risk-assessment"
        print(f"使用自定义同步API URL: {SYNC_BASE_URL}")
    
    # 解析并发用户数配置
    concurrency_list = [int(c.strip()) for c in args.concurrency.split(',')]
    print(f"将测试并发用户数: {concurrency_list}")
    
    # 记录测试时间戳
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # 保存所有测试结果
    all_results = {}
    
    # 对每个并发用户数进行测试
    for concurrent_users in concurrency_list:
        print(f"\n\n开始测试并发用户数: {concurrent_users}\n{'-' * 50}")
        result = run_throughput_test(concurrent_users, args.duration, args.interval)
        all_results[concurrent_users] = result
        
        # 测试间短暂休息，让系统恢复
        if len(concurrency_list) > 1:
            sleep_time = min(30, concurrent_users / 5)
            print(f"休息 {sleep_time:.1f} 秒后开始下一轮测试...")
            time.sleep(sleep_time)
    
    # 如果测试了多个并发用户数，生成比较报告
    if len(all_results) > 1:
        compare_results(all_results, timestamp)
        print("\n所有测试已完成，上方为不同并发用户数的吞吐量比较。")