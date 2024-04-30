import time

import cv2
import numpy as np
import pyautogui
import pyperclip


import os

def find_and_click(folder_path, time_limit=2, double_click=False):
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



def find_and_click_paste(image_path, prompt):
    find_and_click(image_path)
    # pyautogui.typewrite(prompt)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')


import os

def wait_until_image_appears(folder_path, timeout=90, check_interval=0.5):
    """
    等待直到指定的图片出现在屏幕上。
    :param folder_path: 包含待匹配图片的文件夹路径
    :param timeout: 等待的最长时间（秒）
    :param check_interval: 检查间隔时间（秒）
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
            if max_val >= 0.5:
                return True

        # 等待下一次检查
        time.sleep(check_interval)

    return False



def use_client(prompt, status, only_md_json=False, vpn_fresh=True):
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
    # 选中chat-bot按钮
    target_chat_bot = f'../images/target_chat_bot'
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
        find_and_click(refresh_vpn, time_limit=3)
        time.sleep(7)
        find_and_click(ms, time_limit=3, double_click=True)

    # 刷新
    find_and_click(fresh_button)
    # 找到对话
    find_and_click(target_chat_bot)
    # 打开新对话
    find_and_click(new_chat_button)
    
    pyperclip.copy(prompt)
    
    find_and_click_paste(click_input_line, prompt=prompt)

    # 出现网络故障，无法发送消息
    if not wait_until_image_appears(generating_button, timeout=10):
        print("Error occur because of network")
        raise Exception("Error occur because of network")
    # GPT4.0 回答已经达到上限
    if wait_until_image_appears(max_time, timeout=10):
        print("time access limit in GPT4.0 model , wait 30 minutes")
        raise Exception("time access limit in GPT4.0 model , wait 30 minutes")

    # 等待生成完毕
    
    (start_intput)  # Check the specific pixel for color change

    # 执行最多1次继续生成
    for i in range(2):
        pyautogui.click(1522, 883)
        wait_until_image_appears(start_intput)
    find_and_click(title)
    pyautogui.scroll(50)
    find_and_click(go_to_down_button)
    find_and_click(paste_button)
    content = pyperclip.paste()

    if content == prompt:
        print("output equals input Error")
        raise Exception("output equals input Error")

    if only_md_json:
        if '```json' in content:
            start_idx = content.find('```json') + len('```json')
            end_idx = content.find('```', start_idx)
            content = content[start_idx:end_idx].strip()
        else:
            content = ''

    return content
