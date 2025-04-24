import os
import pickle
import torch
from deepod.models import DeepSVDD
import numpy as np
import json
import joblib
from sklearn.preprocessing import StandardScaler

# 全局变量存储模型和参数
_models = {}
_scalers = {}
_feature_cols = {}
_is_loaded = False
_thresholds = {}  # 添加阈值缓存

# 获取model_loader.py文件所在的目录绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 基础路径
MODEL_BASE_PATH = os.path.join(os.path.dirname(__file__), 'svdd')
SCALER_BASE_PATH = os.path.join(os.path.dirname(__file__), 'scalers')
THRESHOLD_PATH = os.path.join(os.path.dirname(__file__), 'risk_thresholds.json')

def load_models():
    """加载所有模型和参数"""
    global _models, _scalers, _feature_cols, _is_loaded
    
    if _is_loaded:
        return
    
    print("加载深度学习模型...")
    
    # 设备配置
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")
    
    # 加载所有模型和参数
    for model_type in ['fee', 'drug', 'diag']:
        try:
            # 加载模型
            model_path = os.path.join(current_dir, f'{model_type}_dsvdd_model.pth')
            _models[model_type] = DeepSVDD.load(model_path, device)
            
            # 加载归一化参数
            scaler_path = os.path.join(current_dir, f'{model_type}_scaler.pkl')
            with open(scaler_path, 'rb') as f:
                _scalers[model_type] = pickle.load(f)
                
            # 加载特征列
            cols_path = os.path.join(current_dir, f'{model_type}_feature_cols.pkl')
            with open(cols_path, 'rb') as f:
                _feature_cols[model_type] = pickle.load(f)
                
            print(f"{model_type}模型和参数加载成功")
        except Exception as e:
            print(f"加载{model_type}模型失败: {e}")
            _models[model_type] = None
    
    # 加载风险阈值
    try:
        threshold_path = os.path.join(current_dir, 'risk_thresholds.json')
        if os.path.exists(threshold_path):
            with open(threshold_path, 'r') as f:
                _thresholds = json.load(f)
            print("风险阈值加载成功")
        else:
            print("风险阈值文件不存在，使用默认值")
            _thresholds = {
                "fee_score": {"low": 50, "high": 75},
                "drug_score": {"low": 50, "high": 75},
                "diag_score": {"low": 50, "high": 75},
                "combined_score": {"low": 50, "high": 75}
            }
    except Exception as e:
        print(f"加载风险阈值失败: {e}")
    
    _is_loaded = True
    print("模型加载完成")

def get_models():
    """获取已加载的模型"""
    global _models, _is_loaded
    if not _is_loaded:
        load_models()
    return _models

def get_scalers():
    """获取已加载的归一化器"""
    global _scalers, _is_loaded
    if not _is_loaded:
        load_models()
    return _scalers

def get_feature_cols():
    """获取已加载的特征列"""
    global _feature_cols, _is_loaded
    if not _is_loaded:
        load_models()
    return _feature_cols

# 添加此函数加载风险阈值
def load_thresholds():
    """加载风险阈值"""
    global _thresholds
    
    if not _thresholds:
        try:
            print(f"从文件加载风险阈值: {THRESHOLD_PATH}")
            with open(THRESHOLD_PATH, 'r') as f:
                _thresholds = json.load(f)
            print(f"成功加载风险阈值: {list(_thresholds.keys())}")
        except Exception as e:
            print(f"加载风险阈值失败: {e}")
            _thresholds = {}
    
    return _thresholds

# 预加载阈值
_thresholds = load_thresholds() 