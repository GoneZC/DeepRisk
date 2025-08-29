#!/usr/bin/env python3
"""
欺诈检测模块测试脚本
"""

import sys
import os
import numpy as np
import time

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_fraud_detection():
    """测试欺诈检测核心模块"""
    print("=== 欺诈检测模块测试 ===")
    
    try:
        # 导入欺诈检测模块
        from app.models.fraud_detection import FraudDetectionCore
        
        # 创建欺诈检测实例，使用6380端口（根据您的docker配置）
        print("1. 创建欺诈检测实例...")
        fraud_detector = FraudDetectionCore(redis_port=6380)
        
        # 生成测试数据
        print("2. 生成测试35维向量...")
        np.random.seed(42)  # 固定种子以便结果可重现
        test_vector = np.random.randn(35).astype(np.float32)
        print(f"   测试向量: {test_vector[:5]}...")  # 只显示前5个元素
        
        # 测试向量处理
        print("3. 处理向量...")
        result = fraud_detector.process_vector(test_vector, "test_doctor_001")
        
        # 显示结果
        print("4. 处理结果:")
        if "error" in result:
            print(f"   错误: {result['error']}")
        else:
            print(f"   医生ID: {result.get('doctor_id')}")
            print(f"   欺诈得分: {result.get('fraud_score', 0):.2f}")
            print(f"   风险等级: {result.get('fraud_level', '未知')}")
            print(f"   128维向量: {result.get('vector_128d', [])[:5]}...")  # 只显示前5个元素
            
            similar_doctors = result.get('similar_doctors', [])
            print(f"   相似医生数量: {len(similar_doctors)}")
            if similar_doctors:
                print("   前3个相似医生:")
                for i, doctor in enumerate(similar_doctors[:3]):
                    print(f"     {i+1}. ID: {doctor.get('doctor_id')}, 相似度: {doctor.get('similarity_score', 0):.4f}")
            else:
                print("   没有找到相似医生")
        
        print("\n=== 测试完成 ===")
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 边界情况测试 ===")
    
    try:
        from app.models.fraud_detection import FraudDetectionCore
        
        fraud_detector = FraudDetectionCore(redis_port=6380)
        
        # 测试错误维度的向量
        print("1. 测试错误维度向量...")
        try:
            wrong_vector = np.random.randn(30)  # 错误维度
            result = fraud_detector.process_vector(wrong_vector, "test_doctor_002")
            print(f"   结果: {result.get('error', '无错误信息')}")
        except Exception as e:
            print(f"   捕获异常: {e}")
        
        # 测试空向量
        print("2. 测试空向量...")
        try:
            empty_vector = []
            result = fraud_detector.process_vector(empty_vector, "test_doctor_003")
            print(f"   结果: {result.get('error', '无错误信息')}")
        except Exception as e:
            print(f"   捕获异常: {e}")
            
        print("\n=== 边界情况测试完成 ===")
        return True
        
    except Exception as e:
        print(f"边界测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_loading():
    """测试模型加载"""
    print("\n=== 模型加载测试 ===")
    
    try:
        from app.models.model_loader import load_models, get_encoder
        print("1. 加载模型...")
        load_models()
        
        print("2. 获取编码器...")
        encoder, scaler = get_encoder()
        if encoder is not None and scaler is not None:
            print("   编码器加载成功")
        else:
            print("   编码器加载失败")
            
        return True
    except Exception as e:
        print(f"模型加载测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_scenarios():
    """测试不同场景下的欺诈检测"""
    print("\n=== 不同场景测试 ===")
    
    try:
        from app.models.fraud_detection import FraudDetectionCore
        
        # 创建欺诈检测实例，使用6380端口
        print("1. 创建欺诈检测实例(使用6380端口)...")
        fraud_detector = FraudDetectionCore(redis_port=6380)
        
        # 测试多个不同的向量
        print("2. 测试多个不同向量...")
        np.random.seed(123)
        
        for i in range(3):
            print(f"   测试向量 {i+1}:")
            test_vector = np.random.randn(35).astype(np.float32)
            result = fraud_detector.process_vector(test_vector, f"test_doctor_{i+1:03d}")
            
            if "error" not in result:
                print(f"     欺诈得分: {result.get('fraud_score', 0):.2f}")
                print(f"     风险等级: {result.get('fraud_level', '未知')}")
                print(f"     相似医生数量: {len(result.get('similar_doctors', []))}")
            else:
                print(f"     错误: {result['error']}")
        
        print("\n=== 不同场景测试完成 ===")
        return True
        
    except Exception as e:
        print(f"不同场景测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试欺诈检测模块...")
    
    # 测试模型加载
    success0 = test_model_loading()
    
    # 测试主功能
    success1 = test_fraud_detection()
    
    # 测试边界情况
    success2 = test_edge_cases()
    
    # 测试不同场景
    success3 = test_different_scenarios()
    
    if success0 and success1 and success2 and success3:
        print("\n✓ 所有测试完成")
        sys.exit(0)
    else:
        print("\n✗ 部分测试失败")
        sys.exit(1)