#!/usr/bin/env python3
"""
测试向量搜索结果，检查返回的医生标签分布
"""

import sys
import os
import numpy as np

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 强制加载模型
from app.models.model_loader import load_models
load_models()

from app.models.fraud_detection import FraudDetectionCore

def test_vector_search():
    """
    测试向量搜索结果
    """
    print("创建欺诈检测核心实例...")
    fraud_detector = FraudDetectionCore()
    
    # 生成多个不同的测试向量
    test_vectors = []
    for i in range(5):
        vector = np.random.randn(35).astype(np.float32)
        test_vectors.append(vector)
    
    print("\n测试向量搜索结果:")
    
    for i, vector in enumerate(test_vectors):
        print(f"\n测试向量 {i+1}:")
        print(f"  向量前5个元素: {vector[:5]}")
        
        # 编码向量
        encoded_vector = fraud_detector._encode_vector(vector)
        if encoded_vector is not None:
            print(f"  编码后向量形状: {encoded_vector.shape}")
            
            # 查找相似医生（获取更多结果以便分析）
            similar_doctors = fraud_detector._find_similar_doctors(encoded_vector, k=50)
            print(f"  找到相似医生数量: {len(similar_doctors)}")
            
            if similar_doctors:
                # 统计标签分布
                labels = [doc['label'] for doc in similar_doctors]
                label_counts = {}
                for label in labels:
                    label_counts[label] = label_counts.get(label, 0) + 1
                
                print(f"  医生标签分布: {label_counts}")
                
                # 显示前10个医生的详细信息
                print("  前10个相似医生:")
                for j, doctor in enumerate(similar_doctors[:10]):
                    print(f"    {j+1}. ID: {doctor['doctor_id']}, 相似度: {doctor['similarity_score']:.4f}, 标签: {doctor['label']}")
            else:
                print("  未找到相似医生")
        else:
            print("  向量编码失败")

if __name__ == "__main__":
    test_vector_search()