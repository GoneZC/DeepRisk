import torch
import torch.nn as nn
from transformers import BertModel, BertConfig
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BertRiskEncoder(nn.Module):
    """
    基于BERT的智能风险特征编码器
    
    应用场景：
    - 用户画像风险评估
    - 交易行为语义理解
    - 多维特征融合
    
    技术特点：
    - 基于BERT的语义编码
    - 结构化特征向量化
    - 多维特征关系建模
    """
    
    def __init__(self, input_dim: int = 35, hidden_dim: int = 768, output_dim: int = 256):
        super(BertRiskEncoder, self).__init__()
        
        # BERT配置 - 针对风险检测优化
        config = BertConfig(
            vocab_size=1000,
            hidden_size=hidden_dim,
            num_hidden_layers=6,
            num_attention_heads=12,
            intermediate_size=3072,
            max_position_embeddings=512,
            type_vocab_size=2,
            hidden_dropout_prob=0.1,
            attention_probs_dropout_prob=0.1
        )
        
        self.bert = BertModel(config)
        
        # 特征投影层 - 将原始特征映射到BERT空间
        self.feature_projection = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        # 风险特征提取层
        self.risk_extractor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LayerNorm(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        # 输出投影层
        self.output_projection = nn.Sequential(
            nn.Linear(hidden_dim // 2, output_dim),
            nn.LayerNorm(output_dim),
            nn.Tanh()
        )
        
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        前向传播
        
        Args:
            x: 输入特征张量 [batch_size, input_dim]
            
        Returns:
            包含多层特征表示的字典
        """
        batch_size = x.size(0)
        
        # 特征投影到BERT隐藏维度
        projected_features = self.feature_projection(x)
        
        # 添加序列维度用于BERT处理
        input_embeds = projected_features.unsqueeze(1)
        
        # BERT语义编码
        outputs = self.bert(inputs_embeds=input_embeds)
        pooled_output = outputs.pooler_output
        
        # 风险特征提取
        risk_features = self.risk_extractor(pooled_output)
        
        # 最终风险编码
        risk_embedding = self.output_projection(risk_features)
        
        return {
            'risk_embedding': risk_embedding,
            'semantic_features': pooled_output,
            'projected_features': projected_features,
            'attention_weights': outputs.attentions[-1] if outputs.attentions else None
        }
    
    def extract_risk_score(self, x: torch.Tensor) -> torch.Tensor:
        """
        直接提取风险分数
        
        Args:
            x: 输入特征
            
        Returns:
            风险分数 [batch_size, 1]
        """
        outputs = self.forward(x)
        risk_embedding = outputs['risk_embedding']
        
        # 简单的风险分数计算
        risk_score = torch.sigmoid(risk_embedding.mean(dim=-1, keepdim=True))
        return risk_score


class BertRiskDetector:
    """
    BERT风险检测器
    
    专门用于处理复杂的用户行为特征和交易模式识别
    适用于需要深度语义理解的风险检测场景
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_config = model_config
        
        # 初始化BERT风险编码器
        self.bert_encoder = BertRiskEncoder(
            input_dim=model_config.get('input_dim', 35),
            hidden_dim=model_config.get('hidden_dim', 768),
            output_dim=model_config.get('output_dim', 256)
        ).to(self.device)
        
        # 风险分类器
        self.risk_classifier = nn.Sequential(
            nn.Linear(model_config.get('output_dim', 256), 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 3)  # 低、中、高风险
        ).to(self.device)
        
        logger.info(f"BERT风险检测器已初始化，设备: {self.device}")
    
    def predict_risk(self, features: np.ndarray) -> Dict[str, Any]:
        """
        预测风险等级
        
        Args:
            features: 输入特征 [batch_size, input_dim]
            
        Returns:
            风险预测结果
        """
        self.bert_encoder.eval()
        self.risk_classifier.eval()
        
        with torch.no_grad():
            # 转换为张量
            x = torch.FloatTensor(features).to(self.device)
            
            # BERT编码
            bert_outputs = self.bert_encoder(x)
            risk_embedding = bert_outputs['risk_embedding']
            
            # 风险分类
            risk_logits = self.risk_classifier(risk_embedding)
            risk_probs = torch.softmax(risk_logits, dim=-1)
            
            # 计算综合风险分数
            risk_scores = {
                'low_risk': risk_probs[:, 0].cpu().numpy(),
                'medium_risk': risk_probs[:, 1].cpu().numpy(),
                'high_risk': risk_probs[:, 2].cpu().numpy(),
                'overall_risk': (risk_probs[:, 1] + risk_probs[:, 2]).cpu().numpy()
            }
            
            return {
                'risk_scores': risk_scores,
                'risk_embedding': risk_embedding.cpu().numpy(),
                'semantic_features': bert_outputs['semantic_features'].cpu().numpy(),
                'risk_probabilities': risk_probs.cpu().numpy()
            }
    
    def analyze_attention(self, features: np.ndarray) -> Dict[str, Any]:
        """
        分析注意力权重，解释模型决策
        
        Args:
            features: 输入特征
            
        Returns:
            注意力分析结果
        """
        self.bert_encoder.eval()
        
        with torch.no_grad():
            x = torch.FloatTensor(features).to(self.device)
            outputs = self.bert_encoder(x)
            
            attention_weights = outputs.get('attention_weights')
            if attention_weights is not None:
                # 平均所有注意力头的权重
                avg_attention = attention_weights.mean(dim=1).cpu().numpy()
                return {
                    'attention_weights': avg_attention,
                    'feature_importance': avg_attention.mean(axis=1)
                }
            
            return {'message': '注意力权重不可用'}
    
    def load_model(self, model_path: str):
        """加载预训练模型"""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.bert_encoder.load_state_dict(checkpoint['encoder_state_dict'])
            self.risk_classifier.load_state_dict(checkpoint['classifier_state_dict'])
            logger.info(f"BERT风险模型加载成功: {model_path}")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise