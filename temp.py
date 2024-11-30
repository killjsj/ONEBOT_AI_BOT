import requests
import time
import slget
# POST请求的参数
post_params = {
    "search": "",
    "countryFilter": [],
    "hideEmptyServer": False,
    "hideFullServer": False,
    "friendlyFire": "null",
    "whitelist": "null",
    "modded": "null",
    "sort": "PLAYERS_DESC"
}

# 记录GET请求开始时间
post_start_time = time.time()

# 发送GET请求
post_response = requests.post("https://backend.scplist.kr/api/servers", json=post_params)
a = post_response.json()
for n in a["servers"]:
    if n["pastebin"] == "Q6u5vvmP"or n["pastebin"] == "YyMi7aUL":
        print(n)
# 记录GET请求结束时间
post_end_time = time.time()

# 计算GET请求执行时间
post_execution_time = post_end_time - post_start_time

# 记录POST请求开始时间
get_start_time = time.time()

# 发送POST请求
get_response = slget.getslserver([
                "YyMi7aUL",
                "Q6u5vvmP"
            ])

# 记录POST请求结束时间
get_end_time = time.time()

# 计算POST请求执行时间
get_execution_time = get_end_time - get_start_time

print(f"GET请求执行时间: {get_execution_time} 秒")
print(f"POST请求执行时间: {post_execution_time} 秒")
print(get_response,post_response)
if get_execution_time < post_execution_time:
    print("GET请求执行速度更快。")
elif get_execution_time > post_execution_time:
    print("POST请求执行速度更快。")
else:
    print("GET请求和POST请求执行速度相同。")