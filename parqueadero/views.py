from django.shortcuts import render

TOTAL_SPOTS = 150
AVERAGE_SERVICE_MINUTES = 10


def calculate_parking_status(occupied_spots, total_spots=TOTAL_SPOTS):
    occupied = max(0, min(occupied_spots, total_spots))
    available = total_spots - occupied
    return {
        "total_spots": total_spots,
        "occupied_spots": occupied,
        "available_spots": available,
        "is_full": available == 0,
        "occupancy_percent": round((occupied / total_spots) * 100, 10),
    }


def calculate_waiting_time(queue_size, average_service_minutes=AVERAGE_SERVICE_MINUTES):
    queue = max(0, queue_size)
    return queue * average_service_minutes


def parse_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def home(request):
    return render(request, "home.html")


def parking(request):
    occupied = parse_int(request.GET.get("occupied"), 0)
    status = calculate_parking_status(occupied)
    context = {"status": status}
    return render(request, "parking.html", context)


def wTime(request):
    queue_size = parse_int(request.GET.get("queue"), 0)
    waiting_minutes = calculate_waiting_time(queue_size)
    context = {
        "queue_size": max(0, queue_size),
        "average_service_minutes": AVERAGE_SERVICE_MINUTES,
        "waiting_minutes": waiting_minutes,
    }
    return render(request, "wTime.html", context)