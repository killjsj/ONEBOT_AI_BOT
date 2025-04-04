# -*- coding: utf-8 -*-
# SHIT 小心观看
import base64
from datetime import datetime
from io import BytesIO
import queue
import shutil
from typing import *
import re

import PIL
import PIL.Image
import ai
import slget
import time
import mcserver
import requests
import os

import asyncio
import websockets

import json
import http.server
import threading
from time import sleep
import builtins
oprint = builtins.print
def cprint(*args, **kwargs):
    oprint(f"<{datetime.now()}>:", *args, **kwargs)

# from wakeonlan import send_magic_packet
global rev_json
rev_json = None
global uset
n = 0
c = 0
self_id = 0
uset = 0
with open('config.json','r+') as f:
    config = json.load(f)
support = ['zh','en']
ws = config["network"]["ws"]["enable"]
fip = config["network"]["http"]["f"]["ip"]
tip = config["network"]["http"]["t"]["ip"]
tport = config["network"]["http"]["t"]["port"]
fport = config["network"]["http"]["f"]["port"]
wurl = config["network"]["ws"]["url"]
lang = config["lang"]
audio=config.get("allow_ai_sound", False)
# enablewelcome = config["lang"]
# sql:bool = config["sql"]
HttpResponseHeader = '''HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n\r\n
'''
from wakeonlan import send_magic_packet #allow remote wakeup (if you dont need it,change wakeup true to false) this feature will remove at next version
#waiting for muilt lang
help_msg = f"""---bot help---
-/config        -Modify bot settings
--group         -Modify group settings
--- cx->mc      -Replace cx with mc/sl (toggle)
--- mcip        -Change MC server IP to check. Parameter 1: ip:port
--- slpb        -Change SL server pastebin to check. Parameter 1 or more: pastebin1 Parameter 2: pastebin2 ...
--- ai          -Allow AI usage (toggle)
--- tdwf        -Not completed
--- welcome     -Enable welcome feature(use ai token)
--- seq         -Change this group call ai sequence(seq reset when 30s)
--aiurl         -change OpenAI api url (can use DM)
--aikey         -change OpenAI api key (can use DM)
--model         -change OpenAI api model (can use DM)
-/server or cx  -Query set server
-/aisetting     -Configure AI
-/restart       -Restart program
-/estop         -Stop call AI feature in 10s
--reset         -Reset AI memory immediately
--0,1,2....     -Modify AI prompts (prompts in lang\\prompt_{lang}.txt, check project readme for more)
-@bot directly  -Call AI"""

# wakeup = True
# wake_mac = '20-31-11-1A-07-CA' # input you mac

def readprompt(file_from: str, target_i: int = 0):
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

def lang_check(lang):
    if lang in support:
        print('lang check pass')
        return 0 # bruh
    else:
        raise Exception('Not support lang:' + lang)
mode = 0
la = 0
langprom = os.path.join('lang', f'prompt_{lang}.txt')
langhelp = os.path.join('lang', f'help_{lang}.txt')
messages = {}
request_queue = queue.Queue()
request_result_queue = queue.Queue()
file_content_dict = {}
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
def is_number(s):
    try:
        int(s)  # 尝试转换为浮点数
        return True
    except ValueError:
        return False
wss = None
class HTTPQQRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            reva = json.loads(post_data)
            request_queue.put(reva) 
        except json.JSONDecodeError:
            print("Received non-JSON data:", post_data)
        
        self.send_response(204)
        self.end_headers()
        self.wfile.write(b"POST request processed.")
def run_server(server_class=http.server.HTTPServer, handler_class=HTTPQQRequestHandler):
    global fip,fport
    fport = int(fport)
    server_address = (fip, fport) #此处由onebot服务端发送post(HTTP POST：OneBot 作为 HTTP 客户端，向用户配置的 URL 推送事件，并处理用户返回的响应)
    httpd = server_class(server_address, handler_class)
    print("POST server START")
    return httpd
