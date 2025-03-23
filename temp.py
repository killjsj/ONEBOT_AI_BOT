from openai import OpenAI
import os

# 初始化OpenAI客户端
client = OpenAI(
    api_key = "sk-22592043dcef4e089c2e62cb613f74b1", 
    base_url ="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

reasoning_content = ""  # 定义完整思考过程
answer_content = ""     # 定义完整回复
is_answering = False   # 判断是否结束思考过程并开始回复

messages = []
conversation_idx = 1
while True:
    print("="*20+f"第{conversation_idx}轮对话"+"="*20)
    conversation_idx += 1
    user_msg = {"role": "user", "content": input("请输入你的消息：")}
    messages.append(user_msg)
    # 创建聊天完成请求
    completion = client.chat.completions.create(
        model="qwq-32b",  # 此处以 qwq-32b 为例，可按需更换模型名称
        messages=messages,
        # QwQ 模型仅支持流式输出方式调用
        stream=True
    )
    print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    for chunk in completion:
        # 如果chunk.choices为空，则打印usage
        if not chunk.choices:
            print("\nUsage:")
            print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            # 打印思考过程
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                print(delta.reasoning_content, end='', flush=True)
                reasoning_content += delta.reasoning_content
            else:
                # 开始回复
                if delta.content != "" and is_answering is False:
                    print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    is_answering = True
                # 打印回复过程
                print(delta.content, end='', flush=True)
                answer_content += delta.content
    messages.append({"role": "assistant", "content": answer_content})
    print("\n")