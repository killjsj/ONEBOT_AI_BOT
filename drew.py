#from tkinter import Image
import os
import time
from diffusers import StableDiffusionPipeline,UNet2DConditionModel,AutoencoderKL,DiffusionPipeline,StableDiffusionUpscalePipeline
import torch
from transformers import BitsAndBytesConfig, CLIPTextModel
import numpy as np
import ipywidgets as widgets
import imp # support amd/intel gpu
try:
    imp.find_module('torch_directml')
    found_directml = True
    import torch_directml # type: ignore
except ImportError:
    found_directml = False
if found_directml:
    device=torch_directml.device()
else:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  #!=cuda support
cache_dir = "./model_cache"
pipe = None
def ai(pro,negpro=''):
    global pipe
    s = time.time()
    # 测试分割函数
    if pipe == None:
        pipe = DiffusionPipeline.from_pretrained("eienmojiki/Anything-XL",cache_dir=cache_dir,allow_pickle=False,torch_dtype=torch.float16,)
        pipe.safety_checker = lambda images, clip_input: (images, None)
        pipe = pipe.to(device)
        # upscale = StableDiffusionUpscalePipeline.from_pretrained(
        #     model_id, variant="fp16", torch_dtype=torch.float16
        # ).to("cuda")
    negative_prompt = negpro
    print(int(time.time()))
    print(pro +'\n'+negpro)
    generated_image = pipe(prompt=pro,negative_prompt=negative_prompt,num_inference_steps=35,width=512, height=768, generator=torch.manual_seed(int(time.time()))).images[0]
    generated_image.save('result.png')
    current_working_directory = os.getcwd()
    print(current_working_directory)
    absolute_path = os.path.abspath(os.path.join(current_working_directory, "result.png"))
    os.chdir("Real-ESRGAN")
    os.system("python inference_realesrgan.py -n RealESRGAN_x2plus -i "+absolute_path+" -o " + current_working_directory)
    os.chdir(current_working_directory)
    os.remove("result.png")
    os.rename("result_out.png","result.png")#fix shit
    print(time.time() - s)
#ai("NSFW:3,explicit:3,sensitive\nbest quality, masterpiece, nekonya, catgirl, cute, loyal, 11-12 years old, 139cm, 36kg, M-shaped bangs, long hair, light green, pink eyes, cat ears, white fur inside ears","lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry，safe")