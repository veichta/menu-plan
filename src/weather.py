import requests
from datetime import datetime, date
import json
from typing import Literal


def get_weather(post_code: int, hour: int):
    if post_code < 1000 or post_code > 9658:
        raise ValueError("Invalid post code")
    if hour % 3 != 0:
        raise ValueError("Hour must be multiple of 3")

    weather = requests.get(
        f"https://app-prod-ws.meteoswiss-app.ch/v1/plzDetail?plz={post_code}00").json()

    graph = weather["graph"]
    if datetime.fromtimestamp(graph["start"] / 1e3).date() != date.today():
        raise LookupError("No weather data for today")

    # Temperature is given for every hour
    temperature = graph["temperatureMean1h"][hour]

    # Use the weather symbol to find the corresponding weather emojis
    # Symbols are given for every 3 hours
    symbol = graph["weatherIcon3hV2"][hour // 3]
    with open("data/weather_emojis.json", "r") as f:
        # Symbols at 1-42 are for day time, 101-142 are analogous for night time
        emoji = json.load(f)[str(symbol % 100)]

    return temperature, emoji
