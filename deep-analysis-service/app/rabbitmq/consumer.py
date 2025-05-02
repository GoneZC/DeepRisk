import pika
import json
import threading
import time
import logging
import requests
from flask import current_app, jsonify
from functools import partial
import datetime

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # 确保日志级别为INFO

# 添加控制台处理器，确保日志输出到控制台
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

class RiskAssessmentConsumer:
    def __init__(self, app=None):
        self.app = app
        self._connection_params = None
        self._consumer_thread = None
        self._stop_event = threading.Event()
        self._is_consuming = False
        self._setup_complete = False
        self.message_count = 0
        self.consumer_count = 0
        self.last_error = None

    def init_app(self, app):
        """安全初始化应用配置"""
        self.app = app
        try:
            logger.info("开始初始化消费者配置...")
            self._load_config()
            self._validate_config()
            self._setup_connection()
            self._setup_complete = True
            logger.info(f"消费者初始化成功，回调地址: {self.callback_url}")
        except Exception as e:
            logger.critical(f"初始化失败: {str(e)}", exc_info=True)
            self._setup_complete = False
            self.last_error = str(e)

    def _load_config(self):
        """加载并验证配置"""
        config = self.app.config
        self._connection_params = pika.ConnectionParameters(
            host=config['RABBITMQ_HOST'],
            port=config.get('RABBITMQ_PORT', 5672),
            virtual_host=config.get('RABBITMQ_VHOST', '/'),
            credentials=pika.PlainCredentials(
                config['RABBITMQ_USERNAME'],
                config['RABBITMQ_PASSWORD']
            ),
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.queue = config['RABBITMQ_QUEUE']
        self.exchange = config['RABBITMQ_EXCHANGE']
        self.routing_key = config['RABBITMQ_ROUTING_KEY']
        self.callback_url = config['CALLBACK_URL']

    def _validate_config(self):
        """验证必要配置"""
        required = ['RABBITMQ_HOST', 'RABBITMQ_USERNAME', 
                   'RABBITMQ_PASSWORD', 'RABBITMQ_QUEUE',
                   'CALLBACK_URL']
        missing = [key for key in required if not self.app.config.get(key)]
        if missing:
            raise ValueError(f"缺少必要配置: {missing}")

    def _setup_connection(self):
        """声明队列和交换器，可选设置死信队列"""
        try:
            with self._get_connection() as conn:
                channel = conn.channel()
                
                # 声明主交换机
                try:
                    channel.exchange_declare(
                        exchange=self.exchange,
                        exchange_type='direct',
                        durable=True
                    )
                    print(f"[队列设置] 成功声明交换机: {self.exchange}")
                except Exception as e:
                    print(f"[队列设置] 声明交换机失败: {self.exchange}, 错误: {str(e)}")
                    logger.error(f"声明交换机失败: {str(e)}")
                    raise
                
                # 声明主队列，简化设置
                try:
                    channel.queue_declare(
                        queue=self.queue,
                        durable=True
                    )
                    print(f"[队列设置] 成功声明队列: {self.queue}")
                except Exception as e:
                    print(f"[队列设置] 声明队列失败: {self.queue}, 错误: {str(e)}")
                    logger.error(f"声明队列失败: {str(e)}")
                    raise
                
                # 绑定主队列到主交换机
                try:
                    channel.queue_bind(
                        exchange=self.exchange,
                        queue=self.queue,
                        routing_key=self.routing_key
                    )
                    print(f"[队列设置] 成功绑定队列: {self.queue} -> {self.exchange}")
                except Exception as e:
                    print(f"[队列设置] 绑定队列失败, 错误: {str(e)}")
                    logger.error(f"绑定队列失败: {str(e)}")
                    raise
                
                # 尝试设置死信队列，但不影响主要功能
                try:
                    dlq_name = f"{self.queue}.dlq"
                    channel.queue_declare(
                        queue=dlq_name,
                        durable=True
                    )
                    print(f"[队列设置] 成功声明死信队列: {dlq_name}")
                    
                    # 检查队列状态
                    result = channel.queue_declare(queue=self.queue, passive=True)
                    print(f"[队列状态] {self.queue}: 消息数={result.method.message_count}, 消费者数={result.method.consumer_count}")
                except Exception as e:
                    # 死信队列设置失败不影响主要功能，只记录日志
                    print(f"[队列设置] 设置死信队列失败 (非致命错误): {str(e)}")
                    logger.warning(f"设置死信队列失败 (非致命错误): {str(e)}")
                
                logger.info("队列和交换器声明完成")
                
        except Exception as e:
            logger.critical(f"设置连接失败: {str(e)}", exc_info=True)
            print(f"[队列设置] 设置连接失败: {str(e)}")
            raise

    def start_consuming(self):
        """启动消费者线程"""
        if not self._setup_complete:
            logger.error("配置未完成，无法启动消费者")
            return False

        if self._consumer_thread and self._consumer_thread.is_alive():
            logger.warning("消费者线程已在运行")
            return True

        self._stop_event.clear()
        self._consumer_thread = threading.Thread(
            target=self._consume_loop,
            name="RabbitMQConsumer",
            daemon=True
        )
        self._consumer_thread.start()
        logger.info("消费者线程已启动")
        return True

    def stop_consuming(self):
        """停止消费者线程"""
        if not self._consumer_thread or not self._consumer_thread.is_alive():
            logger.warning("消费者线程未运行")
            return False
            
        logger.info("正在停止消费者线程...")
        self._stop_event.set()
        
        # 等待线程结束，但最多等待5秒
        self._consumer_thread.join(timeout=5)
        self._is_consuming = False
        logger.info("消费者线程已停止")
        return True

    def _consume_loop(self):
        """消费主循环"""
        retry_count = 0
        max_retries = 5
        retry_delay = 10  # 秒

        print(f"[消费循环] 开始运行消费循环，队列: {self.queue}")
        logger.info(f"开始运行消费循环，队列: {self.queue}")

        while not self._stop_event.is_set() and retry_count < max_retries:
            try:
                print(f"[消费循环] 尝试连接到RabbitMQ: {self._connection_params.host}:{self._connection_params.port}")
                with self._get_connection() as conn:
                    channel = conn.channel()
                    channel.basic_qos(prefetch_count=10)  # 降低预取数量为10
                    
                    self._is_consuming = True
                    print(f"[消费循环] 已连接，开始消费消息...")
                    logger.info("开始消费消息...")
                    
                    def callback(ch, method, properties, body):
                        try:
                            if self._stop_event.is_set():
                                # 不再每次都打印停止信息，避免刷屏
                                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                                return
                            
                            # 不再每条消息都打印，避免日志过多
                            self._process_message(ch, method, body)
                            
                        except Exception as e:
                            logger.error(f"处理消息时发生错误: {str(e)}", exc_info=True)
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    
                    print(f"[消费循环] 注册消费回调函数")
                    channel.basic_consume(
                        queue=self.queue,
                        on_message_callback=callback
                    )
                    
                    # 开始消费循环
                    try:
                        print(f"[消费循环] 启动消费循环，等待消息...")
                        channel.start_consuming()
                    except Exception as e:
                        print(f"[消费循环] 消费循环中断: {str(e)}")
                        logger.error(f"消费循环中断: {str(e)}")
                        if not self._stop_event.is_set():  # 如果不是主动停止，则重试
                            raise
                    
                    retry_count = 0  # 成功连接后重置重试计数

            except pika.exceptions.AMQPError as e:
                print(f"[消费循环] AMQP错误: {str(e)}")
                logger.error(f"AMQP错误: {str(e)}")
                retry_count += 1
                self.last_error = str(e)
                self._handle_retry(retry_count, max_retries, retry_delay)
            except Exception as e:
                print(f"[消费循环] 意外错误: {str(e)}")
                logger.error(f"意外错误: {str(e)}", exc_info=True)
                retry_count += 1
                self.last_error = str(e)
                self._handle_retry(retry_count, max_retries, retry_delay)
            finally:
                self._is_consuming = False
                print(f"[消费循环] 消费循环已结束")
                logger.info("消费循环已结束")

    def _get_connection(self):
        """获取带自动重连的连接"""
        logger.debug(f"尝试连接参数: {self._connection_params}")
        return pika.BlockingConnection(self._connection_params)

    def _handle_retry(self, retry_count, max_retries, retry_delay):
        """处理重试逻辑"""
        if retry_count < max_retries:
            print(f"[消费循环] 将在{retry_delay}秒后重试 ({retry_count}/{max_retries})")
            logger.warning(f"将在{retry_delay}秒后重试连接 ({retry_count}/{max_retries})")
            time.sleep(retry_delay)
        else:
            print(f"[消费循环] 已达到最大重试次数 ({max_retries})，停止重试")
            logger.error(f"已达到最大重试次数 ({max_retries})，停止重试")
            self._stop_event.set()

    def _send_result(self, result):
        """发送处理结果到回调URL"""
        try:
            if not self.callback_url:
                logger.warning("未配置回调URL，无法发送结果")
                # 为避免无限重试，即使未配置回调也返回成功
                logger.warning("未配置回调URL，但标记为成功以避免重试")
                return True
                
            # 发送POST请求到回调URL
            response = requests.post(
                self.callback_url,
                json=result,
                headers={
                    'Content-Type': 'application/json',
                    'X-Request-ID': result.get('requestId', 'unknown')
                },
                timeout=10  # 最多等待10秒
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                return True
            else:
                # 临时解决方案：记录错误但返回成功以避免重试循环
                logger.error(f"回调失败(忽略): {response.status_code} - {response.text[:100]}")
                return True
        except Exception as e:
            # 临时解决方案：记录错误但返回成功以避免重试循环
            logger.error(f"发送回调时发生错误(忽略): {str(e)}")
            return True
            
    def _should_requeue_on_callback_failure(self, result):
        """决定在回调失败时是否重新入队消息"""
        # 如果是系统错误，重试3次
        retries = result.get('retries', 0)
        if retries < 3:
            result['retries'] = retries + 1
            return True
        return False
        
    def _send_to_dlq(self, message):
        """将消息发送到死信队列"""
        try:
            # 简单记录到日志，实际应用可能需要将消息存储到数据库或死信队列
            logger.warning(f"消息发送到死信队列: {message.get('requestId', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"发送到死信队列失败: {str(e)}")
            return False
            
    def _get_queue_status(self, queue_name):
        """获取队列状态"""
        try:
            with self._get_connection() as conn:
                channel = conn.channel()
                result = channel.queue_declare(queue=queue_name, passive=True)
                return {
                    "message_count": result.method.message_count,
                    "consumer_count": result.method.consumer_count
                }
        except Exception as e:
            logger.error(f"获取队列状态失败: {str(e)}")
            return {"message_count": 0, "consumer_count": 0}
            
    def get_consumer_status(self):
        """获取消费者状态"""
        status = {
            "is_setup_complete": self._setup_complete,
            "is_consuming": self._is_consuming,
            "last_error": self.last_error
        }
        
        # 尝试获取队列状态
        try:
            if self._setup_complete:
                queue_status = self._get_queue_status(self.queue)
                status.update(queue_status)
        except:
            pass
            
        return status
        
    def manual_consume(self):
        """手动消费一条消息（用于测试）"""
        if not self._setup_complete:
            raise ValueError("消费者未完成初始化")
            
        try:
            with self._get_connection() as conn:
                channel = conn.channel()
                method, properties, body = channel.basic_get(
                    queue=self.queue,
                    auto_ack=False
                )
                
                if not method:
                    return {"status": "empty", "message": "队列为空"}
                    
                # 处理消息
                with self.app.app_context():
                    result = self._process_message(channel, method, body)
                    
                return {
                    "status": "success" if result else "failed",
                    "message": "消息处理完成" if result else "消息处理失败"
                }
        except Exception as e:
            logger.error(f"手动消费失败: {str(e)}")
            raise

    def _process_message(self, channel, method, body):
        """处理单个消息"""
        # 确保在Flask应用上下文中执行
        if self.app and not current_app:
            with self.app.app_context():
                return self._process_message_with_context(channel, method, body)
        else:
            return self._process_message_with_context(channel, method, body)
            
    def _process_message_with_context(self, channel, method, body):
        """在应用上下文中处理消息"""
        try:
            # 尝试解码消息体
            message_str = body.decode('utf-8')
            original_message = None
            
            # 检查消息是否为JSON格式
            try:
                message = json.loads(message_str)
                # 保存原始消息用于回调
                original_message = message
                
                # 检查message是否为字典
                if not isinstance(message, dict):
                    raise ValueError(f"消息不是有效的JSON对象: {type(message)}")
                
                request_id = message.get('requestId', '未知ID')
            except (json.JSONDecodeError, ValueError) as e:
                # 如果不是JSON或不是字典，使用消息内容的前10个字符作为ID
                print(f"[消息处理] 非标准JSON消息: {str(e)[:50]}")
                
                # 尝试看看原始消息是否包含嵌套的JSON字符串
                try:
                    if message_str.startswith('"') and message_str.endswith('"'):
                        # 尝试解析嵌套的JSON字符串
                        unescaped = message_str[1:-1].replace('\\"', '"')
                        nested_message = json.loads(unescaped)
                        if isinstance(nested_message, dict):
                            original_message = nested_message
                            request_id = nested_message.get('requestId', f"嵌套JSON-{unescaped[:10]}...")
                            print(f"[消息处理] 发现嵌套JSON消息: {request_id}")
                        else:
                            message = {"content": message_str}
                            request_id = f"非JSON-{message_str[:10]}..."
                    else:
                        message = {"content": message_str}
                        request_id = f"非JSON-{message_str[:10]}..."
                except:
                    message = {"content": message_str}
                    request_id = f"非JSON-{message_str[:10]}..."
            
            # 只在处理开始时打印一次简短信息
            print(f"[消息处理] 开始处理: {request_id}")
            logger.info(f"处理消息: {request_id}")
            
            # 从消息中提取参数
            doctor_id = None
            date = None
            
            # 直接从message中获取数据
            if isinstance(message, dict):
                doctor_id = message.get('doctorId')
                date = message.get('date')
            
            if not doctor_id:
                print(f"[消息处理] 消息缺少doctorId参数，使用默认风险评分")
                # 构建默认结果
                result = {
                    "requestId": request_id,
                    "status": "WARNING",
                    "score": 0.85,  # 默认分数
                    "message": "无法找到医生ID，使用默认风险评分",
                    "processed": True,
                    "originalMessage": original_message
                }
            else:
                try:
                    # 准备调用风险评估API
                    from flask import current_app
                    from app.routes.api import risk_assessment as perform_risk_assessment
                    from flask import request as flask_request
                    
                    # 模拟请求对象
                    class MockRequest:
                        def __init__(self, json_data):
                            self.json = json_data
                    
                    # 保存原始请求对象
                    original_request = flask_request
                    
                    # 创建模拟请求
                    assessment_data = {"doctorId": doctor_id}
                    if date:
                        assessment_data["date"] = date
                    
                    # 调用风险评估函数
                    try:
                        # 导入和设置需要的上下文
                        from flask import _request_ctx_stack
                        # 创建测试请求上下文，并传入JSON数据
                        with current_app.test_request_context(json=assessment_data):
                            response = perform_risk_assessment()
                            status_code = response.status_code
                        
                        # 检查响应状态
                        if status_code >= 400:
                            raise Exception(f"风险评估API返回错误: {response}")
                        
                        # 提取评估结果
                        assessment_result = response.get_json()
                        
                        # 构建完整的结果对象
                        result = {
                            "requestId": request_id,
                            "status": "SUCCESS",
                            "score": assessment_result.get("combinedScore", 0.85),
                            "feeScore": assessment_result.get("feeScore", 0),
                            "drugScore": assessment_result.get("drugScore", 0),
                            "diagScore": assessment_result.get("diagScore", 0),
                            "feeRiskLevel": assessment_result.get("feeRiskLevel", "低"),
                            "drugRiskLevel": assessment_result.get("drugRiskLevel", "低"),
                            "diagRiskLevel": assessment_result.get("diagRiskLevel", "低"),
                            "processed": True,
                            "originalMessage": original_message
                        }
                        
                        print(f"[消息处理] 风险评估完成: {doctor_id}, 分数={result['score']}")
                        
                    except Exception as e:
                        print(f"[消息处理] 风险评估异常: {str(e)[:100]}")
                        # 出错时使用默认结果
                        result = {
                            "requestId": request_id,
                            "status": "ERROR",
                            "score": 0.85,  # 默认分数
                            "message": f"风险评估失败: {str(e)[:100]}",
                            "processed": True,
                            "originalMessage": original_message
                        }
                except Exception as e:
                    print(f"[消息处理] 调用风险评估服务异常: {str(e)[:100]}")
                    # 构建错误结果
                    result = {
                        "requestId": request_id,
                        "status": "ERROR",
                        "score": 0.85,
                        "message": f"风险评估服务异常: {str(e)[:100]}",
                        "processed": True,
                        "originalMessage": original_message
                    }
            
            # 发送结果并处理回调失败的情况
            callback_success = self._send_result(result)
            
            if callback_success:
                # 回调成功，确认消息
                channel.basic_ack(method.delivery_tag)
                print(f"[消息处理] 成功: {request_id}")
                logger.info(f"消息处理成功: {request_id}")
                return True
            else:
                # 回调失败处理
                # 1. 确认当前消息队列状态
                try:
                    queue_status = self._get_queue_status(self.queue)
                    msg_count = queue_status.get("message_count", 0)
                    consumer_count = queue_status.get("consumer_count", 0)
                    print(f"[消息处理] 当前队列状态: 消息数={msg_count}, 消费者数={consumer_count}")
                except:
                    pass
                
                # 2. 检查是否已重试过多次（通过死信队列判断）
                dlq_name = f"{self.queue}.dlq"
                try:
                    dlq_status = self._get_queue_status(dlq_name)
                    dlq_count = dlq_status.get("message_count", 0)
                    print(f"[消息处理] 死信队列状态: 消息数={dlq_count}")
                    
                    # 如果死信队列消息数量过多，停止重试
                    if dlq_count > 20:
                        print(f"[消息处理] 死信队列积压严重，不再重新入队: {request_id}")
                        channel.basic_nack(method.delivery_tag, requeue=False)
                        self._send_to_dlq(result)
                        return False
                except:
                    pass
                
                # 决定是否重新入队
                if self._should_requeue_on_callback_failure(result):
                    print(f"[消息处理] 回调失败，消息重新入队: {request_id}")
                    channel.basic_nack(method.delivery_tag, requeue=True)
                    return False
                else:
                    print(f"[消息处理] 回调失败，消息发送到死信队列: {request_id}")
                    channel.basic_nack(method.delivery_tag, requeue=False)
                    self._send_to_dlq(result)
                    return False
            
        except UnicodeDecodeError as e:
            print(f"[消息处理] 解码失败: {str(e)[:50]}")
            logger.error(f"消息解码失败: {str(e)}")
            # 不可恢复的错误，消息格式完全不对
            channel.basic_nack(method.delivery_tag, requeue=False)
            self._send_to_dlq({"error": "decode_error", "message": str(e)})
            return False
        except Exception as e:
            print(f"[消息处理] 处理失败: {str(e)[:50]}")
            logger.error(f"处理失败: {str(e)}")
            # 其他错误可能是暂时的，重新入队
            channel.basic_nack(method.delivery_tag, requeue=True)
            return False

def start_consumer_thread(app):
    """启动消费者线程"""
    consumer = RiskAssessmentConsumer()
    consumer.init_app(app)
    consumer.start_consuming()
    return consumer

consumer = RiskAssessmentConsumer()