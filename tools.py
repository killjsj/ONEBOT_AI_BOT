import json
import requests

with open('config.json','r+') as f:
    config = json.load(f)
fht = config["secert"]["fht"]

def wea(Loc, adm, lang='zh'):
    try:
        geo = requests.get("https://geoapi.qweather.com/v2/city/lookup", params={"location": Loc, "key": fht, "lang": lang})
        geo.raise_for_status()
        geo_data = geo.json()
        location_ids = None
        for location in geo_data["location"]:
            if location["name"].lower() in Loc.lower() and (location["adm2"].lower() in adm.lower() or location["adm1"].lower() in adm.lower()):
                location_ids = location["id"]
                break
        if not location_ids:
            return -1, geo_data["location"]

        re = requests.get("https://devapi.qweather.com/v7/weather/now", params={"location": location_ids, "key": fht, "lang": lang})
        re.raise_for_status()
        weather_data = re.json()
        if weather_data.get("code") != "200":
            return 500, "Failed to get weather data"

        weather = ""
        for key, value in weather_data.get("now").items():
            if key == "temp":
                weather += f"Temperature: {value}°C\n" if lang == 'en' else f"温度: {value}°C\n"
            if key == "feelsLike":
                weather += f"Feels Like: {value}°C\n" if lang == 'en' else f"体感温度: {value}°C\n"
            if key == "windDir":
                weather += f"Wind Direction: {value}\n" if lang == 'en' else f"风向: {value}\n"
            if key == "text":
                weather += f"Weather: {value}\n" if lang == 'en' else f"天气: {value}\n"
            if key == "windSpeed":
                weather += f"Wind Speed: {value} km/h\n" if lang == 'en' else f"风速: {value} km/h\n"
            if key == "wind360":
                weather += f"Wind Direction (360°): {value}\n" if lang == 'en' else f"风向(360°): {value}\n"
            if key == "precip":
                weather += f"Precipitation: {value} mm\n" if lang == 'en' else f"降水量: {value} mm\n"
            if key == "pressure":
                weather += f"Pressure: {value} hPa\n" if lang == 'en' else f"气压: {value} hPa\n"
            if key == "vis":
                weather += f"Visibility: {value} km\n" if lang == 'en' else f"能见度: {value} km\n"
            if key == "obsTime":
                weather += f"Observation Time: {value}\n" if lang == 'en' else f"观测时间: {value}\n"

        day = requests.get("https://devapi.qweather.com/v7/indices/1d", params={"type": "1,3,5", "location": location_ids, "key": fht, "lang": lang})
        day.raise_for_status()
        for index in day.json().get("daily"):
            weather += f"{index['name']}: {index['category']} {index['text']} | "

        return 0, weather

    except requests.exceptions.ConnectionError:
        return 500, "Connection error"
    except requests.exceptions.HTTPError as http_err:
        return 500, f"HTTP error occurred: {http_err}"
    except Exception as e:
        return 500, f"An error occurred: {e}"