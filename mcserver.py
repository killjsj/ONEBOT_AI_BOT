import socket
import time
 
def remove_mc_formatting(text):
   for code in range(0, 10):
       text = text.replace(f'§{code}', '')
   for code in 'abcdefklmnor':
       text = text.replace(f'§{code}', '')
   return text
 
def get_java_server_info(address, port,lang='en'):
   start_time = time.time()
   temp_ip = address
   temp_text = ""
   tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
       tcp_client.connect((temp_ip, port))
       tcp_client.sendall(b'\xfe\x01')
       data = tcp_client.recv(1024)
       if data:
           temp_text = "\nlag:" + str(int((time.time() - start_time) * 1000)) + "ms"
           if data[:2] == b'\xff\x00':
               data_parts = data.split(b'\x00\x00\x00')
               if len(data_parts) >= 6:
                if lang == 'en':
                        temp_text += "\nserver ip:" + address + ':' + str(port)+ \
                                "\nserver version:" + data_parts[2].decode('latin1').replace('\x00', '') + \
                                "\nserver text:" + remove_mc_formatting(data_parts[3].decode('latin1').replace('\x00', '')) + \
                                "\nserver online players:" + data_parts[4].decode('latin1').replace('\x00', '') + \
                                "\nserver max players:" + data_parts[5].decode('latin1').replace('\x00', '')
                elif lang == 'zh':
                        temp_text += "\n服务器ip:" + address + ':' + str(port) + \
                               "\n服务器版本：" + data_parts[2].decode('latin1').replace('\x00', '') + \
                               "\n服务器提示文本：" + remove_mc_formatting(data_parts[3].decode('latin1').replace('\x00', '')) + \
                               "\n服务器在线人数：" + data_parts[4].decode('latin1').replace('\x00', '') + \
                               "\n服务器人数上限：" + data_parts[5].decode('latin1').replace('\x00', '')
               else:
                   temp_text += "\ndata format warn"
               return temp_text
           else:
               if lang == 'en':
                return "not compatible for server"
               elif lang == 'zh':
                    return "不兼容"
       else:
        if lang == 'en':
                return "server offline"
        elif lang == 'zh':
            return "服务器没了"
           
   except socket.error as e:
       return f"connect error: {e}"
   finally:
       tcp_client.close()