127.0.0.1 - - [22/Jan/2025 21:00:01] "POST / HTTP/1.1" 204 -
{'self_id': 3193986128, 'user_id': 1020120106, 'time': 1737550800, 'message_id': 1009984633, 'message_seq': 260781, 'message_type': 'group', 'sender': {'user_id': 1020120106, 'nickname': '小恩恩', 'card': 'killjsj', 'role': 'member', 'title': ''}, 'raw_message': '[CQ:at,qq=3193986128,name=机器人] @ 一下群主', 'font': 14, 'sub_type': 'normal', 'message': [{'type': 'at', 'data': {'qq': '3193986128', 'name': '机器人'}}, {'type': 'text', 'data': {'text': ' @ 一下群主'}}], 'message_format': 'array', 'post_type': 'message', 'group_id': 953504581}
3193986128
['1020120106']
calling  getgroup  args: {'nothing': 'something'}  result: 953504581
[......群内人, {'nickname': '小恩恩', 'user_id': 1020120106, 'card': 'killjsj', 'title': '', 'role': 'member'}, ......群内人]
{'nickname': 'ζั͡溡漪ั͡', 'user_id': 3500197013, 'card': 'DebugSenpai', 'title': '', 'role': 'admin'}
{'nickname': 'Aut_OvO_id', 'user_id': 2399347979, 'card': '密码Wormwake是看不见吗', 'title': '', 'role': 'owner'}
calling  getpeople  args: {'group': '953504581', 'filter_target': 'role', 'filter_cond': 'admin'}  result: [{'nickname': 'ζั͡溡漪ั͡', 'user_id': 3500197013, 'card': 'DebugSenpai', 'title': '', 'role': 'admin'}, {'nickname': 'Aut_OvO_id', 'user_id': 2399347979, 'card': '密码Wormwake是看不见吗', 'title': '', 'role': 'owner'}]
calling  getdeltpeopleinfo  args: {'groupid': '953504581', 'userid': '2399347979'}  result: {'status': 'ok', 'retcode': 0, 'data': {'group_id': 953504581, 'user_id': 2399347979, 'nickname': 'Aut_OvO_id', 'card': '密码Wormwake是看不见吗', 'sex': 'unknown', 'age': 19, 'area': '', 'level': '1', 'qq_level': 0, 'join_time': 1735748346, 'last_sent_time': 1737548389, 'title_expire_time': 0, 'unfriendly': False, 'card_changeable': True, 'is_robot': False, 'shut_up_timestamp': 0, 'role': 'owner', 'title': ''}, 'message': '', 'wording': ''}
sent '[CQ:at,qq=1020120106] [CQ:at,qq=2399347979] 群主喵~'
{"status":"ok","retcode":0,"data":{"message_id":934451482},"message":"","wording":""}
200
{"self_id":3193986128,"user_id":3193986128,"time":1737550806,"message_id":934451482,"message_seq":260782,"message_type":"group","sender":{"user_id":3193986128,"nickname":"机器人","card":"","role":"member","title":""},"raw_message":"[CQ:at,qq=1020120106,name=killjsj] [CQ:at,qq=2399347979,name=密码Wormwake是看不见吗] 群主喵~","font":14,"sub_type":"normal","message":[{"type":"at","data":{"qq":"1020120106","name":"killjsj"}},{"type":"text","data":{"text":" "}},{"type":"at","data":{"qq":"2399347979","name":"密码Wormwake是看不见吗"}},{"type":"text","data":{"text":" 群主喵~"}}],"message_format":"array","post_type":"message_sent","group_id":953504581,"target_id":953504581}

