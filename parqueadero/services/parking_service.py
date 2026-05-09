import random
from datetime import datetime

from django.utils import timezone

from parqueadero.models import AvisoEnCamino, Entrada, Parqueadero

from .localization import get_translation


def _can_view_parking(parqueadero, user):
    if parqueadero.tipo_acceso != "profesores":
        return True
    if not user or not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    try:
        return user.perfilusuario.tipo_usuario == "profesor"
    except Exception:
        return False


def _entrance_display_name(name):
    return name.split("(", 1)[0].strip()


def process_due_arrivals():
    due_notices = AvisoEnCamino.objects.select_related("entrada").filter(
        agregado_a_fila=False,
        cancelado=False,
        llegada_estimada__lte=timezone.now(),
    )

    for notice in due_notices:
        notice.entrada.fila = max(0, notice.entrada.fila) + 1
        notice.entrada.save(update_fields=["fila"])
        notice.agregado_a_fila = True
        notice.save(update_fields=["agregado_a_fila"])


def _build_weather(lang):
    weather_options = [
        {
            "es": {"label": "Nublado", "description": "Brisa ligera"},
            "en": {"label": "Cloudy", "description": "Light breeze"},
            "temperature": random.randint(19, 28),
            "humidity": random.randint(55, 82),
            "wind_speed": random.randint(6, 18),
            "icon": "cloud",
        },
        {
            "es": {"label": "Soleado", "description": "Buen tiempo para conducir"},
            "en": {"label": "Sunny", "description": "Good conditions for driving"},
            "temperature": random.randint(23, 31),
            "humidity": random.randint(38, 60),
            "wind_speed": random.randint(5, 14),
            "icon": "sun",
        },
        {
            "es": {"label": "Lluvioso", "description": "Maneja con precaucion"},
            "en": {"label": "Rainy", "description": "Drive carefully"},
            "temperature": random.randint(17, 24),
            "humidity": random.randint(75, 95),
            "wind_speed": random.randint(8, 22),
            "icon": "rain",
        },
    ]
    selected = random.choice(weather_options)
    return {
        "label": selected[lang]["label"],
        "description": selected[lang]["description"],
        "temperature": selected["temperature"],
        "humidity": selected["humidity"],
        "wind_speed": selected["wind_speed"],
        "icon": selected["icon"],
    }


def _occupancy_label(occupancy_percent, lang):
    if occupancy_percent >= 100:
        return {
            "text": get_translation(lang, "full"),
            "tone": "critical",
        }
    if occupancy_percent >= 90:
        return {
            "text": get_translation(lang, "almost_full"),
            "tone": "critical",
        }
    if occupancy_percent >= 70:
        return {
            "text": get_translation(lang, "moderate_label"),
            "tone": "warning",
        }
    return {
        "text": get_translation(lang, "fluid"),
        "tone": "positive",
    }


def _calculate_wait_time(queue_size, available_slots, occupancy_percent):
    if queue_size <= 0:
        return 0

    pressure_multiplier = 1.0 + max(0, occupancy_percent - 60) / 100
    availability_bonus = min(0.55, available_slots / 240)
    base_minutes = queue_size * 2.6 * pressure_multiplier
    adjusted_minutes = base_minutes * (1 - availability_bonus)

    if available_slots >= queue_size * 8:
        adjusted_minutes *= 0.62
    elif available_slots >= queue_size * 4:
        adjusted_minutes *= 0.78
    elif available_slots <= max(3, queue_size // 2):
        adjusted_minutes *= 1.28

    return max(2, round(adjusted_minutes))


def get_parking_data(lang, user=None):
    process_due_arrivals()
    parqueaderos = Parqueadero.objects.all().order_by("nombre")
    parqueadero_data = []
    total_fila = 0
    total_capacity = 0
    total_occupancy = 0

    for parqueadero in parqueaderos:
        if not _can_view_parking(parqueadero, user):
            continue

        ocupancia = min(parqueadero.capacidad, max(0, parqueadero.ocupancia))
        available_slots = max(parqueadero.capacidad - ocupancia, 0)
        occupancy_percent = (
            (ocupancia / parqueadero.capacidad) * 100 if parqueadero.capacidad else 0
        )
        status = _occupancy_label(occupancy_percent, lang)

        entradas = Entrada.objects.filter(parqueadero=parqueadero).order_by("nombre")
        entrada_data = []

        for index, entrada in enumerate(entradas):
            fila = max(0, entrada.fila)
            sector_availability = max(1, available_slots // max(1, len(entradas)))
            tiempo_espera = _calculate_wait_time(fila, sector_availability, occupancy_percent)
            entrada_data.append(
                {
                    "id": entrada.id,
                    "nombre": _entrance_display_name(entrada.nombre),
                    "fila": fila,
                    "tiempo_espera": tiempo_espera,
                    "highlight": "primary" if index == 0 else "default",
                }
            )
            total_fila += fila

        parqueadero_data.append(
            {
                "id": parqueadero.id,
                "nombre": parqueadero.nombre,
                "capacidad": parqueadero.capacidad,
                "ocupancia": ocupancia,
                "ocupancia_percent": round(occupancy_percent),
                "available_slots": available_slots,
                "status": status,
                "entradas": entrada_data,
            }
        )
        total_capacity += parqueadero.capacidad
        total_occupancy += ocupancia

    congestion_percent = min(95, max(18, round((total_fila * 3.8) + (total_occupancy / max(1, total_capacity)) * 38)))
    if congestion_percent >= 75:
        congestion_key = "high"
    elif congestion_percent >= 45:
        congestion_key = "moderate"
    else:
        congestion_key = "low"

    average_speed = max(12, round(48 - (congestion_percent * 0.34)))
    weather = _build_weather(lang)
    total_available = max(total_capacity - total_occupancy, 0)
    average_wait = round(
        sum(
            entrada["tiempo_espera"]
            for parqueadero in parqueadero_data
            for entrada in parqueadero["entradas"]
        )
        / max(
            1,
            sum(len(parqueadero["entradas"]) for parqueadero in parqueadero_data),
        )
    )

    if total_available > total_capacity * 0.22 and total_fila <= 12:
        recommendation_title = get_translation(lang, "consider_options")
        recommendation_text = (
            "Puedes venir en auto, el flujo actual luce manejable."
            if lang == "es"
            else "You can drive in today; traffic and parking pressure look manageable."
        )
    else:
        recommendation_title = get_translation(lang, "consider_options")
        recommendation_text = get_translation(lang, "recommendation_text")

    return {
        "parqueaderos": parqueadero_data,
        "weather": weather,
        "congestion": {
            "label": get_translation(lang, congestion_key),
            "percent": congestion_percent,
            "average_speed": average_speed,
        },
        "summary": {
            "total_slots": total_capacity,
            "occupied_slots": total_occupancy,
            "available_slots": total_available,
            "average_wait": average_wait,
        },
        "recommendation": {
            "title": recommendation_title,
            "text": recommendation_text,
            "wait_time": average_wait,
        },
        "updated_at": datetime.now().strftime("%H:%M:%S"),
    }
