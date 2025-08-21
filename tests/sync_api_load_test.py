#!/usr/bin/env python3
"""
同步风险评估接口性能测试脚本
直接测试深度分析服务的同步接口性能
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
import matplotlib as mpl
import argparse

# 配置matplotlib显示中文
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'sans-serif'

# 备用方案：检测操作系统并设置合适的字体
import platform
system = platform.system()
if system == 'Windows':
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun']
elif system == 'Linux':
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'AR PL UMing CN']
elif system == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['PingFang SC', 'STHeiti', 'Heiti TC']

# 默认测试配置
DEFAULT_CONCURRENT_USERS = 20   # 默认并发用户数
DEFAULT_REQUESTS_PER_USER = 5   # 默认每用户请求数
BASE_URL = "http://localhost:5000"  # 深度分析服务的默认地址
ENDPOINT = f"{BASE_URL}/api/risk-assessment"  # 同步风险评估接口
REQUEST_TIMEOUT = 10        # 单次请求超时时间(秒)

# 测试数据
payload = {
    "doctorId": "D440305034671",
    "date": "2024-08-31"
}

def send_sync_request(user_id, request_num):
    """发送同步风险评估请求"""
    start_time = time.time()
    result = {
        "userId": user_id,
        "requestNumber": request_num,
        "success": False,
        "responseTime": 0,
        "error": None
    }
    
    try:
        response = requests.post(
            ENDPOINT, 
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )
        
        end_time = time.time()
        result["responseTime"] = (end_time - start_time) * 1000  # 毫秒
        
        if response.status_code == 200:
            result["success"] = True
            print(f"请求成功: 用户 {user_id}, 请求 {request_num} - {result['responseTime']:.2f}ms")
        else:
            result["error"] = f"HTTP {response.status_code}: {response.text}"
            print(f"请求失败: 用户 {user_id}, 请求 {request_num} - HTTP {response.status_code}")
            
    except Exception as e:
        end_time = time.time()
        result["responseTime"] = (end_time - start_time) * 1000
        result["error"] = str(e)
        print(f"请求异常: 用户 {user_id}, 请求 {request_num} - {str(e)}")
    
    # 随机延迟，模拟用户思考时间
    time.sleep(random.uniform(0.05, 0.2))
    return result

def run_load_test(concurrent_users, requests_per_user):
    """运行负载测试"""
    print(f"开始同步接口性能测试 - {concurrent_users}个并发用户，每用户{requests_per_user}个请求")
    print(f"目标端点: {ENDPOINT}")
    print("=" * 50)
    
    start_time = time.time()
    results = []
    
    # 创建所有测试任务
    tasks = []
    for user in range(1, concurrent_users + 1):
        for req in range(1, requests_per_user + 1):
            tasks.append((user, req))
    
    # 使用线程池并发执行
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        future_to_task = {executor.submit(send_sync_request, user, req): (user, req) for user, req in tasks}
        
        for future in concurrent.futures.as_completed(future_to_task):
            user, req = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"任务异常: 用户 {user}, 请求 {req} - {str(e)}")
    
    # 计算测试结果
    end_time = time.time()
    total_time = end_time - start_time
    
    return results, total_time

def analyze_results(results, total_time, concurrent_users):
    """分析测试结果并生成报告"""
    if not results:
        print("无测试结果")
        return None
    
    # 转换为DataFrame便于分析
    df = pd.DataFrame(results)
    
    # 添加并发用户数标记
    df['concurrent_users'] = concurrent_users
    
    # 基本指标
    total_requests = len(results)
    successful_requests = df['success'].sum()
    success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
    
    # 响应时间统计
    if not df.empty and 'responseTime' in df:
        avg_response_time = df['responseTime'].mean()
        min_response_time = df['responseTime'].min()
        max_response_time = df['responseTime'].max()
        p95_response_time = df['responseTime'].quantile(0.95)
    else:
        avg_response_time = min_response_time = max_response_time = p95_response_time = 0
    
    # 计算QPS
    qps = total_requests / total_time if total_time > 0 else 0
    
    # 打印结果
    print("\n" + "=" * 80)
    print(f"并发用户数: {concurrent_users} - 性能测试结果:")
    print(f"总请求数: {total_requests}")
    print(f"成功请求: {successful_requests}")
    print(f"成功率: {success_rate:.2f}%")
    print("-" * 40)
    print(f"平均响应时间: {avg_response_time:.2f}ms")
    print(f"最低响应时间: {min_response_time:.2f}ms")
    print(f"最高响应时间: {max_response_time:.2f}ms")
    print(f"95%响应时间: {p95_response_time:.2f}ms")
    print(f"QPS (每秒查询率): {qps:.2f} req/s")
    print(f"总执行时间: {total_time:.2f}秒")
    print("=" * 80)
    
    # 创建results目录保存结果
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_dir = "test_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # 保存结果到CSV
    csv_filename = os.path.join(results_dir, f"sync_test_c{concurrent_users}_{timestamp}.csv")
    df.to_csv(csv_filename, index=False)
    print(f"结果已保存至: {csv_filename}")
    
    try:
        # 绘制响应时间分布图
        plt.figure(figsize=(12, 6))
        plt.hist(df['responseTime'], bins=20, alpha=0.7, color='blue')
        plt.axvline(avg_response_time, color='r', linestyle='dashed', linewidth=1, label=f'平均值: {avg_response_time:.2f}ms')
        plt.axvline(p95_response_time, color='g', linestyle='dashed', linewidth=1, label=f'95%: {p95_response_time:.2f}ms')
        plt.title(f'并发用户数: {concurrent_users} - 同步接口响应时间分布')
        plt.xlabel('响应时间 (ms)')
        plt.ylabel('请求数')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        chart_filename = os.path.join(results_dir, f"sync_test_c{concurrent_users}_{timestamp}.png")
        plt.savefig(chart_filename)
        print(f"响应时间图表已保存至: {chart_filename}")
        
    except Exception as e:
        print(f"图表生成失败: {str(e)}")
    
    return df

def compare_results(all_results, timestamp):
    """比较不同并发用户数下的测试结果"""
    print("\n" + "=" * 80)
    print("不同并发用户数的性能比较")
    print("=" * 80)
    
    if not all_results:
        print("没有可比较的结果")
        return
    
    # 准备比较数据
    compare_data = []
    for user_count, df in all_results.items():
        avg_response = df['responseTime'].mean()
        p95_response = df['responseTime'].quantile(0.95)
        success_rate = (df['success'].sum() / len(df)) * 100
        
        compare_data.append({
            '并发用户数': user_count,
            '平均响应时间': avg_response,
            '95%响应时间': p95_response,
            '成功率': success_rate,
            '样本数': len(df)
        })
    
    # 转换为DataFrame并打印
    compare_df = pd.DataFrame(compare_data)
    compare_df = compare_df.set_index('并发用户数')
    print("\n性能比较表:")
    print(compare_df.to_string(float_format=lambda x: f"{x:.2f}"))
    
    # 保存比较结果
    results_dir = "test_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # 保存到CSV
    csv_filename = os.path.join(results_dir, f"sync_compare_results_{timestamp}.csv")
    compare_df.to_csv(csv_filename)
    print(f"\n比较结果已保存至: {csv_filename}")
    
    try:
        # 绘制不同并发用户数的响应时间比较图
        plt.figure(figsize=(14, 8))
        
        # 平均响应时间
        plt.subplot(2, 2, 1)
        plt.bar(compare_df.index, compare_df['平均响应时间'], color='blue', alpha=0.7)
        plt.title('平均响应时间比较')
        plt.xlabel('并发用户数')
        plt.ylabel('响应时间 (ms)')
        plt.grid(True, alpha=0.3)
        
        # 95%响应时间
        plt.subplot(2, 2, 2)
        plt.bar(compare_df.index, compare_df['95%响应时间'], color='green', alpha=0.7)
        plt.title('95%响应时间比较')
        plt.xlabel('并发用户数')
        plt.ylabel('响应时间 (ms)')
        plt.grid(True, alpha=0.3)
        
        # 成功率
        plt.subplot(2, 2, 3)
        plt.bar(compare_df.index, compare_df['成功率'], color='red', alpha=0.7)
        plt.title('请求成功率比较')
        plt.xlabel('并发用户数')
        plt.ylabel('成功率 (%)')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        chart_filename = os.path.join(results_dir, f"sync_compare_results_{timestamp}.png")
        plt.savefig(chart_filename)
        print(f"比较图表已保存至: {chart_filename}")
        
        # 生成详细的性能曲线图
        plt.figure(figsize=(12, 6))
        
        # 并发用户数与响应时间的关系
        plt.plot(compare_df.index, compare_df['平均响应时间'], 'o-', label='平均响应时间', color='blue')
        plt.plot(compare_df.index, compare_df['95%响应时间'], 's-', label='95%响应时间', color='green')
        
        plt.title('并发用户数与响应时间的关系')
        plt.xlabel('并发用户数')
        plt.ylabel('响应时间 (ms)')
        plt.legend()
        plt.grid(True)
        
        curve_filename = os.path.join(results_dir, f"sync_response_curve_{timestamp}.png")
        plt.savefig(curve_filename)
        print(f"响应时间曲线图已保存至: {curve_filename}")
        
    except Exception as e:
        print(f"比较图表生成失败: {str(e)}")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='同步风险评估接口性能测试工具')
    parser.add_argument('-c', '--concurrency', type=str, default='20',
                        help='并发用户数，可以是单个数值或逗号分隔的多个数值，例如 "10,20,50"')
    parser.add_argument('-r', '--requests', type=int, default=DEFAULT_REQUESTS_PER_USER,
                        help=f'每用户请求数 (默认: {DEFAULT_REQUESTS_PER_USER})')
    parser.add_argument('-u', '--url', type=str, default=None,
                        help=f'API基础URL (默认: {BASE_URL})')
    return parser.parse_args()

if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置基础URL
    if args.url:
        BASE_URL = args.url
        ENDPOINT = f"{BASE_URL}/api/risk-assessment"
        print(f"使用自定义URL: {BASE_URL}")
    
    # 解析并发用户数配置
    concurrency_list = [int(c.strip()) for c in args.concurrency.split(',')]
    print(f"将测试并发用户数: {concurrency_list}")
    requests_per_user = args.requests
    
    # 记录测试时间戳
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # 保存所有测试结果
    all_results = {}
    
    # 对每个并发用户数进行测试
    for concurrent_users in concurrency_list:
        print(f"\n\n开始测试并发用户数: {concurrent_users}\n{'-' * 50}")
        results, total_time = run_load_test(concurrent_users, requests_per_user)
        df = analyze_results(results, total_time, concurrent_users)
        if df is not None:
            all_results[concurrent_users] = df
        
        # 测试间短暂休息，让系统恢复
        if len(concurrency_list) > 1:
            sleep_time = min(30, concurrent_users / 2)
            print(f"休息 {sleep_time:.1f} 秒后开始下一轮测试...")
            time.sleep(sleep_time)
    
    # 如果测试了多个并发用户数，生成比较报告
    if len(all_results) > 1:
        compare_results(all_results, timestamp)
        print("\n所有测试已完成，上方为不同并发用户数的性能比较。") 