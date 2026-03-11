import random
from django.shortcuts import render

TOTAL_SPOTS = 150


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


def recommendations(request):
    entrance_25 = random.randint(0, 20)
    entrance_24 = random.randint(0, 20)

    time_25 = entrance_25 * 3
    time_24 = entrance_24 * 3

    weather_options = ["Sunny", "Rainy"]
    weather = random.choice(weather_options)

    avg_traffic = (entrance_25 + entrance_24) / 2

    if avg_traffic < 5:
        congestion = "Low"
    elif avg_traffic < 12:
        congestion = "Moderate"
    else:
        congestion = "High"

    if congestion == "High" or weather == "Rainy":
        recommendation = "High congestion expected. Consider delaying your arrival."
    elif congestion == "Moderate":
        recommendation = "Moderate traffic. Plan your arrival."
    else:
        recommendation = "Low traffic. Good time to arrive."

    context = {
        "entrance_25": entrance_25,
        "entrance_24": entrance_24,
        "time_25": time_25,
        "time_24": time_24,
        "weather": weather,
        "congestion": congestion,
        "recommendation": recommendation,
    }

    return render(request, "recommendations.html", context)


def payments(request):
    amount = parse_int(request.GET.get("amount"), 0)
    context = {
        "amount": max(0, amount),
        "payment_ready": amount > 0,
    }
    return render(request, "payments.html", context)


def login_view(request):
    context = {"logged_in": False, "username": ""}
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        context["username"] = username
        context["logged_in"] = bool(username and password)
    return render(request, "login.html", context)


def signup(request):
    context = {"registered": False, "username": ""}
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        context["username"] = username
        context["registered"] = bool(username and email and password)
    return render(request, "signup.html", context)