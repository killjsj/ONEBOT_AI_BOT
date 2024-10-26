import os
import time
from openai import OpenAI
import json
import tools
from typing import *


with open('config.json','r+') as f:
    config = json.load(f)
aikey = config["secert"]["aikey"]
allow_draw = config["allow_ai_draw"]
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
        }
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
        }
    ]



def weather(arguments: Dict[str, Any]) -> Any:
    adm1 = arguments["adm1"]
    adm2 = arguments["adm2"]
    print(adm1 +"+"+ adm2)
    f,result = tools.wea(adm1,adm2,lang)
    if f == -1:
        result = '-1,'
        for n in result:
            result = result + n['name'] +' adm1:'+ n['adm1'] +' adm2:'+ n['adm2'] +' country:' + n['country'] + '\n'
    elif f == 0:
        result = '0,' + result
    return {"result": result}

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

tool_map = {
    "time" : gtime,
    "weather" : weather,
    "draw":draw,
}
def chat(messages,input):
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
                tool_call_arguments = json.loads(tool_call.function.arguments) 
                tool_function = tool_map[tool_call_name] 
                tool_result = tool_function(tool_call_arguments)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_name,
                    "content": json.dumps(tool_result), 
                })
    
    assistant_message = completion.choices[0].message
    messages.append(assistant_message)
    return (choice.message.content,messages)
