#!/usr/bin/env python3
"""
测试Redis连接和数据获取
"""

import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 强制加载模型
from app.models.model_loader import load_models
load_models()

from app.models.fraud_detection import FraudDetectionCore
import numpy as np

def test_redis_connection():
    """
    测试Redis连接和数据获取
    """
    try:
        print("创建欺诈检测核心实例...")
        fraud_detector = FraudDetectionCore()
        print("成功创建欺诈检测核心实例")
        
        # 检查Redis客户端是否初始化
        if fraud_detector.redis_client is None:
            print("Redis客户端未初始化")
            return
        
        print("Redis客户端已初始化")
        
        # 检查数据库大小
        try:
            dbsize = fraud_detector.redis_client.execute_command('DBSIZE')
            print(f"Redis数据库大小: {dbsize}")
        except Exception as e:
            print(f"无法获取数据库大小: {e}")
        
        # 检查索引
        try:
            indexes = fraud_detector.redis_client.execute_command('FT.LIST')
            print(f"Redis索引列表: {indexes}")
        except Exception as e:
            print(f"无法获取索引列表: {e}")
        
        # 生成一个测试向量并查找相似医生
        print("\n生成测试向量...")
        test_vector = np.random.randn(35).astype(np.float32)
        print(f"测试向量: {test_vector[:5]}...")
        
        print("\n编码向量...")
        encoded_vector = fraud_detector._encode_vector(test_vector)
        if encoded_vector is not None:
            print(f"编码后向量形状: {encoded_vector.shape}")
            
            print("\n查找相似医生...")
            similar_doctors = fraud_detector._find_similar_doctors(encoded_vector, k=10)
            print(f"找到 {len(similar_doctors)} 个相似医生")
            
            # 显示相似医生信息
            if similar_doctors:
                print("\n相似医生详情:")
                for i, doctor in enumerate(similar_doctors[:5]):  # 显示前5个
                    print(f"  {i+1}. ID: {doctor.get('doctor_id')}, "
                          f"相似度: {doctor.get('similarity_score'):.4f}, "
                          f"标签: {doctor.get('label')}")
                
                # 统计标签分布
                labels = [doc.get('label') for doc in similar_doctors]
                label_counts = {}
                for label in labels:
                    label_counts[label] = label_counts.get(label, 0) + 1
                
                print(f"\n标签分布: {label_counts}")
                
                # 计算欺诈得分
                fraud_score = fraud_detector._calculate_fraud_score(similar_doctors)
                print(f"\n欺诈得分: {fraud_score:.2f}")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_redis_connection()