async def wsserver():
    global tip,tport,running,wss
    running = True
    while True:
        try:
                async with websockets.connect(wurl) as websocket:
                    wss = websocket
                    while running:
                        try:
                            dat = await websocket.recv()
                            try:
                                reva = json.loads(dat)
                                reva : dict = reva
                                if "114514" in reva.get("echo",""):
                                    print("request_result_queue_received:",reva)
                                    request_result_queue.put_nowait(reva)
                                request_queue.put(reva)
                            except json.JSONDecodeError:
                                print("Received non-JSON data:", dat)
                                #print("raw:", rev_json['raw_message']," type=",rev_json["post_type"])
                        except websockets.ConnectionClosed as e:
                            print("ws code:"+e.code)
                            if e.code == 1006:
                                print('code 1006!restarting connect')
                                await asyncio.sleep(2)
                                break
        except ConnectionRefusedError as e:
                print(e)
                global count
                if count == 10: 
                    return
                count += 1
                await asyncio.sleep(2)
def start_server():
    global httpd
    ai.lower_send = lower_send
    
    if not ws:
        httpd = run_server()
        httpd.serve_forever()
    else:
        
        asyncio.run(wsserver())
def request_to_json(msg):
    for i in range(len(msg)):
        if msg[i]=="{" and msg[-1]=="\n":
            return json.loads(msg[i:])
    return None

# def wake():
#     if wakeup:
#         print("WOL")
#         send_msg({'msg_type':"private",'number':rev['user_id'],'msg':"WOL started"})
#         send_magic_packet(wake_mac)

async def lower_send(ENDPOINT:str,jsons:dict) -> dict:
    global wurl,wss
    if ws:
            await wss.send(json.dumps({"action":ENDPOINT,"params":jsons,"echo":"114514"}))
            print("send to ws")
            r = request_result_queue.get()
            print(r)
            return r
    else:
        ttip = tip + ":" + str(tport)
        response = requests.post(ttip+"/"+ENDPOINT, json=jsons)
        return response.json()
def send_msg(resp_dict):
    global tip,tport
    msg_type = resp_dict['msg_type']  
    number = resp_dict['number'] 
    msg = resp_dict['msg'] 
    ttip = tip + ":" + str(tport)
    if msg_type == 'group':
            payl0 = {"message_type":msg_type,"group_id":number,"message":msg}
            print("sending " + repr(msg))
            asyncio.run(lower_send("send_msg",payl0))
    elif msg_type == 'private':
            payl0 = {"message_type":msg_type,"user_id":number,"message":msg}
            
            print("sending " + repr(msg))
            asyncio.run(lower_send("send_msg",payl0))
    return 0

def clearmessage(qqg:int,messages:dict) -> dict:
    global mode,langprom
    qqg = str(qqg)
    if qqg in messages:
        del messages[qqg]
    messages[qqg] = [{"role": "system", "content": readprompt(langprom,mode)}]
    return messages

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
import sys
import subprocess
def restart_program():
    command = sys.executable + ' ' + __file__
    if not ws:
        httpd.server_close()
        # httpd.shutdown_request()
        httpd.shutdown()
    else:
        running = False
        wss.close()
    sleep(1)
    sys.exit(subprocess.call(command, shell=True))
seq = {}

