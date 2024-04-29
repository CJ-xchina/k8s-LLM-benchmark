import json
import os
import shutil
from time import sleep

import pyautogui
from utils.GPT_client import use_client

pyautogui.FAILSAFE = False

status = ''


def process_markdown_files(input_file, output_file, prompt, log_file='processed_files.log'):
    next_id = 1
    # 获取下一次输出id
    try:
        with open(output_file, 'r') as file:
            for line in file:
                try:
                    json_obj = json.loads(line.strip())
                    if 'id' in json_obj and json_obj['id'] >= next_id:
                        next_id = json_obj['id'] + 1
                except json.JSONDecodeError:
                    continue

    except FileNotFoundError:
        pass  # If file not found, we start with ID 1

    # Reading input JSON file and processing in batches of 4
    valid_jsons = []
    batch_count = 0
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            if batch_count >= 8:
                break
            line = line.strip()
            if line:
                try:
                    json_obj = json.loads(line)
                    cur_id = json_obj['id']
                    if cur_id != next_id:
                        continue
                    next_id += 1
                    valid_jsons.append(json_obj)
                    batch_count += 1
                except json.JSONDecodeError:
                    continue
    total = 0

    updated_prompt = prompt
    # Use valid_jsons as the content to process
    for json_obj in valid_jsons:
        updated_prompt = updated_prompt + json.dumps(json_obj)

    content = ''
    try:
        content = use_client(updated_prompt, status, only_md_json=True)
    except Exception:
        return 1

    # Append JSON data to output file
    with open(output_file, 'a', encoding='utf-8') as out_file:
        out_file.write(content)
    print(f"Written to {output_file}.")
    total += 1
    if total > 3:
        return total
    return total


def modify_json_in_place_with_ids(file_path):
    # 读取并暂存所有有效的JSON对象
    valid_jsons = []
    next_id = 1  # 开始的ID
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:  # 忽略空行
                try:
                    # 尝试解析JSON
                    json_obj = json.loads(line)
                    # 更新id字段
                    json_obj['id'] = next_id
                    next_id += 1
                    # 转回字符串格式，暂存
                    json_str = json.dumps(json_obj)
                    valid_jsons.append(json_str)
                except json.JSONDecodeError:
                    # 忽略无法解析的行
                    continue

    # 将处理后的数据写回同一文件
    with open(file_path, 'w') as file:
        for json_str in valid_jsons:
            file.write(json_str + '\n')


def replace_original_file(original_file, new_file):
    """替换原始文件"""
    if not os.path.exists(new_file):
        print("临时文件不存在！")
        return

    os.remove(original_file)
    shutil.move(new_file, original_file)


# 在脚本开始前暂停5秒以允许准备
sleep(5)
input_file = 'ops_data_en.jsonl'
output_file = 'ops_data_en_improve.jsonl'
with open('./prompt_improve_score.txt', 'r', encoding='utf-8') as file:
    prompt = file.read()

t = 0
while True:
    if t % 2 != 0:
        status = 'chrome'
    else:
        status = 'edge'
    t = t + 1
    ret = process_markdown_files(input_file, output_file, prompt)
    modify_json_in_place_with_ids(output_file)
    if ret == 0:
        break
print("Processing completed!!!")

quit()
