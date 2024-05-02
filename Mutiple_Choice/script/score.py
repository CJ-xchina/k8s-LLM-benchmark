import pandas as pd

from utils.GPT_client import use_client

prompt_file_path = '../resources/prompt/prompt_score_objective_question.txt'

# 读取CSV文件
data = pd.read_csv('../resources/result_obj.csv')
with open(prompt_file_path, 'r', encoding='utf-8') as f:
    prompt_text = f.read()

time = 0
status = 'chrome'


# 定义一个函数，使用GPT-3.5获取分数
def get_gpt_score(text):
    global time, status  # 使用全局变量以便在函数内修改
    prompt = prompt_text.format(answer=text['answer'], GPT=text['GPT-3.5'])

    # 检查是否需要更改浏览器状态
    if time % 4 == 0:
        status = 'edge' if status == 'chrome' else 'chrome'  # 切换状态
        fresh = True
        vpn_fresh = True
    else:
        fresh = False
        vpn_fresh = False
    try:
        simulated_output = use_client(prompt, status=status, vpn_fresh=vpn_fresh, fresh=fresh)
    except Exception as e:
        simulated_output = ''
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()  # 打印堆栈跟踪

    time += 1  # 每次调用后递增time
    return simulated_output


while True:
    for index, row in data.iterrows():
        if pd.isna(row['GPT-3.5_score']):
            score = get_gpt_score(row)
            data.at[index, 'GPT-3.5_score'] = score
            # 每次循环保存一次数据
            data.to_csv('../resources/result_obj.csv', index=False)

print("CSV file has been updated with GPT-3.5 scores.")
