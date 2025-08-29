import sys
import os
import numpy as np

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_encoder():
    """测试编码器功能"""
    print("测试编码器功能...")
    
    # 导入必要的模块
    from app.models.model_loader import load_models, get_encoder
    from app.rabbitmq.consumer import RiskAssessmentConsumer
    
    # 加载模型
    print("加载模型...")
    load_models()
    
    # 获取编码器
    encoder, scaler = get_encoder()
    if encoder is None or scaler is None:
        print("错误：编码器加载失败")
        return False
    
    print("编码器加载成功")
    
    # 创建消费者实例
    consumer = RiskAssessmentConsumer()
    
    # 测试向量编码
    print("\n测试35维向量编码为128维向量...")
    
    # 生成测试向量
    test_vector = np.random.randn(35)
    print(f"输入向量维度: {test_vector.shape}")
    print(f"输入向量示例前5个元素: {test_vector[:5]}")
    
    # 编码向量
    encoded_vector = consumer._encode_vector(test_vector)
    
    if encoded_vector is not None:
        print(f"输出向量维度: {encoded_vector.shape}")
        print(f"输出向量示例前5个元素: {encoded_vector[:5]}")
        print("编码器测试成功!")
        return True
    else:
        print("编码器测试失败!")
        return False

if __name__ == "__main__":
    success = test_encoder()
    if not success:
        sys.exit(1)