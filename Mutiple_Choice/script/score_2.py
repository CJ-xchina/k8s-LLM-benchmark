import numpy as np
import pandas as pd
from scipy.stats import norm


def z_score_transform(scores, mean, std_dev):
    # 使用Z-score标准化
    z_scores = (scores - mean) / std_dev

    # 将Z-score标准化到0-100之间
    min_z = np.min(z_scores)
    max_z = np.max(z_scores)
    normalized_scores = (z_scores - min_z) / (max_z - min_z) * 100

    return normalized_scores


def calculate_normalized_accuracy_per_category_subcategory(csv_file, jsonl_file):
    # 读取 CSV 文件到 DataFrame
    df = pd.read_csv(csv_file)
    if 'answer' not in df.columns:
        raise ValueError("CSV file must contain an 'answer' column")

    # 读取 JSONL 文件到 DataFrame
    jsonl_df = pd.read_json(jsonl_file, lines=True)

    # 合并数据
    df = df.merge(jsonl_df[['id', 'category', 'subcategory', 'score']], on='id', how='left')

    # 排除分数小于3的记录
    df = df[df['score'] >= 3]

    # 提取模型分数列
    score_columns = df.columns[df.columns.str.endswith('_score')]

    # 将分数列转换为数值类型，无效的值转换为NaN
    df[score_columns] = df[score_columns].apply(pd.to_numeric, errors='coerce')

    # 清洗数据，只选择有效的分数（1-100之间的数字且非空）
    valid_scores_mask = df[score_columns].apply(lambda x: (
            (x >= 1) & (x <= 100)
    ), axis=0)  # 检查每个分数列的有效性

    valid_df = df[valid_scores_mask.all(axis=1)].dropna(subset=score_columns)  # 删除包含 NaN 的行

    # 获取所有有效的分数
    all_valid_scores = valid_df[score_columns].values.flatten()
    all_valid_scores = all_valid_scores[~np.isnan(all_valid_scores)]  # 确保没有NaN值

    if all_valid_scores.size > 0:  # 确保数组不为空
        overall_mean = np.mean(all_valid_scores)
        overall_std_dev = np.std(all_valid_scores, ddof=0)  # 使用 ddof=0 计算总体标准差
    else:
        overall_mean = 0
        overall_std_dev = 0

    # 使用Z-score映射所有模型的得分
    for score_column in score_columns:
        # 过滤掉无效的分数
        valid_scores_series = valid_df[score_column]
        # 映射有效的分数到Z-score并标准化到0-100之间
        df.loc[valid_df.index, score_column] = z_score_transform(valid_scores_series, overall_mean, overall_std_dev)

    # 计算准确率
    model_acc = {}
    for model in score_columns:
        model_name = model.replace('_score', '')
        model_acc[model_name] = {
            'overall': ((df['score'] == df[model]).mean()) * 100,
            'category': {},
            'subcategory': {}
        }

        # 计算每个 category 和 subcategory 的准确率
        for category, subcategory_df in df.groupby('category'):
            for subcategory, _ in subcategory_df.groupby('subcategory'):
                correct_predictions = (subcategory_df['score'] == subcategory_df[model]).sum()
                total_predictions = len(subcategory_df)
                if total_predictions > 0:
                    cat_acc = correct_predictions / total_predictions * 100
                    model_acc[model_name]['category'][category] = cat_acc
                    for subcat, subcat_df in subcategory_df.groupby('subcategory'):
                        subcat_acc = (subcat_df['score'] == subcat_df[model]).mean() * 100
                        model_acc[model_name]['subcategory'][(category, subcat)] = subcat_acc
                else:
                    model_acc[model_name]['category'][category] = 0
                    model_acc[model_name]['subcategory'][(category, subcategory)] = 0
    return model_acc


# 使用函数
csv_file = "../resources/result_obj.csv"
jsonl_file = "../resources/questions.jsonl"
accuracy = calculate_normalized_accuracy_per_category_subcategory(csv_file, jsonl_file)
print(accuracy)
