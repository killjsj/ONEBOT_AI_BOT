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
def readprompt(file_from:str,target_i:int = 0):
    target = str(target_i)
    target_i = int(target_i)
    with open(file_from,'r',encoding='utf-8') as file:
        prompt_list = file.readlines()
        if prompt_list[0][:4] != '```0':
            raise TypeError('prompt not correct format')
        #format check
        target = '```' + target
        check_p1 = False
        finall = ''
        for a in prompt_list:
            a = a.strip()
            if check_p1:
                if a[:3+len(str(int(target_i)+1))] == ('```' + str(int(target_i)+1)):
                    finall = finall.strip('\n')
                    return finall
                finall = finall + a + '\n'
            if a[:3+len(str(target_i))] == target:
                check_p1 = True
        return readprompt(file_from,0)
def lang_check(lang):
    if lang in support:
        print('lang check pass')
        return 0 # bruh
    else:
        raise Exception('Not support lang:' + lang)
mode = 0
start_messages = []
langprom = 'lang\\prompt_' + lang + '.txt'
messages = start_messages
request_queue = queue.Queue()
file_content_dict = {}
def permc(id,permneed):
    if permneed == "admin":
        if id in config["admin"]:
            return True
        else:return False
    if permneed == "ai":
        if str(qqg) in config["group"]:
            return config["group"][str(qqg)]["ai"]
        else: 
            return config["group"][0]["ai"]
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
            rev = json.loads(post_data)
            print(rev)
            request_queue.put(rev) 
        except json.JSONDecodeError:
            print("Received non-JSON data:", post_data)
            #print("raw:", rev_json['raw_message']," type=",rev_json["post_type"])
        
        self.send_response(204)
        self.end_headers()
        self.wfile.write(b"POST request processed.")
def run(server_class=http.server.HTTPServer, handler_class=QQRequestHandler):
    global fip,fport
    fport = int(fport)
    server_address = (fip, fport) #此处由onebot服务端发送post(HTTP POST：OneBot 作为 HTTP 客户端，向用户配置的 URL 推送事件，并处理用户返回的响应)
    httpd = server_class(server_address, handler_class)
    print("POST START")
    return httpd
def start_server():
    global httpd
    httpd = run()
    httpd.serve_forever()
def request_to_json(msg):
    for i in range(len(msg)):
        if msg[i]=="{" and msg[-1]=="\n":
            return json.loads(msg[i:])
    return None


def send_msg(resp_dict):
    global tip,tport
    msg_type = resp_dict['msg_type']  
    number = resp_dict['number'] 
    msg = resp_dict['msg'] 
    ttip = tip + ":" + str(tport)
    if msg_type == 'group':
        payl0 = {"message_type":msg_type,"group_id":number,"message":msg}
        print("sent " + payl0.__str__())
        print(msg)
        response = requests.post(ttip+"/send_msg", json=payl0)
        print(response.text)
        print(response.status_code)
    elif msg_type == 'private':
        payl0 = {"message_type":msg_type,"user_id":number,"message":msg}
        print("sent " + payl0)
        print(msg)
        response = requests.post(ttip+"/send_msg", json=payl0)
        print(response.text)
        print(response.status_code)
    return 0
def runchat(i,qqg):
                                    global uset,messages
                                    ng = qqg
                                    comm = rev['raw_message'].replace("/ai ", "")
                                    user = '[CQ:at,qq=' + str(rev['user_id']) + '] '
                                    response,messages = chat(messages,comm)
                                    if i >= 11:
                                        messages.clear()
                                        messages = [{"role": "system", "content": readprompt(langprom,mode)},]
                                    send_msg({'msg_type':'group','number':ng,'msg':user+response})
