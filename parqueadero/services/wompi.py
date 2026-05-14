import hashlib
import hmac
import re
import uuid
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from parqueadero.models import RechargeTransaction
from parqueadero.services.payments import apply_transaction_status


MIN_RECHARGE_COP = 1000
MAX_RECHARGE_COP = 2_000_000


class WompiConfigurationError(RuntimeError):
    pass


class WompiAPIError(RuntimeError):
    pass


def is_wompi_checkout_configured():
    return bool(settings.WOMPI_PUBLIC_KEY and settings.WOMPI_INTEGRITY_SECRET)


def is_wompi_api_configured():
    return bool(settings.WOMPI_PRIVATE_KEY or settings.WOMPI_PUBLIC_KEY)


def normalize_amount_input(value):
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("empty")
    if re.search(r"(^|\s)-\s*\d", raw):
        raise ValueError("invalid")

    normalized = re.sub(r"[^\d,.]", "", raw)
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").split(",", 1)[0]
    elif "," in normalized:
        normalized = normalized.split(",", 1)[0]
    else:
        normalized = normalized.replace(".", "")

    if not normalized.isdigit():
        raise ValueError("invalid")

    try:
        amount = int(Decimal(normalized))
    except (InvalidOperation, ValueError):
        raise ValueError("invalid")

    if amount < MIN_RECHARGE_COP:
        raise ValueError("too_low")
    if amount > MAX_RECHARGE_COP:
        raise ValueError("too_high")
    return amount


def amount_to_cents(amount_cop):
    return int(amount_cop) * 100


def generate_reference(user_id=None):
    user_part = f"U{user_id}" if user_id else "S"
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    suffix = uuid.uuid4().hex[:10].upper()
    return f"FG-{timestamp}-{user_part}-{suffix}"


def generate_integrity_signature(reference, amount_in_cents, currency="COP"):
    secret = settings.WOMPI_INTEGRITY_SECRET
    if not secret:
        raise WompiConfigurationError("WOMPI_INTEGRITY_SECRET is required")
    raw_signature = f"{reference}{amount_in_cents}{currency}{secret}"
    return hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()


def build_checkout_url(recharge, redirect_url):
    if not is_wompi_checkout_configured():
        raise WompiConfigurationError("Wompi checkout keys are missing")

    params = {
        "public-key": settings.WOMPI_PUBLIC_KEY,
        "currency": recharge.currency,
        "amount-in-cents": recharge.amount_in_cents,
        "reference": recharge.reference,
        "redirect-url": redirect_url,
        "signature:integrity": generate_integrity_signature(
            recharge.reference,
            recharge.amount_in_cents,
            recharge.currency,
        ),
    }
    return f"https://checkout.wompi.co/p/?{urlencode(params)}"


def create_recharge_transaction(user, amount_cop, session_key=""):
    amount_in_cents = amount_to_cents(amount_cop)
    return RechargeTransaction.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        session_key=session_key or "",
        amount_cop=amount_cop,
        amount_in_cents=amount_in_cents,
        currency="COP",
        reference=generate_reference(getattr(user, "id", None)),
        status=RechargeTransaction.STATUS_PENDING,
    )


def get_wompi_transaction(wompi_transaction_id):
    if not is_wompi_api_configured():
        raise WompiConfigurationError("Wompi API keys are missing")

    token = settings.WOMPI_PRIVATE_KEY or settings.WOMPI_PUBLIC_KEY
    response = requests.get(
        f"{settings.WOMPI_API_BASE_URL}/transactions/{wompi_transaction_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=12,
    )
    if response.status_code >= 400:
        raise WompiAPIError(f"Wompi returned HTTP {response.status_code}")

    payload = response.json()
    return payload.get("data", payload)


def normalize_wompi_status(status):
    normalized = str(status or "").upper()
    if normalized in {
        RechargeTransaction.STATUS_APPROVED,
        RechargeTransaction.STATUS_DECLINED,
        RechargeTransaction.STATUS_ERROR,
        RechargeTransaction.STATUS_VOIDED,
    }:
        return normalized
    return RechargeTransaction.STATUS_PENDING


def _resolve_event_property(payload, property_path):
    current = payload.get("data", payload)
    for part in property_path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return ""
    return "" if current is None else current


def verify_event_signature(payload):
    secret = settings.WOMPI_EVENTS_SECRET
    if not secret:
        return False

    signature = payload.get("signature") or {}
    checksum = signature.get("checksum") or ""
    properties = signature.get("properties") or []
    timestamp = payload.get("timestamp", "")
    values = "".join(str(_resolve_event_property(payload, prop)) for prop in properties)
    calculated = hashlib.sha256(f"{values}{timestamp}{secret}".encode("utf-8")).hexdigest()
    return hmac.compare_digest(calculated, checksum)


def extract_transaction_payload(event_payload):
    data = event_payload.get("data") or {}
    if "transaction" in data:
        return data["transaction"]
    return data


def apply_wompi_transaction_status(local_recharge, wompi_transaction):
    wompi_status = normalize_wompi_status(wompi_transaction.get("status"))
    wompi_id = wompi_transaction.get("id") or wompi_transaction.get("transaction_id") or ""

    with transaction.atomic():
        recharge = RechargeTransaction.objects.select_for_update().get(pk=local_recharge.pk)
        wompi_reference = wompi_transaction.get("reference")
        wompi_amount = wompi_transaction.get("amount_in_cents")
        wompi_currency = wompi_transaction.get("currency")
        integrity_matches = True

        if wompi_reference and wompi_reference != recharge.reference:
            integrity_matches = False
        if wompi_amount is not None:
            try:
                integrity_matches = integrity_matches and int(wompi_amount) == recharge.amount_in_cents
            except (TypeError, ValueError):
                integrity_matches = False
        if wompi_currency and str(wompi_currency).upper() != recharge.currency:
            integrity_matches = False

        if not integrity_matches:
            wompi_status = RechargeTransaction.STATUS_ERROR

    return apply_transaction_status(
        recharge,
        status=wompi_status,
        provider_transaction_id=wompi_id,
        payment_method=wompi_transaction.get("payment_method_type", ""),
        raw_response=wompi_transaction,
    )
