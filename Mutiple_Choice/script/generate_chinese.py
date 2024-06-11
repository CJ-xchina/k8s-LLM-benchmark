import json
import os

from utils.client import use_client

status = 'chrome'

time = 0


def process_jsonl_files(input_file, translated_file, prompt_file, N):
    # 检查翻译后的文件是否存在并读取内容
    if os.path.exists(translated_file):
        with open(translated_file, 'r', encoding='utf-8') as file:
            translated_data = [json.loads(line) for line in file if line.strip()]
    else:
        translated_data = []

    translated_ids = [item['id'] for item in translated_data]

    # 读取prompt文件
    with open(prompt_file, 'r', encoding='utf-8') as file:
        prompt = file.read()

    total = 0
    collected_data = []
    with open(input_file, 'r', encoding='utf-8') as file:
        for idx, line in enumerate(file):
            # 根据translated_ids的情况决定如何继续处理
            if translated_ids and idx < translated_ids[-1]:
                continue

            data = json.loads(line)
            collected_data.append(data)

            if len(collected_data) == N:
                global time, status  # 使用全局变量以便在函数内修改

                # 检查是否需要更改浏览器状态
                if time % 8 == 0:
                    status = 'edge' if status == 'chrome' else 'chrome'  # 切换状态
                    fresh = True
                    vpn_fresh = False
                else:
                    fresh = False
                    vpn_fresh = False

                # 拼接输入数据
                input_text = "\n".join([json.dumps(item) for item in collected_data])
                updated_prompt = prompt + input_text

                # 使用use_client处理数据
                try:
                    content = use_client(updated_prompt, status=status, vpn_fresh=vpn_fresh, fresh=fresh,
                                         only_md_jsonl=True, long_output=True)
                except Exception as e:
                    print(f"Error processing data: {e}")
                    return 1

                # 写入输出文件
                with open(translated_file, 'a', encoding='utf-8') as out_file:
                    out_file.write(content)

                total += 1
                time += 1
                collected_data = []  # 清空已处理的数据集合

            if total >= N:
                break

    return total


def update_translated_data(translated_file):
    with open(translated_file, 'r', encoding='utf-8') as file:
        translated_data = [json.loads(line) for line in file if line.strip()]

    seen_ids = set()
    unique_data = []
    for item in translated_data:
        if item['id'] not in seen_ids:
            unique_data.append(item)
            seen_ids.add(item['id'])

    with open(translated_file, 'w', encoding='utf-8') as file:
        for item in unique_data:
            file.write(json.dumps(item, ensure_ascii=False) + '\n')

    existing_ids = {item['id'] for item in unique_data}
    expected_ids = set(range(1, max(existing_ids) + 1))
    missing_ids = sorted(expected_ids - existing_ids)

    return missing_ids


# 调用示例
input_file = 'Z:\\MY_FIELS\\Project\\Python\\mistral-src\\k8s-benchmark\\Mutiple_Choice\\resources\\en\\questions.jsonl'
translated_file = 'Z:\\MY_FIELS\\Project\\Python\\mistral-src\\k8s-benchmark\\Mutiple_Choice\\resources\\zh\\questions.jsonl'
prompt_file = 'Z:\\MY_FIELS\\Project\\Python\\mistral-src\\k8s-benchmark\\Mutiple_Choice\\resources\\prompt\\prompt_translate.txt'
N = 15

while True:
    processed_count = process_jsonl_files(input_file, translated_file, prompt_file, N)
    print(f"Total processed: {processed_count}")

    if processed_count == 0:
        break

update_translated_data(translated_file)
