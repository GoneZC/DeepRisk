#!/usr/bin/env python3
"""
检查Redis中医生的标签分布情况
"""

import redis
import sys
import os

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
        
        # 获取医生总数
        try:
            total_result = redis_client.execute_command('FT.SEARCH', 'doctor_vectors', '*', 'LIMIT', '0', '0')
            total_doctors = total_result[0] if total_result else 0
            print(f"Redis中医生总数: {total_doctors}")
        except Exception as e:
            print(f"无法获取医生总数: {e}")
            return
        
        if total_doctors == 0:
            print("Redis中没有医生数据")
            return
            
        # 分批获取医生标签信息
        batch_size = 1000
        label_stats = {}
        processed = 0
        
        for offset in range(0, min(total_doctors, 10000), batch_size):  # 最多检查10000个医生
            try:
                result = redis_client.execute_command(
                    'FT.SEARCH', 'doctor_vectors',
                    '*',
                    'LIMIT', str(offset), str(batch_size),
                    'RETURN', '1', 'label'
                )
                
                # 解析结果
                for i in range(1, len(result), 2):
                    fields = result[i+1]
                    label = None
                    
                    # 查找label字段
                    for j in range(0, len(fields), 2):
                        if fields[j] == 'label':
                            label = fields[j+1]
                            break
                    
                    # 统计标签
                    label_stats[label] = label_stats.get(label, 0) + 1
                    processed += 1
                    
            except Exception as e:
                print(f"处理批次 {offset} 时出错: {e}")
                break
        
        print(f"\n检查了 {processed} 个医生的标签分布:")
        for label, count in sorted(label_stats.items()):
            percentage = (count / processed) * 100 if processed > 0 else 0
            print(f"  标签 '{label}': {count} 个 ({percentage:.2f}%)")
            
        # 检查是否存在预期的标签分布
        fraud_count = label_stats.get('1', 0)
        normal_count = label_stats.get('0', 0)
        total_with_label = fraud_count + normal_count
        
        if total_with_label > 0:
            fraud_percentage = (fraud_count / total_with_label) * 100
            print(f"\n欺诈医生比例: {fraud_percentage:.2f}% ({fraud_count}/{total_with_label})")
            
            if fraud_percentage > 50:  # 如果欺诈医生比例超过50%，说明数据可能有问题
                print("警告: 欺诈医生比例过高，可能数据有问题")
            elif fraud_percentage < 0.1:  # 如果欺诈医生比例过低，也可能是问题
                print("注意: 欺诈医生比例较低")
            else:
                print("欺诈医生比例看起来正常")
        
    except Exception as e:
        print(f"检查标签分布时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_label_distribution()