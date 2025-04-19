# -*- coding: utf-8 -*-
# SHIT 小心观看
import base64
from datetime import datetime
import importlib
from io import BytesIO
import queue
import shutil
from types import ModuleType, TracebackType
import types
from typing import *
import re

import PIL
import PIL.Image
import ai
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
import importlib.util
import logging
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
def load_config():
    config = None
    with open('config.json','r+') as f:
        config = json.load(f)
    return config
config = load_config()
lang = config["lang"]
support = ['zh','en']
ws = config["network"]["ws"]["enable"]
fip = config["network"]["http"]["f"]["ip"]
tip = config["network"]["http"]["t"]["ip"]
tport = config["network"]["http"]["t"]["port"]
fport = config["network"]["http"]["f"]["port"]
wurl = config["network"]["ws"]["url"]
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



def lang_check(lang):
    if lang in support:
        print('lang check pass')
        return 0 #; bruh
    else:
        raise Exception('Not support lang:' + lang)


request_queue = queue.Queue()
request_result_queue = queue.Queue()
def import_plugin(plugin_name: str, plugin_path: str) -> ModuleType:
    # try:
        # 获取完整路径
        init_file = os.path.join(plugin_path, "__init__.py")
        if not os.path.exists(init_file):
            print(f"plugin {plugin_name} lost __init__.py")
            return None
            
        # 构造模块名称
        module_name = f"plugin.{plugin_name}"
        # 像普通import一样导入
        spec = importlib.util.spec_from_file_location(module_name, init_file)
        if spec is None:
            print(f"can not import {plugin_name} (spec_from_file_location) ")
            return None
            
        # 创建新模块
        module = importlib.util.module_from_spec(spec)
        
        # 将模块添加到sys.modules
        sys.modules[module_name] = module
        
        # 执行模块
        spec.loader.exec_module(module)
        
        return module
        
    # except Exception as e:
    #     print(f"error! import {plugin_name} : {str(e)} {e.__traceback__.tb_frame.f_code}")
    #     return None
reg_list = []
rev_list = []
rec_dict:dict[str,list[Callable]] = {}
    
def register(plugin,f:str,mode:int = 0,command:str="") -> None:
    print(f"registing plugin class: {plugin.__name__}")
    a = plugin(send_msg,lower_send,load_config)
    reg_list.append(a)
    if mode == 0:
        # 注册rev模式
        print(f"registing plugin rev")
        
        if not hasattr(a, f):
            raise Exception(f"plugin {plugin.__name__} not {f} function")
        rev_list.append(getattr(a, f))
    elif mode == 1:
        # 注册command模式
        print(f"registing plugin command: {command}")
        
        if not hasattr(plugin, f):
            raise Exception(f"plugin {plugin.__name__} not {f} function")
        if rec_dict.get(command,[]) == []:
            rec_dict[command] = [getattr(a, f)]
        else:
            rec_dict[command].append(getattr(a, f))
    

def load_all_plugins() -> Union[Dict[str, Any], ModuleType]:
    global reg_list
    reg_list = []
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugin")
    
    if not os.path.exists(plugin_dir):
        print(f"cant found {plugin_dir}")
        return []
    plugins = []
    
    for plugin_name in os.listdir(plugin_dir):
        print(f"loading plugin: {plugin_name}")
        plugin_path = os.path.join(plugin_dir, plugin_name)
        
        # 跳过非目录
        if not os.path.isdir(plugin_path):
            continue
        
        # 导入插件
        plugin = import_plugin(plugin_name, plugin_path)
        if plugin is not None:
            plugins.append(plugin)
            try:
                # 初始化插件
                if hasattr(plugin, "set_register"):
                    plugin.set_register(register)
                else:
                    raise Exception(f"plugin {plugin_name} not set_register function")
                if hasattr(plugin, "init"):
                    plugin.init()
            except Exception as e:
                print(f"error at init {plugin_name}: {str(e)}")
                
    return reg_list,plugins

def call_command(rev,command: list[str]) -> None:
    global rec_dict
    for k,v in rec_dict.items():
        if command[0] == k or k == "":
            for n in v:
                    n(rev,command)

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
global loaded_plugin
loaded_plugin = []
def reload_plugin():
    print("reloading plugin")
    print(loaded_plugin)
    
    # 确保父包存在
    if 'plugin' not in sys.modules:
        # 创建空的父包模块
        plugin_module = types.ModuleType('plugin')
        plugin_module.__path__ = [os.path.join(os.path.dirname(__file__), "plugin")]
        sys.modules['plugin'] = plugin_module
    
    for n in loaded_plugin:
        try:
            # 重新加载模块
            importlib.reload(n)
            print(f"reloaded plugin:{n.__name__}")
        except Exception as e:
            print(f"Error reloading {n.__name__}: {str(e)}")

def run_r(rev):
                            rev:dict = rev
                            try:
                                
                                for n in rev_list:
                                    n(rev)
                                #command check(satrt by /)
                                if rev.get("raw_message"," ")[0] == "/": 
                                    command = rev["raw_message"].split()
                                    qqg = rev['group_id']
                                    if '/reload' in command[0] and permc(str(rev['user_id']),"admin",qqg):# someone forced my hand
                                        send_msg({'msg_type':'group','number':qqg,'msg':"200 OK RELOAD IN 1S!!!!"})
                                        print(str(rev['user_id'])+" is reload all plugin!")
                                        reload_plugin()
                                    call_command(rev,rev["raw_message"].split())
                            except Exception as e:
                                logging.exception(e)

if __name__ == '__main__':
        builtins.print = cprint
        
        server_thread = threading.Thread(target=start_server)
        server_thread.start()
        
        
        with open('config.json','r+') as f:
            config = json.load(f)
        for a in config["admin"]:
            print("admin:"+a)
        lang_check(lang)
        langhelp = os.path.join('lang', f'help_{lang}.txt')
        print("loading plugin....")
        plugin_list,tl1 = load_all_plugins()
        loaded_plugin = tl1
        print(loaded_plugin)
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
                                    print(a.with_traceback(None))
