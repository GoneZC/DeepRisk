import numpy as np
import torch
import redis
import logging
import os
from typing import List, Dict, Tuple, Union
from app.models.model_loader import get_encoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class FraudDetectionCore:
    """风险检测核心模块"""
    
    def __init__(self, redis_host=None, redis_port=None):
        redis_host = redis_host or os.environ.get('REDIS_HOST') or 'localhost'
        redis_port = redis_port or int(os.environ.get('REDIS_PORT') or 6379)
        
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=0,
            decode_responses=False
        )
        
        try:
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self.redis_client = None
    
    def process_vector(self, vector_35d: Union[List[float], np.ndarray], entity_id: str) -> Dict:
        """
        处理35维向量，生成风险得分
        
        Args:
            vector_35d: 35维输入向量
            entity_id: 实体ID（用户、商户、员工等）
            
        Returns:
            包含风险得分和相关信息的字典
        """
        try:
            # 确保输入是numpy数组
            if not isinstance(vector_35d, np.ndarray):
                vector_35d = np.array(vector_35d, dtype=np.float32)
            
            # 检查向量维度
            if vector_35d.shape[0] != 35:
                raise ValueError(f"输入向量必须是35维，当前维度: {vector_35d.shape[0]}")
            
            # 使用神经网络将35维向量编码为128维向量
            vector_128d = self._encode_vector(vector_35d)
            if vector_128d is None:
                raise ValueError("向量编码失败")
            
            # 在Redis中执行Top-10相似度查询
            similar_entities = self._find_similar_entities(vector_128d, k=10)
            
            # 根据查询结果计算风险得分
            risk_score = self._calculate_risk_score(similar_entities)
            
            return {
                "entity_id": entity_id,
                "vector_35d": vector_35d.tolist(),
                "vector_128d": vector_128d.tolist(),
                "similar_entities": similar_entities,
                "risk_score": risk_score,
                "risk_level": self._get_risk_level(risk_score)
            }
            
        except Exception as e:
            logger.error(f"处理向量时出错: {e}")
            return {
                "entity_id": entity_id,
                "error": str(e),
                "risk_score": 0.0,
                "risk_level": "未知"
            }
    
    def process_vectors_batch(self, vectors_35d: List[np.ndarray], entity_ids: List[str]) -> List[Dict]:
        """
        批量处理35维向量，计算风险得分
        
        Args:
            vectors_35d: 35维输入向量列表
            entity_ids: 实体ID列表
            
        Returns:
            包含风险得分和相关信息的字典列表
        """
        try:
            if not vectors_35d or not entity_ids or len(vectors_35d) != len(entity_ids):
                raise ValueError("输入向量和实体ID列表不能为空，且长度必须相等")
            
            # 批量编码向量
            vectors_128d = self._batch_encode_vectors(vectors_35d)
            if vectors_128d is None:
                raise ValueError("向量批量编码失败")
            
            results = []
            # 对每个编码后的向量进行处理
            for i, vector_128d in enumerate(vectors_128d):
                if vector_128d is not None:
                    # 在Redis中执行Top-10相似度查询
                    similar_entities = self._find_similar_entities(vector_128d, k=10)
                    
                    # 根据查询结果计算风险得分
                    risk_score = self._calculate_risk_score(similar_entities)
                    
                    results.append({
                        "entity_id": entity_ids[i],
                        "vector_35d": vectors_35d[i].tolist(),
                        "vector_128d": vector_128d.tolist(),
                        "similar_entities": similar_entities,
                        "risk_score": risk_score,
                        "risk_level": self._get_risk_level(risk_score)
                    })
                else:
                    results.append({
                        "entity_id": entity_ids[i],
                        "error": "向量编码失败",
                        "risk_score": 0.0,
                        "risk_level": "未知"
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"批量处理向量时出错: {e}")
            # 返回错误结果
            results = []
            for entity_id in entity_ids:
                results.append({
                    "entity_id": entity_id,
                    "error": str(e),
                    "risk_score": 0.0,
                    "risk_level": "未知"
                })
            return results
    
    def _encode_vector(self, vector_35d: np.ndarray) -> Union[np.ndarray, None]:
        """
        使用编码器将35维向量编码为128维向量
        
        Args:
            vector_35d: 35维输入向量
            
        Returns:
            128维编码后的向量，如果失败则返回None
        """
        try:
            # 获取编码器和标准化器
            encoder, scaler = get_encoder()
            
            if encoder is None or scaler is None:
                logger.error("编码器或标准化器未加载")
                return None
            
            # 确保输入是numpy数组
            if not isinstance(vector_35d, np.ndarray):
                vector_35d = np.array(vector_35d, dtype=np.float32)
            
            # 检查向量维度
            if vector_35d.shape[0] != 35:
                logger.error(f"输入向量维度不正确: {vector_35d.shape[0]}，期望35维")
                return None
            
            # 标准化向量
            vector_scaled = scaler.transform(vector_35d.reshape(1, -1))
            
            # 转换为PyTorch张量
            vector_tensor = torch.FloatTensor(vector_scaled)
            
            # 编码向量
            with torch.no_grad():
                vector_128d = encoder(vector_tensor)
            
            # 转换回numpy数组
            return vector_128d.numpy().flatten()
                
        except Exception as e:
            logger.error(f"向量编码失败: {e}")
            return None
    
    def _batch_encode_vectors(self, vectors_35d: List[np.ndarray]) -> Union[List[np.ndarray], None]:
        """
        批量编码35维向量为128维向量
        
        Args:
            vectors_35d: 35维输入向量列表
            
        Returns:
            128维编码后的向量列表，如果失败则返回None
        """
        try:
            from app.models.model_loader import get_encoder
            import torch
            
            encoder, scaler = get_encoder()
            if encoder is None or scaler is None:
                logger.error("编码器未加载")
                return None
            
            # 确保输入是numpy数组
            vectors_array = np.array(vectors_35d, dtype=np.float32)
            
            # 批量标准化
            vectors_scaled = scaler.transform(vectors_array)
            
            # 转换为PyTorch张量
            vectors_tensor = torch.FloatTensor(vectors_scaled)
            
            # 批量编码
            with torch.no_grad():
                vectors_128d = encoder(vectors_tensor)
            
            # 转换回numpy数组
            results = vectors_128d.numpy()
            
            # 转换为列表
            return [results[i].flatten().astype(np.float32) for i in range(results.shape[0])]
            
        except Exception as e:
            logger.error(f"批量向量编码失败: {e}")
            return None
    
    def _find_similar_entities(self, vector_128d: np.ndarray, k: int = 10) -> List[Dict]:
        """
        查找与指定向量相似的实体
        
        Args:
            vector_128d: 128维向量
            k: 返回最相似的k个实体
            
        Returns:
            相似实体列表，包含实体ID、相似度得分和标签
        """
        if self.redis_client is None:
            logger.warning("Redis客户端未初始化")
            return []
        
        try:
            # 确保向量是FLOAT32类型
            if not isinstance(vector_128d, np.ndarray):
                vector_128d = np.array(vector_128d, dtype=np.float32)
            vector_128d = vector_128d.astype(np.float32)
            
            # 执行向量搜索
            result = self.redis_client.execute_command(
                'FT.SEARCH', 'entity_vectors',
                '*=>[KNN %d @vector $vec AS similarity_score]' % k,
                'PARAMS', '2', 'vec', vector_128d.tobytes(),
                'SORTBY', 'similarity_score', 'ASC',
                'DIALECT', '2',
                'LIMIT', '0', str(k)
            )
            
            # 解析结果
            similar_entities = []
            for i in range(1, len(result), 2):
                fields = result[i+1]
                entity_info = {}
                
                for j in range(0, len(fields), 2):
                    field_name = fields[j].decode('utf-8') if isinstance(fields[j], bytes) else fields[j]
                    field_value = fields[j+1]
                    
                    # 解码字段值如果是字节类型
                    if isinstance(field_value, bytes):
                        try:
                            field_value = field_value.decode('utf-8')
                        except UnicodeDecodeError:
                            continue
                    
                    entity_info[field_name] = field_value
                
                # 提取必要字段
                entity_id = entity_info.get('entity_id') or entity_info.get('id')
                similarity_score = entity_info.get('similarity_score')
                label = entity_info.get('label')
                
                if entity_id and similarity_score is not None:
                    try:
                        similar_entities.append({
                            'entity_id': str(entity_id),
                            'similarity_score': float(similarity_score),
                            'label': int(label) if label is not None else None
                        })
                    except (ValueError, TypeError) as e:
                        logger.warning(f"转换实体信息字段时出错: {e}")
                        continue
            
            return similar_entities
            
        except Exception as e:
            logger.error(f"查找相似实体失败: {e}")
            return []
    
    def _calculate_risk_score(self, similar_entities: List[Dict]) -> float:
        """
        根据相似实体列表计算风险得分
        
        新的评分逻辑：
        1. 基于相似实体的标签和相似度综合计算风险
        2. 考虑相似度权重，相似度越高权重越大
        3. 综合考虑高风险实体比例和相似度分布
        
        Args:
            similar_entities: 相似实体列表
            
        Returns:
            风险得分 (0-100)
        """
        if not similar_entities:
            # 如果没有相似实体，默认返回中等风险
            return 50.0
        
        # 计算加权风险分数
        total_weight = 0.0
        weighted_risk = 0.0
        
        # 获取相似度范围用于归一化
        similarities = [doc['similarity_score'] for doc in similar_entities]
        min_sim = min(similarities)
        max_sim = max(similarities)
        range_sim = max_sim - min_sim if max_sim != min_sim else 1.0
        
        for entity in similar_entities:
            similarity_score = entity['similarity_score']
            label = entity['label']
            
            # 计算归一化相似度（越相似值越大）
            normalized_similarity = (similarity_score - min_sim) / range_sim if range_sim > 0 else 0.5
            # 转换为权重（越相似权重越大）
            weight = 0.1 + 0.9 * normalized_similarity  # 权重范围在0.1-1.0之间
            
            # 标签为1的实体风险值高，标签为0的实体风险值低
            risk_value = 100.0 if label == 1 else 0.0
            
            # 累加加权风险
            weighted_risk += risk_value * weight
            total_weight += weight
        
        # 计算加权平均风险分数
        if total_weight > 0:
            risk_score = weighted_risk / total_weight
        else:
            risk_score = 50.0  # 默认中等风险
            
        # 考虑高风险实体比例因素
        high_risk_count = sum(1 for doc in similar_entities if doc['label'] == 1)
        high_risk_ratio = high_risk_count / len(similar_entities)
        
        # 如果高风险实体比例很高，适当提高评分
        if high_risk_ratio > 0.5:
            risk_score = min(100.0, risk_score * (1 + 0.2 * (high_risk_ratio - 0.5)))
        elif high_risk_ratio < 0.1:
            # 如果高风险实体比例很低，适当降低评分
            risk_score = max(0.0, risk_score * (1 - 0.3 * (0.1 - high_risk_ratio)))
        
        # 考虑相似度的整体水平
        avg_similarity = np.mean(similarities)
        if avg_similarity < 0.05:
            # 相似度很低，说明这是个特殊的向量，降低风险评分
            risk_score *= 0.7
        elif avg_similarity > 0.3:
            # 相似度很高，提高风险评分
            risk_score = min(100.0, risk_score * 1.2)
        
        # 确保得分在合理范围内
        return max(0.0, min(100.0, risk_score))
    
    def _get_risk_level(self, risk_score: float) -> str:
        """
        根据风险得分确定风险等级
        
        Args:
            risk_score: 风险得分 (0-100)
            
        Returns:
            风险等级字符串
        """
        if risk_score >= 80:
            return "高风险"
        elif risk_score >= 60:
            return "中风险"
        elif risk_score >= 30:
            return "低风险"
        else:
            return "正常"

# 使用示例
def main():
    """
    演示如何使用风险检测核心模块
    """
    # 创建风险检测核心实例
    risk_detector = FraudDetectionCore()
    
    # 生成示例35维向量
    np.random.seed(42)
    sample_vector_35d = np.random.randn(35).astype(np.float32)
    
    # 处理向量
    result = risk_detector.process_vector(sample_vector_35d, "entity_001")
    
    # 输出结果
    print("风险检测结果:")
    print(f"实体ID: {result.get('entity_id')}")
    print(f"风险得分: {result.get('risk_score'):.2f}")
    print(f"风险等级: {result.get('risk_level')}")
    print(f"相似实体数量: {len(result.get('similar_entities', []))}")

if __name__ == "__main__":
    main()