def runchat(i,qqg,input,sender,self_id,picture:str = ""):
                                    global uset,messages,seq
                                    nrev = rev
                                    ng = str(qqg)
                                    if ng not in seq:
                                        seq[ng] = 1
                                    else:
                                        seq[ng] += 1
                                        user =''
                                    if sender.get("group","") == "add":
                                        user =  ''
                                    else:
                                        user =  '[CQ:at,qq=' + str(sender["user_id"]) + '] '   
                                    if seq[ng] > int(config["seq"]):
                                        send_msg({'msg_type':'group','number':qqg,'msg':"429 Too Many Requests"})
                                        return
                                    comm = input
                                    if ng not in messages:
                                        messages[ng] = [{"role": "system", "content": readprompt(langprom,mode)}]
                                    if audio:
                                        response,messages[str(qqg)] = ai.chat_stream_sound(messages.get(str(qqg),[]),comm,qqg,sender,str(self_id),picture)
                                        response_audio = f"[CQ:record,file=file://"+os.path.abspath("audio_assistant_temp.wav")+"]"
                                        outp = user+response
                                        send_msg({'msg_type':'group','number':qqg,'msg':response_audio})
                                        send_msg({'msg_type':'group','number':qqg,'msg':outp})
                                        # print(messages[str(qqg)])
                                    elif config["online"]["stream"]:
                                        response,messages[str(qqg)] = ai.chat_stream(messages.get(str(qqg),[]),comm,qqg,sender,str(self_id))
                                        outp = user+response
                                        for a in config["output_blacklist"]:
                                            if a in outp:
                                                outp = outp.replace(a,"filtered")
                                        send_msg({'msg_type':'group','number':qqg,'msg':outp})
                                    else:
                                        response,messages[str(qqg)] = ai.chat(messages.get(str(qqg)),comm,qqg,sender,str(self_id))
                                        outp = user+response
                                        for a in config["output_blacklist"]:
                                            if a in outp:
                                                outp = outp.replace(a,"filtered")
                                        send_msg({'msg_type':'group','number':qqg,'msg':outp})
                                    if i > 30:
                                        messages = clearmessage(qqg,messages)
                                        i = 0
                                    # response = re.sub(
                                    #     r'<think>.*?</think>',  # 非贪婪匹配任意内容
                                    #     '', 
                                    #     response, 
                                    #     flags=re.DOTALL  # 允许.匹配换行符
                                    # ).strip()
                                    
sp = False
def tensecond():
     global sp
     sp = True
     sleep(10)
     sp = False
