"""

THIS IS A DEMO OF TOOLS
USING MODEL:DiTy/gemma-2-9b-it-function-calling-GGUF
viwe image-7.png

"""



import os
import time
from typing import *
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,pipeline
import importlib
import drew
import tools  # support amd/intel gpu

spec = importlib.util.find_spec('torch_directml')
found_directml = spec is not None
if found_directml:
    import torch_directml  # type: ignore
    device = torch_directml.device()
else:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  # !=cuda support
with open('config.json','r+') as f:
    config = json.load(f)
aikey = config["secert"]["aikey"]
allow_draw = config["allow_ai_draw"]
lang = config["lang"]
maxtoken = int(config["maxtokens"])
model_name = "DiTy/gemma-2-9b-it-function-calling-GGUF"  # config["local"]["model"]
cache_dir = "./model_cache"
pipe = None
tokenizer = None
model = None
tool = []
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


tool_map = [gtime, weather, draw] if allow_draw else [gtime, weather]

def chat(messages, input):
    global tokenizer, model,pipe
    print("message:",messages," input:",input)
    if isinstance(input,dict):
        messages.append(input)
        print("dict")
    else:
        messages.append({
            "role": "user",
            "content": input,
        })
        print("append")
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
        pipe = pipeline("text-generation",torch_dtype="auto",model=model, tokenizer=tokenizer,
                trust_remote_code=True,**generate_kwargs)
    inputs = pipe.tokenizer.apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True,
                        tools=tool_map,
                    )
    terminator_ids = [
        pipe.tokenizer.eos_token_id,
        pipe.tokenizer.convert_tokens_to_ids("<end_of_turn>")
    ]
    print(inputs)
    response = pipe(
        inputs,
        max_new_tokens=maxtoken,
        eos_token_id=terminator_ids,
    )
    response = response[0]["generated_text"][len(inputs):]
    function_response = ''
    generated_response = response
    if generated_response[:len("Function call: ")] == "Function call: ":
        json_data = generated_response.replace("Function call: ",'')
        tool_call_arguments = json.loads(json_data) 
        tool_function = tool_call_arguments["name"] 
        args = tool_call_arguments["arguments"]
        returndata = globals()[tool_function](**args)
        print(args)
        
        generated_response = {
            "role": "function-call",
            "content": json.dumps({"name": tool_function, "arguments": args})
        }
        function_response = {
            "role": "function-response",
            "content": str({"function_return":returndata})
                            }
        messages.append(generated_response)
        again_again,messages = chat(messages=messages,input=function_response)
        print("time:",time.time() - s)
        return (again_again,messages)
    else:
        generated_response = {"role": "model", "content": f'{generated_response}'}
        messages.append(generated_response)
        print("time:",time.time() - s)
        return (response,messages)
