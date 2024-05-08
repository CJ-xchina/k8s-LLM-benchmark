import json

import pandas as pd

from utils.client import generate_completion


def read_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        print("CSV文件读取成功")
        return df
    except FileNotFoundError:
        print("CSV文件不存在")
        return None


def input_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f]
        print("JSON文件读取成功")
        return data
    except FileNotFoundError:
        print("JSON文件不存在")
        return None


def find_and_write(df, input_data, model_name, prompt_text, fresh=True):
    empty_indexes = df[df[model_name].isna()].index
    if not empty_indexes.empty:
        empty_index = empty_indexes[0]
        empty_id = df.at[empty_index, 'id']
        question_data = next(item for item in input_data if item["id"] == empty_id)
        prompt_text = prompt_text.format(**question_data)
        try:
            # simulated_output = use_client(prompt_text, status='chrome', vpn_fresh=False, fresh=fresh)
            simulated_output = generate_completion(prompt_text)
            print(f"model output is : {simulated_output}")
        except Exception as e:
            simulated_output = ''
            print(f"An error occurred: {e}")
            # 可选：打印更多关于异常的信息
            import traceback
            traceback.print_exc()  # 这将打印堆栈跟踪，有助于调试

        df.at[empty_index, model_name] = simulated_output
    return df


def main(csv_file_path, json_file_path, model_name, infer_type='multiple_choice'):
    if infer_type == 'multiple_choice':
        prompt_file_path = "../resources/prompt/prompt_infer_mutiple_choice_zero_shot.txt"
    elif infer_type == 'objective_question':
        prompt_file_path = '../resources/prompt/prompt_infer_objective_qustion.txt'

    df = read_csv(csv_file_path)
    if df is None:
        df = pd.DataFrame(columns=['id', 'answer'])

    # 获取题目
    input_data = input_json(json_file_path)
    if not input_data:
        return
    # 获取提示词
    with open(prompt_file_path, 'r', encoding='utf-8') as f:
        prompt_text = f.read()

    # 添加新行
    df = new_json_line(df, input_data)

    if model_name not in df.columns:
        df[model_name] = None
        if infer_type == 'objective_question':
            df[model_name + '_score'] = None

    time = 0
    while df[model_name].isna().any():
        fresh = time % 4 == 0
        df = find_and_write(df, input_data, model_name, prompt_text, fresh)
        df.to_csv(csv_file_path, index=False)
        time = time + 1
        print("结果已写入CSV文件")


def new_json_line(df, json_data):
    for json_obj in json_data:
        id = json_obj['id']
        answer = json_obj['answer']
        if id in df['id'].values:
            # 更新已存在的行
            df.loc[df['id'] == id, 'answer'] = answer
        else:
            # 添加新行
            new_row = {'id': id, 'answer': answer}
            df = df._append(new_row, ignore_index=True)
    return df


if __name__ == "__main__":
    csv_file_path = "../resources/result.csv"
    json_file_path = "../resources/ops_data_en_improve.jsonl"
    model_names = "Mistral-7B-instruct-v2"
    main(csv_file_path, json_file_path, model_names, infer_type='multiple_choice')
