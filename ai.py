# -*- coding: utf-8 -*-
import os
import queue
import time
from openai import OpenAI
import json

import requests
import tools
from typing import *


with open('config.json','r+') as f:
    config = json.load(f)
aikey = config["secert"]["aikey"]
allow_draw = config["allow_ai_draw"]
fip = config["network"]["f"]["ip"]
tip = config["network"]["t"]["ip"]
tport = config["network"]["t"]["port"]
fport = config["network"]["f"]["port"]
url = config["online"]["aiurl"]
lang = config["lang"]
model = config["online"]["model"]
maxtokens = int(config["maxtokens"])

client = OpenAI(
    api_key = aikey, 
    base_url = url,
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
                    "required": ["query"],
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
                "description": "get people list in the group(need groupid,you need first call 'getgroup' to get it,WARN ONLY accepted GROUP numbers)(if you want to at somebody,add '[CQ:at,qq=qid]' and replace qid to user_id(in return data) into message\nWarn!, there should be no extra spaces in the CQ code, please do not add spaces before or after any commas, as it will be recognized as part of a parameter or parameter value.)(WARNING you can not output more than 50 people)",
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
                "description": "get current you are talking with groupid(function getpeople need this!)",
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
        },
    ]

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
    ttip = tip + ":" + str(tport)
    response = requests.post(ttip+"/get_group_member_info", json=payl0)
    return response.json()


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
    ttip = tip + ":" + str(tport)
    response = requests.post(ttip+"/get_group_member_list", json=payl0)
    extracted_data = [
    {
        "nickname": item["nickname"],
        "user_id": item["user_id"],
        "card": item["card"],
        "title": item["title"],
        "role": item["role"]
    }
    for item in response.json()["data"]
    ]
    return extracted_data
def getg(arguments: Dict[str, Any]):
    try:
        return group.get(False)
    except queue.Empty:
        print("qqg empty!return 0....")
        return 0

def get_s(arguments: Dict[str, Any]):
    try:
        return send.get(False)
    except queue.Empty:
        print("sender empty!return 0....")
        return 0

tool_map = {
    "time" : gtime,
    "weather" : weather,
    "draw":draw,
    "getpeople":getp,
    "getgroup":getg,
    "getsender":get_s,
    "getmyself":getm,
    "getdeltpeopleinfo":gdpi,
}
def chat(messages,input,qqg,sender,self_ids):
    global self_id
    self_id = self_ids
    messages.append({
		"role": "user",
		"content": input,	
	})
    finish_reason = None
    while finish_reason is None or finish_reason == "tool_calls":
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            tools=tool, 
            max_tokens= None if maxtokens <= 0 else maxtokens,
        )
        choice = completion.choices[0]
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls": 
            messages.append(choice.message) 
            for tool_call in choice.message.tool_calls: 
                tool_call_name = tool_call.function.name
                try:
                    if tool_call_name == "getgroup":
                        group.put(qqg,False)
                except queue.Full:
                    print("qqg full! skipping put")
                try:
                    if tool_call_name == "getsender":
                        send.put(sender,False)
                except queue.Full:
                    print("sender full! skipping put")
                tool_call_arguments = json.loads(tool_call.function.arguments) 
                tool_function = tool_map[tool_call_name] 
                tool_result = tool_function(tool_call_arguments)
                print("calling ",tool_call_name," args:",tool_call_arguments," result:",tool_result)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_name,
                    "content": json.dumps(tool_result), 
                })
    
    assistant_message = completion.choices[0].message
    messages.append(assistant_message)
    print(messages)
    return (choice.message.content,messages)
