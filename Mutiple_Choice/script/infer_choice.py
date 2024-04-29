import json
import pandas as pd
from utils.GPT_client import use_client

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

def append_to_csv(df, new_data, model_name):
    max_id = int(df['id'].max()) if not df.empty else 0
    new_ids = list(range(max_id + 1, max(item["id"] for item in new_data) + 1))
    new_rows = [{'id': new_id, 'answer': item['answer']} for new_id, item in zip(new_ids, new_data)]
    df = df._append(new_rows, ignore_index=True)
    if model_name not in df.columns:
        df[model_name] = None
    return df

def find_and_write(df, input_data, model_name, prompt_text):
    empty_indexes = df[df[model_name].isna()].index
    if not empty_indexes.empty:
        empty_index = empty_indexes[0]
        empty_id = df.at[empty_index, 'id']
        question_data = next(item for item in input_data if item["id"] == empty_id)
        prompt_text = prompt_text.format(**question_data)
        simulated_output = use_client(prompt_text, status='chrome', vpn_fresh=False)
        df.at[empty_index, model_name] = simulated_output
    return df, prompt_text

def main(csv_file_path, json_file_path, model_name, prompt_file_path):
    df = read_csv(csv_file_path)
    if df is None:
        df = pd.DataFrame(columns=['id', 'answer'])
    input_data = input_json(json_file_path)
    if not input_data:
        return
    with open(prompt_file_path, 'r', encoding='utf-8') as f:
        prompt_text = f.read()
    df = append_to_csv(df, input_data, model_name)
    while df[model_name].isna().any():
        df, prompt = find_and_write(df, input_data, model_name, prompt_text)
        if prompt:
            print("Prompt:", prompt)
        else:
            break
        df.to_csv(csv_file_path, index=False)
        print("结果已写入CSV文件")

if __name__ == "__main__":
    csv_file_path = "../resources/result.csv"
    json_file_path = "../resources/ops_data_en_improve.jsonl"
    model_names = "GPT-3.5"
    prompt_file_path = "../resources/prompt/prompt_infer_mutiple_choice_zero_shot.txt"
    main(csv_file_path, json_file_path, model_names, prompt_file_path)
