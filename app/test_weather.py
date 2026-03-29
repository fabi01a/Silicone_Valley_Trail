import requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "current_weather": True
}

response = requests.get(url, params=params)
data = response.json()

print(data)