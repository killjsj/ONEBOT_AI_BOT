from datetime import datetime


def runchat(i,qqg,input,sender,self_id):
                                    global uset,messages,seq
                                    ng = str(qqg)
                                    if datetime.now().second == 30 or datetime.now().second == 0:
                                         seq = {}
                                    if ng not in seq:
                                        seq[ng] = 1
                                    else:
                                         seq[ng] += 1
                                    print(seq)
                                    user =  '[CQ:at,qq=231] '
                                    
                                    if seq[ng] > int(5):
                                        print({'msg_type':'group','number':qqg,'msg':"429 Too Many Requests"})
                                        return
                                    comm = input
                                    if ng not in messages:
                                        messages[ng] = [{"role": "system", "content": "132"}]
                                    response,messages[str(qqg)] = "",""
                                    print(messages.get(str(qqg)),comm,qqg,sender,str(self_id))
                                    if i > 30:
                                        messages = print("clear",qqg,messages)
                                        i = 0
                                    print(i-1)
                                    print({'msg_type':'group','number':qqg,'msg':user+response})
