def process_message(data):
    # 提取必要字段
    self_id = data['self_id']  # 机器人自己的 ID
    raw_message = data['raw_message']  # 原始消息
    message = data['message']  # 消息数组

    # 检查是否包含 "type=at" 且 "qq=self_id"
    has_self_at = any(
        item['type'] == 'at' and str(item['data']['qq']) == str(self_id)
        for item in message
    )

    if not has_self_at:
        # 如果没有匹配的 "at"，直接返回 None
        return None

    # 从 raw_message 中移除 reply 和匹配的 at
    # 1. 移除 reply
    for item in message:
        if item['type'] == 'reply':
            raw_message = raw_message.replace(
                f"[CQ:reply,id={item['data']['id']}]", "", 1
            )
            break  # 只移除第一个 reply

    # 2. 移除第一个匹配 self_id 的 at
    for item in message:
        if item['type'] == 'at' and str(item['data']['qq']) == str(self_id):
            raw_message = raw_message.replace(
                f"[CQ:at,qq={item['data']['qq']},name={item['data'].get('name', '')}]",
                "",
                1,
            )
            break  # 只移除第一个匹配的 at

    # 返回清理后的消息，去掉首尾空格
    return raw_message.strip()


# 示例数据
data = {
    'self_id': 3193986128,
    'user_id': 1020120106,
    'time': 1732354109,
    'message_id': 1776322940,
    'real_id': 1776322940,
    'message_seq': 1776322940,
    'message_type': 'group',
    'sender': {
        'user_id': 1020120106,
        'nickname': '小恩恩',
        'card': 'killjsj',
        'role': 'owner',
        'title': '糖',
    },
    'raw_message': '[CQ:reply,id=1222571017][CQ:at,qq=3193986127,gf][CQ:at,qq=3193986128,name=a] asa a [CQ:at,qq=3889023973,name=可爱小春] a dsada',
    'font': 14,
    'sub_type': 'normal',
    'message': [
        {'type': 'reply', 'data': {'id': '1222571017'}},
        {'type': 'at', 'data': {'qq': '3193986128', 'name': 'a'}},
        {'type': 'text', 'data': {'text': ' asa a '}},
        {'type': 'at', 'data': {'qq': '3889023973', 'name': '可爱小春'}},
        {'type': 'text', 'data': {'text': ' a dsada'}},
    ],
    'message_format': 'array',
    'post_type': 'message',
    'group_id': 719501584,
}

# 调用函数
result = process_message(data)
print(result)  # 输出结果
