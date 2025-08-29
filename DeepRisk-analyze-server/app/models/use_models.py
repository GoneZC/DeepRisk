import numpy as np
import pandas as pd
import torch
import os
import pickle
import time
from deepod.models import DeepSVDD
import json

print("实体异常分数计算")
start_time = time.time()

if not os.path.exists('models'):
    raise FileNotFoundError("找不到模型目录")

models = {}
scalers = {}
feature_cols = {}

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"使用设备: {device}")

for model_type in ['transaction', 'behavior', 'pattern']:
    print(f"加载{model_type}模型")
    try:
        model_path = f'models/{model_type}_dsvdd_model.pth'
        models[model_type] = DeepSVDD.load(model_path, device)
        
        scaler_path = f'models/{model_type}_scaler.pkl'
        with open(scaler_path, 'rb') as f:
            scalers[model_type] = pickle.load(f)
            
        cols_path = f'models/{model_type}_feature_cols.pkl'
        with open(cols_path, 'rb') as f:
            feature_cols[model_type] = pickle.load(f)
            
        print(f"{model_type}模型加载成功")
    except Exception as e:
        print(f"加载{model_type}模型失败: {e}")
        models[model_type] = None

# 读取数据并计算分数
entity_scores = {}

# 处理交易数据
if models['transaction'] is not None:
    print("\n处理交易聚合数据...")
    try:
        transaction_df = pd.read_csv('output/entity_transaction_vectors.csv')
        print(f"读取了 {len(transaction_df)} 条交易记录")
        
        # 提取特征
        X_transaction = transaction_df[feature_cols['transaction']].values
        X_transaction = np.nan_to_num(X_transaction, nan=0.0)
        
        # 归一化
        X_transaction = scalers['transaction'].transform(X_transaction)
        
        # 计算异常分数
        transaction_scores = models['transaction'].decision_function(X_transaction)
        
        # 保存分数
        for i, row in transaction_df[['ENTITY_CODE', 'TRANSACTION_DATE']].iterrows():
            entity_code = row['ENTITY_CODE']
            if entity_code not in entity_scores:
                entity_scores[entity_code] = {'transaction': [], 'behavior': [], 'pattern': []}
            entity_scores[entity_code]['transaction'].append(transaction_scores[i])
    except Exception as e:
        print(f"处理交易数据失败: {e}")

# 处理行为向量数据
if models['behavior'] is not None:
    print("\n处理行为向量数据...")
    try:
        behavior_df = pd.read_csv('output/entity_behavior_vectors.csv')
        print(f"读取了 {len(behavior_df)} 条行为向量记录")
        
        # 提取特征
        X_behavior = behavior_df[feature_cols['behavior']].values
        X_behavior = np.nan_to_num(X_behavior, nan=0.0)
        
        # 归一化
        X_behavior = scalers['behavior'].transform(X_behavior)
        
        # 计算异常分数
        behavior_scores = models['behavior'].decision_function(X_behavior)
        
        # 保存分数
        for i, row in behavior_df[['ENTITY_CODE', 'TRANSACTION_DATE']].iterrows():
            entity_code = row['ENTITY_CODE']
            if entity_code not in entity_scores:
                entity_scores[entity_code] = {'transaction': [], 'behavior': [], 'pattern': []}
            entity_scores[entity_code]['behavior'].append(behavior_scores[i])
    except Exception as e:
        print(f"处理行为向量数据失败: {e}")

# 处理模式向量数据
if models['pattern'] is not None:
    print("\n处理模式向量数据...")
    try:
        pattern_df = pd.read_csv('output/entity_pattern_vectors.csv')
        print(f"读取了 {len(pattern_df)} 条模式向量记录")
        
        # 提取特征
        X_pattern = pattern_df[feature_cols['pattern']].values
        X_pattern = np.nan_to_num(X_pattern, nan=0.0)
        
        # 归一化
        X_pattern = scalers['pattern'].transform(X_pattern)
        
        # 计算异常分数
        pattern_scores = models['pattern'].decision_function(X_pattern)
        
        # 保存分数
        for i, row in pattern_df[['ENTITY_CODE', 'TRANSACTION_DATE']].iterrows():
            entity_code = row['ENTITY_CODE']
            if entity_code not in entity_scores:
                entity_scores[entity_code] = {'transaction': [], 'behavior': [], 'pattern': []}
            entity_scores[entity_code]['pattern'].append(pattern_scores[i])
    except Exception as e:
        print(f"处理模式向量数据失败: {e}")

