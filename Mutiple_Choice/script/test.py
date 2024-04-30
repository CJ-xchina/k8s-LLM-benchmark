import time

import pyautogui
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
            if max_val >= 0.7:
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


click_input_line = f'../images/click_input_line'
# find_and_click(click_input_line)
pyperclip.copy('1231')
time.sleep(1)

pyperclip.paste()
pyautogui.hotkey('ctrl','v')
