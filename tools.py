import os
from dotenv import load_dotenv
import pandas as pd
import requests
load_dotenv()
fht = os.getenv("fht")

def wea(Loc,adm,lang='zh'):
    # df = pd.read_csv('China-City-List-latest.csv', header=1, encoding='utf-8')
    # filtered_df = df[(df['Location_Name_ZH'].str.contains(Loc)) &
    #                 ((df['Adm1_Name_ZH'].str.contains(adm)) | (df['Adm2_Name_ZH'].str.contains(adm)))]
    # location_ids = filtered_df['Location_ID']
    location_ids = ''
    try:
        geo = requests.get("https://geoapi.qweather.com/v2/city/lookup",params={"location":Loc,"key":fht})
        geo = geo.json()
        print(geo)
        for location in geo["location"]:
            if location["name"] == Loc and (location["adm2"] == adm or location["adm1"] == adm):
                location_ids = location["id"]
        re = requests.get("https://devapi.qweather.com/v7/weather/now",params={"location":location_ids,"key":fht,"lang":lang})
    except requests.exceptions.ConnectionError:
        return 500
    if re.json().get("code") != "200":
        return 500
    print(re.text)
    weather = ""
    for ke,va in re.json().get("now").items():
        if ke == "temp":
            weather = weather + "temp:" + va + "\n"
        # if ke == "feelsLike":
        #     weather = weather + "体感温度:" + va + "\n"
        # if ke == "windDir":
        #     weather = weather + "风向:" + va + "\n"
        # if ke == "text":
        #     weather = weather + "天气描述:" + va + "\n"
        # if ke == "windSpeed":
        #     weather = weather + "风速(km/h):" + va + "\n"
        # if ke == "wind360":
        #     weather = weather + "风向(360角度，正北为0°，顺时针旋转360度。即将360°平分为16份，正北=0°（360°），正东=90°，正南=180°，正西=270° 旋转风=-999 无持续风向=None):" + va + "\n"
        # if ke == "precip":
        #     weather = weather +  "过去1小时降水量 单位：毫米:" + va + "\n"
        # if ke == "pressure":
        #     weather = weather + "大气压强，默认单位：百帕:" + va + "\n"
        # if ke == "vis":
        #     weather = weather + "能见度，默认单位：公里:" + va + "\n"
        # if ke == "obsTime":
        #     weather = weather + "上次观察时间：" + va + "\n"
    # try:
    #     # day = requests.get("https://devapi.qweather.com/v7/indices/1d",params={"type":"1,3,5","location":location_ids,"key":fht,"lang":"zh"})
    #     # print(day.text)
    #     # weather = weather + "天气指数:"
    #     # for va in day.json().get("daily"):
    #     #     weather = weather +va['name'] + ":" +va['category'] + " " + va["text"] + "|"

    # except requests.exceptions.ConnectionError:
    #     return 500
    print(weather)
    return weather
