import json
import shutil
from time import sleep

import pyautogui

from utils.client import use_client

pyautogui.FAILSAFE = False

status = 'chrome'

time = 0
import os


def process_markdown_files(input_folder, output_file, prompt, log_file='../resources/processed_files.log'):
    # 读取已处理的文件列表
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as file:
            processed_files = file.read().splitlines()
    else:
        processed_files = []
        # 如果日志文件不存在，则创建空的日志文件
        open(log_file, 'w').close()

    total = 0
    for root, dirs, files in os.walk(input_folder):
        for file_name in files:
            # if file_name.endswith('.md'):
                file_path = os.path.join(root, file_name)
                if file_path in processed_files:
                    print(f"Skipping {file_path} as it has been processed before.")
                    continue

                print(f"Processing {file_path}")
                with open(file_path, 'r', encoding='utf-8') as file:
                    input_text = file.read()

                if len(input_text) < 300:
                    continue
                updated_prompt = prompt + input_text
                global time, status  # 使用全局变量以便在函数内修改

                # 检查是否需要更改浏览器状态
                if time % 4 == 0:
                    status = 'edge' if status == 'chrome' else 'chrome'  # 切换状态
                    fresh = True
                    vpn_fresh = True
                else:
                    fresh = False
                    vpn_fresh = False

                try:
                    content = use_client(updated_prompt, status=status, vpn_fresh=vpn_fresh, fresh=fresh, only_md_json=True)
                except Exception:
                    return 1

                time = time + 1
                with open(output_file, 'a', encoding='utf-8') as out_file:
                    out_file.write(content)
                print(f"Written to {output_file}. content is : \n {content}")

                # 将处理过的文件路径添加到日志中
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(file_path + '\n')

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
input_folder = 'Z:\MY_FIELS\Project\Python\mistral-src\kubernetes-handbook-master'
output_file = '../resources/ops_data_en_improve.jsonl'
with open('../resources/prompt/prompt_extract_multiple_choice.txt', 'r', encoding='utf-8') as file:
    prompt = file.read()

while True:
    ret = process_markdown_files(input_folder, output_file, prompt)
    modify_json_in_place_with_ids(output_file)
    if ret == 0:
        break
print("Processing completed!!!")

quit()
