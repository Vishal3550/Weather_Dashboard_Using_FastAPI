import requests
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city, country):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None

