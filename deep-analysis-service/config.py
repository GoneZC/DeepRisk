import os
from pathlib import Path

class Config:
    # 项目根目录
    BASEDIR = Path(__file__).resolve().parent
    
    # 秘钥
    SECRET_KEY = 'your-secret-key'
    
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
    
    DEBUG = True 