"""
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
  """
from django.shortcuts import render
from django.http import HttpResponse

def home(request):

    # Se define una lista simulada de entradas
    # FR-01 (una entrada = un slider)
    entrances_data = [
        {"name": "North Entrance", "vehicles": 5},
        {"name": "South Entrance", "vehicles": 8},
    ]

    # Se crea una nueva lista que incluirá cálculos adicionales
    # FR-04 (vehicles × 10)
    entrances = []

    # Se recorre cada entrada para calcular su información derivada
    for e in entrances_data:

        # FR-04
        # Estimated Time = Number of vehicles × 10
        estimated_time = e["vehicles"] * 10

        # Se calcula el nivel de congestión para el slider
        # Se convierte a porcentaje (0–100)
        congestion_level = min(e["vehicles"] * 10, 100)

        # Se construye el diccionario final que usará el template
        entrances.append({
            "name": e["name"],
            "vehicles": e["vehicles"],
            "estimated_time": estimated_time,
            "congestion": congestion_level
        })

    # Se envía la información al template home.html
    # Esto permite que el {% for e in entrances %} funcione
    return render(request, "home.html", {"entrances": entrances})


def parking(request):
    return render(request, "parking.html")


def wTime(request):
    return render(request, "wTime.html")
