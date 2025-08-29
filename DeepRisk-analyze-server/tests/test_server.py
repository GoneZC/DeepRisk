#!/usr/bin/env python3
"""
简单的测试脚本，用于验证FastAPI服务是否正常工作
"""

import requests
import time

def test_health_check():
    """测试健康检查端点"""
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✓ 健康检查通过")
            print(f"  响应: {response.json()}")
            return True
        else:
            print("✗ 健康检查失败")
            print(f"  状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务已启动")
        return False
    except Exception as e:
        print(f"✗ 健康检查出错: {e}")
        return False

def test_main_endpoint():
    """测试主端点"""
    try:
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            print("✓ 主页访问正常")
            print(f"  响应: {response.json()}")
            return True
        else:
            print("✗ 主页访问失败")
            print(f"  状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务已启动")
        return False
    except Exception as e:
        print(f"✗ 主页访问出错: {e}")
        return False

def test_consumer_status():
    """测试消费者状态端点"""
    try:
        response = requests.get("http://localhost:5000/consumer/status")
        if response.status_code == 200:
            print("✓ 消费者状态端点访问正常")
            print(f"  响应: {response.json()}")
            return True
        else:
            print("✗ 消费者状态端点访问失败")
            print(f"  状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务已启动")
        return False
    except Exception as e:
        print(f"✗ 消费者状态端点访问出错: {e}")
        return False

def main():
    print("开始测试SmartRisk Analyze Server (FastAPI版本)")
    print("=" * 50)
    
    # 等待服务启动
    print("正在等待服务启动...")
    time.sleep(2)
    
    tests = [
        test_health_check,
        test_main_endpoint,
        test_consumer_status
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过，服务运行正常！")
    else:
        print("⚠️  部分测试失败，请检查服务状态")

if __name__ == "__main__":
    main()