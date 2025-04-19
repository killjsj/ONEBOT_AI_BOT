import re
from typing import Callable, Dict, Any, List
import os
# la = 0
import mcserver
import slget
from .plugin_lib import *
# dont need send_msg and load_config 
# but need set_register and get_register
# soo you need """from .plugin_lib import *""" 
# im lazy:)
def init():
    """
    Initialize the plugin.
    """
    get_register()(qserverPlugin,"run_r",0) # register plugin class(rev mode) when event come,call "run_r" function
    # Add any initialization code here
    
class qserverPlugin():
    #need this
    def __init__(self,send_msg,lower_send,load_config):
        """
        Initialize the plugin instance.
        """
        self.send_msg = send_msg
        self.lower_send = lower_send
        self.load_config = load_config
        # Add any instance initialization code here
    
    #need this when you use rev mode rev:see https://283375.github.io/onebot_v11_vitepress/event/index.html (this is chinese)
    def run_r(self, rev: dict):
        """
        Run the plugin.
        """
        if rev.get("post_type") == "meta_event":
            return
        config = self.load_config()
        send_msg = self.send_msg
        lang = config["lang"]
        if rev.get("post_type") != "message":
            return
        qqg = rev['group_id']
        if rev['raw_message'].lower().startswith('/server') or rev['raw_message'].lower().startswith("cx"):
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
        
        # Add your plugin logic here
    
    