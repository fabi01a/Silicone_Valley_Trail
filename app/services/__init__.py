"""External integrations (APIs, etc.)."""

from app.services.weather import WeatherForecast, get_weather

__all__ = ["WeatherForecast", "get_weather"]
