import json

# 假设json_data是您提供的JSON字符串
json_data = '''
{
    "status": "ok",
    "retcode": 0,
    "data": [
        {
            "group_id": 719501584,
            "user_id": 1020120106,
            "nickname": "小恩恩",
            "card": "killjsj",
            "sex": "unknown",
            "age": 0,
            "area": "",
            "level": "1",
            "qq_level": 0,
            "join_time": 1699151159,
            "last_sent_time": 1732281660,
            "title_expire_time": 0,
            "unfriendly": false,
            "card_changeable": true,
            "is_robot": false,
            "shut_up_timestamp": 0,
            "role": "owner",
            "title": "糖"
        },
        {
            "group_id": 719501584,
            "user_id": 3889023427,
            "nickname": "机器人-测试中",
            "card": "机器人-测试中",
            "sex": "unknown",
            "age": 0,
            "area": "",
            "level": "1",
            "qq_level": 0,
            "join_time": 1724661691,
            "last_sent_time": 1724663780,
            "title_expire_time": 0,
            "unfriendly": false,
            "card_changeable": true,
            "is_robot": true,
            "shut_up_timestamp": 0,
            "role": "member",
            "title": ""
        },
        {
            "group_id": 719501584,
            "user_id": 2854196310,
            "nickname": "Q群管家",
            "card": "Q群管家",
            "sex": "unknown",
            "age": 0,
            "area": "",
            "level": "1",
            "qq_level": 0,
            "join_time": 1722755228,
            "last_sent_time": 1722755229,
            "title_expire_time": 0,
            "unfriendly": false,
            "card_changeable": true,
            "is_robot": true,
            "shut_up_timestamp": 0,
            "role": "admin",
            "title": ""
        },
        {
            "group_id": 719501584,
            "user_id": 2885842119,
            "nickname": "萝卜",
            "card": "萝卜",
            "sex": "unknown",
            "age": 0,
            "area": "",
            "level": "1",
            "qq_level": 0,
            "join_time": 1708418009,
            "last_sent_time": 1708418009,
            "title_expire_time": 0,
            "unfriendly": false,
            "card_changeable": true,
            "is_robot": false,
            "shut_up_timestamp": 0,
            "role": "member",
            "title": ""
        },
        {
            "group_id": 719501584,
            "user_id": 2854197266,
            "nickname": "AL_1S",
            "card": "AL_1S",
            "sex": "unknown",
            "age": 0,
            "area": "",
            "level": "1",
            "qq_level": 0,
            "join_time": 1721444279,
            "last_sent_time": 1724527086,
            "title_expire_time": 0,
            "unfriendly": false,
            "card_changeable": true,
            "is_robot": true,
            "shut_up_timestamp": 0,
            "role": "member",
            "title": ""
        },
        {
            "group_id": 719501584,
            "user_id": 3889023973,
            "nickname": "可爱小春",
            "card": "可爱小春",
            "sex": "unknown",
            "age": 0,
            "area": "",
            "level": "1",
            "qq_level": 0,
            "join_time": 1731252591,
            "last_sent_time": 1731494822,
            "title_expire_time": 0,
            "unfriendly": false,
            "card_changeable": true,
            "is_robot": true,
            "shut_up_timestamp": 0,
            "role": "member",
            "title": ""
        },
        {
            "group_id": 719501584,
            "user_id": 3889006601,
            "nickname": "幻梦",
            "card": "幻梦",
            "sex": "unknown",
            "age": 0,
            "area": "",
            "level": "1",
            "qq_level": 0,
            "join_time": 1731301755,
            "last_sent_time": 1731810258,
            "title_expire_time": 0,
            "unfriendly": false,
            "card_changeable": true,
            "is_robot": true,
            "shut_up_timestamp": 0,
            "role": "member",
            "title": ""
        },
        {
            "group_id": 719501584,
            "user_id": 3193986128,
            "nickname": "机器人",
            "card": "a",
            "sex": "unknown",
            "age": 0,
            "area": "",
            "level": "28",
            "qq_level": 0,
            "join_time": 1723202879,
            "last_sent_time": 1731808724,
            "title_expire_time": 0,
            "unfriendly": false,
            "card_changeable": true,
            "is_robot": false,
            "shut_up_timestamp": 1723397441,
            "role": "member",
            "title": "sb"
        }
    ],
    "message": "",
    "wording": ""
}
'''

# 将JSON字符串解析为Python字典
data = json.loads(json_data)

# 提取所需的字段
extracted_data = [
    {
        "nickname": item["nickname"],
        "user_id": item["user_id"],
        "card": item["card"],
        "title": item["title"]
    }
    for item in data["data"]
]

# 打印结果
print(json.dumps(extracted_data, indent=4, ensure_ascii=False))