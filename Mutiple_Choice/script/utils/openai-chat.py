import openai

# 填写你的 API 秘钥
openai.api_key = "sk-o7ZNAZAXjyVxG0hU62Fa6288B8Ab42Ab823f7e4cCf454eC9"

import os

os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"
def chat_gpt(prompt):
    # 调用新的 ChatGPT 接口
    response = openai.Completion.create(
        model="gpt-3.5-turbo",  # 指定模型，如果有新版本也可以更换
        messages=[{"role": "system", "content": "你好，请开始你的表演。"},
                  {"role": "user", "content": prompt}],
        max_tokens=1024
    )

    # 打印响应内容
    print(response['choices'][0]['message']['content'])


# 使用示例
chat_gpt("hello")
