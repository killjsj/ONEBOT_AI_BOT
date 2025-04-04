#from tkinter import Image
import importlib
import os
import sys
import time
from diffusers import DiffusionPipeline
import torch
import numpy as np
spec = importlib.util.find_spec('torch_directml')
found_directml = spec is not None
if found_directml:
    import torch_directml  # type: ignore
    device = torch_directml.device()
else:
    device = torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')  # !=cuda support


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
    os.system(sys.executable+" inference_realesrgan.py -n RealESRGAN_x2plus -i "+absolute_path+" -o " + current_working_directory)
    os.chdir(current_working_directory)
    os.remove("result.png")
    os.rename("result_out.png","result.png")#fix shit
    print(time.time() - s)