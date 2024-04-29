import json
import os
import shutil
import time
from time import sleep

import cv2
import numpy as np
import pyautogui
import pyperclip

pyautogui.FAILSAFE = False

status = ''


def find_and_click(image_path, time_limit=2, double_click=False):
    start_time = time.time()  # 开始时间

    while True:
        # 当前时间与开始时间的差
        elapsed_time = time.time() - start_time

        # 如果超过了时间限制，则退出循环
        if elapsed_time > time_limit:
            print(f"Time limit exceeded, image {image_path} not found.")
            return False

        # 屏幕截图
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # 加载目标图片
        template = cv2.imread(image_path)

        # 模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 如果匹配值过低，表示没有找到图片
        if max_val >= 0.8:
            # 计算目标位置
            w, h = template.shape[:-1][::-1]
            x, y = max_loc[0] + w // 2, max_loc[1] + h // 2

            # 移动鼠标并点击
            pyautogui.moveTo(x, y, duration=0.1)
            if double_click:
                pyautogui.doubleClick()
            else:
                pyautogui.click()
            time.sleep(2)
            return True

        # 等待0.5秒后再次尝试
        time.sleep(0.5)


def find_and_click_paste(image_path):
    find_and_click(image_path)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')


def wait_until_image_appears(image_path, timeout=90, check_interval=0.5):
    """
    等待直到指定的图片出现在屏幕上。
    :param image_path: 要检测的图片文件路径
    :param timeout: 等待的最长时间（秒）
    :param check_interval: 检查间隔时间（秒）
    :return: 如果找到图片则返回True，超时则返回False
    """
    start_time = time.time()  # 开始时间记录

    while True:
        # 检查是否超时
        if time.time() - start_time > timeout:
            print("Timeout: Image not found on the screen.")
            return False

        # 屏幕截图
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # 加载目标图片
        template = cv2.imread(image_path)
        if template is None:
            raise ValueError("Image file not found at the provided path.")

        # 模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 检查是否找到了足够匹配的图片
        if max_val >= 0.8:
            print("Image found on the screen.")
            return True

        # 等待下一次检查
        time.sleep(check_interval)
    return False


def process_markdown_files(input_file, output_file, prompt, log_file='processed_files.log'):
    # 点击输入栏
    click_input_line = f'./images/{status}/click_input_line.png'
    # 产生对话按钮
    generating_button = f'./images/{status}/generating_button.png'
    # 回到最下端按钮
    go_to_down_button = f'./images/{status}/go_to_down_button.png'
    # 新的对话按钮
    new_chat_button = f'./images/{status}/new_chat.png'

    # 粘贴按钮
    paste_button = f'./images/{status}/paste_button.png'
    # 选中chat-bot按钮
    target_chat_bot = f'./images/{status}/target_chat_bot.png'
    # 刷新按钮
    fresh_button = f'./images/{status}/refresh_button.png'

    # 系统界面关闭
    sys_cancel = f'./images/{status}/sys_cancel.png'

    # 输出结束
    start_intput = f'./images/{status}/start_input.png'

    # 标题
    title = f'./images/{status}/title.png'
    regenerate = f'./images/{status}/regenerate.png'
    refresh_vpn = f'./images/{status}/refresh_vpn.png'
    max_time = f'./images/{status}/max_time.png'
    ms = f'./images/{status}/ms.png'

    status_map = {
        'chrome': './images/chrome/chrome.png',
        'edge': './images/edge/edge.png'
    }

    # 取消系统页面
    find_and_click(sys_cancel)

    # 点击浏览器
    if find_and_click(fresh_button) == False:
        find_and_click(status_map[status])

    # 刷新vpn网络
    find_and_click(refresh_vpn, time_limit=8)
    time.sleep(7)
    find_and_click(ms, time_limit=5, double_click=True)

    # 刷新
    find_and_click(fresh_button)
    # 找到对话
    find_and_click(target_chat_bot)
    # 打开新对话
    find_and_click(new_chat_button)

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

    pyperclip.copy(updated_prompt)
    find_and_click_paste(click_input_line)
    # 出现网络故障，无法发送消息
    if not wait_until_image_appears(generating_button, timeout=10):
        print("Error occur because of network")
        return 1
    # GPT4.0 回答已经达到上限
    if wait_until_image_appears(max_time, timeout=10):
        print("time access limit in GPT4.0 model , wait 30 minutes")
        time.sleep(3000)
        return 1
    # 等待生成完毕
    wait_until_image_appears(start_intput)  # Check the specific pixel for color change

    # 执行最多1次继续生成
    for i in range(2):
        pyautogui.click(1522, 883)
        wait_until_image_appears(start_intput)
    find_and_click(title)
    pyautogui.scroll(50)
    find_and_click(go_to_down_button)
    find_and_click(paste_button)
    content = pyperclip.paste()
    if content == updated_prompt:
        print("Error encountered, skipping this file.")
        return 1
    if '```json' in content:
        start_idx = content.find('```json') + len('```json')
        end_idx = content.find('```', start_idx)
        content = content[start_idx:end_idx].strip()
    else:
        content = ''
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
