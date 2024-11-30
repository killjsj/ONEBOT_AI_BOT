# -*- coding: utf-8 -*-
# SHIT 小心观看
import queue
from typing import *
import re
from ai import chat
import slget
import time
import mcserver
import requests
import os
import random
import json
import http.server
import threading
from time import sleep
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
fip = config["network"]["f"]["ip"]
tip = config["network"]["t"]["ip"]
tport = config["network"]["t"]["port"]
fport = config["network"]["f"]["port"]
lang = config["lang"]
HttpResponseHeader = '''HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n\r\n
'''
# from wakeonlan import send_magic_packet #allow remote wakeup (if you dont need it,change wakeup true to false) this feature will remove at next version
#waiting for muilt lang
help_msg = f"""---bot help---
-/config        -修改机器人
--group         -修改群设置
--- cx->mc      -将cx替换成mc/sl(切换)
--- mcip        -修改检查的mc服务器ip 参数1: ip:port
--- slpb        -修改检查的sl服务器pastebin 参数1或更多:  pastebin1 参数2: pastebin2 ...
--- ai          -是否允许使用ai(切换)
--- tdwf        -未完成
-/server 或 cx  -查询设置的服务器
-/aisetting     -配置ai
--reset         -立刻重置ai记忆
--0,1,2....     -修改ai提示词(提示词见lang\\prompt_{lang}.txt 更多请检查项目的readme)
-直接@本机器人   -调用ai
"""

wakeup = True
wake_mac = '20.31.11.1A.07.CA' # input youe mac

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
langprom = os.path.join('lang', f'prompt_{lang}.txt')
messages = {}
request_queue = queue.Queue()
file_content_dict = {}
def permc(id,permneed,qqg):
    global config
    
    with open('config.json','r+') as f:
        config = json.load(f)
        print(config["admin"])
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

class QQRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        print(post_data)
        try:
            reva = json.loads(post_data)
            request_queue.put(reva) 
        except json.JSONDecodeError:
            print("Received non-JSON data:", post_data)
            #print("raw:", rev_json['raw_message']," type=",rev_json["post_type"])
        
        self.send_response(204)
        self.end_headers()
        self.wfile.write(b"POST request processed.")
def run_server(server_class=http.server.HTTPServer, handler_class=QQRequestHandler):
    global fip,fport
    fport = int(fport)
    server_address = (fip, fport) #此处由onebot服务端发送post(HTTP POST：OneBot 作为 HTTP 客户端，向用户配置的 URL 推送事件，并处理用户返回的响应)
    httpd = server_class(server_address, handler_class)
    print("POST START")
    return httpd
def start_server():
    global httpd
    httpd = run_server()
    httpd.serve_forever()
def request_to_json(msg):
    for i in range(len(msg)):
        if msg[i]=="{" and msg[-1]=="\n":
            return json.loads(msg[i:])
    return None


def wake():
    if wakeup:
        print("WOL")
        # send_msg({'msg_type':"private",'number':rev['user_id'],'msg':"WOL started"})
        # send_magic_packet(wake_mac)

def send_msg(resp_dict):
    global tip,tport
    msg_type = resp_dict['msg_type']  
    number = resp_dict['number'] 
    msg = resp_dict['msg'] 
    ttip = tip + ":" + str(tport)
    if msg_type == 'group':
        payl0 = {"message_type":msg_type,"group_id":number,"message":msg}
        print("sent " + repr(msg))
        response = requests.post(ttip+"/send_msg", json=payl0)
        print(response.text)
        print(response.status_code)
    elif msg_type == 'private':
        payl0 = {"message_type":msg_type,"user_id":number,"message":msg}
        print("sent " + repr(msg))
        response = requests.post(ttip+"/send_msg", json=payl0)
        print(response.text)
        print(response.status_code)
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

def runchat(i,qqg,input,sender,self_id):
                                    global uset,messages
                                    ng = str(qqg)
                                    comm = input
                                    user =  '[CQ:at,qq=' + str(rev['user_id']) + '] '
                                    if ng not in messages:
                                        messages[ng] = [{"role": "system", "content": readprompt(langprom,mode)}]
                                    
                                    response,messages[str(qqg)] = chat(messages.get(str(qqg)),comm,qqg,sender,str(self_id))
                                    
                                    if i >= 11:
                                        messages = clearmessage(qqg,messages)
                                    send_msg({'msg_type':'group','number':qqg,'msg':user+response})
