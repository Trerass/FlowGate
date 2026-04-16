from django.shortcuts import render

from parqueadero.services import TRANSLATIONS, get_lang


def payments(request):
    lang = get_lang(request)
    amount = request.GET.get("amount", "")
    balance = 125000
    recharge_amount = int(amount) if str(amount).isdigit() else 0
    projected_balance = balance + recharge_amount
    return render(
        request,
        "parqueadero/payments.html",
        {
            "amount": amount,
            "balance": balance,
            "projected_balance": projected_balance,
            "rates": [
                {
                    "title": "Estudiante - Automovil",
                    "description": "Tarifa diaria para estudiantes con automovil convencional",
                    "value": "$8700 / dia",
                    "tone": "primary",
                },
                {
                    "title": "Estudiante - Motocicleta",
                    "description": "Tarifa diaria para estudiantes con motocicleta",
                    "value": "$5000 / dia",
                    "tone": "primary",
                },
                {
                    "title": "Visitante - Automovil",
                    "description": "Tarifa por hora para visitantes",
                    "value": "$4000 / hora",
                    "tone": "soft",
                },
                {
                    "title": "Vehiculo Electrico",
                    "description": "Sin cargo para vehiculos electricos",
                    "value": TRANSLATIONS[lang]["free"],
                    "tone": "success",
                },
            ],
            "lang": lang,
            "translations": TRANSLATIONS[lang],
            "user": request.user,
        },
    )

