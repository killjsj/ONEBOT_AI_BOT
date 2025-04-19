import asyncio
import base64
from datetime import datetime
from io import BytesIO
import re
import threading
from time import sleep
from typing import Callable, Dict, Any, List
import os

import PIL

import ai
from .plugin_lib import *
config = {}
sp = False
atted = False
uset = 0
def permc(id,permneed,qqg):
    global config
    
    with open('config.json','r+') as f:
        config = json.load(f)
    if permneed == "admin":
        if id in config["admin"]:
            return True
        else:return False
    if permneed == "ai":
        if str(qqg) in config["group"]:
            return config["group"][str(qqg)]["ai"]
        else: 
            return config["group"]["0"]["ai"]
def seqc():
    global seq
    while True:
        if datetime.now().second == 30 or datetime.now().second == 0:
                                            seq = {}
        if datetime.now().second == 31 or datetime.now().second == 59:
                                            seq = {}
        if datetime.now().second ==29 or datetime.now().second == 1:
                                            seq = {}
        sleep(1)
# dont need send_msg and load_config 
# but need set_register and get_register
# soo you need """from .plugin_lib import *""" 
# im lazy:)
sp = False
def tensecond():
     global sp
     sp = True
     sleep(10)
     sp = False
def init():
    """
    Initialize the plugin.
    """
    
    
    server_thread = threading.Thread(target=seqc)
    server_thread.start()
    get_register()(qserverPlugin,"run_r",0) # register plugin class(rev mode) when event come,call "run_r" function
    get_register()(qserverPlugin,"run_ais",1) # register plugin class(rev mode) when event come,call "run_r" function
    # Add any initialization code here
la = 0
def process_message(data):
    self_id = data['self_id']
    raw_message = data['raw_message']
    message = data['message']
    has_self_at = any(
        item['type'] == 'at' and str(item['data']['qq']) == str(self_id)
    for item in message
    )
    if not has_self_at:
        return None
    for item in message:
        if item['type'] == 'reply':
            raw_message = raw_message.replace(f"[CQ:reply,id={item['data']['id']}]", "", 1)
            break
    for item in message:
        if item['type'] == 'at' and str(item['data']['qq']) == str(self_id):
            raw_message = raw_message.replace(
                f"[CQ:at,qq={item['data']['qq']},name={item['data'].get('name', '')}]","",1,)
            break
    return raw_message.strip()
