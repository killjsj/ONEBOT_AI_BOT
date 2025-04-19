from typing import Callable, Dict, Any, List
import os
from .plugin_lib import *
# dont need send_msg and load_config 
# but need set_register and get_register
# soo you need """from .plugin_lib import *""" 
# im lazy:)
def init():
    """
    Initialize the plugin.
    """
    get_register()(examplePlugin,"run_r",0) # register plugin class(rev mode) when event come,call "run_r" function
    get_register()(examplePlugin,"run_c",1) # register plugin class(command mode) command:/commandname arg1 arg2 arg3.... when someone use command will call arg1("test") 
    get_register()(examplePlugin,"run_c1",1,"/test1") # register plugin class(command mode) arg4("/test1") is command name,when somebody say:/test1 arg1 arg2 arg3.... will call run_c1
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
        # Add any instance initialization code here
    
    #need this when you use rev mode rev:see https://283375.github.io/onebot_v11_vitepress/event/index.html (this is chinese)
    def run_r(self, rev: dict):
        """
        Run the plugin.
        """
        # print("ExamplePlugin running.")
        pass
        # Add your plugin logic here
    
    #need this when you use command mode,command[0] = "/commandname",command[:-1] = "arg1 arg2 arg3...." in there,is "/test arg1 arg2 arg3...."
    def run_c(self, rev,command: List[str]):
        """
        Run the plugin.
        """
        pass

        # Add your plugin logic here
        
    #need this when you use command mode,command[0] = "/commandname",command[:-1] = "arg1 arg2 arg3...." in there,is "/test arg1 arg2 arg3...."
    def run_c1(self,rev, command: List[str]):
        """
        Run the plugin.
        """
        pass
