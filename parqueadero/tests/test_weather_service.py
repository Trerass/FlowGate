import json
from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from parqueadero.services.weather_service import (
    FALLBACK_WEATHER,
    get_current_weather,
)


class _FakeWeatherResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class WeatherServiceTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @override_settings(
        FLOWGATE_WEATHER_LATITUDE=6.2,
        FLOWGATE_WEATHER_LONGITUDE=-75.57,
        TIME_ZONE="America/Bogota",
    )
    @patch("parqueadero.services.weather_service.urlopen")
    def test_get_current_weather_uses_open_meteo_payload(self, mock_urlopen):
        mock_urlopen.return_value = _FakeWeatherResponse(
            {
                "current": {
                    "temperature_2m": 22.6,
                    "relative_humidity_2m": 81,
                    "weather_code": 61,
                    "wind_speed_10m": 12.4,
                }
            }
        )

        weather = get_current_weather("es")

        self.assertEqual(weather["label"], "Lluvioso")
        self.assertEqual(weather["description"], "Maneja con precaucion")
        self.assertEqual(weather["temperature"], 23)
        self.assertEqual(weather["humidity"], 81)
        self.assertEqual(weather["wind_speed"], 12)
        self.assertEqual(weather["icon"], "rain")
        self.assertIn("api.open-meteo.com/v1/forecast", mock_urlopen.call_args.args[0])

    @patch("parqueadero.services.weather_service.logger.warning")
    @patch("parqueadero.services.weather_service.urlopen", side_effect=TimeoutError)
    def test_get_current_weather_uses_deterministic_fallback_when_api_fails(
        self,
        _mock_urlopen,
        _mock_warning,
    ):
        weather = get_current_weather("en")

        self.assertEqual(weather["label"], "Cloudy")
        self.assertEqual(weather["temperature"], FALLBACK_WEATHER["temperature"])
        self.assertEqual(weather["humidity"], FALLBACK_WEATHER["humidity"])
        self.assertEqual(weather["wind_speed"], FALLBACK_WEATHER["wind_speed"])
        self.assertEqual(weather["icon"], "cloud")
