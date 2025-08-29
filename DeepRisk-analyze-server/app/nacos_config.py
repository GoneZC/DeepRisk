import logging
import json
from nacos import NacosClient
from app.config import Config

logger = logging.getLogger(__name__)

class NacosConfigManager:
    def __init__(self):
        self.config = Config
        self.nacos_client = None
        self.config_data = {}
        self.init_nacos()
    
    def init_nacos(self):
        """初始化Nacos客户端"""
        try:
            nacos_config = self.config.NACOS
            self.nacos_client = NacosClient(
                server_addresses=nacos_config['server_addr'],
                namespace=nacos_config.get('namespace', None),
                username=nacos_config.get('username', None),
                password=nacos_config.get('password', None)
            )
            
            # 获取初始配置
            self.load_config()
            
            # 添加配置监听
            if nacos_config.get('enable_remote_config', False):
                self.add_config_listener()
                
            logger.info("Nacos配置管理器初始化成功")
        except Exception as e:
            logger.error(f"Nacos配置管理器初始化失败: {str(e)}")

    def load_config(self):
        """从Nacos加载配置"""
        try:
            nacos_config = self.config.NACOS
            data_id = nacos_config.get('data_id', 'analysis-service')
            group = nacos_config.get('group', 'DEFAULT_GROUP')
            
            # 从Nacos获取配置
            config_content = self.nacos_client.get_config(
                data_id=data_id,
                group=group
            )
            
            if config_content:
                # 解析配置内容
                self.config_data = json.loads(config_content)
                logger.info(f"成功从Nacos加载配置: {data_id}")
            else:
                logger.warning(f"在Nacos中未找到配置: {data_id}")
                
        except Exception as e:
            logger.error(f"从Nacos加载配置失败: {str(e)}")
    
    def add_config_listener(self):
        """添加配置监听器"""
        try:
            nacos_config = self.config.NACOS
            data_id = nacos_config.get('data_id', 'analysis-service')
            group = nacos_config.get('group', 'DEFAULT_GROUP')
            
            # 添加监听器
            self.nacos_client.add_config_watchers(
                data_id=data_id,
                group=group,
                cb=self.config_change_callback
            )
            
            logger.info(f"已添加配置监听器: {data_id}")
        except Exception as e:
            logger.error(f"添加配置监听器失败: {str(e)}")
    
    def config_change_callback(self, *args, **kwargs):
        """配置变更回调函数"""
        try:
            logger.info("检测到Nacos配置变更")
            self.load_config()
            # 在这里可以添加配置变更后的处理逻辑
            self.apply_config_changes()
        except Exception as e:
            logger.error(f"配置变更处理失败: {str(e)}")
    
    def apply_config_changes(self):
        """应用配置变更"""
        # 这里可以添加配置变更后需要执行的逻辑
        logger.info("应用配置变更完成")
    
    def get_config_value(self, key, default=None):
        """获取配置值"""
        return self.config_data.get(key, default)
    
    def get_all_config(self):
        """获取所有配置"""
        return self.config_data

# 全局配置管理器实例
nacos_config_manager = NacosConfigManager()