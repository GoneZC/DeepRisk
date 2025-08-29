import pika
import json
import threading
import logging
import asyncio
import aiohttp
import torch
import numpy as np
import redis
import time
import os
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

class RiskAssessmentConsumer:
    def __init__(self, app=None):
        self.app = app
        self._connection_params = None
        self._consumer_thread = None
        self._stop_event = threading.Event()
        self._setup_complete = False
        self._redis_client = None
        self._fraud_detector = None
        self.last_error = None
        
        # 异步HTTP会话
        self._http_session = None
        
        # 批处理相关配置
        self.batch_queue = deque()  # 存储待处理的消息
        self.batch_size = 16  # 根据测试结果，16是平衡性能和稳定性的批处理大小
        self.batch_timeout = 0.02  # 优化超时时间
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
            logger.info("Redis连接成功")
            
            # 初始化欺诈检测核心模块，仅当环境变量启用时
            self._fraud_detector = None  # 初始化为 None
            if FRAUD_DETECTION_AVAILABLE:
                use_fraud_detection = os.getenv("ENABLE_FRAUD_DETECTION", "true").lower() == "true"
                if use_fraud_detection:
                    try:
                        self._fraud_detector = FraudDetectionCore()
                        logger.info("欺诈检测核心模块初始化成功")
                    except Exception as e:
                        logger.error(f"欺诈检测核心模块初始化失败: {e}")
                else:
                    logger.info("欺诈检测核心模块被环境变量禁用")
            else:
                logger.warning("欺诈检测核心模块不可用")
            
            self._setup_complete = True
            logger.info("RiskAssessmentConsumer初始化完成")
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"RiskAssessmentConsumer初始化失败: {e}")

    def start_consuming(self):
        """启动消费者"""
        if not self._setup_complete:
            logger.error("消费者未正确初始化")
            return
            
        self._consumer_thread = threading.Thread(target=self._consume_messages, daemon=True)
        self._consumer_thread.start()
        logger.info("消费者线程已启动")

    def stop_consuming(self):
        """停止消费者"""
        self._stop_event.set()
        if self._consumer_thread and self._consumer_thread.is_alive():
            self._consumer_thread.join(timeout=5)
        
        # 关闭HTTP会话
        if self._http_session:
            # 注意：这里需要异步关闭，但在同步环境中我们只能尽量处理
            pass
            
        logger.info("消费者已停止")

    def _consume_messages(self):
        """消费消息的主循环"""
        while not self._stop_event.is_set():
            try:
                connection = pika.BlockingConnection(self._connection_params)
                channel = connection.channel()
                
                # 声明队列
                channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True)
                channel.basic_qos(prefetch_count=50)  # 调整预取数量为50
                
                # 设置回调函数
                channel.basic_consume(
                    queue=Config.RABBITMQ_QUEUE,
                    on_message_callback=self._batch_message_handler,
                    auto_ack=False
                )
                
                logger.info(f"等待消息，队列: {Config.RABBITMQ_QUEUE}")
                
                # 启动消费
                channel.start_consuming()
                
            except Exception as e:
                if not self._stop_event.is_set():
                    logger.error(f"消费者连接错误: {e}")
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
            
        # 只在批处理较大时记录日志
        if batch_count >= 8:
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
                
                # 发送结果并确认消息（使用异步回调）
                for i, (result, msg_detail) in enumerate(zip(results, message_details)):
                    try:
                        # 异步发送回调，不阻塞消息确认
                        self._send_result_async_fire_and_forget(result)
                        # 立即确认消息
                        msg_detail['channel'].basic_ack(msg_detail['method'].delivery_tag)
                        # 只在批处理较大时记录成功日志
                        if batch_count >= 8:
                            logger.info(f"消息处理成功并确认: {msg_detail['request_id']}")
                    except Exception as e:
                        logger.error(f"处理单个消息结果时出错: {e}")
                        msg_detail['channel'].basic_nack(msg_detail['method'].delivery_tag, requeue=False)
                        
        except Exception as e:
            logger.error(f"批处理执行失败: {e}")
            # 所有消息重新入队
            for msg_info in batch_messages:
                msg_info['channel'].basic_nack(msg_info['method'].delivery_tag, requeue=True)

    def _batch_process_vectors(self, vectors_35d, message_details):
        """批量处理向量"""
        results = []
        
        try:
            if self._fraud_detector is not None:
                # 使用欺诈检测核心模块进行真正的批处理风险评估
                logger.info(f"使用欺诈检测核心模块进行批处理风险评估，处理 {len(vectors_35d)} 个向量")
                
                # 提取医生ID列表
                doctor_ids = [msg_detail['doctor_id'] for msg_detail in message_details]
                
                # 使用批处理方法处理所有向量
                batch_results = self._fraud_detector.process_vectors_batch(vectors_35d, doctor_ids)
                
                # 转换为所需的返回格式
                for i, fraud_result in enumerate(batch_results):
                    msg_detail = message_details[i]
                    result = {
                        "requestId": msg_detail['request_id'],
                        "status": "SUCCESS" if "error" not in fraud_result else "ERROR",
                        "doctorId": fraud_result.get("doctor_id"),
                        "fraudScore": fraud_result.get("fraud_score", 0.0),
                        "fraudLevel": fraud_result.get("fraud_level", "未知"),
                        "similarDoctors": fraud_result.get("similar_doctors", []),
                        "processed": True
                    }
                    if "error" in fraud_result:
                        result["message"] = fraud_result["error"]
                    results.append(result)
            else:
                # 备用处理方式
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
            
            # 异步发送回调，不阻塞消息确认
            self._send_result_async_fire_and_forget(result)
            # 立即确认消息
            channel.basic_ack(method.delivery_tag)
        except Exception as e:
            logger.error(f"处理无效向量时出错: {e}")
            channel.basic_nack(method.delivery_tag, requeue=False)

    def _send_result_async_fire_and_forget(self, result):
        """发送结果到回调URL（"fire and forget"方式）"""
        try:
            if not hasattr(Config, 'CALLBACK_URL') or not Config.CALLBACK_URL:
                logger.warning("未配置回调URL")
                return True  # 如果没有配置回调URL，则认为成功
            
            # 使用fire and forget方式发送HTTP请求
            # 这里我们创建一个独立的线程来发送请求，但不等待结果
            thread = threading.Thread(target=self._send_http_request, args=(result,))
            thread.daemon = True
            thread.start()
            
            return True
        except Exception as e:
            logger.error(f"启动异步回调请求失败: {e}")
            return False

    def _send_http_request(self, result):
        """在独立线程中发送HTTP请求"""
        try:
            import requests
            # 发送HTTP POST请求
            response = requests.post(
                Config.CALLBACK_URL,
                json=result,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"回调成功: {result.get('requestId', 'unknown')}")
            else:
                logger.warning(f"回调失败，状态码: {response.status_code}")
        except Exception as e:
            logger.error(f"发送回调请求失败: {e}")

    def _send_result(self, result):
        """发送结果到回调URL（同步方法，为兼容性保留）"""
        try:
            if not hasattr(Config, 'CALLBACK_URL') or not Config.CALLBACK_URL:
                logger.warning("未配置回调URL")
                return True  # 如果没有配置回调URL，则认为成功
            
            # 发送HTTP POST请求
            import requests
            response = requests.post(
                Config.CALLBACK_URL,
                json=result,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"回调成功: {result.get('requestId', 'unknown')}")
                return True
            else:
                logger.warning(f"回调失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"发送回调请求失败: {e}")
            return False

    def get_consumer_status(self):
        """获取消费者运行状态"""
        if self._consumer_thread is not None and self._consumer_thread.is_alive():
            return "running"
        elif self._setup_complete:
            return "initialized"
        else:
            return "stopped"

    def _get_connection(self):
        """获取RabbitMQ连接"""
        if not self._setup_complete:
            raise Exception("消费者未正确初始化")
        
        return pika.BlockingConnection(self._connection_params)

    def get_status(self):
        """获取消费者状态"""
        status = {
            'initialized': self._setup_complete,
            'running': self._consumer_thread is not None and self._consumer_thread.is_alive(),
            'batch_queue_size': len(self.batch_queue),
            'batch_size': self.batch_size,
            'last_error': self.last_error,
            'queue': Config.RABBITMQ_QUEUE if hasattr(Config, 'RABBITMQ_QUEUE') else 'unknown',
            'exchange': Config.RABBITMQ_EXCHANGE if hasattr(Config, 'RABBITMQ_EXCHANGE') else 'unknown',
            'routing_key': Config.RABBITMQ_ROUTING_KEY if hasattr(Config, 'RABBITMQ_ROUTING_KEY') else 'unknown',
            'thread_alive': self._consumer_thread is not None and self._consumer_thread.is_alive() if hasattr(self, '_consumer_thread') else False
        }
        return status

# 移除了这里初始化的 consumer 实例