def run_group(rev):
                            global uset,qqg,messages
                            sender = rev['sender']
                            try:
                                roleq = sender['role']
                            except  Exception as a:
                                print (a.with_traceback)
                                roleq = "admin"
                            qqg = rev['group_id']
                            attext = ""
                            if ('/aisetting' in rev['raw_message']):
                                    attext = rev['raw_message']
                                    print(attext)
                                    comm = rev['raw_message'].split(" ")
                                    print(comm)
                                    if comm[1] == "reset":
                                        messages.clear()
                                        messages =[{"role": "system", "content":  readprompt(langprom,mode)},]
                                        send_msg({'msg_type':'group','number':qqg,'msg':"200 OK AI CONTEXT RESET MODE "+str(mode)+" NOW"})
                                    if is_number(comm[1]):
                                        try:
                                            comm[2] = int(comm[2])
                                            if comm[2] <= 1 and comm[2] >= 0:
                                                mode = comm[2]
                                                messages.clear()
                                                messages = [{"role": "system", "content": readprompt(langprom,0)},]
                                                messages[0]['content'] = readprompt(langprom,mode)
                                                print(messages)
                                                send_msg({'msg_type':'group','number':qqg,'msg':"200 OK"})
                                            else:
                                                send_msg({'msg_type':'group','number':qqg,'msg':"406 Not Acceptable"})
                                        except ValueError:
                                            send_msg({'msg_type':'group','number':qqg,'msg':"406 Not Acceptable,string not acceptable"})
                            if '/ai' in rev['raw_message'] and permc(qqg,"ai"):
                                uset = uset+1
                                
                                threadc = threading.Thread(target=runchat,args=(uset,qqg,))
                                threadc.start()      
                            if '/server' in rev['raw_message'] or rev['raw_message'].lower() == "cx":
                                ms = ''
                                if str(qqg) in config["group"]:
                                    if config["group"][str(qqg)]["cx->mc"]:
                                        ip = config["group"][str(qqg)]["mc_ip"]
                                        ms = mcserver.get_java_server_info(ip,lang)
                                    else:
                                        sl_pb = config["group"][str(qqg)]["sl_pb"]
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
                            if '/config' in rev['raw_message'][:6] and permc(rev['user_id'],"admin"):
                                command = rev['raw_message'][6:].split()
                                if command[0] == "group" and command[1] == "config":
                                    if command[2] == "cx->mc":
                                        if str(qqg) in config["group"]:
                                            config["group"][str(qqg)]["cx->mc"] = not(config["group"][str(qqg)]["cx->mc"])
                                            send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2mc ->" + str(config["group"][str(qqg)]["cx->mc"])})
                                        else: 
                                            config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                            config["group"][str(qqg)]["cx->mc"] = not(config["group"][str(qqg)]["cx->mc"])
                                            send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2mc ->" + str(config["group"][str(qqg)]["cx->mc"])})
                                    if command[2] == "ai":
                                        if str(qqg) in config["group"]:
                                            config["group"][str(qqg)]["ai"] = not(config["group"][str(qqg)]["ai"])
                                            send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK ai mode ->" + str(config["group"][str(qqg)]["ai"])})
                                        else: 
                                            config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                            config["group"][str(qqg)]["ai"] = not(config["group"][str(qqg)]["ai"])
                                            send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created ai mode ->" + str(config["group"][str(qqg)]["ai"])})
                                    if command[2] == "mcip":
                                        if str(qqg) in config["group"]:
                                            config["group"][str(qqg)]["mc_ip"] = command[3]
                                            send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2mc ip ->" + str(command[3])})
                                        else: 
                                            config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                            config["group"][str(qqg)]["mc_ip"] = command[3]
                                            send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2mc ip ->" + command[3]})
                                    if command[2] == "slpb":
                                        if str(qqg) in config["group"]:
                                            config["group"][str(qqg)]["sl_pb"] = command[2:]
                                            send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2sl pastebin changed"})
                                        else: 
                                            config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                            config["group"][str(qqg)]["sl_pb"] = command[2:]
                                            send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2sl pastebin changed"})
                                    if command[2] == "tdwf":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["tdwf"]["en"] = not(config["group"][str(qqg)]["tdwf"]["en"])
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK tdwf(today_wife) ->" + str(config["group"][str(qqg)]["tdwf"]["en"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["tdwf"]["en"] = not(config["group"][str(qqg)]["tdwf"]["en"])
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created tdwf(today_wife) ->" + str(config["group"][str(qqg)]["tdwf"]["en"])})                                          
                                    with open('config.json','w+') as f:
                                        json.dump(config,f)





if __name__ == '__main__':
        server_thread = threading.Thread(target=start_server)
        server_thread.start()
        lang_check(lang)
        while True:
            rev = request_queue.get()
            try:
                if rev == None:
                    continue
                if not rev["post_type"] == "meta_event":
                    print(rev)
                if rev["post_type"] == "meta_event":
                    if not rev["meta_event_type"] == "heartbeat":
                        print(rev)
            except KeyError:
                print(rev)
            finally:
                    try:
                        if rev != None:
                            print(rev)
                        if rev == None or (rev != None and rev['message_type'] == "private") or (rev != None and rev['notice_type'] != "message"):
                            try:
                                if (rev != None and rev['message_type'] == "private") or (rev != None and rev['notice_type'] != "message"):
                                    print(rev)
                                rev = {}
                                continue
                            except:
                                try:
                                    if (rev != None and rev['message_type'] == "private"):
                                            print(rev)
                                    rev = {}
                                    continue
                                except:
                                    try:
                                        if (rev != None and rev['notice_type'] != "message"):
                                            print(rev)
                                        rev = {}
                                        continue
                                    except:
                                        print("WHAT?????")
                            rev = {}
                            continue
                    except:
                        try:
                            if rev == None or (rev != None and rev['message_type'] == "private"):
                                if (rev != None and rev['message_type'] == "private") or (rev != None and rev['notice_type'] != "message"):
                                    print(rev)
                                rev = {}
                                continue
                        except:
                            try:
                                if rev == None or (rev != None and rev['notice_type'] != "message"):
                                    if (rev != None and rev['message_type'] == "private") or (rev != None and rev['notice_type'] != "message"):
                                        print(rev)
                                    rev = {}
                                    continue
                            except:
                                print("WHAT?????")
                    finally:
                        if (rev["post_type"] == "message" or rev["post_type"] == "message_sent") and rev['message_type'] == "group":
                            try:
                                threadc = threading.Thread(target=run_group,args=(rev,))
                                threadc.start() 
                            except Exception as a:
                               print(a.with_traceback())
