from typing import Callable, Dict, Any, List
import os
from .plugin_lib import *
from wakeonlan import send_magic_packet
# dont need send_msg and load_config 
# but need set_register and get_register
# soo you need """from .plugin_lib import *""" 
# im lazy:)
def init():
    """
    Initialize the plugin.
    """
    get_register()(examplePlugin,"run_c1",1,"/wake")
    print("Plugin initialized.")
    # Add any initialization code here
    
class examplePlugin():
    """
    Example plugin class.
    """
    #need this
    def __init__(self,send_msg,lower_send,load_config):
        """
        Initialize the plugin instance.
        """
        self.send_msg = send_msg
        self.lower_send = lower_send
        self.load_config = load_config
        
    #need this when you use command mode,command[0] = "/commandname",command[:-1] = "arg1 arg2 arg3...." in there,is "/test arg1 arg2 arg3...."
    def run_c1(self,rev, command: List[str]):
        """
        Run the plugin.
        """
        def permc(id,permneed,qqg = ""):
            global config
            
            with open('config.json','r+') as f:
                config = json.load(f)
            if permneed == "admin":
                if str(id) in config["admin"]:
                    return True
                else:return False
            if permneed == "ai":
                if str(qqg) in config["group"]:
                    return config["group"][str(qqg)]["ai"]
                else: 
                    return config["group"]["0"]["ai"]
        print("run_c1")
        print(rev.get("user_id"))
        print(rev)
        print(permc(rev.get("user_id"),"admin"))
        if(permc(rev.get("user_id"),"admin") and rev.get("group_id") != None):
            send_magic_packet("20-31-11-1A-07-CA")
            self.send_msg({'msg_type':"group",'number':rev["group_id"],'msg':"200 OK"})
        pass
