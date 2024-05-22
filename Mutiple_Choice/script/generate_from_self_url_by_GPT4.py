import json
import os
import re
import shutil
from time import sleep

import pyautogui
import requests
from bs4 import BeautifulSoup

from utils.client import use_client

pyautogui.FAILSAFE = False

status = 'chrome'

time = 0
max_content = 10000


def clean_text(text):
    # 删除回车、换行符、制表符
    cleaned_text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

    # 删除多余的空格
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    # 删除标点符号
    cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)

    # 删除连续重复的字符（如多个连续的句号）
    cleaned_text = re.sub(r'([.?!])\1+', r'\1', cleaned_text)

    # 如果有其他需要删除的特殊字符，可以在这里添加相应的替换操作

    return cleaned_text


def get_page_text(url):
    try:
        # 发送HTTP请求获取页面内容
        response = requests.get(url)
        # 确认请求成功
        if response.status_code == 200:
            # 使用Beautiful Soup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            # 提取页面所有文本内容
            page_text = soup.get_text()
            return page_text
        else:
            print("Failed to fetch page. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", e)

        return None


def process_urls(output_file, prompt_generate_url, prompt_generate_question,
                 log_file='../resources/processed_urls.log'):
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as file:
            processed_urls = set(file.read().splitlines())
    else:
        processed_urls = set()

    total = 0
    # 首先使用prompt获取初始输出
    try:
        content = use_client(prompt_generate_url, target_chatbot='https://chatgpt.com/g/g-3w1rEXGE0-web-browser',
                             status='edge', only_md_json=True, long_output=True, )
        print(f"Initial content: \n {content}")
    except Exception as e:
        print(e)
    # 提取内容中的所有URL
    urls = re.findall(r'"url": "(https?://[^"]+)"', content)

    # 处理每个URL
    for url in urls:
        if url in processed_urls:
            print(f"Skipping {url} as it has been processed before.")
            continue

        print(f"Processing {url}")
        processed_urls.add(url)
        global time, status  # 使用全局变量以便在函数内修改
        # 检查是否需要更改浏览器状态
        if time % 8 == 0:
            status = 'edge' if status == 'chrome' else 'chrome'  # 切换状态
            fresh = True
            vpn_fresh = False
        else:
            fresh = False
            vpn_fresh = False

        # 为每个URL获取内容
        try:
            # 这里需要根据实际情况实现获取URL内容的逻辑
            # 假设我们已经有了url_content
            url_content = get_page_text(url)
            cleaned_url_content = clean_text(url_content)
            print(f"content of the page:{cleaned_url_content}")
            segments = [cleaned_url_content[i:i + max_content] for i in range(0, len(cleaned_url_content), max_content)]

            for i, segment in enumerate(segments):
                updated_prompt = prompt_generate_question + segment
                try:
                    content = use_client(updated_prompt, target_chatbot='https://chatgpt.com/?model=gpt-4',
                                         status='edge', vpn_fresh=vpn_fresh, fresh=fresh,
                                         only_md_json=True, long_output=True)
                except Exception:
                    continue

                time = time + 1
                with open(output_file, 'a', encoding='utf-8') as out_file:
                    out_file.write(content)
                print(f"Written to {output_file}. content is : \n {content}")

                total += 1
        except Exception as e:
            print(f'Error processing URL {url}: {e}')

    # 将处理过的URL写入日志文件
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write('\n'.join(processed_urls) + '\n')

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


while True:
    # 在脚本开始前暂停5秒以允许准备
    sleep(5)
    input_folder = '/home/cjx/project/learning-k8s-source-code'
    output_file = '../resources/ops_data_en_improve.jsonl'
    with open('../resources/prompt/prompt_extract_multiple_choice.txt', 'r', encoding='utf-8') as file:
        prompt_generate_question = file.read()
    with open('../resources/prompt/prompt_generate_url.txt', 'r', encoding='utf-8') as file:
        prompt_generate_url = file.read()

    # 处理URL并修改JSON
    total_processed = process_urls(output_file, prompt_generate_url, prompt_generate_question)
    print(f"Total processed: {total_processed}")

    # 修改JSON文件，为每个JSON对象添加ID
    modify_json_in_place_with_ids(output_file)
