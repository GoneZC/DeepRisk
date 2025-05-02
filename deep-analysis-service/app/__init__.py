import logging
from flask import Flask, jsonify, request
from config import Config
from app.rabbitmq.consumer import RiskAssessmentConsumer
consumer = RiskAssessmentConsumer()
import time
from logging.handlers import RotatingFileHandler

# 配置全局日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

def create_app(config_class=Config):
    logging.info("Creating Flask app...")
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 配置日志
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    
    # 文件日志
    file_handler = RotatingFileHandler(
        'app.log',
        maxBytes=1024*1024*10,
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

    # 记录关键配置
    app.logger.info("========== RabbitMQ配置 ==========")
    for key in ['RABBITMQ_HOST', 'RABBITMQ_PORT', 'RABBITMQ_USERNAME', 'RABBITMQ_PASSWORD', 
                'RABBITMQ_VHOST', 'RABBITMQ_QUEUE', 'RABBITMQ_EXCHANGE', 'CALLBACK_URL']:
        value = app.config.get(key)
        if key in ['RABBITMQ_PASSWORD']:
            app.logger.info(f"{key}: {'*' * 8 if value else '未配置'}")
        else:
            app.logger.info(f"{key}: {value if value else '未配置'}")

    # 注册蓝图
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.rabbitmq.routes import bp as consumer_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(consumer_bp, url_prefix='/consumer')
    logging.info("Blueprints registered.")

    with app.app_context():
        logging.info("Entering app context for initialization...")
        
        # 加载模型
        from app.models.model_loader import load_models
        load_models()

        # 初始化并启动消费者
        try:
            print("[初始化] 开始初始化消费者...")
            consumer.init_app(app)
            if not consumer._setup_complete:
                error_msg = f"消费者初始化失败，请检查配置和日志。错误: {consumer.last_error}"
                app.logger.error(error_msg)
                print(f"[初始化错误] {error_msg}")
                # 不抛出异常，允许应用继续运行
                app.logger.warning("应用将继续运行，但消费者功能将不可用")
                print("[初始化警告] 应用将继续运行，但消费者功能将不可用")
            else:
                # 确保之前的消费者已停止
                consumer.stop_consuming()
                time.sleep(1)  # 给一点时间让之前的连接完全关闭
                
                # 启动新的消费者
                print("[初始化] 消费者初始化成功，准备启动...")
                consumer.start_consuming()
                app.logger.info("消费者启动成功")
                print("[初始化] 消费者启动成功")
            
        except Exception as e:
            error_msg = f"消费者启动失败: {str(e)}"
            app.logger.error(error_msg, exc_info=True)
            print(f"[初始化错误] {error_msg}")
            # 不抛出异常，允许应用继续运行
            app.logger.warning("应用将继续运行，但消费者功能将不可用")
            print("[初始化警告] 应用将继续运行，但消费者功能将不可用")

        logging.info("Exiting app context.")

    # 添加应用关闭时的清理逻辑
    import atexit
    def cleanup():
        try:
            if hasattr(consumer, 'stop_consuming'):
                consumer.stop_consuming()
                app.logger.info("消费者已停止")
        except Exception as e:
            app.logger.error(f"停止消费者时发生错误: {str(e)}")
    
    atexit.register(cleanup)

    # 添加测试端点
    @app.route('/api/test/manual-consume', methods=['GET'])
    def test_manual_consume():
        """手动触发一次消息消费，用于测试"""
        try:
            result = consumer.manual_consume()
            return jsonify({"status": "success", "message": "手动消费触发成功", "result": result})
        except Exception as e:
            app.logger.error(f"手动消费失败: {str(e)}", exc_info=True)
            return jsonify({"status": "error", "message": f"手动消费失败: {str(e)}"}), 500
    
    @app.route('/api/test/queue-status', methods=['GET'])
    def test_queue_status():
        """获取队列状态，用于测试"""
        try:
            status = consumer.get_consumer_status()
            return jsonify({"status": "success", "queue_status": status})
        except Exception as e:
            app.logger.error(f"获取队列状态失败: {str(e)}", exc_info=True)
            return jsonify({"status": "error", "message": f"获取队列状态失败: {str(e)}"}), 500

    # 添加状态接口路由
    @app.route('/api/consumer/status')
    def consumer_status():
        return jsonify(consumer.get_consumer_status())

    logging.info("Flask app creation complete.")
    return app 