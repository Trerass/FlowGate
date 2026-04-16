import random

from parqueadero.models import Entrada, Parqueadero

from .localization import get_translation


def get_parking_data(lang):
    parqueaderos = Parqueadero.objects.all()
    parqueadero_data = []
    total_fila = 0

    for parqueadero in parqueaderos:
        ocupancia = random.randint(0, int(parqueadero.capacidad * 0.8))
        entradas = Entrada.objects.filter(parqueadero=parqueadero)
        entrada_data = []

        for entrada in entradas:
            fila = random.randint(0, 20)
            tiempo_espera = fila * 3
            entrada_data.append(
                {
                    "nombre": entrada.nombre,
                    "fila": fila,
                    "tiempo_espera": tiempo_espera,
                }
            )
            total_fila += fila

        ocupancia_percent = (
            (ocupancia / parqueadero.capacidad) * 100 if parqueadero.capacidad > 0 else 0
        )
        parqueadero_data.append(
            {
                "nombre": parqueadero.nombre,
                "capacidad": parqueadero.capacidad,
                "ocupancia": ocupancia,
                "ocupancia_percent": round(ocupancia_percent, 2),
                "entradas": entrada_data,
            }
        )

    weather_options = {
        "es": ["Soleado", "Lluvioso", "Nublado", "Tormentoso"],
        "en": ["Sunny", "Rainy", "Cloudy", "Stormy"],
    }
    weather = random.choice(weather_options.get(lang, weather_options["es"]))

    congestion_levels = [(10, "low"), (30, "moderate"), (float("inf"), "high")]
    congestion_key = "low"
    for threshold, level in congestion_levels:
        if total_fila < threshold:
            congestion_key = level
            break

    congestion = get_translation(lang, congestion_key)
    return parqueadero_data, weather, congestion