def run_r(rev):
                            global uset,messages,config,mode,self_id
                            atted = False
                            attext = rev.get("raw_message")
                            print(rev.get('self_id',0))
                            self_id = str(rev.get('self_id',0))
                            if rev.get('message_type')=="group":
                                sender = rev['sender']
                                try:
                                    roleq = sender['role']
                                except  Exception as a:
                                    print (a.with_traceback)
                                    roleq = "admin"
                                rm = rev.get('message')
                                if rm == None:
                                    atted = True
                                    if "[CQ:file," not in rev["raw_message"]:
                                        attext = rev['raw_message']
                                else:
                                     for item in rm:
                                        if item.get('type') == 'at' and 'data' in item:
                                            if item['data'].get('qq') == self_id:
                                                for text_item in rm:
                                                    if text_item.get('type') == 'text' and 'data' in text_item:
                                                        attext = text_item['data']['text']
                                                        atted = True
                                                        break
                                qqg = rev['group_id']
                                if ('/aisetting' in rev['raw_message'].lower()):
                                        attext = rev['raw_message']
                                        print(attext)
                                        comm = rev['raw_message'].split(" ")
                                        print(comm)
                                        if comm[1] == "reset":
                                            messages = clearmessage(qqg,messages)
                                            send_msg({'msg_type':'group','number':qqg,'msg':"200 OK AI CONTEXT RESET MODE "+str(mode)+" NOW"})
                                        if is_number(comm[1]):
                                            try:
                                                comm[1] = int(comm[1])
                                                if comm[1] <= 1 and comm[1] >= 0:
                                                    mode = comm[1]
                                                    print(messages)
                                                    if str(qqg) in messages:
                                                        if not messages[str(qqg)] == []:
                                                            messages[str(qqg)] = [{"role": "system", "content": readprompt(langprom,mode)},]
                                                        else:
                                                            messages[str(qqg)][0] = {"role": "system", "content": readprompt(langprom,mode)}
                                                    else:
                                                        clearmessage(qqg,messages)
                                                    send_msg({'msg_type':'group','number':qqg,'msg':"200 OK"})
                                                else:
                                                    send_msg({'msg_type':'group','number':qqg,'msg':"406 Not Acceptable"})
                                            except ValueError:
                                                send_msg({'msg_type':'group','number':qqg,'msg':"406 Not Acceptable,string not acceptable"})                 
                                elif rev['raw_message'].lower().startswith('/server') or rev['raw_message'].lower().startswith("cx"):
                                    with open('config.json','r+') as f:
                                        config = json.load(f)
                                    ms = ''
                                    if str(qqg) in config["group"]:
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
                                        if config["group"]["0"]["cx->mc"]:
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
                                    print("/help")
                                    send_msg({'msg_type':"group",'number':qqg,'msg':help_msg})
                                elif '/config' in rev['raw_message'].lower().lstrip()[:7] and permc(str(rev['user_id']),"admin",qqg):
                                    command = rev['raw_message'].lstrip()[7:].split()
                                    print(command)
                                    if command[0] == "group":
                                        if command[1] == "cx->mc":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["cx->mc"] = not(config["group"][str(qqg)]["cx->mc"])
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2mc ->" + str(config["group"][str(qqg)]["cx->mc"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["cx->mc"] = not(config["group"][str(qqg)]["cx->mc"])
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2mc ->" + str(config["group"][str(qqg)]["cx->mc"])})
                                        if command[1] == "ai":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["ai"] = not(config["group"][str(qqg)]["ai"])
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK ai mode ->" + str(config["group"][str(qqg)]["ai"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["ai"] = not(config["group"][str(qqg)]["ai"])
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created ai mode ->" + str(config["group"][str(qqg)]["ai"])})
                                        if command[1] == "mcip":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["mc_ip"] = command[2]
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2mc ip ->" + str(command[2])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["mc_ip"] = command[2]
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2mc ip ->" + command[2]})
                                        if command[1] == "slpb":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["sl_pb"] = command[1:]
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2sl pastebin changed"})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["sl_pb"] = command[1:]
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2sl pastebin changed"})
                                        if command[1] == "tdwf":
                                                if str(qqg) in config["group"]:
                                                    config["group"][str(qqg)]["tdwf"]["en"] = not(config["group"][str(qqg)]["tdwf"]["en"])
                                                    send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK tdwf(today_wife) ->" + str(config["group"][str(qqg)]["tdwf"]["en"])})
                                                else: 
                                                    config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                    config["group"][str(qqg)]["tdwf"]["en"] = not(config["group"][str(qqg)]["tdwf"]["en"])
                                                    send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created tdwf(today_wife) ->" + str(config["group"][str(qqg)]["tdwf"]["en"])})                                          
                                        with open('config.json','w+') as f:
                                            json.dump(config,f,indent=4)
                                elif atted and permc(qqg,"ai",qqg)and not rev.get('post_type','message') == "message_sent":
                                    uset = uset+1
                                    attext = attext.strip()
                                    attext = process_message(rev)
                                    threadc = threading.Thread(target=runchat,args=(uset,qqg,attext,sender,self_id,))
                                    threadc.start()    
                            elif rev.get('message_type','group') == "private":
                                if '/wake' in rev['raw_message'] and permc(str(rev['user_id']),"admin",0):
                                    wake()




if __name__ == '__main__':
        server_thread = threading.Thread(target=start_server)
        server_thread.start()
        lang_check(lang)
        while True:
            rev = request_queue.get()
            try:
                if rev == None and rev == {}:
                    continue
                if not rev["post_type"] == "meta_event":
                    print(rev)
                elif rev["post_type"] == "meta_event":
                    if not rev["meta_event_type"] == "heartbeat":
                        print(rev)
            except KeyError:
                print(rev)
            finally:
                            if rev.get('post_type','message') == "message" or rev.get('post_type','message') == "message_sent":
                                try:
                                    threadc = threading.Thread(target=run_r,args=(rev,))
                                    threadc.start() 
                                except Exception as a:
                                    print(a.with_traceback())
