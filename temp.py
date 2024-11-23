ai文字识别错误？(把小恩恩看成小爱爱)
31*****128为 机器人
10******** 为我(小恩恩)

tools无错误返回

---我的消息---
127.0.0.1 - - [23/Nov/2024 11:25:33] "POST / HTTP/1.1" 204 -
{'self_id': 31*****128, 'user_id': 10********, 'time': 1732332333, 'message_id': 1074028754, 'real_id': 1074028754, 'message_seq': 1074028754, 'message_type': 'group', 'sender': {'user_id': 10********, 'nickname': '小恩恩', 'card': 'killjsj', 'role': 'owner', 'title': '糖'}, 'raw_message': '[CQ:at,qq=31*****128,name=a] 查询10********的消息', 'font': 14, 'sub_type': 'normal', 'message': [{'type': 'at', 'data': {'qq': '31*****128', 'name': 'a'}}, {'type': 'text', 'data': {'text': ' 查询10********的消息'}}], 'message_format': 'array', 'post_type': 'message', 'group_id': 719501584}
---调用记录---
calling  getmyself  args: {}  result: 31*****128
calling  getsender  args: {'nothing': 'anything'}  result: {'user_id': 10********, 'nickname': '小恩恩', 'card': 'killjsj', 'role': 'owner', 'title': '糖'}
---messages---
[{'role': 'system', 'content': '你是一个聊天机器人，由 Killjsj 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Killjsj 为专有名词，不可翻译成其他语言。'}, {'role': 'user', 'content': '查询10********的消息'}, ChatCompletionMessage(content='', refusal=None, role='assistant', function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='getmyself:0', function=Function(arguments='{}', name='getmyself'), type='function', index=0)]), {'role': 'tool', 'tool_call_id': 'getmyself:0', 'name': 'getmyself', 'content': '"31*****128"'}, ChatCompletionMessage(content='', refusal=None, role='assistant', function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='getsender:0', function=Function(arguments='{\n    "nothing": "anything"\n}', name='getsender'), type='function', index=0)]), {'role': 'tool', 'tool_call_id': 'getsender:0', 'name': 'getsender', 'content': '{"user_id": 10********, "nickname": "\\u5c0f\\u6069\\u6069", "card": "killjsj", "role": "owner", "title": "\\u7cd6"}'}, ChatCompletionMessage(content='查询到的消息如下：\n- 用户ID：10********\n- 昵称：小爱爱\n- 群名片/备注：killjsj\n- 角色：群主\n- 头衔：糖', refusal=None, role='assistant', function_call=None, tool_calls=None)]
---实际发送消息---
sent '[CQ:at,qq=10********] 查询到的消息如下：\n- 用户ID：10********\n- 昵称：小爱爱\n- 群名片/备注：killjsj\n- 角色：群主\n- 头衔：糖'
{"status":"ok","retcode":0,"data":{"message_id":1286436860},"message":"","wording":""}

tools为        {"type": "function","function": {
                "name": "getmyself",
                "description": "get my userid",
                "parameters": {
                    "type": "object",
                    "required": [],
                    "properties": {
                        "nothing": {
                            "type": "string",
                            "description": "just anything"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "getdeltpeopleinfo",
                "description": "get more people info",
                "parameters": {
                    "type": "object",
                    "required": ["groupid","userid"],
                    "properties": {
                        "groupid": {
                            "type": "string",
                            "description": "input groupid"
                        },
                        "userid": {
                            "type": "string",
                            "description": "input userid(return from getpeople)"
                        }
                    }
                }
            }
        }
        {
            "type": "function",
            "function": {
                "name": "getpeople",
                "description": "get people list in the group(need groupid,you need call 'getgroup' to get it,WARN ONLY accepted GROUP numbers) (if you want to at somebody,add '[CQ:at,qq=qid]' and replace qid to user_id(in return data) into message\nWarn!, there should be no extra spaces in the CQ code, please do not add spaces before or after any commas, as it will be recognized as part of a parameter or parameter value.) (WARNING you can not output more than 50 people)",
                "parameters": {
                    "type": "object",
                    "required": ["group"],
                    "properties": {
                        "group": {
                            "type": "string",
                            "description": "input groupid and return people in this group"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "getgroup",
                "description": "get current you are talking with groupid(function getpeople need this!)(there is only one group number in each memory)",
                "parameters": {
                    "type": "object",
                    "required": [],
                    "properties": {
                        "nothing": {
                            "type": "string",
                            "description": "just anything"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "getsender",
                "description": "get current you are talking with somebody",
                "parameters": {
                    "type": "object",
                    "required": [],
                    "properties": {
                        "nothing": {
                            "type": "string",
                            "description": "just anything"
                        }
                    }
                }
            }
        },