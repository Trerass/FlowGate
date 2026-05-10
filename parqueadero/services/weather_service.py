import json
import logging
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings
from django.core.cache import cache


logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CACHE_KEY = "flowgate:weather:current"
WEATHER_CACHE_SECONDS = 600
REQUEST_TIMEOUT_SECONDS = 3

FALLBACK_WEATHER = {
    "temperature": 24,
    "humidity": 70,
    "wind_speed": 10,
    "weather_code": 3,
}

WEATHER_CODE_GROUPS = {
    "sun": {0, 1},
    "cloud": {2, 3, 45, 48},
    "rain": {
        51,
        53,
        55,
        56,
        57,
        61,
        63,
        65,
        66,
        67,
        71,
        73,
        75,
        77,
        80,
        81,
        82,
        85,
        86,
        95,
        96,
        99,
    },
}

WEATHER_TEXT = {
    "sun": {
        "es": {"label": "Soleado", "description": "Buen tiempo para conducir"},
        "en": {"label": "Sunny", "description": "Good conditions for driving"},
    },
    "cloud": {
        "es": {"label": "Nublado", "description": "Brisa ligera"},
        "en": {"label": "Cloudy", "description": "Light breeze"},
    },
    "rain": {
        "es": {"label": "Lluvioso", "description": "Maneja con precaucion"},
        "en": {"label": "Rainy", "description": "Drive carefully"},
    },
}


def _weather_group(weather_code):
    for group, codes in WEATHER_CODE_GROUPS.items():
        if weather_code in codes:
            return group
    return "cloud"


def _weather_url():
    params = {
        "latitude": getattr(settings, "FLOWGATE_WEATHER_LATITUDE", 6.2006),
        "longitude": getattr(settings, "FLOWGATE_WEATHER_LONGITUDE", -75.5786),
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "weather_code",
                "wind_speed_10m",
            ]
        ),
        "timezone": getattr(settings, "TIME_ZONE", "America/Bogota"),
        "wind_speed_unit": "kmh",
    }
    return f"{OPEN_METEO_URL}?{urlencode(params)}"


def _normalize_current_weather(payload):
    current = payload.get("current", {})
    return {
        "temperature": round(float(current["temperature_2m"])),
        "humidity": round(float(current["relative_humidity_2m"])),
        "wind_speed": round(float(current["wind_speed_10m"])),
        "weather_code": int(current["weather_code"]),
    }


def fetch_current_weather():
    with urlopen(_weather_url(), timeout=REQUEST_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return _normalize_current_weather(payload)


def get_current_weather(lang):
    current_weather = cache.get(WEATHER_CACHE_KEY)
    if current_weather is None:
        if getattr(settings, "FLOWGATE_WEATHER_API_ENABLED", True):
            try:
                current_weather = fetch_current_weather()
            except Exception as exc:
                logger.warning("Could not fetch Open-Meteo weather data: %s", exc)
                current_weather = FALLBACK_WEATHER.copy()
        else:
            current_weather = FALLBACK_WEATHER.copy()
        cache.set(WEATHER_CACHE_KEY, current_weather, WEATHER_CACHE_SECONDS)

    group = _weather_group(current_weather["weather_code"])
    text = WEATHER_TEXT[group].get(lang, WEATHER_TEXT[group]["es"])
    return {
        "label": text["label"],
        "description": text["description"],
        "temperature": current_weather["temperature"],
        "humidity": current_weather["humidity"],
        "wind_speed": current_weather["wind_speed"],
        "icon": group,
    }
