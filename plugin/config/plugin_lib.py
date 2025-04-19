import json
from typing import Callable

def load_config() -> dict:
    raise NotImplementedError("load_config function is not implemented. May not register plugin.")
def send_msg(resp_dict):
    raise NotImplementedError("send_msg function is not implemented. May not register plugin.")
# dont need send_msg and load_config 
#but need set_register and get_register
_register = None

def set_register(func: Callable) -> None:
    global _register
    _register = func

def get_register() -> Callable:
    global _register
    if _register is None:
        raise ValueError("Register function is not set. Please call set_register first.")
    
    return _register