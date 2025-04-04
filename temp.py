import asyncio
import json
import queue
import threading
from time import sleep

import websockets
request_queue = queue.Queue()
request_result_queue = queue.Queue()
wss = None
async def a():
    global wss
    while True:
            try:
                async with websockets.connect("ws://192.168.3.5:3001") as websocket:
                        wss = websocket
                        while True:
                            try:
                                dat = await websocket.recv()
                                try:
                                    reva = json.loads(dat)
                                    reva : dict = reva
                                    if "114514" in reva.get("echo",""):
                                        print("request_result_queue_received:",reva)
                                        request_result_queue.put_nowait(reva)
                                    request_queue.put(reva)
                                except json.JSONDecodeError:
                                    print("Received non-JSON data:", dat)
                                    #print("raw:", rev_json['raw_message']," type=",rev_json["post_type"])
                            except websockets.ConnectionClosed as e:
                                print("ws code:"+e.code)
                                if e.code == 1006:
                                    print('code 1006!restarting connect')
                                    await asyncio.sleep(2)
                                    break
            except ConnectionRefusedError as e:
                    print(e)
                    global count
                    if count == 10: 
                        return
                    count += 1
                    await asyncio.sleep(2)

async def lower_send(ENDPOINT:str,jsons:dict) -> dict:
    global wurl,wss
    if True:
            await wss.send(json.dumps({"action":ENDPOINT,"params":jsons,"echo":"114514"}))
            print("send to ws")
            r = request_result_queue.get()
            print(r)
            return r
    else:
        ttip = tip + ":" + str(tport)
        response = requests.post(ttip+"/"+ENDPOINT, json=jsons)
        return response.json()

threading.Thread(target=lambda: asyncio.run(a())).start()
sleep(100)
print(asyncio.run(lower_send("get_image",{"file_id":"5F15E884C2F5229F2CE50D662484FA1C.png"})))
