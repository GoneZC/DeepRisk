#!/usr/bin/env python3
"""
测试模型对不同输入的响应
"""

import numpy as np
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 强制加载模型
from app.models.model_loader import load_models
load_models()

from app.models.fraud_detection import FraudDetectionCore

def test_model_responses():
    """
    测试模型对不同输入的响应
    """
    print("创建欺诈检测核心实例...")
    fraud_detector = FraudDetectionCore()
    
    # 生成3个明显不同的向量
    vectors = [
        np.array([1.0] * 35, dtype=np.float32),  # 全1向量
        np.array([-1.0] * 35, dtype=np.float32), # 全-1向量
        np.array([0.0] * 35, dtype=np.float32),  # 全0向量
    ]
    
    print("\n测试模型对不同输入的响应:")
    results = []
    
    for i, vector in enumerate(vectors):
        print(f"\n测试向量 {i+1}:")
        print(f"  向量特征: [{vector[0]}, {vector[1]}, ... {vector[-1]}]")
        
        result = fraud_detector.process_vector(vector, f"doctor_{i+1}")
        
        # 打印详细信息
        print(f"  相似医生数量: {len(result.get('similar_doctors', []))}")
        
        # 显示相似医生详情
        similar_doctors = result.get('similar_doctors', [])
        if similar_doctors:
            labels = [doc['label'] for doc in similar_doctors]
            label_counts = {}
            for label in labels:
                label_counts[label] = label_counts.get(label, 0) + 1
            
            print(f"  医生标签分布: {label_counts}")
            
            # 显示前几个医生
            print("  前3个相似医生:")
            for j, doc in enumerate(similar_doctors[:3]):
                print(f"    {j+1}. ID: {doc['doctor_id']}, 相似度: {doc['similarity_score']:.4f}, 标签: {doc['label']}")
        
        fraud_score = result.get('fraud_score', 0.0)
        fraud_level = result.get('fraud_level', '未知')
        similar_count = len(result.get('similar_doctors', []))
        
        print(f"  欺诈得分: {fraud_score:.2f}")
        print(f"  风险等级: {fraud_level}")
        print(f"  相似医生数量: {similar_count}")
        
        results.append(result)
    
    # 分析结果
    print("\n=== 结果分析 ===")
    scores = [r.get('fraud_score', 0.0) for r in results]
    levels = [r.get('fraud_level', '未知') for r in results]
    similarities = []
    
    for r in results:
        similar_docs = r.get('similar_doctors', [])
        if similar_docs:
            avg_sim = np.mean([doc.get('similarity_score', 0) for doc in similar_docs])
            similarities.append(avg_sim)
        else:
            similarities.append(0)
    
    print(f"欺诈得分: {scores}")
    print(f"风险等级: {levels}")
    print(f"平均相似度: {[f'{s:.4f}' for s in similarities]}")
    
    unique_scores = len(set(scores))
    if unique_scores > 1:
        print("✓ 模型对不同输入产生了不同的欺诈得分")
    else:
        print("✗ 模型对所有输入产生了相同的欺诈得分")

if __name__ == "__main__":
    test_model_responses()