from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from uuid import uuid4
from pathlib import Path
import shutil
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import mysql.connector
from mysql.connector import Error
from app.models.model_loader import get_models, get_scalers, _thresholds
from config import Config  # 导入配置


api_bp = Blueprint('api', __name__)
CORS(api_bp)

# 风险评估API接口
@api_bp.route('/risk-assessment', methods=['POST'])
def risk_assessment():
    data = request.json
    doctor_id = data.get('doctorId')
    date = data.get('date')
    
    if not doctor_id:
        return jsonify({"error": "医生编号不能为空"}), 400
    
    print(f"连接数据库查询医生[{doctor_id}]的数据...")
    
    # 初始化默认分数
    fee_score = 0
    drug_score = 0
    diag_score = 0
    
    try:
        # 连接数据库
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        print("数据库连接成功")
        
        # 1. 直接从向量表获取费用向量并评估
        try:
            cursor = conn.cursor()
            query = f"""
                SELECT * FROM doctor_fee_vectors 
                WHERE BILG_DR_CODE = '{doctor_id}'
            """
            if date:
                query += f" AND fee_date = '{date}'"
            
            print(f"执行费用查询: {query}")
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                print(f"找到费用数据，列数: {len(result)}")
                fee_vector = []
                column_names = [desc[0] for desc in cursor.description]
                for i, col_name in enumerate(column_names):
                    if col_name.lower() not in ['bilg_dr_code', 'fee_date']:
                        fee_vector.append(float(result[i] or 0))
                
                # 使用DeepSVDD模型进行评估
                fee_score = 0
                if fee_vector:
                    try:
                        # 获取模型和标准化器
                        models = get_models()
                        scalers = get_scalers()
                        
                        # 检查模型和标准化器是否存在
                        if 'fee' in models and 'fee' in scalers:
                            fee_model = models['fee']
                            fee_scaler = scalers['fee']
                            
                            # 标准化向量
                            fee_vector_norm = fee_scaler.transform([fee_vector])
                            
                            # 直接使用decision_function获取分数
                            fee_score = fee_model.decision_function(fee_vector_norm)[0]
                            print(f"使用模型计算费用风险评分: {fee_score}")
                        else:
                            # 如果模型不存在，使用简单方法计算
                            fee_score = sum(fee_vector) / len(fee_vector) if len(fee_vector) > 0 else 0
                            print(f"模型不存在，使用简单方法计算费用风险评分: {fee_score}")
                    except Exception as e:
                        print(f"模型评估出错，使用简单方法: {e}")
                        fee_score = sum(fee_vector) / len(fee_vector) if len(fee_vector) > 0 else 0
                else:
                    print("费用向量为空")
            else:
                print("未找到费用数据")
            
            cursor.close()
            
        except Exception as e:
            print(f"获取费用向量出错: {e}")
        
        # 2. 直接从向量表获取药品向量并评估
        try:
            cursor = conn.cursor()
            query = f"""
                SELECT * FROM doctor_drug_vectors 
                WHERE BILG_DR_CODE = '{doctor_id}'
            """
            if date:
                query += f" AND fee_date = '{date}'"
            cursor.execute(query)
            result = cursor.fetchone()
            
            drug_vector = []
            if result:
                column_names = [desc[0] for desc in cursor.description]
                for i, col_name in enumerate(column_names):
                    if col_name.lower() not in ['bilg_dr_code', 'fee_date']:
                        drug_vector.append(float(result[i] or 0))
            
            # 使用DeepSVDD模型进行评估
            drug_score = 0
            if drug_vector:
                try:
                    # 获取模型和标准化器
                    models = get_models()
                    scalers = get_scalers()
                    
                    # 检查模型和标准化器是否存在
                    if 'drug' in models and 'drug' in scalers:
                        drug_model = models['drug']
                        drug_scaler = scalers['drug']
                        
                        # 标准化向量
                        drug_vector_norm = drug_scaler.transform([drug_vector])
                        
                        # 直接使用decision_function获取分数
                        drug_score = drug_model.decision_function(drug_vector_norm)[0]
                        print(f"使用模型计算药品风险评分: {drug_score}")
                    else:
                        # 如果模型不存在，使用简单方法计算
                        drug_score = sum(drug_vector) / len(drug_vector) if len(drug_vector) > 0 else 0
                        print(f"模型不存在，使用简单方法计算药品风险评分: {drug_score}")
                except Exception as e:
                    print(f"模型评估出错，使用简单方法: {e}")
                    drug_score = sum(drug_vector) / len(drug_vector) if len(drug_vector) > 0 else 0
            else:
                print("药品向量为空")
            
            cursor.close()
            
        except Exception as e:
            print(f"获取药品向量出错: {e}")
            drug_score = 50
        
        # 3. 直接从向量表获取诊断向量并评估
        try:
            cursor = conn.cursor()
            query = f"""
                SELECT * FROM doctor_diag_vectors 
                WHERE BILG_DR_CODE = '{doctor_id}'
            """
            if date:
                query += f" AND fee_date = '{date}'"
            cursor.execute(query)
            result = cursor.fetchone()
            
            diag_vector = []
            if result:
                column_names = [desc[0] for desc in cursor.description]
                for i, col_name in enumerate(column_names):
                    if col_name.lower() not in ['bilg_dr_code', 'fee_date']:
                        diag_vector.append(float(result[i] or 0))
            
            # 使用模型进行诊断风险评估
            diag_score = 0
            if diag_vector:
                # 获取模型和标准化器
                models = get_models()
                scalers = get_scalers()
                
                if 'diag' in models and 'diag' in scalers:
                    # 标准化向量
                    diag_vector_np = np.array(diag_vector).reshape(1, -1)
                    diag_vector_scaled = scalers['diag'].transform(diag_vector_np)
                    
                    # 使用模型计算风险分数
                    diag_score = models['diag'].decision_function(diag_vector_scaled)[0]
                    
                    # 将分数转换为0-100的范围
                    diag_score = min(max(diag_score * 100, 0), 100)
                else:
                    # 如果没有模型，退化到使用平均值
                    diag_score = sum(diag_vector) / len(diag_vector) * 10
                    diag_score = min(max(diag_score, 0), 100)
            
            print(f"诊断风险评分: {diag_score}")
            cursor.close()
            
        except Exception as e:
            print(f"获取诊断向量出错: {e}")
            diag_score = 50
        
        # 关闭数据库连接
        conn.close()
        
        # 计算综合分数
        valid_scores = []
        if fee_score > 0: valid_scores.append(fee_score)
        if drug_score > 0: valid_scores.append(drug_score)
        if diag_score > 0: valid_scores.append(diag_score)
        
        # 确保即使没有有效分数也能返回结果
        if valid_scores:
            combined_score = float(sum(valid_scores) / len(valid_scores))
        else:
            # 没有有效分数时设置默认值
            combined_score = 0
        
        # 计算各维度的风险等级
        fee_risk_level = get_risk_level(fee_score, "fee_score")
        drug_risk_level = get_risk_level(drug_score, "drug_score")
        diag_risk_level = get_risk_level(diag_score, "diag_score")

        # 返回结果，只包含各维度的风险等级，移除riskLevel字段
        result = {
            "doctorId": doctor_id,
            "feeScore": fee_score,
            "drugScore": drug_score,
            "diagScore": diag_score,
            "feeRiskLevel": fee_risk_level,   # 费用风险等级
            "drugRiskLevel": drug_risk_level, # 药品风险等级
            "diagRiskLevel": diag_risk_level, # 诊断风险等级
            "combinedScore": combined_score
        }
        
        print(f"医生[{doctor_id}]风险评估完成: 费用风险={fee_risk_level}, 药品风险={drug_risk_level}, 诊断风险={diag_risk_level}")
        return jsonify(result)
        
    except Exception as e:
        print(f"风险评估失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 计算风险等级函数
def get_risk_level(score, score_type):
    thresholds = _thresholds.get(score_type, {})
    
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

