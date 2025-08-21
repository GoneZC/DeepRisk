#!/usr/bin/env python3
"""
消息队列优势量化测试脚本
专门测试异步API在高负载情况下的优势
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
import threading

# 配置matplotlib显示中文
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'sans-serif'

# 测试配置
DEFAULT_BURST_SIZE = 200        # 默认突发请求数量
DEFAULT_MONITOR_DURATION = 300  # 默认监控持续时间(秒)
DEFAULT_REPORT_INTERVAL = 5     # 默认报告间隔(秒)
ASYNC_BASE_URL = "http://localhost:8080"
SYNC_BASE_URL = "http://localhost:5000"
ASYNC_SUBMIT_ENDPOINT = f"{ASYNC_BASE_URL}/api/async-risk-assessment/assess"
ASYNC_RESULT_TEMPLATE = f"{ASYNC_BASE_URL}/api/async-risk-assessment/{{}}"
SYNC_ENDPOINT = f"{SYNC_BASE_URL}/api/risk-assessment"
REQUEST_TIMEOUT = 10             # 请求超时时间(秒)
POLL_INTERVAL = 1.0              # 轮询间隔(秒)
MAX_POLL_COUNT = 180             # 最大轮询次数(延长到3分钟)

# 测试数据
payload = {
    "doctorId": "D440305034671",
    "date": "2024-08-31"
}

# 结果跟踪器
class ResultTracker:
    def __init__(self):
        self.lock = Lock()
        self.reset()
    
    def reset(self):
        with self.lock:
            # 异步API统计
            self.async_submitted = 0
            self.async_accepted = 0
            self.async_rejected = 0
            self.async_completed = 0
            self.async_pending = set()  # 跟踪待处理的请求ID
            self.async_response_times = []
            
            # 同步API统计
            self.sync_submitted = 0
            self.sync_accepted = 0
            self.sync_rejected = 0
            self.sync_response_times = []
            
            # 请求ID到时间戳的映射，用于计算端到端时间
            self.request_start_times = {}
            self.request_end_times = {}
    
    def track_async_submit(self, success, request_id=None):
        with self.lock:
            self.async_submitted += 1
            
            if success and request_id:
                self.async_accepted += 1
                self.async_pending.add(request_id)
                # 记录开始时间
                self.request_start_times[request_id] = time.time()
            else:
                self.async_rejected += 1
    
    def track_async_complete(self, request_id, success):
        with self.lock:
            if request_id in self.async_pending:
                self.async_pending.remove(request_id)
                
                if success:
                    self.async_completed += 1
                    # 记录结束时间
                    self.request_end_times[request_id] = time.time()
                    
                    # 计算端到端时间
                    if request_id in self.request_start_times:
                        start_time = self.request_start_times[request_id]
                        end_time = self.request_end_times[request_id]
                        e2e_time = (end_time - start_time) * 1000  # 毫秒
                        self.async_response_times.append(e2e_time)
    
    def track_sync_request(self, success, response_time=None):
        with self.lock:
            self.sync_submitted += 1
            
            if success:
                self.sync_accepted += 1
                if response_time is not None:
                    self.sync_response_times.append(response_time)
            else:
                self.sync_rejected += 1
    
    def get_stats(self):
        with self.lock:
            return {
                # 异步API指标
                "async_submitted": self.async_submitted,
                "async_accepted": self.async_accepted,
                "async_rejected": self.async_rejected,
                "async_completed": self.async_completed,
                "async_pending": len(self.async_pending),
                "async_response_times": self.async_response_times.copy() if self.async_response_times else [],
                
                # 同步API指标
                "sync_submitted": self.sync_submitted,
                "sync_accepted": self.sync_accepted,
                "sync_rejected": self.sync_rejected,
                "sync_response_times": self.sync_response_times.copy() if self.sync_response_times else [],
                
                # 请求ID集合
                "pending_request_ids": list(self.async_pending)
            }

# 全局跟踪器实例
tracker = ResultTracker()

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
                tracker.track_async_complete(request_id, True)
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
                tracker.track_async_complete(request_id, False)
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

def submit_async_request():
    """提交异步请求，不等待处理完成"""
    try:
        # 提交异步请求
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
                tracker.track_async_submit(True, request_id)
                return request_id
        
        tracker.track_async_submit(False)
        return None
        
    except Exception as e:
        tracker.track_async_submit(False)
        return None

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
        tracker.track_sync_request(success, response_time if success else None)
        
    except Exception as e:
        tracker.track_sync_request(False)

def background_poller():
    """后台轮询线程，持续检查异步结果"""
    print("启动后台轮询线程")
    while True:
        stats = tracker.get_stats()
        pending_ids = stats["pending_request_ids"]
        
        # 如果没有待处理请求，休息一下
        if not pending_ids:
            time.sleep(1)
            continue
        
        # 为不超过5个待处理请求启动轮询
        for request_id in pending_ids[:5]:
            threading.Thread(target=poll_result, args=(request_id,)).start()
            
        # 避免过快轮询
        time.sleep(2)

def burst_test(burst_size, monitor_duration, report_interval):
    """
    突发请求测试，量化MQ优势
    1. 发送突发请求
    2. 监控请求处理情况
    """
    # 重置跟踪器
    tracker.reset()
    
    # 启动后台轮询线程
    poller_thread = threading.Thread(target=background_poller, daemon=True)
    poller_thread.start()
    
    # 时间点
    start_time = time.time()
    end_monitor_time = start_time + monitor_duration
    
    # 用于记录时间序列数据
    time_series_data = {
        "timestamp": [],
        "async_accepted": [],
        "async_completed": [],
        "async_pending": [],
        "sync_accepted": []
    }
    
    print(f"开始突发请求测试 - {burst_size}个并发请求")
    print(f"异步API端点: {ASYNC_SUBMIT_ENDPOINT}")
    print(f"同步API端点: {SYNC_ENDPOINT}")
    print("=" * 50)
    
    # 发送突发请求
    print(f"发送 {burst_size} 个突发请求...")
    async_futures = []
    sync_futures = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(burst_size, 50)) as executor:
        # 提交异步请求
        for _ in range(burst_size):
            async_futures.append(executor.submit(submit_async_request))
        
        # 提交同步请求
        for _ in range(burst_size):
            sync_futures.append(executor.submit(make_sync_request))
            
        # 等待所有提交完成
        concurrent.futures.wait(async_futures + sync_futures)
    
    print("突发请求已全部提交，开始监控处理情况...")
    
    # 监控处理情况
    last_report_time = time.time()
    
    while time.time() < end_monitor_time:
        # 定期报告
        current_time = time.time()
        if current_time - last_report_time >= report_interval:
            stats = tracker.get_stats()
            
            # 更新时间序列数据
            elapsed = current_time - start_time
            time_series_data["timestamp"].append(elapsed)
            time_series_data["async_accepted"].append(stats["async_accepted"])
            time_series_data["async_completed"].append(stats["async_completed"])
            time_series_data["async_pending"].append(stats["async_pending"])
            time_series_data["sync_accepted"].append(stats["sync_accepted"])
            
            # 打印状态报告
            print(f"\n时间点: {elapsed:.1f}秒")
            print(f"异步API - 已接受: {stats['async_accepted']}, 已完成: {stats['async_completed']}, 待处理: {stats['async_pending']}")
            print(f"同步API - 已接受: {stats['sync_accepted']}, 已拒绝: {stats['sync_rejected']}")
            
            # 检查是否所有异步请求都已处理完成
            if stats["async_pending"] == 0 and stats["async_accepted"] > 0:
                if stats["async_completed"] >= stats["async_accepted"]:
                    print("\n所有异步请求已处理完成，提前结束监控")
                    break
            
            last_report_time = current_time
        
        # 避免CPU过载
        time.sleep(0.1)
    
    # 获取最终统计
    final_stats = tracker.get_stats()
    monitor_duration = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("测试结果:")
    print(f"监控总时间: {monitor_duration:.2f}秒")
    print("-" * 40)
    print(f"异步API - 提交请求: {final_stats['async_submitted']}, 接受请求: {final_stats['async_accepted']}, 拒绝请求: {final_stats['async_rejected']}")
    print(f"异步API - 完成请求: {final_stats['async_completed']}, 待处理请求: {final_stats['async_pending']}")
    print(f"异步API - 请求接受率: {final_stats['async_accepted']/final_stats['async_submitted']*100:.2f}%")
    print(f"异步API - 请求完成率: {final_stats['async_completed']/final_stats['async_accepted']*100:.2f}% (相对于接受的请求)")
    
    if final_stats["async_response_times"]:
        avg_time = sum(final_stats["async_response_times"]) / len(final_stats["async_response_times"])
        print(f"异步API - 平均处理时间: {avg_time:.2f}ms")
    
    print("-" * 40)
    print(f"同步API - 提交请求: {final_stats['sync_submitted']}, 接受请求: {final_stats['sync_accepted']}, 拒绝请求: {final_stats['sync_rejected']}")
    print(f"同步API - 请求接受率: {final_stats['sync_accepted']/final_stats['sync_submitted']*100:.2f}%")
    
    if final_stats["sync_response_times"]:
        avg_time = sum(final_stats["sync_response_times"]) / len(final_stats["sync_response_times"])
        print(f"同步API - 平均处理时间: {avg_time:.2f}ms")
    
    print("=" * 80)
    
    # 创建结果目录
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_dir = "test_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # 保存时间序列数据
    time_series_df = pd.DataFrame(time_series_data)
    time_series_csv = os.path.join(results_dir, f"mq_advantage_series_{burst_size}_{timestamp}.csv")
    time_series_df.to_csv(time_series_csv, index=False)
    
    # 绘制请求处理曲线
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(time_series_data["timestamp"], time_series_data["async_accepted"], 'b-', label='异步API接受')
    plt.plot(time_series_data["timestamp"], time_series_data["async_completed"], 'g-', label='异步API完成')
    plt.plot(time_series_data["timestamp"], time_series_data["sync_accepted"], 'r-', label='同步API接受')
    plt.title(f'突发请求处理进度 (总请求: {burst_size})')
    plt.xlabel('时间 (秒)')
    plt.ylabel('请求数')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    plt.plot(time_series_data["timestamp"], time_series_data["async_pending"], 'm-', label='异步API待处理')
    plt.title('异步系统待处理请求数')
    plt.xlabel('时间 (秒)')
    plt.ylabel('请求数')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    chart_filename = os.path.join(results_dir, f"mq_advantage_chart_{burst_size}_{timestamp}.png")
    plt.savefig(chart_filename)
    print(f"处理曲线图表已保存至: {chart_filename}")
    
    # 绘制系统吞吐能力对比图
    plt.figure(figsize=(10, 6))
    
    # 准备数据
    labels = ['请求接受率', '请求完成率']
    async_values = [
        final_stats['async_accepted']/final_stats['async_submitted']*100, 
        final_stats['async_completed']/final_stats['async_accepted']*100 if final_stats['async_accepted'] > 0 else 0
    ]
    sync_values = [
        final_stats['sync_accepted']/final_stats['sync_submitted']*100,
        100.0  # 同步API接受即完成
    ]
    
    x = np.arange(len(labels))
    width = 0.35
    
    plt.bar(x - width/2, async_values, width, label='异步API', color='blue', alpha=0.7)
    plt.bar(x + width/2, sync_values, width, label='同步API', color='red', alpha=0.7)
    
    plt.title('系统吞吐能力对比')
    plt.ylabel('百分比 (%)')
    plt.xticks(x, labels)
    plt.ylim(0, 110)
    
    # 在柱状图上添加百分比标签
    for i, v in enumerate(async_values):
        plt.text(i - width/2, v + 3, f"{v:.1f}%", ha='center', va='bottom')
    
    for i, v in enumerate(sync_values):
        plt.text(i + width/2, v + 3, f"{v:.1f}%", ha='center', va='bottom')
    
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)
    
    comparison_chart = os.path.join(results_dir, f"mq_capability_comparison_{burst_size}_{timestamp}.png")
    plt.savefig(comparison_chart)
    print(f"系统吞吐能力对比图已保存至: {comparison_chart}")
    
    # 如果有足够的响应时间数据，绘制响应时间分布图
    if len(final_stats["async_response_times"]) > 5 or len(final_stats["sync_response_times"]) > 5:
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
        rt_chart_filename = os.path.join(results_dir, f"response_time_dist_{burst_size}_{timestamp}.png")
        plt.savefig(rt_chart_filename)
        print(f"响应时间分布图已保存至: {rt_chart_filename}")
    
    return {
        "burst_size": burst_size,
        "monitor_duration": monitor_duration,
        "async_submitted": final_stats["async_submitted"],
        "async_accepted": final_stats["async_accepted"],
        "async_rejected": final_stats["async_rejected"],
        "async_completed": final_stats["async_completed"],
        "async_pending": final_stats["async_pending"],
        "async_acceptance_rate": final_stats["async_accepted"]/final_stats["async_submitted"]*100,
        "async_completion_rate": final_stats["async_completed"]/final_stats["async_accepted"]*100 if final_stats["async_accepted"] > 0 else 0,
        "sync_submitted": final_stats["sync_submitted"],
        "sync_accepted": final_stats["sync_accepted"],
        "sync_rejected": final_stats["sync_rejected"],
        "sync_acceptance_rate": final_stats["sync_accepted"]/final_stats["sync_submitted"]*100
    }

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='消息队列优势量化测试工具')
    parser.add_argument('-b', '--burst', type=int, default=DEFAULT_BURST_SIZE,
                        help=f'突发请求数量 (默认: {DEFAULT_BURST_SIZE})')
    parser.add_argument('-d', '--duration', type=int, default=DEFAULT_MONITOR_DURATION,
                        help=f'监控持续时间(秒) (默认: {DEFAULT_MONITOR_DURATION})')
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
    
    if args.sync_url:
        SYNC_BASE_URL = args.sync_url
        SYNC_ENDPOINT = f"{SYNC_BASE_URL}/api/risk-assessment"
    
    # 运行测试
    burst_test(args.burst, args.duration, args.interval) 