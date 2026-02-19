import random
from django.shortcuts import render
from django.http import HttpResponse  

# Create your views here. 

def home(request):
    #return HttpResponse('<h1>Welcome to the parking lot management system!</h1>')
    return render(request, 'home.html')

def parking(request):
    #return HttpResponse('<h1>Here you can see if the parking lot is full or not</h1>')
    return render(request, 'parking.html')

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
