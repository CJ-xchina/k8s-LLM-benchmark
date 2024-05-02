import json
import pandas as pd

# 加载JSON数据，每行一个JSON对象
def load_json(json_file):
    question_map = {}
    with open(json_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line)
            question_map[data['id']] = data['question']
    return question_map

# 加载CSV文件，并合并问题
def merge_questions_to_csv(json_file, csv_file, output_csv_file):
    # 加载json数据，构建id到question的映射
    question_map = load_json(json_file)

    # 读取CSV文件
    df = pd.read_csv(csv_file)

    # 根据ID将问题从JSON映射到CSV的answer列
    df['answer'] = df['id'].map(question_map)

    # 保存修改后的CSV文件
    df.to_csv(output_csv_file, index=False)


# 指定文件路径
json_file = '../resources/questions.json'
csv_file = '../resources/result_obj.csv'
output_csv_file = csv_file

# 调用函数
merge_questions_to_csv(json_file, csv_file, output_csv_file)
