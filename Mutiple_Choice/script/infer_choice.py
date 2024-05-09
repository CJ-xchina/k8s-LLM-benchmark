import json
import re
from collections import Counter

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


def extract_answer(response_answer):
    patterns = [
        r"^选([A-DN])",
        r"^选项([A-DN])",
        r"答案是\s*选?项?\s?([A-DN])",
        r"答案为\s*选?项?\s?([A-DN])",
        r"答案应为\s*选?项?\s?([A-DN])",
        r"答案选\s*选?项?\s?([A-DN])",
        r"答案是:\s*选?项?\s?([A-DN])",
        r"答案应该是:\s*选?项?\s?([A-DN])",
        r"正确的一项是\s*([A-DN])",
        r"答案为:\s*选?项?\s?([A-DN])",
        r"答案应为:\s*选?项?\s?([A-DN])",
        r"答案:\s*选?项?\s?([A-DN])",
        r"答案是：\s*选?项?\s?([A-DN])",
        r"答案应该是：\s*选?项?\s?([A-DN])",
        r"答案为：\s*选?项?\s?([A-DN])",
        r"答案应为：\s*选?项?\s?([A-DN])",
        r"答案：\s*选?项?\s?([A-DN])",
        r"answer\s+is\s*([A-DN])",
        r"answer\s+is\s+\(([A-DN])\)",
        r"answer\s+is\s+\(([A-DN])\)",
        r"answer\s+is\s?:\s+([A-DN])",
        r"answer\s+is\s?:\s+([A-DN])",
        r"answer\s+is\s?:\s+(([A-DN]))",
        r"answer\s+is\s?:\s+(([A-DN]))",
        r"^([A-DN])\sis\s+the\s+answer",
        r"^([A-DN])\sis\s+correct",
        r"^([A-DN])\sis\s+the\s+correct\s+answer",
        r"^([A-DN])\sis\s+the\s+right\s+answer",
        r"^([A-DN])\sis\s+correct\s+choice",
        r"^([A-DN])\sis\s+the\s+correct\s+choice",
        r"^([A-DN])\sis\s+the\s+right\s+choice",
        r"^([A-DN])\sis\s+the\s+correct\s+option",
        r"^([A-DN])\sis\s+the\s+right\s+option",
        r"^([A-DN])\sis\s+the\s+correct\s+option",
        r"^([A-DN])\sis\s+the\s+right\s+option",
        r"^([A-DN])\sis\s+the\s+correct\s+answer",
        r"^([A-DN])\sis\s+the\s+right\s+answer",
        r"^([A-DN])\sis\s+the\s+correct\s+response",
        r"^([A-DN])\sis\s+the\s+right\s+response",
        r"^([A-DN])\sis\s+the\s+correct\s+solution",
        r"^([A-DN])\sis\s+the\s+right\s+solution",
        r"^([A-DN])\sis\s+the\s+correct\s+selection",
        r"^([A-DN])\sis\s+the\s+right\s+selection",
        r"^([A-DN])\sis\s+correctly\s+selected",
        r"^([A-DN])\sis\s+the\s+correctly\s+selected\s+answer",
        r"^([A-DN])\sis\s+the\s+correctly\s+selected\s+choice",
        r"^([A-DN])\sis\s+the\s+correctly\s+selected\s+option",
        r"^([A-DN])\sis\s+the\s+correctly\s+selected\s+option",
        r"^([A-DN])\sis\s+the\s+correctly\s+selected\s+answer",
        r"^([A-DN])\sis\s+the\s+selected\s+option",
        r"^([A-DN])\sis\s+the\s+selected\s+answer",
        r"^([A-DN])\sis\s+precise",
        r"^([A-DN])\sis\s+right",
        r"^([A-DN])\sis\s+correctly\s+specified",
        r"^([A-DN])\sis\s+specified\s+correctly",
        r"^([A-DN])\sis\s+correctly\s+defined",
        r"^([A-DN])\sis\s+defined\s+correctly",
        r"^([A-DN])\sis\s+correctly\s+answered",
        r"^([A-DN])\sis\s+answered\s+correctly",
        r"^([A-DN])\sis\s+the\s+answer",
        r"^([A-DN])\sis\s+correctly\s+the\s+answer",
        r"^([A-DN])\sis\s+the\s+answer",
        r"^([A-DN])\sis\s+the\s+answer\s+to\s+the\s+question",
        r"^([A-DN])\sis\s+the\s+correct\s+answer\s+to\s+the\s+question",
        r"^([A-DN])\sis\s+the\s+right\s+answer\s+to\s+the\s+question",
        r"^([A-DN])\sis\s+the\s+right\s+answer\s+to\s+this\s+question",
        r"^([A-DN])\sis\s+the\s+correct\s+answer\s+to\s+this\s+question",
        r"^([A-DN])\sis\s+the\s+selected\s+answer\s+to\s+the\s+question",
        r"^([A-DN])\sis\s+the\s+chosen\s+answer\s+to\s+the\s+question",
        r"^([A-DN])\sis\s+the\s+preferred\s+answer\s+to\s+the\s+question",
        r"^([A-DN])\sis\s+the\s+indicated\s+answer\s+to\s+the\s+question",
        r"^([A-DN])\sis\s+the\s+marked\s+answer\s+to\s+the\s+question",
        r"^([A-DN])\sis\s+the\s+correct\s+option",
        r"^([A-DN])\sis\s+the\s+right\s+option",
        r"^([A-DN])\sis\s+the\s+correct\s+choice",
        r"^([A-DN])\sis\s+the\s+right\s+choice",
        r"^([A-DN])\sis\s+the\s+correct\s+response",
        r"^([A-DN])\sis\s+the\s+right\s+response",
        r"^([A-DN])\sis\s+the\s+correct\s+solution",
        r"^([A-DN])\sis\s+the\s+right\s+solution",
        r"^([A-DN])\sis\s+the\s+correct\s+selection",
        r"^([A-DN])\sis\s+the\s+right\s+selection",
        r"^([A-DN])\sis\s+the\s+correctly\s+selected\s+option",
        r"^([A-DN])\sis\s+the\s+correctly\s+selected\s+choice",
        r"^([A-DN])\sis\s+the\s+correctly\s+selected\s+answer",
        r"^([A-DN])\sis\s+the\s+selected\s+option",
        r"^([A-DN])\sis\s+the\s+selected\s+choice",
        r"^([A-DN])\sis\s+the\s+selected\s+answer",
        r"^([A-DN])\sis\s+the\s+chosen\s+option",
        r"^([A-DN])\sis\s+the\s+chosen\s+choice",
        r"^([A-DN])\sis\s+the\s+chosen\s+answer",
        r"^([A-DN])\sis\s+the\s+preferred\s+option",
        r"^([A-DN])\sis\s+the\s+preferred\s+choice",
        r"^([A-DN])\sis\s+the\s+preferred\s+answer",
        r"^([A-DN])\sis\s+the\s+indicated\s+option",
        r"^([A-DN])\sis\s+the\s+indicated\s+choice",
        r"^([A-DN])\sis\s+the\s+indicated\s+answer",
        r"^([A-DN])\sis\s+the\s+marked\s+option",
        r"^([A-DN])\sis\s+the\s+marked\s+choice",
        r"^([A-DN])\sis\s+the\s+marked\s+answer",
        r"^([A-DN])\sis\s+the\s+correct\s+answer",
        r"^([A-DN])\sis\s+the\s+right\s+answer",
        r"^([A-DN])\sis\s+correct",
        r"^([A-DN])\sis\s+accurate",
        r"^([A-DN])\sis\s+precise",
        r"^([A-DN])\sis\s+right",
        r"^([A-DN])\sis\s+the\s+correct\s+option",
        r"^([A-DN])\sis\s+the\s+right\s+option",
        r"^([A-DN])\sis\s+correctly\s+selected",
        r"^([A-DN])\sis\s+the\s+correctly\s+selected\s+answer",
        r"^([A-DN])\sis\s+the\s+correctly\s+selected\s+choice",
        r"^([A-DN])\sis\s+the\s+correctly\s+selected\s+option",
        r"^([A-DN])\sis\s+the\s+selected\s+option",
        r"^([A-DN])\sis\s+the\s+selected\s+answer",
        r"^([A-DN])\sis\s+the\s+selected\s+choice",
        r"^([A-DN])\sis\s+the\s+chosen\s+option",
        r"^([A-DN])\sis\s+the\s+chosen\s+choice",
        r"^([A-DN])\sis\s+the\s+chosen\s+answer",
        r"^([A-DN])\sis\s+the\s+preferred\s+option",
        r"^([A-DN])\sis\s+the\s+preferred\s+choice",
        r"^([A-DN])\sis\s+the\s+preferred\s+answer",
        r"^([A-DN])\sis\s+the\s+indicated\s+option",
        r"^([A-DN])\sis\s+the\s+indicated\s+choice",
        r"^([A-DN])\sis\s+the\s+indicated\s+answer",
        r"^([A-DN])\sis\s+the\s+marked\s+option",
        r"^([A-DN])\sis\s+the\s+marked\s+choice",
        r"^([A-DN])\sis\s+the\s+marked\s+answer",
    ]

    results = []
    for pattern in patterns:
        matches = re.findall(pattern, response_answer)
        results.extend(matches)

    if results:
        counter = Counter(results)
        most_common = counter.most_common(1)
        final_result = most_common[0][0]

        if final_result in ['A', 'B', 'C', 'D', 'N']:
            return final_result

    return ''  # 默认返回 'N'