# 计算最终异常分数
print("\n计算最终异常分数...")
results = []

for entity_code, scores in entity_scores.items():
    transaction_avg = np.mean(scores['transaction']) if scores['transaction'] else np.nan
    behavior_avg = np.mean(scores['behavior']) if scores['behavior'] else np.nan
    pattern_avg = np.mean(scores['pattern']) if scores['pattern'] else np.nan
    
    # 计算组合分数（权重各1/3）
    valid_scores = []
    valid_weights = []
    
    if not np.isnan(transaction_avg):
        valid_scores.append(transaction_avg)
        valid_weights.append(1/3)
    if not np.isnan(behavior_avg):
        valid_scores.append(behavior_avg)
        valid_weights.append(1/3)
    if not np.isnan(pattern_avg):
        valid_scores.append(pattern_avg)
        valid_weights.append(1/3)
    
    # 归一化权重
    if valid_weights:
        valid_weights = [w/sum(valid_weights) for w in valid_weights]
    
    # 计算加权平均分数
    combined_score = np.sum(np.array(valid_scores) * np.array(valid_weights)) if valid_scores else np.nan
    
    # 统计每种类型的记录数
    transaction_count = len(scores['transaction'])
    behavior_count = len(scores['behavior'])
    pattern_count = len(scores['pattern'])
    
    results.append({
        'ENTITY_CODE': entity_code,
        'transaction_score': transaction_avg,
        'behavior_score': behavior_avg,
        'pattern_score': pattern_avg,
        'combined_score': combined_score,
        'transaction_count': transaction_count,
        'behavior_count': behavior_count,
        'pattern_count': pattern_count,
        'total_count': transaction_count + behavior_count + pattern_count
    })

# 创建结果DataFrame
results_df = pd.DataFrame(results)

# 根据异常分数排序
if 'combined_score' in results_df.columns:
    results_df = results_df.sort_values(by='combined_score', ascending=False)

# 保存结果
output_file = 'output/entity_anomaly_scores.csv'
results_df.to_csv(output_file, index=False)
print(f"\n异常分数已保存至 '{output_file}'")

# 显示结果
print("\n===== 排名前20的异常实体 =====")
if len(results_df) > 0:
    top_n = min(20, len(results_df))
    print(results_df.head(top_n)[['ENTITY_CODE', 'combined_score', 'transaction_score', 'behavior_score', 'pattern_score', 'total_count']])
else:
    print("没有计算出有效的异常分数")

# 统计信息
print("\n===== 统计信息 =====")
print(f"处理的实体总数: {len(results_df)}")

valid_combined = results_df['combined_score'].notna()
if valid_combined.any():
    print(f"有效综合分数的实体数: {valid_combined.sum()}")
    print(f"综合分数平均值: {results_df.loc[valid_combined, 'combined_score'].mean():.4f}")
    print(f"综合分数中位数: {results_df.loc[valid_combined, 'combined_score'].median():.4f}")
    print(f"综合分数最大值: {results_df.loc[valid_combined, 'combined_score'].max():.4f}")
    print(f"综合分数最小值: {results_df.loc[valid_combined, 'combined_score'].min():.4f}")

total_time = time.time() - start_time
print(f"\n处理完成，总用时: {total_time:.2f}秒 ({total_time/60:.2f}分钟)")
print("========== 程序结束 ==========")

# 在现有代码结尾添加以下内容（保留之前的代码不变）

# 计算风险阈值
print("\n===== 计算风险阈值 =====")

# 定义计算风险阈值的函数
def calculate_risk_thresholds(scores, method='percentile'):
    """计算低、中、高风险的阈值
    
    Parameters:
    -----------
    scores: array-like
        异常分数数组
    method: str, default='percentile'
        阈值计算方法，可选值:
        - 'percentile': 使用分位数（70%/90%）
        - 'sigma': 使用均值+标准差（μ+1σ/μ+2σ）
    
    Returns:
    --------
    thresholds: dict
        包含low和high阈值的字典
    """
    if method == 'percentile':
        # 使用70%分位数和90%分位数作为阈值
        low = np.nanpercentile(scores, 70)
        high = np.nanpercentile(scores, 90)
    elif method == 'sigma':
        # 使用均值+1个标准差和均值+2个标准差作为阈值
        mean = np.nanmean(scores)
        std = np.nanstd(scores)
        low = mean + 1 * std
        high = mean + 2 * std
    else:
        raise ValueError(f"不支持的方法: {method}")
    
    return {'low': low, 'high': high}

