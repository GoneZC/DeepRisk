import os
from pathlib import Path

class Config:
    # 基础配置
    BASEDIR = Path(__file__).resolve().parent.parent
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key'
    
    # 目录配置
    MODELS_DIR = os.environ.get('MODELS_DIR') or os.path.join(BASEDIR, 'models')
    TEMP_DIR = os.environ.get('TEMP_DIR') or os.path.join(BASEDIR, 'temp')
    
    # 设备配置
    DEVICE = os.environ.get('DEVICE') or ('cuda' if os.path.exists('/dev/nvidia0') else 'cpu')
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png']
    
    # MySQL配置
    MYSQL_HOST = os.environ.get('DB_HOST', '172.20.0.1')
    MYSQL_USER = os.environ.get('DB_USERNAME', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
    MYSQL_DB = 'risk_control_platform'
    MYSQL_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # RabbitMQ配置
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'host.docker.internal')
    RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
    RABBITMQ_USERNAME = os.environ.get('RABBITMQ_USERNAME', 'guest')
    RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD', 'guest')
    RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST', '/')
    RABBITMQ_EXCHANGE = os.environ.get('RABBITMQ_EXCHANGE', 'risk.assessment.exchange')
    RABBITMQ_QUEUE = os.environ.get('RABBITMQ_QUEUE', 'risk.assessment.queue')
    RABBITMQ_ROUTING_KEY = os.environ.get('RABBITMQ_ROUTING_KEY', 'risk.assessment')

    # Redis配置
    REDIS_HOST = os.environ.get('REDIS_HOST', 'host.docker.internal')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6380))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    
    # 回调配置
    CALLBACK_URL = 'http://localhost:8081/async-risk-assessment/result'
    
    # 重试配置
    CALLBACK_MAX_RETRIES = 3
    CALLBACK_RETRY_DELAY = 2  # 秒
    
    # 即使回调失败也确认消息（避免消息堆积）
    ACK_ON_CALLBACK_FAILURE = True
    
    # API网关配置
    API_GATEWAY_SCHEME = os.environ.get('API_GATEWAY_SCHEME', 'http') # http or https
    API_GATEWAY_HOST = os.environ.get('API_GATEWAY_HOST', 'host.docker.internal')
    API_GATEWAY_PORT = int(os.environ.get('API_GATEWAY_PORT', 8081))
    
    DEBUG = True 

    # 模型路径等其他配置
    MODEL_PATH = os.environ.get('MODEL_PATH', 'app/models/saved_models')
    THRESHOLD_PATH = os.environ.get('THRESHOLD_PATH', 'app/models/risk_thresholds.json')

    # Nacos配置中心配置 (运行在Docker容器中)
    NACOS = {
        'server_addr': os.environ.get('NACOS_SERVER_ADDR', 'nacos:8848'),
        'namespace': os.environ.get('NACOS_NAMESPACE', 'public'),
        'group': os.environ.get('NACOS_GROUP', 'DEFAULT_GROUP'),
        'service_name': os.environ.get('NACOS_SERVICE_NAME', 'analysis-service'),
        'data_id': os.environ.get('NACOS_DATA_ID', 'analysis-service'),
        'timeout': int(os.environ.get('NACOS_TIMEOUT', 3000)),
        'enable_remote_config': os.environ.get('NACOS_ENABLE_REMOTE_CONFIG', 'false').lower() == 'true',
        'cluster_name': os.environ.get('NACOS_CLUSTER_NAME', 'DEFAULT')
    }
    
    PORT = int(os.environ.get('SERVER_PORT', 8000))
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
    VERSION = os.environ.get('VERSION', '1.0.0')

    # 可以添加数据库配置等
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False