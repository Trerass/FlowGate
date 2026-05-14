import json

from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from parqueadero.models import RechargeTransaction, Wallet
from parqueadero.services import TRANSLATIONS, get_lang
from parqueadero.services.demo_payments import apply_demo_payment
from parqueadero.services.payments import (
    create_recharge_transaction,
    get_payment_provider,
    is_demo_provider,
    is_wompi_provider,
    normalize_amount_input,
)
from parqueadero.services.wompi import (
    WompiAPIError,
    WompiConfigurationError,
    apply_wompi_transaction_status,
    build_checkout_url,
    extract_transaction_payload,
    get_wompi_transaction,
    is_wompi_checkout_configured,
    verify_event_signature,
)


def _rates(lang):
    return [
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
    ]


def _payment_redirect(lang, tab="recharge", **params):
    query = {"lang": lang, "tab": tab}
    query.update({key: value for key, value in params.items() if value})
    query_string = "&".join(f"{key}={value}" for key, value in query.items())
    return f"{reverse('payments')}?{query_string}"


def _build_return_url(request):
    if settings.APP_BASE_URL:
        return f"{settings.APP_BASE_URL.rstrip('/')}{reverse('wompi_return')}"
    return request.build_absolute_uri(reverse("wompi_return"))


def payments(request):
    lang = get_lang(request)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login_view')}?lang={lang}")
        return redirect(_payment_redirect(lang))

    active_tab = request.GET.get("tab", "rates")
    if active_tab not in {"rates", "recharge", "history"}:
        active_tab = "rates"
    if not request.user.is_authenticated:
        active_tab = "rates"

    wallet = None
    transactions = RechargeTransaction.objects.none()
    balance = 0
    pending_checkout = None
    checkout_url = ""
    using_demo_checkout = False
    payment_provider = get_payment_provider()
    amount = request.GET.get("amount", "")
    status = request.GET.get("status", "")

    if request.user.is_authenticated:
        wallet = Wallet.objects.filter(user=request.user).first()
        balance = wallet.balance_cop if wallet else 0
        transactions = RechargeTransaction.objects.filter(user=request.user)

        reference = request.GET.get("reference", "")
        if active_tab == "recharge" and reference:
            pending_checkout = get_object_or_404(
                RechargeTransaction,
                user=request.user,
                reference=reference,
                status=RechargeTransaction.STATUS_PENDING,
            )
            amount = str(pending_checkout.amount_cop)
            try:
                if is_demo_provider():
                    using_demo_checkout = True
                elif is_wompi_provider() and is_wompi_checkout_configured():
                    checkout_url = build_checkout_url(pending_checkout, _build_return_url(request))
                else:
                    raise WompiConfigurationError("Wompi checkout keys are missing")
            except WompiConfigurationError:
                messages.error(request, TRANSLATIONS[lang]["wompi_config_missing"])
                pending_checkout = None

    return render(
        request,
        "parqueadero/payments.html",
        {
            "amount": amount,
            "active_tab": active_tab,
            "balance": balance,
            "checkout_url": checkout_url,
            "pending_checkout": pending_checkout,
            "payment_status": status,
            "rates": _rates(lang),
            "recharge_history": transactions,
            "payment_provider": payment_provider,
            "using_demo_checkout": using_demo_checkout,
            "wompi_configured": is_wompi_checkout_configured(),
            "lang": lang,
            "translations": TRANSLATIONS[lang],
            "user": request.user,
        },
    )


