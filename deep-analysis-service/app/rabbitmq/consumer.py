import pika
import json
import threading
import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)

class RiskAssessmentConsumer:
    def __init__(self, app=None):
        self.app = app
        self._connection_params = None
        self._consumer_thread = None
        self._stop_event = threading.Event()
        self._setup_complete = False

    def init_app(self, app):
        """初始化配置"""
        self.app = app
        try:
            config = app.config
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
            
            self._setup_queues()
            self._setup_complete = True
            logger.info(f"消费者初始化成功")
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            self._setup_complete = False

    def _setup_queues(self):
        """设置队列和交换器"""
        with pika.BlockingConnection(self._connection_params) as conn:
            channel = conn.channel()
            
            # 声明交换器和队列
            channel.exchange_declare(exchange=self.exchange, exchange_type='direct', durable=True)
            channel.queue_declare(queue=self.queue, durable=True)
            channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=self.routing_key)
            
            # 死信队列
            dlq_name = f"{self.queue}.dlq"
            channel.queue_declare(queue=dlq_name, durable=True)

    def start_consuming(self):
        """启动消费者"""
        if not self._setup_complete:
            logger.error("配置未完成，无法启动消费者")
            return False

        if self._consumer_thread and self._consumer_thread.is_alive():
            return True

        self._stop_event.clear()
        self._consumer_thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._consumer_thread.start()
        logger.info("消费者线程已启动")
        return True

    def stop_consuming(self):
        """停止消费者"""
        self._stop_event.set()
        if self._consumer_thread:
            self._consumer_thread.join(timeout=5)
        logger.info("消费者线程已停止")

    def _consume_loop(self):
        """消费主循环"""
        retry_count = 0
        max_retries = 5

        while not self._stop_event.is_set() and retry_count < max_retries:
            try:
                with pika.BlockingConnection(self._connection_params) as conn:
                    channel = conn.channel()
                    channel.basic_qos(prefetch_count=10)
                    
                    def callback(ch, method, properties, body):
                        if self._stop_event.is_set():
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                            return
                        self._process_message(ch, method, body)
                    
                    channel.basic_consume(queue=self.queue, on_message_callback=callback)
                    channel.start_consuming()
                    
                retry_count = 0  # 重置重试计数

            except Exception as e:
                logger.error(f"消费循环错误: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    threading.Event().wait(10)  # 等待10秒重试

    def _process_message(self, channel, method, body):
        """处理消息"""
        try:
            # 解析消息
            message_str = body.decode('utf-8')
            try:
                message = json.loads(message_str)
                if isinstance(message, str):  # 处理嵌套JSON
                    message = json.loads(message)
            except:
                message = {"content": message_str}
            
            request_id = message.get('requestId', f"msg-{message_str[:10]}")
            doctor_id = message.get('doctorId')
            
            logger.info(f"处理消息: {request_id}")
            
            # 调用风险评估
            if doctor_id:
                result = self._perform_risk_assessment(request_id, doctor_id, message)
            else:
                result = {
                    "requestId": request_id,
                    "status": "WARNING", 
                    "score": 0.85,
                    "message": "缺少医生ID",
                    "processed": True
                }
            
            # 发送回调
            if self._send_result(result):
                channel.basic_ack(method.delivery_tag)
                logger.info(f"消息处理成功: {request_id}")
            else:
                # 修复回调失败逻辑
                retries = message.get('retries', 0)
                if retries < 3:
                    message['retries'] = retries + 1
                    channel.basic_nack(method.delivery_tag, requeue=True)
                    logger.warning(f"消息重试: {request_id}, 次数: {retries + 1}")
                else:
                    channel.basic_nack(method.delivery_tag, requeue=False)
                    logger.error(f"消息发送到死信队列: {request_id}")
                    
        except Exception as e:
            logger.error(f"处理消息失败: {str(e)}")
            channel.basic_nack(method.delivery_tag, requeue=True)

    def _perform_risk_assessment(self, request_id, doctor_id, original_message):
        """执行风险评估"""
        try:
            from app.routes.api import risk_assessment as perform_risk_assessment
            
            assessment_data = {"doctorId": doctor_id}
            if 'date' in original_message:
                assessment_data["date"] = original_message['date']
            
            with current_app.test_request_context(json=assessment_data):
                response = perform_risk_assessment()
                
                if response.status_code >= 400:
                    raise Exception(f"API错误: {response.status_code}")
                
                assessment_result = response.get_json()
                
                return {
                    "requestId": request_id,
                    "status": "SUCCESS",
                    "score": assessment_result.get("combinedScore", 0.85),
                    "feeScore": assessment_result.get("feeScore", 0),
                    "drugScore": assessment_result.get("drugScore", 0), 
                    "diagScore": assessment_result.get("diagScore", 0),
                    "feeRiskLevel": assessment_result.get("feeRiskLevel", "低"),
                    "drugRiskLevel": assessment_result.get("drugRiskLevel", "低"),
                    "diagRiskLevel": assessment_result.get("diagRiskLevel", "低"),
                    "processed": True
                }
                
        except Exception as e:
            logger.error(f"风险评估失败: {str(e)}")
            return {
                "requestId": request_id,
                "status": "ERROR",
                "score": 0.85,
                "message": f"评估失败: {str(e)[:100]}",
                "processed": True
            }

    def _send_result(self, result):
        """发送结果到回调URL"""
        try:
            if not self.callback_url:
                logger.warning("未配置回调URL")
                return False  # 修复：没有回调URL应该返回False
                
            response = requests.post(
                self.callback_url,
                json=result,
                headers={
                    'Content-Type': 'application/json',
                    'X-Request-ID': result.get('requestId', 'unknown')
                },
                timeout=10
            )
            
            if 200 <= response.status_code < 300:
                return True
            else:
                logger.error(f"回调失败: {response.status_code} - {response.text[:100]}")
                return False  # 修复：失败应该返回False以触发重试
                
        except Exception as e:
            logger.error(f"发送回调异常: {str(e)}")
            return False  # 修复：异常应该返回False以触发重试

def start_consumer_thread(app):
    """启动消费者线程"""
    consumer = RiskAssessmentConsumer()
    consumer.init_app(app)
    consumer.start_consuming()
    return consumer

consumer = RiskAssessmentConsumer()