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
  