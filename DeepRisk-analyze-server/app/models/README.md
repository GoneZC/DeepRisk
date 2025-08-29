# DeepRisk 高级风险检测模型

本目录包含三个专门的深度学习风险检测模块，每个模块针对不同的应用场景进行了优化设计。

## 📋 模块概览

### 1. BERT风险编码器 (`bert_risk_encoder.py`)
**应用场景：用户画像与特征语义理解**

- 🎯 **主要用途**：
  - 用户画像风险评估
  - 交易行为语义理解
  - 多维特征深度融合

- 🔧 **技术特点**：
  - 基于BERT的强大语义理解能力
  - 将结构化风险特征转换为高维语义表示
  - 支持复杂特征关系建模
  - 提供注意力权重分析，增强模型可解释性

- 💡 **适用场景**：
  - 新用户风险评估
  - 用户信用评级
  - 复杂特征组合分析

### 2. LSTM时序分析器 (`lstm_sequence_analyzer.py`)
**应用场景：行为时序模式分析**

- 🎯 **主要用途**：
  - 用户行为时序模式分析
  - 交易频率异常检测
  - 操作习惯变化监控

- 🔧 **技术特点**：
  - 双向LSTM捕获前后文信息
  - 多头注意力机制突出关键时间点
  - 自适应序列长度处理
  - 支持基线行为模式比较

- 💡 **适用场景**：
  - 用户行为异常检测
  - 交易模式变化分析
  - 时间序列风险预警

### 3. GCN图网络分析器 (`gcn_graph_analyzer.py`)
**应用场景：关系网络风险传播**

- 🎯 **主要用途**：
  - 用户关系网络风险传播分析
  - 商户-用户交易网络异常检测
  - 设备指纹关联性分析

- 🔧 **技术特点**：
  - GCN + GAT双分支架构
  - 多层图卷积捕获复杂关系
  - 图级别和节点级别风险评估
  - 支持风险传播路径分析

- 💡 **适用场景**：
  - 团伙欺诈检测
  - 关联账户风险分析
  - 社交网络风险传播

## 🚀 快速开始

### 环境要求

```bash
# 基础依赖
pip install torch torchvision
pip install transformers
pip install numpy pandas

# GCN模块额外依赖
pip install torch-geometric
```

### 使用示例

#### 1. 单独使用BERT风险编码器

```python
from models.bert_risk_encoder import BertRiskDetector
import numpy as np

# 初始化检测器
config = {
    'input_dim': 35,
    'hidden_dim': 768,
    'output_dim': 256
}
bert_detector = BertRiskDetector(config)

# 用户特征风险评估
user_features = np.random.randn(10, 35)  # 10个用户，35维特征
results = bert_detector.predict_risk(user_features)

print(f"风险分数: {results['risk_scores']}")
print(f"风险等级: {results['risk_probabilities']}")
```

#### 2. 单独使用LSTM时序分析器

```python
from models.lstm_sequence_analyzer import SequenceRiskDetector
import numpy as np

# 初始化检测器
config = {
    'input_dim': 35,
    'hidden_dim': 128,
    'num_layers': 3,
    'output_dim': 256
}
lstm_detector = SequenceRiskDetector(config)

# 行为序列分析
sequences = np.random.randn(5, 20, 35)  # 5个用户，20个时间步，35维特征
results = lstm_detector.analyze_sequence(sequences)

print(f"序列风险分数: {results['risk_scores']}")
print(f"异常分数: {results['anomaly_scores']}")
```

#### 3. 单独使用GCN图网络分析器

```python
from models.gcn_graph_analyzer import GraphRiskDetector
import numpy as np

# 初始化检测器
config = {
    'input_dim': 35,
    'hidden_dim': 128,
    'output_dim': 256,
    'num_layers': 3
}
gcn_detector = GraphRiskDetector(config)

# 构建图数据
graph_data = {
    'node_features': np.random.randn(100, 35),  # 100个节点
    'edge_index': np.random.randint(0, 100, (2, 200))  # 200条边
}

results = gcn_detector.analyze_graph_risk(graph_data)
print(f"图风险分数: {results['risk_scores']}")
```

#### 4. 使用统一管理器进行综合分析

```python
from models.risk_model_manager import RiskModelManager
import numpy as np

# 创建管理器
manager = RiskModelManager()
manager.initialize_all_detectors()

# 准备多模态数据
user_features = np.random.randn(5, 35)
sequences = np.random.randn(5, 20, 35)
graph_data = {
    'node_features': np.random.randn(50, 35),
    'edge_index': np.random.randint(0, 50, (2, 100))
}

# 综合风险评估
results = manager.comprehensive_risk_assessment(
    user_features=user_features,
    sequences=sequences,
    graph_data=graph_data
)

print(f"综合风险评估: {results['fusion_result']}")
print(f"各模型结果: {results['individual_results'].keys()}")
```

## 📊 模型架构对比

| 模型 | 输入类型 | 主要技术 | 输出维度 | 适用场景 |
|------|----------|----------|----------|----------|
| BERT | 静态特征 | Transformer + 注意力 | 256 | 用户画像分析 |
| LSTM | 时序数据 | 双向LSTM + 注意力 | 256 | 行为模式分析 |
| GCN | 图结构 | 图卷积 + 图注意力 | 256 | 关系网络分析 |

## 🔧 配置说明

### BERT配置参数
```python
bert_config = {
    'input_dim': 35,        # 输入特征维度
    'hidden_dim': 768,      # BERT隐藏层维度
    'output_dim': 256       # 输出嵌入维度
}
```

### LSTM配置参数
```python
lstm_config = {
    'input_dim': 35,        # 输入特征维度
    'hidden_dim': 128,      # LSTM隐藏层维度
    'num_layers': 3,        # LSTM层数
    'output_dim': 256       # 输出嵌入维度
}
```

### GCN配置参数
```python
gcn_config = {
    'input_dim': 35,        # 节点特征维度
    'hidden_dim': 128,      # 图卷积隐藏维度
    'output_dim': 256,      # 图嵌入维度
    'num_layers': 3         # 图卷积层数
}
```

## 📈 性能优化建议

### 1. 硬件配置
- **GPU推荐**：NVIDIA RTX 3080或更高
- **内存要求**：至少16GB RAM
- **存储**：SSD存储以提高数据加载速度

### 2. 模型优化
- **批处理**：使用适当的batch_size以平衡速度和内存
- **混合精度**：使用FP16训练以节省内存
- **模型剪枝**：对于生产环境可考虑模型压缩

### 3. 数据预处理
- **特征标准化**：确保输入特征在合理范围内
- **序列填充**：LSTM模型需要统一序列长度
- **图构建优化**：合理设计图结构以避免过度连接

## 🛠️ 扩展开发

### 添加新的风险检测模块

1. 继承基础检测器接口
2. 实现特定的前向传播逻辑
3. 在`RiskModelManager`中注册新模块
4. 更新配置文件和文档

### 自定义损失函数

```python
class CustomRiskLoss(nn.Module):
    def __init__(self, alpha=0.5, beta=0.3):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        
    def forward(self, predictions, targets, weights=None):
        # 实现自定义损失逻辑
        pass
```

## 📝 注意事项

1. **依赖管理**：确保所有依赖包版本兼容
2. **内存管理**：大规模图数据可能导致内存不足
3. **模型保存**：定期保存训练好的模型权重
4. **日志记录**：启用详细日志以便调试
5. **安全考虑**：避免在日志中记录敏感信息

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这些模型！

1. Fork本项目
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。