import random
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Parqueadero, Entrada, PerfilUsuario, Vehiculo, Historial
from datetime import datetime

TOTAL_SPOTS = 150

# Diccionario de traducciones
TRANSLATIONS = {
    'es': {
        'welcome': 'Bienvenido a FlowGate',
        'weather': 'Estado del Clima',
        'congestion': 'Congestión Vehicular',
        'parking_status': 'Estado de los Parqueaderos',
        'capacity': 'Capacidad',
        'occupancy': 'Ocupancia',
        'entrance': 'Entrada',
        'queue': 'Fila',
        'waiting_time': 'Tiempo de espera',
        'minutes': 'minutos',
        'payments': 'Pagos',
        'login': 'Iniciar Sesión',
        'logout': 'Cerrar Sesión',
        'profile': 'Perfil',
        'history': 'Historial',
        'signup': 'Registrarse',
        'language': 'Idioma',
        'select_language': 'Selecciona un idioma',
        'sunny': 'Soleado',
        'rainy': 'Lluvioso',
        'cloudy': 'Nublado',
        'stormy': 'Tormentoso',
        'low': 'Baja',
        'moderate': 'Moderada',
        'high': 'Alta',
        'user_info': 'Información del Usuario',
        'vehicle_info': 'Información del Vehículo',
        'email': 'Correo Electrónico',
        'phone': 'Teléfono',
        'student_code': 'Código Estudiantil',
        'user_type': 'Tipo de Usuario',
        'plate': 'Placa',
        'brand': 'Marca',
        'model': 'Modelo',
        'color': 'Color',
        'vehicle_type': 'Tipo de Vehículo',
        'electric': 'Eléctrico',
        'daily_price': 'Precio Diario',
        'free': 'Gratis',
    },
    'en': {
        'welcome': 'Welcome to FlowGate',
        'weather': 'Weather Status',
        'congestion': 'Vehicle Congestion',
        'parking_status': 'Parking Status',
        'capacity': 'Capacity',
        'occupancy': 'Occupancy',
        'entrance': 'Entrance',
        'queue': 'Queue',
        'waiting_time': 'Waiting Time',
        'minutes': 'minutes',
        'payments': 'Payments',
        'login': 'Log In',
        'logout': 'Log Out',
        'profile': 'Profile',
        'history': 'History',
        'signup': 'Sign Up',
        'language': 'Language',
        'select_language': 'Select a language',
        'sunny': 'Sunny',
        'rainy': 'Rainy',
        'cloudy': 'Cloudy',
        'stormy': 'Stormy',
        'low': 'Low',
        'moderate': 'Moderate',
        'high': 'High',
        'user_info': 'User Information',
        'vehicle_info': 'Vehicle Information',
        'email': 'Email',
        'phone': 'Phone',
        'student_code': 'Student Code',
        'user_type': 'User Type',
        'plate': 'License Plate',
        'brand': 'Brand',
        'model': 'Model',
        'color': 'Color',
        'vehicle_type': 'Vehicle Type',
        'electric': 'Electric',
        'daily_price': 'Daily Price',
        'free': 'Free',
    }
}

def get_translation(lang, key):
    """Obtener traducción para una clave y idioma específicos."""
    return TRANSLATIONS.get(lang, TRANSLATIONS['es']).get(key, key)

def get_lang(request):
    """Obtener idioma de la sesión o por defecto español."""
    lang = request.GET.get('lang', request.session.get('lang', 'es'))
    if lang not in ['es', 'en']:
        lang = 'es'
    request.session['lang'] = lang
    return lang

