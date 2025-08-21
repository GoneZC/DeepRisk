import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app/models'))

from app import create_app
# 不再导入start_consumer_thread，因为consumer已在app/__init__.py中初始化

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
logging.getLogger('werkzeug').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

print("="*50)
print("【启动】开始启动深度分析服务")
print("="*50)

print("【启动】创建Flask应用实例...")
app = create_app()
print("【启动】Flask应用创建完成")

if __name__ == "__main__":
    print("="*50)
    print("【启动】进入应用主函数")
    print("【启动】准备启动消费者线程...")
    
    # 消费者线程已在app创建过程中启动，无需重复启动
    print("【启动】消费者线程已启动，准备启动Web服务...")
    print("="*50)
    
    # 禁用 reloader 以避免重复启动
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    print("【关闭】Web服务已关闭") 