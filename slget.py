re = 0
import time
from bs4 import BeautifulSoup as bs
import requests
def getslserver(pb) -> list:
    global re
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
    try:
        printed_rows = []
        post_response = requests.post("https://backend.scplist.kr/api/servers", json=post_params)
        a = post_response.json()
        for n in a["servers"]:
            if n["pastebin"] in pb:
                printed_rows.append(n)

        if printed_rows == []:
            return "404"
        
        return printed_rows
    except:
        if re == 0:
            re = 1
            return getslserver(pb)
        else:
            re = 0
            return "500"