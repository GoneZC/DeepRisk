#!/usr/bin/env python3
"""
MQ测试消息发布脚本
用于向RabbitMQ队列发送测试消息以验证消费者功能
"""

import random
import pika
import json
import uuid
import numpy as np
import sys
import os
import time  # 添加time模块导入

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import Config

def create_test_message(message_id=None, doctor_id=None):
    """
    创建测试消息
    
    Args:
        message_id: 消息ID
        doctor_id: 医生ID
    
    Returns:
        dict: 测试消息
    """
    if message_id is None:
        message_id = str(uuid.uuid4())
    
    if doctor_id is None:
        doctor_id = f"doctor_{int(time.time() * 1000) % 100000}"
    
    # 生成35个随机特征值，每次调用都生成全新的随机向量
    features = np.random.randn(35).tolist()
    
    # 构建消息
    message = {
        "requestId": message_id,
        "doctorId": doctor_id,
        "timestamp": time.time(),
        # 添加35个核心特征字段
        "feature_1": features[0],
        "feature_2": features[1],
        "feature_3": features[2],
        "feature_4": features[3],
        "feature_5": features[4],
        "feature_6": features[5],
        "feature_7": features[6],
        "feature_8": features[7],
        "feature_9": features[8],
        "feature_10": features[9],
        "feature_11": features[10],
        "feature_12": features[11],
        "feature_13": features[12],
        "feature_14": features[13],
        "feature_15": features[14],
        "feature_16": features[15],
        "feature_17": features[16],
        "feature_18": features[17],
        "feature_19": features[18],
        "feature_20": features[19],
        "feature_21": features[20],
        "feature_22": features[21],
        "feature_23": features[22],
        "feature_24": features[23],
        "feature_25": features[24],
        "feature_26": features[25],
        "feature_27": features[26],
        "feature_28": features[27],
        "feature_29": features[28],
        "feature_30": features[29],
        "feature_31": features[30],
        "feature_32": features[31],
        "feature_33": features[32],
        "feature_34": features[33],
        "feature_35": features[34],
        # 也可以直接包含vector字段
        "vector": features
    }
    
    return message

def publish_test_messages(num_messages=5):
    """
    发布测试消息到RabbitMQ
    
    Args:
        num_messages: 要发送的消息数量
    """
    try:
        # 建立RabbitMQ连接 (Windows直接连接到localhost)
        credentials = pika.PlainCredentials('guest', 'guest')
        
        parameters = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            virtual_host='/',
            credentials=credentials
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # 声明交换机和队列 (使用固定配置)
        exchange_name = 'risk.assessment.exchange'
        queue_name = 'risk.assessment.queue'
        routing_key = 'risk.assessment'
        
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type='direct',
            durable=True
        )
        
        channel.queue_declare(
            queue=queue_name,
            durable=True
        )
        
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        
        print(f"开始发送 {num_messages} 条测试消息...")
        
        # 发送测试消息
        for i in range(num_messages):
            # 为每个消息生成唯一的ID和医生ID
            message = create_test_message(
                message_id=f"test_msg_{int(time.time() * 1000000) % 10000000}_{i}_{uuid.uuid4().hex[:8]}",
                doctor_id=f"test_doctor_{random.randint(100000, 999999)}"
            )
            
            channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=json.dumps(message, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 消息持久化
                )
            )
            
            print(f"已发送消息 {i+1}/{num_messages}: {message['requestId']}")
            time.sleep(0.01)  # 短暂延迟避免发送过快，确保时间戳不同
        
        # 关闭连接
        connection.close()
        print(f"测试消息发送完成，共发送 {num_messages} 条消息")
        
    except Exception as e:
        print(f"发送测试消息时出错: {e}")
        import traceback
        traceback.print_exc()

def publish_single_message_with_custom_features():
    """
    发送一条具有特定特征值的测试消息，用于验证欺诈检测逻辑
    """
    try:
        # 建立RabbitMQ连接 (Windows直接连接到localhost)
        credentials = pika.PlainCredentials('guest', 'guest')
        
        parameters = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            virtual_host='/',
            credentials=credentials
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # 声明交换机和队列 (使用固定配置)
        exchange_name = 'risk.assessment.exchange'
        queue_name = 'risk.assessment.queue'
        routing_key = 'risk.assessment'
        
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type='direct',
            durable=True
        )
        
        channel.queue_declare(
            queue=queue_name,
            durable=True
        )
        
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        
        # 生成随机特征值
        timestamp = int(time.time() * 1000000)
        seed = timestamp + random.randint(1, 1000000)
        random.seed(seed)
        features = [random.uniform(-3, 3) for _ in range(35)]
        
        # 创建具有随机特征的测试消息
        message = {
            "requestId": f"custom_test_msg_{timestamp}",
            "doctorId": f"custom_doctor_{random.randint(10000, 99999)}",
            "timestamp": time.time(),
            # 使用随机生成的特征值
            **{f"feature_{i+1}": features[i] for i in range(35)}
        }
        
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=json.dumps(message, ensure_ascii=False),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 消息持久化
            )
        )
        
        print(f"已发送自定义特征测试消息: {message['requestId']}")
        
        # 关闭连接
        connection.close()
        
    except Exception as e:
        print(f"发送自定义特征测试消息时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("MQ测试消息发布脚本")
    print("1. 发送随机特征测试消息")
    print("2. 发送自定义特征测试消息")
    
    choice = input("请选择操作 (1 或 2): ").strip()
    
    if choice == "1":
        num = input("请输入要发送的消息数量 (默认5条): ").strip()
        try:
            num_messages = int(num) if num else 5
        except ValueError:
            num_messages = 5
            print("输入无效，使用默认值5条消息")
        
        publish_test_messages(num_messages)
        
    elif choice == "2":
        publish_single_message_with_custom_features()
        
    else:
        print("无效选择，发送默认5条随机特征测试消息")
        publish_test_messages(5)