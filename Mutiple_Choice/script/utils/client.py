import time

import cv2
import numpy as np
import pyautogui
import pyperclip
import requests
from pydantic import BaseModel


def find_and_click(folder_path, time_limit=2, double_click=False, left_offset=0):
    start_time = time.time()  # 开始时间

    while True:
        # 当前时间与开始时间的差
        elapsed_time = time.time() - start_time

        # 如果超过了时间限制，则退出循环
        if elapsed_time > time_limit:
            print(f"Time limit exceeded, no image found in folder {folder_path}.")
            return False

        # 屏幕截图
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # 获取文件夹下所有 PNG 图片文件
        image_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
        if not image_files:
            raise ValueError("No PNG image files found in the provided folder.")

        # 对每张图片进行匹配检查
        for image_file in image_files:
            # 加载目标图片
            template_path = os.path.join(folder_path, image_file)
            template = cv2.imread(template_path)

            # 模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # 如果匹配值过低，表示没有找到图片
            if max_val >= 0.95:
                # 计算目标位置
                w, h = template.shape[:-1][::-1]
                x, y = max_loc[0] + w // 2, max_loc[1] + h // 2

                # 移动鼠标并点击
                pyautogui.moveTo(x + left_offset, y, duration=0.1)
                if double_click:
                    pyautogui.click()
                    pyautogui.click()
                else:
                    pyautogui.click()
                time.sleep(1)
                return True

        # 等待0.5秒后再次尝试
        time.sleep(0.5)


def find_and_click_paste(image_path, prompt, left_offset=0):
    pyperclip.copy(prompt)
    res = find_and_click(image_path, left_offset=left_offset)
    # pyautogui.typewrite(prompt)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    time.sleep(2)
    return res


import os


def wait_until_image_appears(folder_path, timeout=90, check_interval=0.5):
    """
    等待直到指定的图片出现在屏幕上。
    :param folder_path: 包含待匹配图片的文件夹路径
    :param timeout: 等待的最长时间(秒)
    :param check_interval: 检查间隔时间(秒)
    :return: 如果找到图片则返回True，超时则返回False
    """
    start_time = time.time()  # 开始时间记录

    # 获取文件夹下所有 PNG 图片文件
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
    if not image_files:
        raise ValueError("No PNG image files found in the provided folder.")

    while True:
        # 检查是否超时
        if time.time() - start_time > timeout:
            print(f"Timeout: Image folder {folder_path} not found  on the screen.")
            return False

        # 屏幕截图
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # 对每张图片进行匹配检查
        for image_file in image_files:
            # 加载目标图片
            template_path = os.path.join(folder_path, image_file)
            template = cv2.imread(template_path)
            if template is None:
                raise ValueError(f"Image file not found at the path: {template_path}")

            # 模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # 检查是否找到了足够匹配的图片
            if max_val >= 0.99:
                return True

        # 等待下一次检查
        time.sleep(check_interval)

    return False