def run_r(rev):
                            global uset,messages,config,mode,self_id,sp,la
                            atted = False
                            attext = rev.get("raw_message")
                            self_id = str(rev.get('self_id',0))
                            if rev.get('post_type') == "notice":
                                if rev.get('notice_type') == "group_increase":
                                    if str(qqg) in config["group"]:
                                        if config["group"][str(qqg)]["enableaiwelcome"]:
                                            threadc = threading.Thread(target=runchat,args=(0,rev.get("group_id"),"有新人"+str(rev.get("user_id"))+"(qid)入群 请欢迎它",{"nickname":"系统自动提示","title":"","card":"","group":"add"},self_id,))
                                            threadc.start()  
                                            print("new user in "+rev.get("group_id")) 
                                        elif config["group"]["0"]["enableaiwelcome"]:
                                            threadc = threading.Thread(target=runchat,args=(0,rev.get("group_id"),"有新人"+str(rev.get("user_id"))+"(qid)入群 请欢迎它",{"nickname":"系统自动提示","title":"","card":"","group":"add"},self_id,))
                                            threadc.start()
                                            print("new user in "+rev.get("group_id")) 
                                            
                            elif rev.get('message_type')=="group":
                                sender = rev['sender']
                                try:
                                    roleq = sender['role']
                                except  Exception as a:
                                    print (a.with_traceback)
                                    roleq = "admin"
                                nrev = rev
                                rm = rev.get('message')
                                image:str = ""
                                if rm == None:
                                    atted = True
                                    if "[CQ:file," not in rev["raw_message"]:
                                        attext = rev['raw_message']
                                else:
                                    if type(rm) !=str:
                                        for item in rm:
                                            if item.get('type') == 'at' and 'data' in item:
                                                if item['data'].get('qq') == self_id:
                                                    for text_item in rm:
                                                        if text_item.get('type') == 'text' and 'data' in text_item:
                                                            attext = text_item['data']['text']
                                                            atted = True
                                            if item.get('type') == 'image':
                                                            image_name = item['data']['file']
                                                            def image_to_base64(image):
                                                                byte_data = BytesIO()# 创建一个字节流管道
                                                                image.save(byte_data, format="JPEG")# 将图片数据存入字节流管道
                                                                byte_data = byte_data.getvalue()# 从字节流管道中获取二进制
                                                                base64_str = base64.b64encode(byte_data).decode("ascii")# 二进制转base64
                                                                return base64_str
                                                            nrev = rev
                                                            result = asyncio.run(lower_send("get_image",{"file_id":image_name}))
                                                            image = PIL.Image.open(result["data"]["file"])
                                                            image = image_to_base64(image)
                                                            break
                                rev = nrev
                                qqg = rev['group_id']
                                user = str(rev['user_id'])
                                if ('/aisetting' in rev['raw_message'].lower()):
                                        attext = rev['raw_message']
                                        comm = rev['raw_message'].split(" ")
                                        if comm[1] == "reset":
                                            messages = clearmessage(qqg,messages)
                                            send_msg({'msg_type':'group','number':qqg,'msg':"200 OK AI CONTEXT RESET MODE "+str(mode)+" NOW"})
                                            print(f"reset context in group:{qqg} by:"+user)
                                        if is_number(comm[1]):
                                            try:
                                                comm[1] = int(comm[1])
                                                if comm[1] <= int(la) and comm[1] >= 0:
                                                    mode = comm[1]
                                                    if str(qqg) in messages:
                                                        if not messages[str(qqg)] == []:
                                                            messages[str(qqg)] = [{"role": "system", "content": readprompt(langprom,mode)},]
                                                        else:
                                                            messages[str(qqg)][0] = {"role": "system", "content": readprompt(langprom,mode)}
                                                    else:
                                                        clearmessage(qqg,messages)
                                                    send_msg({'msg_type':'group','number':qqg,'msg':"200 OK"})
                                                    print(f"mode change in group:{qqg} by:"+user)
                                                else:
                                                    send_msg({'msg_type':'group','number':qqg,'msg':"406 Not Acceptable"})
                                                    print("prompt:"+comm[1]+" 406 Not Acceptable")
                                            except ValueError:
                                                send_msg({'msg_type':'group','number':qqg,'msg':"406 Not Acceptable,string not acceptable"})  
                                                print("ValueError")               
                                elif rev['raw_message'].lower().startswith('/server') or rev['raw_message'].lower().startswith("cx"):
                                    with open('config.json','r+') as f:
                                        config = json.load(f)
                                    ms = ''
                                    if str(qqg) in config["group"]:
                                        if  config["group"][str(qqg)]["cx"]:
                                            if config["group"][str(qqg)]["cx->mc"]:
                                                ip = config["group"][str(qqg)]["mc_ip"]
                                                ms = mcserver.get_java_server_info(ip,lang)
                                            else:
                                                sl_pb = config["group"][str(qqg)]["sl_pb"]
                                                server = slget.getslserver(sl_pb) #sl pastebin
                                                ms = ""
                                                if server != "404":
                                                    for no in server:
                                                        def remove_html_tags(text):
                                                            clean_text = re.sub(r'(?i)<[^>]+>', '', text)
                                                            return clean_text
                                                        # no = [remove_html_tags(item) for item in no]
                                                        no['info'] = remove_html_tags(no['info'])
                                                        if lang == 'zh':
                                                            ms = ms + no["info"] + " 玩家数:" + no["players"] +' ip:'+str(no["ip"])+":"+str(no["port"]) +"\n"
                                                        elif lang == 'en':
                                                            ms = ms + no["info"] + " players:" + no["players"] +' ip:'+str(no["ip"])+":"+str(no["port"])+"\n"
                                                elif server == "500":
                                                    if lang == 'zh':
                                                        ms = "内部错误 可能机器人网络问题 请稍后重试"
                                                    elif lang == 'en':
                                                        ms = "500 Interal error sorry:("
                                                elif server == "404":
                                                    if lang == 'zh':
                                                        ms = "服务器没了 可能没搜到或者机器人网络问题"
                                                    elif lang == 'en':
                                                        ms = "404 server offline:("
                                                else:
                                                    ms = server
                                    else: 
                                        if config["group"][str(qqg)]["cx->mc"]:
                                            ip = config["group"][str(qqg)]["mc_ip"]
                                            ms = mcserver.get_java_server_info(ip,lang)
                                        else:
                                            sl_pb = config["group"]["0"]["sl_pb"]
                                            server = slget.getslserver(sl_pb) #sl pastebin AND WAITING FOR REWRITE
                                            ms = ""
                                            if server != "404":
                                                for no in server:
                                                    def remove_html_tags(text):
                                                        clean_text = re.sub(r'(?i)<[^>]+>', '', text)
                                                        return clean_text
                                                    no = [remove_html_tags(item) for item in no]
                                                    if lang == 'zh':
                                                        ms = ms + no[3] + " 玩家数:" + no[5] +' ip:'+no[0]+"\n"
                                                    elif lang == 'en':
                                                        ms = ms + no[3] + " players:" + no[5] +' ip:'+no[0] +"\n"
                                            elif server == "500":
                                                if lang == 'zh':
                                                    ms = "内部错误 可能机器人网络问题 请稍后重试"
                                                elif lang == 'en':
                                                    ms = "500 Interal error sorry:("
                                            elif server == "404":
                                                if lang == 'zh':
                                                    ms = "服务器没了 可能没搜到或者机器人网络问题"
                                                elif lang == 'en':
                                                    ms = "404 server offline:("
                                            else:
                                                ms = server
                                    send_msg({'msg_type':"group",'number':qqg,'msg':ms})
                                    #wait for tdwf write:(
                                elif '/help' in rev['raw_message']:
                                    send_msg({'msg_type':"group",'number':qqg,'msg':help_msg})
                                elif '/config' in rev['raw_message'].lower().lstrip()[:7] and permc(str(rev['user_id']),"admin",qqg):
                                    command = rev['raw_message'].lstrip()[7:].split()
                                    print(command)
                                    if command[0] == "group":
                                        if command[1] == "cx->mc":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["cx->mc"] = not(config["group"][str(qqg)]["cx->mc"])
                                                print(str(rev['user_id']+" is changing cx->mc -> ")+str(config["group"][str(qqg)]["cx->mc"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2mc ->" + str(config["group"][str(qqg)]["cx->mc"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["cx->mc"] = not(config["group"][str(qqg)]["cx->mc"])
                                                print(str(rev['user_id']+" is creating new config and changing cx->mc -> ")+str(config["group"][str(qqg)]["cx->mc"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2mc ->" + str(config["group"][str(qqg)]["cx->mc"])})                                       
                                        if command[1] == "cx":  
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["cx"] = not(config["group"][str(qqg)]["cx"])
                                                print(str(rev['user_id']+" is changing cx -> ")+str(config["group"][str(qqg)]["cx"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server) ->" + str(config["group"][str(qqg)]["cx->mc"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["cx"] = not(config["group"][str(qqg)]["cx"])
                                                print(str(rev['user_id']+" is creating new config and changing cx -> ")+str(config["group"][str(qqg)]["cx"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server) ->" + str(config["group"][str(qqg)]["cx->mc"])})                                        
                                        if command[1] == "ai":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["ai"] = not(config["group"][str(qqg)]["ai"])
                                                print(str(rev['user_id']+" is changing ai -> ")+str(config["group"][str(qqg)]["ai"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK ai mode ->" + str(config["group"][str(qqg)]["ai"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["ai"] = not(config["group"][str(qqg)]["ai"])
                                                print(str(rev['user_id']+" is creating new config and changing ai -> ")+str(config["group"][str(qqg)]["ai"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created ai mode ->" + str(config["group"][str(qqg)]["ai"])})
                                        if command[1] == "welcome":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["enableaiwelcome"] = not(config["group"][str(qqg)]["enableaiwelcome"])
                                                print(str(rev['user_id']+" is changing welcome -> ")+str(config["group"][str(qqg)]["enableaiwelcome"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK ai mode ->" + str(config["group"][str(qqg)]["enableaiwelcome"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["enableaiwelcome"] = not(config["group"][str(qqg)]["enableaiwelcome"])
                                                print(str(rev['user_id']+" is creating new config and changing welcome -> ")+str(config["group"][str(qqg)]["enableaiwelcome"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created enableaiwelcome ->" + str(config["group"][str(qqg)]["enableaiwelcome"])})
                                        if command[1] == "mcip":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["mc_ip"] = command[2]
                                                print(str(rev['user_id']+" is changing mcip -> ")+command[2])
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2mc ip ->" + str(command[2])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["mc_ip"] = command[2]
                                                print(str(rev['user_id']+" is creating new config and changing mcip -> ")+command[2])
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2mc ip ->" + command[2]})
                                        if command[1] == "slpb":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["sl_pb"] = command[1:]
                                                print(str(rev['user_id']+" is changing slpb -> ")+str(command[1:]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2sl pastebin changed"})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["sl_pb"] = command[1:]
                                                print(str(rev['user_id']+" is creating new config and changing slpb -> ")+str(command[1:]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2sl pastebin changed"})
                                        if command[1] == "tdwf":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["tdwf"]["en"] = not(config["group"][str(qqg)]["tdwf"]["en"])
                                                print(str(rev['user_id']+" is changing tdwf -> ")+str(config["group"][str(qqg)]["tdwf"]["en"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK tdwf(today_wife) ->" + str(config["group"][str(qqg)]["tdwf"]["en"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["tdwf"]["en"] = not(config["group"][str(qqg)]["tdwf"]["en"])
                                                print(str(rev['user_id']+" is creating new config and changing tdwf -> ")+str(config["group"][str(qqg)]["tdwf"]["en"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created tdwf(today_wife) ->" + str(config["group"][str(qqg)]["tdwf"]["en"])})              
                                        if command[1] == "seq":
                                            config["seq"] = int(command[2])
                                            print(str(rev['user_id']+" is changing seq -> ")+str(command[2]))
                                            send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK seq(global) -> " + str(config["seq"])})                                          

                                        with open('config.json','w+') as f:
                                            json.dump(config,f,indent=4)              
                                    elif command[0] == "aiurl":
                                        ai.cbu(command[1],"")
                                        print(str(rev['user_id']+" is changing ai url-> ")+command[1])
                                        
                                        send_msg({'msg_type':'group','number':qqg,'msg':"200 OK AI URL CHANGED-> "+command[1]})
                                    elif command[0] == "aikey":
                                        ai.cbu("",command[1])
                                        print(str(rev['user_id']+" is changing ai key-> ")+command[1])
                                        send_msg({'msg_type':'group','number':qqg,'msg':"200 OK AI KEY CHANGED-> *****"})
                                    elif command[0] == "model":
                                        ai.cam(command[1])
                                        print(str(rev['user_id']+" is changing model -> ")+command[1])
                                        send_msg({'msg_type':'group','number':qqg,'msg':"200 OK MODEL CHANGED-> "+command[1]})
                                elif '/estop' in rev['raw_message'].lower().lstrip()[:6] and permc(str(rev['user_id']),"admin",qqg):
                                    sp = True
                                    threadc = threading.Thread(target=tensecond)
                                    threadc.start()   
                                    print(str(rev['user_id']+" is stopping ai for 10s!"))
                                    send_msg({'msg_type':'group','number':qqg,'msg':"200 OK STOP 10 SECOND"})
                                elif '/restart' in rev['raw_message'].lower().lstrip()[:9] and permc(str(rev['user_id']),"admin",qqg):
                                    send_msg({'msg_type':'group','number':qqg,'msg':"200 OK RESTARTING IN 1S!!!!"})
                                    print(str(rev['user_id']+" is restarting program!"))
                                    restart_program()
                                elif atted and permc(qqg,"ai",qqg)and not rev.get('post_type','message') == "message_sent" and not sp:
                                    uset = uset+1
                                    attext = attext.strip()
                                    attext = process_message(rev)
                                    if attext != "":
                                        print(str(rev['user_id'])+" is calling ai!")
                                        threadc = threading.Thread(target=runchat,args=(uset,qqg,attext,sender,self_id,image))
                                        threadc.start()    
                                        if uset> 30:
                                            uset = 0
                            elif rev.get('message_type','group') == "private":
                                if '/wake' in rev['raw_message'] and permc(str(rev['user_id']),"admin",0):
                                    pass
                                elif '/config' in rev['raw_message'].lower().lstrip()[:7] and permc(str(rev['user_id']),"admin",qqg):
                                    command = rev['raw_message'].lstrip()[7:].split()
                                    print(command)         
                                    if command[0] == "aiurl":
                                        ai.cbu(command[1],"")
                                        print(str(rev['user_id']+" is changing ai url-> ")+command[1])
                                        
                                        send_msg({'msg_type':'private','number':user,'msg':"200 OK AI URL CHANGED-> "+command[1]})
                                    elif command[0] == "aikey":
                                        ai.cbu("",command[1])
                                        print(str(rev['user_id']+" is changing ai key-> ")+command[1])
                                        send_msg({'msg_type':'private','number':user,'msg':"200 OK AI KEY CHANGED-> *****"})
                                    elif command[0] == "model":
                                        ai.cam(command[1])
                                        print(str(rev['user_id']+" is changing model -> ")+command[1])
                                        send_msg({'msg_type':'private','number':user,'msg':"200 OK MODEL CHANGED-> "+command[1]})

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
     
def read_last_prompt(file_from):
    with open(file_from, 'r', encoding='utf-8') as file:
        content = file.read()
        last_prompt_index = content.rfind('```',0,len(content[:-3]))
        if last_prompt_index == -1:
            raise TypeError('No prompt found in the file')
        last_prompt = content[last_prompt_index:]
        match = re.search(r'```(\d+)', last_prompt)
        if not match:
            raise TypeError('No valid prompt number found in the last prompt')
        last_prompt_number = match.group(1)
        return last_prompt_number
def escape_json_string(json_string: str) -> str:
    return json_string.replace('&#44;', ',').replace('&amp;', '&').replace('&#91;', '[').replace('&#93;', ']')
if __name__ == '__main__':

        builtins.print = cprint
    
        server_thread = threading.Thread(target=start_server)
        server_thread.start()
        server_thread = threading.Thread(target=seqc)
        server_thread.start()
        with open('config.json','r+') as f:
            config = json.load(f)
        for a in config["admin"]:
            print("admin:"+a)
        lang_check(lang)
        la=read_last_prompt(langprom)
        with open(langhelp,"r+",encoding='utf-8') as file:
            texts = file.readlines()
            text = ''
            for n in texts:
                text += n
        help_msg = text
                
        while True:
            rev = request_queue.get()
            try:
                if rev == None or rev == {}:
                    continue
                if not rev.get("post_type","") == "meta_event":
                    print(rev)
                elif rev.get("post_type","") == "meta_event":
                    if not rev.get("meta_event_type","") == "heartbeat":
                        print("meta_event:",rev)
            except KeyError:
                print("KeyError:",rev)
            finally:
                                try:
                                    threadc = threading.Thread(target=run_r,args=(rev,))
                                    threadc.start() 
                                except Exception as a:
                                    print(a.with_traceback())
