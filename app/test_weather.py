"""Quick check against OpenWeatherMap (requires OPENWEATHERMAP_API_KEY)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import requests

from app.load_env import load_dotenv_if_present
from app.services.weather import OPENWEATHERMAP_URL

load_dotenv_if_present()

if __name__ == "__main__":
    key = os.environ.get("OPENWEATHERMAP_API_KEY", "").strip()
    if not key:
        print("Set OPENWEATHERMAP_API_KEY in the environment.", file=sys.stderr)
        sys.exit(1)

    response = requests.get(
        OPENWEATHERMAP_URL,
        params={
            "lat": 37.7749,
            "lon": -122.4194,
            "appid": key,
            "units": "imperial",
        },
        timeout=10,
    )
    response.raise_for_status()
    print(response.json())