def find_and_write(df, input_data, model_name, prompt_text, fresh=True, multiple_choice=True):
    empty_indexes = df[df[model_name].isna()].index
    if not empty_indexes.empty:
        empty_index = empty_indexes[0]
        empty_id = df.at[empty_index, 'id']
        question_data = next(item for item in input_data if item["id"] == empty_id)
        prompt_text = prompt_text.format(**question_data)
        try:
            # simulated_output = use_client(prompt_text, status='chrome', vpn_fresh=False, fresh=fresh)
            print(f"prompt is : {prompt_text}")
            simulated_output = generate_completion(prompt_text)
            last_inst_index = simulated_output.rfind("[/INST]")
            last_s_index = simulated_output.rfind("</s>")
            str_back = simulated_output[last_inst_index + 7:last_s_index].strip()

            # 提取选择题答案
            if multiple_choice:
                str_back = extract_answer(str_back)
            print(f"model output is: {str_back}")
        except Exception as e:
            str_back = ''
            print(f"An error occurred: {e}")
            # 可选：打印更多关于异常的信息
            import traceback
            traceback.print_exc()  # 这将打印堆栈跟踪，有助于调试

        df.at[empty_index, model_name] = str_back
    return df


def main(csv_file_path, json_file_path, model_name, infer_type='multiple_choice'):
    multiple_choice = False
    if infer_type == 'multiple_choice':
        prompt_file_path = "../resources/prompt/prompt_infer_mutiple_choice_zero_shot.txt"
        multiple_choice = True
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
        df = find_and_write(df, input_data, model_name, prompt_text, fresh, multiple_choice=multiple_choice)
        df.to_csv(csv_file_path, index=False)
        time = time + 1
        print("结果已写入CSV文件")


def new_json_line(df, json_data):
    for json_obj in json_data:
        id = json_obj['id']
        answer = json_obj.get('answer', json_obj.get('question', ''))  # 如果没有'answer'，则使用'question'，如果都没有，则为空字符串
        if id in df['id'].values:
            # 更新已存在的行
            df.loc[df['id'] == id, 'answer'] = answer
        else:
            # 添加新行
            new_row = {'id': id, 'answer': answer}
            df = df._append(new_row, ignore_index=True)
    return df


if __name__ == "__main__":
    csv_file_path = "../resources/result_obj.csv"
    json_file_path = "../resources/questions.json"
    model_names = "Mistral-7B-instruct-v2"
    main(csv_file_path, json_file_path, model_names, infer_type='objective_question')
