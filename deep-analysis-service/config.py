import os
from pathlib import Path

class Config:
    # 项目根目录
    BASEDIR = Path(__file__).resolve().parent
    
    # 秘钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key'
    
    # 模型目录
    MODELS_DIR = os.environ.get('MODELS_DIR') or os.path.join(BASEDIR, 'models')
    
    # 临时文件目录
    TEMP_DIR = os.environ.get('TEMP_DIR') or os.path.join(BASEDIR, 'temp')
    
    # 设备配置 (CPU/GPU)
    DEVICE = os.environ.get('DEVICE') or ('cuda' if os.path.exists('/dev/nvidia0') else 'cpu')
    
    # 上传文件配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB限制
    UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png']
    
    # 数据库连接配置
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '123456'
    MYSQL_DB = 'shenzhen_medical'
    MYSQL_PORT = 3306
    
    # RabbitMQ配置
    RABBITMQ_HOST = 'localhost'
    RABBITMQ_PORT = 5672
    RABBITMQ_USERNAME = 'guest'
    RABBITMQ_PASSWORD = 'guest'
    RABBITMQ_VHOST = '/'
    RABBITMQ_EXCHANGE = 'risk.assessment.exchange'
    RABBITMQ_QUEUE = 'risk.assessment.queue'
    RABBITMQ_ROUTING_KEY = 'risk.assessment'
    
    # 回调配置
    
    # 尝试不同的回调URL格式
    CALLBACK_URL = 'http://localhost:8082/async-risk-assessment/result'
    
    # 回调重试配置
    CALLBACK_MAX_RETRIES = 3
    CALLBACK_RETRY_DELAY = 2  # 秒
    
    # API网关配置
    API_GATEWAY_SCHEME = os.environ.get('API_GATEWAY_SCHEME', 'http') # http or https
    API_GATEWAY_HOST = os.environ.get('API_GATEWAY_HOST', 'localhost')
    API_GATEWAY_PORT = int(os.environ.get('API_GATEWAY_PORT', 8082))
    
    DEBUG = True 

    # 模型路径等其他配置
    MODEL_PATH = os.environ.get('MODEL_PATH', 'app/models/saved_models')
    THRESHOLD_PATH = os.environ.get('THRESHOLD_PATH', 'app/models/risk_thresholds.json')

    # 可以添加数据库配置等
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False 