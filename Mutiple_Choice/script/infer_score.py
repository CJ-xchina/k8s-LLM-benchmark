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


# 定义一个函数，使用GPT-3.5获取分数
def get_gpt_scores(text, score_column):
    column = score_column.replace('_score', '')
    global time, status  # 使用全局变量以便在函数内修改
    prompt = prompt_text.format(answer=text['answer'], GPT=text[column])

    # 检查是否需要更改浏览器状态
    if time % 4 == 0:
        status = 'edge' if status == 'chrome' else 'chrome'  # 切换状态
        fresh = True
        vpn_fresh = True
    else:
        fresh = False
        vpn_fresh = False

    scores = []
    status = 'edge'
    try:
        # 根据已有数据情况决定获取分数的次数
        existing_scores = str(text[score_column]).split(',') if pd.notna(text[score_column]) else []
        num_scores = 3 - len(existing_scores)
        for _ in range(num_scores):
            simulated_output = use_client(prompt, status=status, vpn_fresh=vpn_fresh, fresh=fresh)
            score = extract_score(simulated_output)
            if score is not None:
                scores.append(score)
    except Exception as e:
        print(f"An error occurred: {e}")
        scores = [None, None, None]

    time += 1  # 每次调用后递增time

    return existing_scores + scores


def extract_score(output):
    output = str(output)
    # 尝试匹配 "Overall Score: 100" 格式
    match = re.search(r'Overall Score: (\d+)', output)
    if match:
        return int(match.group(1))

    # 尝试匹配单独的数字
    match = re.search(r'\b(\d{1,2}|100)\b', output)
    if match:
        return int(match.group(1))

    # 如果没有找到匹配的分数，返回 None 或者你想要的默认值
    return None


# 获取所有以'_score'结尾的列
score_columns = [col for col in data.columns if col.endswith('_score')]

# 获取并保存分数
for index, row in data.iterrows():
    for column in score_columns:
        if pd.isna(row[column]) or len(str(row[column]).split(',')) < 3:
            if pd.isna(row[column.replace('_score', '')]):
                continue
            scores = get_gpt_scores(row, column)
            data.at[index, column] = ','.join(map(str, filter(None, scores)))  # 过滤掉 None 值
            # 每次循环保存一次数据
            data.to_csv('../resources/result_obj.csv', index=False)
            break  # 获取到分数后直接跳出循环