def use_client(prompt, status, target_chatbot='https://chatgpt.com/?model=gpt-4o', only_md_json=False,
               only_md_jsonl=False, vpn_fresh=True,
               long_output=False, fresh=True):
    # 点击输入栏
    click_input_line = f'../images/click_input_line'
    # 产生对话按钮
    generating_button = f'../images/generating_button'
    # 回到最下端按钮
    go_to_down_button = f'../images/go_to_down_button'
    # 新的对话按钮
    new_chat_button = f'../images/new_chat'

    # 粘贴按钮
    paste_button = f'../images/paste_button'
    # 刷新按钮
    fresh_button = f'../images/refresh_button'

    # 系统界面关闭
    sys_cancel = f'../images/sys_cancel'

    # 输出结束
    start_intput = f'../images/start_input'

    # 标题
    title = f'../images/title'
    regenerate = f'../images/regenerate'
    refresh_vpn = f'../images/refresh_vpn'
    max_time = f'../images/max_time'
    ms = f'../images/ms'
    gpt_title = f"../images/GPT3.5"
    # 继续生存
    continue_generation = f'../images/continue_generation'

    #
    web_search = f"../images/web_search"
    status_map = {
        'chrome': '../images/chrome',
        'edge': '../images/edge'
    }
    # 取消系统页面
    find_and_click(sys_cancel)

    # 点击浏览器
    find_and_click(status_map[status])

    if vpn_fresh:
        # 刷新vpn网络
        find_and_click(refresh_vpn, time_limit=2)
        time.sleep(7)
        find_and_click(ms, time_limit=2, double_click=True)

    # 找到对话chatbot
    find_and_click_paste(fresh_button, target_chatbot, left_offset=200)

    # 刷新
    if fresh:
        find_and_click(fresh_button)

    # # 打开新对话
    # find_and_click(new_chat_button)

    # 出现网络故障，无法发送消息
    # if wait_until_image_appears(generating_button, timeout=4):
    #     print("Error occur because of network")
    #     # 点击浏览器
    #     find_and_click(status_map[status])
    #     raise Exception("Error occur because of network")

    # GPT4.0 回答已经达到上限
    # if wait_until_image_appears(max_time, timeout=3):
    #     print("time access limit in GPT4.0 model , wait 30 minutes")
    #     # 点击浏览器
    #     find_and_click(status_map[status])
    #     raise Exception("time access limit in GPT4.0 model , wait 30 minutes")
    time.sleep(5)
    find_and_click(new_chat_button)
    time.sleep(2)

    # GPT4o无法使用
    if find_and_click(gpt_title):
        # 点击浏览器
        find_and_click(status_map[status])
        raise Exception("Max use of this chatbot")
    # 加载出错
    if not find_and_click(click_input_line):
        print("Error occur because of errors")
        find_and_click(fresh_button)
        # 点击浏览器
        find_and_click(status_map[status])
        raise Exception("Error occur because of network")

    find_and_click_paste(click_input_line, prompt=prompt)

    wait_until_image_appears(start_intput, timeout=60)

    if long_output:
        while find_and_click(continue_generation):
            time.sleep(2)
            wait_until_image_appears(start_intput)

    # find_and_click(title)
    # pyautogui.scroll(20)

    # 无法定位到输入栏，认为出现错误！
    if not find_and_click(click_input_line):
        print("Error occur because of errors")
        find_and_click(fresh_button)
        # 点击浏览器
        find_and_click(status_map[status])
        raise Exception("Error occur because of network")

    find_and_click(go_to_down_button)
    find_and_click(paste_button)
    content = pyperclip.paste()

    if content == prompt:
        print("output equals input Error")
        find_and_click(status_map[status])
        raise Exception("output equals input Error")

    if only_md_json or only_md_jsonl:
        json_content = ''
        start_idx = 0
        while True:
            if '```json' in content[start_idx:]:
                start_idx = content.find('```json', start_idx) + len('```json')
                if only_md_jsonl:
                    start_idx += 1
                end_idx = content.find('```', start_idx)
                if end_idx != -1:
                    json_content += content[start_idx:end_idx].strip() + '\n'
                    start_idx = end_idx + len('```')
                else:
                    break
            else:
                break
        content = json_content
    # 点击浏览器
    find_and_click(status_map[status])
    return content


class CompletionRequest(BaseModel):
    prompt: str
    temperature: float = 0.2
    top_p: float = 0.9
    top_k: int = 40
    max_length: int = 512
    num_beams: int = 1
    repetition_penalty: float = 1.1
    do_sample: bool = True


def generate_completion(prompt: str):
    # Define the URL of the API endpoint
    url = "http://mp-660.default.ai.iscas:31050/predict"

    # Create an instance of the request body using passed prompt
    data = CompletionRequest(
        prompt=prompt,
        temperature=0.85,
        max_length=2000,
        num_beams=20,
        top_p=0.9,
        top_k=30,
        repetition_penalty=10000
    )

    # Convert the Pydantic model to a dictionary and then to JSON
    json_data = data.dict()

    # Make a POST request to the server
    response = requests.post(url, json=json_data)

    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()
        return response_json['choices'][0]['text']
    else:
        print("Failed to get response:", response.status_code)
        raise Exception('API returned non-successful status')
