from django.shortcuts import render

from parqueadero.services import TRANSLATIONS, get_lang


def payments(request):
    lang = get_lang(request)
    amount = request.GET.get("amount", "")
    return render(
        request,
        "parqueadero/payments.html",
        {
            "amount": amount,
            "lang": lang,
            "translations": TRANSLATIONS[lang],
            "user": request.user,
        },
    )

