import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class LSTMSequenceAnalyzer(nn.Module):
    """
    基于LSTM的时序风险分析器
    
    应用场景：
    - 用户行为时序模式分析
    - 交易频率异常检测
    - 操作习惯变化监控
    
    技术特点：
    - 双向LSTM捕获前后文信息
    - 多头注意力机制突出关键时间点
    - 自适应序列长度处理
    """
    
    def __init__(self, input_dim: int = 35, hidden_dim: int = 128, num_layers: int = 3, output_dim: int = 256):
        super(LSTMSequenceAnalyzer, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.output_dim = output_dim
        
        # 输入特征预处理
        self.input_projection = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        # 双向LSTM层 - 捕获时序依赖
        self.lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0,
            bidirectional=True
        )
        
        # 时序注意力机制
        self.temporal_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim * 2,  # 双向LSTM输出
            num_heads=8,
            dropout=0.1,
            batch_first=True
        )
        
        # 时序特征提取器
        self.temporal_extractor = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        # 异常检测分支
        self.anomaly_detector = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
        
        # 风险等级分类分支
        self.risk_classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, 3)  # 低、中、高风险
        )
        
        # 最终特征融合
        self.feature_fusion = nn.Sequential(
            nn.Linear(hidden_dim, output_dim),
            nn.LayerNorm(output_dim),
            nn.Tanh()
        )
        
    def forward(self, x: torch.Tensor, sequence_lengths: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """
        前向传播
        
        Args:
            x: 输入序列 [batch_size, seq_len, input_dim]
            sequence_lengths: 实际序列长度 [batch_size]
            
        Returns:
            包含多种分析结果的字典
        """
        batch_size, seq_len, _ = x.size()
        
        # 输入特征投影
        projected_input = self.input_projection(x)
        
        # LSTM时序编码
        lstm_out, (hidden, cell) = self.lstm(projected_input)
        
        # 时序注意力机制
        attended_out, attention_weights = self.temporal_attention(
            lstm_out, lstm_out, lstm_out
        )
        
        # 序列池化 - 考虑实际长度
        if sequence_lengths is not None:
            # 创建掩码
            mask = torch.arange(seq_len).expand(batch_size, seq_len).to(x.device)
            mask = mask < sequence_lengths.unsqueeze(1)
            
            # 应用掩码
            attended_out = attended_out * mask.unsqueeze(-1).float()
            
            # 加权平均池化
            pooled_output = attended_out.sum(dim=1) / sequence_lengths.unsqueeze(-1).float()
        else:
            # 简单平均池化
            pooled_output = attended_out.mean(dim=1)
        
        # 时序特征提取
        temporal_features = self.temporal_extractor(pooled_output)
        
        # 异常检测
        anomaly_score = self.anomaly_detector(temporal_features)
        
        # 风险分类
        risk_logits = self.risk_classifier(temporal_features)
        risk_probs = F.softmax(risk_logits, dim=-1)
        
        # 最终特征融合
        sequence_embedding = self.feature_fusion(temporal_features)
        
        return {
            'sequence_embedding': sequence_embedding,
            'temporal_features': temporal_features,
            'anomaly_score': anomaly_score,
            'risk_logits': risk_logits,
            'risk_probs': risk_probs,
            'attention_weights': attention_weights,
            'lstm_output': lstm_out
        }
    
    def detect_pattern_change(self, x: torch.Tensor, baseline_embedding: torch.Tensor) -> torch.Tensor:
        """
        检测行为模式变化
        
        Args:
            x: 当前序列
            baseline_embedding: 基线行为模式
            
        Returns:
            模式变化程度 [batch_size, 1]
        """
        outputs = self.forward(x)
        current_embedding = outputs['sequence_embedding']
        
        # 计算余弦相似度
        similarity = F.cosine_similarity(current_embedding, baseline_embedding, dim=-1)
        
        # 转换为变化程度（1 - 相似度）
        pattern_change = 1 - similarity
        
        return pattern_change.unsqueeze(-1)


class SequenceRiskDetector:
    """
    时序风险检测器
    
    专门用于分析用户行为的时间序列特征
    适用于需要捕获时序依赖关系的风险检测场景
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_config = model_config
        
        # 初始化LSTM序列分析器
        self.lstm_analyzer = LSTMSequenceAnalyzer(
            input_dim=model_config.get('input_dim', 35),
            hidden_dim=model_config.get('hidden_dim', 128),
            num_layers=model_config.get('num_layers', 3),
            output_dim=model_config.get('output_dim', 256)
        ).to(self.device)
        
        # 基线行为模式存储
        self.baseline_patterns = {}
        
        logger.info(f"LSTM时序风险检测器已初始化，设备: {self.device}")
    
    def analyze_sequence(self, sequences: np.ndarray, sequence_lengths: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        分析时序数据
        
        Args:
            sequences: 时序数据 [batch_size, seq_len, input_dim]
            sequence_lengths: 实际序列长度
            
        Returns:
            时序分析结果
        """
        self.lstm_analyzer.eval()
        
        with torch.no_grad():
            # 转换为张量
            x = torch.FloatTensor(sequences).to(self.device)
            
            if sequence_lengths is not None:
                seq_lens = torch.LongTensor(sequence_lengths).to(self.device)
            else:
                seq_lens = None
            
            # LSTM分析
            outputs = self.lstm_analyzer(x, seq_lens)
            
            # 提取结果
            results = {
                'sequence_embedding': outputs['sequence_embedding'].cpu().numpy(),
                'temporal_features': outputs['temporal_features'].cpu().numpy(),
                'anomaly_scores': outputs['anomaly_score'].cpu().numpy(),
                'risk_probabilities': outputs['risk_probs'].cpu().numpy(),
                'attention_weights': outputs['attention_weights'].cpu().numpy()
            }
            
            # 计算风险分数
            risk_probs = outputs['risk_probs'].cpu().numpy()
            results['risk_scores'] = {
                'low_risk': risk_probs[:, 0],
                'medium_risk': risk_probs[:, 1],
                'high_risk': risk_probs[:, 2],
                'overall_risk': risk_probs[:, 1] + risk_probs[:, 2],
                'anomaly_risk': outputs['anomaly_score'].cpu().numpy().flatten()
            }
            
            return results
    
    def detect_behavioral_anomaly(self, sequences: np.ndarray, user_id: str = None) -> Dict[str, Any]:
        """
        检测行为异常
        
        Args:
            sequences: 用户行为序列
            user_id: 用户ID（用于获取基线模式）
            
        Returns:
            异常检测结果
        """
        analysis_results = self.analyze_sequence(sequences)
        
        # 如果有用户基线模式，计算偏差
        if user_id and user_id in self.baseline_patterns:
            baseline = self.baseline_patterns[user_id]
            
            with torch.no_grad():
                x = torch.FloatTensor(sequences).to(self.device)
                baseline_tensor = torch.FloatTensor(baseline).to(self.device)
                
                pattern_change = self.lstm_analyzer.detect_pattern_change(x, baseline_tensor)
                analysis_results['pattern_change_score'] = pattern_change.cpu().numpy()
        
        return analysis_results
    
    def update_baseline_pattern(self, user_id: str, sequences: np.ndarray):
        """
        更新用户基线行为模式
        
        Args:
            user_id: 用户ID
            sequences: 正常行为序列
        """
        analysis_results = self.analyze_sequence(sequences)
        
        # 计算平均嵌入作为基线
        baseline_embedding = analysis_results['sequence_embedding'].mean(axis=0)
        self.baseline_patterns[user_id] = baseline_embedding
        
        logger.info(f"用户 {user_id} 的基线行为模式已更新")
    
    def analyze_temporal_patterns(self, sequences: np.ndarray) -> Dict[str, Any]:
        """
        分析时序模式
        
        Args:
            sequences: 时序数据
            
        Returns:
            时序模式分析结果
        """
        results = self.analyze_sequence(sequences)
        
        # 分析注意力权重以识别关键时间点
        attention_weights = results['attention_weights']
        
        # 计算每个时间步的重要性
        temporal_importance = attention_weights.mean(axis=(0, 1))  # 平均所有样本和注意力头
        
        # 识别异常时间点
        importance_threshold = np.percentile(temporal_importance, 80)
        critical_timepoints = np.where(temporal_importance > importance_threshold)[0]
        
        results['temporal_analysis'] = {
            'temporal_importance': temporal_importance,
            'critical_timepoints': critical_timepoints,
            'pattern_stability': 1 - np.std(temporal_importance)
        }
        
        return results
    
    def load_model(self, model_path: str):
        """加载预训练模型"""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.lstm_analyzer.load_state_dict(checkpoint['model_state_dict'])
            
            # 加载基线模式（如果存在）
            if 'baseline_patterns' in checkpoint:
                self.baseline_patterns = checkpoint['baseline_patterns']
            
            logger.info(f"LSTM时序模型加载成功: {model_path}")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def save_model(self, save_path: str):
        """保存模型"""
        try:
            torch.save({
                'model_state_dict': self.lstm_analyzer.state_dict(),
                'model_config': self.model_config,
                'baseline_patterns': self.baseline_patterns
            }, save_path)
            logger.info(f"LSTM时序模型已保存: {save_path}")
        except Exception as e:
            logger.error(f"模型保存失败: {e}")
            raise