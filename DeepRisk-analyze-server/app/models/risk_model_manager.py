import torch
import numpy as np
from typing import Dict, Any, Optional, List
import logging
import json
from pathlib import Path

# 导入三个专门的风险检测模块
from .bert_risk_encoder import BertRiskDetector
from .lstm_sequence_analyzer import SequenceRiskDetector
from .gcn_graph_analyzer import GraphRiskDetector

logger = logging.getLogger(__name__)

class RiskModelManager:
    """
    风险模型管理器
    
    统一管理三种不同场景的风险检测模型：
    1. BERT风险编码器 - 用户画像和特征语义理解
    2. LSTM序列分析器 - 时序行为模式分析
    3. GCN图网络分析器 - 关系网络风险传播
    
    支持单独使用或组合使用多种模型进行综合风险评估
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 加载配置
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self._get_default_config()
        
        # 初始化三个专门的检测器
        self.bert_detector = None
        self.lstm_detector = None
        self.gcn_detector = None
        
        # 模型状态
        self.models_loaded = {
            'bert': False,
            'lstm': False,
            'gcn': False
        }
        
        logger.info(f"风险模型管理器已初始化，设备: {self.device}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'bert_config': {
                'input_dim': 35,
                'hidden_dim': 768,
                'output_dim': 256
            },
            'lstm_config': {
                'input_dim': 35,
                'hidden_dim': 128,
                'num_layers': 3,
                'output_dim': 256
            },
            'gcn_config': {
                'input_dim': 35,
                'hidden_dim': 128,
                'output_dim': 256,
                'num_layers': 3
            },
            'fusion_weights': {
                'bert': 0.4,
                'lstm': 0.3,
                'gcn': 0.3
            }
        }
    
    def initialize_bert_detector(self) -> bool:
        """
        初始化BERT风险检测器
        
        Returns:
            初始化是否成功
        """
        try:
            self.bert_detector = BertRiskDetector(self.config['bert_config'])
            self.models_loaded['bert'] = True
            logger.info("BERT风险检测器初始化成功")
            return True
        except Exception as e:
            logger.error(f"BERT风险检测器初始化失败: {e}")
            return False
    
    def initialize_lstm_detector(self) -> bool:
        """
        初始化LSTM序列分析器
        
        Returns:
            初始化是否成功
        """
        try:
            self.lstm_detector = SequenceRiskDetector(self.config['lstm_config'])
            self.models_loaded['lstm'] = True
            logger.info("LSTM序列分析器初始化成功")
            return True
        except Exception as e:
            logger.error(f"LSTM序列分析器初始化失败: {e}")
            return False
    
    def initialize_gcn_detector(self) -> bool:
        """
        初始化GCN图网络分析器
        
        Returns:
            初始化是否成功
        """
        try:
            self.gcn_detector = GraphRiskDetector(self.config['gcn_config'])
            self.models_loaded['gcn'] = True
            logger.info("GCN图网络分析器初始化成功")
            return True
        except Exception as e:
            logger.error(f"GCN图网络分析器初始化失败: {e}")
            return False
    
    def initialize_all_detectors(self) -> Dict[str, bool]:
        """
        初始化所有检测器
        
        Returns:
            各检测器初始化状态
        """
        results = {
            'bert': self.initialize_bert_detector(),
            'lstm': self.initialize_lstm_detector(),
            'gcn': self.initialize_gcn_detector()
        }
        
        logger.info(f"检测器初始化完成: {results}")
        return results
    
    def predict_user_profile_risk(self, user_features: np.ndarray) -> Dict[str, Any]:
        """
        用户画像风险评估（使用BERT模型）
        
        Args:
            user_features: 用户特征 [batch_size, feature_dim]
            
        Returns:
            用户画像风险评估结果
        """
        if not self.models_loaded['bert']:
            if not self.initialize_bert_detector():
                raise RuntimeError("BERT检测器未能成功初始化")
        
        results = self.bert_detector.predict_risk(user_features)
        results['model_type'] = 'bert_user_profile'
        results['scenario'] = '用户画像风险评估'
        
        return results
    
    def analyze_behavioral_sequence(self, sequences: np.ndarray, 
                                  sequence_lengths: Optional[np.ndarray] = None,
                                  user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        行为序列风险分析（使用LSTM模型）
        
        Args:
            sequences: 行为序列 [batch_size, seq_len, feature_dim]
            sequence_lengths: 实际序列长度
            user_id: 用户ID（用于基线比较）
            
        Returns:
            行为序列风险分析结果
        """
        if not self.models_loaded['lstm']:
            if not self.initialize_lstm_detector():
                raise RuntimeError("LSTM检测器未能成功初始化")
        
        if user_id:
            results = self.lstm_detector.detect_behavioral_anomaly(sequences, user_id)
        else:
            results = self.lstm_detector.analyze_sequence(sequences, sequence_lengths)
        
        results['model_type'] = 'lstm_sequence'
        results['scenario'] = '行为序列风险分析'
        
        return results
    
    def analyze_relationship_network(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        关系网络风险分析（使用GCN模型）
        
        Args:
            graph_data: 图数据
            
        Returns:
            关系网络风险分析结果
        """
        if not self.models_loaded['gcn']:
            if not self.initialize_gcn_detector():
                raise RuntimeError("GCN检测器未能成功初始化")
        
        results = self.gcn_detector.analyze_graph_risk(graph_data)
        results['model_type'] = 'gcn_graph'
        results['scenario'] = '关系网络风险分析'
        
        return results
    
    def comprehensive_risk_assessment(self, 
                                    user_features: Optional[np.ndarray] = None,
                                    sequences: Optional[np.ndarray] = None,
                                    graph_data: Optional[Dict[str, Any]] = None,
                                    **kwargs) -> Dict[str, Any]:
        """
        综合风险评估（融合多种模型）
        
        Args:
            user_features: 用户特征（BERT输入）
            sequences: 行为序列（LSTM输入）
            graph_data: 图数据（GCN输入）
            **kwargs: 其他参数
            
        Returns:
            综合风险评估结果
        """
        results = {
            'individual_results': {},
            'fusion_result': {},
            'model_availability': self.models_loaded.copy()
        }
        
        risk_scores = []
        model_weights = []
        
        # BERT用户画像分析
        if user_features is not None and self.models_loaded['bert']:
            try:
                bert_result = self.predict_user_profile_risk(user_features)
                results['individual_results']['bert'] = bert_result
                
                # 提取风险分数
                bert_risk = np.mean(bert_result['risk_scores']['overall_risk'])
                risk_scores.append(bert_risk)
                model_weights.append(self.config['fusion_weights']['bert'])
                
            except Exception as e:
                logger.error(f"BERT分析失败: {e}")
        
        # LSTM序列分析
        if sequences is not None and self.models_loaded['lstm']:
            try:
                lstm_result = self.analyze_behavioral_sequence(
                    sequences, 
                    kwargs.get('sequence_lengths'),
                    kwargs.get('user_id')
                )
                results['individual_results']['lstm'] = lstm_result
                
                # 提取风险分数
                lstm_risk = np.mean(lstm_result['risk_scores']['overall_risk'])
                risk_scores.append(lstm_risk)
                model_weights.append(self.config['fusion_weights']['lstm'])
                
            except Exception as e:
                logger.error(f"LSTM分析失败: {e}")
        
        # GCN图网络分析
        if graph_data is not None and self.models_loaded['gcn']:
            try:
                gcn_result = self.analyze_relationship_network(graph_data)
                results['individual_results']['gcn'] = gcn_result
                
                # 提取风险分数
                gcn_risk = np.mean(gcn_result['risk_scores']['graph_risks']['overall_risk'])
                risk_scores.append(gcn_risk)
                model_weights.append(self.config['fusion_weights']['gcn'])
                
            except Exception as e:
                logger.error(f"GCN分析失败: {e}")
        
        # 融合多模型结果
        if risk_scores:
            # 加权平均
            total_weight = sum(model_weights)
            if total_weight > 0:
                normalized_weights = [w / total_weight for w in model_weights]
                fused_risk_score = sum(score * weight for score, weight in zip(risk_scores, normalized_weights))
            else:
                fused_risk_score = np.mean(risk_scores)
            
            # 风险等级判断
            if fused_risk_score < 0.3:
                risk_level = 'low'
            elif fused_risk_score < 0.7:
                risk_level = 'medium'
            else:
                risk_level = 'high'
            
            results['fusion_result'] = {
                'overall_risk_score': fused_risk_score,
                'risk_level': risk_level,
                'individual_scores': risk_scores,
                'model_weights': normalized_weights if 'normalized_weights' in locals() else model_weights,
                'models_used': len(risk_scores)
            }
        else:
            results['fusion_result'] = {
                'error': '没有可用的模型结果进行融合',
                'overall_risk_score': 0.0,
                'risk_level': 'unknown'
            }
        
        return results
    
    def get_model_status(self) -> Dict[str, Any]:
        """
        获取模型状态信息
        
        Returns:
            模型状态信息
        """
        return {
            'models_loaded': self.models_loaded,
            'device': str(self.device),
            'config': self.config,
            'available_scenarios': {
                'bert': '用户画像风险评估',
                'lstm': '行为序列风险分析',
                'gcn': '关系网络风险分析'
            }
        }
    
    def load_pretrained_models(self, model_paths: Dict[str, str]):
        """
        加载预训练模型
        
        Args:
            model_paths: 模型路径字典 {'bert': path, 'lstm': path, 'gcn': path}
        """
        for model_type, path in model_paths.items():
            if not Path(path).exists():
                logger.warning(f"模型文件不存在: {path}")
                continue
            
            try:
                if model_type == 'bert' and self.bert_detector:
                    self.bert_detector.load_model(path)
                elif model_type == 'lstm' and self.lstm_detector:
                    self.lstm_detector.load_model(path)
                elif model_type == 'gcn' and self.gcn_detector:
                    self.gcn_detector.load_model(path)
                
                logger.info(f"{model_type.upper()}模型加载成功: {path}")
            except Exception as e:
                logger.error(f"{model_type.upper()}模型加载失败: {e}")
    



# 便捷函数
def create_risk_manager(config_path: Optional[str] = None) -> RiskModelManager:
    """
    创建风险模型管理器的便捷函数
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        风险模型管理器实例
    """
    manager = RiskModelManager(config_path)
    manager.initialize_all_detectors()
    return manager


def quick_risk_assessment(user_features: np.ndarray, 
                         sequences: Optional[np.ndarray] = None,
                         graph_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    快速风险评估的便捷函数
    
    Args:
        user_features: 用户特征
        sequences: 行为序列（可选）
        graph_data: 图数据（可选）
        
    Returns:
        风险评估结果
    """
    manager = create_risk_manager()
    return manager.comprehensive_risk_assessment(
        user_features=user_features,
        sequences=sequences,
        graph_data=graph_data
    )