import re
from typing import Callable, Dict, Any, List
import os
# la = 0
import ai
from main import reload_plugin, restart_program
from .plugin_lib import *
# dont need send_msg and load_config 
# but need set_register and get_register
# soo you need """from .plugin_lib import *""" 
# im lazy:)

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
def init():
    """
    Initialize the plugin.
    """
    get_register()(qserverPlugin,"run_c_c",1,"/config") # register plugin class(rev mode) when event come,call "run_r" function
    get_register()(qserverPlugin,"run_c_a",1) # register plugin class(rev mode) when event come,call "run_r" function
    # Add any initialization code here
    
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
        config = self.load_config()
        # Add any instance initialization code here
    
    #need this when you use rev mode rev:see https://283375.github.io/onebot_v11_vitepress/event/index.html (this is chinese)
    def run_c_c(self,rev, command: list):
        """
        Run the plugin.
        """
        config = self.load_config()
        send_msg = self.send_msg
        lang = config["lang"]
        qqg = rev['group_id']
        
        if '/config' in command[0] and permc(str(rev['user_id']),"admin",qqg):
                                    print(command)
                                    command = command[1:]
                                    if command[0] == "group":
                                        if command[1] == "cx->mc":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["cx->mc"] = not(config["group"][str(qqg)]["cx->mc"])
                                                print(str(rev['user_id'])+" is changing cx->mc -> "+str(config["group"][str(qqg)]["cx->mc"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2mc ->" + str(config["group"][str(qqg)]["cx->mc"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["cx->mc"] = not(config["group"][str(qqg)]["cx->mc"])
                                                print(str(rev['user_id'])+" is creating new config and changing cx->mc -> "+str(config["group"][str(qqg)]["cx->mc"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2mc ->" + str(config["group"][str(qqg)]["cx->mc"])})                                       
                                        if command[1] == "cx":  
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["cx"] = not(config["group"][str(qqg)]["cx"])
                                                print(str(rev['user_id'])+" is changing cx -> "+str(config["group"][str(qqg)]["cx"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server) ->" + str(config["group"][str(qqg)]["cx->mc"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["cx"] = not(config["group"][str(qqg)]["cx"])
                                                print(str(rev['user_id'])+" is creating new config and changing cx -> "+str(config["group"][str(qqg)]["cx"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server) ->" + str(config["group"][str(qqg)]["cx->mc"])})                                        
                                        if command[1] == "ai":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["ai"] = not(config["group"][str(qqg)]["ai"])
                                                print(str(rev['user_id'])+" is changing ai -> "+str(config["group"][str(qqg)]["ai"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK ai mode ->" + str(config["group"][str(qqg)]["ai"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["ai"] = not(config["group"][str(qqg)]["ai"])
                                                print(str(rev['user_id'])+" is creating new config and changing ai -> "+str(config["group"][str(qqg)]["ai"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created ai mode ->" + str(config["group"][str(qqg)]["ai"])})
                                        if command[1] == "welcome":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["enableaiwelcome"] = not(config["group"][str(qqg)]["enableaiwelcome"])
                                                print(str(rev['user_id'])+" is changing welcome -> "+str(config["group"][str(qqg)]["enableaiwelcome"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK ai mode ->" + str(config["group"][str(qqg)]["enableaiwelcome"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["enableaiwelcome"] = not(config["group"][str(qqg)]["enableaiwelcome"])
                                                print(str(rev['user_id'])+" is creating new config and changing welcome -> "+str(config["group"][str(qqg)]["enableaiwelcome"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created enableaiwelcome ->" + str(config["group"][str(qqg)]["enableaiwelcome"])})
                                        if command[1] == "mcip":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["mc_ip"] = command[2]
                                                print(str(rev['user_id'])+" is changing mcip -> "+command[2])
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2mc ip ->" + str(command[2])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["mc_ip"] = command[2]
                                                print(str(rev['user_id'])+" is creating new config and changing mcip -> "+command[2])
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2mc ip ->" + command[2]})
                                        if command[1] == "slpb":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["sl_pb"] = command[1:]
                                                print(str(rev['user_id'])+" is changing slpb -> "+str(command[1:]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK cx(/server)2sl pastebin changed"})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["sl_pb"] = command[1:]
                                                print(str(rev['user_id'])+" is creating new config and changing slpb -> "+str(command[1:]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created cx(/server)2sl pastebin changed"})
                                        if command[1] == "tdwf":
                                            if str(qqg) in config["group"]:
                                                config["group"][str(qqg)]["tdwf"]["en"] = not(config["group"][str(qqg)]["tdwf"]["en"])
                                                print(str(rev['user_id'])+" is changing tdwf -> "+str(config["group"][str(qqg)]["tdwf"]["en"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK tdwf(today_wife) ->" + str(config["group"][str(qqg)]["tdwf"]["en"])})
                                            else: 
                                                config["group"][str(qqg)] = config["group"]["0"] # copy a new config
                                                config["group"][str(qqg)]["tdwf"]["en"] = not(config["group"][str(qqg)]["tdwf"]["en"])
                                                print(str(rev['user_id'])+" is creating new config and changing tdwf -> "+str(config["group"][str(qqg)]["tdwf"]["en"]))
                                                send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK new config created tdwf(today_wife) ->" + str(config["group"][str(qqg)]["tdwf"]["en"])})              
                                        if command[1] == "seq":
                                            config["seq"] = int(command[2])
                                            print(str(rev['user_id'])+" is changing seq -> "+str(command[2]))
                                            send_msg({'msg_type':"group",'number':qqg,'msg':"200 OK seq(global) -> " + str(config["seq"])})                                          

                                        with open('config.json','w+') as f:
                                            json.dump(config,f,indent=4)              
                                    elif command[0] == "aiurl":
                                        ai.cbu(command[1],"")
                                        print(str(rev['user_id'])+" is changing ai url-> "+command[1])
                                        
                                        send_msg({'msg_type':'group','number':qqg,'msg':"200 OK AI URL CHANGED-> "+command[1]})
                                    elif command[0] == "aikey":
                                        ai.cbu("",command[1])
                                        print(str(rev['user_id'])+" is changing ai key-> "+command[1])
                                        send_msg({'msg_type':'group','number':qqg,'msg':"200 OK AI KEY CHANGED-> *****"})
                                    elif command[0] == "model":
                                        ai.cam(command[1])
                                        print(str(rev['user_id'])+" is changing model -> "+command[1])
                                        send_msg({'msg_type':'group','number':qqg,'msg':"200 OK MODEL CHANGED-> "+command[1]})
                                
    def run_c_a(self,rev, command: list):
        """
        Run the plugin.
        """
        config = self.load_config()
        send_msg = self.send_msg
        qqg = rev['group_id']
        lang = config["lang"]
        langhelp = os.path.join('lang', f'help_{lang}.txt')
        with open(langhelp,"r+",encoding='utf-8') as file:
            texts = file.readlines()
            text = ''
            for n in texts:
                text += n
        help_msg = text
        if '/help' in command[0]:
                                    send_msg({'msg_type':"group",'number':qqg,'msg':help_msg})
        if '/restart' in command[0] and permc(str(rev['user_id']),"admin",qqg):
                                    send_msg({'msg_type':'group','number':qqg,'msg':"200 OK RESTART IN 1S!!!!"})
                                    print(str(rev['user_id'])+" is restarting program!")
                                    restart_program()
        
        