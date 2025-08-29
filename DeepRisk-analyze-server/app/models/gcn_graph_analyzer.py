import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
import logging

# 注意：需要安装 torch-geometric
# pip install torch-geometric
try:
    from torch_geometric.nn import GCNConv, GATConv, GraphConv, global_mean_pool, global_max_pool
    from torch_geometric.data import Data, Batch
    TORCH_GEOMETRIC_AVAILABLE = True
except ImportError:
    TORCH_GEOMETRIC_AVAILABLE = False
    logging.warning("torch-geometric未安装，图网络功能将受限")

logger = logging.getLogger(__name__)

class GraphRiskAnalyzer(nn.Module):
    """
    基于图卷积网络的关系风险分析器
    
    应用场景：
    - 用户关系网络风险传播分析
    - 商户-用户交易网络异常检测
    - 设备指纹关联性分析
    
    技术特点：
    - GCN + GAT双分支架构
    - 多层图卷积捕获复杂关系
    - 图级别和节点级别风险评估
    """
    
    def __init__(self, input_dim: int = 35, hidden_dim: int = 128, output_dim: int = 256, num_layers: int = 3):
        super(GraphRiskAnalyzer, self).__init__()
        
        if not TORCH_GEOMETRIC_AVAILABLE:
            raise ImportError("需要安装torch-geometric: pip install torch-geometric")
        
        self.num_layers = num_layers
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # 节点特征预处理
        self.node_projection = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        # GCN分支 - 捕获局部邻域信息
        self.gcn_layers = nn.ModuleList()
        self.gcn_layers.append(GCNConv(hidden_dim, hidden_dim))
        
        for _ in range(num_layers - 2):
            self.gcn_layers.append(GCNConv(hidden_dim, hidden_dim))
        
        self.gcn_layers.append(GCNConv(hidden_dim, hidden_dim))
        
        # GAT分支 - 注意力机制捕获重要关系
        self.gat_layers = nn.ModuleList()
        self.gat_layers.append(GATConv(hidden_dim, hidden_dim // 8, heads=8, dropout=0.1))
        
        for _ in range(num_layers - 2):
            self.gat_layers.append(GATConv(hidden_dim, hidden_dim // 8, heads=8, dropout=0.1))
        
        self.gat_layers.append(GATConv(hidden_dim, hidden_dim, heads=1, dropout=0.1))
        
        # 特征融合层
        self.feature_fusion = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        # 节点风险预测器
        self.node_risk_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, 3)  # 低、中、高风险
        )
        
        # 图级别特征提取
        self.graph_feature_extractor = nn.Sequential(
            nn.Linear(hidden_dim * 2, output_dim),  # mean + max pooling
            nn.LayerNorm(output_dim),
            nn.Tanh()
        )
        
        # 关系强度预测器
        self.edge_predictor = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, 
                batch: Optional[torch.Tensor] = None, edge_attr: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """
        前向传播
        
        Args:
            x: 节点特征 [num_nodes, input_dim]
            edge_index: 边索引 [2, num_edges]
            batch: 批次索引 [num_nodes]
            edge_attr: 边属性 [num_edges, edge_dim]
            
        Returns:
            包含多种分析结果的字典
        """
        # 节点特征投影
        node_features = self.node_projection(x)
        
        # GCN分支处理
        gcn_x = node_features
        gcn_embeddings = []
        
        for i, layer in enumerate(self.gcn_layers):
            gcn_x = layer(gcn_x, edge_index)
            if i < len(self.gcn_layers) - 1:
                gcn_x = F.relu(gcn_x)
                gcn_x = self.dropout(gcn_x)
            gcn_embeddings.append(gcn_x)
        
        # GAT分支处理
        gat_x = node_features
        gat_embeddings = []
        gat_attention_weights = []
        
        for i, layer in enumerate(self.gat_layers):
            if i < len(self.gat_layers) - 1:
                gat_x, attention = layer(gat_x, edge_index, return_attention_weights=True)
                gat_attention_weights.append(attention)
                gat_x = F.relu(gat_x)
                gat_x = self.dropout(gat_x)
            else:
                gat_x = layer(gat_x, edge_index)
            gat_embeddings.append(gat_x)
        
        # 特征融合
        fused_features = torch.cat([gcn_x, gat_x], dim=-1)
        node_embeddings = self.feature_fusion(fused_features)
        
        # 节点风险预测
        node_risk_logits = self.node_risk_predictor(node_embeddings)
        node_risk_probs = F.softmax(node_risk_logits, dim=-1)
        
        # 图级别特征提取
        if batch is not None:
            # 批次图处理
            graph_mean = global_mean_pool(node_embeddings, batch)
            graph_max = global_max_pool(node_embeddings, batch)
        else:
            # 单图处理
            graph_mean = node_embeddings.mean(dim=0, keepdim=True)
            graph_max = node_embeddings.max(dim=0, keepdim=True)[0]
        
        graph_features = torch.cat([graph_mean, graph_max], dim=-1)
        graph_embedding = self.graph_feature_extractor(graph_features)
        
        # 边关系强度预测
        edge_strengths = None
        if edge_index.size(1) > 0:
            source_nodes = node_embeddings[edge_index[0]]
            target_nodes = node_embeddings[edge_index[1]]
            edge_features = torch.cat([source_nodes, target_nodes], dim=-1)
            edge_strengths = self.edge_predictor(edge_features)
        
        return {
            'node_embeddings': node_embeddings,
            'graph_embedding': graph_embedding,
            'node_risk_logits': node_risk_logits,
            'node_risk_probs': node_risk_probs,
            'edge_strengths': edge_strengths,
            'gcn_embeddings': gcn_embeddings,
            'gat_embeddings': gat_embeddings,
            'attention_weights': gat_attention_weights
        }
    
    def analyze_risk_propagation(self, x: torch.Tensor, edge_index: torch.Tensor, 
                                source_risks: torch.Tensor) -> torch.Tensor:
        """
        分析风险在图中的传播
        
        Args:
            x: 节点特征
            edge_index: 边索引
            source_risks: 源节点风险分数 [num_nodes, 1]
            
        Returns:
            传播后的风险分数
        """
        outputs = self.forward(x, edge_index)
        node_embeddings = outputs['node_embeddings']
        edge_strengths = outputs['edge_strengths']
        
        # 基于边强度的风险传播
        propagated_risks = source_risks.clone()
        
        if edge_strengths is not None:
            for i in range(edge_index.size(1)):
                source_idx, target_idx = edge_index[0, i], edge_index[1, i]
                edge_strength = edge_strengths[i]
                
                # 风险传播公式：目标风险 += 源风险 * 边强度 * 衰减因子
                propagated_risks[target_idx] += source_risks[source_idx] * edge_strength * 0.1
        
        return torch.clamp(propagated_risks, 0, 1)


class GraphRiskDetector:
    """
    图网络风险检测器
    
    专门用于分析复杂的实体关系网络
    适用于需要考虑实体间关联性的风险检测场景
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        if not TORCH_GEOMETRIC_AVAILABLE:
            raise ImportError("需要安装torch-geometric: pip install torch-geometric")
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_config = model_config
        
        # 初始化图风险分析器
        self.graph_analyzer = GraphRiskAnalyzer(
            input_dim=model_config.get('input_dim', 35),
            hidden_dim=model_config.get('hidden_dim', 128),
            output_dim=model_config.get('output_dim', 256),
            num_layers=model_config.get('num_layers', 3)
        ).to(self.device)
        
        # 图级别风险分类器
        self.graph_risk_classifier = nn.Sequential(
            nn.Linear(model_config.get('output_dim', 256), 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 3)  # 低、中、高风险
        ).to(self.device)
        
        logger.info(f"图网络风险检测器已初始化，设备: {self.device}")
    
    def analyze_graph_risk(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析图网络风险
        
        Args:
            graph_data: 图数据字典，包含:
                - node_features: 节点特征 [num_nodes, input_dim]
                - edge_index: 边索引 [2, num_edges]
                - edge_attr: 边属性（可选）
                - batch: 批次索引（可选）
                
        Returns:
            图风险分析结果
        """
        self.graph_analyzer.eval()
        self.graph_risk_classifier.eval()
        
        with torch.no_grad():
            # 转换为张量
            node_features = torch.FloatTensor(graph_data['node_features']).to(self.device)
            edge_index = torch.LongTensor(graph_data['edge_index']).to(self.device)
            
            edge_attr = None
            if 'edge_attr' in graph_data and graph_data['edge_attr'] is not None:
                edge_attr = torch.FloatTensor(graph_data['edge_attr']).to(self.device)
            
            batch = None
            if 'batch' in graph_data and graph_data['batch'] is not None:
                batch = torch.LongTensor(graph_data['batch']).to(self.device)
            
            # 图分析
            outputs = self.graph_analyzer(node_features, edge_index, batch, edge_attr)
            
            # 图级别风险分类
            graph_risk_logits = self.graph_risk_classifier(outputs['graph_embedding'])
            graph_risk_probs = F.softmax(graph_risk_logits, dim=-1)
            
            # 整理结果
            results = {
                'graph_embedding': outputs['graph_embedding'].cpu().numpy(),
                'node_embeddings': outputs['node_embeddings'].cpu().numpy(),
                'node_risk_probs': outputs['node_risk_probs'].cpu().numpy(),
                'graph_risk_probs': graph_risk_probs.cpu().numpy(),
                'edge_strengths': outputs['edge_strengths'].cpu().numpy() if outputs['edge_strengths'] is not None else None
            }
            
            # 计算各种风险分数
            node_risks = outputs['node_risk_probs'].cpu().numpy()
            graph_risks = graph_risk_probs.cpu().numpy()
            
            results['risk_scores'] = {
                'node_risks': {
                    'low_risk': node_risks[:, 0],
                    'medium_risk': node_risks[:, 1],
                    'high_risk': node_risks[:, 2],
                    'overall_risk': node_risks[:, 1] + node_risks[:, 2]
                },
                'graph_risks': {
                    'low_risk': graph_risks[:, 0],
                    'medium_risk': graph_risks[:, 1],
                    'high_risk': graph_risks[:, 2],
                    'overall_risk': graph_risks[:, 1] + graph_risks[:, 2]
                }
            }
            
            return results
    
    def detect_suspicious_subgraphs(self, graph_data: Dict[str, Any], risk_threshold: float = 0.7) -> Dict[str, Any]:
        """
        检测可疑子图
        
        Args:
            graph_data: 图数据
            risk_threshold: 风险阈值
            
        Returns:
            可疑子图检测结果
        """
        analysis_results = self.analyze_graph_risk(graph_data)
        
        # 识别高风险节点
        node_risks = analysis_results['risk_scores']['node_risks']['overall_risk']
        high_risk_nodes = np.where(node_risks > risk_threshold)[0]
        
        # 分析高风险节点的连接模式
        edge_index = graph_data['edge_index']
        suspicious_edges = []
        
        for i, (source, target) in enumerate(edge_index.T):
            if source in high_risk_nodes or target in high_risk_nodes:
                suspicious_edges.append(i)
        
        results = {
            'high_risk_nodes': high_risk_nodes.tolist(),
            'suspicious_edges': suspicious_edges,
            'subgraph_risk_score': np.mean(node_risks[high_risk_nodes]) if len(high_risk_nodes) > 0 else 0.0,
            'network_density': len(edge_index[0]) / (len(node_risks) * (len(node_risks) - 1)) if len(node_risks) > 1 else 0.0
        }
        
        return results
    
    def analyze_risk_propagation(self, graph_data: Dict[str, Any], source_risks: np.ndarray) -> Dict[str, Any]:
        """
        分析风险传播
        
        Args:
            graph_data: 图数据
            source_risks: 初始风险分数
            
        Returns:
            风险传播分析结果
        """
        self.graph_analyzer.eval()
        
        with torch.no_grad():
            node_features = torch.FloatTensor(graph_data['node_features']).to(self.device)
            edge_index = torch.LongTensor(graph_data['edge_index']).to(self.device)
            initial_risks = torch.FloatTensor(source_risks).to(self.device)
            
            # 风险传播分析
            propagated_risks = self.graph_analyzer.analyze_risk_propagation(
                node_features, edge_index, initial_risks
            )
            
            # 计算传播效应
            risk_increase = propagated_risks - initial_risks
            
            return {
                'initial_risks': initial_risks.cpu().numpy(),
                'propagated_risks': propagated_risks.cpu().numpy(),
                'risk_increase': risk_increase.cpu().numpy(),
                'propagation_intensity': torch.mean(risk_increase).item()
            }
    
    def build_graph_from_transactions(self, transactions: List[Dict]) -> Dict[str, Any]:
        """
        从交易数据构建图
        
        Args:
            transactions: 交易记录列表
            
        Returns:
            图数据
        """
        # 提取实体
        users = set()
        merchants = set()
        devices = set()
        
        for trans in transactions:
            users.add(trans.get('user_id'))
            merchants.add(trans.get('merchant_id'))
            if 'device_id' in trans:
                devices.add(trans['device_id'])
        
        # 创建节点映射
        all_entities = list(users) + list(merchants) + list(devices)
        entity_to_idx = {entity: idx for idx, entity in enumerate(all_entities)}
        
        # 构建边
        edges = []
        edge_attrs = []
        
        for trans in transactions:
            user_idx = entity_to_idx[trans['user_id']]
            merchant_idx = entity_to_idx[trans['merchant_id']]
            
            # 用户-商户边
            edges.append([user_idx, merchant_idx])
            edge_attrs.append([trans.get('amount', 0), trans.get('frequency', 1)])
            
            # 用户-设备边（如果有设备信息）
            if 'device_id' in trans:
                device_idx = entity_to_idx[trans['device_id']]
                edges.append([user_idx, device_idx])
                edge_attrs.append([1.0, 1.0])  # 设备关联强度
        
        # 创建节点特征（这里使用随机特征，实际应用中应该是真实特征）
        node_features = np.random.randn(len(all_entities), self.model_config.get('input_dim', 35))
        
        return {
            'node_features': node_features,
            'edge_index': np.array(edges).T,
            'edge_attr': np.array(edge_attrs),
            'entity_mapping': entity_to_idx,
            'entity_types': {
                'users': list(users),
                'merchants': list(merchants),
                'devices': list(devices)
            }
        }
    
    def load_model(self, model_path: str):
        """加载预训练模型"""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.graph_analyzer.load_state_dict(checkpoint['analyzer_state_dict'])
            self.graph_risk_classifier.load_state_dict(checkpoint['classifier_state_dict'])
            logger.info(f"图网络风险模型加载成功: {model_path}")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def save_model(self, save_path: str):
        """保存模型"""
        try:
            torch.save({
                'analyzer_state_dict': self.graph_analyzer.state_dict(),
                'classifier_state_dict': self.graph_risk_classifier.state_dict(),
                'model_config': self.model_config
            }, save_path)
            logger.info(f"图网络风险模型已保存: {save_path}")
        except Exception as e:
            logger.error(f"模型保存失败: {e}")
            raise