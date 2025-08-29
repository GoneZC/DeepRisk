from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import mysql.connector
import numpy as np
from app.models.model_loader import get_models, get_scalers, get_thresholds
from app.config import Config

router = APIRouter()

class RiskAssessmentRequest(BaseModel):
    entityId: str
    date: Optional[str] = None
    businessType: Optional[str] = "general"

@router.post("/risk-assessment")
async def risk_assessment(request: RiskAssessmentRequest):
    entity_id = request.entityId
    date = request.date
    business_type = request.businessType
    
    if not entity_id:
        raise HTTPException(status_code=400, detail="实体编号不能为空")
    
    print(f"查询实体[{entity_id}]数据")
    
    # 初始化分数
    transaction_score = 0
    behavior_score = 0
    pattern_score = 0
    
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        print("数据库连接成功")
        
        # 查询交易向量数据
        try:
            cursor = conn.cursor()
            query = f"""
                SELECT * FROM entity_transaction_vectors 
                WHERE ENTITY_CODE = '{entity_id}'
            """
            if date:
                query += f" AND transaction_date = '{date}'"
            
            print(f"执行查询: {query}")
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                print(f"找到数据，列数: {len(result)}")
                transaction_vector = []
                column_names = [desc[0] for desc in cursor.description]
                for i, col_name in enumerate(column_names):
                    if col_name.lower() not in ['entity_code', 'transaction_date']:
                        transaction_vector.append(float(result[i] or 0))
                
                transaction_score = 0
                if transaction_vector:
                    try:
                        models = get_models()
                        scalers = get_scalers()
                        
                        if 'transaction' in models and 'transaction' in scalers:
                            transaction_model = models['transaction']
                            transaction_scaler = scalers['transaction']
                            
                            transaction_vector_norm = transaction_scaler.transform([transaction_vector])
                            
                            # 直接使用decision_function获取分数
                            transaction_score = transaction_model.decision_function(transaction_vector_norm)[0]
                            print(f"使用模型计算交易风险评分: {transaction_score}")
                        else:
                            # 如果模型不存在，使用简单方法计算
                            transaction_score = sum(transaction_vector) / len(transaction_vector) if len(transaction_vector) > 0 else 0
                            print(f"模型不存在，使用简单方法计算交易风险评分: {transaction_score}")
                    except Exception as e:
                        print(f"模型评估出错，使用简单方法: {e}")
                        transaction_score = sum(transaction_vector) / len(transaction_vector) if len(transaction_vector) > 0 else 0
                else:
                    print("交易向量为空")
            else:
                print("未找到交易数据")
            
            cursor.close()
            
        except Exception as e:
            print(f"获取交易向量出错: {e}")
        
        # 2. 直接从向量表获取行为向量并评估
        try:
            cursor = conn.cursor()
            query = f"""
                SELECT * FROM entity_behavior_vectors 
                WHERE ENTITY_CODE = '{entity_id}'
            """
            if date:
                query += f" AND behavior_date = '{date}'"
            cursor.execute(query)
            result = cursor.fetchone()
            
            behavior_vector = []
            if result:
                column_names = [desc[0] for desc in cursor.description]
                for i, col_name in enumerate(column_names):
                    if col_name.lower() not in ['entity_code', 'behavior_date']:
                        behavior_vector.append(float(result[i] or 0))
            
            # 使用DeepSVDD模型进行评估
            behavior_score = 0
            if behavior_vector:
                try:
                    # 获取模型和标准化器
                    models = get_models()
                    scalers = get_scalers()
                    
                    # 检查模型和标准化器是否存在
                    if 'behavior' in models and 'behavior' in scalers:
                        behavior_model = models['behavior']
                        behavior_scaler = scalers['behavior']
                        
                        # 标准化向量
                        behavior_vector_norm = behavior_scaler.transform([behavior_vector])
                        
                        # 直接使用decision_function获取分数
                        behavior_score = behavior_model.decision_function(behavior_vector_norm)[0]
                        print(f"使用模型计算行为风险评分: {behavior_score}")
                    else:
                        # 如果模型不存在，使用简单方法计算
                        behavior_score = sum(behavior_vector) / len(behavior_vector) if len(behavior_vector) > 0 else 0
                        print(f"模型不存在，使用简单方法计算行为风险评分: {behavior_score}")
                except Exception as e:
                    print(f"模型评估出错，使用简单方法: {e}")
                    behavior_score = sum(behavior_vector) / len(behavior_vector) if len(behavior_vector) > 0 else 0
            else:
                print("行为向量为空")
            
            cursor.close()
            
        except Exception as e:
            print(f"获取行为向量出错: {e}")
            behavior_score = 50
        
        # 3. 直接从向量表获取模式向量并评估
        try:
            cursor = conn.cursor()
            query = f"""
                SELECT * FROM entity_pattern_vectors 
                WHERE ENTITY_CODE = '{entity_id}'
            """
            if date:
                query += f" AND transaction_date = '{date}'"
            cursor.execute(query)
            result = cursor.fetchone()
            
            pattern_vector = []
            if result:
                column_names = [desc[0] for desc in cursor.description]
                for i, col_name in enumerate(column_names):
                    if col_name.lower() not in ['entity_code', 'transaction_date']:
                        pattern_vector.append(float(result[i] or 0))
            
            # 使用模型进行模式风险评估
            pattern_score = 0
            if pattern_vector:
                # 获取模型和标准化器
                models = get_models()
                scalers = get_scalers()
                
                if 'pattern' in models and 'pattern' in scalers:
                    # 标准化向量
                    pattern_vector_np = np.array(pattern_vector).reshape(1, -1)
                    pattern_vector_scaled = scalers['pattern'].transform(pattern_vector_np)
                    
                    # 使用模型计算风险分数
                    pattern_score = models['pattern'].decision_function(pattern_vector_scaled)[0]
                    
                    # 将分数转换为0-100的范围
                    pattern_score = min(max(pattern_score * 100, 0), 100)
                else:
                    # 如果没有模型，退化到使用平均值
                    pattern_score = sum(pattern_vector) / len(pattern_vector) * 10
                    pattern_score = min(max(pattern_score, 0), 100)
            
            print(f"模式风险评分: {pattern_score}")
            cursor.close()
            
        except Exception as e:
            print(f"获取模式向量出错: {e}")
            pattern_score = 50
        
        # 关闭数据库连接
        conn.close()
        
        # 计算综合分数
        valid_scores = []
        if transaction_score > 0: valid_scores.append(transaction_score)
        if behavior_score > 0: valid_scores.append(behavior_score)
        if pattern_score > 0: valid_scores.append(pattern_score)
        
        # 确保即使没有有效分数也能返回结果
        if valid_scores:
            combined_score = float(sum(valid_scores) / len(valid_scores))
        else:
            # 没有有效分数时设置默认值
            combined_score = 0
        
        # 计算各维度的风险等级
        transaction_risk_level = get_risk_level(transaction_score, "transaction_score")
        behavior_risk_level = get_risk_level(behavior_score, "behavior_score")
        pattern_risk_level = get_risk_level(pattern_score, "pattern_score")

        # 返回结果，只包含各维度的风险等级，移除riskLevel字段
        result = {
            "entityId": entity_id,
            "transactionScore": transaction_score,
            "behaviorScore": behavior_score,
            "patternScore": pattern_score,
            "transactionRiskLevel": transaction_risk_level,   # 交易风险等级
            "behaviorRiskLevel": behavior_risk_level, # 行为风险等级
            "patternRiskLevel": pattern_risk_level, # 模式风险等级
            "combinedScore": combined_score
        }
        
        print(f"实体[{entity_id}]风险评估完成: 交易风险={transaction_risk_level}, 行为风险={behavior_risk_level}, 模式风险={pattern_risk_level}")
        return result
        
    except Exception as e:
        print(f"风险评估失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 计算风险等级函数
def get_risk_level(score, score_type):
    thresholds = get_thresholds().get(score_type, {})
    
    if not thresholds:
        # 默认阈值
        if score < 50:
            return "正常"
        elif score < 75:
            return "低风险"
        elif score < 90:
            return "中风险"
        else:
            return "高风险"
    
    # 使用配置的阈值
    low_max = thresholds.get("low_max", 0)
    medium_max = thresholds.get("medium_max", 0)
    high_min = thresholds.get("high_min", 0)
    
    if score < low_max:
        return "正常"
    elif score < medium_max:
        return "低风险"
    elif score >= high_min:
        return "高风险"
    else:
        return "中风险"