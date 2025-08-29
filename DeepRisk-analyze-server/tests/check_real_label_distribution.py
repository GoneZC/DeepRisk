#!/usr/bin/env python3
"""
检查Redis中医生标签的真实分布
"""

import redis
import random

def check_label_distribution():
    try:
        # 连接到Redis
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            password=None,
            decode_responses=True
        )
        
        # 检查连接
        redis_client.ping()
        print("成功连接到Redis")
        
        # 随机抽样检查1000个医生的标签
        sampled_doctors = []
        fraud_count = 0
        normal_count = 0
        total_sampled = 0
        
        print("开始随机抽样检查医生标签...")
        
        # 通过随机扫描方式获取样本
        for i in range(1000):
            try:
                # 随机生成医生ID（根据之前的模式）
                random_id = random.randint(1, 1000000)
                key = f"doctor:doctor_{random_id}"
                
                # 获取标签
                label = redis_client.hget(key, 'label')
                if label is not None:
                    sampled_doctors.append((key, label))
                    total_sampled += 1
                    
                    if label == '1':
                        fraud_count += 1
                    elif label == '0':
                        normal_count += 1
                        
            except Exception as e:
                continue  # 忽略单个错误
        
        print(f"\n抽样检查了 {total_sampled} 个医生:")
        print(f"  欺诈医生 (标签=1): {fraud_count} 个")
        print(f"  正常医生 (标签=0): {normal_count} 个")
        
        if total_sampled > 0:
            fraud_percentage = (fraud_count / total_sampled) * 100
            print(f"  欺诈医生比例: {fraud_percentage:.2f}%")
        
        # 检查几个具体的医生
        print("\n检查一些具体医生的标签:")
        test_ids = [1, 100, 1000, 10000, 100000, 500000, 900000]
        for test_id in test_ids:
            key = f"doctor:doctor_{test_id}"
            label = redis_client.hget(key, 'label')
            print(f"  医生 {test_id}: 标签={label}")
            
    except Exception as e:
        print(f"检查标签分布时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_label_distribution()