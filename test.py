import importlib
import importlib.util
import os
import sys
from typing import Any, Callable, Dict

# from plugin import example

def send_msg(msg: str) -> None:
    print(f"Sending message: {msg}")
def load_config() -> None:
    print(f"l")
def import_plugin(plugin_name: str, plugin_path: str) -> Any:
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
    a = plugin(send_msg,send_msg,load_config)
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
    

def load_all_plugins() -> Dict[str, Any]:
    global reg_list
    reg_list = []
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugin")
    
    if not os.path.exists(plugin_dir):
        print(f"cant found {plugin_dir}")
        return []
        
    for plugin_name in os.listdir(plugin_dir):
        print(f"loading plugin: {plugin_name}")
        plugin_path = os.path.join(plugin_dir, plugin_name)
        
        # 跳过非目录
        if not os.path.isdir(plugin_path):
            continue
        
        # 导入插件
        plugin = import_plugin(plugin_name, plugin_path)
        if plugin is not None:
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
                
    return reg_list

def call_command(rev,command: list[str]) -> None:
    global rec_dict
    for k,v in rec_dict.items():
        if command[0] == k or k == "":
            for n in v:
                    n(rev,command)
a = load_all_plugins()

call_command({},["/test1", "arg1", "arg2", "arg3"])