import random
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
    #return HttpResponse('<h1>Here you can see the waiting time for each parking spot</h1>')
    return render(request, 'wTime.html')
  




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
    queue_size = parse_int(request.GET.get("queue"), 0)
    waiting_minutes = calculate_waiting_time(queue_size)
    context = {
        "queue_size": max(0, queue_size),
        "average_service_minutes": AVERAGE_SERVICE_MINUTES,
        "waiting_minutes": waiting_minutes,
    }
    return render(request, "wTime.html", context)
