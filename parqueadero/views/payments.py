import re

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from parqueadero.models import MetodoPago, PerfilUsuario
from parqueadero.services import TRANSLATIONS, get_lang


def _digits_only(value):
    return re.sub(r"\D", "", value or "")


def _is_luhn_valid(digits):
    total = 0
    reverse_digits = digits[::-1]
    for index, digit in enumerate(reverse_digits):
        number = int(digit)
        if index % 2 == 1:
            number *= 2
            if number > 9:
                number -= 9
        total += number
    return total % 10 == 0


def _detect_card_brand(digits):
    if digits.startswith("4"):
        return "Visa"
    if len(digits) >= 2 and digits[:2] in {"34", "37"}:
        return "American Express"
    if len(digits) >= 2 and 51 <= int(digits[:2]) <= 55:
        return "Mastercard"
    if len(digits) >= 4 and 2221 <= int(digits[:4]) <= 2720:
        return "Mastercard"
    return "Tarjeta"


def _parse_expiry(value):
    match = re.fullmatch(r"\s*(\d{2})/(\d{2}|\d{4})\s*", value or "")
    if not match:
        return None

    month = int(match.group(1))
    year = int(match.group(2))
    if year < 100:
        year += 2000

    if month < 1 or month > 12:
        return None

    today = timezone.localdate()
    if (year, month) < (today.year, today.month):
        return None

    return month, year


def _save_payment_method(request, lang):
    card_number = _digits_only(request.POST.get("card_number"))
    cvv = _digits_only(request.POST.get("cvv"))
    titular = request.POST.get("card_name", "").strip().upper()
    expiry = _parse_expiry(request.POST.get("expiry"))

    valid_card = 13 <= len(card_number) <= 19 and _is_luhn_valid(card_number)
    valid_cvv = 3 <= len(cvv) <= 4

    if not titular or not expiry or not valid_card or not valid_cvv:
        messages.error(request, TRANSLATIONS[lang]["card_invalid"])
        return

    perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)
    MetodoPago.objects.filter(usuario=perfil, es_activa=True).update(es_activa=False)
    MetodoPago.objects.create(
        usuario=perfil,
        titular=titular,
        marca=_detect_card_brand(card_number),
        ultimos_cuatro=card_number[-4:],
        mes_expiracion=expiry[0],
        anio_expiracion=expiry[1],
    )
    messages.success(request, TRANSLATIONS[lang]["card_saved"])


def payments(request):
    lang = get_lang(request)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login_view')}?lang={lang}")
        recharge_amount = request.POST.get("amount", "")
        if request.POST.get("action") == "save_card":
            _save_payment_method(request, lang)
        redirect_url = f"{request.path}?lang={lang}&tab=recharge"
        if str(recharge_amount).isdigit() and int(recharge_amount) > 0:
            redirect_url = f"{redirect_url}&amount={recharge_amount}"
        return redirect(redirect_url)

    amount = request.GET.get("amount", "")
    balance = 125000
    recharge_amount = int(amount) if str(amount).isdigit() else 0
    projected_balance = balance + recharge_amount
    active_tab = request.GET.get("tab", "rates")
    if active_tab not in {"rates", "recharge", "history"}:
        active_tab = "rates"
    if recharge_amount > 0:
        active_tab = "recharge"
    if not request.user.is_authenticated:
        active_tab = "rates"

    show_payment_card = request.user.is_authenticated and active_tab == "recharge" and recharge_amount > 0
    payment_method = None
    if request.user.is_authenticated:
        perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)
        payment_method = MetodoPago.objects.filter(usuario=perfil, es_activa=True).first()

    return render(
        request,
        "parqueadero/payments.html",
        {
            "amount": amount,
            "active_tab": active_tab,
            "balance": balance,
            "payment_method": payment_method,
            "projected_balance": projected_balance,
            "show_payment_card": show_payment_card,
            "rates": [
                {
                    "title": TRANSLATIONS[lang]["student_car_title"],
                    "description": TRANSLATIONS[lang]["student_car_description"],
                    "value": f"$8700 {TRANSLATIONS[lang]['per_day']}",
                    "tone": "primary",
                },
                {
                    "title": TRANSLATIONS[lang]["personal_car_title"],
                    "description": TRANSLATIONS[lang]["personal_car_description"],
                    "value": f"$8700 {TRANSLATIONS[lang]['per_day']}",
                    "tone": "primary",
                },
                {
                    "title": TRANSLATIONS[lang]["student_motorcycle_title"],
                    "description": TRANSLATIONS[lang]["student_motorcycle_description"],
                    "value": f"$5000 {TRANSLATIONS[lang]['per_day']}",
                    "tone": "primary",
                },
                {
                    "title": TRANSLATIONS[lang]["visitor_car_title"],
                    "description": TRANSLATIONS[lang]["visitor_car_description"],
                    "value": f"$4000 {TRANSLATIONS[lang]['per_hour']}",
                    "tone": "soft",
                },
                {
                    "title": TRANSLATIONS[lang]["electric_vehicle_title"],
                    "description": TRANSLATIONS[lang]["electric_vehicle_description"],
                    "value": TRANSLATIONS[lang]["free"],
                    "tone": "success",
                },
            ],
            "lang": lang,
            "translations": TRANSLATIONS[lang],
            "user": request.user,
        },
    )

