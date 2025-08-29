import os
import pickle
import torch
import logging
from sklearn.preprocessing import StandardScaler

# 配置日志
logger = logging.getLogger(__name__)

# 定义模型文件路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_DIR = os.path.join(BASE_DIR, 'data', 'models')

# 全局变量存储加载的模型
_loaded_models = {}
_encoder = None
_scaler = None
_thresholds = {}
models_loaded = False  # 添加模型加载状态标志

def load_models():
    """加载所有深度学习模型"""
    global _loaded_models, _encoder, _scaler, _thresholds, models_loaded
    
    logger.info("加载深度学习模型...")
    print("[模型] 开始加载深度学习模型...")
    
    try:
        # 加载编码器模型和标准化器
        encoder_path = os.path.join(MODEL_DIR, 'encoder_35_to_128.pkl')
        scaler_path = os.path.join(MODEL_DIR, 'encoder_35_to_128_scaler.pkl')
        
        print(f"[模型] 编码器模型路径: {encoder_path}")
        print(f"[模型] 标准化器路径: {scaler_path}")
        
        if os.path.exists(encoder_path):
            print("[模型] 开始加载编码器模型...")
            loaded_obj = torch.load(encoder_path, map_location='cpu')
            print(f"[模型] 加载的对象类型: {type(loaded_obj)}")
            
            # 检查是否是OrderedDict（状态字典），如果是则需要创建模型实例并加载状态
            if isinstance(loaded_obj, dict) or str(type(loaded_obj)) == "<class 'collections.OrderedDict'>":
                print("[模型] 检测到状态字典，需要创建模型实例")
                try:
                    # 导入正确的模型结构
                    from torch import nn
                    
                    # 定义编码器模型结构（与训练时保持一致）
                    class Encoder(nn.Module):
                        """编码器网络：将35维数据映射到128维"""
                        def __init__(self, input_dim=35, hidden_dim=64, latent_dim=128):
                            super(Encoder, self).__init__()
                            
                            self.encoder = nn.Sequential(
                                nn.Linear(input_dim, hidden_dim),
                                nn.ReLU(),
                                nn.Linear(hidden_dim, hidden_dim*2),
                                nn.ReLU(),
                                nn.Linear(hidden_dim*2, latent_dim),
                                nn.ReLU()
                            )
                            
                        def forward(self, x):
                            return self.encoder(x)
                    
                    # 创建模型实例并加载状态字典
                    _encoder = Encoder()
                    _encoder.load_state_dict(loaded_obj)
                    _encoder.eval()  # 设置为评估模式
                    print("[模型] 成功从状态字典创建模型实例")
                except Exception as e:
                    print(f"[模型] 从状态字典创建模型实例失败: {e}")
                    import traceback
                    traceback.print_exc()
                    _encoder = loaded_obj  # 回退到原始对象
            else:
                _encoder = loaded_obj
                print("[模型] 直接使用加载的对象作为模型")
            
            print(f"[模型] 编码器模型加载成功: {_encoder}")
            logger.info("编码器模型加载成功")
        else:
            print(f"[模型] 编码器模型文件不存在: {encoder_path}")
            logger.warning(f"编码器模型文件不存在: {encoder_path}")
            
        if os.path.exists(scaler_path):
            print("[模型] 开始加载标准化器...")
            with open(scaler_path, 'rb') as f:
                _scaler = pickle.load(f)
            print(f"[模型] 标准化器加载成功: {_scaler}")
            logger.info("编码器标准化器加载成功")
        else:
            print(f"[模型] 编码器标准化器文件不存在: {scaler_path}")
            logger.warning(f"编码器标准化器文件不存在: {scaler_path}")
        
        print(f"[模型] 当前编码器: {_encoder}, 当前标准化器: {_scaler}")
        
        # 加载费用异常检测模型
        try:
            from app.models.deepod.models.tabular import DeepSVDD
            fee_model_path = os.path.join(MODEL_DIR, 'fee_dsvdd_model.pth')
            if os.path.exists(fee_model_path):
                # 这里应该加载模型，但DeepSVDD没有load方法
                # fee_model = DeepSVDD.load(fee_model_path)
                # _loaded_models['fee'] = fee_model
                logger.warning("加载fee模型失败: type object 'DeepSVDD' has no attribute 'load'")
        except Exception as e:
            logger.warning(f"加载费用异常检测模型时出错: {e}")
        
        # 加载风险阈值
        threshold_path = os.path.join(MODEL_DIR, 'risk_thresholds.json')
        if os.path.exists(threshold_path):
            import json
            with open(threshold_path, 'r', encoding='utf-8') as f:
                _thresholds = json.load(f)
            logger.info("风险阈值加载成功")
        else:
            logger.warning(f"风险阈值文件不存在: {threshold_path}")
            
        logger.info("模型加载完成")
        print("[模型] 模型加载完成")
        
    except Exception as e:
        logger.error(f"加载模型时出错: {e}", exc_info=True)
        print(f"[模型] 加载模型时出错: {e}")

def get_encoder():
    """获取编码器模型和标准化器"""
    global _encoder, _scaler
    # 只在调试模式下打印详细日志
    if os.environ.get('DEBUG', '').lower() in ('1', 'true'):
        print(f"[模型] 获取编码器: encoder={_encoder is not None}, scaler={_scaler is not None}")
    return _encoder, _scaler

def get_models():
    """获取所有加载的模型"""
    global _loaded_models
    return _loaded_models

def get_scalers():
    """获取所有标准化器"""
    global _scaler
    return _scaler

def get_thresholds():
    """获取风险阈值"""
    global _thresholds
    return _thresholds