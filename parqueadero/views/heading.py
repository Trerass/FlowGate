from django.shortcuts import render

from parqueadero.services import TRANSLATIONS, get_lang, get_parking_data


def heading(request):
    lang = get_lang(request)
    dashboard_data = get_parking_data(lang)
    eta = int(request.GET.get("eta", 15))
    selected = request.GET.get("parking")

    parking_options = []
    for parqueadero in dashboard_data["parqueaderos"]:
        adjusted_available = max(0, parqueadero["available_slots"] - max(0, eta - 10) // 3)
        parking_options.append(
            {
                **parqueadero,
                "projected_available": adjusted_available,
                "selected": selected == parqueadero["nombre"] or (not selected and not parking_options),
            }
        )

    context = {
        "lang": lang,
        "translations": TRANSLATIONS[lang],
        "user": request.user,
        "eta": eta,
        "parking_options": parking_options,
    }
    return render(request, "parqueadero/heading.html", context)