@require_POST
def create_recharge(request):
    lang = get_lang(request)
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login_view')}?lang={lang}")

    try:
        amount_cop = normalize_amount_input(request.POST.get("amount"))
    except ValueError:
        messages.error(request, TRANSLATIONS[lang]["invalid_recharge_amount"])
        return redirect(_payment_redirect(lang))

    provider = get_payment_provider()
    if provider == RechargeTransaction.PROVIDER_WOMPI and not is_wompi_checkout_configured():
        messages.error(request, TRANSLATIONS[lang]["wompi_config_missing"])
        return redirect(_payment_redirect(lang, amount=amount_cop))

    if not request.session.session_key:
        request.session.save()

    Wallet.objects.get_or_create(user=request.user)
    recharge = create_recharge_transaction(
        user=request.user,
        amount_cop=amount_cop,
        provider=provider,
        session_key=request.session.session_key,
    )
    messages.info(request, TRANSLATIONS[lang]["payment_pending"])
    return redirect(_payment_redirect(lang, reference=recharge.reference, amount=amount_cop))


@require_POST
def demo_payment(request):
    lang = get_lang(request)
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login_view')}?lang={lang}")
    if not is_demo_provider():
        return HttpResponseBadRequest("Demo checkout is disabled")

    reference = request.POST.get("reference", "")
    result = request.POST.get("result", "approved")
    payment_method = request.POST.get("payment_method", "card")
    recharge = get_object_or_404(
        RechargeTransaction,
        user=request.user,
        reference=reference,
        status=RechargeTransaction.STATUS_PENDING,
        provider=RechargeTransaction.PROVIDER_DEMO,
    )
    updated = apply_demo_payment(recharge, result, payment_method)

    if updated.status == RechargeTransaction.STATUS_APPROVED:
        messages.success(request, TRANSLATIONS[lang]["payment_approved"])
    elif updated.status == RechargeTransaction.STATUS_VOIDED:
        messages.info(request, TRANSLATIONS[lang]["payment_voided"])
    else:
        messages.error(request, TRANSLATIONS[lang]["payment_declined"])
    return redirect(_payment_redirect(lang, tab="history", status=updated.status.lower()))


def wompi_return(request):
    lang = get_lang(request)
    transaction_id = (
        request.GET.get("id")
        or request.GET.get("transaction_id")
        or request.GET.get("wompi_transaction_id")
    )
    reference = request.GET.get("reference")

    if not transaction_id and not reference:
        messages.error(request, TRANSLATIONS[lang]["payment_error"])
        return redirect(_payment_redirect(lang, tab="history", status="error"))

    try:
        wompi_transaction = get_wompi_transaction(transaction_id) if transaction_id else {}
    except (WompiAPIError, WompiConfigurationError, ValueError):
        messages.error(request, TRANSLATIONS[lang]["payment_error"])
        return redirect(_payment_redirect(lang, tab="history", status="error"))

    reference = wompi_transaction.get("reference") or reference
    if not reference:
        messages.error(request, TRANSLATIONS[lang]["payment_error"])
        return redirect(_payment_redirect(lang, tab="history", status="error"))

    recharge = get_object_or_404(RechargeTransaction, reference=reference)
    updated = apply_wompi_transaction_status(recharge, wompi_transaction)

    if updated.status == RechargeTransaction.STATUS_APPROVED:
        messages.success(request, TRANSLATIONS[lang]["payment_approved"])
    elif updated.status == RechargeTransaction.STATUS_PENDING:
        messages.info(request, TRANSLATIONS[lang]["payment_pending"])
    else:
        messages.error(request, TRANSLATIONS[lang]["payment_declined"])

    return redirect(_payment_redirect(lang, tab="history", status=updated.status.lower()))


@csrf_exempt
@require_POST
def wompi_webhook(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON")

    if not verify_event_signature(payload):
        return HttpResponseBadRequest("Invalid signature")

    wompi_transaction = extract_transaction_payload(payload)
    reference = wompi_transaction.get("reference")
    if not reference:
        return HttpResponseBadRequest("Missing reference")

    try:
        recharge = RechargeTransaction.objects.get(reference=reference)
    except RechargeTransaction.DoesNotExist:
        return HttpResponseBadRequest("Unknown reference")

    apply_wompi_transaction_status(recharge, wompi_transaction)
    return JsonResponse({"ok": True})