class qserverPlugin():
    #need this
    def __init__(self,send_msg,lower_send,load_config):
        """
        Initialize the plugin instance.
        """
        global config
        self.send_msg = send_msg
        self.lower_send = lower_send
        self.load_config = load_config
        config = load_config()
        self.lang = config["lang"]
        self.mode = 0
        self.model_mode = config["online"]["model_mode"]
        self.langprom = os.path.join('lang', f'prompt_{self.lang}.txt')
        # Add any instance initialization code here
    seq = {}
    messages = {}
    def runchat(self,i,qqg,input,sender,self_id,me:str):
                                    """
                                    me:only used for audio,image
                                    """
                                    global messages,seq
                                    ng = str(qqg)
                                    if ng not in self.seq:
                                        self.seq[ng] = 1
                                    else:
                                        self.seq[ng] += 1
                                        user =''
                                    if sender.get("group","") == "add":
                                        user =  ''
                                    else:
                                        user =  '[CQ:at,qq=' + str(sender["user_id"]) + '] '   
                                    if self.seq[ng] > int(config["seq"]):
                                        self.send_msg({'msg_type':'group','number':qqg,'msg':"429 Too Many Requests"})
                                        return
                                    if ng not in self.messages:
                                        self.messages[ng] = [{"role": "system", "content": self.readprompt(self.langprom,self.mode)}]
                                    if self.model_mode == "audio":
                                        response,self.messages[str(qqg)] = ai.chat_stream_sound(self.messages.get(str(qqg),[]),input,qqg,sender,str(self_id),me)
                                        response_audio = f"[CQ:record,file=file://"+os.path.abspath("audio_assistant_temp.wav")+"]"
                                        outp = user+response
                                        self.send_msg({'msg_type':'group','number':qqg,'msg':response_audio})
                                        self.send_msg({'msg_type':'group','number':qqg,'msg':outp})
                                        # print(messages[str(qqg)])
                                    elif self.model_mode == "image":
                                        response,self.messages[str(qqg)] = ai.chat_stream_image_infer(self.messages.get(str(qqg),[]),input,qqg,sender,str(self_id),me)
                                        outp = user+response
                                        for a in config["output_blacklist"]:
                                                if a in outp:
                                                    outp = outp.replace(a,"filtered")   
                                        self.send_msg({'msg_type':'group','number':qqg,'msg':outp})
                                    elif self.model_mode == "stream":
                                            response,self.messages[str(qqg)] = ai.chat_stream(self.messages.get(str(qqg),[]),input,qqg,sender,str(self_id))
                                            outp = user+response
                                            for a in config["output_blacklist"]:
                                                if a in outp:
                                                    outp = outp.replace(a,"filtered")
                                            self.send_msg({'msg_type':'group','number':qqg,'msg':outp})
                                    else:
                                            response,self.messages[str(qqg)] = ai.chat(self.messages.get(str(qqg)),input,qqg,sender,str(self_id))
                                            outp = user+response
                                            for a in config["output_blacklist"]:
                                                if a in outp:
                                                    outp = outp.replace(a,"filtered")
                                            self.send_msg({'msg_type':'group','number':qqg,'msg':outp})
                                    if i > 30:
                                        self.messages = self.clearmessage(qqg,self.messages)
                                        i = 0
                                    # response = re.sub(
                                    #     r'<think>.*?</think>',  # 非贪婪匹配任意内容
                                    #     '', 
                                    #     response, 
                                    #     flags=re.DOTALL  # 允许.匹配换行符
                                    # ).strip()
                   
    def is_number(self,s):
        try:
            int(s)  # 尝试转换为浮点数
            return True
        except ValueError:
            return False
    def readprompt(self,file_from: str, target_i: int = 0):
        with open(file_from, 'r', encoding='utf-8') as file:
            prompt_list = file.readlines()
            if prompt_list[0][:4] != '```0':
                raise TypeError('prompt not correct format')
            # format check
            target = '```' + str(target_i)
            finall = ''
            check_p1 = False
            for a in prompt_list:
                a = a.strip()
                if check_p1:
                    if a[:3 + len(str(int(target_i) + 1))] == ('```' + str(int(target_i) + 1)) or a[:3 + len(str(int(target_i) + 1))] == "```":
                        finall = finall.strip('\n')
                        return finall
                    finall += a + '\n'
                if a[:3 + len(str(target_i))] == target:
                    check_p1 = True
            return None
    def clearmessage(self,qqg:int,messages:dict) -> dict:
        global mode
        qqg = str(qqg)
        if qqg in messages:
            del messages[qqg]
        messages[qqg] = [{"role": "system", "content": self.readprompt(self.langprom,self.mode)}]
        return messages
    
    def run_ais(self,rev,command:list[str]):
        config = self.load_config()
        self.model_mode = config["online"].get("model_mode", "normal") # normal, stream, audio, image
        send_msg = self.send_msg
        lang = config["lang"]
        if rev.get("post_type") == "meta_event":
            return
        qqg = rev['group_id']
        user = str(rev['user_id'])
        
        if ('/aisetting' in rev['raw_message'].lower()):
                                        attext = rev['raw_message']
                                        comm = rev['raw_message'].split(" ")
                                        if comm[1] == "reset":
                                            self.messages = self.clearmessage(qqg,self.messages)
                                            send_msg({'msg_type':'group','number':qqg,'msg':"200 OK AI CONTEXT RESET MODE "+str(self.mode)+" NOW"})
                                            print(f"reset context in group:{qqg} by:"+user)
                                        if self.is_number(comm[1]):
                                            try:
                                                comm[1] = int(comm[1])
                                                if comm[1] <= int(la) and comm[1] >= 0:
                                                    self.mode = comm[1]
                                                    if str(qqg) in self.messages:
                                                        if not self.messages[str(qqg)] == []:
                                                            self.messages[str(qqg)] = [{"role": "system", "content": self.readprompt(self.langprom,self.mode)},]
                                                        else:
                                                            self.messages[str(qqg)][0] = {"role": "system", "content": self.readprompt(self.langprom,self.mode)}
                                                    else:
                                                        self.clearmessage(qqg,self.messages)
                                                    send_msg({'msg_type':'group','number':qqg,'msg':"200 OK"})
                                                    print(f"mode change in group:{qqg} by:"+user)
                                                else:
                                                    send_msg({'msg_type':'group','number':qqg,'msg':"406 Not Acceptable"})
                                                    print("prompt:"+comm[1]+" 406 Not Acceptable")
                                            except ValueError:
                                                send_msg({'msg_type':'group','number':qqg,'msg':"406 Not Acceptable,string not acceptable"})  
                                                print("ValueError")     
                                        elif comm[1] == "None":     
                                            if str(qqg) in self.messages:
                                                        if not self.messages[str(qqg)] == []:
                                                            self.messages[str(qqg)] = []
                                                        else:
                                                            self.messages[str(qqg)] = self.messages[str(qqg)].pop(0)
                                            else:
                                                        self.clearmessage(qqg,self.messages)   
                                            send_msg({'msg_type':'group','number':qqg,'msg':"200 OK"})
        elif '/estop' in rev['raw_message'].lower().lstrip()[:6] and permc(str(rev['user_id']),"admin",qqg):
                                    sp = True
                                    threadc = threading.Thread(target=tensecond)
                                    threadc.start()   
                                    print(str(rev['user_id']+" is stopping ai for 10s!"))
                                    send_msg({'msg_type':'group','number':qqg,'msg':"200 OK STOP 10 SECOND"})
    
    #need this when you use rev mode rev:see https://283375.github.io/onebot_v11_vitepress/event/index.html (this is chinese)
    def run_r(self, rev: dict):
        """
        Run the plugin.
        """
        global uset,atted
        config = self.load_config()
        send_msg = self.send_msg
        lang = config["lang"]
        if rev.get("post_type") == "meta_event":
            return
        
        atted = False
        if rev.get('post_type') == "notice":
                                qqg = rev['group_id']
                                attext = rev.get("raw_message")
                                self_id = str(rev.get('self_id',0))
                                rm = rev.get('message')
                                sender = rev['sender']
                                if rev.get('notice_type') == "group_increase":
                                    if str(qqg) in config["group"]:
                                        if config["group"][str(qqg)]["enableaiwelcome"]:
                                            threadc = threading.Thread(target=self.runchat,args=(0,rev.get("group_id"),"有新人"+str(rev.get("user_id"))+"(qid)入群 请欢迎它",{"nickname":"系统自动提示","title":"","card":"","group":"add"},self_id,))
                                            threadc.start()  
                                            print("new user in "+rev.get("group_id")) 
                                        elif config["group"]["0"]["enableaiwelcome"]:
                                            threadc = threading.Thread(target=self.runchat,args=(0,rev.get("group_id"),"有新人"+str(rev.get("user_id"))+"(qid)入群 请欢迎它",{"nickname":"系统自动提示","title":"","card":"","group":"add"},self_id,))
                                            threadc.start()
                                            print("new user in "+rev.get("group_id")) 
        if rev.get("post_type") == "message":
                                qqg = rev['group_id']
                                attext = rev.get("raw_message")
                                self_id = str(rev.get('self_id',0))
                                rm = rev.get('message')
                                sender = rev['sender']
                                image:str = ""
                                AI_message_list: List[Dict] = []
                                if rm == None:
                                    atted = True
                                    if "[CQ:file," not in rev["raw_message"]:
                                        attext = rev['raw_message']
                                else:
                                    if type(rm) !=str:
                                        for item1 in rm:
                                            if item1.get('type') == 'at' and 'data' in item1:
                                                if item1['data'].get('qq') == self_id:
                                                    for item in rm:
                                                        if item.get('type') == 'text' and 'data' in item:
                                                            attext = item['data']['text']
                                                            atted = True
                                                            AI_message_list.append({"type": "text", "text": attext})
                                                        if item.get('type') == 'image':
                                                            image_name = item['data']['file']
                                                            def image_to_base64(image):
                                                                byte_data = BytesIO()# 创建一个字节流管道
                                                                image.save(byte_data, format="JPEG")# 将图片数据存入字节流管道
                                                                byte_data = byte_data.getvalue()# 从字节流管道中获取二进制
                                                                base64_str = base64.b64encode(byte_data).decode("ascii")# 二进制转base64
                                                                return base64_str
                                                            result = asyncio.run(self.lower_send("get_image",{"file_id":image_name}))
                                                            image = PIL.Image.open(result["data"]["file"])
                                                            image = image_to_base64(image)
                                                            AI_message_list.append({
                                                                "type": "image_url",
                                                                "image_url": {"url": f"data:image/png;base64,{image}"},
                                                            })
                                                    break
                                        
                                        print(AI_message_list)
                                if atted and permc(qqg,"ai",qqg)and not rev.get('post_type','message') == "message_sent" and not sp:
                                    uset = uset+1
                                    attext = attext.strip()
                                    attext = process_message(rev)
                                    if attext != "":
                                        print(str(rev['user_id'])+" is calling ai!")
                                        threadc = threading.Thread(target=self.runchat,args=(uset,qqg,attext,sender,self_id,AI_message_list))
                                        threadc.start()    
                                        if uset> 30:
                                            uset = 0
        
        # Add your plugin logic here
    
    