import json
import os
import time
from typing import *
from dotenv import load_dotenv
import time
import torch
from bitsandbytes import *
from transformers import pipeline
from transformers import AutoModelForCausalLM, AutoTokenizer,BitsAndBytesConfig
import tools # support amd/intel gpu
import importlib

spec = importlib.util.find_spec('torch_directml')
found_directml = spec is not None
if found_directml:
    import torch_directml  # type: ignore
    device = torch_directml.device()
else:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  # !=cuda support



allow_ai_use_tools = False #!!! WRITE BY YOU !!!!
#no tools because i dont know how to write:(

with open('config.json','r+') as f:
    config = json.load(f)
aikey = config["secert"]["aikey"]
allow_draw = config["allow_ai_draw"]
lang = config["lang"]
maxtoken = int(config["maxtokens"])
model_name = config["local"]["model"]
cache_dir="./model_cache"
pipe = None
tokenizer= None
model = None
if not(allow_ai_use_tools):
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
                    "description": "Query the weather and return text; if two or more cities are found, return -1 and list the cities found; if there's a failure or query error, return 500",
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
                    "description": "Query the weather and return text; if two or more cities are found, return -1 and list the cities found; if there's a failure or query error, return 500",
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

def weather(adm1: str, adm2: str) -> Any:
    """
    Query the weather and return text; if two or more cities are found, return -1 and list the cities found(you need choose and call it again); if there's a failure or query error, return 500
    
    Args:
        adm1: The city or district (e.g., Nanshan, Jiangmen, etc.) without 'District'.
        adm2: The province (e.g., Chongqing, Shenzhen, etc.).
    """
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

def gtime() -> str:
    """Retrieves the current time and formats it as a string in the format YYYY-MM-DD HH:MM:SS."""
    current_time = time.time()
    local_time = time.localtime(current_time)
    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
    return formatted_time

def draw(prompt: str, neg_prompt: str) -> str:
    """Invoke AI drawing, return image as ((./result.png)). Processing is slow, so make sure to write 'the place where the image needs to be inserted' as ((./result.png)). English is required, and it can only be used once per message.
    **Prompt Guide**: For the best results, follow this structured prompt template (the more the better):
    - <|special|>,(newline)
    - <|artist|>,(newline)
    - <|special(optional)|>, (newline)
    - <|characters name|>, (newline)
    <|copyrights|>, (newline)
    - <|quality|>, (newline)
    <|meta|>, (newline)
    <|rating|>, (newline)
    ...(content)

    - <|tags|>, (newline)
    **Special Tags**: These prompts only need to be entered once, at the beginning, and do not need to be at the end. **Special Tags**:
    - years: These words help guide the result towards modern and retro anime art styles, with a specific time range of approximately 2005 to 2023
    - newest: 2021 to 2024
    - recent: 2018 to 2020
    - mid: 2015 to 2017
    - early: 2011 to 2014
    - old: 2005 to 2010
    - NSFW: These words help guide the result towards adult content, but if there are no adult content prompts, adult content is generally not generated.
    - safe: General
    - sensitive: Sensitive
    - nsfw: Suspicious
    - high quality: High quality
    - masterpiece: Outstanding
    - best quality: Best quality
    - white background: White background
    - looking at viewer: Looking at the viewer
    - explicit, nsfw: Explicit adult
    - negative_hand: (Negative prompt) Prevent hand issues
    - quality:
    - masterpiece: > 95%
    - best quality: > ?
    - great quality: > ?
    - good quality: > ?
    - normal quality: > ?
    - low quality: > ?
    - worst quality: ≤ 10%
    - Resolution: - You can freely use most reasonable resolutions, whether it's 512*768 used by SD1.5 or higher resolutions above 2048, each resolution will produce different effects. However, using too large or too small images may cause image fragmentation or distortion of character/background structure.
    - Tags: - If you want to generate high-quality images, you can use negative prompts, such as:
        - lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name
    - Negative tags can include common negative tags, but it's best not to give them too much weight, such as (ugly:2.8).
    - Due to model merging, some tags that were not fully trained in the original model may be lost, and some tags may require a weight greater than 1.5 to be effective.
    
    Args:
        prompt: The positive prompt in English.
        neg_prompt: The negative prompt in English.
    """
    print("drawing" + prompt)
    drew.ai(prompt, neg_prompt)  # Assuming 'drew.ai' is a function that generates an image
    return "(((./wdads.png)))"


tool_map = [gtime, weather, draw,] if allow_draw else [gtime, weather,]

def chat(messages,input,qqg):
    global pipe,tokenizer,model
    messages.append({
		"role": "user",
		"content": input,	
	})
    s = time.time()
    if pipe == None:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            quantization_config=BitsAndBytesConfig(
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            ),
            cache_dir=cache_dir,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        ).to(device)
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir, trust_remote_code=True)
        generate_kwargs = {
                "max_new_tokens": maxtoken
        } if maxtoken >= 0 else {}
    inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
    pipe = pipeline("text-generation",torch_dtype="auto",model=model, tokenizer=tokenizer,
            trust_remote_code=True,**generate_kwargs)

    return_mes = pipe(messages)
    assistant_message_raw = return_mes["generated_text"][-1]
    assistant_message = assistant_message_raw['content']
    print(time.time()-s)
    messages.append(assistant_message_raw)
    return (assistant_message,messages)