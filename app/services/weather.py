"""Live weather → game conditions (OpenWeatherMap)."""

from __future__ import annotations

import os
import random
from typing import Any, TypedDict

import requests

from app.world.config import CITY_COORDS

OPENWEATHERMAP_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherForecast(TypedDict):
    condition: str
    fuel_multiplier: float


_FUEL_MULTIPLIER: dict[str, float] = {
    "clear": 1.0,
    "rain": 1.2,
    "fog": 1.1,
    "heat": 1.3,
}


def get_weather(start: str, end: str) -> WeatherForecast:
    """Map current weather at `start` to travel modifiers (`end` reserved for routing)."""
    del end  # API is point-based for now

    api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "").strip()
    if not api_key:
        condition = random.choice(["clear", "rain", "fog", "heat"])
        return WeatherForecast(
            condition=condition,
            fuel_multiplier=_FUEL_MULTIPLIER[condition],
        )

    try:
        lat, lon = CITY_COORDS.get(start, (37.7749, -122.4194))
        response = requests.get(
            OPENWEATHERMAP_URL,
            params={
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": "imperial",
            },
            timeout=5,
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        temp_f = float(data["main"]["temp"])

        if temp_f < 55:
            condition = "fog"
        elif temp_f > 85:
            condition = "heat"
        elif 55 <= temp_f <= 70:
            # Mild temps are common along the route; pure "rain" every leg felt repetitive.
            condition = random.choices(
                ["rain", "fog", "clear"],
                weights=[0.5, 0.28, 0.22],
            )[0]
        else:
            condition = random.choices(
                ["clear", "rain", "fog"],
                weights=[0.5, 0.25, 0.25],
            )[0]

    except Exception:
        condition = random.choice(["clear", "rain", "fog", "heat"])

    return WeatherForecast(
        condition=condition,
        fuel_multiplier=_FUEL_MULTIPLIER[condition],
    )
