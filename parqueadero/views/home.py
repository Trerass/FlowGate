from django.shortcuts import render

from parqueadero.services import TRANSLATIONS, get_lang, get_parking_data


def home(request):
    lang = get_lang(request)
    dashboard_data = get_parking_data(lang)
    context = {
        **dashboard_data,
        "lang": lang,
        "translations": TRANSLATIONS[lang],
        "user": request.user,
    }
    return render(request, "parqueadero/home.html", context)

