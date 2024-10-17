"""

THIS IS A DEMO OF VL TOOLS
USING MODEL:Qwen/Qwen2-VL-7B-Instruct-GPTQ-Int4
NO TOOLS BECAUSE I DONT FIND IT
UNFIN

"""



import os
import re
import time
from typing import *
from dotenv import load_dotenv
import torch
from transformers import AutoTokenizer, BitsAndBytesConfig,pipeline,Qwen2VLForConditionalGeneration,AutoProcessor
import importlib

spec = importlib.util.find_spec('torch_directml')
found_directml = spec is not None
if found_directml:
    import torch_directml  # type: ignore
    device = torch_directml.device()
else:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  # !=cuda support


load_dotenv()  # tools demo(you can just use this)
maxtoken = int(os.getenv("Gmodel_maxtokens"))
model_name = "Qwen/Qwen2-VL-7B-Instruct-GPTQ-Int4"  # os.getenv("Gmodel")

cache_dir = "./model_cache"
pipe = None
tokenizer = None
model = None
def chat(messages, input=None):
    '''
    running ai chat

    Args:
        messages
    '''
    global tokenizer, model,pipe
    print("message:",messages," input:",input)
    if input != None: #tool call
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
        model = Qwen2VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2-VL-7B-Instruct-GPTQ-Int4", torch_dtype="auto", device_map="auto",cache_dir=cache_dir,
        )
        processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct-GPTQ-Int4",cache_dir=cache_dir,)
        tokenizer = AutoTokenizer.from_pretrained(model_name,cache_dir=cache_dir,)
        pipe = ''#init

    text = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=False
    )
    inputs = tokenizer(
        text, padding=True, return_tensors="pt"
    ).to(device)
    print(text)
    # inputs = processor(
    #     text=[text], padding=True, return_tensors="pt"
    # ).to(device)
    output_ids = model.generate(**inputs, max_new_tokens=maxtoken)
    generated_ids = [output_ids[len(input_ids) :] for input_ids, output_ids in zip(inputs.input_ids, output_ids)]
    output_text = processor.batch_decode(
        generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
    )
    if isinstance(output_text, list):
        output_text = output_text[0] if output_text else ""
    
    print(output_text)
    messages.append({"role": "assistant", "content": output_text})
    response = output_text

    print("time:",time.time() - s)
    return (response,messages)