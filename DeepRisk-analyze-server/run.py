import sys
import os
import logging

# 设置基本日志配置
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# 调整第三方库日志级别，减少噪音
logging.getLogger('pika').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('uvicorn').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

print("="*50)
print("【启动】开始启动深度分析服务(FastAPI版本)")
print("="*50)

import uvicorn

if __name__ == "__main__":
    print("="*50)
    print("【启动】准备启动Web服务...")
    print("="*50)
    
    # 从环境变量获取端口号，默认为8000
    port = int(os.getenv('SERVER_PORT', 8000))
    print(f"【启动】服务将在端口 {port} 上启动")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
    
    print("【关闭】Web服务已关闭")