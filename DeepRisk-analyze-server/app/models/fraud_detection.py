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
        精细化风险得分计算逻辑
        
        核心思想：
        1. 标签风险：恶意标签直接贡献风险分数
        2. 相似度风险：低相似度表示异常行为，也是风险信号
        3. 分布风险：考虑相似度分布的离散程度
        4. 综合评估：多维度加权计算最终风险
        
        Args:
            similar_entities: 相似实体列表
            
        Returns:
            风险得分 (0-100)
        """
        if not similar_entities:
            # 没有相似实体本身就是高风险信号
            return 85.0
        
        similarities = [entity['similarity_score'] for entity in similar_entities]
        labels = [entity['label'] for entity in similar_entities if entity['label'] is not None]
        
        # 1. 标签风险评估
        label_risk = self._calculate_label_risk(labels)
        
        # 2. 相似度风险评估
        similarity_risk = self._calculate_similarity_risk(similarities)
        
        # 3. 分布风险评估
        distribution_risk = self._calculate_distribution_risk(similarities, labels)
        
        # 4. 综合风险计算（加权平均）
        weights = {
            'label': 0.4,      # 标签风险权重
            'similarity': 0.35, # 相似度风险权重
            'distribution': 0.25 # 分布风险权重
        }
        
        final_risk = (
            label_risk * weights['label'] +
            similarity_risk * weights['similarity'] +
            distribution_risk * weights['distribution']
        )
        
        # 5. 特殊情况调整
        final_risk = self._apply_special_adjustments(final_risk, similarities, labels)
        
        return max(0.0, min(100.0, final_risk))
    
    def _calculate_label_risk(self, labels: List[int]) -> float:
        """
        基于标签计算风险分数
        
        Args:
            labels: 标签列表
            
        Returns:
            标签风险分数 (0-100)
        """
        if not labels:
            return 50.0  # 无标签信息，中等风险
        
        malicious_count = sum(1 for label in labels if label == 1)
        total_count = len(labels)
        malicious_ratio = malicious_count / total_count
        
        # 恶意标签比例越高，风险越大
        base_risk = malicious_ratio * 100
        
        # 考虑恶意标签的集中度
        if malicious_count > 0:
            # 如果前几个结果中有恶意标签，风险更高
            top3_malicious = sum(1 for i, label in enumerate(labels[:3]) if label == 1)
            concentration_bonus = (top3_malicious / min(3, len(labels))) * 20
            base_risk += concentration_bonus
        
        return min(100.0, base_risk)
    
    def _calculate_similarity_risk(self, similarities: List[float]) -> float:
        """
        基于相似度计算风险分数
        
        核心逻辑：相似度过低表示异常行为，也是风险信号
        
        Args:
            similarities: 相似度列表
            
        Returns:
            相似度风险分数 (0-100)
        """
        if not similarities:
            return 90.0  # 无相似实体，高风险
        
        avg_similarity = np.mean(similarities)
        max_similarity = max(similarities)
        min_similarity = min(similarities)
        
        # 1. 平均相似度风险
        if avg_similarity < 0.1:
            # 平均相似度很低，高风险
            avg_risk = 80.0
        elif avg_similarity < 0.3:
            # 平均相似度较低，中高风险
            avg_risk = 60.0 + (0.3 - avg_similarity) * 100
        elif avg_similarity > 0.8:
            # 平均相似度很高，可能是正常行为
            avg_risk = 10.0
        else:
            # 中等相似度，中等风险
            avg_risk = 40.0 - (avg_similarity - 0.3) * 60
        
        # 2. 最高相似度风险
        if max_similarity < 0.2:
            # 连最相似的都不够相似，高风险
            max_risk = 70.0
        elif max_similarity > 0.9:
            # 有非常相似的实体，低风险
            max_risk = 5.0
        else:
            max_risk = 35.0 - (max_similarity - 0.2) * 42.8
        
        # 综合相似度风险
        similarity_risk = (avg_risk * 0.7 + max_risk * 0.3)
        
        return max(0.0, min(100.0, similarity_risk))
    
    def _calculate_distribution_risk(self, similarities: List[float], labels: List[int]) -> float:
        """
        基于相似度和标签分布计算风险
        
        Args:
            similarities: 相似度列表
            labels: 标签列表
            
        Returns:
            分布风险分数 (0-100)
        """
        if not similarities:
            return 50.0
        
        # 1. 相似度分布的离散程度
        similarity_std = np.std(similarities)
        if similarity_std > 0.3:
            # 相似度分布很分散，可能是异常
            dispersion_risk = 60.0
        elif similarity_std < 0.05:
            # 相似度分布很集中，相对正常
            dispersion_risk = 20.0
        else:
            dispersion_risk = 20.0 + (similarity_std - 0.05) * 160
        
        # 2. 标签与相似度的一致性
        consistency_risk = 30.0  # 默认值
        if labels and len(labels) == len(similarities):
            # 检查高相似度是否对应安全标签
            high_sim_indices = [i for i, sim in enumerate(similarities) if sim > 0.5]
            if high_sim_indices:
                safe_high_sim = sum(1 for i in high_sim_indices if i < len(labels) and labels[i] == 0)
                consistency_ratio = safe_high_sim / len(high_sim_indices)
                # 高相似度对应安全标签比例越高，风险越低
                consistency_risk = 60.0 * (1 - consistency_ratio)
        
        return (dispersion_risk * 0.6 + consistency_risk * 0.4)
    
    def _apply_special_adjustments(self, base_risk: float, similarities: List[float], labels: List[int]) -> float:
        """
        应用特殊情况的风险调整
        
        Args:
            base_risk: 基础风险分数
            similarities: 相似度列表
            labels: 标签列表
            
        Returns:
            调整后的风险分数
        """
        adjusted_risk = base_risk
        
        # 1. 极端相似度情况
        if similarities:
            min_sim = min(similarities)
            if min_sim < 0.01:
                # 存在极低相似度，额外风险
                adjusted_risk += 15.0
            
            max_sim = max(similarities)
            if max_sim > 0.95:
                # 存在极高相似度，降低风险
                adjusted_risk -= 10.0
        
        # 2. 全部正常标签但低相似度的情况（用户特别提到的场景）
        if labels and all(label == 0 for label in labels):
            avg_similarity = np.mean(similarities) if similarities else 0
            if avg_similarity < 0.2:
                # 全部正常标签但相似度很低，这是异常信号
                adjusted_risk = max(adjusted_risk, 65.0)
                logger.info(f"检测到异常模式：全部正常标签但低相似度(avg={avg_similarity:.3f})，风险分数调整为{adjusted_risk}")
        
        # 3. 数据质量调整
        if len(similarities) < 5:
            # 相似实体太少，增加不确定性风险
            adjusted_risk += 10.0
        
        return adjusted_risk
    
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