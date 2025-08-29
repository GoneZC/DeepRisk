import pika
import json
import threading
import logging
import requests
import torch
import numpy as np
import redis
import time
import pymysql
from typing import List, Dict
from collections import deque
from app.config import Config
from app.models.model_loader import get_encoder

# 添加FraudDetectionCore的导入
try:
    from app.models.fraud_detection import FraudDetectionCore
    FRAUD_DETECTION_AVAILABLE = True
    print("[初始化] 成功导入 FraudDetectionCore")
except ImportError as e:
    FraudDetectionCore = None
    FRAUD_DETECTION_AVAILABLE = False
    print(f"[初始化] 无法导入 FraudDetectionCore: {e}")

logger = logging.getLogger(__name__)

class OptimizedRiskAssessmentConsumer:
    def __init__(self, app=None):
        self.app = app
        self._connection_params = None
        self._consumer_thread = None
        self._stop_event = threading.Event()
        self._setup_complete = False
        self._redis_client = None
        self._fraud_detector = None
        self.last_error = None
        
        # 批处理相关配置
        self.batch_queue = deque()  # 存储待处理的消息
        self.batch_size = 32  # 批处理大小
        self.batch_timeout = 0.1  # 批处理超时时间（秒）
        self.last_batch_time = time.time()  # 上次批处理时间

    def init_app(self, app):
        """初始化配置"""
        self.app = app
        try:
            # 使用Config类而不是app.config
            self._connection_params = pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                virtual_host=Config.RABBITMQ_VHOST,
                credentials=pika.PlainCredentials(
                    Config.RABBITMQ_USERNAME,
                    Config.RABBITMQ_PASSWORD
                ),
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            # 初始化Redis客户端
            self._redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                password=Config.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # 测试Redis连接
            self._redis_client.ping()
            print("[Redis] Redis连接成功")
            logger.info("Redis连接成功")
            
            # 初始化欺诈检测核心模块
            if FRAUD_DETECTION_AVAILABLE:
                try:
                    self._fraud_detector = FraudDetectionCore()
                    print("[欺诈检测] 欺诈检测核心模块初始化成功")
                    logger.info("欺诈检测核心模块初始化成功")
                except Exception as e:
                    print(f"[欺诈检测] 欺诈检测核心模块初始化失败: {e}")
                    logger.error(f"欺诈检测核心模块初始化失败: {e}")
            else:
                print("[欺诈检测] 欺诈检测核心模块不可用")
                logger.warning("欺诈检测核心模块不可用")
            
            self._setup_complete = True
            logger.info("RiskAssessmentConsumer初始化完成")
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"RiskAssessmentConsumer初始化失败: {e}")
            print(f"[初始化] RiskAssessmentConsumer初始化失败: {e}")

    def start_consuming(self):
        """启动消费者"""
        if not self._setup_complete:
            logger.error("消费者未正确初始化")
            return
            
        self._consumer_thread = threading.Thread(target=self._consume_messages, daemon=True)
        self._consumer_thread.start()
        logger.info("消费者线程已启动")
        print("[消费者] 消费者线程已启动")

    def stop_consuming(self):
        """停止消费者"""
        self._stop_event.set()
        if self._consumer_thread and self._consumer_thread.is_alive():
            self._consumer_thread.join(timeout=5)
        logger.info("消费者已停止")
        print("[消费者] 消费者已停止")

    def _consume_messages(self):
        """消费消息的主循环"""
        while not self._stop_event.is_set():
            try:
                connection = pika.BlockingConnection(self._connection_params)
                channel = connection.channel()
                
                # 声明队列
                channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True)
                channel.basic_qos(prefetch_count=100)  # 增加预取数量以支持批处理
                
                # 设置回调函数
                channel.basic_consume(
                    queue=Config.RABBITMQ_QUEUE,
                    on_message_callback=self._batch_message_handler,
                    auto_ack=False
                )
                
                print(f"[消费者] 等待消息，队列: {Config.RABBITMQ_QUEUE}")
                logger.info(f"等待消息，队列: {Config.RABBITMQ_QUEUE}")
                
                # 启动消费
                channel.start_consuming()
                
            except Exception as e:
                if not self._stop_event.is_set():
                    logger.error(f"消费者连接错误: {e}")
                    print(f"[消费者] 连接错误: {e}")
                    time.sleep(5)  # 等待5秒后重试
                else:
                    break

    def _batch_message_handler(self, channel, method, properties, body):
        """批处理消息处理器"""
        try:
            # 将消息添加到批处理队列
            message_info = {
                'channel': channel,
                'method': method,
                'properties': properties,
                'body': body,
                'receive_time': time.time()
            }
            self.batch_queue.append(message_info)
            
            # 检查是否应该处理批处理
            current_time = time.time()
            if (len(self.batch_queue) >= self.batch_size or 
                current_time - self.last_batch_time >= self.batch_timeout):
                self._process_batch()
                self.last_batch_time = current_time
                
        except Exception as e:
            logger.error(f"批处理消息处理错误: {e}")
            print(f"[批处理] 消息处理错误: {e}")
            channel.basic_nack(method.delivery_tag, requeue=False)

    def _process_batch(self):
        """处理批处理消息"""
        if not self.batch_queue:
            return
            
        batch_messages = []
        # 取出批处理大小的消息
        batch_count = min(len(self.batch_queue), self.batch_size)
        for _ in range(batch_count):
            batch_messages.append(self.batch_queue.popleft())
            
        print(f"[批处理] 开始处理批处理，包含 {len(batch_messages)} 条消息")
        logger.info(f"开始处理批处理，包含 {len(batch_messages)} 条消息")
        
        try:
            # 提取所有向量进行批处理编码
            vectors_35d = []
            message_details = []
            
            for msg_info in batch_messages:
                try:
                    message_str = msg_info['body'].decode('utf-8')
                    message = json.loads(message_str)
                    if isinstance(message, str):
                        message = json.loads(message)
                        
                    request_id = message.get('requestId', f"msg-{message_str[:10]}")
                    doctor_id = message.get('doctorId')
                    vector_data = message.get('vector')
                    
                    if vector_data and len(vector_data) == 35:
                        vector_35d = np.array(vector_data, dtype=np.float32)
                        vectors_35d.append(vector_35d)
                        message_details.append({
                            'request_id': request_id,
                            'doctor_id': doctor_id,
                            'channel': msg_info['channel'],
                            'method': msg_info['method'],
                            'original_message': message
                        })
                    else:
                        # 向量无效，直接处理并确认
                        self._handle_invalid_vector(msg_info['channel'], msg_info['method'], request_id, doctor_id)
                        
                except Exception as e:
                    logger.error(f"解析消息失败: {e}")
                    msg_info['channel'].basic_nack(msg_info['method'].delivery_tag, requeue=False)
            
            if vectors_35d:
                # 批量处理向量
                results = self._batch_process_vectors(vectors_35d, message_details)
                
                # 发送结果并确认消息
                for i, (result, msg_detail) in enumerate(zip(results, message_details)):
                    try:
                        callback_success = self._send_result(result)
                        if callback_success:
                            msg_detail['channel'].basic_ack(msg_detail['method'].delivery_tag)
                            logger.info(f"消息处理成功并回调成功: {msg_detail['request_id']}")
                        else:
                            msg_detail['channel'].basic_nack(msg_detail['method'].delivery_tag, requeue=True)
                            logger.warning(f"消息回调失败，重新入队: {msg_detail['request_id']}")
                    except Exception as e:
                        logger.error(f"处理单个消息结果时出错: {e}")
                        msg_detail['channel'].basic_nack(msg_detail['method'].delivery_tag, requeue=False)
                        
        except Exception as e:
            logger.error(f"批处理执行失败: {e}")
            print(f"[批处理] 批处理执行失败: {e}")
            # 所有消息重新入队
            for msg_info in batch_messages:
                msg_info['channel'].basic_nack(msg_info['method'].delivery_tag, requeue=True)

    def _batch_process_vectors(self, vectors_35d, message_details):
        """批量处理向量"""
        results = []
        
        try:
            if self._fraud_detector is not None:
                # 使用欺诈检测核心模块进行批处理风险评估
                print(f"[批处理] 使用欺诈检测核心模块进行批处理风险评估，处理 {len(vectors_35d)} 个向量")
                logger.info(f"使用欺诈检测核心模块进行批处理风险评估，处理 {len(vectors_35d)} 个向量")
                
                # 对每个向量单独处理（因为当前欺诈检测模块不支持批处理）
                for i, vector_35d in enumerate(vectors_35d):
                    msg_detail = message_details[i]
                    try:
                        fraud_result = self._fraud_detector.process_vector(vector_35d, msg_detail['doctor_id'])
                        
                        result = {
                            "requestId": msg_detail['request_id'],
                            "status": "SUCCESS",
                            "doctorId": msg_detail['doctor_id'],
                            "vector_35d": fraud_result.get("vector_35d", vector_35d.tolist()),
                            "vector_128d": fraud_result.get("vector_128d", []),
                            "fraudScore": fraud_result.get("fraud_score", 0.0),
                            "fraudLevel": fraud_result.get("fraud_level", "未知"),
                            "similarDoctors": fraud_result.get("similar_doctors", []),
                            "processed": True
                        }
                        results.append(result)
                    except Exception as e:
                        logger.error(f"处理向量时出错: {e}")
                        result = {
                            "requestId": msg_detail['request_id'],
                            "status": "ERROR",
                            "doctorId": msg_detail['doctor_id'],
                            "message": str(e),
                            "processed": True
                        }
                        results.append(result)
            else:
                # 备用处理方式
                print("[批处理] 欺诈检测模块不可用，使用备用处理方式")
                logger.warning("欺诈检测模块不可用，使用备用处理方式")
                
                # 批量编码向量
                vectors_128d = self._batch_encode_vectors(vectors_35d)
                
                for i, vector_128d in enumerate(vectors_128d):
                    msg_detail = message_details[i]
                    if vector_128d is not None:
                        # 查找相似医生
                        similar_doctors = self._fraud_detector._find_similar_doctors(vector_128d, k=10) if self._fraud_detector else []
                        fraud_score = self._fraud_detector._calculate_fraud_score(similar_doctors) if self._fraud_detector else 0.0
                        fraud_level = self._fraud_detector._get_fraud_level(fraud_score) if self._fraud_detector else "未知"
                        
                        result = {
                            "requestId": msg_detail['request_id'],
                            "status": "SUCCESS",
                            "doctorId": msg_detail['doctor_id'],
                            "vector_35d": vectors_35d[i].tolist(),
                            "vector_128d": vector_128d.tolist(),
                            "fraudScore": fraud_score,
                            "fraudLevel": fraud_level,
                            "similarDoctors": similar_doctors,
                            "processed": True
                        }
                    else:
                        result = {
                            "requestId": msg_detail['request_id'],
                            "status": "ERROR",
                            "doctorId": msg_detail['doctor_id'],
                            "message": "向量编码失败",
                            "processed": True
                        }
                    results.append(result)
                    
        except Exception as e:
            logger.error(f"批量处理向量时出错: {e}")
            # 返回错误结果
            for msg_detail in message_details:
                result = {
                    "requestId": msg_detail['request_id'],
                    "status": "ERROR",
                    "doctorId": msg_detail['doctor_id'],
                    "message": str(e),
                    "processed": True
                }
                results.append(result)
                
        return results

    def _batch_encode_vectors(self, vectors_35d):
        """批量编码向量"""
        try:
            encoder, scaler = get_encoder()
            if encoder is None or scaler is None:
                return [None] * len(vectors_35d)
            
            # 转换为numpy数组
            vectors_array = np.array(vectors_35d, dtype=np.float32)
            
            # 批量标准化
            vectors_scaled = scaler.transform(vectors_array)
            
            # 转换为PyTorch张量
            vectors_tensor = torch.FloatTensor(vectors_scaled)
            
            # 批量编码
            with torch.no_grad():
                vectors_128d = encoder(vectors_tensor)
            
            # 转换回numpy数组
            results = vectors_128d.numpy()
            
            # 转换为列表
            return [results[i].flatten().astype(np.float32) for i in range(results.shape[0])]
            
        except Exception as e:
            logger.error(f"批量编码向量失败: {e}")
            return [None] * len(vectors_35d)

    def _handle_invalid_vector(self, channel, method, request_id, doctor_id):
        """处理无效向量"""
        try:
            result = {
                "requestId": request_id,
                "status": "ERROR",
                "doctorId": doctor_id,
                "message": "无效的向量数据",
                "processed": True
            }
            
            callback_success = self._send_result(result)
            if callback_success:
                channel.basic_ack(method.delivery_tag)
            else:
                channel.basic_nack(method.delivery_tag, requeue=True)
        except Exception as e:
            logger.error(f"处理无效向量时出错: {e}")
            channel.basic_nack(method.delivery_tag, requeue=False)

    def _send_result(self, result):
        """发送结果到回调URL"""
        try:
            if not hasattr(Config, 'CALLBACK_URL') or not Config.CALLBACK_URL:
                logger.warning("未配置回调URL")
                print("[回调] 未配置回调URL")
                return True  # 如果没有配置回调URL，则认为成功
            
            # 发送HTTP POST请求
            response = requests.post(
                Config.CALLBACK_URL,
                json=result,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"回调成功: {result.get('requestId', 'unknown')}")
                print(f"[回调] 回调成功: {result.get('requestId', 'unknown')}")
                return True
            else:
                logger.warning(f"回调失败，状态码: {response.status_code}")
                print(f"[回调] 回调失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"发送回调请求失败: {e}")
            print(f"[回调] 发送回调请求失败: {e}")
            return False