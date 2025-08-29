import sys
import os
import logging
import socket
import time
from contextlib import asynccontextmanager
from nacos import NacosClient

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app/models'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import Config
from app.nacos_config import nacos_config_manager
from app.rabbitmq.consumer import RiskAssessmentConsumer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# 减少第三方库日志输出
logging.getLogger('pika').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('uvicorn').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

print("=" * 50)
print("启动深度分析服务")
print("=" * 50)

# 全局消费者实例
consumer = RiskAssessmentConsumer()

# 全局Nacos客户端实例
nacos_client = None
service_registered = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global nacos_client, service_registered
    # 应用启动时的初始化逻辑
    print("【启动】初始化应用...")
    logger.info("Starting application initialization...")
    
    # 配置应用
    app.config = Config
    
    # 初始化Nacos配置管理器
    try:
        nacos_config_manager.init_nacos()
        logger.info("Nacos配置管理器初始化完成")
    except Exception as e:
        logger.error(f"Nacos配置管理器初始化失败: {str(e)}")
    
    # 初始化Nacos客户端
    try:
        nacos_config = Config.NACOS
        nacos_client = NacosClient(
            server_addresses=nacos_config['server_addr'],
            namespace=nacos_config.get('namespace', None),
            username=nacos_config.get('username', None),
            password=nacos_config.get('password', None)
        )
        
        # 获取本机IP
        host_ip = socket.gethostbyname(socket.gethostname())
        
        # 注册服务到Nacos
        service_name = nacos_config['service_name']
        group = nacos_config.get('group', 'DEFAULT_GROUP')
        cluster_name = nacos_config.get('cluster_name', 'DEFAULT')
        
        nacos_client.add_naming_instance(
            service_name=service_name,
            ip=host_ip,
            port=Config.PORT,
            group_name=group,
            cluster_name=cluster_name,
            metadata={
                "environment": Config.ENVIRONMENT,
                "version": Config.VERSION
            }
        )
        
        logger.info(f"服务 {service_name} 已注册到Nacos")
        service_registered = True
    except Exception as e:
        logger.error(f"Nacos服务注册失败: {str(e)}")
        print(f"[Nacos错误] 服务注册失败: {str(e)}")
    
    # 加载模型
    from app.models.model_loader import load_models
    load_models()
    
    # 初始化并启动消费者
    try:
        print("[初始化] 开始初始化消费者...")
        consumer.init_app(app)
        if not consumer._setup_complete:
            error_msg = f"消费者初始化失败，请检查配置和日志。错误: {consumer.last_error if hasattr(consumer, 'last_error') else '未知错误'}"
            logger.error(error_msg)
            print(f"[初始化错误] {error_msg}")
            logger.warning("应用将继续运行，但消费者功能将不可用")
            print("[初始化警告] 应用将继续运行，但消费者功能将不可用")
        else:
            # 启动消费者
            print("[初始化] 消费者初始化成功，准备启动...")
            consumer.start_consuming()
            logger.info("消费者启动成功")
            print("[初始化] 消费者启动成功")
    except Exception as e:
        error_msg = f"消费者启动失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(f"[初始化错误] {error_msg}")
        logger.warning("应用将继续运行，但消费者功能将不可用")
        print("[初始化警告] 应用将继续运行，但消费者功能将不可用")
    
    yield
    
    # 应用关闭时的清理逻辑
    try:
        if hasattr(consumer, 'stop_consuming'):
            consumer.stop_consuming()
            logger.info("消费者已停止")
    except Exception as e:
        logger.error(f"停止消费者时发生错误: {str(e)}")
    
    # 从Nacos注销服务
    try:
        if service_registered and nacos_client:
            nacos_config = Config.NACOS
            host_ip = socket.gethostbyname(socket.gethostname())
            service_name = nacos_config['service_name']
            group = nacos_config.get('group', 'DEFAULT_GROUP')
            
            nacos_client.remove_naming_service(
                service_name=service_name,
                ip=host_ip,
                port=Config.PORT,
                group_name=group
            )
            logger.info(f"服务 {service_name} 已从Nacos注销")
    except Exception as e:
        logger.error(f"Nacos服务注销失败: {str(e)}")

# 创建FastAPI应用
app = FastAPI(
    title="SmartRisk Analyze Service",
    description="基于FastAPI的风险分析服务",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from app.routes.api import router as api_router
from app.rabbitmq.routes import router as consumer_router
from app.routes.health import router as health_router

app.include_router(api_router, prefix="/api")
app.include_router(consumer_router, prefix="/consumer")
app.include_router(health_router)

@app.get("/")
async def root():
    """首页"""
    return {"message": "欢迎使用SmartRisk分析服务(FastAPI版本)"}

if __name__ == "__main__":
    print("=" * 50)
    print("启动Web服务")
    print("=" * 50)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

    print("Web服务已关闭")
