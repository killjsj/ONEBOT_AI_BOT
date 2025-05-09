# -*- coding: utf-8 -*-
import asyncio
import base64
import logging
import os
import queue
import time
import numpy as np
from openai import BadRequestError, OpenAI
import json

import openai
import requests
import tools
from typing import *

def decode_unicode_escapes(s: str) -> str:
    try:
        return bytes(s, 'utf-8').decode('unicode_escape')
    except:
        return s

with open('config.json','r+') as f:
    config:dict = json.load(f)
ai_infer = config["online"]["infer"]
aikey = config["secert"]["aikey"]
allow_draw = config["allow_ai_draw"]
url = config["online"]["aiurl"]
ws = config["network"]["ws"]["enable"]
fip = config["network"]["http"]["f"]["ip"]
tip = config["network"]["http"]["t"]["ip"]
tport = config["network"]["http"]["t"]["port"]
fport = config["network"]["http"]["f"]["port"]
wurl = config["network"]["ws"]["url"]
lang = config["lang"]
model = config["online"]["model"]
maxtokens = int(config["maxtokens"])
wss = None
async def lower_send(ENDPOINT,jsons) -> dict:
    global wurl
    if ws:
        async with ws.connect(wurl) as websocket:
            await websocket.send(json.dump({"action":ENDPOINT,"params":jsons}))
            r = await websocket.recv()
            return json.loads(r)
    else:
        ttip = tip + ":" + str(tport)
        response = requests.post(ttip+"/"+ENDPOINT, json=jsons)
        return response.json()
client = OpenAI(
    api_key=aikey,
    base_url=url,  # Ensure this is the correct OpenAI API endpoint
)