# 选择阈值计算方法
threshold_method = 'percentile'  # 可选: 'percentile', 'sigma'
print(f"使用方法: {threshold_method}")

# 计算每种分数的阈值
thresholds = {}
for score_type in ['transaction_score', 'behavior_score', 'pattern_score', 'combined_score']:
    scores = results_df[score_type].dropna().values
    if len(scores) > 0:
        thresholds[score_type] = calculate_risk_thresholds(scores, threshold_method)
        print(f"{score_type} 阈值: 低风险 > {thresholds[score_type]['low']:.4f}, 高风险 > {thresholds[score_type]['high']:.4f}")

# 添加风险等级列
for score_type in ['transaction_score', 'behavior_score', 'pattern_score', 'combined_score']:
    if score_type in thresholds:
        risk_col = f"{score_type.split('_')[0]}_risk"
        results_df[risk_col] = 'low'
        # 中等风险
        mask = (results_df[score_type] >= thresholds[score_type]['low'])
        results_df.loc[mask, risk_col] = 'medium'
        # 高风险
        mask = (results_df[score_type] >= thresholds[score_type]['high'])
        results_df.loc[mask, risk_col] = 'high'

# 统计每种风险级别的医生数量
print("\n===== 风险级别统计 =====")
for risk_col in ['fee_risk', 'drug_risk', 'diag_risk', 'combined_risk']:
    if risk_col in results_df.columns:
        risk_counts = results_df[risk_col].value_counts()
        print(f"\n{risk_col} 分布:")
        for risk_level, count in risk_counts.items():
            percentage = count / len(results_df) * 100
            print(f"  {risk_level}: {count} 人 ({percentage:.1f}%)")

# 保存添加了风险等级的结果
risk_output_file = 'output/doctor_risk_levels.csv'
results_df.to_csv(risk_output_file, index=False)
print(f"\n风险分级结果已保存至 '{risk_output_file}'")

# 显示高风险医生
print("\n===== 高风险医生（综合分数）=====")
high_risk = results_df[results_df['combined_risk'] == 'high']
if len(high_risk) > 0:
    columns_to_show = ['BILG_DR_CODE', 'combined_score', 'fee_score', 'drug_score', 'diag_score', 
                      'combined_risk', 'fee_risk', 'drug_risk', 'diag_risk', 'total_count']
    print(high_risk[columns_to_show].head(20))
    print(f"共有 {len(high_risk)} 名高风险医生")
else:
    print("没有检测到高风险医生")

# 在计算完阈值后，添加以下代码保存阈值

# 创建更完整的阈值字典
threshold_dict = {
    'fee_score': {
        'low_max': thresholds['fee_score']['low'],  # 低风险上限
        'medium_min': thresholds['fee_score']['low'],  # 中风险下限
        'medium_max': thresholds['fee_score']['high'],  # 中风险上限
        'high_min': thresholds['fee_score']['high']  # 高风险下限
    },
    'drug_score': {
        'low_max': thresholds['drug_score']['low'],
        'medium_min': thresholds['drug_score']['low'],
        'medium_max': thresholds['drug_score']['high'],
        'high_min': thresholds['drug_score']['high']
    },
    'diag_score': {
        'low_max': thresholds['diag_score']['low'],
        'medium_min': thresholds['diag_score']['low'],
        'medium_max': thresholds['diag_score']['high'],
        'high_min': thresholds['diag_score']['high']
    },
    'combined_score': {
        'low_max': thresholds['combined_score']['low'],
        'medium_min': thresholds['combined_score']['low'],
        'medium_max': thresholds['combined_score']['high'],
        'high_min': thresholds['combined_score']['high']
    },
    'method': threshold_method,  # 记录使用的阈值计算方法
    'percentiles': {
        'low_max': 70,  # 对应于low/medium的分界线
        'high_min': 90   # 对应于medium/high的分界线
    }
}

# 保存阈值到JSON文件
thresholds_file = 'models/risk_thresholds.json'
with open(thresholds_file, 'w') as f:
    json.dump(threshold_dict, f, indent=4)
print(f"\n风险阈值已保存至 '{thresholds_file}'")