def get_parking_data(lang):
    """Generar datos de parqueaderos aleatoriamente."""
    parqueaderos = Parqueadero.objects.all()
    parqueadero_data = []
    total_fila = 0
    total_ocupancia = 0
    total_capacidad = 0

    for p in parqueaderos:
        ocupancia = random.randint(0, int(p.capacidad * 0.8))
        
        entradas = Entrada.objects.filter(parqueadero=p)
        entrada_data = []
        
        for e in entradas:
            fila = random.randint(0, 20)
            tiempo_espera = fila * 3
            entrada_data.append({
                'nombre': e.nombre,
                'fila': fila,
                'tiempo_espera': tiempo_espera,
            })
            total_fila += fila
        
        ocupancia_percent = (ocupancia / p.capacidad) * 100 if p.capacidad > 0 else 0
        parqueadero_data.append({
            'nombre': p.nombre,
            'capacidad': p.capacidad,
            'ocupancia': ocupancia,
            'ocupancia_percent': round(ocupancia_percent, 2),
            'entradas': entrada_data,
        })
        total_ocupancia += ocupancia
        total_capacidad += p.capacidad

    weather_options_es = ["Soleado", "Lluvioso", "Nublado", "Tormentoso"]
    weather_options_en = ["Sunny", "Rainy", "Cloudy", "Stormy"]
    weather_options = weather_options_es if lang == 'es' else weather_options_en
    weather = random.choice(weather_options)

    if total_fila < 10:
        congestion_key = "low"
    elif total_fila < 30:
        congestion_key = "moderate"
    else:
        congestion_key = "high"
    
    congestion = get_translation(lang, congestion_key)

    return parqueadero_data, weather, congestion

def home(request):
    lang = get_lang(request)
    parqueadero_data, weather, congestion = get_parking_data(lang)
    
    context = {
        'parqueaderos': parqueadero_data,
        'weather': weather,
        'congestion': congestion,
        'lang': lang,
        'translations': TRANSLATIONS[lang],
        'user': request.user,
    }
    return render(request, "home.html", context)

@login_required(login_url='login_view')
def profile(request):
    lang = get_lang(request)
    user = request.user
    
    try:
        perfil = PerfilUsuario.objects.get(user=user)
    except PerfilUsuario.DoesNotExist:
        perfil = PerfilUsuario.objects.create(user=user)
    
    try:
        vehiculo = Vehiculo.objects.get(usuario=perfil)
    except Vehiculo.DoesNotExist:
        vehiculo = None
    
    context = {
        'perfil': perfil,
        'vehiculo': vehiculo,
        'lang': lang,
        'translations': TRANSLATIONS[lang],
    }
    return render(request, "profile.html", context)

@login_required(login_url='login_view')
def history(request):
    lang = get_lang(request)
    user = request.user
    
    try:
        perfil = PerfilUsuario.objects.get(user=user)
        historial = Historial.objects.filter(usuario=perfil)
    except PerfilUsuario.DoesNotExist:
        historial = []
    
    context = {
        'historial': historial,
        'lang': lang,
        'translations': TRANSLATIONS[lang],
    }
    return render(request, "history.html", context)

def login_view(request):
    lang = get_lang(request)
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home')
        
        elif action == 'signup':
            username = request.POST.get('signup_username')
            email = request.POST.get('email')
            password = request.POST.get('signup_password')
            phone = request.POST.get('phone')
            codigo = request.POST.get('codigo')
            tipo_usuario = request.POST.get('tipo_usuario', 'estudiante')
            
            if User.objects.filter(username=username).exists():
                context = {
                    'error': 'El usuario ya existe',
                    'lang': lang,
                    'translations': TRANSLATIONS[lang],
                }
                return render(request, 'login.html', context)
            
            user = User.objects.create_user(username=username, email=email, password=password)
            perfil = PerfilUsuario.objects.create(
                user=user,
                telefono=phone,
                codigo_estudiantil=codigo,
                tipo_usuario=tipo_usuario
            )
            
            login(request, user)
            return redirect('profile')
    
    context = {
        'lang': lang,
        'translations': TRANSLATIONS[lang],
    }
    return render(request, "login.html", context)

def logout_view(request):
    logout(request)
    return redirect('home')

def payments(request):
    lang = get_lang(request)
    
    amount = request.GET.get("amount", "")
    context = {
        "amount": amount,
        "lang": lang,
        'translations': TRANSLATIONS[lang],
        'user': request.user,
    }
    return render(request, "payments.html", context)