if not(allow_draw):
        tool = [
        {
            "type": "function",
            "function": {
                "name": "time",
                "description": "get current time (formatted as YYYY-MM-DD HH:MM:SS)",
                "parameters": {
                    "type": "object",
                    "required": [],
                    "properties": {
                        "nothing": {
                            "type": "string",
                            "description": "just anything (JUST A TIME)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "getpeople",
                "description": "get people list in the group(need groupid,you need call 'getgroup' to get it,WARN ONLY accepted GROUP numbers) (if you want to at(@) somebody,add '[CQ:at,qq=qid]' and replace qid to user_id(MUST in the return data) into message,Warn!, there should be no extra spaces in the CQ code, please do not add spaces before or after any commas, as it will be recognized as part of a parameter or parameter value.) (WARNING you can not output more than 50 people) | Filter parameters: 1. target (role, name, user_id), 2. filter_cond(also known as parameter 2) When target = 'role', the filter_condcan only be 'admin' (administrator and group owner), 'member' (non-admin), when target = 'name', the output is nickname, title, name (card) in the group whether it contains parameter 2, when target = 'user_id' , the output is Parameter 2 = Target of the user's user_id If you don't fill in the field, all will be returned (it is not recommended not to fill in this parameter) (when you can't find the target, you can try to search by another parameter)",
                "parameters": {
                    "type": "object",
                    "required": ["group"],
                    "properties": {
                        "group": {
                            "type": "string",
                            "description": "input groupid and return people in this group,if you dont know the groupid,call getgroup"
                        },
                        "filter_target": {
                            "type": "string",
                            "description": """Target (role, name, user_id)"""
                        },
                        "filter_cond":{
                            "type": "string",
                            "description": """filter_cond(parameter 2) When target = 'role', the filter_cond can only be 'admin' (administrator and group owner), 'member' (non-admin), when target = 'name', the output is nickname, title, name (card) in the group whether it contains parameter 2, when target = 'user_id' , the output is Parameter 2 = Target of the user's user_id"""
                        },
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "getgroupinfo",
                "description": "input groupid and return group info",
                "parameters": {
                    "type": "object",
                    "required": ["group"],
                    "properties": {
                        "group": {
                            "type": "string",
                            "description": "input groupid and return group info,if you dont know the groupid,call getgroup"
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
        {
            "type": "function",
            "function": {
                "name": "weather",
                "description": "Query the weather and return text; if two or more cities are found, return -1 and list the cities found(you need choose and call it again); if there's a failure or query error, return 500",
                "parameters": {
                    "type": "object",
                    "required": ["adm1","adm2"],
                    "properties": {
                        "adm1":{
                            "type": "string",
                            "description":"location (e.g., Nanshan, Jiangmen, etc.) (do not add 'District')"
                        },
                        "adm2":{
                            "type": "string",
                            "description":"province (e.g., Chongqing, Shenzhen, etc.)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
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
                "description": "get more personal(one person) info (if you want to at(@) somebody,add '[CQ:at,qq=qid]' and replace qid to user_id(MUST in the return data) into message,Warn!, there should be no extra spaces in the CQ code, please do not add spaces before or after any commas, as it will be recognized as part of a parameter or parameter value.)",
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
        },
    ]
else:
    import drew
    tool = [
        {
            "type": "function",
            "function": {
                "name": "time",
                "description": "get current time (formatted as YYYY-MM-DD HH:MM:SS)",
                "parameters": {
                    "type": "object",
                    "required": [],
                    "properties": {
                        "nothing": {
                            "type": "string",
                            "description": "just anything (JUST A TIME)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "getpeople",
                "description": "get people list in the group(need groupid,you need call 'getgroup' to get it,WARN ONLY accepted GROUP numbers) (if you want to at(@) somebody,add '[CQ:at,qq=qid]' and replace qid to user_id(MUST in the return data) into message,Warn!, there should be no extra spaces in the CQ code, please do not add spaces before or after any commas, as it will be recognized as part of a parameter or parameter value.) (WARNING you can not output more than 50 people) | Filter parameters: 1. target (role, name, user_id), 2. filter_cond(also known as parameter 2) When target = 'role', the filter_condcan only be 'admin' (administrator and group owner), 'member' (non-admin), when target = 'name', the output is nickname, title, name (card) in the group whether it contains parameter 2, when target = 'user_id' , the output is Parameter 2 = Target of the user's user_id If you don't fill in the field, all will be returned (it is not recommended not to fill in this parameter) (when you can't find the target, you can try to search by another parameter)",
                "parameters": {
                    "type": "object",
                    "required": ["group"],
                    "properties": {
                        "group": {
                            "type": "string",
                            "description": "input groupid and return people in this group,if you dont know the groupid,call getgroup"
                        },
                        "filter_target": {
                            "type": "string",
                            "description": """Target (role, name, user_id)"""
                        },
                        "filter_cond":{
                            "type": "string",
                            "description": """filter_cond(parameter 2) When target = 'role', the filter_cond can only be 'admin' (administrator and group owner), 'member' (non-admin), when target = 'name', the output is nickname, title, name (card) in the group whether it contains parameter 2, when target = 'user_id' , the output is Parameter 2 = Target of the user's user_id"""
                        },
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "getgroupinfo",
                "description": "input groupid and return group info",
                "parameters": {
                    "type": "object",
                    "required": ["group"],
                    "properties": {
                        "group": {
                            "type": "string",
                            "description": "input groupid and return group info,if you dont know the groupid,call getgroup"
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
        {
            "type": "function",
            "function": {
                "name": "weather",
                "description": "Query the weather and return text; if two or more cities are found, return -1 and list the cities found(you need choose and call it again); if there's a failure or query error, return 500",
                "parameters": {
                    "type": "object",
                    "required": ["adm1","adm2"],
                    "properties": {
                        "adm1":{
                            "type": "string",
                            "description":"location (e.g., Nanshan, Jiangmen, etc.) (do not add 'District')"
                        },
                        "adm2":{
                            "type": "string",
                            "description":"province (e.g., Chongqing, Shenzhen, etc.)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "draw",
                "description": "Invoke AI drawing, return image as ((./result.png)). Processing is slow, so make sure to write 'the place where the image needs to be inserted' as ((./result.png)). English is required, and it can only be used once per message.\n\n**Prompt Guide**: For the best results, follow this structured prompt template (the more the better):\n- <|special|>,(newline)\n- <|artist|>,(newline)\n- <|special(optional)|>, (newline)\n- <|characters name|>, (newline)\n<|copyrights|>, (newline)\n- <|quality|>, (newline)\n<|meta|>, (newline)\n<|rating|>, (newline)\n...(content)\n\n- <|tags|>, (newline)\n**Special Tags**: These prompts only need to be entered once, at the beginning, and do not need to be at the end. **Special Tags**:\n  - years: These words help guide the result towards modern and retro anime art styles, with a specific time range of approximately 2005 to 2023\n  - newest: 2021 to 2024\n  - recent: 2018 to 2020\n  - mid: 2015 to 2017\n  - early: 2011 to 2014\n  - old: 2005 to 2010\n  - NSFW: These words help guide the result towards adult content, but if there are no adult content prompts, adult content is generally not generated.\n  - safe: General\n  - sensitive: Sensitive\n  - nsfw: Suspicious\n  - high quality: High quality\n  - masterpiece: Outstanding\n  - best quality: Best quality\n  - white background: White background\n  - looking at viewer: Looking at the viewer\n  - explicit, nsfw: Explicit adult\n  - negative_hand: (Negative prompt) Prevent hand issues\n  - quality:\n  - masterpiece: > 95%\n  - best quality: > ?\n  - great quality: > ?\n  - good quality: > ?\n  - normal quality: > ?\n  - low quality: > ?\n  - worst quality: ≤ 10%\n  - Resolution: - You can freely use most reasonable resolutions, whether it's 512*768 used by SD1.5 or higher resolutions above 2048, each resolution will produce different effects. However, using too large or too small images may cause image fragmentation or distortion of character/background structure.\n  - Tags: - If you want to generate high-quality images, you can use negative prompts, such as:\n    - lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name\n  - Negative tags can include common negative tags, but it's best not to give them too much weight, such as (ugly:2.8).\n  - Due to model merging, some tags that were not fully trained in the original model may be lost, and some tags may require a weight greater than 1.5 to be effective.",
                "parameters": {
                    "type": "object",
                    "required": ["pro","negpro"],
                    "properties": {
                        "pro":{
                            "type": "string",
                            "description":"prompt in English"
                        },
                        "negpro":{
                            "type": "string",
                            "description":"negative prompt in English"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
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
                "description": "get more personal(one person) info (if you want to at(@) somebody,add '[CQ:at,qq=qid]' and replace qid to user_id(MUST in the return data) into message,Warn!, there should be no extra spaces in the CQ code, please do not add spaces before or after any commas, as it will be recognized as part of a parameter or parameter value.)",
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
        },
    ]
def cbu(burl,apik):
    global client
    if burl == "":
        burl = url
        config["online"]["aiurl"] = url
        
    if apik == "":
        apik = aikey
        config["secert"]["aikey"] = apik
        
    client = OpenAI(
        api_key = apik, 
        base_url = burl,
    )
    with open('config.json','w+') as f:
                                            json.dump(config,f,indent=4)     
def cam(modeln):
    global model
    model = modeln
    config["online"]["model"] = modeln
    
    with open('config.json','w+') as f:
                                            json.dump(config,f,indent=4)     
self_id = "0"
group = queue.Queue(maxsize=3)
send = queue.Queue(maxsize=3)
def weather(arguments: Dict[str, Any]) -> Any:
    adm1 = arguments["adm1"]
    adm2 = arguments["adm2"]
    print(adm1 +"+"+ adm2)
    f,result = tools.wea(adm1,adm2,lang)
    print(result)
    if f == -1:
        resultb = '-1,'
        for n in result:
            resultb += str(n['name']) + ' adm1:' + n['adm1'] + ' adm2:' + n['adm2'] + ' country:' + n['country'] + '\n'        
            result = resultb    
    elif f == 0:
        result = '0,' + result
    return {"result": result}

def getm(arguments: Dict[str, Any]):
    return self_id

def gdpi(arguments: Dict[str, Any]):
    adm1 = arguments["groupid"]
    adm2 = arguments["userid"]
    payl0 = {"group_id":adm1,"user_id":adm2}
    response = asyncio.run(lower_send("get_group_member_info", payl0))
    return response


def gtime(arguments: Dict[str, Any]) :
    print(arguments.__str__())
    current_time = time.time()
    local_time = time.localtime(current_time)
    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
    return formatted_time

def draw(arguments: Dict[str, Any]) :
    adm1 = arguments["pro"]
    adm2 = arguments["negpro"]
    print(adm1 +"+"+ adm2)
    drew.ai(adm1,adm2)
    return "(((./wdads.png)))"

def getp(arguments: Dict[str, Any]):
    qqg = arguments["group"]
    payl0 = {"group_id":qqg}
    response = asyncio.run(lower_send("get_group_member_list", payl0))
    cond =arguments.get("filter_cond")
    target = arguments.get("filter_target")
    wp_d = [
    {
        "nickname": item["nickname"],
        "user_id": item["user_id"],
        "card": item["card"],
        "title": item["title"],
        "role": item["role"]
    }
    for item in response["data"]
    ]
    print(wp_d)
    extracted_data = []
    if cond != None:
        if target != None:
            if target == "role":
                if cond == "admin":
                    for item in wp_d:
                        if "admin" == str(item["role"]) or "owner" == str(item["role"]):
                            extracted_data.append(item)
                            print(item)
                elif cond == "member": 
                    for item in wp_d:
                        if "member" == str(item["role"]):
                            extracted_data.append(item)
            elif target == "name":
                for item in wp_d:
                    if cond in item["nickname"] or cond in item["card"] or cond in item["title"]:
                        extracted_data.append(item)
            elif target == "user_id":
                for item in wp_d:
                    if cond == str(item["user_id"]):
                        extracted_data.append(item)
            else:
                extracted_data = wp_d
        else:
            extracted_data = wp_d
    else:
        extracted_data = wp_d
    return extracted_data
def getg(arguments: Dict[str, Any]):
    try:
        return group.get(False)
    except queue.Empty:
        print("qqg empty!return 0....")
        return 0

def get_s(arguments: Dict[str, Any]):
    try:
        sender_data = send.get(False)
        if isinstance(sender_data, dict):
            for key in ['nickname', 'card', 'title']:
                if key in sender_data and isinstance(sender_data[key], str):
                    sender_data[key] = decode_unicode_escapes(sender_data[key])
            print("Processed sender data:", sender_data)
        return sender_data
    except queue.Empty:
        print("sender empty!return 0....")
        return 0

def getgi(arguments: Dict[str, Any]):
    adm1 = arguments["group"]
    payl0 = {"group_id":adm1}
    ttip = tip + ":" + str(tport)
    print("getgi:run")
    
    response = asyncio.run(lower_send("get_group_info", payl0))
    print(response)
    return response

tool_map = {
    "time" : gtime,
    "weather" : weather,
    "draw":draw,
    "getpeople":getp,
    "getgroup":getg,
    "getsender":get_s,
    "getmyself":getm,
    "getdeltpeopleinfo":gdpi,
    "getgroupinfo":getgi,
}
def chat_stream(messages,input,qqg,sender,self_ids):
        global self_id
        self_id = self_ids
        messages.append({
            "role": "user",
            "content": input,	
        })
        with open('config.json','r+') as f:
            config:dict = json.load(f)
        ai_infer = config["online"]["infer"]
        undone_tool_info = []
        reasoning_content = ""
        answer_content=  ""
    # while finish_reason is None or finish_reason == "tool_calls":
        # completion.
        while True:
            undone_tool_info = []
            print("while")
            completion : openai.Stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                parallel_tool_calls=True,
                tools=tool, 
                max_tokens= None if maxtokens <= 0 else maxtokens,
                stream=True,
    #             extra_body={
    #     "enable_search": True
    # }
                extra_body={"enable_thinking": ai_infer},
            ) 
            for chunk in completion:
                print(chunk)
                delta = chunk.choices[0].delta
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                    reasoning_content += delta.reasoning_content
                else:
                    if delta.content is not None:
                        answer_content += delta.content
                        # print(delta.content,end="",flush=True)  # 流式输出回复内容
                    
                    # 处理工具调用信息（支持并行工具调用）
                    if delta.tool_calls is not None:
                        for tool_call in delta.tool_calls:
                            index = tool_call.index  # 工具调用索引，用于并行调用
                                
                                # 动态扩展工具信息存储列表
                            while len(undone_tool_info) <= index:
                                    undone_tool_info.append({})
                                
                                # 收集工具调用ID（用于后续函数调用）
                            if tool_call.id:
                                    undone_tool_info[index]['id'] = undone_tool_info[index].get('id', '') + tool_call.id
                                
                                # 收集函数名称（用于后续路由到具体函数）
                            if tool_call.function and tool_call.function.name:
                                    undone_tool_info[index]['name'] = undone_tool_info[index].get('name', '') + tool_call.function.name
                                
                                # 收集函数参数（JSON字符串格式，需要后续解析）
                            if tool_call.function and tool_call.function.arguments:
                                    undone_tool_info[index]['arguments'] = undone_tool_info[index].get('arguments', '') + tool_call.function.arguments
            if undone_tool_info == []:
                break
            for n in undone_tool_info:
                                tool_call_name = n['name']
                                try:
                                        if tool_call_name == "getgroup":
                                            group.put(qqg, False)
                                except queue.Full:
                                        print("qqg full! skipping put")
                                try:
                                        if tool_call_name == "getsender":
                                            # 确保发送者信息正确编码
                                            if isinstance(sender, dict):
                                                for key in ['nickname', 'card', 'title']:
                                                    if key in sender and isinstance(sender[key], str):
                                                        sender[key] = decode_unicode_escapes(sender[key])
                                            send.put(sender, False)
                                except queue.Full:
                                        print("sender full! skipping put")
                                    
                                tool_call_arguments = json.loads(n["arguments"]) 
                                tool_function = tool_map[tool_call_name] 
                                tool_result = tool_function(tool_call_arguments)
                                print("calling ", tool_call_name, " args:", tool_call_arguments, " result:", tool_result)
                                messages.append({'role': 'assistant', 
                                                'content': answer_content, 
                                                'tool_calls': [
                                                    {'id': n["id"], 
                                                    'function':{"name":n["name"],'arguments':n['arguments']}
                                                    }
                                                    ]
                                                })
                                messages.append({
                                "role": "tool",
                                "tool_call_id": n["id"],
                                "name": tool_call_name,
                                "content": json.dumps(tool_result, ensure_ascii=False)  # 添加 ensure_ascii=False
                                })            
                                print(messages)
        print("ac:"+answer_content)
        assistant_message = answer_content
        messages.append({"role": "assistant", "content": assistant_message})
        return (answer_content,messages)
# only test on Qwen Omni-Turbo!
import soundfile as sf
def chat_stream_sound(messages:list,input,qqg,sender,self_ids,picture:List[dict] = []):
        """overlook input when picture is not []"""
        global self_id
        self_id = self_ids
        messages.append({
                    "role": "user",
                    "content": picture if picture != "" or picture != None or picture != [] else 
                    [{"type": "text", "text": input}],
                })
        
        if len(messages) >= 2 and messages[0]["role"] == "system":
            # 把system提到user消息列表最前面
            if isinstance(messages[1]["content"], list):
                messages[1]["content"].insert(0, {"type": "text", "text": messages[0]["content"]})
            else:
                # 处理普通文本消息
                messages[1]["content"] = [
                    {"type": "text", "text": messages[0]["content"]},
                    {"type": "text", "text": messages[1]["content"]}
                ]
            # 删除原始system消息
            messages.pop(0)
        # print(messages)
        undone_tool_info = []
        reasoning_content = ""
        answer_content=  ""
    # while finish_reason is None or finish_reason == "tool_calls":
        # completion.
        audio_string = ""
        while True:
            undone_tool_info = []
            print("while")
            try:
                completion : openai.Stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,
                    parallel_tool_calls=True,
                    tools=tool, 
                    max_tokens= None if maxtokens <= 0 else maxtokens,
                    stream=True,
                    modalities=["text", "audio"],
                    #             extra_body={
                    #     "enable_search": True
                    # }
                    # extra_body={"enable_thinking": ai_infer},
                    
                    audio={"voice": "Cherry", "format": "wav"},
                ) 
            except BadRequestError as e:
                logging.exception(e)
                answer_content = "Error: " + str(e) + "\ninput too long!"
                messages.append({"role": "assistant", "content": answer_content})
                break
            for chunk in completion:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                    reasoning_content += delta.reasoning_content
                else:
                    if chunk.choices:
                        if hasattr(delta, "audio"):
                            try:
                                audio_string += delta.audio["data"]
                            except Exception as e:
                                # print(delta.audio["transcript"])
                                #内容
                                answer_content += delta.audio["transcript"]
                    if delta.content is not None:
                        answer_content += delta.content
                        
                        
                        # print(delta.content,end="",flush=True)  # 流式输出回复内容
                    
                    # 处理工具调用信息（支持并行工具调用）
                    if delta.tool_calls is not None:
                        for tool_call in delta.tool_calls:
                            index = tool_call.index  # 工具调用索引，用于并行调用
                                
                                # 动态扩展工具信息存储列表
                            while len(undone_tool_info) <= index:
                                    undone_tool_info.append({})
                                
                                # 收集工具调用ID（用于后续函数调用）
                            if tool_call.id:
                                    undone_tool_info[index]['id'] = undone_tool_info[index].get('id', '') + tool_call.id
                                
                                # 收集函数名称（用于后续路由到具体函数）
                            if tool_call.function and tool_call.function.name:
                                    undone_tool_info[index]['name'] = undone_tool_info[index].get('name', '') + tool_call.function.name
                                
                                # 收集函数参数（JSON字符串格式，需要后续解析）
                            if tool_call.function and tool_call.function.arguments:
                                    undone_tool_info[index]['arguments'] = undone_tool_info[index].get('arguments', '') + tool_call.function.arguments
            if undone_tool_info == []:
                break
            for n in undone_tool_info:
                                tool_call_name = n['name']
                                try:
                                        if tool_call_name == "getgroup":
                                            group.put(qqg, False)
                                except queue.Full:
                                        print("qqg full! skipping put")
                                try:
                                        if tool_call_name == "getsender":
                                            # 确保发送者信息正确编码
                                            if isinstance(sender, dict):
                                                for key in ['nickname', 'card', 'title']:
                                                    if key in sender and isinstance(sender[key], str):
                                                        sender[key] = decode_unicode_escapes(sender[key])
                                            send.put(sender, False)
                                except queue.Full:
                                        print("sender full! skipping put")
                                    
                                tool_call_arguments = json.loads(n["arguments"]) 
                                tool_function = tool_map[tool_call_name] 
                                tool_result = tool_function(tool_call_arguments)
                                print("calling ", tool_call_name, " args:", tool_call_arguments, " result:", tool_result)
                                messages.append({'role': 'assistant', 
                                                'content': answer_content, 
                                                'tool_calls': [
                                                    {'id': n["id"], 
                                                    'function':{"name":n["name"],'arguments':n['arguments']}
                                                    }
                                                    ]
                                                })
                                messages.append({
                                "role": "tool",
                                "tool_call_id": n["id"],
                                "name": tool_call_name,
                                "content": json.dumps(tool_result, ensure_ascii=False)  # 添加 ensure_ascii=False
                                })            
                                print(messages)
        wav_bytes = base64.b64decode(audio_string)
        audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
        sf.write("audio_assistant_temp.wav", audio_np, samplerate=24000)
        print("ac:"+answer_content)
        assistant_message = answer_content
        messages.append({"role": "assistant", "content": assistant_message})
        return (answer_content,messages)
def chat_stream_image_infer(messages:list,input,qqg,sender,self_ids,picture:List[dict]):
        """overlook input when picture is not []"""
        print("while")
        
        global self_id
        self_id = self_ids
        messages.append({
                    "role": "user",
                    "content": picture if picture != "" or picture != None or picture != [] else 
                    [{"type": "text", "text": input}],
                })
        undone_tool_info = []
        reasoning_content = ""
        answer_content=  ""
    # while finish_reason is None or finish_reason == "tool_calls":
        # completion.
        with open('config.json','r+') as f:
            config:dict = json.load(f)
        ai_infer = config["online"]["infer"]
        audio_string = ""
        while True:
            undone_tool_info = []
            try:
                completion : openai.Stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    parallel_tool_calls=True,
                    tools=tool, 
                    max_tokens= None if maxtokens <= 0 else maxtokens,
                    stream=True,
                    extra_body={"enable_thinking": ai_infer},
                    
                ) 
                # completion : openai.Stream = client.chat.completions.create(
                #     model=model,
                #     messages=messages,
                #     max_tokens=None if maxtokens <= 0 else maxtokens,
                #     stream=True,
                # ) 
            except BadRequestError as e:
                logging.exception(e)
                answer_content = "Error: " + str(e) + "\npossable input too long!"
                messages.append({"role": "assistant", "content": answer_content})
                break
            for chunk in completion:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                    reasoning_content += delta.reasoning_content
                else:
                    if chunk.choices:
                        if hasattr(delta, "audio"):
                            try:
                                audio_string += delta.audio["data"]
                            except Exception as e:
                                # print(delta.audio["transcript"])
                                #内容
                                answer_content += delta.audio["transcript"]
                    if delta.content is not None:
                        answer_content += delta.content
                        
                        
                        # print(delta.content,end="",flush=True)  # 流式输出回复内容
                    
                    # 处理工具调用信息（支持并行工具调用）
                    if delta.tool_calls is not None:
                        for tool_call in delta.tool_calls:
                            index = tool_call.index  # 工具调用索引，用于并行调用
                                
                                # 动态扩展工具信息存储列表
                            while len(undone_tool_info) <= index:
                                    undone_tool_info.append({})
                                
                                # 收集工具调用ID（用于后续函数调用）
                            if tool_call.id:
                                    undone_tool_info[index]['id'] = undone_tool_info[index].get('id', '') + tool_call.id
                                
                                # 收集函数名称（用于后续路由到具体函数）
                            if tool_call.function and tool_call.function.name:
                                    undone_tool_info[index]['name'] = undone_tool_info[index].get('name', '') + tool_call.function.name
                                
                                # 收集函数参数（JSON字符串格式，需要后续解析）
                            if tool_call.function and tool_call.function.arguments:
                                    undone_tool_info[index]['arguments'] = undone_tool_info[index].get('arguments', '') + tool_call.function.arguments
            if undone_tool_info == []:
                break
            for n in undone_tool_info:
                                tool_call_name = n['name']
                                try:
                                        if tool_call_name == "getgroup":
                                            group.put(qqg, False)
                                except queue.Full:
                                        print("qqg full! skipping put")
                                try:
                                        if tool_call_name == "getsender":
                                            # 确保发送者信息正确编码
                                            if isinstance(sender, dict):
                                                for key in ['nickname', 'card', 'title']:
                                                    if key in sender and isinstance(sender[key], str):
                                                        sender[key] = decode_unicode_escapes(sender[key])
                                            send.put(sender, False)
                                except queue.Full:
                                        print("sender full! skipping put")
                                    
                                tool_call_arguments = json.loads(n["arguments"]) 
                                tool_function = tool_map[tool_call_name] 
                                tool_result = tool_function(tool_call_arguments)
                                print("calling ", tool_call_name, " args:", tool_call_arguments, " result:", tool_result)
                                messages.append({'role': 'assistant', 
                                                'content': answer_content, 
                                                'tool_calls': [
                                                    {'id': n["id"], 
                                                    'function':{"name":n["name"],'arguments':n['arguments']}
                                                    }
                                                    ]
                                                })
                                messages.append({
                                "role": "tool",
                                "tool_call_id": n["id"],
                                "name": tool_call_name,
                                "content": json.dumps(tool_result, ensure_ascii=False)  # 添加 ensure_ascii=False
                                })            
                                print(messages)
        print("ac:"+answer_content)
        assistant_message = answer_content
        messages.append({"role": "assistant", "content": assistant_message})
        return (answer_content,messages)

def chat(messages,input,qqg,sender,self_ids):
    global self_id
    self_id = self_ids
    messages.append({
		"role": "user",
		"content": input,	
	})
    with open('config.json','r+') as f:
            config:dict = json.load(f)
    ai_infer = config["online"]["infer"]
    finish_reason = None
    while finish_reason is None or finish_reason == "tool_calls":
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                tools=tool, 
                max_tokens= None if maxtokens <= 0 else maxtokens,
                extra_body={"enable_thinking": ai_infer},
        #         extra_body={
        #     "enable_search": True
        # }
            )
        except BadRequestError as e:
                logging.exception(e)
                answer_content = "Error: " + str(e) + "\npossable input too long!"
                messages.append({"role": "assistant", "content": answer_content})
                return (answer_content,messages)
        choice = completion.choices[0]
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls": 
            messages.append(choice.message) 
            for tool_call in choice.message.tool_calls: 
                tool_call_name = tool_call.function.name
                try:
                    if tool_call_name == "getgroup":
                        group.put(qqg, False)
                except queue.Full:
                    print("qqg full! skipping put")
                try:
                    if tool_call_name == "getsender":
                        # 确保发送者信息正确编码
                        if isinstance(sender, dict):
                            for key in ['nickname', 'card', 'title']:
                                if key in sender and isinstance(sender[key], str):
                                    sender[key] = decode_unicode_escapes(sender[key])
                        send.put(sender, False)
                except queue.Full:
                    print("sender full! skipping put")
                
                tool_call_arguments = json.loads(tool_call.function.arguments) 
                tool_function = tool_map[tool_call_name] 
                tool_result = tool_function(tool_call_arguments)
                print("calling ", tool_call_name, " args:", tool_call_arguments, " result:", tool_result)
                
                # 修改 JSON 序列化部分
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_name,
                    "content": json.dumps(tool_result, ensure_ascii=False)  # 添加 ensure_ascii=False
                })
    
    assistant_message = completion.choices[0].message
    messages.append(assistant_message)
    return (choice.message.content,messages)
