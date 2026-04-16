from django.shortcuts import render

from parqueadero.services import TRANSLATIONS, get_lang, get_parking_data


def home(request):
    lang = get_lang(request)
    parqueadero_data, weather, congestion = get_parking_data(lang)
    context = {
        "parqueaderos": parqueadero_data,
        "weather": weather,
        "congestion": congestion,
        "lang": lang,
        "translations": TRANSLATIONS[lang],
        "user": request.user,
    }
    return render(request, "parqueadero/home.html", context)

