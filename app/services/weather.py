"""Live weather → game conditions (Open-Meteo)."""

from __future__ import annotations

import random
from typing import Any, TypedDict

import requests

from app.world.config import CITY_COORDS


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

    try:
        lat, lon = CITY_COORDS.get(start, (37.7749, -122.4194))
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
            },
            timeout=2,
        )
        data: dict[str, Any] = response.json()
        temp_c = float(data["current_weather"]["temperature"])
        temp_f = (temp_c * 9 / 5) + 32

        if temp_f < 55:
            condition = "fog"
        elif temp_f > 85:
            condition = "heat"
        elif 55 <= temp_f <= 70:
            condition = "rain"
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
