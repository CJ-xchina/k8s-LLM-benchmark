import re

import pandas as pd

from utils.client import use_client

prompt_file_path = '../resources/prompt/prompt_score_objective_question.txt'

# 读取CSV文件
data = pd.read_csv('../resources/result_obj.csv')
with open(prompt_file_path, 'r', encoding='utf-8') as f:
    prompt_text = f.read()

time = 0
status = 'chrome'


def get_gpt_scores(text, score_column):
    column = score_column.replace('_score', '')
    global time, status
    prompt = prompt_text.format(answer=text['answer'], GPT=text[column])

    # 检查是否需要更改浏览器状态
    if time % 4 == 0:
        status = 'edge' if status == 'chrome' else 'chrome'
        fresh = True
        vpn_fresh = True
    else:
        fresh = False
        vpn_fresh = False

    # 从已存在的分数中筛选并清理 NaN
    existing_scores = [score for score in str(text[score_column]).split(',') if
                       score.strip().lower() != 'nan' and score.strip()]

    # 如果已经有三个分数，则不需要再评估
    if len(existing_scores) >= 3:
        return existing_scores

    # 否则，继续获取新的分数
    try:
        simulated_output = use_client(prompt, status=status, vpn_fresh=vpn_fresh, fresh=fresh)
        score = extract_score(simulated_output)
        if score is not None:
            existing_scores.append(score)
    except Exception as e:
        print(f"An error occurred: {e}")
        # 如果发生错误，返回已有的分数列表
        return existing_scores

    time += 1
    return existing_scores


def extract_score(output):
    output = str(output)
    match = re.search(r'Overall Score: (\d+)', output)
    if match:
        return int(match.group(1))
    match = re.search(r'\b(\d{1,2}|100)\b', output)
    if match:
        return int(match.group(1))
    return None


score_columns = [col for col in data.columns if col.endswith('_score')]
for column in score_columns:
    data[column] = data[column].astype(str)

# 对每个需要评估的列进行评估，直到达到三次评估为止
for index, row in data.iterrows():
    updates = False
    for column in score_columns:
        if pd.isna(row[column.replace('__score', '')]):
            continue
        scores = get_gpt_scores(row, column)
        updated_scores = ','.join(map(str, scores))
        print(f"打分为：{updated_scores}")
        if data.at[index, column] != updated_scores:
            data.at[index, column] = updated_scores
            updates = True
    if updates:
        # 每次循环后保存数据，确保更新被持久化
        data.to_csv('../resources/result_obj.csv', index=False)
