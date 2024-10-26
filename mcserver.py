import socket
import time
 
def remove_mc_formatting(text):
   for code in range(0, 10):
       text = text.replace(f'§{code}', '')
   for code in 'abcdefklmnor':
       text = text.replace(f'§{code}', '')
   return text
 
def get_java_server_info(address,lang='en'):
   start_time = time.time()
   temp_ip, port = address, 25565

# 检查address是否包含冒号（:）
   if ":" in address:
      # 如果包含冒号，分割字符串获取IP地址和端口号
      temp_ip, port = address.split(":")
    # 确保端口号是整数
      port = int(port)
   else:
    # 如果不包含冒号，使用默认端口号25565
      temp_ip = address
      port = 25565

   temp_text = ""
   tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
       tcp_client.connect((temp_ip, int(port)))
       tcp_client.sendall(b'\xfe\x01')
       data = tcp_client.recv(1024)
       if data:
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
                return "server "+ address + " offline"
        elif lang == 'zh':
            return "服务器 "+ address + " 没了"
           
   except socket.error as e:
       if e.errno == 111:
           if lang == 'en':
               return "server "+ address + " offline"
           elif lang == 'zh':
               return "服务器"+ address + "没了"
       return f"connect error: {e}"
   finally:
       tcp_client.close()
