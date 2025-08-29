#!/usr/bin/env python3
"""
使用SCAN命令检查医生标签分布
"""

import redis

def scan_doctor_labels():
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
        
        # 使用SCAN命令遍历医生键
        label_stats = {}
        total_checked = 0
        cursor = 0
        
        print("开始扫描医生数据...")
        
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match="doctor:*", count=100)
            
            # 检查这些键的标签
            for key in keys:
                try:
                    label = redis_client.hget(key, 'label')
                    if label is not None:
                        label_stats[label] = label_stats.get(label, 0) + 1
                        total_checked += 1
                        
                        # 每检查1000个医生显示一次进度
                        if total_checked % 1000 == 0:
                            print(f"已检查 {total_checked} 个医生...")
                            
                        # 限制检查数量以避免运行时间过长
                        if total_checked >= 10000:
                            break
                except Exception as e:
                    continue
                    
            if cursor == 0 or total_checked >= 10000:
                break
        
        print(f"\n总共检查了 {total_checked} 个医生:")
        for label, count in sorted(label_stats.items()):
            percentage = (count / total_checked) * 100 if total_checked > 0 else 0
            print(f"  标签 '{label}': {count} 个 ({percentage:.2f}%)")
            
    except Exception as e:
        print(f"扫描医生标签时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    scan_doctor_labels()