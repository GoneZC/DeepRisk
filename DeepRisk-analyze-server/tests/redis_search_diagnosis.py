#!/usr/bin/env python3
"""
Redis向量搜索诊断脚本
用于诊断FT.SEARCH失败的具体原因
"""

import sys
import os
import time
import numpy as np
import redis
import logging

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_redis_connection():
    """测试Redis基本连接"""
    print("=== Redis连接测试 ===")
    try:
        redis_client = redis.Redis(
            host=os.environ.get('REDIS_HOST', 'localhost'),
            port=int(os.environ.get('REDIS_PORT', 6380)),  # 使用映射的端口6380
            db=0,
            decode_responses=False
        )
        
        # 测试ping
        result = redis_client.ping()
        print(f"Redis PING: {result}")
        
        # 测试模块
        modules = redis_client.execute_command('MODULE', 'LIST')
        print(f"已加载模块: {modules}")
        
        return redis_client
    except Exception as e:
        print(f"Redis连接失败: {e}")
        return None

def test_index_info(redis_client):
    """测试索引信息"""
    print("\n=== 索引信息测试 ===")
    try:
        info = redis_client.execute_command('FT.INFO', 'doctor_vectors')
        print("索引信息:")
        for i in range(0, len(info), 2):
            key = info[i].decode('utf-8') if isinstance(info[i], bytes) else info[i]
            value = info[i+1]
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8')
                except:
                    pass
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"获取索引信息失败: {e}")

def test_simple_search(redis_client):
    """测试简单搜索"""
    print("\n=== 简单搜索测试 ===")
    try:
        # 测试基本搜索
        result = redis_client.execute_command(
            'FT.SEARCH', 'doctor_vectors', '*', 'LIMIT', '0', '1'
        )
        print(f"基本搜索结果: {result}")
        
        if len(result) > 1:
            print("找到数据，索引正常工作")
            return True
        else:
            print("未找到数据")
            return False
    except Exception as e:
        print(f"简单搜索失败: {e}")
        return False

def test_vector_search(redis_client):
    """测试向量搜索"""
    print("\n=== 向量搜索测试 ===")
    try:
        # 生成测试向量
        test_vector = np.random.randn(128).astype(np.float32)
        print(f"测试向量形状: {test_vector.shape}")
        print(f"测试向量类型: {test_vector.dtype}")
        
        # 执行向量搜索
        start_time = time.time()
        result = redis_client.execute_command(
            'FT.SEARCH', 'doctor_vectors',
            '*=>[KNN 5 @vector $vec AS similarity_score]',
            'PARAMS', '2', 'vec', test_vector.tobytes(),
            'SORTBY', 'similarity_score', 'ASC',
            'DIALECT', '2',
            'LIMIT', '0', '5'
        )
        search_time = time.time() - start_time
        
        print(f"向量搜索耗时: {search_time:.4f}秒")
        print(f"搜索结果数量: {result[0] if result else 0}")
        
        if result and result[0] > 0:
            print("向量搜索成功")
            # 解析第一个结果
            if len(result) > 2:
                fields = result[2]
                print(f"第一个结果字段: {fields}")
            return True
        else:
            print("向量搜索无结果")
            return False
            
    except Exception as e:
        print(f"向量搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_searches(redis_client, count=10):
    """测试多次搜索性能"""
    print(f"\n=== 多次搜索性能测试 ({count}次) ===")
    
    times = []
    success_count = 0
    
    for i in range(count):
        try:
            test_vector = np.random.randn(128).astype(np.float32)
            
            start_time = time.time()
            result = redis_client.execute_command(
                'FT.SEARCH', 'doctor_vectors',
                '*=>[KNN 10 @vector $vec AS similarity_score]',
                'PARAMS', '2', 'vec', test_vector.tobytes(),
                'SORTBY', 'similarity_score', 'ASC',
                'DIALECT', '2',
                'LIMIT', '0', '10'
            )
            search_time = time.time() - start_time
            times.append(search_time)
            
            if result and result[0] > 0:
                success_count += 1
                
        except Exception as e:
            print(f"第{i+1}次搜索失败: {e}")
    
    if times:
        avg_time = np.mean(times)
        min_time = np.min(times)
        max_time = np.max(times)
        
        print(f"成功次数: {success_count}/{count}")
        print(f"平均耗时: {avg_time:.4f}秒")
        print(f"最小耗时: {min_time:.4f}秒")
        print(f"最大耗时: {max_time:.4f}秒")
        print(f"理论TPS: {1/avg_time:.2f}")
    else:
        print("所有搜索都失败了")

def main():
    print("Redis向量搜索诊断开始...")
    
    # 测试Redis连接
    redis_client = test_redis_connection()
    if not redis_client:
        return
    
    # 测试索引信息
    test_index_info(redis_client)
    
    # 测试简单搜索
    if not test_simple_search(redis_client):
        print("简单搜索失败，停止后续测试")
        return
    
    # 测试向量搜索
    if not test_vector_search(redis_client):
        print("向量搜索失败，停止后续测试")
        return
    
    # 测试多次搜索性能
    test_multiple_searches(redis_client, 50)
    
    print("\n诊断完成")

if __name__ == "__main__":
    main()